"""
State persistence and recovery for parallel PRD execution.

This module handles saving and loading execution state to enable resumable
execution and crash recovery.
"""

import json
import os
import shutil
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from models.execution_state import (
    ExecutionState, PhaseStatus, PhaseExecutionDetails, 
    AgentInfo, AgentStatus
)
from models.parallel_execution import ExecutionWave, PhaseInfo, DependencyGraph


class StateVersion(Enum):
    """Version of the state file format."""
    V1 = "1.0"
    CURRENT = V1


@dataclass
class StateMetadata:
    """Metadata about the saved state."""
    version: str
    created_at: datetime
    last_updated: datetime
    checkpoint_number: int
    workspace_path: str
    total_phases: int
    completed_phases: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "checkpoint_number": self.checkpoint_number,
            "workspace_path": self.workspace_path,
            "total_phases": self.total_phases,
            "completed_phases": self.completed_phases
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateMetadata':
        """Create from dictionary."""
        return cls(
            version=data["version"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            checkpoint_number=data["checkpoint_number"],
            workspace_path=data["workspace_path"],
            total_phases=data["total_phases"],
            completed_phases=data["completed_phases"]
        )


class StateManager:
    """
    Manages persistent state for parallel PRD execution.
    
    Features:
    - Atomic state updates with file locking
    - Automatic checkpointing
    - Crash recovery
    - State validation
    - Backup management
    """
    
    def __init__(self, workspace: str, config: Dict[str, Any]):
        """
        Initialize the state manager.
        
        Args:
            workspace: Path to the workspace
            config: Configuration dictionary
        """
        self.workspace = Path(workspace)
        self.config = config
        
        # Configuration
        self.checkpoint_interval = config.get("checkpoint_interval_seconds", 30)
        self.max_backups = config.get("max_state_backups", 5)
        self.enable_auto_checkpoint = config.get("enable_auto_checkpoint", True)
        
        # State file paths
        self.state_dir = self.workspace / ".parallel-state"
        self.state_dir.mkdir(exist_ok=True)
        
        self.state_file = self.state_dir / "parallel-state.json"
        self.temp_state_file = self.state_dir / "parallel-state.tmp"
        self.backup_dir = self.state_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # State tracking
        self._current_state: Optional[ExecutionState] = None
        self._metadata: Optional[StateMetadata] = None
        self._checkpoint_number = 0
        self._last_checkpoint = datetime.now()
        self._state_lock = threading.RLock()
        
        # Auto-checkpoint thread
        self._checkpoint_thread = None
        self._stop_checkpoint = threading.Event()
        
        if self.enable_auto_checkpoint:
            self._start_auto_checkpoint()
    
    def save_execution_state(self, state: ExecutionState) -> bool:
        """
        Save the current execution state to disk.
        
        Args:
            state: The execution state to save
            
        Returns:
            True if successfully saved
        """
        with self._state_lock:
            try:
                # Update metadata
                now = datetime.now()
                if not self._metadata:
                    self._metadata = StateMetadata(
                        version=StateVersion.CURRENT.value,
                        created_at=now,
                        last_updated=now,
                        checkpoint_number=0,
                        workspace_path=str(self.workspace),
                        total_phases=len(state.phase_states),
                        completed_phases=len(state.get_completed_phases())
                    )
                else:
                    self._metadata.last_updated = now
                    self._metadata.checkpoint_number = self._checkpoint_number
                    self._metadata.completed_phases = len(state.get_completed_phases())
                
                # Prepare state data
                state_data = self._serialize_state(state)
                
                # Add metadata
                state_data["metadata"] = self._metadata.to_dict()
                
                # Write atomically
                with open(self.temp_state_file, 'w') as f:
                    json.dump(state_data, f, indent=2)
                
                # Backup current state if it exists
                if self.state_file.exists():
                    self._backup_current_state()
                
                # Move temp to actual
                self.temp_state_file.replace(self.state_file)
                
                self._current_state = state
                self._last_checkpoint = now
                self._checkpoint_number += 1
                
                return True
                
            except Exception as e:
                print(f"Error saving state: {e}")
                # Clean up temp file
                if self.temp_state_file.exists():
                    self.temp_state_file.unlink()
                return False
    
    def load_execution_state(self) -> Optional[ExecutionState]:
        """
        Load execution state from disk.
        
        Returns:
            ExecutionState if found and valid, None otherwise
        """
        with self._state_lock:
            if not self.state_file.exists():
                return None
            
            try:
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)
                
                # Extract and validate metadata
                metadata_dict = state_data.get("metadata", {})
                if not metadata_dict:
                    print("Warning: No metadata in state file")
                    return None
                
                self._metadata = StateMetadata.from_dict(metadata_dict)
                
                # Check version compatibility
                if self._metadata.version != StateVersion.CURRENT.value:
                    print(f"Warning: State file version mismatch: {self._metadata.version}")
                    # Could implement version migration here
                
                # Deserialize state
                state = self._deserialize_state(state_data)
                
                self._current_state = state
                self._checkpoint_number = self._metadata.checkpoint_number + 1
                
                return state
                
            except Exception as e:
                print(f"Error loading state: {e}")
                return None
    
    def update_phase_status(self, phase_id: str, status: PhaseStatus, 
                           error: Optional[str] = None) -> bool:
        """
        Update the status of a specific phase.
        
        Args:
            phase_id: ID of the phase to update
            status: New status
            error: Optional error message
            
        Returns:
            True if successfully updated
        """
        with self._state_lock:
            if not self._current_state:
                return False
            
            if phase_id not in self._current_state.phase_states:
                self._current_state.phase_states[phase_id] = PhaseExecutionDetails(phase_id)
            
            phase_details = self._current_state.phase_states[phase_id]
            phase_details.status = status
            
            if error:
                phase_details.error_message = error
            
            if status == PhaseStatus.IN_PROGRESS:
                phase_details.start_time = datetime.now()
            elif status in {PhaseStatus.COMPLETED, PhaseStatus.FAILED}:
                phase_details.end_time = datetime.now()
            
            # Trigger checkpoint if significant change
            if status in {PhaseStatus.COMPLETED, PhaseStatus.FAILED}:
                self._maybe_checkpoint()
            
            return True
    
    def recover_from_crash(self) -> Optional[ExecutionState]:
        """
        Attempt to recover from a crash by loading the last valid state.
        
        Returns:
            Recovered ExecutionState or None if recovery fails
        """
        # First try to load the main state file
        state = self.load_execution_state()
        if state:
            print(f"Recovered state from checkpoint {self._metadata.checkpoint_number}")
            
            # Mark any in-progress phases as failed
            phases_to_retry = []
            for phase_id, details in state.phase_states.items():
                if details.status == PhaseStatus.IN_PROGRESS:
                    details.status = PhaseStatus.FAILED
                    details.error_message = "Interrupted by crash"
                    details.end_time = datetime.now()
                    phases_to_retry.append(phase_id)
            
            if phases_to_retry:
                print(f"Marking {len(phases_to_retry)} interrupted phases for retry")
            
            return state
        
        # Try to recover from backups
        backups = sorted(self.backup_dir.glob("*.json"), reverse=True)
        for backup_file in backups[:3]:  # Try last 3 backups
            try:
                print(f"Attempting recovery from backup: {backup_file.name}")
                
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                
                # Copy backup to main state file
                with open(self.state_file, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                
                # Try loading again
                state = self.load_execution_state()
                if state:
                    print(f"Successfully recovered from backup")
                    return state
                    
            except Exception as e:
                print(f"Failed to recover from backup {backup_file.name}: {e}")
        
        print("Failed to recover state")
        return None
    
    def get_checkpoint_info(self) -> Dict[str, Any]:
        """Get information about the current checkpoint."""
        with self._state_lock:
            if not self._metadata:
                return {
                    "has_checkpoint": False,
                    "checkpoint_number": 0
                }
            
            return {
                "has_checkpoint": True,
                "checkpoint_number": self._metadata.checkpoint_number,
                "created_at": self._metadata.created_at.isoformat(),
                "last_updated": self._metadata.last_updated.isoformat(),
                "total_phases": self._metadata.total_phases,
                "completed_phases": self._metadata.completed_phases,
                "workspace": self._metadata.workspace_path
            }
    
    def clear_state(self):
        """Clear all saved state (use with caution)."""
        with self._state_lock:
            # Remove state file
            if self.state_file.exists():
                self.state_file.unlink()
            
            # Remove backups
            for backup in self.backup_dir.glob("*.json"):
                backup.unlink()
            
            self._current_state = None
            self._metadata = None
            self._checkpoint_number = 0
    
    def _serialize_state(self, state: ExecutionState) -> Dict[str, Any]:
        """
        Serialize ExecutionState to JSON-compatible format.
        
        Args:
            state: The state to serialize
            
        Returns:
            Dictionary representation
        """
        # Serialize phase states
        phase_states = {}
        for phase_id, details in state.phase_states.items():
            phase_states[phase_id] = {
                "phase_id": details.phase_id,
                "status": details.status.value,
                "agent_id": details.agent_id,
                "start_time": details.start_time.isoformat() if details.start_time else None,
                "end_time": details.end_time.isoformat() if details.end_time else None,
                "error_message": details.error_message,
                "retry_count": details.retry_count,
                "output_files": details.output_files,
                "metrics": details.metrics
            }
        
        # Serialize waves
        waves = []
        for wave in state.waves:
            waves.append({
                "wave_number": wave.wave_number,
                "phases": wave.phases,
                "start_time": wave.start_time.isoformat() if wave.start_time else None,
                "end_time": wave.end_time.isoformat() if wave.end_time else None,
                "status": wave.status
            })
        
        # Serialize agents
        agents = {}
        for agent_id, agent_info in state.agents.items():
            agents[agent_id] = {
                "agent_id": agent_info.agent_id,
                "assigned_phase": agent_info.assigned_phase,
                "status": agent_info.status.value,
                "created_at": agent_info.created_at.isoformat(),
                "terminated_at": agent_info.terminated_at.isoformat() if agent_info.terminated_at else None,
                "logs": agent_info.logs  # Already in dict format
            }
        
        return {
            "phase_states": phase_states,
            "waves": waves,
            "agents": agents,
            "start_time": state.start_time.isoformat() if state.start_time else None,
            "end_time": state.end_time.isoformat() if state.end_time else None,
            "config": state.config
        }
    
    def _deserialize_state(self, data: Dict[str, Any]) -> ExecutionState:
        """
        Deserialize ExecutionState from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            ExecutionState object
        """
        state = ExecutionState()
        
        # Deserialize phase states
        for phase_id, details_dict in data.get("phase_states", {}).items():
            details = PhaseExecutionDetails(phase_id=phase_id)
            details.status = PhaseStatus(details_dict["status"])
            details.agent_id = details_dict.get("agent_id")
            details.start_time = (
                datetime.fromisoformat(details_dict["start_time"]) 
                if details_dict.get("start_time") else None
            )
            details.end_time = (
                datetime.fromisoformat(details_dict["end_time"]) 
                if details_dict.get("end_time") else None
            )
            details.error_message = details_dict.get("error_message")
            details.retry_count = details_dict.get("retry_count", 0)
            details.output_files = details_dict.get("output_files", [])
            details.metrics = details_dict.get("metrics", {})
            
            state.phase_states[phase_id] = details
        
        # Deserialize waves
        for wave_dict in data.get("waves", []):
            wave = ExecutionWave(
                wave_number=wave_dict["wave_number"],
                phases=wave_dict["phases"],
                status=wave_dict.get("status", "pending")
            )
            wave.start_time = (
                datetime.fromisoformat(wave_dict["start_time"]) 
                if wave_dict.get("start_time") else None
            )
            wave.end_time = (
                datetime.fromisoformat(wave_dict["end_time"]) 
                if wave_dict.get("end_time") else None
            )
            state.waves.append(wave)
        
        # Deserialize agents
        for agent_id, agent_dict in data.get("agents", {}).items():
            agent_info = AgentInfo(agent_id=agent_id)
            agent_info.assigned_phase = agent_dict.get("assigned_phase")
            agent_info.status = AgentStatus(agent_dict["status"])
            agent_info.created_at = datetime.fromisoformat(agent_dict["created_at"])
            agent_info.terminated_at = (
                datetime.fromisoformat(agent_dict["terminated_at"]) 
                if agent_dict.get("terminated_at") else None
            )
            agent_info.logs = agent_dict.get("logs", [])
            
            state.agents[agent_id] = agent_info
        
        # Deserialize other fields
        state.start_time = (
            datetime.fromisoformat(data["start_time"]) 
            if data.get("start_time") else None
        )
        state.end_time = (
            datetime.fromisoformat(data["end_time"]) 
            if data.get("end_time") else None
        )
        state.config = data.get("config", {})
        
        return state
    
    def _backup_current_state(self):
        """Create a backup of the current state file."""
        if not self.state_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"state_backup_{timestamp}_{self._checkpoint_number}.json"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(self.state_file, backup_path)
        
        # Clean up old backups
        self._cleanup_old_backups()
    
    def _cleanup_old_backups(self):
        """Remove old backups exceeding the limit."""
        backups = sorted(self.backup_dir.glob("*.json"))
        
        if len(backups) > self.max_backups:
            for backup in backups[:-self.max_backups]:
                backup.unlink()
    
    def _maybe_checkpoint(self):
        """Checkpoint if enough time has passed or significant changes."""
        if not self.enable_auto_checkpoint:
            return
        
        elapsed = (datetime.now() - self._last_checkpoint).total_seconds()
        if elapsed >= self.checkpoint_interval:
            if self._current_state:
                self.save_execution_state(self._current_state)
    
    def _auto_checkpoint_loop(self):
        """Background thread for automatic checkpointing."""
        while not self._stop_checkpoint.is_set():
            try:
                # Wait for checkpoint interval
                self._stop_checkpoint.wait(self.checkpoint_interval)
                
                if not self._stop_checkpoint.is_set() and self._current_state:
                    with self._state_lock:
                        self.save_execution_state(self._current_state)
                        
            except Exception as e:
                print(f"Error in auto-checkpoint: {e}")
    
    def _start_auto_checkpoint(self):
        """Start the auto-checkpoint thread."""
        self._checkpoint_thread = threading.Thread(
            target=self._auto_checkpoint_loop,
            daemon=True
        )
        self._checkpoint_thread.start()
    
    def stop(self):
        """Stop the state manager and save final state."""
        self._stop_checkpoint.set()
        
        if self._checkpoint_thread:
            self._checkpoint_thread.join(timeout=5)
        
        # Final checkpoint
        if self._current_state:
            self.save_execution_state(self._current_state)