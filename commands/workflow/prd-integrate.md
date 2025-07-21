# /prd-integrate - Integrate PRD Results into Repository

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#DEVOPS_ARCHITECT -->

Safely integrate PRD sandbox implementation into the target repository with full rollback support.

## Purpose

Moves validated implementation from sandbox to production code:
- Applies file mappings from sandbox to repository
- Handles conflicts intelligently
- Creates backup for rollback
- Updates version control appropriately

## Workflow

1. **Pre-Integration Checks**:
   ```
   Running integration checks...
   ✓ Git status clean (no uncommitted changes)
   ✓ All tests passing in sandbox
   ✓ Integration mapping validated
   ✓ Backup directory prepared
   ```

2. **Create Integration Backup**:
   ```
   Creating backup: .claude/prd-workspace/[project]/backups/2025-01-21-143052/
   ✓ Backed up 3 existing files
   ✓ Recorded current git state
   ✓ Rollback point created
   ```

3. **Execute Integration**:
   ```
   Integrating: user-auth-system
   
   Creating new files (12):
   ✓ src/auth/login.js
   ✓ src/auth/register.js
   ✓ src/auth/middleware.js
   ✓ tests/auth/login.test.js
   
   Updating existing files (3):
   ✓ package.json (dependencies merged)
   ✓ src/index.js (routes added)
   ✓ README.md (documentation updated)
   
   Creating directories (2):
   ✓ src/auth/
   ✓ tests/auth/
   ```

4. **Post-Integration Verification**:
   ```
   Running post-integration checks...
   ✓ All files created successfully
   ✓ No compilation errors
   ✓ Tests still passing
   ✓ Git diff shows expected changes
   ```

5. **Integration Report**:
   ```
   Integration Complete!
   
   Summary:
   - Files created: 12
   - Files modified: 3
   - Tests status: ✓ Passing
   - Backup ID: 2025-01-21-143052
   
   Next steps:
   1. Review changes: git diff
   2. Run full test suite: npm test
   3. Commit when ready: git add . && git commit
   
   Rollback available: /prd-rollback user-auth-system
   ```

## Integration Mapping

The system uses `integration/mapping.json` to determine file destinations:

```json
{
  "repository": "auto-detect",
  "mappings": {
    "commands/": ".claude/commands/workflow/",
    "lib/": ".claude/lib/",
    "src/": "src/",
    "tests/": "tests/"
  },
  "ignore": [
    "*.tmp",
    ".DS_Store"
  ]
}
```

## Options

- `--phase N`: Integrate only specific phase
- `--dry-run`: Same as /prd-preview
- `--force`: Override conflict detection
- `--interactive`: Manual merge for conflicts
- `--no-backup`: Skip backup creation (not recommended)

## Example Usage

```bash
/prd-integrate parallel-execution-system

> Pre-integration checks...
> ✓ Repository clean
> ✓ Creating backup at .claude/prd-workspace/parallel-execution-system/backups/
> 
> Integrating files...
> ✓ Created: commands/workflow/prd-parallel.md
> ✓ Created: commands/workflow/prd-analyze.md
> ✓ Created: lib/dependency-graph.js
> ✓ Created: lib/parallel-orchestrator.js
> ✓ Updated: commands/workflow/prd-implement.md
> 
> Integration successful!
> Backup ID: 2025-01-21-145523
> 
> Review with: git status
> Rollback with: /prd-rollback parallel-execution-system
```

## Conflict Resolution

When conflicts are detected:

1. **Interactive Mode** (`--interactive`):
   - Opens merge tool for each conflict
   - Allows line-by-line resolution
   - Preserves both versions for review

2. **Force Mode** (`--force`):
   - Overwrites target files
   - Still creates backup first
   - Use with caution

3. **Manual Resolution**:
   - Integration pauses at conflict
   - Fix conflicts manually
   - Resume with `/prd-integrate --continue`

## Safety Features

- Always creates backup before changes
- Validates git status before starting
- Atomic operation (all or nothing)
- Full rollback capability
- Preserves file permissions
- Respects .gitignore

This ensures PRD implementations can be safely integrated into any repository.