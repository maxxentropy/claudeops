# Phase 3: Parallel Execution Orchestrator

## Overview
Build the core orchestration engine that spawns multiple agents, coordinates their execution, manages resource locks, and ensures smooth parallel processing of PRD phases.

## Estimated Time: 2 hours

## Dependencies: Phase 1 (models), Phase 2 (dependency analysis)

## Objectives
1. Implement multi-agent spawning system
2. Build wave-based execution engine
3. Create resource coordination manager
4. Add state persistence layer

## Detailed Tasks

### 1. Agent Spawner (`orchestrator/agent_spawner.py`)
```python
# Multi-agent management:
- spawn_agent(phase_info, workspace) -> AgentProcess
- monitor_agent_health(agent) -> AgentStatus
- terminate_agent(agent_id) -> bool
- collect_agent_logs(agent_id) -> List[LogEntry]

# Agent process wrapper:
- AgentProcess: subprocess wrapper with phase execution
- Inter-agent communication via shared state file
- Graceful shutdown handling
```

### 2. Wave Execution Engine (`orchestrator/wave_executor.py`)
```python
# Execute phases in waves:
- execute_wave(wave, workspace, config) -> WaveResult
- wait_for_wave_completion(wave) -> bool
- handle_phase_failure(phase, error) -> RecoveryAction
- transition_to_next_wave(current_wave) -> ExecutionWave

# Coordination logic:
- Max agents per wave enforcement
- Wave completion detection
- Inter-wave delay management
```

### 3. Resource Coordinator (`orchestrator/resource_coordinator.py`)
```python
# Advanced resource management:
- acquire_resources_for_phase(phase) -> List[ResourceLock]
- release_phase_resources(phase) -> None
- resolve_lock_conflict(conflict) -> Resolution
- monitor_deadlocks() -> List[Deadlock]

# Builds on Phase 1's resource manager
# Add distributed locking with file-based locks
```

### 4. State Persistence (`orchestrator/state_manager.py`)
```python
# Persist execution state:
- save_execution_state(state, workspace) -> None
- load_execution_state(workspace) -> ExecutionState
- update_phase_status(phase_id, status) -> None
- recover_from_crash(workspace) -> ExecutionState

# State file: workspace/parallel-state.json
# Atomic updates with file locking
```

### 5. Main Orchestrator (`orchestrator/parallel_orchestrator.py`)
```python
# Tie everything together:
class ParallelOrchestrator:
    def __init__(self, workspace, config)
    def execute_prd(self, phases) -> ExecutionResult
    def pause_execution(self) -> None
    def resume_execution(self) -> None
    def get_progress(self) -> ProgressReport

# Main execution flow:
1. Load phases and build dependency graph
2. Calculate execution waves
3. For each wave:
   - Acquire necessary resources
   - Spawn agents for parallel phases
   - Monitor progress
   - Handle completions/failures
4. Aggregate results and cleanup
```

## Expected Outputs

### Files to Create:
1. `/orchestrator/agent_spawner.py` - Agent lifecycle management
2. `/orchestrator/wave_executor.py` - Wave-based execution
3. `/orchestrator/resource_coordinator.py` - Resource coordination
4. `/orchestrator/state_manager.py` - State persistence
5. `/orchestrator/parallel_orchestrator.py` - Main orchestrator
6. `/tests/test_orchestrator.py` - Integration tests

### Key Classes:
- `AgentSpawner` - Manages agent processes
- `WaveExecutor` - Executes phases in waves
- `ResourceCoordinator` - Handles resource locking
- `StateManager` - Persists execution state
- `ParallelOrchestrator` - Main orchestration class

## Integration Points
- Uses models from Phase 1
- Uses dependency analysis from Phase 2
- Provides execution engine for Phase 4's commands
- Generates data for Phase 5's monitoring

## Success Criteria
- [ ] Successfully spawns multiple agents
- [ ] Executes independent phases in parallel
- [ ] Prevents resource conflicts via locking
- [ ] Recovers gracefully from failures
- [ ] Persists state for resumability
- [ ] No deadlocks or race conditions
- [ ] 90%+ test coverage

## Example Usage
```python
# Initialize orchestrator
orchestrator = ParallelOrchestrator(workspace, config)

# Execute PRD phases in parallel
result = orchestrator.execute_prd(phases)

# Monitor progress
while not result.is_complete:
    progress = orchestrator.get_progress()
    print(f"Wave {progress.current_wave}: {progress.percent_complete}%")
```

## Notes for Next Phase
Phase 4 will create user-facing commands that leverage this orchestrator. Ensure the orchestrator API is clean and provides all necessary hooks for command integration.