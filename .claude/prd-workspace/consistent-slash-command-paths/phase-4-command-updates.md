# Phase 4: Command Updates

## Objective
Update all slash commands to use repository-relative paths instead of current-directory-relative paths, ensuring consistent output locations.

## Dependencies
- **Required from Phase 2**: Path resolution service
- **Required from Phase 3**: Hook infrastructure with path context
- All existing command files

## Deliverables

### 1. PRD Command Updates
Update these commands to use `${REPO_ROOT}`:

**`/prd` command changes:**
- FROM: `Save to: docs/prds/[filename]`
- TO: `Save to: ${REPO_ROOT}/docs/prds/[filename]`
- Workspace: `${REPO_ROOT}/.claude/prd-workspace/[slug]/`

**`/prdq` command changes:**
- Similar updates for quick PRD creation
- Same path structure as `/prd`

**All `/prd-*` commands:**
- `/prd-decompose` - Update workspace paths
- `/prd-implement` - Read from repo-relative paths
- `/prd-preview` - Load from consistent location
- `/prd-progress` - Track in repo workspace
- Others: analyze, integrate, rollback, etc.

### 2. Generation Command Updates
Update path handling in:
- `/create-docs` - Documentation in `${REPO_ROOT}/docs/`
- `/api-crud` - API files relative to repo
- `/mobile-scaffold` - Mobile structure at repo root
- `/context-prime` - Context files in repo

### 3. Path Resolution Helper
Create a shared helper for commands:

**File**: `system/utils/command_paths.py`
```python
def get_prd_path(filename):
    """Get absolute path for PRD file"""
    
def get_workspace_path(feature_slug):
    """Get absolute path for feature workspace"""
    
def ensure_directory(path):
    """Create directory if it doesn't exist"""
    
def resolve_command_path(template):
    """Resolve any path template for commands"""
```

### 4. Command Template Updates
Modify command output messages:

**Before:**
```
✓ PRD saved to: docs/prds/2024-01-21-feature.md
```

**After:**
```
✓ PRD saved to: /absolute/path/to/repo/docs/prds/2024-01-21-feature.md
✓ (Repository: my-project)
```

### 5. Migration Testing
**File**: `tests/test_command_migrations.py`

Test each updated command:
- [ ] Run from repo root
- [ ] Run from subdirectory
- [ ] Run from outside repo
- [ ] Verify output locations
- [ ] Check backward compatibility

## Success Criteria
- [ ] All PRD commands use repo-relative paths
- [ ] All generation commands use repo-relative paths
- [ ] Commands show absolute paths in output
- [ ] Fallback behavior works correctly
- [ ] No breaking changes for existing workflows

## Implementation Strategy

### 1. Systematic Updates
For each command file:
1. Identify all path references
2. Replace with template variables
3. Update output messages
4. Test from multiple locations

### 2. Common Patterns to Update
```markdown
# Before:
Save to: `docs/prds/[filename]`
Create workspace: `.claude/prd-workspace/[slug]/`

# After:
Save to: `${REPO_ROOT}/docs/prds/[filename]`
Create workspace: `${REPO_ROOT}/.claude/prd-workspace/[slug]/`
```

### 3. Environment Access
Commands should check for:
```python
repo_root = os.environ.get('CLAUDE_REPO_ROOT', '.')
# Use repo_root in all path operations
```

### 4. Error Messages
Improve error messages to show context:
```
Error: Cannot create PRD directory
Path: /absolute/path/to/repo/docs/prds/
Reason: Permission denied
Hint: Check write permissions for the repository
```

## Context for Next Phase
Phase 5 will:
- Create comprehensive test suite
- Test edge cases and error conditions
- Document the new behavior
- Create migration guide