"""
Advanced resource coordination for parallel PRD execution.

This module extends the base resource manager with distributed locking,
deadlock detection, and conflict resolution capabilities.
"""

import os
import time
import fcntl
import threading
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from models.parallel_execution import ResourceLock, LockType, PhaseInfo
from core.resource_manager import LockRegistry, LockRequest, FileLock, LockConflictError


class ConflictResolution(Enum):
    """Strategies for resolving resource conflicts."""
    WAIT = "wait"                # Wait for resource to become available
    PREEMPT = "preempt"          # Preempt lower priority phase
    SHARE = "share"              # Convert to shared access if possible
    DEFER = "defer"              # Defer phase to later wave
    FAIL = "fail"                # Fail the phase


@dataclass
class ResourceConflict:
    """Information about a resource conflict."""
    requesting_phase: str
    conflicting_phase: str
    resource_path: str
    conflict_type: str  # "exclusive_held", "shared_upgrade", etc.
    detected_at: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        return (
            f"ResourceConflict: {self.requesting_phase} wants {self.resource_path} "
            f"but blocked by {self.conflicting_phase} ({self.conflict_type})"
        )


@dataclass
class Deadlock:
    """Information about a detected deadlock."""
    phases_involved: List[str]
    resources_involved: List[str]
    cycle_path: List[Tuple[str, str]]  # [(phase1, resource1), (phase2, resource2), ...]
    detected_at: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        cycle_str = " -> ".join([f"{p} waits for {r}" for p, r in self.cycle_path])
        return f"Deadlock detected: {cycle_str}"


class DistributedLock:
    """
    File-based distributed lock for cross-process synchronization.
    
    Uses file locking primitives to ensure locks work across multiple
    agent processes.
    """
    
    def __init__(self, lock_file_path: Path, phase_id: str, 
                 lock_type: LockType = LockType.EXCLUSIVE):
        """
        Initialize a distributed lock.
        
        Args:
            lock_file_path: Path to the lock file
            phase_id: ID of the phase requesting the lock
            lock_type: Type of lock (shared or exclusive)
        """
        self.lock_file_path = lock_file_path
        self.phase_id = phase_id
        self.lock_type = lock_type
        self._file_handle = None
        self._acquired = False
        
        # Ensure lock directory exists
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire the distributed lock.
        
        Args:
            blocking: Whether to block until lock is available
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if lock was acquired
        """
        if self._acquired:
            return True
        
        start_time = time.time()
        
        # Open or create lock file
        mode = 'a+' if self.lock_type == LockType.SHARED else 'w+'
        self._file_handle = open(self.lock_file_path, mode)
        
        # Determine lock flags
        if self.lock_type == LockType.EXCLUSIVE:
            lock_flags = fcntl.LOCK_EX
        else:
            lock_flags = fcntl.LOCK_SH
        
        if not blocking:
            lock_flags |= fcntl.LOCK_NB
        
        while True:
            try:
                fcntl.flock(self._file_handle.fileno(), lock_flags)
                self._acquired = True
                
                # Write lock info
                self._file_handle.seek(0)
                self._file_handle.write(f"{self.phase_id}:{self.lock_type.value}\n")
                self._file_handle.flush()
                
                return True
                
            except BlockingIOError:
                if not blocking:
                    self._cleanup()
                    return False
                
                # Check timeout
                if timeout and (time.time() - start_time) >= timeout:
                    self._cleanup()
                    return False
                
                time.sleep(0.1)
            
            except Exception:
                self._cleanup()
                raise
    
    def release(self):
        """Release the distributed lock."""
        if self._acquired and self._file_handle:
            try:
                fcntl.flock(self._file_handle.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
            finally:
                self._cleanup()
    
    def _cleanup(self):
        """Clean up file handle."""
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception:
                pass
            self._file_handle = None
        self._acquired = False
    
    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


class ResourceCoordinator:
    """
    Advanced resource coordination with distributed locking and deadlock detection.
    
    Extends the base resource manager with:
    - File-based distributed locks for cross-process synchronization
    - Deadlock detection using wait-for graphs
    - Conflict resolution strategies
    - Priority-based resource allocation
    """
    
    def __init__(self, workspace: str, config: Dict[str, Any]):
        """
        Initialize the resource coordinator.
        
        Args:
            workspace: Path to the workspace
            config: Configuration dictionary
        """
        self.workspace = Path(workspace)
        self.config = config
        
        # Configuration
        self.enable_deadlock_detection = config.get("enable_deadlock_detection", True)
        self.deadlock_check_interval = config.get("deadlock_check_interval", 10)
        self.lock_timeout = config.get("default_lock_timeout", 300)
        self.conflict_resolution = config.get("conflict_resolution", "wait")
        
        # Distributed lock directory
        self.lock_dir = self.workspace / ".locks"
        self.lock_dir.mkdir(exist_ok=True)
        
        # Tracking
        self._wait_graph: Dict[str, Set[str]] = defaultdict(set)  # phase -> waiting for phases
        self._resource_waiters: Dict[str, Set[str]] = defaultdict(set)  # resource -> waiting phases
        self._phase_priorities: Dict[str, int] = {}  # phase -> priority
        self._conflicts: List[ResourceConflict] = []
        self._deadlocks: List[Deadlock] = []
        self._lock = threading.RLock()
        
        # Start deadlock detection thread
        self._deadlock_thread = None
        self._stop_deadlock_detection = threading.Event()
        if self.enable_deadlock_detection:
            self._start_deadlock_detection()
    
    def acquire_resources_for_phase(self, phase_id: str, resources: List[str],
                                   lock_types: Optional[Dict[str, LockType]] = None) -> List[ResourceLock]:
        """
        Acquire multiple resources for a phase atomically.
        
        Args:
            phase_id: ID of the phase requesting resources
            resources: List of resource paths
            lock_types: Optional mapping of resources to lock types
            
        Returns:
            List of acquired ResourceLock objects
            
        Raises:
            LockConflictError: If resources cannot be acquired
        """
        if not lock_types:
            lock_types = {r: LockType.EXCLUSIVE for r in resources}
        
        acquired_locks = []
        
        try:
            # Sort resources to prevent deadlock (consistent ordering)
            sorted_resources = sorted(resources)
            
            for resource in sorted_resources:
                lock_type = lock_types.get(resource, LockType.EXCLUSIVE)
                
                # Try to acquire with conflict detection
                lock = self._acquire_resource_with_conflict_handling(
                    phase_id, resource, lock_type
                )
                
                if lock:
                    acquired_locks.append(lock)
                else:
                    # Failed to acquire, rollback
                    raise LockConflictError(
                        f"Failed to acquire {resource} for phase {phase_id}"
                    )
            
            return acquired_locks
            
        except Exception as e:
            # Rollback any acquired locks
            self.release_phase_resources(phase_id)
            raise
    
    def release_phase_resources(self, phase_id: str):
        """
        Release all resources held by a phase.
        
        Args:
            phase_id: ID of the phase
        """
        with self._lock:
            # Release from lock registry
            LockRegistry.instance().release_all_phase_locks(phase_id)
            
            # Clean up distributed locks
            phase_lock_files = list(self.lock_dir.glob(f"*_{phase_id}.lock"))
            for lock_file in phase_lock_files:
                try:
                    lock_file.unlink()
                except Exception:
                    pass
            
            # Update wait graph
            self._remove_from_wait_graph(phase_id)
    
    def resolve_lock_conflict(self, conflict: ResourceConflict) -> ConflictResolution:
        """
        Determine how to resolve a resource conflict.
        
        Args:
            conflict: The resource conflict to resolve
            
        Returns:
            ConflictResolution strategy
        """
        resolution_strategy = self.conflict_resolution
        
        if resolution_strategy == "preempt":
            # Check if we can preempt based on priority
            req_priority = self._phase_priorities.get(conflict.requesting_phase, 0)
            conf_priority = self._phase_priorities.get(conflict.conflicting_phase, 0)
            
            if req_priority > conf_priority:
                return ConflictResolution.PREEMPT
            else:
                return ConflictResolution.WAIT
        
        elif resolution_strategy == "share":
            # Try to convert to shared access
            if conflict.conflict_type == "exclusive_held":
                return ConflictResolution.WAIT
            else:
                return ConflictResolution.SHARE
        
        elif resolution_strategy == "defer":
            return ConflictResolution.DEFER
        
        elif resolution_strategy == "fail":
            return ConflictResolution.FAIL
        
        else:  # default to wait
            return ConflictResolution.WAIT
    
    def monitor_deadlocks(self) -> List[Deadlock]:
        """
        Check for deadlocks in the current wait graph.
        
        Returns:
            List of detected deadlocks
        """
        with self._lock:
            deadlocks = self._detect_cycles_in_wait_graph()
            self._deadlocks.extend(deadlocks)
            return deadlocks
    
    def set_phase_priority(self, phase_id: str, priority: int):
        """
        Set priority for a phase (higher number = higher priority).
        
        Args:
            phase_id: ID of the phase
            priority: Priority value
        """
        with self._lock:
            self._phase_priorities[phase_id] = priority
    
    def get_resource_conflicts(self) -> List[ResourceConflict]:
        """Get list of current resource conflicts."""
        with self._lock:
            return self._conflicts.copy()
    
    def get_deadlocks(self) -> List[Deadlock]:
        """Get list of detected deadlocks."""
        with self._lock:
            return self._deadlocks.copy()
    
    def _acquire_resource_with_conflict_handling(self, phase_id: str, 
                                                resource: str, 
                                                lock_type: LockType) -> Optional[ResourceLock]:
        """
        Try to acquire a resource with conflict handling.
        
        Args:
            phase_id: ID of the requesting phase
            resource: Resource path
            lock_type: Type of lock requested
            
        Returns:
            ResourceLock if acquired, None otherwise
        """
        # First try with the lock registry
        lock_request = LockRequest(
            resource_path=resource,
            phase_id=phase_id,
            lock_type=lock_type,
            timeout_seconds=self.lock_timeout
        )
        
        # Check for conflicts
        conflicts = LockRegistry.instance().detect_conflicts(lock_request)
        
        if conflicts:
            # Record conflict
            for conf_lock in conflicts:
                conflict = ResourceConflict(
                    requesting_phase=phase_id,
                    conflicting_phase=conf_lock.owner_phase,
                    resource_path=resource,
                    conflict_type="exclusive_held" if conf_lock.is_exclusive() else "shared_held"
                )
                self._conflicts.append(conflict)
                
                # Update wait graph
                with self._lock:
                    self._wait_graph[phase_id].add(conf_lock.owner_phase)
                    self._resource_waiters[resource].add(phase_id)
                
                # Resolve conflict
                resolution = self.resolve_lock_conflict(conflict)
                
                if resolution == ConflictResolution.WAIT:
                    # Try to acquire with timeout
                    file_lock = FileLock(resource, phase_id, lock_type, self.lock_timeout)
                    if file_lock.acquire(blocking=True, timeout=self.lock_timeout):
                        return ResourceLock(
                            resource_path=resource,
                            owner_phase=phase_id,
                            lock_type=lock_type
                        )
                    return None
                
                elif resolution == ConflictResolution.PREEMPT:
                    # Force release the conflicting lock
                    LockRegistry.instance().release_lock(resource, conf_lock.owner_phase)
                    # Try again
                    return self._acquire_resource_with_conflict_handling(
                        phase_id, resource, lock_type
                    )
                
                elif resolution == ConflictResolution.SHARE:
                    # Try with shared lock instead
                    if lock_type == LockType.EXCLUSIVE:
                        return self._acquire_resource_with_conflict_handling(
                            phase_id, resource, LockType.SHARED
                        )
                    return None
                
                else:  # DEFER or FAIL
                    return None
        
        # No conflicts, acquire normally
        file_lock = FileLock(resource, phase_id, lock_type, self.lock_timeout)
        if file_lock.acquire(blocking=False):
            # Also create distributed lock file
            dist_lock_path = self.lock_dir / f"{Path(resource).name}_{phase_id}.lock"
            dist_lock = DistributedLock(dist_lock_path, phase_id, lock_type)
            dist_lock.acquire(blocking=False)
            
            return ResourceLock(
                resource_path=resource,
                owner_phase=phase_id,
                lock_type=lock_type
            )
        
        return None
    
    def _remove_from_wait_graph(self, phase_id: str):
        """Remove a phase from the wait graph."""
        # Remove as waiter
        if phase_id in self._wait_graph:
            del self._wait_graph[phase_id]
        
        # Remove from other phases' wait lists
        for waiting_phases in self._wait_graph.values():
            waiting_phases.discard(phase_id)
        
        # Remove from resource waiters
        for waiters in self._resource_waiters.values():
            waiters.discard(phase_id)
    
    def _detect_cycles_in_wait_graph(self) -> List[Deadlock]:
        """
        Detect cycles in the wait-for graph using DFS.
        
        Returns:
            List of detected deadlocks
        """
        deadlocks = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(phase: str) -> Optional[List[str]]:
            visited.add(phase)
            rec_stack.add(phase)
            path.append(phase)
            
            for waiting_for in self._wait_graph.get(phase, set()):
                if waiting_for not in visited:
                    cycle = dfs(waiting_for)
                    if cycle:
                        return cycle
                elif waiting_for in rec_stack:
                    # Found cycle
                    cycle_start = path.index(waiting_for)
                    return path[cycle_start:]
            
            path.pop()
            rec_stack.remove(phase)
            return None
        
        # Check each phase
        for phase in list(self._wait_graph.keys()):
            if phase not in visited:
                cycle = dfs(phase)
                if cycle:
                    # Build deadlock info
                    cycle_path = []
                    resources = []
                    
                    for i in range(len(cycle)):
                        curr_phase = cycle[i]
                        next_phase = cycle[(i + 1) % len(cycle)]
                        
                        # Find resource causing the wait
                        for resource, waiters in self._resource_waiters.items():
                            if curr_phase in waiters:
                                cycle_path.append((curr_phase, resource))
                                resources.append(resource)
                                break
                    
                    deadlock = Deadlock(
                        phases_involved=cycle,
                        resources_involved=resources,
                        cycle_path=cycle_path
                    )
                    deadlocks.append(deadlock)
        
        return deadlocks
    
    def _deadlock_detection_loop(self):
        """Background thread for periodic deadlock detection."""
        while not self._stop_deadlock_detection.is_set():
            try:
                deadlocks = self.monitor_deadlocks()
                
                if deadlocks:
                    # Log deadlocks
                    for deadlock in deadlocks:
                        print(f"WARNING: {deadlock}")
                    
                    # Attempt to resolve (simplest: fail one phase)
                    for deadlock in deadlocks:
                        if deadlock.phases_involved:
                            # Release resources of first phase in cycle
                            victim = deadlock.phases_involved[0]
                            self.release_phase_resources(victim)
                
            except Exception as e:
                print(f"Error in deadlock detection: {e}")
            
            # Wait before next check
            self._stop_deadlock_detection.wait(self.deadlock_check_interval)
    
    def _start_deadlock_detection(self):
        """Start the deadlock detection thread."""
        self._deadlock_thread = threading.Thread(
            target=self._deadlock_detection_loop,
            daemon=True
        )
        self._deadlock_thread.start()
    
    def stop(self):
        """Stop the resource coordinator."""
        self._stop_deadlock_detection.set()
        if self._deadlock_thread:
            self._deadlock_thread.join(timeout=5)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get resource coordination statistics."""
        with self._lock:
            registry_stats = LockRegistry.instance().get_stats()
            
            return {
                "registry_stats": registry_stats,
                "active_conflicts": len(self._conflicts),
                "total_deadlocks": len(self._deadlocks),
                "phases_waiting": len(self._wait_graph),
                "distributed_locks": len(list(self.lock_dir.glob("*.lock"))),
                "wait_graph_size": sum(len(waiters) for waiters in self._wait_graph.values())
            }