"""
Core data structures for parallel PRD execution system.

This module defines the foundational models used throughout the parallel
execution system, including phase information, dependency graphs, execution
waves, and resource locks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from datetime import datetime
from enum import Enum


class LockType(Enum):
    """Types of resource locks."""
    SHARED = "shared"      # Multiple readers allowed
    EXCLUSIVE = "exclusive"  # Single writer only


@dataclass
class PhaseInfo:
    """
    Represents information about a single phase in the PRD.
    
    Attributes:
        id: Unique identifier for the phase (e.g., "phase-1")
        name: Human-readable name for the phase
        dependencies: List of phase IDs this phase depends on
        outputs: List of expected output files/resources
        estimated_time: Estimated time in hours to complete
        description: Brief description of the phase
    """
    id: str
    name: str
    dependencies: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    estimated_time: float = 1.0
    description: str = ""
    
    def __hash__(self):
        """Make PhaseInfo hashable for use in sets."""
        return hash(self.id)
    
    def __eq__(self, other):
        """Equality based on phase ID."""
        if isinstance(other, PhaseInfo):
            return self.id == other.id
        return False


@dataclass
class DependencyEdge:
    """Represents a dependency relationship between phases."""
    from_phase: str
    to_phase: str
    description: str = ""


@dataclass
class DependencyGraph:
    """
    Represents the complete dependency graph for all phases.
    
    The graph is stored as an adjacency list where:
    - nodes: Dictionary mapping phase IDs to PhaseInfo objects
    - edges: Dictionary mapping phase IDs to sets of dependent phase IDs
    - reverse_edges: Dictionary mapping phase IDs to sets of phases that depend on it
    """
    nodes: Dict[str, PhaseInfo] = field(default_factory=dict)
    edges: Dict[str, Set[str]] = field(default_factory=dict)
    reverse_edges: Dict[str, Set[str]] = field(default_factory=dict)
    
    def add_phase(self, phase: PhaseInfo):
        """Add a phase to the dependency graph."""
        self.nodes[phase.id] = phase
        if phase.id not in self.edges:
            self.edges[phase.id] = set()
        if phase.id not in self.reverse_edges:
            self.reverse_edges[phase.id] = set()
        
        # Add edges based on dependencies
        for dep_id in phase.dependencies:
            if dep_id not in self.edges:
                self.edges[dep_id] = set()
            self.edges[dep_id].add(phase.id)
            
            if phase.id not in self.reverse_edges:
                self.reverse_edges[phase.id] = set()
            self.reverse_edges[phase.id].add(dep_id)
    
    def get_phase(self, phase_id: str) -> Optional[PhaseInfo]:
        """Get phase info by ID."""
        return self.nodes.get(phase_id)
    
    def get_dependents(self, phase_id: str) -> Set[str]:
        """Get all phases that depend on the given phase."""
        return self.edges.get(phase_id, set())
    
    def get_dependencies(self, phase_id: str) -> Set[str]:
        """Get all phases that the given phase depends on."""
        return self.reverse_edges.get(phase_id, set())
    
    def get_root_phases(self) -> List[PhaseInfo]:
        """Get all phases with no dependencies (can start immediately)."""
        return [
            phase for phase in self.nodes.values()
            if not phase.dependencies
        ]


@dataclass
class ExecutionWave:
    """
    Represents a wave of phases that can be executed in parallel.
    
    Attributes:
        wave_number: Sequential number of this wave (0-based)
        phases: List of phase IDs that can execute in this wave
        start_time: When this wave started execution
        end_time: When this wave completed execution
        status: Current status of the wave
    """
    wave_number: int
    phases: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"
    
    def add_phase(self, phase_id: str):
        """Add a phase to this wave."""
        if phase_id not in self.phases:
            self.phases.append(phase_id)
    
    def remove_phase(self, phase_id: str):
        """Remove a phase from this wave."""
        if phase_id in self.phases:
            self.phases.remove(phase_id)
    
    def is_complete(self) -> bool:
        """Check if this wave has completed execution."""
        return self.status == "completed"
    
    def is_active(self) -> bool:
        """Check if this wave is currently executing."""
        return self.status == "in_progress"


@dataclass
class ResourceLock:
    """
    Represents a lock on a file or resource.
    
    Attributes:
        resource_path: Path to the locked resource
        owner_phase: ID of the phase holding the lock
        lock_time: When the lock was acquired
        lock_type: Type of lock (shared or exclusive)
        expires_at: When the lock expires (if timeout is set)
    """
    resource_path: str
    owner_phase: str
    lock_time: datetime = field(default_factory=datetime.now)
    lock_type: LockType = LockType.EXCLUSIVE
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if this lock has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def is_shared(self) -> bool:
        """Check if this is a shared lock."""
        return self.lock_type == LockType.SHARED
    
    def is_exclusive(self) -> bool:
        """Check if this is an exclusive lock."""
        return self.lock_type == LockType.EXCLUSIVE
    
    def __str__(self):
        """String representation of the lock."""
        return (
            f"ResourceLock({self.resource_path}, "
            f"owner={self.owner_phase}, type={self.lock_type.value})"
        )