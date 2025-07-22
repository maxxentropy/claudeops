# Phase 3: Hook Infrastructure Update

## Objective
Update the hook infrastructure to inject repository root information into command context, making it available to all slash commands.

## Dependencies
- Required from Phase 1: `system/utils/repo_detector.py`
- Required from Phase 2: `system/utils/path_resolver.py`
- Existing hook infrastructure

## Deliverables
- [x] Updated hook system to inject `${REPO_ROOT}` variable
- [x] Context enhancement for path resolution
- [x] Backward compatibility maintained
- [x] Hook tests updated

## Success Criteria
- [x] All commands have access to `${REPO_ROOT}` in their context
- [x] Path resolver available via command context
- [x] No breaking changes to existing commands
- [x] Performance impact < 5ms per command
- [x] Clear documentation for command authors

## Implementation Details

The hook infrastructure modifications:
1. Pre-command hook to detect repository root
2. Context injection of path variables
3. Helper functions for commands to use

```python
# system/hooks/path_context.py
def inject_path_context(context: dict) -> dict:
    """Inject repository path information into command context."""
    resolver = PathResolver()
    repo_root = resolver.get_repo_root()
    
    context['REPO_ROOT'] = str(repo_root) if repo_root else os.getcwd()
    context['path_resolver'] = resolver
    return context
```

## Context for Next Phase
Phase 4 will update individual slash commands to use the injected path context for their file operations.