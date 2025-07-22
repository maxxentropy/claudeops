# Path Resolution Quick Reference

## For Users

### Quick Setup
```bash
# Option 1: Use defaults (recommended)
# Just run commands from anywhere in your repo!

# Option 2: Force a specific output directory
export CLAUDE_OUTPUT_ROOT=/path/to/project

# Option 3: Customize paths for your project
echo '{
  "prds": "specs",
  "tests": "test",
  "lib": "src"
}' > .claude-paths.json
```

### Common Commands & Output Locations
| Command | Output Location |
|---------|----------------|
| `/prd "Feature"` | `{repo}/docs/prds/YYYY-MM-DD-feature.md` |
| `/prd-implement` | `{repo}/.claude/prd-workspace/feature/` |
| `/create-docs` | `{repo}/docs/` |
| `/api-crud User` | `{repo}/lib/controllers/UserController.cs` |
| `/tdd "test"` | `{repo}/tests/test_*.py` |

## For Developers

### Using Path Resolution in Commands

```python
# Import the utilities
from system.utils import (
    get_prd_path,
    get_workspace_path,
    resolve,
    ensure_directory,
    format_output_message
)

# Get PRD path
prd_path = get_prd_path('my-feature')  # {repo}/docs/prds/2025-01-22-my-feature.md

# Get workspace path
workspace = get_workspace_path('my-feature')  # {repo}/.claude/prd-workspace/my-feature/

# Resolve custom paths
controller_path = resolve('lib', 'controllers/UserController.cs')
test_path = resolve('tests', 'test_user.py')

# Ensure directory exists
docs_dir = ensure_directory('docs')  # Creates {repo}/docs/ if needed

# Format output for users
paths = {
    'PRD created': prd_path,
    'Workspace created': workspace
}
output = format_output_message(paths)
print(output)
# ✓ PRD created: docs/prds/2025-01-22-my-feature.md
# ✓ Workspace created: .claude/prd-workspace/my-feature
```

### Path Types
- `prds` - PRD documents
- `prd_workspace` - PRD workspaces
- `docs` - Documentation
- `tests` - Test files
- `lib` - Library/source code
- `commands` - Custom commands
- `hooks` - Hook scripts
- `system` - System utilities

### Testing Path Resolution
```python
# Clear any cached values
from system.utils import clear_cache
clear_cache()

# Test with environment override
import os
os.environ['CLAUDE_OUTPUT_ROOT'] = '/tmp/test'
path = resolve('prds')  # Will use /tmp/test/docs/prds/
```

### Debugging
```python
# Check current repo root
from system.utils import find_repo_root
print(f"Repo root: {find_repo_root()}")

# Check if in repo
from system.utils import is_in_repo
print(f"In repo: {is_in_repo()}")

# Check resolved path
from system.utils import resolve_path
print(f"PRDs path: {resolve_path('docs/prds')}")
```