"""
Comprehensive test suite for dependency analysis components.

Tests the phase parser, dependency analyzer, wave calculator, and conflict detector.
"""

import unittest
import tempfile
import os
from pathlib import Path
from typing import List

from models.parallel_execution import PhaseInfo, DependencyGraph, ExecutionWave, LockType
from parsers.phase_parser import PhaseParser
from analyzers.dependency_analyzer import DependencyAnalyzer, ValidationError, CircularDependencyError
from analyzers.wave_calculator import WaveCalculator
from analyzers.conflict_detector import ConflictDetector, ConflictInfo


class TestPhaseParser(unittest.TestCase):
    """Test the phase file parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = PhaseParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_parse_simple_phase(self):
        """Test parsing a simple phase file."""
        content = """# Phase 1: Foundation Setup
        
Build the core data structures and models for the parallel execution system.

## Dependencies: None

## Estimated Time: 2 hours

## Expected Outputs:
- /src/models/parallel_execution.py
- /src/models/execution_state.py
"""
        
        phase_file = os.path.join(self.temp_dir, "phase-1.md")
        with open(phase_file, 'w') as f:
            f.write(content)
        
        phase = self.parser.parse_phase_file(phase_file)
        
        self.assertEqual(phase.id, "phase-1")
        self.assertEqual(phase.name, "Foundation Setup")
        self.assertEqual(phase.dependencies, [])
        self.assertEqual(phase.estimated_time, 2.0)
        self.assertIn("/src/models/parallel_execution.py", phase.outputs)
        self.assertIn("/src/models/execution_state.py", phase.outputs)
    
    def test_parse_phase_with_dependencies(self):
        """Test parsing a phase with dependencies."""
        content = """# Phase 3: Orchestrator Implementation

## Dependencies: Phase 1, Phase 2

## Time: 1.5 hours
"""
        
        phase_file = os.path.join(self.temp_dir, "phase-3.md")
        with open(phase_file, 'w') as f:
            f.write(content)
        
        phase = self.parser.parse_phase_file(phase_file)
        
        self.assertEqual(phase.id, "phase-3")
        self.assertIn("phase-1", phase.dependencies)
        self.assertIn("phase-2", phase.dependencies)
        self.assertEqual(phase.estimated_time, 1.5)
    
    def test_extract_file_references(self):
        """Test extracting file references from content."""
        content = """
This phase will read `/config/settings.yaml` and update `/src/main.py`.
It also creates a new file at `/docs/guide.md`.

```python
# Working with /data/input.json
with open('/data/input.json') as f:
    data = json.load(f)
```
"""
        
        refs = self.parser.extract_file_references(content)
        
        self.assertIn("/config/settings.yaml", refs)
        self.assertIn("/src/main.py", refs)
        self.assertIn("/docs/guide.md", refs)
        self.assertIn("/data/input.json", refs)
    
    def test_parse_missing_file(self):
        """Test parsing a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_phase_file("/nonexistent/file.md")


class TestDependencyAnalyzer(unittest.TestCase):
    """Test the dependency analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = DependencyAnalyzer()
    
    def test_build_simple_graph(self):
        """Test building a simple dependency graph."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", dependencies=[]),
            PhaseInfo(id="phase-2", name="Phase 2", dependencies=["phase-1"]),
            PhaseInfo(id="phase-3", name="Phase 3", dependencies=["phase-1", "phase-2"])
        ]
        
        graph = self.analyzer.build_dependency_graph(phases)
        
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(graph.get_dependents("phase-1"), {"phase-2", "phase-3"})
        self.assertEqual(graph.get_dependents("phase-2"), {"phase-3"})
        self.assertEqual(len(graph.get_root_phases()), 1)
    
    def test_detect_circular_dependency(self):
        """Test detecting circular dependencies."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", dependencies=["phase-3"]),
            PhaseInfo(id="phase-2", name="Phase 2", dependencies=["phase-1"]),
            PhaseInfo(id="phase-3", name="Phase 3", dependencies=["phase-2"])
        ]
        
        graph = self.analyzer.build_dependency_graph(phases)
        has_cycle = self.analyzer.detect_circular_dependencies(graph)
        
        self.assertTrue(has_cycle)
    
    def test_validate_dependencies(self):
        """Test dependency validation."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", dependencies=[], outputs=["/src/base.py"]),
            PhaseInfo(id="phase-2", name="Phase 2", dependencies=["phase-1"], outputs=[]),
            PhaseInfo(id="phase-3", name="Phase 3", dependencies=["phase-1"], outputs=["/src/other.py"])
        ]
        
        graph = self.analyzer.build_dependency_graph(phases)
        errors = self.analyzer.validate_dependencies(graph)
        
        # Should have warning about phase-2 having no outputs
        no_output_errors = [e for e in errors if e.error_type == "no_outputs"]
        self.assertEqual(len(no_output_errors), 1)
        self.assertIn("phase-2", no_output_errors[0].affected_phases)
    
    def test_missing_dependency_error(self):
        """Test error when referencing non-existent dependency."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", dependencies=["phase-0"]),
        ]
        
        with self.assertRaises(ValueError) as ctx:
            self.analyzer.build_dependency_graph(phases)
        
        self.assertIn("non-existent phase", str(ctx.exception))


class TestWaveCalculator(unittest.TestCase):
    """Test the wave calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = WaveCalculator()
    
    def test_calculate_simple_waves(self):
        """Test calculating waves for a simple graph."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", dependencies=[]),
            PhaseInfo(id="phase-2", name="Phase 2", dependencies=[]),
            PhaseInfo(id="phase-3", name="Phase 3", dependencies=["phase-1", "phase-2"])
        ]
        
        graph = DependencyGraph()
        for phase in phases:
            graph.add_phase(phase)
        
        waves = self.calculator.calculate_execution_waves(graph)
        
        self.assertEqual(len(waves), 2)
        self.assertEqual(set(waves[0].phases), {"phase-1", "phase-2"})
        self.assertEqual(set(waves[1].phases), {"phase-3"})
    
    def test_optimize_wave_distribution(self):
        """Test optimizing waves with agent limits."""
        # Create a wave with 5 phases
        wave = ExecutionWave(wave_number=0)
        for i in range(1, 6):
            wave.add_phase(f"phase-{i}")
        
        # Optimize with max 3 agents
        optimized = self.calculator.optimize_wave_distribution([wave], max_agents=3)
        
        self.assertEqual(len(optimized), 2)
        self.assertLessEqual(len(optimized[0].phases), 3)
        self.assertLessEqual(len(optimized[1].phases), 3)
    
    def test_estimate_total_time(self):
        """Test estimating total execution time."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", estimated_time=2.0),
            PhaseInfo(id="phase-2", name="Phase 2", estimated_time=1.5),
            PhaseInfo(id="phase-3", name="Phase 3", estimated_time=3.0)
        ]
        
        graph = DependencyGraph()
        for phase in phases:
            graph.add_phase(phase)
        
        waves = [
            ExecutionWave(wave_number=0, phases=["phase-1", "phase-2"]),
            ExecutionWave(wave_number=1, phases=["phase-3"])
        ]
        
        total_time = self.calculator.estimate_total_time(waves, graph)
        
        # Wave 1: max(2.0, 1.5) = 2.0
        # Wave 2: 3.0
        # Total: 5.0
        self.assertEqual(total_time, 5.0)
    
    def test_identify_critical_path(self):
        """Test identifying the critical path."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", estimated_time=1.0),
            PhaseInfo(id="phase-2", name="Phase 2", dependencies=["phase-1"], estimated_time=2.0),
            PhaseInfo(id="phase-3", name="Phase 3", dependencies=["phase-1"], estimated_time=1.0),
            PhaseInfo(id="phase-4", name="Phase 4", dependencies=["phase-2", "phase-3"], estimated_time=1.0)
        ]
        
        graph = DependencyGraph()
        for phase in phases:
            graph.add_phase(phase)
        
        critical_path = self.calculator.identify_critical_path(graph)
        
        # Critical path should be: phase-1 -> phase-2 -> phase-4 (total: 4.0)
        self.assertEqual(len(critical_path), 3)
        self.assertEqual([p.id for p in critical_path], ["phase-1", "phase-2", "phase-4"])
    
    def test_circular_dependency_error(self):
        """Test error handling for circular dependencies."""
        phases = [
            PhaseInfo(id="phase-1", name="Phase 1", dependencies=["phase-2"]),
            PhaseInfo(id="phase-2", name="Phase 2", dependencies=["phase-1"])
        ]
        
        graph = DependencyGraph()
        for phase in phases:
            graph.add_phase(phase)
        
        with self.assertRaises(ValueError) as ctx:
            self.calculator.calculate_execution_waves(graph)
        
        self.assertIn("Circular dependency", str(ctx.exception))


class TestConflictDetector(unittest.TestCase):
    """Test the conflict detector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = ConflictDetector()
    
    def test_detect_write_write_conflict(self):
        """Test detecting write-write conflicts."""
        phases = [
            PhaseInfo(
                id="phase-1", 
                name="Phase 1",
                outputs=["/src/config.py"],
                description="Generate configuration file"
            ),
            PhaseInfo(
                id="phase-2",
                name="Phase 2", 
                outputs=["/src/config.py"],
                description="Create config from template"
            )
        ]
        
        conflicts = self.detector.analyze_file_conflicts(phases)
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, "write-write")
        self.assertEqual(conflicts[0].severity, "high")
        self.assertIn("phase-1", conflicts[0].conflicting_phases)
        self.assertIn("phase-2", conflicts[0].conflicting_phases)
    
    def test_suggest_lock_requirements(self):
        """Test suggesting locks for conflicts."""
        conflict = ConflictInfo(
            resource_path="/src/data.json",
            conflicting_phases=["phase-1", "phase-2"],
            conflict_type="write-write",
            severity="high",
            suggested_resolution="Use exclusive locks"
        )
        
        locks = self.detector.suggest_lock_requirements([conflict])
        
        self.assertEqual(len(locks), 2)
        for lock in locks:
            self.assertEqual(lock.resource_path, "/src/data.json")
            self.assertEqual(lock.lock_type, LockType.EXCLUSIVE)
    
    def test_validate_parallel_safety(self):
        """Test validating parallel safety of a wave."""
        phases = {
            "phase-1": PhaseInfo(
                id="phase-1",
                name="Phase 1",
                outputs=["/src/shared.py"]
            ),
            "phase-2": PhaseInfo(
                id="phase-2",
                name="Phase 2",
                outputs=["/src/shared.py"]
            ),
            "phase-3": PhaseInfo(
                id="phase-3",
                name="Phase 3",
                outputs=["/src/other.py"]
            )
        }
        
        # Wave with conflicting phases
        unsafe_wave = ExecutionWave(wave_number=0, phases=["phase-1", "phase-2"])
        self.assertFalse(self.detector.validate_parallel_safety(unsafe_wave, phases))
        
        # Wave without conflicts
        safe_wave = ExecutionWave(wave_number=1, phases=["phase-1", "phase-3"])
        self.assertTrue(self.detector.validate_parallel_safety(safe_wave, phases))
    
    def test_generate_conflict_report(self):
        """Test generating a conflict report."""
        conflicts = [
            ConflictInfo(
                resource_path="/src/main.py",
                conflicting_phases=["phase-1", "phase-2"],
                conflict_type="write-write",
                severity="high",
                suggested_resolution="Use exclusive locks"
            ),
            ConflictInfo(
                resource_path="/data/cache.json",
                conflicting_phases=["phase-2", "phase-3"],
                conflict_type="write-read",
                severity="medium",
                suggested_resolution="Ensure readers complete first"
            )
        ]
        
        report = self.detector.generate_conflict_report(conflicts)
        
        self.assertIn("Total conflicts detected: 2", report)
        self.assertIn("High: 1", report)
        self.assertIn("Medium: 1", report)
        self.assertIn("/src/main.py", report)
        self.assertIn("/data/cache.json", report)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete analysis pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = PhaseParser()
        self.analyzer = DependencyAnalyzer(self.parser)
        self.calculator = WaveCalculator()
        self.detector = ConflictDetector()
    
    def test_full_analysis_pipeline(self):
        """Test the complete analysis pipeline."""
        # Create test phases
        phases = [
            PhaseInfo(
                id="phase-1",
                name="Setup",
                dependencies=[],
                outputs=["/src/base.py"],
                estimated_time=1.0
            ),
            PhaseInfo(
                id="phase-2",
                name="Core Features",
                dependencies=["phase-1"],
                outputs=["/src/features.py"],
                estimated_time=2.0
            ),
            PhaseInfo(
                id="phase-3",
                name="Utils",
                dependencies=["phase-1"],
                outputs=["/src/utils.py"],
                estimated_time=1.5
            ),
            PhaseInfo(
                id="phase-4",
                name="Integration",
                dependencies=["phase-2", "phase-3"],
                outputs=["/src/main.py"],
                estimated_time=1.0
            )
        ]
        
        # Build dependency graph
        graph = self.analyzer.build_dependency_graph(phases)
        
        # Validate dependencies
        errors = self.analyzer.validate_dependencies(graph)
        self.assertEqual(len(errors), 0)
        
        # Calculate waves
        waves = self.calculator.calculate_execution_waves(graph)
        self.assertEqual(len(waves), 3)
        
        # Check for conflicts
        conflicts = self.detector.analyze_file_conflicts(phases)
        self.assertEqual(len(conflicts), 0)  # No conflicts in this example
        
        # Calculate metrics
        metrics = self.calculator.calculate_metrics(waves, graph)
        self.assertEqual(metrics.total_waves, 3)
        self.assertEqual(metrics.max_parallelism, 2)  # phase-2 and phase-3 in parallel


if __name__ == '__main__':
    unittest.main()