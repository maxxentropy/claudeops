## Quick Requirements: Consistent Slash Command Output Paths

### Problem
Slash commands currently save files relative to the working directory where Claude Code is launched (e.g., `docs/prds/` could end up in `/Users/sean/project1/docs/prds/` or `/Users/sean/project2/docs/prds/`), causing outputs to be scattered across the filesystem depending on where `claude` command is run.

### Solution Approach
- Create repository root detection utility that finds the nearest `.git` directory
- Implement path resolution service that converts relative paths to repository-relative paths
- Update all slash commands to use repository-relative paths for outputs
- Add fallback behavior for non-git directories (use current directory)
- Provide environment variable override for explicit path control

### Success Criteria
- [ ] PRDs always save to `{repo_root}/docs/prds/` regardless of current working directory
- [ ] Workspaces always created at `{repo_root}/.claude/prd-workspace/`
- [ ] All slash commands use consistent repository-relative paths
- [ ] Works correctly when Claude is invoked from any subdirectory
- [ ] Gracefully falls back to current directory when not in a git repo
- [ ] Environment variable `CLAUDE_OUTPUT_ROOT` can override detection

### Out of Scope
- Changing the existing directory structure or file naming conventions
- Modifying git configuration or creating new repositories
- Cross-repository file operations
- Network/remote repository operations

### Implementation Notes
- Add `system/utils/repo_detector.py` with git root detection logic
- Update hook infrastructure to inject repository root into command context
- Modify commands to use `${REPO_ROOT}` variable in paths
- Key commands to update: `/prd`, `/prdq`, `/prd-*`, all generation commands
- Test with nested git repos (submodules) - should use nearest parent
- Consider caching repo root detection for performance (invalidate on directory change)