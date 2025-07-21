"""
Comprehensive tests for orchestrator components.
"""

import unittest
import tempfile
import shutil
import time
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from models.parallel_execution import PhaseInfo, DependencyGraph, ExecutionWave, ResourceLock, LockType
from models.execution_state import ExecutionState, PhaseStatus, AgentStatus
from orchestrator.agent_spawner import AgentSpawner, AgentProcess, AgentCommand, AgentCommandType
from orchestrator.wave_executor import WaveExecutor, WaveResult, RecoveryAction
from orchestrator.resource_coordinator import ResourceCoordinator, ResourceConflict, ConflictResolution
from orchestrator.state_manager import StateManager, StateMetadata
from orchestrator.parallel_orchestrator import ParallelOrchestrator, ExecutionMode, ExecutionResult


class TestAgentSpawner(unittest.TestCase):
    """Test agent spawning and lifecycle management."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {"max_agents": 3}
        self.spawner = AgentSpawner(self.temp_dir, self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.spawner.terminate_all()
        shutil.rmtree(self.temp_dir)
    
    def test_spawn_agent(self):
        """Test spawning a new agent."""
        phase_info = {
            "id": "test-phase",
            "name": "Test Phase",
            "outputs": ["output.txt"],
            "estimated_time": 1.0
        }
        
        success, agent_id = self.spawner.spawn_agent(phase_info)
        
        self.assertTrue(success)
        self.assertTrue(agent_id.startswith("agent-test-phase-"))
        self.assertIn(agent_id, self.spawner.agents)
    
    def test_agent_limit(self):
        """Test agent limit enforcement."""
        # Spawn max agents
        for i in range(3):
            phase_info = {"id": f"phase-{i}", "name": f"Phase {i}"}
            success, _ = self.spawner.spawn_agent(phase_info)
            self.assertTrue(success)
        
        # Try to spawn one more
        phase_info = {"id": "phase-4", "name": "Phase 4"}
        success, error = self.spawner.spawn_agent(phase_info)
        
        self.assertFalse(success)
        self.assertIn("limit reached", error)
    
    def test_monitor_agent_health(self):
        """Test agent health monitoring."""
        phase_info = {"id": "test-phase", "name": "Test Phase"}
        success, agent_id = self.spawner.spawn_agent(phase_info)
        
        self.assertTrue(success)
        
        # Check initial health
        status = self.spawner.monitor_agent_health(agent_id)
        self.assertIn(status, [AgentStatus.ASSIGNED, AgentStatus.WORKING])
    
    def test_terminate_agent(self):
        """Test agent termination."""
        phase_info = {"id": "test-phase", "name": "Test Phase"}
        success, agent_id = self.spawner.spawn_agent(phase_info)
        
        self.assertTrue(success)
        
        # Terminate agent
        terminated = self.spawner.terminate_agent(agent_id)
        self.assertTrue(terminated)
        
        # Verify agent is removed
        self.assertNotIn(agent_id, self.spawner.agents)
    
    def test_collect_agent_logs(self):
        """Test log collection."""
        phase_info = {"id": "test-phase", "name": "Test Phase"}
        success, agent_id = self.spawner.spawn_agent(phase_info)
        
        self.assertTrue(success)
        
        # Add some logs to the agent
        agent = self.spawner.agents[agent_id]
        agent.agent_info.add_log("info", "Test log message")
        
        # Collect logs
        logs = self.spawner.collect_agent_logs(agent_id)
        
        # Note: In the actual implementation, logs would come from the subprocess
        # For now, we just verify the method exists and returns a list
        self.assertIsInstance(logs, list)


class TestWaveExecutor(unittest.TestCase):
    """Test wave-based execution engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "max_agents_per_wave": 2,
            "phase_timeout_seconds": 10,
            "retry_limit": 1
        }
        
        # Create mock components
        self.agent_spawner = Mock(spec=AgentSpawner)
        self.execution_state = ExecutionState()
        self.dependency_graph = DependencyGraph()
        
        # Create test phases
        self.phase1 = PhaseInfo(id="phase-1", name="Phase 1")
        self.phase2 = PhaseInfo(id="phase-2", name="Phase 2")
        self.dependency_graph.add_phase(self.phase1)
        self.dependency_graph.add_phase(self.phase2)
        
        self.executor = WaveExecutor(
            self.agent_spawner,
            self.execution_state,
            self.dependency_graph,
            self.config
        )
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_execute_wave_success(self):
        """Test successful wave execution."""
        # Create wave
        wave = ExecutionWave(wave_number=0, phases=["phase-1", "phase-2"])
        
        # Mock agent spawning
        self.agent_spawner.spawn_agent.return_value = (True, "agent-1")
        self.agent_spawner.monitor_agent_health.return_value = AgentStatus.COMPLETED
        self.agent_spawner.agents = {"agent-1": Mock(get_state=Mock(return_value={"outputs": []}))}
        
        # Execute wave
        result = self.executor.execute_wave(wave, self.temp_dir)
        
        self.assertTrue(result.success)
        self.assertEqual(result.wave_number, 0)
        self.assertEqual(len(result.phases_completed), 2)
        self.assertEqual(len(result.phases_failed), 0)
    
    def test_execute_wave_with_failure(self):
        """Test wave execution with phase failure."""
        # Create wave
        wave = ExecutionWave(wave_number=0, phases=["phase-1", "phase-2"])
        
        # Mock agent spawning - first succeeds, second fails
        self.agent_spawner.spawn_agent.side_effect = [
            (True, "agent-1"),
            (False, "Agent spawn failed")
        ]
        
        # Execute wave
        result = self.executor.execute_wave(wave, self.temp_dir)
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.phases_failed), 1)
        self.assertIn("phase-2", result.phases_failed)
    
    def test_handle_phase_failure(self):
        """Test phase failure handling."""
        # Test retry strategy
        self.executor.failure_strategy = "retry"
        action = self.executor.handle_phase_failure("phase-1", "Test error")
        self.assertEqual(action, RecoveryAction.RETRY)
        
        # Test skip strategy
        self.executor.failure_strategy = "skip"
        action = self.executor.handle_phase_failure("phase-1", "Test error")
        self.assertEqual(action, RecoveryAction.SKIP)
    
    def test_wave_progress_tracking(self):
        """Test wave progress tracking."""
        wave = ExecutionWave(wave_number=0, phases=["phase-1", "phase-2"])
        self.executor.current_wave = wave
        
        # Update phase states
        self.execution_state.add_phase("phase-1")
        self.execution_state.add_phase("phase-2")
        self.execution_state.update_phase_status("phase-1", PhaseStatus.COMPLETED)
        self.execution_state.update_phase_status("phase-2", PhaseStatus.IN_PROGRESS)
        
        progress = self.executor.get_wave_progress(wave)
        
        self.assertEqual(progress["wave_number"], 0)
        self.assertEqual(progress["completed"], 1)
        self.assertEqual(progress["in_progress"], 1)
        self.assertEqual(progress["progress_percent"], 50.0)


class TestResourceCoordinator(unittest.TestCase):
    """Test resource coordination and deadlock detection."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "enable_deadlock_detection": True,
            "deadlock_check_interval": 1
        }
        self.coordinator = ResourceCoordinator(self.temp_dir, self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.coordinator.stop()
        shutil.rmtree(self.temp_dir)
    
    def test_acquire_resources(self):
        """Test acquiring multiple resources."""
        resources = ["/file1.txt", "/file2.txt"]
        
        locks = self.coordinator.acquire_resources_for_phase("phase-1", resources)
        
        self.assertEqual(len(locks), 2)
        for lock in locks:
            self.assertIsInstance(lock, ResourceLock)
            self.assertEqual(lock.owner_phase, "phase-1")
    
    def test_resource_conflict_detection(self):
        """Test conflict detection."""
        # Phase 1 acquires resource
        self.coordinator.acquire_resources_for_phase("phase-1", ["/shared.txt"])
        
        # Phase 2 tries to acquire same resource
        with self.assertRaises(Exception):
            self.coordinator.acquire_resources_for_phase(
                "phase-2", ["/shared.txt"],
                {"/shared.txt": LockType.EXCLUSIVE}
            )
        
        # Check conflicts were recorded
        conflicts = self.coordinator.get_resource_conflicts()
        self.assertGreater(len(conflicts), 0)
    
    def test_deadlock_detection(self):
        """Test deadlock detection."""
        # Create circular wait scenario
        # This is a simplified test - in reality, deadlocks would occur across processes
        
        # Phase 1 waits for phase 2
        self.coordinator._wait_graph["phase-1"].add("phase-2")
        # Phase 2 waits for phase 1
        self.coordinator._wait_graph["phase-2"].add("phase-1")
        
        deadlocks = self.coordinator.monitor_deadlocks()
        
        self.assertEqual(len(deadlocks), 1)
        self.assertIn("phase-1", deadlocks[0].phases_involved)
        self.assertIn("phase-2", deadlocks[0].phases_involved)
    
    def test_priority_based_resolution(self):
        """Test priority-based conflict resolution."""
        self.coordinator.config["conflict_resolution"] = "preempt"
        
        # Set priorities
        self.coordinator.set_phase_priority("phase-1", 10)
        self.coordinator.set_phase_priority("phase-2", 5)
        
        # Create conflict
        conflict = ResourceConflict(
            requesting_phase="phase-1",
            conflicting_phase="phase-2",
            resource_path="/file.txt",
            conflict_type="exclusive_held"
        )
        
        resolution = self.coordinator.resolve_lock_conflict(conflict)
        self.assertEqual(resolution, ConflictResolution.PREEMPT)


class TestStateManager(unittest.TestCase):
    """Test state persistence and recovery."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "checkpoint_interval_seconds": 1,
            "max_state_backups": 3
        }
        self.state_manager = StateManager(self.temp_dir, self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.state_manager.stop()
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_state(self):
        """Test saving and loading execution state."""
        # Create test state
        state = ExecutionState()
        state.add_phase("phase-1")
        state.update_phase_status("phase-1", PhaseStatus.COMPLETED)
        state.start_time = datetime.now()
        
        # Save state
        success = self.state_manager.save_execution_state(state)
        self.assertTrue(success)
        
        # Load state
        loaded_state = self.state_manager.load_execution_state()
        
        self.assertIsNotNone(loaded_state)
        self.assertEqual(len(loaded_state.phase_states), 1)
        self.assertEqual(loaded_state.get_phase_status("phase-1"), PhaseStatus.COMPLETED)
    
    def test_auto_checkpoint(self):
        """Test automatic checkpointing."""
        state = ExecutionState()
        state.add_phase("phase-1")
        
        # Save initial state
        self.state_manager.save_execution_state(state)
        initial_checkpoint = self.state_manager._checkpoint_number
        
        # Wait for auto-checkpoint
        time.sleep(2)
        
        # Update state to trigger checkpoint
        self.state_manager.update_phase_status("phase-1", PhaseStatus.COMPLETED)
        
        # Check checkpoint was created
        self.assertGreater(self.state_manager._checkpoint_number, initial_checkpoint)
    
    def test_crash_recovery(self):
        """Test recovery from crash."""
        # Create state with in-progress phase
        state = ExecutionState()
        state.add_phase("phase-1")
        state.add_phase("phase-2")
        state.update_phase_status("phase-1", PhaseStatus.COMPLETED)
        state.update_phase_status("phase-2", PhaseStatus.IN_PROGRESS)
        
        # Save state
        self.state_manager.save_execution_state(state)
        
        # Simulate crash and recovery
        recovered_state = self.state_manager.recover_from_crash()
        
        self.assertIsNotNone(recovered_state)
        # In-progress phase should be marked as failed
        self.assertEqual(
            recovered_state.get_phase_status("phase-2"),
            PhaseStatus.FAILED
        )
    
    def test_backup_management(self):
        """Test backup creation and cleanup."""
        state = ExecutionState()
        
        # Create multiple checkpoints
        for i in range(5):
            state.add_phase(f"phase-{i}")
            self.state_manager.save_execution_state(state)
            time.sleep(0.1)
        
        # Check backup limit is enforced
        backups = list(self.state_manager.backup_dir.glob("*.json"))
        self.assertLessEqual(len(backups), self.config["max_state_backups"])


class TestParallelOrchestrator(unittest.TestCase):
    """Test main orchestration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "max_agents": 2,
            "phase_timeout_seconds": 10
        }
        self.orchestrator = ParallelOrchestrator(self.temp_dir, self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        if self.orchestrator._is_running:
            self.orchestrator.stop_execution()
        shutil.rmtree(self.temp_dir)
    
    def test_validate_execution(self):
        """Test execution validation."""
        # Create valid phases
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1"),
            PhaseInfo(id="phase-2", name="Phase 2", dependencies=["phase-1"])
        ]
        
        result = self.orchestrator.execute_prd(phases, mode=ExecutionMode.VALIDATE)
        
        self.assertTrue(result.success)
        self.assertEqual(result.mode, ExecutionMode.VALIDATE)
        self.assertEqual(len(result.errors), 0)
    
    def test_dry_run_execution(self):
        """Test dry run mode."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", estimated_time=0.5),
            PhaseInfo(id="phase-2", name="Phase 2", estimated_time=0.5),
            PhaseInfo(id="phase-3", name="Phase 3", dependencies=["phase-1", "phase-2"])
        ]
        
        result = self.orchestrator.execute_prd(phases, mode=ExecutionMode.DRY_RUN)
        
        self.assertTrue(result.success)
        self.assertEqual(result.mode, ExecutionMode.DRY_RUN)
        self.assertEqual(result.completed_phases, 3)
        self.assertEqual(result.waves_executed, 2)  # Two waves due to dependencies
    
    @patch('orchestrator.agent_spawner.subprocess.Popen')
    def test_normal_execution(self, mock_popen):
        """Test normal execution mode."""
        # Mock subprocess to simulate agent execution
        mock_process = MagicMock()
        mock_process.poll.return_value = 0  # Process completed
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1"),
            PhaseInfo(id="phase-2", name="Phase 2")
        ]
        
        # Track callbacks
        phase_starts = []
        phase_completes = []
        
        self.orchestrator.on_phase_start = lambda pid, pinfo: phase_starts.append(pid)
        self.orchestrator.on_phase_complete = lambda pid, success: phase_completes.append((pid, success))
        
        result = self.orchestrator.execute_prd(phases, mode=ExecutionMode.NORMAL)
        
        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.mode, ExecutionMode.NORMAL)
        self.assertEqual(result.total_phases, 2)
    
    def test_progress_reporting(self):
        """Test progress reporting during execution."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1"),
            PhaseInfo(id="phase-2", name="Phase 2")
        ]
        
        # Initialize execution (don't actually run)
        self.orchestrator._initialize_execution(phases, ExecutionMode.NORMAL)
        
        # Simulate some progress
        self.orchestrator.execution_state.update_phase_status("phase-1", PhaseStatus.COMPLETED)
        
        progress = self.orchestrator.get_progress()
        
        self.assertEqual(progress.phases_total, 2)
        self.assertEqual(progress.phases_completed, 1)
        self.assertEqual(progress.percent_complete, 50.0)
    
    def test_pause_and_resume(self):
        """Test pause and resume functionality."""
        phases = [PhaseInfo(id="phase-1", name="Phase 1")]
        
        # Initialize execution
        self.orchestrator._initialize_execution(phases, ExecutionMode.NORMAL)
        self.orchestrator._is_running = True
        
        # Pause
        self.orchestrator.pause_execution()
        self.assertTrue(self.orchestrator._pause_requested.is_set())
        
        # Resume
        self.orchestrator.resume_execution()
        self.assertFalse(self.orchestrator._pause_requested.is_set())
        
        # Clean up
        self.orchestrator._is_running = False


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete orchestrator system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_execution(self):
        """Test complete execution flow."""
        # Create orchestrator
        orchestrator = ParallelOrchestrator(self.temp_dir)
        
        # Create test phases with dependencies
        phases = [
            PhaseInfo(id="setup", name="Setup Phase"),
            PhaseInfo(id="build-1", name="Build Component 1", dependencies=["setup"]),
            PhaseInfo(id="build-2", name="Build Component 2", dependencies=["setup"]),
            PhaseInfo(id="test", name="Test Phase", dependencies=["build-1", "build-2"]),
            PhaseInfo(id="deploy", name="Deploy Phase", dependencies=["test"])
        ]
        
        # Execute in dry run mode
        result = orchestrator.execute_prd(phases, mode=ExecutionMode.DRY_RUN)
        
        self.assertTrue(result.success)
        self.assertEqual(result.completed_phases, 5)
        self.assertEqual(result.waves_executed, 4)  # setup -> build-1&2 -> test -> deploy
    
    def test_state_persistence_across_runs(self):
        """Test state persistence between orchestrator instances."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1"),
            PhaseInfo(id="phase-2", name="Phase 2")
        ]
        
        # First orchestrator - initialize execution
        orchestrator1 = ParallelOrchestrator(self.temp_dir)
        orchestrator1._initialize_execution(phases, ExecutionMode.NORMAL)
        
        # Simulate some progress
        orchestrator1.execution_state.update_phase_status("phase-1", PhaseStatus.COMPLETED)
        orchestrator1.state_manager.save_execution_state(orchestrator1.execution_state)
        
        # Second orchestrator - resume execution
        orchestrator2 = ParallelOrchestrator(self.temp_dir)
        resumed = orchestrator2._resume_execution()
        
        self.assertTrue(resumed)
        self.assertEqual(
            orchestrator2.execution_state.get_phase_status("phase-1"),
            PhaseStatus.COMPLETED
        )


if __name__ == '__main__':
    unittest.main()