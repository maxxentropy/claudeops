# Parallel PRD Execution Guide

## Overview

The Parallel PRD Execution System transforms sequential Product Requirements Documents (PRDs) into optimized parallel execution plans, reducing implementation time by 40-60% through intelligent dependency analysis and concurrent phase execution.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Command Reference](#command-reference)
4. [Configuration](#configuration)
5. [Monitoring & Metrics](#monitoring--metrics)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd parallel-prd-execution

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
python -m pytest tests/
```

### Quick Start

1. **Analyze a PRD for parallel execution:**
```bash
/prd-analyze feature-prd.md --visualize
```

2. **Execute a PRD in parallel:**
```bash
/prd-parallel feature-prd.md --max-agents 4 --monitor
```

3. **Monitor execution progress:**
```bash
/prd-parallel status
```

## Core Concepts

### Phases
A phase represents a discrete unit of work in the PRD with:
- Unique identifier
- Dependencies on other phases
- Estimated duration
- Resource requirements (files to modify)

### Waves
Waves are groups of phases that can execute concurrently:
- All phases in a wave have no interdependencies
- Wave duration equals the longest phase in the wave
- Waves execute sequentially

### Dependency Analysis
The system automatically:
- Parses phase dependencies from PRD markdown
- Detects resource conflicts (file modifications)
- Builds an optimal execution graph
- Identifies parallelization opportunities

### Agent Management
Agents are parallel execution units that:
- Execute individual phases
- Manage resource locks
- Report progress and metrics
- Handle failures gracefully

## Command Reference

### /prd-analyze

Analyzes a PRD for parallel execution opportunities.

```bash
/prd-analyze <prd-file> [options]

Options:
  --output, -o       Output directory for analysis results
  --visualize, -v    Generate dependency graph visualization
  --format, -f       Output format (json, yaml, text)
  --max-agents, -m   Maximum concurrent agents to consider
```

**Example:**
```bash
/prd-analyze authentication-system.md --visualize --max-agents 4
```

**Output:**
- Dependency graph visualization
- Wave execution plan
- Time savings analysis
- Resource conflict report

### /prd-parallel

Executes a PRD with parallel optimization.

```bash
/prd-parallel <command> [options]

Commands:
  execute <prd-file>   Start parallel execution
  status               Show current execution status
  abort                Abort running execution
  resume               Resume from checkpoint

Options:
  --max-agents, -m     Maximum concurrent agents (default: 4)
  --monitor            Enable real-time monitoring UI
  --checkpoint-dir     Custom checkpoint directory
  --dry-run           Show execution plan without running
```

**Examples:**
```bash
# Execute with monitoring
/prd-parallel execute user-service.md --monitor --max-agents 6

# Check status
/prd-parallel status

# Resume after failure
/prd-parallel resume --checkpoint-dir ./checkpoints/user-service
```

## Configuration

### Config File (parallel_config.py)

```python
class ParallelExecutionConfig:
    max_concurrent_agents = 4        # Maximum parallel agents
    agent_timeout_hours = 4.0        # Per-phase timeout
    checkpoint_interval_minutes = 15  # State save frequency
    enable_monitoring = True         # Terminal UI monitoring
    resource_lock_timeout = 300      # Lock timeout (seconds)
    retry_failed_phases = True       # Auto-retry on failure
    max_retries = 2                 # Maximum retry attempts
```

### Environment Variables

```bash
# Override configuration
export PRD_MAX_AGENTS=8
export PRD_CHECKPOINT_DIR=/custom/checkpoint/path
export PRD_ENABLE_MONITORING=true
```

## Monitoring & Metrics

### Real-time Dashboard

The monitoring UI provides:
- Overall execution progress
- Wave-by-wave phase status
- Agent activity and resource usage
- Live log streaming
- Performance metrics

**Keyboard Shortcuts:**
- `P` - Pause/Resume execution
- `Q` - Quit (with confirmation)
- `L` - Toggle log view
- `D` - Show detailed metrics
- `R` - Refresh display

### Metrics Collection

The system automatically collects:
- **Time Metrics**: Sequential vs parallel duration, time saved
- **Phase Metrics**: Individual phase performance, estimation accuracy
- **Resource Metrics**: CPU/memory usage, lock contention
- **Efficiency Metrics**: Parallelization efficiency, agent utilization

**Export Metrics:**
```bash
# After execution, find metrics in:
./metrics/execution_summary_*.csv
./metrics/execution_metrics_*.json
```

### Performance Reports

Generate detailed performance reports:
```python
from monitoring.metrics_collector import MetricsCollector

collector = MetricsCollector()
report = collector.generate_report(execution_metrics)
print(report)
```

## Best Practices

### PRD Structure

1. **Clear Phase Boundaries**: Define distinct, atomic phases
2. **Explicit Dependencies**: Use "Dependencies:" or "Depends on:" consistently
3. **Resource Declarations**: Specify "Modifies:" for file changes
4. **Accurate Estimates**: Provide realistic time estimates

**Good Example:**
```markdown
## Phase 3: User API
**Dependencies**: Phase 1, Phase 2
**Modifies**: api/users.py, models/user.py
**Estimated hours**: 4

Implement RESTful API endpoints for user management.
```

### Dependency Management

1. **Minimize Dependencies**: Only declare essential dependencies
2. **Avoid Circular Dependencies**: System will detect and error
3. **Group Related Work**: Phases modifying same files should be sequential
4. **Consider Resource Conflicts**: Plan file modifications carefully

### Performance Optimization

1. **Right-size Agents**: More agents ≠ faster (overhead costs)
2. **Balance Wave Sizes**: Even distribution improves efficiency
3. **Monitor Lock Contention**: High contention indicates poor parallelization
4. **Profile Long Phases**: Break down phases over 4 hours

### Error Handling

1. **Checkpoint Frequently**: Default 15 minutes is recommended
2. **Design for Idempotency**: Phases should be re-runnable
3. **Handle Partial Completion**: Use state management properly
4. **Log Comprehensively**: Aid debugging and recovery

## Troubleshooting

### Common Issues

**1. High Lock Contention**
```
Symptom: Phases waiting for resource locks
Solution: Review file modification patterns, reduce conflicts
```

**2. Poor Parallelization**
```
Symptom: Low time savings (<20%)
Solution: Break down large phases, reduce dependencies
```

**3. Agent Failures**
```
Symptom: Phases failing with timeout
Solution: Increase agent_timeout_hours, check phase complexity
```

**4. Memory Issues**
```
Symptom: High memory usage with many phases
Solution: Reduce max_concurrent_agents, enable swap
```

### Debug Mode

Enable detailed debugging:
```bash
export PRD_DEBUG=true
/prd-parallel execute feature.md --monitor
```

### Recovery Procedures

**From Checkpoint:**
```bash
# Find latest checkpoint
ls -la checkpoints/

# Resume execution
/prd-parallel resume --checkpoint-dir checkpoints/feature_20240115_143022
```

**Manual State Recovery:**
```python
from orchestrator.state_manager import StateManager

# Load state
state_manager = StateManager(Path("./checkpoints"))
state = state_manager.load_latest_state()

# Inspect state
print(f"Completed phases: {len([p for p in state.execution.phases.values() if p.status == 'COMPLETED'])}")
print(f"Failed phases: {[p.phase_id for p in state.execution.phases.values() if p.status == 'FAILED']}")
```

### Performance Tuning

**Run Benchmarks:**
```bash
python -m benchmarks.parallel_benchmarks
```

**Analyze Results:**
- Optimal agent count for your workload
- Overhead measurements
- Scalability limits
- Resource bottlenecks

## Advanced Usage

### Custom Wave Strategies

Implement custom wave calculation:
```python
from analyzers.wave_calculator import WaveCalculator

class CustomWaveCalculator(WaveCalculator):
    def calculate_waves(self, phases, graph, conflicts=None):
        # Custom logic for wave assignment
        pass
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Execute PRD in Parallel
  run: |
    /prd-parallel execute ${{ github.event.inputs.prd_file }} \
      --max-agents 4 \
      --checkpoint-dir ./prd-checkpoints
```

### Programmatic Usage

```python
from orchestrator.parallel_orchestrator import ParallelOrchestrator
from monitoring.terminal_ui import monitor_execution

# Create orchestrator
orchestrator = ParallelOrchestrator(state_manager, config)

# Start execution
execution_id = orchestrator.execute_parallel(phases, waves, "feature-name")

# Monitor in separate thread
monitor_execution(orchestrator)

# Wait for completion
orchestrator.wait_for_completion()
```

## Support

For issues, questions, or contributions:
- GitHub Issues: [repo-url]/issues
- Documentation: [repo-url]/docs
- Examples: [repo-url]/examples