"""
Wave-based execution engine for parallel PRD processing.

This module implements the core execution logic that processes phases in waves,
managing parallel execution within each wave and sequential progression between waves.
"""

import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future, as_completed

from models.parallel_execution import ExecutionWave, PhaseInfo, DependencyGraph
from models.execution_state import PhaseStatus, ExecutionState, PhaseExecutionDetails
from orchestrator.agent_spawner import AgentSpawner, AgentStatus
from core.resource_manager import LockRegistry


class RecoveryAction(Enum):
    """Actions to take when a phase fails."""
    RETRY = "retry"           # Retry the phase
    SKIP = "skip"             # Skip and mark as failed
    ABORT_WAVE = "abort_wave" # Abort current wave
    ABORT_ALL = "abort_all"   # Abort entire execution


@dataclass
class PhaseResult:
    """Result of executing a single phase."""
    phase_id: str
    success: bool
    start_time: datetime
    end_time: datetime
    outputs: List[str] = field(default_factory=list)
    error: Optional[str] = None
    agent_id: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate execution duration."""
        return (self.end_time - self.start_time).total_seconds()


@dataclass
class WaveResult:
    """Result of executing a complete wave."""
    wave_number: int
    phases_attempted: List[str]
    phases_completed: List[str]
    phases_failed: List[str]
    start_time: datetime
    end_time: datetime
    phase_results: Dict[str, PhaseResult] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """Check if wave completed successfully."""
        return len(self.phases_failed) == 0
    
    @property
    def duration_seconds(self) -> float:
        """Calculate wave execution duration."""
        return (self.end_time - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get wave execution summary."""
        return {
            "wave_number": self.wave_number,
            "total_phases": len(self.phases_attempted),
            "completed": len(self.phases_completed),
            "failed": len(self.phases_failed),
            "success_rate": (
                len(self.phases_completed) / len(self.phases_attempted) 
                if self.phases_attempted else 0
            ),
            "duration_seconds": self.duration_seconds,
            "phases": {
                "attempted": self.phases_attempted,
                "completed": self.phases_completed,
                "failed": self.phases_failed
            }
        }


class WaveExecutor:
    """
    Executes phases in waves with parallel processing support.
    
    Manages the execution of phases within waves, handling agent assignment,
    progress monitoring, failure recovery, and wave transitions.
    """
    
    def __init__(self, agent_spawner: AgentSpawner, execution_state: ExecutionState,
                 dependency_graph: DependencyGraph, config: Dict[str, Any]):
        """
        Initialize the wave executor.
        
        Args:
            agent_spawner: Agent spawner instance
            execution_state: Global execution state
            dependency_graph: Phase dependency graph
            config: Execution configuration
        """
        self.agent_spawner = agent_spawner
        self.execution_state = execution_state
        self.dependency_graph = dependency_graph
        self.config = config
        
        # Configuration
        self.max_agents_per_wave = config.get("max_agents_per_wave", 5)
        self.phase_timeout = config.get("phase_timeout_seconds", 3600)  # 1 hour
        self.retry_limit = config.get("retry_limit", 2)
        self.inter_wave_delay = config.get("inter_wave_delay_seconds", 5)
        self.failure_strategy = config.get("failure_strategy", "retry")  # retry, skip, abort
        
        # Execution tracking
        self.current_wave: Optional[ExecutionWave] = None
        self.wave_results: List[WaveResult] = []
        self._executor: Optional[ThreadPoolExecutor] = None
        self._phase_futures: Dict[str, Future] = {}
        self._stop_requested = threading.Event()
        
        # Callbacks
        self.on_phase_start: Optional[Callable[[str], None]] = None
        self.on_phase_complete: Optional[Callable[[str, PhaseResult], None]] = None
        self.on_wave_complete: Optional[Callable[[WaveResult], None]] = None
    
    def execute_wave(self, wave: ExecutionWave, workspace: str) -> WaveResult:
        """
        Execute all phases in a wave in parallel.
        
        Args:
            wave: The wave to execute
            workspace: Path to the workspace
            
        Returns:
            WaveResult with execution details
        """
        self.current_wave = wave
        wave_start = datetime.now()
        
        # Update wave status
        wave.status = "in_progress"
        wave.start_time = wave_start
        
        # Initialize result tracking
        phases_attempted = wave.phases.copy()
        phases_completed = []
        phases_failed = []
        phase_results = {}
        
        # Create thread pool for parallel execution
        with ThreadPoolExecutor(max_workers=self.max_agents_per_wave) as executor:
            self._executor = executor
            
            # Submit all phases for execution
            futures = {}
            for phase_id in wave.phases:
                if self._stop_requested.is_set():
                    break
                
                # Check if phase is ready (dependencies satisfied)
                if self._can_execute_phase(phase_id):
                    future = executor.submit(
                        self._execute_phase,
                        phase_id,
                        workspace
                    )
                    futures[future] = phase_id
                    self._phase_futures[phase_id] = future
                else:
                    phases_failed.append(phase_id)
                    phase_results[phase_id] = PhaseResult(
                        phase_id=phase_id,
                        success=False,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        error="Dependencies not satisfied"
                    )
            
            # Wait for phases to complete
            for future in as_completed(futures):
                phase_id = futures[future]
                
                try:
                    result = future.result()
                    phase_results[phase_id] = result
                    
                    if result.success:
                        phases_completed.append(phase_id)
                    else:
                        phases_failed.append(phase_id)
                        
                        # Handle failure based on strategy
                        recovery = self._handle_phase_failure(phase_id, result.error)
                        if recovery == RecoveryAction.ABORT_WAVE:
                            self._cancel_remaining_phases(futures)
                            break
                        elif recovery == RecoveryAction.ABORT_ALL:
                            self._stop_requested.set()
                            self._cancel_remaining_phases(futures)
                            break
                        
                except Exception as e:
                    phases_failed.append(phase_id)
                    phase_results[phase_id] = PhaseResult(
                        phase_id=phase_id,
                        success=False,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        error=f"Execution exception: {str(e)}"
                    )
            
            self._executor = None
            self._phase_futures.clear()
        
        # Update wave status
        wave_end = datetime.now()
        wave.end_time = wave_end
        wave.status = "completed" if not phases_failed else "failed"
        
        # Create wave result
        result = WaveResult(
            wave_number=wave.wave_number,
            phases_attempted=phases_attempted,
            phases_completed=phases_completed,
            phases_failed=phases_failed,
            start_time=wave_start,
            end_time=wave_end,
            phase_results=phase_results
        )
        
        self.wave_results.append(result)
        self.current_wave = None
        
        # Callback
        if self.on_wave_complete:
            self.on_wave_complete(result)
        
        return result
    
    def wait_for_wave_completion(self, wave: ExecutionWave, 
                                 timeout: Optional[int] = None) -> bool:
        """
        Wait for a wave to complete execution.
        
        Args:
            wave: The wave to wait for
            timeout: Optional timeout in seconds
            
        Returns:
            True if wave completed, False if timeout
        """
        start_time = time.time()
        
        while wave.status == "in_progress":
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(1)
        
        return True
    
    def handle_phase_failure(self, phase_id: str, error: str) -> RecoveryAction:
        """
        Determine recovery action for a failed phase.
        
        Args:
            phase_id: ID of the failed phase
            error: Error message
            
        Returns:
            RecoveryAction to take
        """
        return self._handle_phase_failure(phase_id, error)
    
    def transition_to_next_wave(self, current_wave: ExecutionWave) -> Optional[ExecutionWave]:
        """
        Prepare transition to the next wave.
        
        Args:
            current_wave: The current wave that just completed
            
        Returns:
            Next wave if available, None otherwise
        """
        # Apply inter-wave delay
        if self.inter_wave_delay > 0:
            time.sleep(self.inter_wave_delay)
        
        # Clean up resources from current wave
        self._cleanup_wave_resources(current_wave)
        
        # Get next wave from execution state
        next_wave_number = current_wave.wave_number + 1
        for wave in self.execution_state.waves:
            if wave.wave_number == next_wave_number:
                return wave
        
        return None
    
    def stop_execution(self):
        """Stop execution of current wave."""
        self._stop_requested.set()
        
        # Cancel any running phases
        if self._executor:
            self._executor.shutdown(wait=False)
    
    def _execute_phase(self, phase_id: str, workspace: str) -> PhaseResult:
        """
        Execute a single phase using an agent.
        
        Args:
            phase_id: ID of the phase to execute
            workspace: Path to the workspace
            
        Returns:
            PhaseResult with execution details
        """
        phase_info = self.dependency_graph.get_phase(phase_id)
        if not phase_info:
            return PhaseResult(
                phase_id=phase_id,
                success=False,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error="Phase not found in dependency graph"
            )
        
        # Update phase status
        phase_details = self.execution_state.phase_states.get(phase_id)
        if not phase_details:
            phase_details = PhaseExecutionDetails(phase_id=phase_id)
            self.execution_state.phase_states[phase_id] = phase_details
        
        # Callback
        if self.on_phase_start:
            self.on_phase_start(phase_id)
        
        start_time = datetime.now()
        
        # Spawn agent for this phase
        success, agent_id_or_error = self.agent_spawner.spawn_agent({
            "id": phase_id,
            "name": phase_info.name,
            "description": phase_info.description,
            "outputs": phase_info.outputs,
            "estimated_time": phase_info.estimated_time
        })
        
        if not success:
            end_time = datetime.now()
            result = PhaseResult(
                phase_id=phase_id,
                success=False,
                start_time=start_time,
                end_time=end_time,
                error=agent_id_or_error
            )
            phase_details.mark_failed(agent_id_or_error)
            return result
        
        agent_id = agent_id_or_error
        phase_details.mark_started(agent_id)
        
        # Monitor agent execution
        result = self._monitor_phase_execution(
            phase_id,
            agent_id,
            phase_info,
            start_time
        )
        
        # Update phase details
        if result.success:
            phase_details.mark_completed(result.outputs)
        else:
            phase_details.mark_failed(result.error or "Unknown error")
        
        # Callback
        if self.on_phase_complete:
            self.on_phase_complete(phase_id, result)
        
        return result
    
    def _monitor_phase_execution(self, phase_id: str, agent_id: str, 
                                phase_info: PhaseInfo, start_time: datetime) -> PhaseResult:
        """
        Monitor the execution of a phase by an agent.
        
        Args:
            phase_id: ID of the phase
            agent_id: ID of the executing agent
            phase_info: Phase information
            start_time: When execution started
            
        Returns:
            PhaseResult with execution outcome
        """
        timeout_seconds = self.phase_timeout
        check_interval = 5  # Check every 5 seconds
        
        while True:
            # Check if stop requested
            if self._stop_requested.is_set():
                self.agent_spawner.terminate_agent(agent_id)
                return PhaseResult(
                    phase_id=phase_id,
                    success=False,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error="Execution stopped by user",
                    agent_id=agent_id
                )
            
            # Check agent status
            status = self.agent_spawner.monitor_agent_health(agent_id)
            
            if status == AgentStatus.COMPLETED:
                # Collect outputs
                agent = self.agent_spawner.agents.get(agent_id)
                outputs = []
                if agent:
                    state = agent.get_state()
                    outputs = state.get("outputs", [])
                
                return PhaseResult(
                    phase_id=phase_id,
                    success=True,
                    start_time=start_time,
                    end_time=datetime.now(),
                    outputs=outputs,
                    agent_id=agent_id
                )
            
            elif status == AgentStatus.ERROR:
                # Collect error information
                logs = self.agent_spawner.collect_agent_logs(agent_id)
                error_msg = "Phase execution failed"
                for log in reversed(logs):
                    if log.level == "error":
                        error_msg = log.message
                        break
                
                return PhaseResult(
                    phase_id=phase_id,
                    success=False,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error=error_msg,
                    agent_id=agent_id
                )
            
            elif status == AgentStatus.TERMINATED:
                return PhaseResult(
                    phase_id=phase_id,
                    success=False,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error="Agent terminated unexpectedly",
                    agent_id=agent_id
                )
            
            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                self.agent_spawner.terminate_agent(agent_id)
                return PhaseResult(
                    phase_id=phase_id,
                    success=False,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error=f"Phase execution timeout ({timeout_seconds}s)",
                    agent_id=agent_id
                )
            
            # Wait before next check
            time.sleep(check_interval)
    
    def _can_execute_phase(self, phase_id: str) -> bool:
        """
        Check if a phase can be executed (all dependencies satisfied).
        
        Args:
            phase_id: ID of the phase to check
            
        Returns:
            True if phase can be executed
        """
        phase = self.dependency_graph.get_phase(phase_id)
        if not phase:
            return False
        
        # Check all dependencies are completed
        for dep_id in phase.dependencies:
            dep_status = self.execution_state.get_phase_status(dep_id)
            if dep_status != PhaseStatus.COMPLETED:
                return False
        
        return True
    
    def _handle_phase_failure(self, phase_id: str, error: Optional[str]) -> RecoveryAction:
        """
        Determine recovery action for a failed phase.
        
        Args:
            phase_id: ID of the failed phase
            error: Error message
            
        Returns:
            RecoveryAction to take
        """
        phase_details = self.execution_state.phase_states.get(phase_id)
        
        # Check retry limit
        if phase_details and phase_details.retry_count < self.retry_limit:
            if self.failure_strategy == "retry":
                return RecoveryAction.RETRY
        
        # Determine action based on configuration
        if self.failure_strategy == "skip":
            return RecoveryAction.SKIP
        elif self.failure_strategy == "abort_wave":
            return RecoveryAction.ABORT_WAVE
        elif self.failure_strategy == "abort_all":
            return RecoveryAction.ABORT_ALL
        else:
            return RecoveryAction.SKIP
    
    def _cancel_remaining_phases(self, futures: Dict[Future, str]):
        """Cancel any phases that haven't started yet."""
        for future, phase_id in futures.items():
            if not future.done():
                future.cancel()
                # Mark phase as cancelled
                phase_details = self.execution_state.phase_states.get(phase_id)
                if phase_details:
                    phase_details.status = PhaseStatus.CANCELLED
    
    def _cleanup_wave_resources(self, wave: ExecutionWave):
        """
        Clean up resources after wave completion.
        
        Args:
            wave: The completed wave
        """
        # Release any locks held by phases in this wave
        lock_registry = LockRegistry.instance()
        for phase_id in wave.phases:
            lock_registry.release_all_phase_locks(phase_id)
        
        # Clean up completed agents
        self.agent_spawner.cleanup_stale_agents()
    
    def get_wave_progress(self, wave: ExecutionWave) -> Dict[str, Any]:
        """
        Get detailed progress information for a wave.
        
        Args:
            wave: The wave to check
            
        Returns:
            Dictionary with progress information
        """
        if wave != self.current_wave:
            # Historical wave
            for result in self.wave_results:
                if result.wave_number == wave.wave_number:
                    return result.get_summary()
            
            return {
                "wave_number": wave.wave_number,
                "status": wave.status,
                "phases": wave.phases,
                "progress": "Not started"
            }
        
        # Current wave
        completed = []
        in_progress = []
        pending = []
        failed = []
        
        for phase_id in wave.phases:
            status = self.execution_state.get_phase_status(phase_id)
            if status == PhaseStatus.COMPLETED:
                completed.append(phase_id)
            elif status == PhaseStatus.IN_PROGRESS:
                in_progress.append(phase_id)
            elif status == PhaseStatus.FAILED:
                failed.append(phase_id)
            else:
                pending.append(phase_id)
        
        return {
            "wave_number": wave.wave_number,
            "status": wave.status,
            "total_phases": len(wave.phases),
            "completed": len(completed),
            "in_progress": len(in_progress),
            "pending": len(pending),
            "failed": len(failed),
            "progress_percent": (len(completed) / len(wave.phases) * 100) if wave.phases else 0,
            "phases": {
                "completed": completed,
                "in_progress": in_progress,
                "pending": pending,
                "failed": failed
            }
        }