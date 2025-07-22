# /prd-parallel - Execute PRD Phases in Parallel

🎯 **COMMAND**: /prd-parallel | 📋 **WORKFLOW**: parallel - Execute PRD Phases in Parallel | 👤 **PERSONAS**: Software Architect + DevOps Engineer

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#DEVOPS_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->

Execute multiple PRD phases in parallel with intelligent dependency management, resource coordination, and real-time progress monitoring.

## Workflow:

1. **Load PRD Context**:
   - Read original PRD from `.claude/prd-workspace/[project]/prd-original.md` (repository-relative)
   - Load tracker from `.claude/prd-workspace/[project]/prd-tracker.md` (repository-relative)
   - Load all phase specifications from phase files

2. **Analyze Dependencies**:
   ```
   Analyzing phase dependencies...
   ✓ 6 phases identified
   ✓ Dependency graph validated
   ✓ No circular dependencies found
   
   Execution waves calculated:
   Wave 1: [phase-1-foundation] (1 phase)
   Wave 2: [phase-2-api, phase-3-database] (2 phases)
   Wave 3: [phase-4-business-logic, phase-5-frontend] (2 phases)
   Wave 4: [phase-6-integration-tests] (1 phase)
   ```

3. **Resource & Conflict Analysis**:
   ```
   Checking resource conflicts...
   ⚠ Warning: phase-2 and phase-3 both modify /src/config.yaml
   → Conflict resolution: phase-3 will wait for phase-2
   
   Resource allocation:
   - Max parallel agents: 5
   - Available workspace: 4 sandboxes
   - Memory allocation: 2GB per agent
   ```

4. **Execution Preview**:
   ```
   Parallel Execution Plan:
   ========================
   Total phases: 6
   Execution waves: 4
   Estimated time: 3.5 hours (vs 12 hours sequential)
   Parallelism efficiency: 71%
   
   Wave breakdown:
   - Wave 1 (0h): 1 agent for foundation setup
   - Wave 2 (0-3h): 2 agents for API and Database
   - Wave 3 (3-7h): 2 agents for Business Logic and Frontend
   - Wave 4 (7-9h): 1 agent for Integration Tests
   
   Proceed? (y/n)
   ```

5. **Live Execution Dashboard**:
   ```
   PRD Parallel Execution - continuous-improvement
   ===============================================
   Overall Progress: ████████░░░░░░░░ 45% (2.7/6 phases)
   Time Elapsed: 1h 23m | Est. Remaining: 2h 07m
   
   Wave 2/4 - Active Agents: 2/5
   ┌─────────────────────────┬─────────────────────────┐
   │ Phase 2: API Layer      │ Phase 3: Database       │
   │ Status: IN_PROGRESS     │ Status: IN_PROGRESS     │
   │ Progress: ███████░░ 70% │ Progress: ████░░░░░ 40% │
   │ Duration: 45m           │ Duration: 45m           │
   │ Agent: claude-agent-2   │ Agent: claude-agent-3   │
   └─────────────────────────┴─────────────────────────┘
   
   Completed Phases:
   ✓ Phase 1: Foundation Setup (30m)
   
   Resource Usage:
   CPU: 45% | Memory: 3.2/8GB | Disk I/O: moderate
   
   Recent Activity:
   [1h23m] Phase 2: Created /src/api/endpoints.py
   [1h22m] Phase 3: Running database migrations
   [1h20m] Phase 2: Completed authentication module
   ```

6. **Real-time Monitoring**:
   - Track individual agent progress
   - Monitor resource utilization
   - View live logs from each sandbox
   - Detect and handle deadlocks
   - Automatic failure recovery

7. **Completion Summary**:
   ```
   Parallel Execution Complete!
   ===========================
   Total Duration: 3h 28m
   Success Rate: 100% (6/6 phases)
   Time Saved: 8h 32m (71% faster)
   
   Phase Results:
   ✓ Phase 1: Foundation Setup (30m)
   ✓ Phase 2: API Layer (2h 15m)
   ✓ Phase 3: Database Layer (2h 45m)
   ✓ Phase 4: Business Logic (3h 30m)
   ✓ Phase 5: Frontend (3h 15m)
   ✓ Phase 6: Integration Tests (2h 00m)
   
   Artifacts created: 47 files
   Tests passed: 156/156
   
   Ready for integration with /prd-integrate
   ```

## Command Options:

```bash
# Basic parallel execution
/prd-parallel [project-name]

# With specific configuration
/prd-parallel [project-name] --max-agents 3

# Dry run to see execution plan
/prd-parallel [project-name] --dry-run

# Resume from saved state
/prd-parallel [project-name] --resume

# Validate only (no execution)
/prd-parallel [project-name] --validate
```

## Advanced Features:

### Resource Management:
- Dynamic agent spawning based on available resources
- Intelligent work distribution across agents
- Automatic load balancing
- Resource contention resolution

### Failure Handling:
- Automatic retry for transient failures
- Graceful degradation to sequential execution
- Checkpoint/resume capability
- Rollback on critical failures

### Progress Tracking:
- Real-time web dashboard (optional)
- CLI progress bars and status updates
- Detailed execution logs per agent
- Performance metrics and analytics

## Example Usage:

```
/prd-parallel continuous-improvement

> Loading PRD and phase specifications...
> Analyzing dependencies and calculating waves...
> 
> Execution Plan:
> - 6 phases across 4 waves
> - Max parallelism: 2 phases simultaneously
> - Estimated time: 3.5 hours
> 
> Starting parallel execution...
> 
> [Live dashboard showing progress]
> 
> Execution complete! All phases successful.
> Time saved: 8.5 hours (71% improvement)
> 
> Use /prd-integrate to merge results into main repository
```

## Path Resolution:
- This command automatically uses repository-relative paths
- All paths resolve to the repository root when in a git repository
- Falls back to current directory when not in a repository
- Set `CLAUDE_OUTPUT_ROOT` environment variable to override

## Integration with Other Commands:

```bash
# Analyze dependencies before execution
/prd-analyze [project-name]

# Execute specific phases in parallel
/prd-parallel [project-name] --phases 2,3,4

# Monitor ongoing execution
/prd-progress [project-name] --watch

# Preview integration after parallel execution
/prd-preview [project-name]
```

This enables massive productivity gains for complex PRDs while maintaining quality and correctness through intelligent orchestration.