# API Reference

## Table of Contents
1. [Models](#models)
2. [Parsers](#parsers)
3. [Analyzers](#analyzers)
4. [Orchestrator](#orchestrator)
5. [Monitoring](#monitoring)
6. [CLI Commands](#cli-commands)

## Models

### Phase
`models.parallel_execution.Phase`

Represents a single phase in the PRD.

```python
@dataclass
class Phase:
    phase_id: str              # Unique identifier (e.g., "phase-1")
    name: str                  # Phase name from PRD
    description: str           # Full phase description
    dependencies: List[str]    # List of phase IDs this depends on
    estimated_hours: float     # Time estimate in hours
    modifies_files: List[str]  # Files this phase will modify
```

**Methods:**
- `to_dict() -> Dict`: Convert to dictionary representation
- `from_dict(data: Dict) -> Phase`: Create from dictionary

### Wave
`models.parallel_execution.Wave`

Group of phases that can execute concurrently.

```python
@dataclass
class Wave:
    wave_id: str              # Unique wave identifier
    name: str                 # Descriptive name
    phase_ids: List[str]      # Phases in this wave
    estimated_duration: float # Max duration of phases
```

### ParallelExecution
`models.parallel_execution.ParallelExecution`

Complete execution plan with waves and phases.

```python
@dataclass
class ParallelExecution:
    execution_id: str                    # Unique execution ID
    feature_name: str                    # Feature being implemented
    status: ExecutionStatus              # Current status
    phases: Dict[str, PhaseState]        # All phases
    waves: List[Wave]                    # Execution waves
    created_at: datetime                 # Creation timestamp
    started_at: Optional[datetime]       # Start time
    completed_at: Optional[datetime]     # Completion time
```

### ExecutionState
`models.execution_state.ExecutionState`

Current state of parallel execution.

```python
@dataclass
class ExecutionState:
    execution: ParallelExecution      # Execution plan
    agents: Dict[str, AgentState]     # Active agents
    resource_locks: Dict[str, str]    # Resource -> phase_id
    checkpoint_time: datetime         # Last checkpoint
```

## Parsers

### PRDParser
`parsers.phase_parser.PRDParser`

Parses markdown PRD files into phases.

```python
class PRDParser:
    def parse_file(self, file_path: str) -> List[Phase]:
        """Parse PRD file into phases.
        
        Args:
            file_path: Path to markdown PRD file
            
        Returns:
            List of Phase objects
            
        Raises:
            ValueError: If file format is invalid
        """
    
    def parse_content(self, content: str) -> List[Phase]:
        """Parse PRD content string.
        
        Args:
            content: Markdown content
            
        Returns:
            List of Phase objects
        """
```

**Usage Example:**
```python
parser = PRDParser()
phases = parser.parse_file("feature-prd.md")

for phase in phases:
    print(f"{phase.phase_id}: {phase.name}")
    print(f"  Dependencies: {phase.dependencies}")
    print(f"  Estimated: {phase.estimated_hours}h")
```

## Analyzers

### DependencyAnalyzer
`analyzers.dependency_analyzer.DependencyAnalyzer`

Analyzes phase dependencies and detects conflicts.

```python
class DependencyAnalyzer:
    def build_dependency_graph(self, phases: List[Phase]) -> nx.DiGraph:
        """Build directed graph of dependencies.
        
        Args:
            phases: List of phases
            
        Returns:
            NetworkX directed graph
        """
    
    def validate_dependencies(self, phases: List[Phase]) -> List[str]:
        """Validate dependency structure.
        
        Returns:
            List of validation errors (empty if valid)
        """
    
    def detect_resource_conflicts(self, 
                                phases: List[Phase]) -> Dict[str, List[str]]:
        """Detect file modification conflicts.
        
        Returns:
            Dict mapping file -> list of phase IDs
        """
    
    def find_circular_dependencies(self, 
                                 graph: nx.DiGraph) -> List[List[str]]:
        """Find circular dependency chains.
        
        Returns:
            List of circular dependency paths
        """
```

### WaveCalculator
`analyzers.wave_calculator.WaveCalculator`

Calculates optimal execution waves.

```python
class WaveCalculator:
    def calculate_waves(self, 
                       phases: List[Phase],
                       dependency_graph: nx.DiGraph,
                       resource_conflicts: Dict[str, List[str]] = None,
                       max_concurrent: int = None) -> List[Wave]:
        """Calculate execution waves.
        
        Args:
            phases: List of phases
            dependency_graph: Dependency graph
            resource_conflicts: Resource conflict map
            max_concurrent: Max phases per wave
            
        Returns:
            List of Wave objects
        """
    
    def optimize_waves(self, waves: List[Wave]) -> List[Wave]:
        """Optimize wave distribution.
        
        Returns:
            Optimized wave list
        """
```

### ConflictDetector
`analyzers.conflict_detector.ConflictDetector`

Advanced conflict detection and resolution.

```python
class ConflictDetector:
    def detect_all_conflicts(self, 
                           phases: List[Phase]) -> ConflictReport:
        """Comprehensive conflict detection.
        
        Returns:
            ConflictReport with all conflicts
        """
    
    def suggest_resolutions(self, 
                          conflicts: ConflictReport) -> List[Resolution]:
        """Suggest conflict resolutions.
        
        Returns:
            List of suggested resolutions
        """
```

## Orchestrator

### ParallelOrchestrator
`orchestrator.parallel_orchestrator.ParallelOrchestrator`

Main orchestration engine for parallel execution.

```python
class ParallelOrchestrator:
    def __init__(self, 
                 state_manager: StateManager,
                 config: ParallelExecutionConfig):
        """Initialize orchestrator.
        
        Args:
            state_manager: State persistence manager
            config: Execution configuration
        """
    
    def execute_parallel(self,
                        phases: List[Phase],
                        waves: List[Wave],
                        feature_name: str) -> str:
        """Execute phases in parallel.
        
        Args:
            phases: All phases to execute
            waves: Execution waves
            feature_name: Feature being implemented
            
        Returns:
            Execution ID
            
        Raises:
            ExecutionError: If execution fails
        """
    
    def abort_execution(self) -> None:
        """Abort current execution gracefully."""
    
    def get_status(self) -> ExecutionStatus:
        """Get current execution status."""
    
    def wait_for_completion(self, timeout: float = None) -> bool:
        """Wait for execution to complete.
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            True if completed, False if timeout
        """
```

### StateManager
`orchestrator.state_manager.StateManager`

Manages execution state and checkpoints.

```python
class StateManager:
    def __init__(self, checkpoint_dir: Path):
        """Initialize state manager.
        
        Args:
            checkpoint_dir: Directory for checkpoints
        """
    
    def initialize_execution(self, 
                           execution: ParallelExecution) -> ExecutionState:
        """Initialize new execution state."""
    
    def save_checkpoint(self, state: ExecutionState) -> Path:
        """Save state checkpoint.
        
        Returns:
            Path to checkpoint file
        """
    
    def load_latest_state(self) -> Optional[ExecutionState]:
        """Load most recent checkpoint."""
    
    def update_phase_status(self,
                          phase_id: str,
                          status: str,
                          error: str = None) -> None:
        """Update phase execution status."""
```

### AgentSpawner
`orchestrator.agent_spawner.AgentSpawner`

Manages agent lifecycle.

```python
class AgentSpawner:
    def spawn_agent(self,
                   agent_id: str,
                   phase: Phase,
                   workspace: Path) -> AgentProcess:
        """Spawn new agent process.
        
        Args:
            agent_id: Unique agent identifier
            phase: Phase to execute
            workspace: Agent workspace directory
            
        Returns:
            AgentProcess handle
        """
    
    def monitor_agent(self, 
                     agent: AgentProcess) -> AgentStatus:
        """Monitor agent status."""
    
    def terminate_agent(self, agent: AgentProcess) -> None:
        """Terminate agent gracefully."""
```

## Monitoring

### ProgressDashboard
`monitoring.dashboard.ProgressDashboard`

Real-time progress visualization.

```python
class ProgressDashboard:
    def display_execution_overview(self, 
                                 execution: ParallelExecution) -> Panel:
        """Display execution overview panel."""
    
    def render_wave_progress(self, 
                           wave: Wave,
                           wave_number: int,
                           total_waves: int) -> Panel:
        """Render wave progress panel."""
    
    def show_agent_status(self, 
                         agents: List[AgentState]) -> Table:
        """Display agent status table."""
    
    def update_dashboard(self, state: ExecutionState) -> Layout:
        """Update complete dashboard."""
```

### ParallelExecutionUI
`monitoring.terminal_ui.ParallelExecutionUI`

Interactive terminal UI.

```python
class ParallelExecutionUI:
    def start_monitoring(self) -> None:
        """Start monitoring UI."""
    
    def stop_monitoring(self) -> None:
        """Stop monitoring UI."""
    
    def update_agent_panel(self, agents: List[Dict]) -> Panel:
        """Update agent status panel."""
    
    def display_error(self, error: str) -> None:
        """Display error message."""
    
    def show_completion_summary(self) -> None:
        """Show final execution summary."""
```

### MetricsCollector
`monitoring.metrics_collector.MetricsCollector`

Collects and analyzes execution metrics.

```python
class MetricsCollector:
    def start_collection(self, execution_id: str) -> None:
        """Start metrics collection."""
    
    def collect_phase_metrics(self,
                            phase: PhaseState,
                            wave_number: int,
                            agent_id: str,
                            metrics: Dict) -> None:
        """Collect phase execution metrics."""
    
    def calculate_execution_metrics(self,
                                  execution: ParallelExecution,
                                  state: ExecutionState) -> ExecutionMetrics:
        """Calculate comprehensive metrics."""
    
    def export_metrics_csv(self, 
                         metrics: ExecutionMetrics) -> Path:
        """Export metrics to CSV."""
    
    def export_metrics_json(self,
                          metrics: ExecutionMetrics) -> Path:
        """Export metrics to JSON."""
    
    def generate_report(self, 
                       metrics: ExecutionMetrics) -> str:
        """Generate human-readable report."""
```

## CLI Commands

### prd_analyze_cli
`cli.prd_analyze_cli`

Command-line interface for PRD analysis.

```python
def main(args: List[str] = None) -> int:
    """Main entry point for prd-analyze command.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success)
    """
```

**Arguments:**
- `prd_file`: Path to PRD markdown file
- `--output, -o`: Output directory
- `--visualize, -v`: Generate visualization
- `--format, -f`: Output format (json/yaml/text)
- `--max-agents, -m`: Maximum concurrent agents

### prd_parallel_cli
`cli.prd_parallel_cli`

Command-line interface for parallel execution.

```python
def main(args: List[str] = None) -> int:
    """Main entry point for prd-parallel command.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success)
    """
```

**Commands:**
- `execute <prd_file>`: Execute PRD in parallel
- `status`: Show current execution status
- `abort`: Abort running execution
- `resume`: Resume from checkpoint

**Arguments:**
- `--max-agents, -m`: Maximum concurrent agents
- `--monitor`: Enable monitoring UI
- `--checkpoint-dir`: Checkpoint directory
- `--dry-run`: Show plan without executing

## Error Handling

### Common Exceptions

```python
class ExecutionError(Exception):
    """Base exception for execution errors."""

class DependencyError(ExecutionError):
    """Raised when dependency validation fails."""

class ResourceConflictError(ExecutionError):
    """Raised when resource conflicts cannot be resolved."""

class AgentError(ExecutionError):
    """Raised when agent execution fails."""

class CheckpointError(ExecutionError):
    """Raised when checkpoint operations fail."""
```

### Error Handling Pattern

```python
try:
    orchestrator.execute_parallel(phases, waves, "feature")
except DependencyError as e:
    print(f"Dependency error: {e}")
    # Handle invalid dependencies
except ResourceConflictError as e:
    print(f"Resource conflict: {e}")
    # Handle resource conflicts
except AgentError as e:
    print(f"Agent failure: {e}")
    # Handle agent failures
except ExecutionError as e:
    print(f"Execution failed: {e}")
    # Handle general execution errors
```

## Configuration

### ParallelExecutionConfig
`config.parallel_config.ParallelExecutionConfig`

```python
@dataclass
class ParallelExecutionConfig:
    max_concurrent_agents: int = 4
    agent_timeout_hours: float = 4.0
    checkpoint_interval_minutes: int = 15
    enable_monitoring: bool = True
    resource_lock_timeout: int = 300
    retry_failed_phases: bool = True
    max_retries: int = 2
    
    @classmethod
    def from_env(cls) -> 'ParallelExecutionConfig':
        """Create config from environment variables."""
    
    @classmethod
    def from_file(cls, path: Path) -> 'ParallelExecutionConfig':
        """Load config from file."""
```