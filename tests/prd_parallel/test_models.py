"""
Unit tests for all Phase 1 models.

This module provides comprehensive test coverage for:
- Core data structures (parallel_execution.py)
- State management models (execution_state.py)
- Resource lock manager (resource_manager.py)
- Configuration schema (parallel_config.py)
"""

import unittest
import time
import threading
import os
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))

from prd_parallel.models.parallel_execution import (
    PhaseInfo, DependencyGraph, ExecutionWave, ResourceLock, LockType
)
from prd_parallel.models.execution_state import (
    PhaseStatus, AgentStatus, PhaseExecutionDetails, AgentInfo, ExecutionState
)
from prd_parallel.core.resource_manager import (
    FileLock, LockRegistry, LockRequest, LockConflictError, LockTimeoutError
)
from prd_parallel.config.parallel_config import ParallelExecutionConfig, get_default_config


class TestPhaseInfo(unittest.TestCase):
    """Test PhaseInfo model."""
    
    def test_phase_creation(self):
        """Test creating a phase with all attributes."""
        phase = PhaseInfo(
            id="phase-1",
            name="Foundation",
            dependencies=["phase-0"],
            outputs=["models.py", "config.py"],
            estimated_time=1.5,
            description="Build foundation models"
        )
        
        self.assertEqual(phase.id, "phase-1")
        self.assertEqual(phase.name, "Foundation")
        self.assertEqual(phase.dependencies, ["phase-0"])
        self.assertEqual(phase.outputs, ["models.py", "config.py"])
        self.assertEqual(phase.estimated_time, 1.5)
        self.assertEqual(phase.description, "Build foundation models")
    
    def test_phase_defaults(self):
        """Test phase creation with defaults."""
        phase = PhaseInfo(id="phase-1", name="Test Phase")
        
        self.assertEqual(phase.dependencies, [])
        self.assertEqual(phase.outputs, [])
        self.assertEqual(phase.estimated_time, 1.0)
        self.assertEqual(phase.description, "")
    
    def test_phase_hashable(self):
        """Test that phases can be used in sets."""
        phase1 = PhaseInfo(id="phase-1", name="Phase 1")
        phase2 = PhaseInfo(id="phase-2", name="Phase 2")
        phase1_dup = PhaseInfo(id="phase-1", name="Different Name")
        
        phase_set = {phase1, phase2, phase1_dup}
        self.assertEqual(len(phase_set), 2)  # Duplicate should be ignored
    
    def test_phase_equality(self):
        """Test phase equality based on ID."""
        phase1 = PhaseInfo(id="phase-1", name="Phase 1")
        phase1_same = PhaseInfo(id="phase-1", name="Different Name")
        phase2 = PhaseInfo(id="phase-2", name="Phase 2")
        
        self.assertEqual(phase1, phase1_same)
        self.assertNotEqual(phase1, phase2)
        self.assertNotEqual(phase1, "not a phase")


class TestDependencyGraph(unittest.TestCase):
    """Test DependencyGraph model."""
    
    def setUp(self):
        """Set up test phases."""
        self.phase1 = PhaseInfo(id="phase-1", name="Phase 1")
        self.phase2 = PhaseInfo(id="phase-2", name="Phase 2", dependencies=["phase-1"])
        self.phase3 = PhaseInfo(id="phase-3", name="Phase 3", dependencies=["phase-1", "phase-2"])
        self.phase4 = PhaseInfo(id="phase-4", name="Phase 4", dependencies=["phase-3"])
    
    def test_add_phase(self):
        """Test adding phases to the graph."""
        graph = DependencyGraph()
        
        graph.add_phase(self.phase1)
        graph.add_phase(self.phase2)
        
        self.assertIn("phase-1", graph.nodes)
        self.assertIn("phase-2", graph.nodes)
        self.assertEqual(len(graph.nodes), 2)
    
    def test_dependency_tracking(self):
        """Test that dependencies are properly tracked."""
        graph = DependencyGraph()
        
        graph.add_phase(self.phase1)
        graph.add_phase(self.phase2)
        graph.add_phase(self.phase3)
        
        # Check forward edges (dependents)
        self.assertIn("phase-2", graph.get_dependents("phase-1"))
        self.assertIn("phase-3", graph.get_dependents("phase-1"))
        self.assertIn("phase-3", graph.get_dependents("phase-2"))
        
        # Check reverse edges (dependencies)
        self.assertIn("phase-1", graph.get_dependencies("phase-2"))
        self.assertIn("phase-1", graph.get_dependencies("phase-3"))
        self.assertIn("phase-2", graph.get_dependencies("phase-3"))
    
    def test_get_phase(self):
        """Test retrieving phase by ID."""
        graph = DependencyGraph()
        graph.add_phase(self.phase1)
        
        retrieved = graph.get_phase("phase-1")
        self.assertEqual(retrieved, self.phase1)
        
        missing = graph.get_phase("phase-99")
        self.assertIsNone(missing)
    
    def test_root_phases(self):
        """Test finding root phases with no dependencies."""
        graph = DependencyGraph()
        
        graph.add_phase(self.phase1)
        graph.add_phase(self.phase2)
        graph.add_phase(self.phase3)
        graph.add_phase(self.phase4)
        
        roots = graph.get_root_phases()
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].id, "phase-1")


class TestExecutionWave(unittest.TestCase):
    """Test ExecutionWave model."""
    
    def test_wave_creation(self):
        """Test creating an execution wave."""
        wave = ExecutionWave(wave_number=0)
        
        self.assertEqual(wave.wave_number, 0)
        self.assertEqual(wave.phases, [])
        self.assertIsNone(wave.start_time)
        self.assertIsNone(wave.end_time)
        self.assertEqual(wave.status, "pending")
    
    def test_phase_management(self):
        """Test adding and removing phases from wave."""
        wave = ExecutionWave(wave_number=1)
        
        wave.add_phase("phase-1")
        wave.add_phase("phase-2")
        wave.add_phase("phase-1")  # Duplicate
        
        self.assertEqual(len(wave.phases), 2)
        self.assertIn("phase-1", wave.phases)
        self.assertIn("phase-2", wave.phases)
        
        wave.remove_phase("phase-1")
        self.assertEqual(len(wave.phases), 1)
        self.assertNotIn("phase-1", wave.phases)
    
    def test_wave_status(self):
        """Test wave status checks."""
        wave = ExecutionWave(wave_number=0)
        
        self.assertFalse(wave.is_complete())
        self.assertFalse(wave.is_active())
        
        wave.status = "in_progress"
        self.assertFalse(wave.is_complete())
        self.assertTrue(wave.is_active())
        
        wave.status = "completed"
        self.assertTrue(wave.is_complete())
        self.assertFalse(wave.is_active())


class TestResourceLock(unittest.TestCase):
    """Test ResourceLock model."""
    
    def test_lock_creation(self):
        """Test creating a resource lock."""
        lock = ResourceLock(
            resource_path="/path/to/file.py",
            owner_phase="phase-1",
            lock_type=LockType.EXCLUSIVE
        )
        
        self.assertEqual(lock.resource_path, "/path/to/file.py")
        self.assertEqual(lock.owner_phase, "phase-1")
        self.assertEqual(lock.lock_type, LockType.EXCLUSIVE)
        self.assertIsNotNone(lock.lock_time)
        self.assertIsNone(lock.expires_at)
    
    def test_lock_expiration(self):
        """Test lock expiration checking."""
        lock = ResourceLock(
            resource_path="/path/to/file.py",
            owner_phase="phase-1"
        )
        
        # No expiration set
        self.assertFalse(lock.is_expired())
        
        # Set expiration in future
        lock.expires_at = datetime.now() + timedelta(seconds=10)
        self.assertFalse(lock.is_expired())
        
        # Set expiration in past
        lock.expires_at = datetime.now() - timedelta(seconds=10)
        self.assertTrue(lock.is_expired())
    
    def test_lock_type_checks(self):
        """Test lock type checking methods."""
        shared_lock = ResourceLock(
            resource_path="/file.py",
            owner_phase="phase-1",
            lock_type=LockType.SHARED
        )
        
        exclusive_lock = ResourceLock(
            resource_path="/file.py",
            owner_phase="phase-2",
            lock_type=LockType.EXCLUSIVE
        )
        
        self.assertTrue(shared_lock.is_shared())
        self.assertFalse(shared_lock.is_exclusive())
        self.assertFalse(exclusive_lock.is_shared())
        self.assertTrue(exclusive_lock.is_exclusive())


class TestPhaseExecutionDetails(unittest.TestCase):
    """Test PhaseExecutionDetails model."""
    
    def test_execution_details_creation(self):
        """Test creating execution details."""
        details = PhaseExecutionDetails(phase_id="phase-1")
        
        self.assertEqual(details.phase_id, "phase-1")
        self.assertEqual(details.status, PhaseStatus.NOT_STARTED)
        self.assertIsNone(details.agent_id)
        self.assertIsNone(details.start_time)
        self.assertIsNone(details.end_time)
        self.assertEqual(details.retry_count, 0)
    
    def test_mark_started(self):
        """Test marking phase as started."""
        details = PhaseExecutionDetails(phase_id="phase-1")
        details.mark_started("agent-1")
        
        self.assertEqual(details.status, PhaseStatus.IN_PROGRESS)
        self.assertEqual(details.agent_id, "agent-1")
        self.assertIsNotNone(details.start_time)
    
    def test_mark_completed(self):
        """Test marking phase as completed."""
        details = PhaseExecutionDetails(phase_id="phase-1")
        details.mark_started("agent-1")
        time.sleep(0.1)  # Ensure some duration
        details.mark_completed(["output1.py", "output2.py"])
        
        self.assertEqual(details.status, PhaseStatus.COMPLETED)
        self.assertIsNotNone(details.end_time)
        self.assertEqual(details.output_files, ["output1.py", "output2.py"])
        self.assertGreater(details.duration_seconds(), 0)
    
    def test_mark_failed(self):
        """Test marking phase as failed."""
        details = PhaseExecutionDetails(phase_id="phase-1")
        details.mark_started("agent-1")
        details.mark_failed("Test error message")
        
        self.assertEqual(details.status, PhaseStatus.FAILED)
        self.assertEqual(details.error_message, "Test error message")
        self.assertEqual(details.retry_count, 1)


class TestAgentInfo(unittest.TestCase):
    """Test AgentInfo model."""
    
    def test_agent_creation(self):
        """Test creating an agent."""
        agent = AgentInfo(agent_id="agent-1")
        
        self.assertEqual(agent.agent_id, "agent-1")
        self.assertIsNone(agent.assigned_phase)
        self.assertEqual(agent.status, AgentStatus.IDLE)
        self.assertEqual(agent.logs, [])
        self.assertIsNotNone(agent.created_at)
        self.assertIsNone(agent.terminated_at)
    
    def test_agent_assignment(self):
        """Test assigning phase to agent."""
        agent = AgentInfo(agent_id="agent-1")
        agent.assign_phase("phase-1")
        
        self.assertEqual(agent.assigned_phase, "phase-1")
        self.assertEqual(agent.status, AgentStatus.ASSIGNED)
        self.assertEqual(len(agent.logs), 1)
        self.assertEqual(agent.logs[0]["level"], "info")
    
    def test_agent_workflow(self):
        """Test complete agent workflow."""
        agent = AgentInfo(agent_id="agent-1")
        
        # Initial state
        self.assertTrue(agent.is_available())
        
        # Assign and start work
        agent.assign_phase("phase-1")
        self.assertFalse(agent.is_available())  # Not available when assigned
        
        agent.start_work()
        self.assertFalse(agent.is_available())
        self.assertEqual(agent.status, AgentStatus.WORKING)
        
        # Complete work
        agent.complete_work()
        self.assertTrue(agent.is_available())
        self.assertEqual(agent.status, AgentStatus.COMPLETED)
        self.assertIsNone(agent.assigned_phase)
    
    def test_agent_error_handling(self):
        """Test agent error reporting."""
        agent = AgentInfo(agent_id="agent-1")
        agent.report_error("Test error")
        
        self.assertEqual(agent.status, AgentStatus.ERROR)
        self.assertFalse(agent.is_available())
        
        # Check error log
        error_logs = [log for log in agent.logs if log["level"] == "error"]
        self.assertEqual(len(error_logs), 1)
        self.assertEqual(error_logs[0]["message"], "Test error")
    
    def test_agent_termination(self):
        """Test agent termination."""
        agent = AgentInfo(agent_id="agent-1")
        agent.terminate()
        
        self.assertEqual(agent.status, AgentStatus.TERMINATED)
        self.assertIsNotNone(agent.terminated_at)
        self.assertFalse(agent.is_available())


class TestExecutionState(unittest.TestCase):
    """Test ExecutionState model."""
    
    def test_state_creation(self):
        """Test creating execution state."""
        state = ExecutionState()
        
        self.assertEqual(state.phase_states, {})
        self.assertEqual(state.waves, [])
        self.assertEqual(state.agents, {})
        self.assertIsNone(state.start_time)
        self.assertIsNone(state.end_time)
    
    def test_phase_management(self):
        """Test managing phases in state."""
        state = ExecutionState()
        
        state.add_phase("phase-1")
        state.add_phase("phase-2")
        
        self.assertEqual(len(state.phase_states), 2)
        self.assertEqual(state.get_phase_status("phase-1"), PhaseStatus.NOT_STARTED)
        
        state.update_phase_status("phase-1", PhaseStatus.IN_PROGRESS)
        self.assertEqual(state.get_phase_status("phase-1"), PhaseStatus.IN_PROGRESS)
    
    def test_agent_management(self):
        """Test managing agents in state."""
        state = ExecutionState()
        
        agent1 = AgentInfo(agent_id="agent-1")
        agent2 = AgentInfo(agent_id="agent-2")
        agent2.start_work()  # Make agent2 busy
        
        state.add_agent(agent1)
        state.add_agent(agent2)
        
        available = state.get_available_agents()
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0].agent_id, "agent-1")
    
    def test_phase_tracking(self):
        """Test tracking phases by status."""
        state = ExecutionState()
        
        # Add phases with different statuses
        for i in range(5):
            state.add_phase(f"phase-{i}")
        
        state.phase_states["phase-0"].status = PhaseStatus.COMPLETED
        state.phase_states["phase-1"].status = PhaseStatus.COMPLETED
        state.phase_states["phase-2"].status = PhaseStatus.IN_PROGRESS
        state.phase_states["phase-3"].status = PhaseStatus.FAILED
        
        self.assertEqual(len(state.get_completed_phases()), 2)
        self.assertEqual(len(state.get_active_phases()), 1)
        self.assertEqual(len(state.get_failed_phases()), 1)
    
    def test_progress_calculation(self):
        """Test progress calculation."""
        state = ExecutionState()
        
        # Empty state
        self.assertEqual(state.calculate_progress(), 0.0)
        
        # Add phases
        for i in range(4):
            state.add_phase(f"phase-{i}")
        
        # Complete half
        state.phase_states["phase-0"].status = PhaseStatus.COMPLETED
        state.phase_states["phase-1"].status = PhaseStatus.COMPLETED
        
        self.assertEqual(state.calculate_progress(), 50.0)
    
    def test_completion_check(self):
        """Test checking if execution is complete."""
        state = ExecutionState()
        
        state.add_phase("phase-1")
        state.add_phase("phase-2")
        
        self.assertFalse(state.is_complete())
        
        state.phase_states["phase-1"].status = PhaseStatus.COMPLETED
        self.assertFalse(state.is_complete())
        
        state.phase_states["phase-2"].status = PhaseStatus.FAILED
        self.assertTrue(state.is_complete())  # All terminal states
    
    def test_summary_generation(self):
        """Test generating execution summary."""
        state = ExecutionState()
        state.start_time = datetime.now()
        
        # Add some test data
        state.add_phase("phase-1")
        state.add_phase("phase-2")
        state.phase_states["phase-1"].status = PhaseStatus.COMPLETED
        
        agent = AgentInfo(agent_id="agent-1")
        agent.start_work()
        state.add_agent(agent)
        
        summary = state.get_summary()
        
        self.assertEqual(summary["total_phases"], 2)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["active"], 0)
        self.assertEqual(summary["progress_percent"], 50.0)
        self.assertEqual(summary["active_agents"], 1)
        self.assertEqual(summary["total_agents"], 1)


class TestFileLock(unittest.TestCase):
    """Test FileLock implementation."""
    
    def setUp(self):
        """Reset lock registry before each test."""
        LockRegistry._instance = None
    
    def test_lock_acquisition(self):
        """Test basic lock acquisition and release."""
        lock = FileLock("/test/file.py", "phase-1")
        
        self.assertFalse(lock.is_acquired())
        
        # Acquire lock
        acquired = lock.acquire()
        self.assertTrue(acquired)
        self.assertTrue(lock.is_acquired())
        
        # Release lock
        lock.release()
        self.assertFalse(lock.is_acquired())
    
    def test_lock_context_manager(self):
        """Test using lock as context manager."""
        lock = FileLock("/test/file.py", "phase-1")
        
        with lock:
            self.assertTrue(lock.is_acquired())
        
        self.assertFalse(lock.is_acquired())
    
    def test_exclusive_lock_conflict(self):
        """Test that exclusive locks conflict."""
        lock1 = FileLock("/test/file.py", "phase-1", LockType.EXCLUSIVE)
        lock2 = FileLock("/test/file.py", "phase-2", LockType.EXCLUSIVE)
        
        # First lock succeeds
        self.assertTrue(lock1.acquire())
        
        # Second lock fails (non-blocking)
        self.assertFalse(lock2.acquire(blocking=False))
        
        # Release first lock
        lock1.release()
        
        # Now second lock succeeds
        self.assertTrue(lock2.acquire())
        lock2.release()
    
    def test_shared_locks_compatible(self):
        """Test that multiple shared locks can coexist."""
        lock1 = FileLock("/test/file.py", "phase-1", LockType.SHARED)
        lock2 = FileLock("/test/file.py", "phase-2", LockType.SHARED)
        lock3 = FileLock("/test/file.py", "phase-3", LockType.SHARED)
        
        # All shared locks should succeed
        self.assertTrue(lock1.acquire())
        self.assertTrue(lock2.acquire())
        self.assertTrue(lock3.acquire())
        
        # Exclusive lock should fail
        exclusive = FileLock("/test/file.py", "phase-4", LockType.EXCLUSIVE)
        self.assertFalse(exclusive.acquire(blocking=False))
        
        # Clean up
        lock1.release()
        lock2.release()
        lock3.release()
    
    def test_lock_timeout(self):
        """Test lock timeout handling."""
        lock1 = FileLock("/test/file.py", "phase-1")
        lock2 = FileLock("/test/file.py", "phase-2")
        
        lock1.acquire()
        
        # Try to acquire with timeout
        with self.assertRaises(LockTimeoutError):
            lock2.acquire(timeout=0.1)
        
        lock1.release()


class TestLockRegistry(unittest.TestCase):
    """Test LockRegistry singleton."""
    
    def setUp(self):
        """Reset registry before each test."""
        LockRegistry._instance = None
    
    def test_singleton_pattern(self):
        """Test that LockRegistry is a singleton."""
        registry1 = LockRegistry.instance()
        registry2 = LockRegistry.instance()
        
        self.assertIs(registry1, registry2)
    
    def test_lock_tracking(self):
        """Test tracking active locks."""
        registry = LockRegistry.instance()
        
        lock1 = ResourceLock("/file1.py", "phase-1")
        lock2 = ResourceLock("/file2.py", "phase-2")
        
        registry.acquire_lock(lock1)
        registry.acquire_lock(lock2)
        
        all_locks = registry.get_active_locks()
        self.assertEqual(len(all_locks), 2)
        
        phase1_locks = registry.get_phase_locks("phase-1")
        self.assertEqual(len(phase1_locks), 1)
        self.assertEqual(phase1_locks[0].resource_path, "/file1.py")
    
    def test_conflict_detection(self):
        """Test detecting lock conflicts."""
        registry = LockRegistry.instance()
        
        # Acquire exclusive lock
        lock = ResourceLock("/test.py", "phase-1", lock_type=LockType.EXCLUSIVE)
        registry.acquire_lock(lock)
        
        # Check conflicts
        request = LockRequest("/test.py", "phase-2", LockType.EXCLUSIVE)
        conflicts = registry.detect_conflicts(request)
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].owner_phase, "phase-1")
        
        # Shared request should also conflict with exclusive
        shared_request = LockRequest("/test.py", "phase-2", LockType.SHARED)
        conflicts = registry.detect_conflicts(shared_request)
        self.assertEqual(len(conflicts), 1)
    
    def test_phase_lock_cleanup(self):
        """Test releasing all locks for a phase."""
        registry = LockRegistry.instance()
        
        # Phase acquires multiple locks
        lock1 = ResourceLock("/file1.py", "phase-1")
        lock2 = ResourceLock("/file2.py", "phase-1")
        lock3 = ResourceLock("/file3.py", "phase-2")
        
        registry.acquire_lock(lock1)
        registry.acquire_lock(lock2)
        registry.acquire_lock(lock3)
        
        # Release all phase-1 locks
        registry.release_all_phase_locks("phase-1")
        
        # Check that only phase-2 lock remains
        all_locks = registry.get_active_locks()
        self.assertEqual(len(all_locks), 1)
        self.assertEqual(all_locks[0].owner_phase, "phase-2")
    
    def test_lock_expiration_cleanup(self):
        """Test cleaning up expired locks."""
        registry = LockRegistry.instance()
        
        # Create lock that expires immediately
        lock = ResourceLock("/test.py", "phase-1")
        lock.expires_at = datetime.now() - timedelta(seconds=1)
        
        registry.acquire_lock(lock)
        
        # Before cleanup
        self.assertEqual(len(registry.get_active_locks()), 0)  # Already filtered
        
        # After cleanup
        registry.cleanup_expired_locks()
        stats = registry.get_stats()
        self.assertEqual(stats["total_active_locks"], 0)


class TestParallelExecutionConfig(unittest.TestCase):
    """Test ParallelExecutionConfig."""
    
    def test_config_defaults(self):
        """Test configuration default values."""
        config = ParallelExecutionConfig()
        
        self.assertEqual(config.max_parallel_agents, 3)
        self.assertEqual(config.lock_timeout_seconds, 300)
        self.assertEqual(config.wave_delay_seconds, 5)
        self.assertEqual(config.monitoring_update_interval_seconds, 2)
        self.assertTrue(config.retry_failed_phases)
        self.assertFalse(config.fail_fast)
    
    def test_config_from_env(self):
        """Test loading configuration from environment."""
        # Set test environment variables
        os.environ["PRD_PARALLEL_MAX_PARALLEL_AGENTS"] = "5"
        os.environ["PRD_PARALLEL_LOCK_TIMEOUT_SECONDS"] = "600"
        os.environ["PRD_PARALLEL_FAIL_FAST"] = "true"
        os.environ["PRD_PARALLEL_SHOW_AGENT_LOGS"] = "false"
        
        try:
            config = ParallelExecutionConfig.from_env()
            
            self.assertEqual(config.max_parallel_agents, 5)
            self.assertEqual(config.lock_timeout_seconds, 600)
            self.assertTrue(config.fail_fast)
            self.assertFalse(config.show_agent_logs)
        finally:
            # Clean up
            for key in list(os.environ.keys()):
                if key.startswith("PRD_PARALLEL_"):
                    del os.environ[key]
    
    def test_config_file_operations(self):
        """Test saving and loading configuration from file."""
        config = ParallelExecutionConfig(
            max_parallel_agents=4,
            lock_timeout_seconds=120,
            fail_fast=True
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config.to_file(f.name)
            temp_path = f.name
        
        try:
            # Load from file
            loaded_config = ParallelExecutionConfig.from_file(temp_path)
            
            self.assertEqual(loaded_config.max_parallel_agents, 4)
            self.assertEqual(loaded_config.lock_timeout_seconds, 120)
            self.assertTrue(loaded_config.fail_fast)
        finally:
            os.unlink(temp_path)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = ParallelExecutionConfig()
        errors = config.validate()
        self.assertEqual(len(errors), 0)
        
        # Invalid: max agents too low
        config = ParallelExecutionConfig(max_parallel_agents=0)
        errors = config.validate()
        self.assertIn("max_parallel_agents must be at least 1", errors)
        
        # Invalid: conflicting flags
        config = ParallelExecutionConfig(fail_fast=True, continue_on_error=True)
        errors = config.validate()
        self.assertIn("fail_fast and continue_on_error cannot both be true", errors)
        
        # Invalid: backoff settings
        config = ParallelExecutionConfig(
            conflict_backoff_base_seconds=10,
            conflict_backoff_max_seconds=5
        )
        errors = config.validate()
        self.assertIn("conflict_backoff_base_seconds cannot exceed conflict_backoff_max_seconds", errors)
    
    def test_config_summary(self):
        """Test configuration summary generation."""
        config = ParallelExecutionConfig(
            max_parallel_agents=5,
            fail_fast=True,
            retry_failed_phases=False
        )
        
        summary = config.get_summary()
        self.assertIn("5 max parallel", summary)
        self.assertIn("Fail fast", summary)
        self.assertIn("Disabled", summary)  # Retry disabled
    
    def test_post_init_paths(self):
        """Test automatic path generation in __post_init__."""
        config = ParallelExecutionConfig()
        
        self.assertIsNotNone(config.state_file_path)
        self.assertIn(".prd-parallel-state.json", config.state_file_path)
        
        self.assertIsNotNone(config.log_directory)
        self.assertIn(".prd-parallel-logs", config.log_directory)
        
        # Test with custom workspace
        config = ParallelExecutionConfig(workspace_root="/custom/path")
        self.assertTrue(config.state_file_path.startswith("/custom/path"))
        self.assertTrue(config.log_directory.startswith("/custom/path"))


class TestPhaseStatusEnum(unittest.TestCase):
    """Test PhaseStatus enum methods."""
    
    def test_terminal_states(self):
        """Test identifying terminal states."""
        terminal_states = [PhaseStatus.COMPLETED, PhaseStatus.FAILED, PhaseStatus.CANCELLED]
        non_terminal = [PhaseStatus.NOT_STARTED, PhaseStatus.QUEUED, 
                       PhaseStatus.IN_PROGRESS, PhaseStatus.BLOCKED]
        
        for status in terminal_states:
            self.assertTrue(status.is_terminal())
            
        for status in non_terminal:
            self.assertFalse(status.is_terminal())
    
    def test_active_states(self):
        """Test identifying active states."""
        active_states = [PhaseStatus.IN_PROGRESS, PhaseStatus.QUEUED]
        inactive = [PhaseStatus.NOT_STARTED, PhaseStatus.COMPLETED, 
                   PhaseStatus.FAILED, PhaseStatus.BLOCKED, PhaseStatus.CANCELLED]
        
        for status in active_states:
            self.assertTrue(status.is_active())
            
        for status in inactive:
            self.assertFalse(status.is_active())


class TestConcurrency(unittest.TestCase):
    """Test thread safety and concurrency handling."""
    
    def setUp(self):
        """Reset registry before each test."""
        LockRegistry._instance = None
    
    def test_concurrent_lock_acquisition(self):
        """Test that locks properly handle concurrent access."""
        results = []
        barrier = threading.Barrier(3)
        
        def try_acquire_lock(phase_id, lock_type):
            barrier.wait()  # Synchronize start
            lock = FileLock("/shared/resource.py", phase_id, lock_type)
            acquired = lock.acquire(blocking=False)
            results.append((phase_id, acquired))
            if acquired:
                time.sleep(0.1)
                lock.release()
        
        # Try to acquire exclusive locks concurrently
        threads = []
        for i in range(3):
            t = threading.Thread(
                target=try_acquire_lock,
                args=(f"phase-{i}", LockType.EXCLUSIVE)
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Only one should succeed
        successful = sum(1 for _, acquired in results if acquired)
        self.assertEqual(successful, 1)
    
    def test_registry_thread_safety(self):
        """Test that registry operations are thread-safe."""
        registry = LockRegistry.instance()
        errors = []
        
        def registry_operations(phase_id):
            try:
                for i in range(10):
                    lock = ResourceLock(f"/file{i}.py", phase_id)
                    registry.acquire_lock(lock)
                    
                    # Check operations
                    registry.get_active_locks()
                    registry.get_phase_locks(phase_id)
                    
                    # Release some locks
                    if i % 2 == 0:
                        registry.release_lock(f"/file{i}.py", phase_id)
                
                # Clean up
                registry.release_all_phase_locks(phase_id)
            except Exception as e:
                errors.append(e)
        
        # Run operations from multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(
                target=registry_operations,
                args=(f"phase-{i}",)
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # No errors should occur
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()