# /path-info - Display Path Resolution Information

🎯 **COMMAND**: /path-info | 📋 **WORKFLOW**: Information Display | 👤 **PERSONAS**: Default

Display current path resolution settings and information about where files will be created.

## Purpose
This command helps users understand:
- Current repository root detection
- Active path overrides
- Where slash commands will create files
- Environment variable settings

## Implementation

```python
from system.utils import (
    find_repo_root,
    resolve,
    is_in_repo,
    PathResolver
)
import os
from pathlib import Path

# Get current settings
repo_root = find_repo_root()
current_dir = Path.cwd()
env_override = os.environ.get('CLAUDE_OUTPUT_ROOT')

# Display information
print("=== Path Resolution Information ===\n")

# Repository Detection
if repo_root:
    print(f"✓ Repository Root: {repo_root}")
    print(f"  Current Directory: {current_dir}")
    try:
        rel_path = current_dir.relative_to(repo_root)
        print(f"  Relative Position: {rel_path}")
    except ValueError:
        print("  ⚠️  Current directory is outside repository")
else:
    print("✗ Not in a git repository")
    print(f"  Current Directory: {current_dir}")
    print("  Files will be created relative to current directory")

# Environment Override
print(f"\nEnvironment Override:")
if env_override:
    print(f"  ✓ CLAUDE_OUTPUT_ROOT = {env_override}")
    if Path(env_override).exists():
        print("    Status: Valid directory")
    else:
        print("    Status: ⚠️  Directory does not exist")
else:
    print("  ✗ CLAUDE_OUTPUT_ROOT not set")

# Project Overrides
print("\nProject-Specific Overrides:")
config_path = Path(repo_root) / '.claude-paths.json' if repo_root else Path('.claude-paths.json')
if config_path.exists():
    print(f"  ✓ Found: {config_path}")
    try:
        import json
        with open(config_path) as f:
            overrides = json.load(f)
        for path_type, override in overrides.items():
            if not path_type.startswith('_'):
                print(f"    {path_type}: {override}")
    except Exception as e:
        print(f"    ⚠️  Error loading: {e}")
else:
    print(f"  ✗ Not found: {config_path}")
    print("    Create .claude-paths.json to customize paths")

# Standard Paths
print("\nStandard Output Paths:")
resolver = PathResolver()
for path_type, default_path in resolver.DEFAULT_PATHS.items():
    resolved = resolve(path_type)
    default_info = f" (default: {default_path})"
    # Check if this path is overridden
    is_overridden = path_type in resolver._path_overrides
    override_marker = " [OVERRIDDEN]" if is_overridden else ""
    
    print(f"  {path_type}: {resolved}{override_marker}")
    print(f"    Default: {default_path}")
    if resolved.exists():
        print(f"    Status: ✓ Exists")
    else:
        print(f"    Status: ✗ Does not exist")

# Usage Examples
print("\nExample Usage:")
print("  Set custom output root:")
print("    export CLAUDE_OUTPUT_ROOT=/path/to/project")
print("\n  Create PRD from any directory:")
print("    cd src/components/widget")
print("    claude '/prd widget-enhancement'")
print(f"\n  PRD will be saved to: {resolve('prds', '2025-01-22-widget-enhancement.md')}")
```

## Features

1. **Repository Detection**
   - Shows detected git repository root
   - Displays current working directory
   - Shows relative position within repository

2. **Environment Variables**
   - Checks CLAUDE_OUTPUT_ROOT setting
   - Validates if override directory exists

3. **Path Mappings**
   - Lists all standard path types
   - Shows where each type resolves to
   - Indicates if directories exist

4. **Usage Examples**
   - How to set environment overrides
   - Examples of path resolution in action

## Output Example

```
=== Path Resolution Information ===

✓ Repository Root: /Users/sean/.claude
  Current Directory: /Users/sean/.claude/commands/core
  Relative Position: commands/core

Environment Override:
  ✗ CLAUDE_OUTPUT_ROOT not set

Standard Output Paths:
  prds: /Users/sean/.claude/docs/prds
    Status: ✓ Exists
  prd_workspace: /Users/sean/.claude/.claude/prd-workspace
    Status: ✓ Exists
  docs: /Users/sean/.claude/docs
    Status: ✓ Exists
  tests: /Users/sean/.claude/tests
    Status: ✓ Exists
  lib: /Users/sean/.claude/lib
    Status: ✓ Exists

Example Usage:
  Set custom output root:
    export CLAUDE_OUTPUT_ROOT=/path/to/project

  Create PRD from any directory:
    cd src/components/widget
    claude '/prd widget-enhancement'

  PRD will be saved to: /Users/sean/.claude/docs/prds/2025-01-22-widget-enhancement.md
```

This command provides transparency about where files will be created and helps users understand the path resolution system.