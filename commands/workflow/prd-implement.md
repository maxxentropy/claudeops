# /prd-implement - Execute PRD Phase with Full Context

Embody these expert personas:
<!-- INCLUDE: system/../system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/../system/personas.md#SENIOR_TEST_ENGINEER -->

Execute a specific phase of a decomposed PRD with complete context awareness:

## Workflow:

1. **Load Full Context**:
   - Read original PRD from `.claude/prd-workspace/[project]/prd-original.md`
   - Load tracker from `.claude/prd-workspace/[project]/prd-tracker.md`
   - Read phase spec from `.claude/prd-workspace/[project]/phase-[N]-[name].md`
   - **Load all previous phase artifacts** from `artifacts/`

2. **Verify Prerequisites**:
   ```
   Checking Phase 3 prerequisites...
   ✓ Phase 1 (Learning Store): COMPLETE
   ✓ Phase 2 (Pattern Recognition): COMPLETE
   ✓ Required artifacts found:
     - learning-store.js
     - patterns.js
     - store-schema.json
   ```

3. **Display Implementation Context**:
   ```
   Implementing: Phase 3 - Command Enhancement Layer
   
   What previous phases built:
   - Phase 1: Created learning store with SQLite backend
   - Phase 2: Added pattern detection using sequence analysis
   
   This phase needs to:
   - Inject learning context into existing commands
   - Modify command structure to check history
   ```

4. **Execute Implementation**:
   - Follow phase specification exactly
   - Reference previous artifacts explicitly
   - Apply all safety protocols from `/safe`
   - Create new artifacts in `artifacts/phase-[N]/`

5. **Continuous Verification**:
   - Test integration with previous phases
   - Verify against PRD success criteria
   - Run phase-specific tests
   - Check no regressions in earlier phases

6. **Update Tracking**:
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

7. **Prepare Next Phase Context**:
   - Document key decisions made
   - List new artifacts created
   - Note any deviations from plan
   - Identify optimization opportunities

## Example Usage:
```
/prd-implement continuous-improvement phase-3

> Loading context...
> Previous phases built: learning-store.js, patterns.js
> This phase objective: Enhance commands with learning context
> 
> Starting implementation...
> [Full implementation with context awareness]
>
> Phase 3 COMPLETE. Ready for phase-4.
> Overall progress: 60% complete
```

## Key Features:
- **Never loses context** between phases
- **Builds on previous work** explicitly
- **Tracks against original PRD** continuously
- **Documents everything** for team handoffs
- **Enables parallel work** once dependencies met

This ensures complex PRDs are implemented correctly without overwhelming context or losing track of progress.