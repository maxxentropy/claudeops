"""
End-to-end integration tests for parallel PRD execution.

Tests complete workflows from PRD parsing through parallel execution
with monitoring and metrics collection.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import time
import json

from ..parsers.phase_parser import PRDParser
from ..analyzers.dependency_analyzer import DependencyAnalyzer
from ..analyzers.wave_calculator import WaveCalculator
from ..orchestrator.parallel_orchestrator import ParallelOrchestrator
from ..orchestrator.state_manager import StateManager
from ..monitoring.metrics_collector import MetricsCollector
from ..config.parallel_config import ParallelExecutionConfig


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete parallel execution workflows."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config = ParallelExecutionConfig(
            max_concurrent_agents=3,
            agent_timeout_hours=1.0,
            checkpoint_interval_minutes=5,
            enable_monitoring=True
        )
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_simple_linear_workflow(self):
        """Test execution of simple linear dependencies."""
        # Create test PRD
        prd_content = """
# Feature: User Authentication

## Phase 1: Database Schema
Create user and session tables.
Estimated hours: 2

## Phase 2: User Model
**Dependencies**: Phase 1
Implement User model with authentication.
Estimated hours: 3

## Phase 3: Auth API
**Dependencies**: Phase 2
Create authentication endpoints.
Estimated hours: 4
"""
        prd_path = Path(self.test_dir) / "auth.md"
        prd_path.write_text(prd_content)
        
        # Parse PRD
        parser = PRDParser()
        phases = parser.parse_file(str(prd_path))
        self.assertEqual(len(phases), 3)
        
        # Analyze dependencies
        analyzer = DependencyAnalyzer()
        graph = analyzer.build_dependency_graph(phases)
        
        # Calculate waves
        calculator = WaveCalculator()
        waves = calculator.calculate_waves(phases, graph)
        self.assertEqual(len(waves), 3)  # Linear = 3 sequential waves
        
        # Create orchestrator
        state_manager = StateManager(Path(self.test_dir) / "state")
        orchestrator = ParallelOrchestrator(state_manager, self.config)
        
        # Start metrics collection
        metrics = MetricsCollector(Path(self.test_dir) / "metrics")
        metrics.start_collection("test_linear")
        
        # Mock execution
        execution = orchestrator._create_execution(phases, waves, "user-auth")
        state = state_manager.initialize_execution(execution)
        
        # Verify execution structure
        self.assertEqual(execution.status.value, "PENDING")
        self.assertEqual(len(execution.phases), 3)
        self.assertEqual(len(execution.waves), 3)
        
        # Simulate wave execution
        for i, wave in enumerate(waves):
            # All phases in wave should be executable
            can_execute = all(
                graph.in_degree(phase_id) == 0
                for phase_id in wave.phase_ids
            )
            self.assertTrue(can_execute, f"Wave {i} has unmet dependencies")
            
            # Remove completed phases from graph
            for phase_id in wave.phase_ids:
                graph.remove_node(phase_id)
                
    def test_complex_diamond_workflow(self):
        """Test execution with diamond dependency pattern."""
        prd_content = """
# Feature: E-commerce Platform

## Phase 1: Database Design
Design all database schemas.
Estimated hours: 4

## Phase 2: Product Model
**Dependencies**: Phase 1
Implement product catalog.
Estimated hours: 3

## Phase 3: User Model
**Dependencies**: Phase 1
Implement user management.
Estimated hours: 3

## Phase 4: Order System
**Dependencies**: Phase 2, Phase 3
Implement order processing.
Estimated hours: 5
"""
        prd_path = Path(self.test_dir) / "ecommerce.md"
        prd_path.write_text(prd_content)
        
        # Full workflow
        parser = PRDParser()
        phases = parser.parse_file(str(prd_path))
        
        analyzer = DependencyAnalyzer()
        graph = analyzer.build_dependency_graph(phases)
        conflicts = analyzer.detect_resource_conflicts(phases)
        
        calculator = WaveCalculator()
        waves = calculator.calculate_waves(phases, graph, conflicts)
        
        # Verify diamond pattern execution
        self.assertEqual(len(waves), 3)
        self.assertEqual(len(waves[0].phase_ids), 1)  # Phase 1 alone
        self.assertEqual(len(waves[1].phase_ids), 2)  # Phase 2 & 3 parallel
        self.assertEqual(len(waves[2].phase_ids), 1)  # Phase 4 alone
        
        # Verify time savings
        sequential_time = sum(p.estimated_hours for p in phases)
        parallel_time = sum(w.estimated_duration for w in waves)
        self.assertLess(parallel_time, sequential_time)
        
    def test_resource_conflict_handling(self):
        """Test proper handling of resource conflicts."""
        prd_content = """
# Feature: API Refactoring

## Phase 1: Update User Model
Modifies: models/user.py
Estimated hours: 2

## Phase 2: Update Auth API
Modifies: models/user.py, api/auth.py
**Dependencies**: Phase 1
Estimated hours: 3

## Phase 3: Update Profile API  
Modifies: models/user.py, api/profile.py
Estimated hours: 2

## Phase 4: Integration Tests
**Dependencies**: Phase 2, Phase 3
Estimated hours: 1
"""
        prd_path = Path(self.test_dir) / "refactor.md"
        prd_path.write_text(prd_content)
        
        # Parse and analyze
        parser = PRDParser()
        phases = parser.parse_file(str(prd_path))
        
        analyzer = DependencyAnalyzer()
        graph = analyzer.build_dependency_graph(phases)
        conflicts = analyzer.detect_resource_conflicts(phases)
        
        # Phase 2 and 3 both modify user.py - should not be parallel
        self.assertIn("models/user.py", conflicts)
        self.assertEqual(len(conflicts["models/user.py"]), 3)  # Used by phase 1, 2, 3
        
        # Calculate waves with conflicts
        calculator = WaveCalculator()
        waves = calculator.calculate_waves(phases, graph, conflicts)
        
        # Verify conflict resolution
        # Phase 3 should not be in same wave as Phase 2 due to user.py conflict
        phase2_wave = next(i for i, w in enumerate(waves) if "phase-2" in w.phase_ids)
        phase3_wave = next(i for i, w in enumerate(waves) if "phase-3" in w.phase_ids)
        self.assertNotEqual(phase2_wave, phase3_wave)
        
    def test_failure_recovery(self):
        """Test recovery from phase failures."""
        # Create simple PRD
        prd_content = """
# Feature: Test Feature

## Phase 1: Setup
Estimated hours: 1

## Phase 2: Implementation
**Dependencies**: Phase 1
Estimated hours: 2
"""
        prd_path = Path(self.test_dir) / "test.md"
        prd_path.write_text(prd_content)
        
        # Set up execution
        parser = PRDParser()
        phases = parser.parse_file(str(prd_path))
        
        analyzer = DependencyAnalyzer()
        graph = analyzer.build_dependency_graph(phases)
        
        calculator = WaveCalculator()
        waves = calculator.calculate_waves(phases, graph)
        
        state_manager = StateManager(Path(self.test_dir) / "state")
        orchestrator = ParallelOrchestrator(state_manager, self.config)
        
        # Create execution
        execution = orchestrator._create_execution(phases, waves, "test-feature")
        state = state_manager.initialize_execution(execution)
        
        # Simulate phase 1 failure
        state_manager.update_phase_status("phase-1", "FAILED", error="Test error")
        
        # Verify phase 2 cannot proceed
        updated_state = state_manager.get_state()
        phase2 = updated_state.execution.phases["phase-2"]
        self.assertEqual(phase2.status.value, "PENDING")
        
        # Verify execution marked as failed
        self.assertIn(updated_state.execution.status.value, ["FAILED", "PARTIALLY_COMPLETED"])
        
    def test_performance_metrics(self):
        """Test metrics collection and calculation."""
        # Create PRD with parallel opportunities
        prd_content = """
# Feature: Microservices

## Phase 1: Service Design
Estimated hours: 2

## Phase 2: User Service
**Dependencies**: Phase 1
Estimated hours: 4

## Phase 3: Product Service
**Dependencies**: Phase 1
Estimated hours: 3

## Phase 4: Order Service
**Dependencies**: Phase 1
Estimated hours: 5

## Phase 5: API Gateway
**Dependencies**: Phase 2, Phase 3, Phase 4
Estimated hours: 2
"""
        prd_path = Path(self.test_dir) / "microservices.md"
        prd_path.write_text(prd_content)
        
        # Full execution setup
        parser = PRDParser()
        phases = parser.parse_file(str(prd_path))
        
        analyzer = DependencyAnalyzer()
        graph = analyzer.build_dependency_graph(phases)
        
        calculator = WaveCalculator()
        waves = calculator.calculate_waves(phases, graph)
        
        # Start metrics collection
        metrics_collector = MetricsCollector(Path(self.test_dir) / "metrics")
        metrics_collector.start_collection("test_performance")
        
        # Calculate expected metrics
        sequential_time = sum(p.estimated_hours for p in phases)  # 16 hours
        parallel_time = sum(w.estimated_duration for w in waves)   # ~9 hours
        
        # Verify significant time savings
        time_saved = sequential_time - parallel_time
        efficiency = (time_saved / sequential_time) * 100
        
        self.assertGreater(efficiency, 30)  # At least 30% improvement
        self.assertEqual(len(waves), 3)  # Optimal wave count
        
        # Verify wave 2 has maximum parallelism
        wave2 = waves[1]
        self.assertEqual(len(wave2.phase_ids), 3)  # Services in parallel


class TestMonitoringIntegration(unittest.TestCase):
    """Test monitoring and UI integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_metrics_export(self):
        """Test metrics export functionality."""
        metrics = MetricsCollector(Path(self.test_dir))
        metrics.start_collection("test_export")
        
        # Add some test data
        metrics.resource_samples.append({
            'timestamp': datetime.now(),
            'cpu_percent': 45.2,
            'memory_mb': 512.3,
            'active_agents': 2,
            'total_agents': 4
        })
        
        # Create mock execution metrics
        from ..monitoring.metrics_collector import ExecutionMetrics
        
        exec_metrics = ExecutionMetrics(
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_duration_seconds=3600,
            sequential_estimated_hours=10,
            parallel_actual_hours=6,
            time_saved_hours=4,
            time_saved_percentage=40,
            total_phases=5,
            completed_phases=5,
            failed_phases=0,
            average_phase_duration=720,
            total_waves=3,
            average_wave_duration=1200,
            max_wave_duration=1500,
            wave_parallelism=1.67,
            max_concurrent_agents=3,
            average_cpu_usage=45.2,
            peak_cpu_usage=78.5,
            average_memory_mb=512.3,
            peak_memory_mb=1024.0,
            total_lock_requests=10,
            average_lock_wait_time=0.5,
            max_lock_wait_time=2.0,
            lock_contention_rate=10.0,
            parallel_efficiency=40.0,
            resource_utilization=0.452,
            agent_utilization=75.0,
            failure_rate=0.0,
            retry_count=0,
            recovery_success_rate=100.0
        )
        
        # Test CSV export
        csv_path = metrics.export_metrics_csv(exec_metrics)
        self.assertTrue(csv_path.exists())
        
        # Test JSON export
        json_path = metrics.export_metrics_json(exec_metrics)
        self.assertTrue(json_path.exists())
        
        # Verify JSON content
        with open(json_path) as f:
            data = json.load(f)
            self.assertEqual(data['execution_id'], 'test_export')
            self.assertEqual(data['summary']['time_saved_percentage'], 40)
            
        # Test report generation
        report = metrics.generate_report(exec_metrics)
        self.assertIn("40.0% reduction", report)
        self.assertIn("Parallel Efficiency: 40.0%", report)


if __name__ == '__main__':
    unittest.main()