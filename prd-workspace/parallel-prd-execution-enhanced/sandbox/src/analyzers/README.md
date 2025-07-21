# Dependency Analysis Engine

This module contains the dependency analysis components for the parallel PRD execution system. These components work together to analyze phase dependencies, calculate optimal execution waves, and detect potential conflicts.

## Components

### 1. Phase Parser (`parsers/phase_parser.py`)
Parses PRD phase markdown files to extract:
- Phase metadata (ID, name, description)
- Dependencies on other phases
- Expected output files
- Estimated execution time
- File references within the phase

**Key Features:**
- Robust regex-based parsing
- Caching for performance
- Handles various markdown formats
- Extracts file paths from code blocks and text

### 2. Dependency Analyzer (`dependency_analyzer.py`)
Builds and validates dependency graphs from phase information:
- Constructs complete dependency graphs
- Detects circular dependencies
- Validates phase references
- Identifies unreachable phases
- Calculates dependency depth

**Key Features:**
- Uses DFS for cycle detection
- Provides detailed validation errors
- Finds close matches for typos
- Identifies critical dependency chains

### 3. Wave Calculator (`wave_calculator.py`)
Calculates optimal execution waves using topological sorting:
- Implements Kahn's algorithm
- Groups phases into parallel execution waves
- Optimizes for agent limits
- Identifies critical paths
- Calculates execution metrics

**Key Features:**
- Maximizes parallelization
- Handles agent constraints
- Provides utilization metrics
- Critical path analysis

### 4. Conflict Detector (`conflict_detector.py`)
Analyzes phases to detect potential resource conflicts:
- Identifies file access patterns
- Detects write-write conflicts
- Suggests locking strategies
- Validates parallel safety

**Key Features:**
- Pattern-based conflict detection
- Severity classification
- Lock requirement suggestions
- Detailed conflict reports

## Usage Example

```python
from parsers.phase_parser import PhaseParser
from analyzers.dependency_analyzer import DependencyAnalyzer
from analyzers.wave_calculator import WaveCalculator
from analyzers.conflict_detector import ConflictDetector

# Initialize components
parser = PhaseParser()
analyzer = DependencyAnalyzer(parser)
calculator = WaveCalculator()
detector = ConflictDetector()

# Load and analyze phases
phases = analyzer.load_all_phases("/path/to/workspace")
graph = analyzer.build_dependency_graph(phases)

# Validate dependencies
errors = analyzer.validate_dependencies(graph)
if errors:
    for error in errors:
        print(f"{error.error_type}: {error.message}")

# Calculate execution waves
waves = calculator.calculate_execution_waves(graph)
metrics = calculator.calculate_metrics(waves, graph)

# Detect conflicts
conflicts = detector.analyze_file_conflicts(phases)
if conflicts:
    report = detector.generate_conflict_report(conflicts)
    print(report)
```

## Integration with Phase 3

The dependency analysis engine provides the following interfaces for the orchestrator (Phase 3):

1. **Execution Waves**: Pre-calculated waves that can be executed in order
2. **Conflict Information**: Resource conflicts that need locking
3. **Critical Path**: For prioritizing phase execution
4. **Validation Results**: Ensure safe execution before starting

## Testing

Run the comprehensive test suite:

```bash
python3 -m unittest tests.test_analyzers -v
```

The test suite includes:
- Unit tests for each component
- Integration tests for the full pipeline
- Edge case handling
- Performance validation