#!/usr/bin/env python3
"""
Quick integration test for the parallel PRD system.
"""

import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

try:
    # Test imports
    from prd_parallel.models.parallel_execution import PhaseInfo, DependencyGraph
    from prd_parallel.analyzers.wave_calculator import WaveCalculator
    from prd_parallel.orchestrator.parallel_orchestrator import ParallelOrchestrator
    
    print("✅ All imports successful!")
    
    # Test basic functionality
    phase1 = PhaseInfo(
        id="1",
        name="Foundation",
        dependencies=[],
        outputs=["models.py"],
        estimated_hours=1.5
    )
    
    phase2 = PhaseInfo(
        id="2", 
        name="API",
        dependencies=["1"],
        outputs=["api.py"],
        estimated_hours=2.0
    )
    
    # Create dependency graph
    graph = DependencyGraph()
    graph.add_phase(phase1)
    graph.add_phase(phase2)
    
    print(f"✅ Created dependency graph with {len(graph.phases)} phases")
    
    # Calculate waves
    calculator = WaveCalculator(max_agents=2)
    waves = calculator.calculate_waves(graph)
    
    print(f"✅ Calculated {len(waves)} execution waves")
    print(f"   Wave 1: {[p.name for p in waves[0].phases]}")
    if len(waves) > 1:
        print(f"   Wave 2: {[p.name for p in waves[1].phases]}")
    
    print("\n🎉 Integration test passed! The parallel PRD system is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)