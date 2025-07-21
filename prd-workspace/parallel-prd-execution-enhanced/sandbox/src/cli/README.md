# CLI Commands for Parallel PRD Execution

This directory contains command-line interfaces for the parallel PRD execution system.

## Commands

### prd-parallel
Main command for executing PRD phases in parallel.

```bash
# Basic parallel execution
prd-parallel my-project

# Dry run to see execution plan
prd-parallel my-project --dry-run

# Resume from saved state
prd-parallel my-project --resume

# Limit concurrent agents
prd-parallel my-project --max-agents 3

# Validate dependencies only
prd-parallel my-project --validate
```

### prd-analyze
Analyze PRD dependencies and generate execution plans.

```bash
# Basic dependency analysis
prd-analyze my-project

# Generate visual dependency graph
prd-analyze my-project --graph

# Export analysis as JSON
prd-analyze my-project --json > analysis.json

# Generate detailed markdown report
prd-analyze my-project --report > report.md

# Check specific aspects
prd-analyze my-project --check conflicts
prd-analyze my-project --check critical-path
```

### prd-implement --parallel
Updated to support parallel execution of ready phases.

```bash
# Sequential implementation (default)
prd-implement my-project phase-3

# Parallel implementation of ready phases
prd-implement my-project --parallel

# Implement specific phases in parallel
prd-implement my-project --parallel --phases 2,3,4
```

## Shell Integration

Source the shell integration script to add commands to your shell:

```bash
source /path/to/cli/shell_integration.sh
```

This provides:
- `prd-parallel` - Execute PRD phases in parallel
- `prd-analyze` - Analyze PRD dependencies
- `prd-watch` - Monitor active execution
- `prd-list` - List available projects
- `prd-stop` - Stop running execution

## Progress Monitoring

Monitor real-time progress of parallel execution:

```bash
# Watch execution progress
prd-watch my-project

# Or use the progress monitor directly
python3 progress_monitor.py my-project
```

## Architecture

The CLI commands are built on top of the orchestration system:

1. **prd_parallel_cli.py** - Main parallel execution interface
   - Loads phases from project directory
   - Configures and runs ParallelOrchestrator
   - Provides progress callbacks and output formatting

2. **prd_analyze_cli.py** - Dependency analysis interface
   - Uses analyzers to build dependency graphs
   - Calculates execution waves and metrics
   - Generates reports in multiple formats

3. **progress_monitor.py** - Real-time progress display
   - Reads execution state from `.execution_state.json`
   - Shows phase status, timing, and resource usage
   - Updates every 2 seconds

4. **shell_integration.sh** - Shell convenience functions
   - Adds commands to current shell session
   - Provides bash completion support
   - Helper functions for common operations