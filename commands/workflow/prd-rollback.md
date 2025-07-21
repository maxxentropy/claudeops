# /prd-rollback - Rollback PRD Integration

🎯 **COMMAND**: /prd-rollback | 📋 **WORKFLOW**: rollback - Rollback PRD Integration | 👤 **PERSONAS**: Devops Architect + Senior Engineer

Embody these expert personas:
<!-- INCLUDE: system/personas.md#DEVOPS_ARCHITECT -->
<!-- INCLUDE: system/personas.md#SENIOR_ENGINEER -->

Safely rollback a PRD integration to restore the repository to its previous state.

## Purpose

Provides a safety net for PRD integrations:
- Restores files to pre-integration state
- Removes newly created files
- Reverts all modifications
- Maintains git history integrity

## Workflow

1. **List Available Rollbacks**:
   ```
   Available rollbacks for: user-auth-system
   
   1. 2025-01-21-143052 (2 hours ago)
      - Phase: Complete integration
      - Files affected: 15
      - Status: Ready to rollback
   
   2. 2025-01-20-094521 (1 day ago)
      - Phase: Phase 3 only
      - Files affected: 5
      - Status: Partially applied
   ```

2. **Analyze Rollback Scope**:
   ```
   Rollback analysis for: 2025-01-21-143052
   
   Files to restore (3):
   - src/index.js → Restore from backup
   - package.json → Restore from backup
   - README.md → Restore from backup
   
   Files to remove (12):
   - src/auth/login.js
   - src/auth/register.js
   - tests/auth/*.test.js
   
   Directories to remove (2):
   - src/auth/ (if empty)
   - tests/auth/ (if empty)
   ```

3. **Execute Rollback**:
   ```
   Executing rollback...
   
   ✓ Restored: src/index.js
   ✓ Restored: package.json
   ✓ Restored: README.md
   ✓ Removed: src/auth/login.js
   ✓ Removed: src/auth/register.js
   ✓ Cleaned: Empty directories
   
   Rollback complete!
   Repository restored to pre-integration state.
   ```

4. **Post-Rollback Verification**:
   ```
   Verification:
   ✓ All backup files restored
   ✓ New files removed
   ✓ Git status matches pre-integration
   ✓ Tests passing
   
   Rollback backup archived at:
   .claude/prd-workspace/[project]/rollback-history/2025-01-21-143052/
   ```

## Example Usage

```bash
# Rollback latest integration
/prd-rollback parallel-execution-system

# Rollback specific backup
/prd-rollback parallel-execution-system --backup-id 2025-01-21-143052

# Preview rollback without executing
/prd-rollback parallel-execution-system --dry-run
```

## Options

- `--backup-id`: Specify exact backup to use
- `--dry-run`: Preview rollback without executing
- `--keep-files`: Don't remove new files (partial rollback)
- `--force`: Skip confirmation prompts

## Rollback Scenarios

1. **Full Rollback**: Complete restoration to pre-integration
2. **Partial Rollback**: Keep some changes, revert others
3. **Selective Rollback**: Choose specific files to restore

## Safety Features

- Requires confirmation for destructive actions
- Creates rollback history for audit trail
- Preserves git commit history
- Validates backup integrity before rollback
- Won't rollback if uncommitted changes exist

## Backup Structure

```
.claude/prd-workspace/[project]/backups/[timestamp]/
├── manifest.json          # List of all changes
├── files/                # Backed up original files
│   ├── src/index.js
│   └── package.json
├── git-state.json        # Git status at backup time
└── integration-log.json  # What was integrated
```

This ensures that any PRD integration can be safely undone if issues arise.