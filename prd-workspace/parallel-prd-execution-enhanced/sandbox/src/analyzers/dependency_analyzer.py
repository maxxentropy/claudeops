"""
Dependency graph builder for parallel PRD execution.

This module builds and validates dependency graphs from phase information,
detecting circular dependencies and ensuring graph integrity.
"""

import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from collections import deque
from dataclasses import dataclass

from models.parallel_execution import PhaseInfo, DependencyGraph
from parsers.phase_parser import PhaseParser


@dataclass
class ValidationError:
    """Represents a validation error in the dependency graph."""
    error_type: str
    message: str
    affected_phases: List[str]
    severity: str = "error"  # error, warning, info


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected."""
    pass


class DependencyAnalyzer:
    """Analyzes and builds dependency graphs from phase files."""
    
    def __init__(self, parser: Optional[PhaseParser] = None):
        """
        Initialize the dependency analyzer.
        
        Args:
            parser: Optional phase parser instance to use
        """
        self.parser = parser or PhaseParser()
        self._phase_cache: Dict[str, PhaseInfo] = {}
    
    def load_all_phases(self, workspace_dir: str) -> List[PhaseInfo]:
        """
        Load all phase files from a workspace directory.
        
        Args:
            workspace_dir: Root directory containing phase files
            
        Returns:
            List of PhaseInfo objects for all discovered phases
            
        Raises:
            ValueError: If workspace directory is invalid
        """
        workspace_path = Path(workspace_dir).resolve()
        if not workspace_path.exists():
            raise ValueError(f"Workspace directory does not exist: {workspace_dir}")
        
        phases = []
        
        # Search for phase files in common locations
        search_patterns = [
            "phase-*.md",
            "phases/phase-*.md", 
            "artifacts/phase-*/phase-*.md",
            "**/phase-*.md"
        ]
        
        phase_files = set()
        for pattern in search_patterns:
            phase_files.update(workspace_path.glob(pattern))
        
        # Also search for numbered phase files
        for i in range(1, 10):  # Assume max 9 phases
            patterns = [
                f"phase-{i}.md",
                f"phase{i}.md",
                f"artifacts/phase-{i}/*.md"
            ]
            for pattern in patterns:
                phase_files.update(workspace_path.glob(pattern))
        
        # Parse each phase file
        for phase_file in sorted(phase_files):
            try:
                phase_info = self.parser.parse_phase_file(str(phase_file))
                phases.append(phase_info)
                self._phase_cache[phase_info.id] = phase_info
            except Exception as e:
                print(f"Warning: Failed to parse {phase_file}: {e}")
        
        return phases
    
    def build_dependency_graph(self, phases: List[PhaseInfo]) -> DependencyGraph:
        """
        Build a complete dependency graph from phase information.
        
        Args:
            phases: List of PhaseInfo objects
            
        Returns:
            DependencyGraph representing all phase dependencies
            
        Raises:
            ValueError: If dependencies reference non-existent phases
        """
        graph = DependencyGraph()
        
        # First pass: add all phases as nodes
        phase_ids = set()
        for phase in phases:
            graph.add_phase(phase)
            phase_ids.add(phase.id)
            self._phase_cache[phase.id] = phase
        
        # Validate all dependencies exist
        for phase in phases:
            for dep_id in phase.dependencies:
                if dep_id not in phase_ids:
                    # Try to find a close match
                    close_match = self._find_close_match(dep_id, phase_ids)
                    if close_match:
                        raise ValueError(
                            f"Phase '{phase.id}' depends on non-existent phase '{dep_id}'. "
                            f"Did you mean '{close_match}'?"
                        )
                    else:
                        raise ValueError(
                            f"Phase '{phase.id}' depends on non-existent phase '{dep_id}'"
                        )
        
        return graph
    
    def validate_dependencies(self, graph: DependencyGraph) -> List[ValidationError]:
        """
        Validate the dependency graph for issues.
        
        Checks for:
        - Circular dependencies
        - Unreachable phases
        - Missing dependencies
        - Phases with no outputs
        - Long dependency chains
        
        Args:
            graph: The dependency graph to validate
            
        Returns:
            List of validation errors found
        """
        errors = []
        
        # Check for circular dependencies
        try:
            if self.detect_circular_dependencies(graph):
                cycles = self._find_all_cycles(graph)
                for cycle in cycles:
                    errors.append(ValidationError(
                        error_type="circular_dependency",
                        message=f"Circular dependency detected: {' -> '.join(cycle)}",
                        affected_phases=cycle,
                        severity="error"
                    ))
        except CircularDependencyError as e:
            errors.append(ValidationError(
                error_type="circular_dependency",
                message=str(e),
                affected_phases=[],
                severity="error"
            ))
        
        # Check for unreachable phases
        reachable = self._find_reachable_phases(graph)
        all_phases = set(graph.nodes.keys())
        unreachable = all_phases - reachable
        
        if unreachable:
            errors.append(ValidationError(
                error_type="unreachable_phases",
                message=f"Phases cannot be reached from root: {', '.join(sorted(unreachable))}",
                affected_phases=list(unreachable),
                severity="warning"
            ))
        
        # Check for phases with no outputs
        for phase_id, phase in graph.nodes.items():
            if not phase.outputs:
                errors.append(ValidationError(
                    error_type="no_outputs",
                    message=f"Phase '{phase_id}' has no defined outputs",
                    affected_phases=[phase_id],
                    severity="warning"
                ))
        
        # Check for very long dependency chains
        max_depth = self._calculate_max_depth(graph)
        if max_depth > 5:
            errors.append(ValidationError(
                error_type="deep_dependency_chain",
                message=f"Dependency chain depth of {max_depth} may impact parallelization",
                affected_phases=[],
                severity="info"
            ))
        
        # Check for phases that depend on themselves
        for phase_id, phase in graph.nodes.items():
            if phase_id in phase.dependencies:
                errors.append(ValidationError(
                    error_type="self_dependency",
                    message=f"Phase '{phase_id}' depends on itself",
                    affected_phases=[phase_id],
                    severity="error"
                ))
        
        return errors
    
    def detect_circular_dependencies(self, graph: DependencyGraph) -> bool:
        """
        Detect if the graph contains circular dependencies.
        
        Args:
            graph: The dependency graph to check
            
        Returns:
            True if circular dependencies exist, False otherwise
        """
        # Use DFS with recursion stack to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(phase_id: str) -> bool:
            visited.add(phase_id)
            rec_stack.add(phase_id)
            
            # Check all dependencies
            phase = graph.nodes.get(phase_id)
            if phase:
                for dep_id in phase.dependencies:
                    if dep_id not in visited:
                        if has_cycle(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True
            
            rec_stack.remove(phase_id)
            return False
        
        # Check each unvisited phase
        for phase_id in graph.nodes:
            if phase_id not in visited:
                if has_cycle(phase_id):
                    return True
        
        return False
    
    def _find_all_cycles(self, graph: DependencyGraph) -> List[List[str]]:
        """Find all circular dependency cycles in the graph."""
        cycles = []
        visited = set()
        rec_stack = []
        
        def find_cycles_from(phase_id: str, path: List[str]):
            if phase_id in rec_stack:
                # Found a cycle
                cycle_start = rec_stack.index(phase_id)
                cycle = rec_stack[cycle_start:] + [phase_id]
                cycles.append(cycle)
                return
            
            if phase_id in visited:
                return
            
            visited.add(phase_id)
            rec_stack.append(phase_id)
            
            phase = graph.nodes.get(phase_id)
            if phase:
                for dep_id in phase.dependencies:
                    find_cycles_from(dep_id, path + [phase_id])
            
            rec_stack.pop()
        
        for phase_id in graph.nodes:
            if phase_id not in visited:
                find_cycles_from(phase_id, [])
        
        # Remove duplicate cycles
        unique_cycles = []
        for cycle in cycles:
            # Normalize cycle (start from smallest element)
            min_idx = cycle.index(min(cycle))
            normalized = cycle[min_idx:] + cycle[:min_idx]
            if normalized not in unique_cycles:
                unique_cycles.append(normalized)
        
        return unique_cycles
    
    def _find_reachable_phases(self, graph: DependencyGraph) -> Set[str]:
        """Find all phases reachable from root phases."""
        reachable = set()
        
        # Start from root phases
        roots = graph.get_root_phases()
        queue = deque([phase.id for phase in roots])
        
        while queue:
            phase_id = queue.popleft()
            if phase_id in reachable:
                continue
            
            reachable.add(phase_id)
            
            # Add all phases that depend on this one
            dependents = graph.get_dependents(phase_id)
            queue.extend(dependents)
        
        return reachable
    
    def _calculate_max_depth(self, graph: DependencyGraph) -> int:
        """Calculate maximum dependency chain depth."""
        depths = {}
        
        def calculate_depth(phase_id: str) -> int:
            if phase_id in depths:
                return depths[phase_id]
            
            phase = graph.nodes.get(phase_id)
            if not phase or not phase.dependencies:
                depths[phase_id] = 0
                return 0
            
            max_dep_depth = 0
            for dep_id in phase.dependencies:
                dep_depth = calculate_depth(dep_id)
                max_dep_depth = max(max_dep_depth, dep_depth)
            
            depths[phase_id] = max_dep_depth + 1
            return depths[phase_id]
        
        max_depth = 0
        for phase_id in graph.nodes:
            depth = calculate_depth(phase_id)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _find_close_match(self, target: str, candidates: Set[str]) -> Optional[str]:
        """Find a close match for a phase ID."""
        target_lower = target.lower()
        
        # Exact match (case insensitive)
        for candidate in candidates:
            if candidate.lower() == target_lower:
                return candidate
        
        # Partial match
        for candidate in candidates:
            if target_lower in candidate.lower() or candidate.lower() in target_lower:
                return candidate
        
        # Number match (e.g., "1" matches "phase-1")
        if target.isdigit():
            phase_id = f"phase-{target}"
            if phase_id in candidates:
                return phase_id
        
        return None
    
    def get_phase_info(self, phase_id: str) -> Optional[PhaseInfo]:
        """Get cached phase information."""
        return self._phase_cache.get(phase_id)