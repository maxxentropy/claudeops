"""
Resource lock manager for parallel PRD execution.

This module provides the infrastructure for managing file and resource locks
to prevent conflicts when multiple agents are working in parallel.
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, Set, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

from models.parallel_execution import ResourceLock, LockType


class LockError(Exception):
    """Base exception for lock-related errors."""
    pass


class LockConflictError(LockError):
    """Raised when a lock cannot be acquired due to conflicts."""
    pass


class LockTimeoutError(LockError):
    """Raised when a lock operation times out."""
    pass


@dataclass
class LockRequest:
    """Request to acquire a lock on a resource."""
    resource_path: str
    phase_id: str
    lock_type: LockType
    timeout_seconds: Optional[int] = None
    
    def normalize_path(self) -> str:
        """Normalize the resource path for consistent locking."""
        return str(Path(self.resource_path).resolve())


class FileLock:
    """
    Thread-safe file lock implementation.
    
    Supports both shared (read) and exclusive (write) locks with
    timeout and automatic cleanup.
    """
    
    def __init__(self, resource_path: str, phase_id: str, 
                 lock_type: LockType = LockType.EXCLUSIVE,
                 timeout_seconds: int = 300):
        """
        Initialize a file lock.
        
        Args:
            resource_path: Path to the resource to lock
            phase_id: ID of the phase requesting the lock
            lock_type: Type of lock (shared or exclusive)
            timeout_seconds: Lock timeout in seconds
        """
        self.resource_path = str(Path(resource_path).resolve())
        self.phase_id = phase_id
        self.lock_type = lock_type
        self.timeout_seconds = timeout_seconds
        self._lock = threading.RLock()
        self._acquired = False
        self._lock_time: Optional[datetime] = None
        self._expires_at: Optional[datetime] = None
    
    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire the lock.
        
        Args:
            blocking: Whether to block until lock is available
            timeout: Maximum time to wait for lock (seconds)
            
        Returns:
            True if lock was acquired, False otherwise
            
        Raises:
            LockTimeoutError: If timeout is exceeded
        """
        with self._lock:
            if self._acquired:
                return True
            
            start_time = time.time()
            while True:
                # Check with lock registry if we can acquire
                if LockRegistry.instance().can_acquire(self.resource_path, 
                                                      self.phase_id, 
                                                      self.lock_type):
                    # Register the lock
                    lock = ResourceLock(
                        resource_path=self.resource_path,
                        owner_phase=self.phase_id,
                        lock_type=self.lock_type,
                        lock_time=datetime.now()
                    )
                    
                    if self.timeout_seconds:
                        lock.expires_at = lock.lock_time + timedelta(seconds=self.timeout_seconds)
                    
                    if LockRegistry.instance().acquire_lock(lock):
                        self._acquired = True
                        self._lock_time = lock.lock_time
                        self._expires_at = lock.expires_at
                        return True
                
                if not blocking:
                    return False
                
                # Check timeout
                if timeout and (time.time() - start_time) >= timeout:
                    raise LockTimeoutError(
                        f"Failed to acquire lock on {self.resource_path} "
                        f"for phase {self.phase_id} within {timeout} seconds"
                    )
                
                # Brief sleep before retry
                time.sleep(0.1)
    
    def release(self):
        """Release the lock."""
        with self._lock:
            if self._acquired:
                LockRegistry.instance().release_lock(self.resource_path, self.phase_id)
                self._acquired = False
                self._lock_time = None
                self._expires_at = None
    
    def is_acquired(self) -> bool:
        """Check if lock is currently acquired."""
        return self._acquired
    
    def is_expired(self) -> bool:
        """Check if lock has expired."""
        if not self._acquired or not self._expires_at:
            return False
        return datetime.now() > self._expires_at
    
    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


class LockRegistry:
    """
    Central registry for tracking all active locks.
    
    This is a singleton that maintains the global state of all
    resource locks across all phases and agents.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize the lock registry."""
        self._registry_lock = threading.RLock()
        # Map resource paths to active locks
        self._locks: Dict[str, List[ResourceLock]] = defaultdict(list)
        # Map phase IDs to their held locks
        self._phase_locks: Dict[str, Set[str]] = defaultdict(set)
    
    @classmethod
    def instance(cls) -> 'LockRegistry':
        """Get the singleton instance of LockRegistry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def can_acquire(self, resource_path: str, phase_id: str, 
                   lock_type: LockType) -> bool:
        """
        Check if a lock can be acquired on a resource.
        
        Rules:
        - Multiple shared locks are allowed
        - Exclusive lock requires no other locks
        - Same phase can upgrade shared to exclusive
        """
        with self._registry_lock:
            resource_path = str(Path(resource_path).resolve())
            active_locks = self._get_active_locks(resource_path)
            
            if not active_locks:
                return True
            
            # Check if phase already has a lock
            phase_locks = [l for l in active_locks if l.owner_phase == phase_id]
            if phase_locks:
                # Same phase can always re-acquire or upgrade
                if lock_type == LockType.EXCLUSIVE and len(active_locks) > 1:
                    # Can't upgrade to exclusive if others have locks
                    return False
                return True
            
            # New lock request
            if lock_type == LockType.EXCLUSIVE:
                # Exclusive requires no other locks
                return False
            
            # Shared lock - check if all existing locks are shared
            return all(l.lock_type == LockType.SHARED for l in active_locks)
    
    def acquire_lock(self, lock: ResourceLock) -> bool:
        """
        Acquire a lock on a resource.
        
        Returns:
            True if lock was acquired, False otherwise
        """
        with self._registry_lock:
            if not self.can_acquire(lock.resource_path, lock.owner_phase, lock.lock_type):
                return False
            
            # Remove any existing lock by same phase (for upgrades)
            self._remove_phase_lock(lock.resource_path, lock.owner_phase)
            
            # Add new lock
            self._locks[lock.resource_path].append(lock)
            self._phase_locks[lock.owner_phase].add(lock.resource_path)
            
            return True
    
    def release_lock(self, resource_path: str, phase_id: str):
        """Release a lock held by a phase."""
        with self._registry_lock:
            resource_path = str(Path(resource_path).resolve())
            self._remove_phase_lock(resource_path, phase_id)
    
    def release_all_phase_locks(self, phase_id: str):
        """Release all locks held by a phase."""
        with self._registry_lock:
            # Get copy of paths to avoid modification during iteration
            paths = list(self._phase_locks.get(phase_id, set()))
            for path in paths:
                self._remove_phase_lock(path, phase_id)
    
    def get_active_locks(self, resource_path: Optional[str] = None) -> List[ResourceLock]:
        """
        Get list of active locks, optionally filtered by resource.
        
        Args:
            resource_path: If provided, only return locks for this resource
            
        Returns:
            List of active locks
        """
        with self._registry_lock:
            if resource_path:
                resource_path = str(Path(resource_path).resolve())
                return self._get_active_locks(resource_path).copy()
            
            # Return all active locks
            all_locks = []
            for locks in self._locks.values():
                all_locks.extend(l for l in locks if not l.is_expired())
            return all_locks
    
    def get_phase_locks(self, phase_id: str) -> List[ResourceLock]:
        """Get all locks held by a specific phase."""
        with self._registry_lock:
            locks = []
            for path in self._phase_locks.get(phase_id, set()):
                phase_locks = [
                    l for l in self._locks.get(path, [])
                    if l.owner_phase == phase_id and not l.is_expired()
                ]
                locks.extend(phase_locks)
            return locks
    
    def detect_conflicts(self, request: LockRequest) -> List[ResourceLock]:
        """
        Detect any conflicts for a lock request.
        
        Returns:
            List of conflicting locks
        """
        with self._registry_lock:
            if self.can_acquire(request.resource_path, request.phase_id, request.lock_type):
                return []
            
            # Return the conflicting locks
            active_locks = self._get_active_locks(request.resource_path)
            
            # Filter out locks from same phase (not conflicts)
            conflicts = [l for l in active_locks if l.owner_phase != request.phase_id]
            
            # For shared requests, only exclusive locks are conflicts
            if request.lock_type == LockType.SHARED:
                conflicts = [l for l in conflicts if l.lock_type == LockType.EXCLUSIVE]
            
            return conflicts
    
    def cleanup_expired_locks(self):
        """Remove all expired locks from the registry."""
        with self._registry_lock:
            for resource_path in list(self._locks.keys()):
                # Remove expired locks
                active_locks = self._get_active_locks(resource_path)
                self._locks[resource_path] = active_locks
                
                # Clean up empty entries
                if not self._locks[resource_path]:
                    del self._locks[resource_path]
            
            # Clean up phase_locks mapping
            for phase_id in list(self._phase_locks.keys()):
                # Remove paths that no longer have locks for this phase
                valid_paths = set()
                for path in self._phase_locks[phase_id]:
                    if any(l.owner_phase == phase_id for l in self._locks.get(path, [])):
                        valid_paths.add(path)
                
                if valid_paths:
                    self._phase_locks[phase_id] = valid_paths
                else:
                    del self._phase_locks[phase_id]
    
    def _get_active_locks(self, resource_path: str) -> List[ResourceLock]:
        """Get active (non-expired) locks for a resource."""
        locks = self._locks.get(resource_path, [])
        return [l for l in locks if not l.is_expired()]
    
    def _remove_phase_lock(self, resource_path: str, phase_id: str):
        """Remove a specific phase's lock on a resource."""
        if resource_path in self._locks:
            self._locks[resource_path] = [
                l for l in self._locks[resource_path]
                if l.owner_phase != phase_id
            ]
            
            if not self._locks[resource_path]:
                del self._locks[resource_path]
        
        if phase_id in self._phase_locks:
            self._phase_locks[phase_id].discard(resource_path)
            if not self._phase_locks[phase_id]:
                del self._phase_locks[phase_id]
    
    def get_stats(self) -> Dict[str, any]:
        """Get statistics about current lock state."""
        with self._registry_lock:
            self.cleanup_expired_locks()
            
            total_locks = sum(len(locks) for locks in self._locks.values())
            shared_locks = sum(
                1 for locks in self._locks.values()
                for lock in locks if lock.lock_type == LockType.SHARED
            )
            exclusive_locks = total_locks - shared_locks
            
            return {
                "total_active_locks": total_locks,
                "shared_locks": shared_locks,
                "exclusive_locks": exclusive_locks,
                "locked_resources": len(self._locks),
                "phases_with_locks": len(self._phase_locks)
            }