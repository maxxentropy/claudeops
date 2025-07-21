#!/usr/bin/env python3
"""
Example usage of the dependency analysis components.

This demonstrates how Phase 2 components work together to analyze
PRD phases and calculate optimal execution waves.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from models.parallel_execution import PhaseInfo
from parsers.phase_parser import PhaseParser
from analyzers.dependency_analyzer import DependencyAnalyzer
from analyzers.wave_calculator import WaveCalculator
from analyzers.conflict_detector import ConflictDetector


def main():
    """Demonstrate the dependency analysis pipeline."""
    
    print("=== Parallel PRD Execution - Dependency Analysis Demo ===\n")
    
    # Create sample phases (simulating parsed phase files)
    phases = [
        PhaseInfo(
            id="phase-1",
            name="Foundation Setup",
            dependencies=[],
            outputs=["/src/models/base.py", "/src/config.yaml"],
            estimated_time=2.0,
            description="Set up foundational models and configurations"
        ),
        PhaseInfo(
            id="phase-2",
            name="API Layer",
            dependencies=["phase-1"],
            outputs=["/src/api/endpoints.py", "/src/api/auth.py"],
            estimated_time=3.0,
            description="Build REST API endpoints"
        ),
        PhaseInfo(
            id="phase-3",
            name="Database Layer",
            dependencies=["phase-1"],
            outputs=["/src/db/models.py", "/src/db/migrations.py"],
            estimated_time=2.5,
            description="Create database models and migrations"
        ),
        PhaseInfo(
            id="phase-4",
            name="Business Logic",
            dependencies=["phase-2", "phase-3"],
            outputs=["/src/services/user_service.py", "/src/services/data_service.py"],
            estimated_time=4.0,
            description="Implement core business logic"
        ),
        PhaseInfo(
            id="phase-5",
            name="Frontend",
            dependencies=["phase-2"],
            outputs=["/frontend/app.js", "/frontend/styles.css"],
            estimated_time=3.5,
            description="Build frontend application"
        ),
        PhaseInfo(
            id="phase-6",
            name="Integration Tests",
            dependencies=["phase-4", "phase-5"],
            outputs=["/tests/integration/test_api.py", "/tests/integration/test_ui.py"],
            estimated_time=2.0,
            description="Write comprehensive integration tests"
        )
    ]
    
    # Initialize components
    analyzer = DependencyAnalyzer()
    calculator = WaveCalculator()
    detector = ConflictDetector()
    
    # Step 1: Build dependency graph
    print("1. Building Dependency Graph...")
    graph = analyzer.build_dependency_graph(phases)
    print(f"   - Added {len(graph.nodes)} phases to graph")
    print(f"   - Root phases: {[p.id for p in graph.get_root_phases()]}")
    
    # Step 2: Validate dependencies
    print("\n2. Validating Dependencies...")
    errors = analyzer.validate_dependencies(graph)
    if errors:
        print(f"   - Found {len(errors)} validation issues:")
        for error in errors:
            print(f"     * {error.error_type}: {error.message}")
    else:
        print("   - No validation errors found")
    
    # Step 3: Calculate execution waves
    print("\n3. Calculating Execution Waves...")
    waves = calculator.calculate_execution_waves(graph)
    print(f"   - Calculated {len(waves)} execution waves:")
    for wave in waves:
        print(f"     * Wave {wave.wave_number}: {wave.phases}")
    
    # Step 4: Calculate metrics
    print("\n4. Execution Metrics:")
    metrics = calculator.calculate_metrics(waves, graph)
    print(f"   - Total waves: {metrics.total_waves}")
    print(f"   - Max parallelism: {metrics.max_parallelism}")
    print(f"   - Estimated total time: {metrics.total_time} hours")
    print(f"   - Critical path length: {metrics.critical_path_length} phases")
    print(f"   - Utilization score: {metrics.utilization_score:.2%}")
    
    # Step 5: Identify critical path
    print("\n5. Critical Path Analysis:")
    critical_path = calculator.identify_critical_path(graph)
    path_str = " -> ".join([p.id for p in critical_path])
    path_time = sum(p.estimated_time for p in critical_path)
    print(f"   - Critical path: {path_str}")
    print(f"   - Critical path time: {path_time} hours")
    
    # Step 6: Optimize for limited agents
    print("\n6. Optimizing for Limited Agents (max 2):")
    optimized_waves = calculator.optimize_wave_distribution(waves, max_agents=2)
    print(f"   - Optimized to {len(optimized_waves)} waves:")
    for wave in optimized_waves:
        print(f"     * Wave {wave.wave_number}: {wave.phases}")
    
    # Step 7: Detect conflicts
    print("\n7. Conflict Detection:")
    conflicts = detector.analyze_file_conflicts(phases)
    if conflicts:
        print(f"   - Found {len(conflicts)} potential conflicts")
        report = detector.generate_conflict_report(conflicts)
        print("\nConflict Report:")
        print(report)
    else:
        print("   - No file conflicts detected")
    
    # Step 8: Validate parallel safety
    print("\n8. Parallel Safety Validation:")
    phases_dict = {p.id: p for p in phases}
    for wave in waves:
        is_safe = detector.validate_parallel_safety(wave, phases_dict)
        status = "✓ Safe" if is_safe else "✗ Unsafe"
        print(f"   - Wave {wave.wave_number}: {status}")
    
    print("\n=== Analysis Complete ===")


if __name__ == "__main__":
    main()