"""
Wave calculation algorithms for parallel PRD execution.

This module implements algorithms to calculate optimal execution waves
using topological sorting and load balancing strategies.
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import deque, defaultdict
from dataclasses import dataclass

from models.parallel_execution import PhaseInfo, DependencyGraph, ExecutionWave


@dataclass
class WaveMetrics:
    """Metrics for wave calculation."""
    total_waves: int
    max_parallelism: int
    total_time: float
    critical_path_length: int
    utilization_score: float  # 0-1, higher is better


class WaveCalculator:
    """Calculates optimal execution waves for parallel processing."""
    
    def calculate_execution_waves(self, graph: DependencyGraph) -> List[ExecutionWave]:
        """
        Calculate execution waves using Kahn's algorithm.
        
        This implements a topological sort that groups phases into waves
        where all phases in a wave can execute in parallel.
        
        Args:
            graph: The dependency graph
            
        Returns:
            List of ExecutionWave objects representing parallel execution groups
            
        Raises:
            ValueError: If the graph contains cycles
        """
        # Create a copy of the graph structure to avoid modifying original
        in_degree = self._calculate_in_degrees(graph)
        
        # Find all nodes with no incoming edges (can start immediately)
        queue = deque([
            phase_id for phase_id, degree in in_degree.items()
            if degree == 0
        ])
        
        waves = []
        wave_number = 0
        processed = set()
        
        while queue:
            # All nodes in current queue can execute in parallel
            current_wave = ExecutionWave(wave_number=wave_number)
            current_batch = list(queue)
            queue.clear()
            
            for phase_id in current_batch:
                current_wave.add_phase(phase_id)
                processed.add(phase_id)
                
                # Reduce in-degree for all dependents
                dependents = graph.get_dependents(phase_id)
                for dependent_id in dependents:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)
            
            if current_wave.phases:
                waves.append(current_wave)
                wave_number += 1
        
        # Check if all nodes were processed (no cycles)
        if len(processed) != len(graph.nodes):
            unprocessed = set(graph.nodes.keys()) - processed
            raise ValueError(
                f"Circular dependency detected. Unable to process phases: {unprocessed}"
            )
        
        return waves
    
    def optimize_wave_distribution(self, waves: List[ExecutionWave], 
                                   max_agents: int) -> List[ExecutionWave]:
        """
        Optimize wave distribution considering agent limits.
        
        If a wave has more phases than available agents, split it into
        multiple waves to improve load balancing.
        
        Args:
            waves: Initial waves from topological sort
            max_agents: Maximum number of parallel agents
            
        Returns:
            Optimized list of execution waves
        """
        if max_agents <= 0:
            return waves
        
        optimized_waves = []
        
        for wave in waves:
            if len(wave.phases) <= max_agents:
                # Wave fits within agent limit
                optimized_waves.append(wave)
            else:
                # Split wave into sub-waves
                sub_waves = self._split_wave(wave, max_agents)
                optimized_waves.extend(sub_waves)
        
        # Re-number waves
        for i, wave in enumerate(optimized_waves):
            wave.wave_number = i
        
        return optimized_waves
    
    def estimate_total_time(self, waves: List[ExecutionWave], 
                            graph: DependencyGraph) -> float:
        """
        Estimate total execution time for all waves.
        
        Assumes perfect parallelization within waves and sequential
        execution between waves.
        
        Args:
            waves: List of execution waves
            graph: Dependency graph with phase information
            
        Returns:
            Estimated total time in hours
        """
        total_time = 0.0
        
        for wave in waves:
            # Wave time is the maximum time of any phase in the wave
            wave_time = 0.0
            for phase_id in wave.phases:
                phase = graph.get_phase(phase_id)
                if phase:
                    wave_time = max(wave_time, phase.estimated_time)
            total_time += wave_time
        
        return total_time
    
    def identify_critical_path(self, graph: DependencyGraph) -> List[PhaseInfo]:
        """
        Identify the critical path through the dependency graph.
        
        The critical path is the longest path from any root to any leaf,
        where length is measured by cumulative estimated time.
        
        Args:
            graph: The dependency graph
            
        Returns:
            List of PhaseInfo objects representing the critical path
        """
        # Calculate longest path to each node
        longest_paths: Dict[str, Tuple[float, List[str]]] = {}
        
        # Process in topological order
        topo_order = self._topological_sort(graph)
        
        for phase_id in topo_order:
            phase = graph.get_phase(phase_id)
            if not phase:
                continue
            
            # Find longest path to this node
            max_time = 0.0
            best_path = []
            
            for dep_id in phase.dependencies:
                if dep_id in longest_paths:
                    dep_time, dep_path = longest_paths[dep_id]
                    if dep_time > max_time:
                        max_time = dep_time
                        best_path = dep_path.copy()
            
            # Add this node to the path
            best_path.append(phase_id)
            total_time = max_time + phase.estimated_time
            longest_paths[phase_id] = (total_time, best_path)
        
        # Find the overall longest path
        if not longest_paths:
            return []
        
        max_time = 0.0
        critical_path_ids = []
        
        for phase_id, (time, path) in longest_paths.items():
            if time > max_time:
                max_time = time
                critical_path_ids = path
        
        # Convert to PhaseInfo objects
        critical_path = []
        for phase_id in critical_path_ids:
            phase = graph.get_phase(phase_id)
            if phase:
                critical_path.append(phase)
        
        return critical_path
    
    def calculate_metrics(self, waves: List[ExecutionWave], 
                          graph: DependencyGraph) -> WaveMetrics:
        """
        Calculate detailed metrics about the wave execution plan.
        
        Args:
            waves: List of execution waves
            graph: Dependency graph
            
        Returns:
            WaveMetrics object with execution statistics
        """
        if not waves:
            return WaveMetrics(
                total_waves=0,
                max_parallelism=0,
                total_time=0.0,
                critical_path_length=0,
                utilization_score=0.0
            )
        
        # Calculate basic metrics
        total_waves = len(waves)
        max_parallelism = max(len(wave.phases) for wave in waves)
        total_time = self.estimate_total_time(waves, graph)
        
        # Calculate critical path
        critical_path = self.identify_critical_path(graph)
        critical_path_length = len(critical_path)
        
        # Calculate utilization score
        total_phase_time = sum(
            phase.estimated_time for phase in graph.nodes.values()
        )
        theoretical_min_time = total_phase_time / max_parallelism if max_parallelism > 0 else 0
        utilization_score = theoretical_min_time / total_time if total_time > 0 else 0
        utilization_score = min(1.0, utilization_score)  # Cap at 1.0
        
        return WaveMetrics(
            total_waves=total_waves,
            max_parallelism=max_parallelism,
            total_time=total_time,
            critical_path_length=critical_path_length,
            utilization_score=utilization_score
        )
    
    def _calculate_in_degrees(self, graph: DependencyGraph) -> Dict[str, int]:
        """Calculate in-degree (number of dependencies) for each node."""
        in_degree = defaultdict(int)
        
        # Initialize all nodes with 0
        for phase_id in graph.nodes:
            in_degree[phase_id] = 0
        
        # Count dependencies
        for phase_id, phase in graph.nodes.items():
            in_degree[phase_id] = len(phase.dependencies)
        
        return in_degree
    
    def _split_wave(self, wave: ExecutionWave, max_size: int) -> List[ExecutionWave]:
        """Split a wave into smaller waves based on max size."""
        sub_waves = []
        
        # Sort phases by estimated time (longest first) for better load balancing
        phase_times = []
        for phase_id in wave.phases:
            phase = self._get_phase_from_cache(phase_id)
            time = phase.estimated_time if phase else 1.0
            phase_times.append((phase_id, time))
        
        phase_times.sort(key=lambda x: x[1], reverse=True)
        
        # Create sub-waves
        current_sub_wave = ExecutionWave(wave_number=wave.wave_number)
        
        for phase_id, _ in phase_times:
            if len(current_sub_wave.phases) >= max_size:
                sub_waves.append(current_sub_wave)
                current_sub_wave = ExecutionWave(wave_number=wave.wave_number)
            current_sub_wave.add_phase(phase_id)
        
        if current_sub_wave.phases:
            sub_waves.append(current_sub_wave)
        
        return sub_waves
    
    def _topological_sort(self, graph: DependencyGraph) -> List[str]:
        """Perform a topological sort of the graph."""
        in_degree = self._calculate_in_degrees(graph)
        queue = deque([
            phase_id for phase_id, degree in in_degree.items()
            if degree == 0
        ])
        
        result = []
        
        while queue:
            phase_id = queue.popleft()
            result.append(phase_id)
            
            # Reduce in-degree for dependents
            dependents = graph.get_dependents(phase_id)
            for dependent_id in dependents:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        return result
    
    # Cache for phase lookups
    _phase_cache: Dict[str, PhaseInfo] = {}
    
    def _get_phase_from_cache(self, phase_id: str) -> Optional[PhaseInfo]:
        """Get phase from cache (set by dependency analyzer)."""
        return self._phase_cache.get(phase_id)