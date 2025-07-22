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

## Path Resolution:
- This command automatically uses repository-relative paths
- Backup files are loaded from `.claude/prd-workspace/[project]/backups/` at repository root
- Files are restored to their original locations relative to repository root
- If not in a git repository, falls back to current directory
- Set `CLAUDE_OUTPUT_ROOT` environment variable to override

## Implementation Note:
When implementing this command, always use the path resolution utilities to ensure consistent paths:

```python
# Import path resolution utilities
import sys
import os
sys.path.insert(0, os.path.expanduser('~/.claude'))
from system.utils import path_resolver

# Get workspace path for the project
workspace_path = path_resolver.get_workspace_path(project_name)

if not workspace_path.exists():
    print(f"No workspace found for project: {project_name}")
    return

# Find backups directory
backups_dir = workspace_path / "backups"
if not backups_dir.exists():
    print(f"No backups found for project: {project_name}")
    return

# List available backups
backups = sorted(backups_dir.iterdir(), reverse=True)  # Most recent first

# For specific backup
if backup_id:
    backup_path = backups_dir / backup_id
else:
    # Use most recent backup
    backup_path = backups[0] if backups else None

if not backup_path or not backup_path.exists():
    print(f"Backup not found: {backup_id or 'latest'}")
    return

# Load backup manifest
manifest_path = backup_path / "manifest.json"
import json
with open(manifest_path) as f:
    manifest = json.load(f)

# Get repository root for file restoration
repo_root = path_resolver.get_repo_root()
if not repo_root:
    print("Warning: Not in a git repository, using current directory")
    repo_root = Path.cwd()

# Restore files
backup_files_dir = backup_path / "files"
for relative_path in manifest['modified_files']:
    backup_file = backup_files_dir / relative_path
    target_file = repo_root / relative_path
    
    if backup_file.exists():
        import shutil
        shutil.copy2(backup_file, target_file)
        print(f"✓ Restored: {relative_path}")

# Remove new files
for relative_path in manifest['created_files']:
    target_file = repo_root / relative_path
    if target_file.exists():
        target_file.unlink()
        print(f"✓ Removed: {relative_path}")

# Archive rollback
rollback_history = workspace_path / "rollback-history" / backup_id
rollback_history.mkdir(parents=True, exist_ok=True)
shutil.move(str(backup_path), str(rollback_history))

# Format output
output_paths = {
    "Rollback completed from": backup_path,
    "Files restored": len(manifest['modified_files']),
    "Files removed": len(manifest['created_files']),
    "Rollback archived to": rollback_history
}
print(path_resolver.format_output_message(output_paths))
```

**Important**: Never hardcode paths like `.claude/prd-workspace/`. Always use the path resolver to ensure paths work correctly from any directory.