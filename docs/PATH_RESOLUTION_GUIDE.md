# Path Resolution Guide for Claude Code

## Overview

Claude Code now includes an intelligent path resolution system that ensures all slash command outputs are saved to consistent, predictable locations regardless of where you invoke the `claude` command. This guide explains how the system works and how to configure it for your needs.

## Key Benefits

- **Consistency**: Files are always saved relative to your repository root, not your current working directory
- **Predictability**: Know exactly where your files will be created
- **Flexibility**: Override default paths for your project's specific structure
- **Portability**: Team members get the same file structure regardless of their working directory

## How It Works

### 1. Repository Detection

When you run a slash command, Claude Code automatically:
1. Searches for the nearest `.git` directory (traveling up the directory tree)
2. Uses that as the repository root for all path calculations
3. Falls back to the current directory if not in a git repository

### 2. Path Resolution

All paths are resolved relative to the detected repository root:
- `/prd` creates files in `{repo_root}/docs/prds/`
- Workspaces are created in `{repo_root}/.claude/prd-workspace/`
- Test files go to `{repo_root}/tests/`
- Library code goes to `{repo_root}/lib/`

### 3. Smart Fallbacks

If you're not in a git repository:
- Paths are resolved relative to your current working directory
- The same directory structure is maintained

## Default Path Mappings

| Path Type | Default Location | Used By |
|-----------|-----------------|---------|
| `prds` | `docs/prds` | `/prd`, `/prdq` commands |
| `prd_workspace` | `.claude/prd-workspace` | `/prd-implement`, `/prd-decompose`, etc. |
| `docs` | `docs` | `/create-docs` |
| `tests` | `tests` | `/tdd`, test generation |
| `lib` | `lib` | `/api-crud`, `/mobile-scaffold` |
| `commands` | `commands` | Custom command creation |
| `hooks` | `hooks` | Hook system |
| `system` | `system` | System utilities |

## Configuration Options

### 1. Environment Variable Override

Set `CLAUDE_OUTPUT_ROOT` to override the automatic detection:

```bash
# Force all outputs to a specific directory
export CLAUDE_OUTPUT_ROOT=/path/to/my/project

# Run Claude from anywhere, files still go to your project
cd /some/other/directory
claude /prd "New feature"  # Creates /path/to/my/project/docs/prds/new-feature.md
```

### 2. Project-Specific Overrides

Create a `.claude-paths.json` file in your repository root to customize paths:

```json
{
  "prds": "requirements/specifications",
  "prd_workspace": ".workspaces/prd",
  "docs": "documentation",
  "tests": "test_suite",
  "lib": "src"
}
```

With this configuration:
- PRDs will be saved to `{repo_root}/requirements/specifications/`
- Workspaces will be created in `{repo_root}/.workspaces/prd/`
- And so on...

### 3. Precedence Order

1. **Environment Variable** (`CLAUDE_OUTPUT_ROOT`) - Highest priority
2. **Project Overrides** (`.claude-paths.json`) - Medium priority
3. **Default Paths** - Lowest priority

## Examples

### Example 1: Working from a Subdirectory

```bash
# You're in a deeply nested directory
cd ~/projects/myapp/src/components/ui/buttons

# Run a PRD command
claude /prd "Enhanced button system"

# File is created at: ~/projects/myapp/docs/prds/2025-01-22-enhanced-button-system.md
# NOT at: ~/projects/myapp/src/components/ui/buttons/docs/prds/...
```

### Example 2: Using Environment Override

```bash
# Set a custom output root
export CLAUDE_OUTPUT_ROOT=~/claude-outputs

# Run commands from anywhere
cd /tmp
claude /prd "Test feature"

# File is created at: ~/claude-outputs/docs/prds/2025-01-22-test-feature.md
```

### Example 3: Project with Custom Structure

Create `.claude-paths.json`:
```json
{
  "prds": "specs",
  "lib": "source",
  "tests": "test"
}
```

Now:
```bash
claude /prd "Custom paths"        # Creates: {repo}/specs/2025-01-22-custom-paths.md
claude /api-crud User            # Creates: {repo}/source/controllers/UserController.cs
claude /tdd "user service"       # Creates: {repo}/test/test_user_service.py
```

## Viewing Current Configuration

To see your current path configuration, you can check:

1. **Repository Root**: Run `git rev-parse --show-toplevel`
2. **Environment Override**: Run `echo $CLAUDE_OUTPUT_ROOT`
3. **Project Overrides**: Check for `.claude-paths.json` in your repo root

## Troubleshooting

### Files Created in Unexpected Locations

1. **Check if you're in a git repository**: Run `git status`
2. **Check for environment override**: Run `echo $CLAUDE_OUTPUT_ROOT`
3. **Check for project overrides**: Look for `.claude-paths.json`

### Path Resolution Not Working

1. **Clear any caches**: Restart your Claude session
2. **Verify git repository**: Ensure `.git` directory exists
3. **Check permissions**: Ensure Claude can read the `.git` directory

### Submodules and Nested Repositories

- Claude uses the **nearest** `.git` directory
- In a submodule, files will be created relative to the submodule root
- Use `CLAUDE_OUTPUT_ROOT` to force a specific root if needed

## Best Practices

1. **Commit `.claude-paths.json`**: Share your path configuration with your team
2. **Use Relative Paths**: Always use relative paths in `.claude-paths.json`
3. **Document Custom Paths**: If you use custom paths, document them in your README
4. **Avoid Absolute Paths**: Don't use absolute paths in `.claude-paths.json` as they won't work for other team members

## Migration from Old Behavior

If you have existing files created with the old behavior (relative to current directory):

1. **No automatic migration**: Existing files stay where they are
2. **New files use new system**: All new files will use repository-relative paths
3. **Manual consolidation**: Move existing files to the new locations if desired

Example migration:
```bash
# Old location (created from src/ directory)
src/docs/prds/feature.md

# New location (repository-relative)
docs/prds/feature.md

# Move manually if needed
mv src/docs/prds/*.md docs/prds/
```

## Technical Details

The path resolution system consists of two main components:

1. **Repository Detector** (`system/utils/repo_detector.py`)
   - Finds git repository root
   - Handles environment variable override
   - Provides caching for performance

2. **Path Resolver** (`system/utils/path_resolver.py`)
   - Resolves paths based on type
   - Loads project overrides
   - Ensures directories exist

All slash commands use these utilities to ensure consistent behavior.