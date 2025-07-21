# Phase 2: Dependency Analysis Engine

## Overview
Build the intelligent dependency analyzer that parses PRD phase files, extracts dependencies, and calculates optimal execution waves for parallel processing.

## Estimated Time: 1.5 hours

## Dependencies: Phase 1 (models and data structures)

## Objectives
1. Parse phase files to extract dependencies
2. Build dependency graph from phase relationships
3. Calculate execution waves using topological sorting
4. Detect potential resource conflicts

## Detailed Tasks

### 1. Phase File Parser (`parsers/phase_parser.py`)
```python
# Parse phase markdown files to extract:
- Phase metadata (name, dependencies, outputs)
- File paths mentioned in phase content
- Expected outputs and artifacts
- Time estimates

# Key functions:
- parse_phase_file(filepath) -> PhaseInfo
- extract_dependencies(content) -> List[str]
- extract_file_references(content) -> List[str]
```

### 2. Dependency Graph Builder (`analyzers/dependency_analyzer.py`)
```python
# Build complete dependency graph:
- load_all_phases(workspace_dir) -> List[PhaseInfo]
- build_dependency_graph(phases) -> DependencyGraph
- validate_dependencies(graph) -> List[ValidationError]
- detect_circular_dependencies(graph) -> bool

# Use Phase 1's DependencyGraph model
```

### 3. Wave Calculator (`analyzers/wave_calculator.py`)
```python
# Calculate optimal execution waves:
- calculate_execution_waves(graph) -> List[ExecutionWave]
- optimize_wave_distribution(waves, max_agents) -> List[ExecutionWave]
- estimate_total_time(waves) -> float
- identify_critical_path(graph) -> List[PhaseInfo]

# Implement Kahn's algorithm for topological sorting
```

### 4. Conflict Detection (`analyzers/conflict_detector.py`)
```python
# Detect potential resource conflicts:
- analyze_file_conflicts(phases) -> List[ConflictInfo]
- suggest_lock_requirements(conflicts) -> List[ResourceLock]
- validate_parallel_safety(wave) -> bool
- generate_conflict_report(conflicts) -> str
```

## Expected Outputs

### Files to Create:
1. `/parsers/phase_parser.py` - Phase file parsing logic
2. `/analyzers/dependency_analyzer.py` - Dependency graph construction
3. `/analyzers/wave_calculator.py` - Wave calculation algorithms
4. `/analyzers/conflict_detector.py` - Resource conflict detection
5. `/tests/test_analyzers.py` - Comprehensive test suite

### Key Functions:
- `parse_phase_file()` - Extract phase metadata
- `build_dependency_graph()` - Construct dependency graph
- `calculate_execution_waves()` - Determine parallel waves
- `analyze_file_conflicts()` - Detect resource conflicts

## Integration Points
- Uses models from Phase 1: `PhaseInfo`, `DependencyGraph`, `ExecutionWave`
- Provides dependency data for Phase 3's orchestrator
- Identifies locking requirements for resource manager

## Success Criteria
- [ ] Correctly parses all phase file formats
- [ ] Builds accurate dependency graphs
- [ ] Calculates optimal execution waves
- [ ] Detects all potential file conflicts
- [ ] Handles circular dependencies gracefully
- [ ] 95%+ test coverage

## Example Usage
```python
# Parse workspace phases
phases = load_all_phases("/path/to/workspace")

# Build dependency graph
graph = build_dependency_graph(phases)

# Calculate waves
waves = calculate_execution_waves(graph)

# Check for conflicts
conflicts = analyze_file_conflicts(phases)
```

## Notes for Next Phase
Phase 3 will use the dependency analysis to orchestrate actual parallel execution. Ensure wave calculation considers resource constraints and provides clear execution order.