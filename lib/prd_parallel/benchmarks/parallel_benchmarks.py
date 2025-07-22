"""
Performance benchmarks for parallel PRD execution.

Measures performance improvements, overhead costs, and scalability
of the parallel execution system.
"""

import time
import statistics
import random
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from ..models.parallel_execution import Phase, Wave, ParallelExecution
from ..analyzers.dependency_analyzer import DependencyAnalyzer
from ..analyzers.wave_calculator import WaveCalculator
from ..orchestrator.parallel_orchestrator import ParallelOrchestrator
from ..orchestrator.state_manager import StateManager
from ..monitoring.metrics_collector import MetricsCollector
from ..config.parallel_config import ParallelExecutionConfig


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    name: str
    num_phases: int
    sequential_time: float
    parallel_time: float
    time_reduction: float
    speedup: float
    efficiency: float
    overhead_time: float
    max_concurrency: int
    avg_wave_size: float


class ParallelBenchmarks:
    """Performance benchmarking suite for parallel execution."""
    
    def __init__(self, output_dir: Path = None):
        """Initialize benchmarks.
        
        Args:
            output_dir: Directory for benchmark outputs
        """
        self.output_dir = output_dir or Path("./benchmark_results")
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[BenchmarkResult] = []
        
    def benchmark_sequential_vs_parallel(self, 
                                       phase_counts: List[int] = None) -> Dict[str, Any]:
        """Benchmark sequential vs parallel execution.
        
        Args:
            phase_counts: List of phase counts to test
            
        Returns:
            Benchmark report with comparisons
        """
        phase_counts = phase_counts or [5, 10, 20, 50, 100]
        results = []
        
        for count in phase_counts:
            print(f"\nBenchmarking with {count} phases...")
            
            # Generate test phases
            phases = self._generate_test_phases(count)
            
            # Time sequential execution
            seq_start = time.time()
            seq_time = sum(p.estimated_hours for p in phases) * 3600  # Convert to seconds
            seq_end = time.time()
            seq_overhead = seq_end - seq_start
            
            # Time parallel execution
            par_start = time.time()
            
            # Analyze dependencies and calculate waves
            analyzer = DependencyAnalyzer()
            graph = analyzer.build_dependency_graph(phases)
            
            calculator = WaveCalculator()
            waves = calculator.calculate_waves(phases, graph)
            
            # Calculate parallel time
            par_time = sum(w.estimated_duration for w in waves) * 3600  # Convert to seconds
            par_end = time.time()
            par_overhead = par_end - par_start
            
            # Calculate metrics
            time_reduction = ((seq_time - par_time) / seq_time) * 100
            speedup = seq_time / par_time if par_time > 0 else 1.0
            efficiency = speedup / len(waves) if waves else 0
            max_concurrency = max(len(w.phase_ids) for w in waves) if waves else 1
            avg_wave_size = statistics.mean(len(w.phase_ids) for w in waves) if waves else 1
            
            result = BenchmarkResult(
                name=f"{count}_phases",
                num_phases=count,
                sequential_time=seq_time,
                parallel_time=par_time,
                time_reduction=time_reduction,
                speedup=speedup,
                efficiency=efficiency,
                overhead_time=par_overhead,
                max_concurrency=max_concurrency,
                avg_wave_size=avg_wave_size
            )
            
            results.append(result)
            self.results.append(result)
            
            print(f"  Sequential: {seq_time/3600:.2f}h")
            print(f"  Parallel: {par_time/3600:.2f}h")
            print(f"  Speedup: {speedup:.2f}x")
            print(f"  Time saved: {time_reduction:.1f}%")
            
        # Generate report
        report = self._generate_benchmark_report(results)
        
        # Create visualizations
        self._plot_speedup_chart(results)
        self._plot_efficiency_chart(results)
        
        return report
        
    def measure_overhead_costs(self) -> Dict[str, float]:
        """Measure various overhead costs in the system.
        
        Returns:
            Dictionary of overhead measurements
        """
        print("\nMeasuring system overhead...")
        
        overheads = {}
        iterations = 100
        
        # Measure dependency analysis overhead
        phases = self._generate_test_phases(20)
        
        analysis_times = []
        for _ in range(iterations):
            start = time.time()
            analyzer = DependencyAnalyzer()
            graph = analyzer.build_dependency_graph(phases)
            end = time.time()
            analysis_times.append(end - start)
            
        overheads['dependency_analysis_ms'] = statistics.mean(analysis_times) * 1000
        
        # Measure wave calculation overhead
        wave_times = []
        for _ in range(iterations):
            start = time.time()
            calculator = WaveCalculator()
            waves = calculator.calculate_waves(phases, graph)
            end = time.time()
            wave_times.append(end - start)
            
        overheads['wave_calculation_ms'] = statistics.mean(wave_times) * 1000
        
        # Measure state persistence overhead
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            
            persist_times = []
            for _ in range(iterations):
                execution = self._create_test_execution(phases)
                start = time.time()
                state_manager.initialize_execution(execution)
                end = time.time()
                persist_times.append(end - start)
                
        overheads['state_persistence_ms'] = statistics.mean(persist_times) * 1000
        
        # Measure agent spawn overhead (simulated)
        spawn_times = []
        for _ in range(iterations):
            start = time.time()
            # Simulate agent spawn delay
            time.sleep(0.01)  # 10ms spawn time
            end = time.time()
            spawn_times.append(end - start)
            
        overheads['agent_spawn_ms'] = statistics.mean(spawn_times) * 1000
        
        # Total overhead
        overheads['total_overhead_ms'] = sum(overheads.values())
        
        print(f"\nOverhead measurements:")
        for key, value in overheads.items():
            print(f"  {key}: {value:.2f}ms")
            
        return overheads
        
    def test_scalability(self, max_phases: int = 100) -> Dict[str, Any]:
        """Test system scalability with increasing phase counts.
        
        Args:
            max_phases: Maximum number of phases to test
            
        Returns:
            Scalability analysis results
        """
        print(f"\nTesting scalability up to {max_phases} phases...")
        
        phase_counts = [5, 10, 20, 30, 50, 75, 100]
        phase_counts = [p for p in phase_counts if p <= max_phases]
        
        scalability_data = {
            'phase_counts': phase_counts,
            'execution_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'efficiency': []
        }
        
        for count in phase_counts:
            print(f"  Testing {count} phases...")
            
            # Generate phases with complex dependencies
            phases = self._generate_complex_phases(count)
            
            # Measure execution
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            analyzer = DependencyAnalyzer()
            graph = analyzer.build_dependency_graph(phases)
            
            calculator = WaveCalculator()
            waves = calculator.calculate_waves(phases, graph)
            
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            # Calculate metrics
            exec_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            seq_time = sum(p.estimated_hours for p in phases)
            par_time = sum(w.estimated_duration for w in waves)
            efficiency = ((seq_time - par_time) / seq_time) * 100 if seq_time > 0 else 0
            
            scalability_data['execution_times'].append(exec_time)
            scalability_data['memory_usage'].append(memory_delta)
            scalability_data['efficiency'].append(efficiency)
            
        # Plot scalability graphs
        self._plot_scalability_charts(scalability_data)
        
        # Analyze scalability
        analysis = {
            'linear_scalability': self._check_linear_scalability(scalability_data),
            'memory_efficiency': self._analyze_memory_efficiency(scalability_data),
            'performance_degradation': self._analyze_performance_degradation(scalability_data)
        }
        
        return {
            'data': scalability_data,
            'analysis': analysis
        }
        
    def analyze_resource_usage(self) -> Dict[str, Any]:
        """Analyze resource usage patterns during execution.
        
        Returns:
            Resource usage statistics
        """
        print("\nAnalyzing resource usage patterns...")
        
        # Test with different concurrency levels
        concurrency_levels = [1, 2, 4, 8, 16]
        resource_stats = []
        
        for max_agents in concurrency_levels:
            print(f"  Testing with {max_agents} agents...")
            
            # Configure for testing
            config = ParallelExecutionConfig(
                max_concurrent_agents=max_agents,
                agent_timeout_hours=1.0
            )
            
            # Generate test workload
            phases = self._generate_test_phases(30)
            
            # Simulate execution and measure resources
            stats = self._simulate_execution_resources(phases, config)
            stats['max_agents'] = max_agents
            resource_stats.append(stats)
            
        # Analyze patterns
        analysis = {
            'optimal_concurrency': self._find_optimal_concurrency(resource_stats),
            'resource_efficiency': self._calculate_resource_efficiency(resource_stats),
            'bottlenecks': self._identify_bottlenecks(resource_stats)
        }
        
        # Create resource usage visualizations
        self._plot_resource_charts(resource_stats)
        
        return {
            'stats': resource_stats,
            'analysis': analysis
        }
        
    def _generate_test_phases(self, count: int) -> List[Phase]:
        """Generate test phases with dependencies."""
        phases = []
        
        for i in range(count):
            # Create dependencies (previous 1-3 phases)
            dependencies = []
            if i > 0:
                num_deps = min(random.randint(0, 2), i)
                if num_deps > 0:
                    dep_indices = random.sample(range(i), num_deps)
                    dependencies = [f"phase-{j+1}" for j in dep_indices]
                    
            phase = Phase(
                phase_id=f"phase-{i+1}",
                name=f"Test Phase {i+1}",
                description=f"Test phase number {i+1}",
                dependencies=dependencies,
                estimated_hours=random.uniform(1, 5),
                modifies_files=[f"file_{i}.py"] if random.random() > 0.5 else []
            )
            phases.append(phase)
            
        return phases
        
    def _generate_complex_phases(self, count: int) -> List[Phase]:
        """Generate phases with complex dependency patterns."""
        phases = []
        
        # Create layers for complex patterns
        layers = int(np.sqrt(count))
        phases_per_layer = count // layers
        
        phase_counter = 0
        for layer in range(layers):
            for j in range(phases_per_layer):
                phase_counter += 1
                
                # Dependencies from previous layer
                dependencies = []
                if layer > 0:
                    # Connect to 1-3 phases from previous layer
                    prev_layer_start = (layer - 1) * phases_per_layer
                    num_deps = min(random.randint(1, 3), phases_per_layer)
                    dep_indices = random.sample(
                        range(prev_layer_start, prev_layer_start + phases_per_layer),
                        num_deps
                    )
                    dependencies = [f"phase-{i+1}" for i in dep_indices]
                    
                phase = Phase(
                    phase_id=f"phase-{phase_counter}",
                    name=f"Complex Phase {phase_counter}",
                    description=f"Layer {layer}, position {j}",
                    dependencies=dependencies,
                    estimated_hours=random.uniform(1, 8),
                    modifies_files=[f"module_{layer}/file_{j}.py"]
                )
                phases.append(phase)
                
        return phases[:count]
        
    def _create_test_execution(self, phases: List[Phase]) -> ParallelExecution:
        """Create a test parallel execution."""
        from ..models.execution_state import ExecutionStatus
        
        waves = [Wave(
            wave_id=f"wave-{i}",
            name=f"Wave {i}",
            phase_ids=[p.phase_id for p in phases[i:i+3]],
            estimated_duration=max(p.estimated_hours for p in phases[i:i+3])
        ) for i in range(0, len(phases), 3)]
        
        return ParallelExecution(
            execution_id=f"test-{datetime.now().timestamp()}",
            feature_name="test-feature",
            status=ExecutionStatus.PENDING,
            phases={p.phase_id: p for p in phases},
            waves=waves,
            created_at=datetime.now()
        )
        
    def _simulate_execution_resources(self, phases: List[Phase], 
                                    config: ParallelExecutionConfig) -> Dict[str, Any]:
        """Simulate execution and measure resource usage."""
        # This would integrate with actual execution in production
        # For benchmarking, we simulate the metrics
        
        analyzer = DependencyAnalyzer()
        graph = analyzer.build_dependency_graph(phases)
        
        calculator = WaveCalculator()
        waves = calculator.calculate_waves(phases, graph)
        
        # Simulate resource usage
        total_time = sum(w.estimated_duration for w in waves)
        avg_concurrency = statistics.mean(min(len(w.phase_ids), config.max_concurrent_agents) 
                                        for w in waves)
        
        return {
            'total_time_hours': total_time,
            'average_concurrency': avg_concurrency,
            'cpu_utilization': avg_concurrency / config.max_concurrent_agents * 85,  # Simulated
            'memory_per_agent_mb': 256 + random.uniform(-50, 50),  # Simulated
            'lock_contention_rate': random.uniform(5, 15),  # Simulated percentage
            'agent_idle_time_pct': max(0, (1 - avg_concurrency / config.max_concurrent_agents) * 100)
        }
        
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
        
    def _generate_benchmark_report(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        report = {
            'summary': {
                'total_benchmarks': len(results),
                'average_speedup': statistics.mean(r.speedup for r in results),
                'average_time_reduction': statistics.mean(r.time_reduction for r in results),
                'max_speedup': max(r.speedup for r in results),
                'max_time_reduction': max(r.time_reduction for r in results)
            },
            'details': [
                {
                    'phases': r.num_phases,
                    'sequential_hours': r.sequential_time / 3600,
                    'parallel_hours': r.parallel_time / 3600,
                    'speedup': f"{r.speedup:.2f}x",
                    'time_saved': f"{r.time_reduction:.1f}%",
                    'efficiency': f"{r.efficiency:.2f}",
                    'max_concurrency': r.max_concurrency
                }
                for r in results
            ]
        }
        
        # Save report
        import json
        report_path = self.output_dir / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
        
    def _plot_speedup_chart(self, results: List[BenchmarkResult]) -> None:
        """Plot speedup comparison chart."""
        phases = [r.num_phases for r in results]
        speedups = [r.speedup for r in results]
        
        plt.figure(figsize=(10, 6))
        plt.plot(phases, speedups, 'b-o', linewidth=2, markersize=8)
        plt.xlabel('Number of Phases')
        plt.ylabel('Speedup Factor')
        plt.title('Parallel Execution Speedup vs Sequential')
        plt.grid(True, alpha=0.3)
        
        # Add ideal speedup line
        ideal_speedup = [min(p/5, 4) for p in phases]  # Assuming ~5 phases per wave
        plt.plot(phases, ideal_speedup, 'g--', label='Theoretical Maximum', alpha=0.5)
        
        plt.legend()
        plt.savefig(self.output_dir / 'speedup_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def _plot_efficiency_chart(self, results: List[BenchmarkResult]) -> None:
        """Plot efficiency trends."""
        phases = [r.num_phases for r in results]
        time_reductions = [r.time_reduction for r in results]
        
        plt.figure(figsize=(10, 6))
        plt.bar(phases, time_reductions, color='green', alpha=0.7)
        plt.xlabel('Number of Phases')
        plt.ylabel('Time Reduction (%)')
        plt.title('Time Savings with Parallel Execution')
        plt.grid(True, axis='y', alpha=0.3)
        
        # Add trend line
        z = np.polyfit(phases, time_reductions, 2)
        p = np.poly1d(z)
        plt.plot(phases, p(phases), 'r--', linewidth=2, label='Trend')
        
        plt.legend()
        plt.savefig(self.output_dir / 'efficiency_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def _plot_scalability_charts(self, data: Dict[str, List]) -> None:
        """Plot scalability analysis charts."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Execution time scalability
        ax1.plot(data['phase_counts'], data['execution_times'], 'b-o', linewidth=2)
        ax1.set_xlabel('Number of Phases')
        ax1.set_ylabel('Analysis Time (seconds)')
        ax1.set_title('Execution Time Scalability')
        ax1.grid(True, alpha=0.3)
        
        # Memory usage scalability
        ax2.plot(data['phase_counts'], data['memory_usage'], 'r-o', linewidth=2)
        ax2.set_xlabel('Number of Phases')
        ax2.set_ylabel('Memory Usage (MB)')
        ax2.set_title('Memory Usage Scalability')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'scalability_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def _plot_resource_charts(self, stats: List[Dict[str, Any]]) -> None:
        """Plot resource usage analysis."""
        agents = [s['max_agents'] for s in stats]
        cpu_usage = [s['cpu_utilization'] for s in stats]
        idle_time = [s['agent_idle_time_pct'] for s in stats]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # CPU utilization
        ax1.plot(agents, cpu_usage, 'g-o', linewidth=2, markersize=8)
        ax1.set_xlabel('Max Concurrent Agents')
        ax1.set_ylabel('CPU Utilization (%)')
        ax1.set_title('CPU Utilization vs Concurrency')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # Agent idle time
        ax2.bar(agents, idle_time, color='orange', alpha=0.7)
        ax2.set_xlabel('Max Concurrent Agents')
        ax2.set_ylabel('Agent Idle Time (%)')
        ax2.set_title('Agent Utilization Efficiency')
        ax2.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'resource_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def _check_linear_scalability(self, data: Dict[str, List]) -> bool:
        """Check if system scales linearly."""
        # Calculate correlation between phase count and execution time
        phases = np.array(data['phase_counts'])
        times = np.array(data['execution_times'])
        
        correlation = np.corrcoef(phases, times)[0, 1]
        
        # Strong linear correlation indicates good scalability
        return correlation > 0.95
        
    def _analyze_memory_efficiency(self, data: Dict[str, List]) -> Dict[str, float]:
        """Analyze memory efficiency."""
        phases = np.array(data['phase_counts'])
        memory = np.array(data['memory_usage'])
        
        # Memory per phase
        memory_per_phase = memory / phases
        avg_memory_per_phase = np.mean(memory_per_phase)
        
        return {
            'average_mb_per_phase': avg_memory_per_phase,
            'memory_growth_rate': np.polyfit(phases, memory, 1)[0],
            'memory_efficiency': 1.0 / avg_memory_per_phase * 100  # Arbitrary scale
        }
        
    def _analyze_performance_degradation(self, data: Dict[str, List]) -> Dict[str, Any]:
        """Analyze performance degradation with scale."""
        efficiency = np.array(data['efficiency'])
        phases = np.array(data['phase_counts'])
        
        # Fit degradation curve
        z = np.polyfit(phases, efficiency, 2)
        degradation_rate = -z[0] * 100  # Negative quadratic coefficient
        
        return {
            'degradation_rate': degradation_rate,
            'maintains_efficiency': degradation_rate < 0.1,  # Less than 0.1% per phase
            'efficiency_at_100_phases': np.poly1d(z)(100)
        }
        
    def _find_optimal_concurrency(self, stats: List[Dict[str, Any]]) -> int:
        """Find optimal concurrency level."""
        # Balance between CPU usage and idle time
        scores = []
        
        for s in stats:
            # Score based on high CPU usage and low idle time
            score = s['cpu_utilization'] - s['agent_idle_time_pct']
            scores.append((s['max_agents'], score))
            
        # Return concurrency with highest score
        return max(scores, key=lambda x: x[1])[0]
        
    def _calculate_resource_efficiency(self, stats: List[Dict[str, Any]]) -> float:
        """Calculate overall resource efficiency."""
        efficiencies = []
        
        for s in stats:
            # Efficiency = CPU utilization * (1 - idle_time/100)
            eff = s['cpu_utilization'] * (1 - s['agent_idle_time_pct'] / 100)
            efficiencies.append(eff)
            
        return statistics.mean(efficiencies)
        
    def _identify_bottlenecks(self, stats: List[Dict[str, Any]]) -> List[str]:
        """Identify system bottlenecks."""
        bottlenecks = []
        
        # Check for high lock contention
        high_contention = [s for s in stats if s['lock_contention_rate'] > 20]
        if high_contention:
            bottlenecks.append("High lock contention detected")
            
        # Check for poor agent utilization
        poor_utilization = [s for s in stats if s['agent_idle_time_pct'] > 50]
        if poor_utilization:
            bottlenecks.append("Poor agent utilization")
            
        # Check for memory constraints
        high_memory = [s for s in stats if s['memory_per_agent_mb'] > 512]
        if high_memory:
            bottlenecks.append("High memory usage per agent")
            
        return bottlenecks


# Main benchmark runner
def run_all_benchmarks(output_dir: Path = None) -> None:
    """Run all performance benchmarks.
    
    Args:
        output_dir: Directory for benchmark outputs
    """
    benchmarks = ParallelBenchmarks(output_dir)
    
    print("=" * 60)
    print("Running Parallel PRD Execution Benchmarks")
    print("=" * 60)
    
    # Run benchmarks
    seq_vs_par = benchmarks.benchmark_sequential_vs_parallel()
    overhead = benchmarks.measure_overhead_costs()
    scalability = benchmarks.test_scalability()
    resources = benchmarks.analyze_resource_usage()
    
    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    
    print(f"\nPerformance Improvements:")
    print(f"  Average Speedup: {seq_vs_par['summary']['average_speedup']:.2f}x")
    print(f"  Average Time Saved: {seq_vs_par['summary']['average_time_reduction']:.1f}%")
    print(f"  Maximum Speedup: {seq_vs_par['summary']['max_speedup']:.2f}x")
    
    print(f"\nSystem Overhead:")
    print(f"  Total Overhead: {overhead['total_overhead_ms']:.1f}ms")
    print(f"  Dependency Analysis: {overhead['dependency_analysis_ms']:.1f}ms")
    print(f"  Wave Calculation: {overhead['wave_calculation_ms']:.1f}ms")
    
    print(f"\nScalability:")
    print(f"  Linear Scalability: {'Yes' if scalability['analysis']['linear_scalability'] else 'No'}")
    print(f"  Memory Efficiency: {scalability['analysis']['memory_efficiency']['memory_efficiency']:.1f}")
    
    print(f"\nResource Usage:")
    print(f"  Optimal Concurrency: {resources['analysis']['optimal_concurrency']} agents")
    print(f"  Resource Efficiency: {resources['analysis']['resource_efficiency']:.1f}%")
    
    if resources['analysis']['bottlenecks']:
        print(f"\nIdentified Bottlenecks:")
        for bottleneck in resources['analysis']['bottlenecks']:
            print(f"  - {bottleneck}")
            
    print(f"\nBenchmark results saved to: {benchmarks.output_dir}")


if __name__ == '__main__':
    run_all_benchmarks()