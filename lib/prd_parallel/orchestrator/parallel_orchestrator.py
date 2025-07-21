"""
Main orchestration engine for parallel PRD execution.

This module ties together all components to provide a high-level interface
for executing PRD phases in parallel with proper coordination and monitoring.
"""

import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from models.parallel_execution import PhaseInfo, DependencyGraph, ExecutionWave
from models.execution_state import ExecutionState, PhaseStatus, PhaseExecutionDetails
from analyzers.dependency_analyzer import DependencyAnalyzer
from analyzers.wave_calculator import WaveCalculator
from analyzers.conflict_detector import ConflictDetector
from orchestrator.agent_spawner import AgentSpawner
from orchestrator.wave_executor import WaveExecutor, WaveResult
from orchestrator.resource_coordinator import ResourceCoordinator
from orchestrator.state_manager import StateManager


class ExecutionMode(Enum):
    """Modes of execution."""
    NORMAL = "normal"          # Execute all phases
    RESUME = "resume"          # Resume from saved state
    DRY_RUN = "dry_run"       # Simulate execution without running agents
    VALIDATE = "validate"      # Only validate dependencies and conflicts


@dataclass
class ExecutionResult:
    """Overall result of PRD execution."""
    success: bool
    mode: ExecutionMode
    start_time: datetime
    end_time: datetime
    total_phases: int
    completed_phases: int
    failed_phases: int
    waves_executed: int
    total_duration_seconds: float
    phase_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    @property
    def is_complete(self) -> bool:
        """Check if execution is complete."""
        return self.completed_phases + self.failed_phases == self.total_phases
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return {
            "success": self.success,
            "mode": self.mode.value,
            "duration": f"{self.total_duration_seconds:.2f}s",
            "phases": {
                "total": self.total_phases,
                "completed": self.completed_phases,
                "failed": self.failed_phases,
                "success_rate": (
                    self.completed_phases / self.total_phases 
                    if self.total_phases > 0 else 0
                )
            },
            "waves": self.waves_executed,
            "errors": len(self.errors)
        }


@dataclass
class ProgressReport:
    """Progress report for ongoing execution."""
    current_wave: int
    total_waves: int
    percent_complete: float
    phases_completed: int
    phases_total: int
    active_agents: int
    estimated_time_remaining: float  # seconds
    current_phase_status: Dict[str, str]  # phase_id -> status
    
    def __str__(self):
        return (
            f"Wave {self.current_wave}/{self.total_waves} "
            f"({self.percent_complete:.1f}% complete) - "
            f"{self.phases_completed}/{self.phases_total} phases done, "
            f"{self.active_agents} agents active"
        )


class ParallelOrchestrator:
    """
    Main orchestration class for parallel PRD execution.
    
    Coordinates all components to execute PRD phases in parallel while
    managing dependencies, resources, and state.
    """
    
    def __init__(self, workspace: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the parallel orchestrator.
        
        Args:
            workspace: Path to the workspace directory
            config: Optional configuration dictionary
        """
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
        
        # Default configuration
        default_config = {
            "max_agents": 5,
            "max_agents_per_wave": 5,
            "phase_timeout_seconds": 3600,
            "retry_limit": 2,
            "failure_strategy": "retry",
            "enable_deadlock_detection": True,
            "checkpoint_interval_seconds": 30,
            "inter_wave_delay_seconds": 5
        }
        self.config = {**default_config, **(config or {})}
        
        # Initialize components
        self._init_components()
        
        # Execution state
        self.execution_state: Optional[ExecutionState] = None
        self.dependency_graph: Optional[DependencyGraph] = None
        self.execution_waves: List[ExecutionWave] = []
        self.current_result: Optional[ExecutionResult] = None
        
        # Control flags
        self._is_running = False
        self._pause_requested = threading.Event()
        self._stop_requested = threading.Event()
        self._execution_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_phase_start: Optional[Callable[[str, PhaseInfo], None]] = None
        self.on_phase_complete: Optional[Callable[[str, bool], None]] = None
        self.on_wave_complete: Optional[Callable[[int, WaveResult], None]] = None
        self.on_execution_complete: Optional[Callable[[ExecutionResult], None]] = None
    
    def execute_prd(self, phases: List[PhaseInfo], 
                    mode: ExecutionMode = ExecutionMode.NORMAL) -> ExecutionResult:
        """
        Execute PRD phases in parallel.
        
        Args:
            phases: List of phases to execute
            mode: Execution mode
            
        Returns:
            ExecutionResult with execution outcome
        """
        if self._is_running:
            raise RuntimeError("Execution already in progress")
        
        start_time = datetime.now()
        
        try:
            # Initialize execution
            if mode == ExecutionMode.RESUME:
                success = self._resume_execution()
                if not success:
                    return ExecutionResult(
                        success=False,
                        mode=mode,
                        start_time=start_time,
                        end_time=datetime.now(),
                        total_phases=0,
                        completed_phases=0,
                        failed_phases=0,
                        waves_executed=0,
                        total_duration_seconds=0,
                        errors=["Failed to resume from saved state"]
                    )
            else:
                self._initialize_execution(phases, mode)
            
            if mode == ExecutionMode.VALIDATE:
                # Only validate, don't execute
                return self._validate_execution()
            
            if mode == ExecutionMode.DRY_RUN:
                # Simulate execution
                return self._dry_run_execution()
            
            # Start execution in background thread
            self._is_running = True
            self._stop_requested.clear()
            self._pause_requested.clear()
            
            self._execution_thread = threading.Thread(
                target=self._execution_loop,
                daemon=True
            )
            self._execution_thread.start()
            
            # Wait for completion
            self._execution_thread.join()
            
            # Get final result
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            completed = len(self.execution_state.get_completed_phases())
            failed = len(self.execution_state.get_failed_phases())
            
            result = ExecutionResult(
                success=(failed == 0),
                mode=mode,
                start_time=start_time,
                end_time=end_time,
                total_phases=len(self.execution_state.phase_states),
                completed_phases=completed,
                failed_phases=failed,
                waves_executed=len([w for w in self.execution_waves if w.status == "completed"]),
                total_duration_seconds=duration
            )
            
            # Add phase results
            for phase_id, details in self.execution_state.phase_states.items():
                result.phase_results[phase_id] = {
                    "status": details.status.value,
                    "duration": details.duration_seconds(),
                    "error": details.error_message,
                    "outputs": details.output_files
                }
            
            self.current_result = result
            
            # Callback
            if self.on_execution_complete:
                self.on_execution_complete(result)
            
            return result
            
        finally:
            self._is_running = False
            self._cleanup()
    
    def pause_execution(self):
        """Pause the current execution."""
        if self._is_running:
            self._pause_requested.set()
            self.state_manager.save_execution_state(self.execution_state)
    
    def resume_execution(self):
        """Resume a paused execution."""
        if self._is_running:
            self._pause_requested.clear()
    
    def stop_execution(self):
        """Stop the current execution."""
        if self._is_running:
            self._stop_requested.set()
            self.wave_executor.stop_execution()
            
            # Wait for execution thread to finish
            if self._execution_thread:
                self._execution_thread.join(timeout=30)
    
    def get_progress(self) -> ProgressReport:
        """
        Get current execution progress.
        
        Returns:
            ProgressReport with current status
        """
        if not self.execution_state:
            return ProgressReport(
                current_wave=0,
                total_waves=0,
                percent_complete=0.0,
                phases_completed=0,
                phases_total=0,
                active_agents=0,
                estimated_time_remaining=0,
                current_phase_status={}
            )
        
        # Find current wave
        current_wave_num = 0
        for wave in self.execution_waves:
            if wave.status == "in_progress":
                current_wave_num = wave.wave_number
                break
            elif wave.status == "completed":
                current_wave_num = wave.wave_number + 1
        
        # Calculate progress
        completed = len(self.execution_state.get_completed_phases())
        total = len(self.execution_state.phase_states)
        percent = (completed / total * 100) if total > 0 else 0
        
        # Get active agents
        active_agents = len(self.agent_spawner.get_active_agents())
        
        # Estimate remaining time
        if completed > 0 and self.execution_state.start_time:
            elapsed = (datetime.now() - self.execution_state.start_time).total_seconds()
            rate = completed / elapsed
            remaining_phases = total - completed
            estimated_remaining = remaining_phases / rate if rate > 0 else 0
        else:
            estimated_remaining = 0
        
        # Get phase status
        phase_status = {
            phase_id: details.status.value
            for phase_id, details in self.execution_state.phase_states.items()
        }
        
        return ProgressReport(
            current_wave=current_wave_num,
            total_waves=len(self.execution_waves),
            percent_complete=percent,
            phases_completed=completed,
            phases_total=total,
            active_agents=active_agents,
            estimated_time_remaining=estimated_remaining,
            current_phase_status=phase_status
        )
    
    def get_execution_state(self) -> Optional[ExecutionState]:
        """Get the current execution state."""
        return self.execution_state
    
    def get_resource_statistics(self) -> Dict[str, Any]:
        """Get resource usage statistics."""
        return self.resource_coordinator.get_statistics()
    
    def _init_components(self):
        """Initialize all orchestrator components."""
        # Analyzers
        self.dependency_analyzer = DependencyAnalyzer()
        self.wave_calculator = WaveCalculator()
        self.conflict_detector = ConflictDetector()
        
        # Core components
        self.agent_spawner = AgentSpawner(str(self.workspace), self.config)
        self.resource_coordinator = ResourceCoordinator(str(self.workspace), self.config)
        self.state_manager = StateManager(str(self.workspace), self.config)
        
        # Wave executor (initialized after state is loaded)
        self.wave_executor = None
    
    def _initialize_execution(self, phases: List[PhaseInfo], mode: ExecutionMode):
        """Initialize a new execution."""
        # Build dependency graph
        self.dependency_graph = self.dependency_analyzer.build_dependency_graph(phases)
        
        # Validate dependencies
        is_valid, errors = self.dependency_analyzer.validate_dependencies(self.dependency_graph)
        if not is_valid:
            raise ValueError(f"Invalid dependencies: {errors}")
        
        # Calculate execution waves
        self.execution_waves = self.wave_calculator.calculate_execution_waves(
            self.dependency_graph
        )
        
        # Optimize for agent limit
        self.execution_waves = self.wave_calculator.optimize_wave_distribution(
            self.execution_waves,
            self.config["max_agents_per_wave"]
        )
        
        # Detect conflicts
        conflicts = self.conflict_detector.detect_all_conflicts(phases)
        if conflicts and mode != ExecutionMode.DRY_RUN:
            print(f"Warning: {len(conflicts)} potential conflicts detected")
        
        # Initialize execution state
        self.execution_state = ExecutionState()
        self.execution_state.start_time = datetime.now()
        self.execution_state.config = self.config
        
        # Add phases to state
        for phase in phases:
            self.execution_state.add_phase(phase.id)
        
        # Add waves to state
        self.execution_state.waves = self.execution_waves
        
        # Initialize wave executor
        self.wave_executor = WaveExecutor(
            self.agent_spawner,
            self.execution_state,
            self.dependency_graph,
            self.config
        )
        
        # Set callbacks
        self._setup_callbacks()
        
        # Save initial state
        self.state_manager.save_execution_state(self.execution_state)
    
    def _resume_execution(self) -> bool:
        """Resume execution from saved state."""
        # Load saved state
        saved_state = self.state_manager.recover_from_crash()
        if not saved_state:
            return False
        
        self.execution_state = saved_state
        
        # Rebuild dependency graph from phase info
        # (In a real implementation, we'd save and restore the graph too)
        phases = []
        for phase_id in saved_state.phase_states:
            # Reconstruct phase info (simplified)
            phase = PhaseInfo(
                id=phase_id,
                name=f"Phase {phase_id}",
                dependencies=[],  # Would need to restore these
                outputs=[],
                estimated_time=1.0
            )
            phases.append(phase)
        
        self.dependency_graph = self.dependency_analyzer.build_dependency_graph(phases)
        self.execution_waves = saved_state.waves
        
        # Initialize wave executor
        self.wave_executor = WaveExecutor(
            self.agent_spawner,
            self.execution_state,
            self.dependency_graph,
            self.config
        )
        
        self._setup_callbacks()
        
        return True
    
    def _validate_execution(self) -> ExecutionResult:
        """Validate execution without running."""
        errors = []
        
        # Check dependency graph
        is_valid, dep_errors = self.dependency_analyzer.validate_dependencies(
            self.dependency_graph
        )
        if not is_valid:
            errors.extend(dep_errors)
        
        # Check for conflicts
        conflicts = self.conflict_detector.detect_all_conflicts(
            list(self.dependency_graph.nodes.values())
        )
        for conflict in conflicts:
            errors.append(f"Conflict: {conflict}")
        
        # Check wave distribution
        metrics = self.wave_calculator.calculate_metrics(
            self.execution_waves,
            self.dependency_graph
        )
        
        return ExecutionResult(
            success=len(errors) == 0,
            mode=ExecutionMode.VALIDATE,
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_phases=len(self.dependency_graph.nodes),
            completed_phases=0,
            failed_phases=0,
            waves_executed=0,
            total_duration_seconds=0,
            errors=errors
        )
    
    def _dry_run_execution(self) -> ExecutionResult:
        """Simulate execution without running agents."""
        print("Starting dry run...")
        
        start_time = datetime.now()
        simulated_time = 0.0
        
        for wave in self.execution_waves:
            print(f"\nWave {wave.wave_number}: {len(wave.phases)} phases")
            
            # Simulate wave execution
            wave_time = 0.0
            for phase_id in wave.phases:
                phase = self.dependency_graph.get_phase(phase_id)
                if phase:
                    print(f"  - {phase_id}: {phase.name} ({phase.estimated_time}h)")
                    wave_time = max(wave_time, phase.estimated_time)
                    
                    # Update state
                    self.execution_state.update_phase_status(
                        phase_id, PhaseStatus.COMPLETED
                    )
            
            simulated_time += wave_time * 3600  # Convert to seconds
        
        end_time = datetime.now()
        
        return ExecutionResult(
            success=True,
            mode=ExecutionMode.DRY_RUN,
            start_time=start_time,
            end_time=end_time,
            total_phases=len(self.dependency_graph.nodes),
            completed_phases=len(self.dependency_graph.nodes),
            failed_phases=0,
            waves_executed=len(self.execution_waves),
            total_duration_seconds=simulated_time
        )
    
    def _execution_loop(self):
        """Main execution loop running in background thread."""
        try:
            for wave in self.execution_waves:
                # Check if stopped
                if self._stop_requested.is_set():
                    break
                
                # Check if paused
                while self._pause_requested.is_set():
                    time.sleep(1)
                    if self._stop_requested.is_set():
                        return
                
                # Skip completed waves (for resume)
                if wave.status == "completed":
                    continue
                
                print(f"\nExecuting wave {wave.wave_number} with {len(wave.phases)} phases")
                
                # Execute wave
                result = self.wave_executor.execute_wave(wave, str(self.workspace))
                
                # Save state after each wave
                self.state_manager.save_execution_state(self.execution_state)
                
                # Check if we should stop due to failures
                if not result.success and self.config.get("stop_on_wave_failure", False):
                    print(f"Wave {wave.wave_number} failed, stopping execution")
                    break
            
            # Mark execution as complete
            self.execution_state.end_time = datetime.now()
            self.state_manager.save_execution_state(self.execution_state)
            
        except Exception as e:
            print(f"Error in execution loop: {e}")
            # Save state on error
            if self.execution_state:
                self.state_manager.save_execution_state(self.execution_state)
            raise
    
    def _setup_callbacks(self):
        """Set up callbacks for components."""
        # Wave executor callbacks
        def on_phase_start(phase_id: str):
            if self.on_phase_start:
                phase = self.dependency_graph.get_phase(phase_id)
                if phase:
                    self.on_phase_start(phase_id, phase)
        
        def on_phase_complete(phase_id: str, result):
            # Update state
            if result.success:
                self.state_manager.update_phase_status(phase_id, PhaseStatus.COMPLETED)
            else:
                self.state_manager.update_phase_status(
                    phase_id, PhaseStatus.FAILED, result.error
                )
            
            if self.on_phase_complete:
                self.on_phase_complete(phase_id, result.success)
        
        def on_wave_complete(result: WaveResult):
            if self.on_wave_complete:
                self.on_wave_complete(result.wave_number, result)
        
        self.wave_executor.on_phase_start = on_phase_start
        self.wave_executor.on_phase_complete = on_phase_complete
        self.wave_executor.on_wave_complete = on_wave_complete
    
    def _cleanup(self):
        """Clean up resources after execution."""
        # Terminate any remaining agents
        self.agent_spawner.terminate_all()
        
        # Stop components
        self.resource_coordinator.stop()
        self.state_manager.stop()
        
        # Clean up temporary files
        agents_dir = self.workspace / "agents"
        if agents_dir.exists():
            import shutil
            shutil.rmtree(agents_dir, ignore_errors=True)