# Phase 2: Path Resolution Service

## Objective
Implement a path resolution service that converts template paths to absolute paths using the repository root detection from Phase 1.

## Dependencies
- **Required from Phase 1**: `system/utils/repo_detector.py`
- Python 3.6+ (standard library only)

## Deliverables

### 1. Path Resolution Module
**File**: `system/utils/path_resolver.py`

```python
class PathResolver:
    def __init__(self, repo_detector=None):
        """Initialize with optional repo detector instance"""
        
    def resolve_path(self, template_path, context=None):
        """Resolve a template path to absolute path"""
        # Replace ${REPO_ROOT} with actual repo root
        # Replace ${CWD} with current working directory
        # Replace ${HOME} with user home
        # Handle relative paths from repo root
        # Return absolute path
        
    def resolve_command_path(self, command_name, relative_path):
        """Resolve path for a specific command output"""
        # Get repo root or fallback to CWD
        # Join with relative path
        # Create directories if needed
        # Return absolute path
        
    def get_workspace_path(self, feature_slug):
        """Get consistent workspace path for a feature"""
        # Always returns ${REPO_ROOT}/.claude/prd-workspace/{slug}
        # Creates directory structure if missing
```

### 2. Template Variable Support
Support these variables in paths:
- `${REPO_ROOT}` - Repository root (or CWD if not in repo)
- `${CWD}` - Current working directory
- `${HOME}` - User home directory
- `${DATE}` - Current date in YYYY-MM-DD format
- `${TIMESTAMP}` - Unix timestamp

### 3. Fallback Logic
When not in a git repository:
1. `${REPO_ROOT}` → current working directory
2. Log warning about fallback mode
3. Still create expected directory structure
4. Consider `.claude` marker file as alternative root indicator

### 4. Path Safety
- Validate paths don't escape intended directories
- Prevent path traversal attacks
- Normalize paths (remove .., symlinks, etc.)
- Handle Windows vs Unix path separators

### 5. Unit Tests
**File**: `tests/test_path_resolver.py`

Test cases:
- [ ] Template variable replacement
- [ ] Relative path resolution
- [ ] Fallback when no repo
- [ ] Directory creation
- [ ] Path safety validation
- [ ] Cross-platform paths
- [ ] Integration with repo detector

## Success Criteria
- [ ] All template variables replaced correctly
- [ ] Paths are always absolute
- [ ] Fallback behavior works smoothly
- [ ] Directories created as needed
- [ ] No security vulnerabilities

## Implementation Notes

### Template Processing
```python
# Example usage:
resolver = PathResolver()
path = resolver.resolve_path("${REPO_ROOT}/docs/prds/${DATE}-${SLUG}.md", {
    "SLUG": "feature-name"
})
# Returns: /absolute/path/to/repo/docs/prds/2024-01-21-feature-name.md
```

### Directory Creation
- Use `os.makedirs(path, exist_ok=True)`
- Set appropriate permissions (755 for dirs)
- Handle race conditions in concurrent usage

### Error Handling
- FileNotFoundError → Create directory
- PermissionError → Return error with helpful message
- Invalid template → Raise ValueError with details

## Context for Next Phase
Phase 3 will integrate this resolver into the hook system:
- Hooks will create a PathResolver instance
- Pass it to commands via environment or config
- Commands will use it instead of hardcoded paths