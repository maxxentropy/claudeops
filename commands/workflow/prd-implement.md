# /prd-implement - Execute PRD Phase with Full Context

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#SENIOR_TEST_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->

Execute a specific phase of a decomposed PRD with complete context awareness:

## Workflow:

1. **Load Full Context**:
   - Read original PRD from `.claude/prd-workspace/[project]/prd-original.md`
   - Load tracker from `.claude/prd-workspace/[project]/prd-tracker.md`
   - Read phase spec from `.claude/prd-workspace/[project]/phase-[N]-[name].md`
   - **Load all previous phase artifacts** from `artifacts/`

2. **Setup Sandbox Environment**:
   ```
   Creating sandbox at: .claude/prd-workspace/[project]/sandbox/
   ✓ Isolated implementation directory ready
   ✓ Repository context detected: [repo-name]
   ✓ Integration mapping initialized
   ```

3. **Verify Prerequisites**:
   ```
   Checking Phase 3 prerequisites...
   ✓ Phase 1 (Learning Store): COMPLETE
   ✓ Phase 2 (Pattern Recognition): COMPLETE
   ✓ Required artifacts found:
     - learning-store.js
     - patterns.js
     - store-schema.json
   ```

4. **Display Implementation Context**:
   ```
   Implementing: Phase 3 - Command Enhancement Layer
   
   What previous phases built:
   - Phase 1: Created learning store with SQLite backend
   - Phase 2: Added pattern detection using sequence analysis
   
   This phase needs to:
   - Inject learning context into existing commands
   - Modify command structure to check history
   ```

5. **Execute Implementation in Sandbox**:
   - Follow phase specification exactly
   - Reference previous artifacts explicitly
   - Apply all safety protocols from `/safe`
   - Create new files in `sandbox/` directory
   - Save reference artifacts in `artifacts/phase-[N]/`

6. **Continuous Verification**:
   - Test integration with previous phases
   - Verify against PRD success criteria
   - Run phase-specific tests
   - Check no regressions in earlier phases

7. **Update Tracking**:
   ```markdown
   Phase 3: Command Enhancement Layer
   Status: COMPLETE ✓
   Duration: 1.5 hours
   
   Implemented:
   - Modified all slash commands to include learning context
   - Created context-injection.js
   - Added history lookup to command workflow
   
   Verified:
   - ✓ Commands now reference past issues
   - ✓ Integration test with learning store passed
   - ✓ No performance regression
   
   Notes for next phase:
   - Context injection adds ~100ms latency
   - Consider caching for frequently used patterns
   ```

8. **Prepare Integration**:
   - Update `integration/mapping.json` with file destinations
   - Document any repository-specific adjustments needed
   - Create integration preview report

## Sandbox Directory Structure:

```
.claude/prd-workspace/[project]/
├── sandbox/                    # Isolated implementation area
│   ├── src/                   # Source code
│   ├── tests/                 # Test files
│   ├── commands/              # New commands (if applicable)
│   └── docs/                  # Documentation
├── artifacts/                 # Phase outputs for reference
│   ├── phase-1/
│   ├── phase-2/
│   └── phase-3/
└── integration/               # Integration mappings
    ├── mapping.json           # File destination mappings
    └── conflicts.log          # Detected conflicts
```

## Integration Workflow:

After implementation, use these commands to integrate results:

```bash
# Preview what would be integrated
/prd-preview [project-name]

# Integrate sandbox results into target repository
/prd-integrate [project-name] [--phase N]

# Rollback integration if needed
/prd-rollback [project-name]
```

## Command Options:

```bash
# Sequential implementation (default)
/prd-implement [project-name] phase-[N]

# Parallel implementation of ready phases
/prd-implement [project-name] --parallel

# Implement specific phases in parallel
/prd-implement [project-name] --parallel --phases 2,3,4

# Check if phases can be parallelized
/prd-implement [project-name] --parallel --dry-run
```

## Parallel Execution Mode:

When using `--parallel`, the command:

1. **Analyzes Current State**:
   ```
   Checking ready phases...
   ✓ Phase 1: COMPLETE
   ✓ Phase 2: READY (dependencies met)
   ✓ Phase 3: READY (dependencies met)
   ✗ Phase 4: BLOCKED (requires phase 2 & 3)
   
   Ready for parallel execution: phase-2, phase-3
   ```

2. **Spawns Parallel Agents**:
   ```
   Starting parallel implementation...
   ✓ Agent 1: Assigned to phase-2-api-layer
   ✓ Agent 2: Assigned to phase-3-database-layer
   
   Monitoring parallel execution...
   [Agent 1] Creating API endpoints...
   [Agent 2] Setting up database schema...
   ```

3. **Provides Real-time Updates**:
   ```
   Parallel Implementation Progress:
   ================================
   Phase 2: ████████░░ 80% (45m) - Creating auth module
   Phase 3: ██████░░░░ 60% (45m) - Running migrations
   
   Resources: 2/5 agents active | CPU: 40% | Memory: 3.1GB
   ```

## Example Usage:

### Sequential Mode:
```
/prd-implement continuous-improvement phase-3

> Loading context...
> Setting up sandbox environment...
> Repository detected: ~/.claude
> Previous phases built: learning-store.js, patterns.js
> This phase objective: Enhance commands with learning context
> 
> Starting implementation in sandbox...
> [Full implementation with context awareness]
>
> Phase 3 COMPLETE. 
> Files created in sandbox:
>   - src/context-injection.js
>   - tests/context-injection.test.js
>   - commands/enhanced-safe.md
>
> Ready for integration review with /prd-preview
> Overall progress: 60% complete
```

### Parallel Mode:
```
/prd-implement continuous-improvement --parallel

> Analyzing phase dependencies...
> Ready phases: phase-2-api, phase-3-database
> 
> Starting parallel implementation with 2 agents...
> 
> [Agent 1 - Phase 2] Setting up API layer...
> [Agent 2 - Phase 3] Creating database schema...
> 
> Parallel execution complete!
> Phase 2: COMPLETE (2h 15m)
> Phase 3: COMPLETE (2h 45m)
> Total time: 2h 45m (saved 2h 15m)
> 
> Ready for integration review with /prd-preview
> Overall progress: 50% complete
```

## Key Features:
- **Sandbox isolation** prevents accidental modifications
- **Repository-agnostic** works with any codebase
- **Never loses context** between phases
- **Builds on previous work** explicitly
- **Tracks against original PRD** continuously
- **Safe integration** with preview and rollback
- **Enables parallel work** once dependencies met

This ensures complex PRDs are implemented correctly without overwhelming context or losing track of progress while maintaining clean separation between development and production code.