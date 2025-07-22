# Phase 3: Hook Infrastructure Updates

## Objective
Update the hook infrastructure to detect repository root and inject it into the command execution context, making it available to all slash commands.

## Dependencies
- **Required from Phase 1**: `system/utils/repo_detector.py`
- **Required from Phase 2**: `system/utils/path_resolver.py`
- Existing hook files: `combined_hook.sh`, `slash_command_validator.py`

## Deliverables

### 1. Enhanced Hook Script
**File**: Update `hooks/combined_hook.sh`

```bash
#!/bin/bash
# Combined hook that runs all UserPromptSubmit actions

# Detect repository root
REPO_ROOT=$(python3 -c "
import sys
sys.path.insert(0, '$HOME/.claude')
from system.utils.repo_detector import RepoDetector
detector = RepoDetector()
root = detector.get_repo_root_with_override()
print(root or '.')
")

# Export for child processes
export CLAUDE_REPO_ROOT="$REPO_ROOT"
export CLAUDE_CWD="$(pwd)"

# Rest of existing hook logic...
```

### 2. Hook Configuration Enhancement
**File**: Create `hooks/path_context_injector.py`

```python
class PathContextInjector:
    def inject_context(self, input_data):
        """Add path context to command execution"""
        # Detect repo root
        # Add to input_data context
        # Include resolver instance
        
    def get_path_variables(self):
        """Return dict of available path variables"""
        return {
            "REPO_ROOT": self.repo_root,
            "CWD": os.getcwd(),
            "HOME": os.path.expanduser("~"),
            "DATE": datetime.now().strftime("%Y-%m-%d")
        }
```

### 3. Command Context Protocol
Define how commands receive path context:

**Option A: Environment Variables**
- `CLAUDE_REPO_ROOT` - Repository root path
- `CLAUDE_CWD` - Original working directory
- `CLAUDE_PATH_MODE` - "repo" or "fallback"

**Option B: JSON Context**
Add to command input:
```json
{
  "prompt": "/prd My Feature",
  "pathContext": {
    "repoRoot": "/path/to/repo",
    "cwd": "/path/to/repo/subdir",
    "mode": "repo"
  }
}
```

### 4. Backward Compatibility
- Commands without path support continue working
- Gradual migration approach
- Feature flag for new behavior

### 5. Integration Tests
**File**: `tests/test_hook_integration.py`

Test scenarios:
- [ ] Hook sets environment variables correctly
- [ ] Context passed to Python hooks
- [ ] Commands can access path context
- [ ] Fallback behavior when not in repo
- [ ] Performance impact is minimal

## Success Criteria
- [ ] Repository root available to all commands
- [ ] No breaking changes to existing commands
- [ ] Hook execution time < 50ms overhead
- [ ] Clean error handling
- [ ] Works in all supported shells

## Implementation Notes

### Shell Compatibility
Test with:
- Bash
- Zsh
- Fish (may need separate script)
- PowerShell (Windows support)

### Performance Considerations
- Cache repo detection in shell session
- Lazy load Python modules
- Consider pure shell implementation for speed

### Error Handling
- If repo detection fails, continue with CWD
- Log errors to `~/.claude/logs/hooks.log`
- Never block command execution

### Security
- Validate paths before setting environment
- Prevent injection attacks in shell scripts
- Use proper quoting in all contexts

## Context for Next Phase
Phase 4 will update individual commands to:
- Read path context from environment/input
- Use PathResolver for all file operations
- Replace hardcoded paths with templates