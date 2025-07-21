"""
State management models for parallel PRD execution.

This module defines the state tracking and management structures used
to monitor and control the execution of phases across multiple agents.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum, auto


class PhaseStatus(Enum):
    """Enumeration of possible phase execution states."""
    NOT_STARTED = "not_started"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # Waiting for dependencies
    CANCELLED = "cancelled"
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal state (no further transitions)."""
        return self in {self.COMPLETED, self.FAILED, self.CANCELLED}
    
    def is_active(self) -> bool:
        """Check if this represents active execution."""
        return self in {self.IN_PROGRESS, self.QUEUED}


class AgentStatus(Enum):
    """Status of an execution agent."""
    IDLE = "idle"
    ASSIGNED = "assigned"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class PhaseExecutionDetails:
    """Detailed information about a phase's execution."""
    phase_id: str
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    agent_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    output_files: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def mark_started(self, agent_id: str):
        """Mark phase as started by an agent."""
        self.status = PhaseStatus.IN_PROGRESS
        self.agent_id = agent_id
        self.start_time = datetime.now()
    
    def mark_completed(self, output_files: List[str] = None):
        """Mark phase as successfully completed."""
        self.status = PhaseStatus.COMPLETED
        self.end_time = datetime.now()
        if output_files:
            self.output_files.extend(output_files)
    
    def mark_failed(self, error_message: str):
        """Mark phase as failed with error message."""
        self.status = PhaseStatus.FAILED
        self.end_time = datetime.now()
        self.error_message = error_message
        self.retry_count += 1


@dataclass
class AgentInfo:
    """
    Information about an execution agent.
    
    Attributes:
        agent_id: Unique identifier for the agent
        assigned_phase: Currently assigned phase ID (if any)
        status: Current agent status
        logs: List of log entries from this agent
        created_at: When the agent was created
        terminated_at: When the agent was terminated (if applicable)
    """
    agent_id: str
    assigned_phase: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    logs: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    terminated_at: Optional[datetime] = None
    
    def assign_phase(self, phase_id: str):
        """Assign a phase to this agent."""
        self.assigned_phase = phase_id
        self.status = AgentStatus.ASSIGNED
        self.add_log("info", f"Assigned to phase: {phase_id}")
    
    def start_work(self):
        """Mark agent as actively working."""
        self.status = AgentStatus.WORKING
        self.add_log("info", f"Started work on phase: {self.assigned_phase}")
    
    def complete_work(self):
        """Mark agent as having completed its work."""
        self.status = AgentStatus.COMPLETED
        self.add_log("info", f"Completed phase: {self.assigned_phase}")
        self.assigned_phase = None
    
    def report_error(self, error_message: str):
        """Report an error and mark agent as errored."""
        self.status = AgentStatus.ERROR
        self.add_log("error", error_message)
    
    def terminate(self):
        """Terminate this agent."""
        self.status = AgentStatus.TERMINATED
        self.terminated_at = datetime.now()
        self.add_log("info", "Agent terminated")
    
    def add_log(self, level: str, message: str, metadata: Dict[str, Any] = None):
        """Add a log entry for this agent."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "metadata": metadata or {}
        }
        self.logs.append(log_entry)
    
    def is_available(self) -> bool:
        """Check if agent is available for new work."""
        return self.status in {AgentStatus.IDLE, AgentStatus.COMPLETED}


@dataclass
class ExecutionState:
    """
    Overall execution state for the parallel PRD implementation.
    
    Tracks the state of all phases, waves, and agents involved
    in the execution.
    """
    phase_states: Dict[str, PhaseExecutionDetails] = field(default_factory=dict)
    waves: List['ExecutionWave'] = field(default_factory=list)
    agents: Dict[str, AgentInfo] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    def add_phase(self, phase_id: str):
        """Add a phase to track."""
        if phase_id not in self.phase_states:
            self.phase_states[phase_id] = PhaseExecutionDetails(phase_id)
    
    def get_phase_status(self, phase_id: str) -> PhaseStatus:
        """Get the current status of a phase."""
        if phase_id in self.phase_states:
            return self.phase_states[phase_id].status
        return PhaseStatus.NOT_STARTED
    
    def update_phase_status(self, phase_id: str, status: PhaseStatus):
        """Update the status of a phase."""
        if phase_id in self.phase_states:
            self.phase_states[phase_id].status = status
    
    def add_agent(self, agent: AgentInfo):
        """Register a new agent."""
        self.agents[agent.agent_id] = agent
    
    def get_available_agents(self) -> List[AgentInfo]:
        """Get list of agents available for work."""
        return [
            agent for agent in self.agents.values()
            if agent.is_available()
        ]
    
    def get_active_phases(self) -> List[str]:
        """Get list of currently executing phases."""
        return [
            phase_id for phase_id, details in self.phase_states.items()
            if details.status == PhaseStatus.IN_PROGRESS
        ]
    
    def get_completed_phases(self) -> List[str]:
        """Get list of completed phases."""
        return [
            phase_id for phase_id, details in self.phase_states.items()
            if details.status == PhaseStatus.COMPLETED
        ]
    
    def get_failed_phases(self) -> List[str]:
        """Get list of failed phases."""
        return [
            phase_id for phase_id, details in self.phase_states.items()
            if details.status == PhaseStatus.FAILED
        ]
    
    def is_complete(self) -> bool:
        """Check if all phases are in a terminal state."""
        return all(
            details.status.is_terminal()
            for details in self.phase_states.values()
        )
    
    def calculate_progress(self) -> float:
        """Calculate overall progress as a percentage."""
        if not self.phase_states:
            return 0.0
        
        completed = len(self.get_completed_phases())
        total = len(self.phase_states)
        return (completed / total) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary statistics."""
        return {
            "total_phases": len(self.phase_states),
            "completed": len(self.get_completed_phases()),
            "failed": len(self.get_failed_phases()),
            "active": len(self.get_active_phases()),
            "progress_percent": self.calculate_progress(),
            "active_agents": len([a for a in self.agents.values() if a.status == AgentStatus.WORKING]),
            "total_agents": len(self.agents),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds()
                if self.start_time and self.end_time else None
            )
        }