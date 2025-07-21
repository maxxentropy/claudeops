# Phase 4: Commands & Integration

## Overview
Create user-facing commands that integrate the parallel execution system into the existing Claude workflow, including the new `/prd-parallel` command and `--parallel` flag enhancement.

## Estimated Time: 1.5 hours

## Dependencies: Phase 1 (models), Phase 2 (analysis), Phase 3 (orchestrator)

## Objectives
1. Implement `/prd-parallel` command
2. Add `--parallel` flag to `/prd-implement`
3. Create command validation and error handling
4. Integrate with existing workflow seamlessly

## Detailed Tasks

### 1. PRD Parallel Command (`commands/workflow/prd-parallel.md`)
```markdown
# /prd-parallel - Execute PRD Phases in Parallel

Intelligent parallel execution of PRD implementation phases with automatic dependency analysis and resource coordination.

## Usage:
/prd-parallel [feature-slug] [options]

## Options:
--max-agents N     Maximum parallel agents (default: 3)
--dry-run         Show execution plan without running
--from-phase N    Start from specific phase number
--monitor         Open real-time monitoring dashboard

## Workflow:
1. Load PRD workspace and phases
2. Analyze dependencies and calculate waves
3. Display execution plan for confirmation
4. Execute phases in parallel waves
5. Monitor progress and handle failures

## Example:
/prd-parallel user-auth --max-agents 4 --monitor
```

### 2. Enhanced PRD Implement (`commands/workflow/prd-implement-enhanced.py`)
```python
# Add --parallel flag support:
- Detect --parallel flag in arguments
- Switch to parallel orchestrator when flag present
- Maintain backward compatibility
- Share progress tracking with original command

# Key changes:
def execute_command(args):
    if "--parallel" in args:
        return execute_parallel(args)
    else:
        return execute_sequential(args)
```

### 3. Command Validators (`validators/command_validator.py`)
```python
# Validate parallel execution requirements:
- check_workspace_exists(slug) -> bool
- validate_phase_files(workspace) -> List[Error]
- check_parallel_prerequisites() -> bool
- estimate_resource_requirements(phases) -> ResourceEstimate

# Pre-flight checks:
- Sufficient phases for parallelization
- No active locks in workspace
- Valid dependency structure
- Available system resources
```

### 4. Error Handlers (`handlers/parallel_error_handler.py`)
```python
# Graceful error handling:
- handle_agent_failure(agent, error) -> Recovery
- handle_lock_timeout(lock) -> Resolution
- handle_wave_failure(wave, errors) -> Decision
- generate_failure_report(execution) -> Report

# Recovery strategies:
- Retry failed phases
- Skip non-critical failures
- Rollback on critical errors
- Save partial progress
```

### 5. Integration Layer (`integration/workflow_integration.py`)
```python
# Seamless workflow integration:
- merge_parallel_progress(tracker) -> None
- update_prd_tracker(phase_results) -> None
- notify_completion(execution) -> None
- archive_execution_logs(workspace) -> None

# Ensure compatibility with:
- Existing PRD tracker format
- Progress monitoring tools
- Artifact organization
- Team collaboration features
```

## Expected Outputs

### Files to Create:
1. `/commands/workflow/prd-parallel.md` - New parallel command
2. `/commands/workflow/prd-implement-enhanced.py` - Enhanced implement command
3. `/validators/command_validator.py` - Command validation logic
4. `/handlers/parallel_error_handler.py` - Error handling
5. `/integration/workflow_integration.py` - Workflow integration
6. `/tests/test_commands.py` - Command tests

### Command Examples:
```bash
# New parallel command
/prd-parallel authentication-system --max-agents 4

# Enhanced implement with parallel flag
/prd-implement auth-system phase-1 --parallel

# Dry run to see execution plan
/prd-parallel payment-gateway --dry-run

# Resume from specific phase
/prd-parallel user-dashboard --from-phase 3
```

## Integration Points
- Uses orchestrator from Phase 3
- Leverages analysis from Phase 2
- Updates existing PRD tracker
- Compatible with current workflow

## Success Criteria
- [ ] `/prd-parallel` command works end-to-end
- [ ] `--parallel` flag enhances existing command
- [ ] Clear error messages for all failure modes
- [ ] Seamless integration with current workflow
- [ ] Comprehensive validation prevents bad states
- [ ] 95%+ test coverage for commands

## User Experience Flow
```
1. User runs: /prd-parallel feature-xyz
2. System shows execution plan:
   Wave 1: Phase 1 (foundation) - 1.5 hrs
   Wave 2: Phase 2, 3 (parallel) - 2 hrs
   Wave 3: Phase 4 (integration) - 1 hr
   Total time: 4.5 hrs (vs 7 hrs sequential)
3. User confirms execution
4. System spawns agents and shows progress
5. Completion notification with results
```

## Notes for Next Phase
Phase 5 will add the monitoring dashboard that these commands reference. Ensure commands provide appropriate hooks for real-time progress updates.