# /prd-preview - Preview PRD Integration Changes

🎯 **COMMAND**: /prd-preview | 📋 **WORKFLOW**: preview - Preview PRD Integration Changes | 👤 **PERSONAS**: Software Architect + Devops Architect

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#DEVOPS_ARCHITECT -->

Preview what changes would be made if PRD sandbox results were integrated into the target repository.

## Purpose

Shows a dry-run of the integration process, allowing review before actual file changes:
- Lists all files that would be created/modified
- Shows file mappings from sandbox to repository
- Detects and reports potential conflicts
- Provides integration statistics

## Workflow

1. **Load Integration Context**:
   - Read from `.claude/prd-workspace/[project]/integration/mapping.json` (repository-relative)
   - Scan sandbox directory for all files
   - Detect current repository context

2. **Analyze Changes**:
   ```
   PRD Integration Preview: user-auth-system
   Repository: ~/projects/my-app
   
   Files to be created (12):
   ✓ sandbox/src/auth/login.js → src/auth/login.js
   ✓ sandbox/src/auth/register.js → src/auth/register.js
   ✓ sandbox/tests/auth.test.js → tests/auth.test.js
   
   Files to be modified (3):
   ⚠ sandbox/src/index.js → src/index.js (conflict detected)
   ✓ sandbox/package.json → package.json (dependencies added)
   ✓ sandbox/docs/auth.md → docs/auth.md
   
   New directories (2):
   ✓ src/auth/
   ✓ tests/auth/
   ```

3. **Conflict Detection**:
   ```
   Conflicts found (1):
   
   src/index.js:
   - Existing file has uncommitted changes
   - Integration would modify lines 45-67
   - Manual merge required
   
   Resolution options:
   1. Commit current changes first
   2. Use --force flag to overwrite
   3. Use /prd-integrate --interactive for manual merge
   ```

4. **Integration Summary**:
   ```
   Integration Summary:
   - Total files: 15
   - New files: 12
   - Modified files: 3
   - Conflicts: 1
   - Estimated changes: +1,245 lines
   
   Dependencies to add:
   - bcrypt: ^5.1.0
   - jsonwebtoken: ^9.0.0
   
   Commands:
   /prd-integrate user-auth-system    # Apply all changes
   /prd-integrate user-auth-system --phase 2    # Apply only phase 2
   ```

## Example Usage

```bash
/prd-preview parallel-execution-system

> Analyzing sandbox contents...
> Detecting repository: ~/.claude
> 
> Files to be created (8):
> ✓ sandbox/commands/workflow/prd-parallel.md → commands/workflow/prd-parallel.md
> ✓ sandbox/lib/dependency-graph.js → lib/dependency-graph.js
> ✓ sandbox/lib/parallel-orchestrator.js → lib/parallel-orchestrator.js
> 
> No conflicts detected.
> Safe to integrate with: /prd-integrate parallel-execution-system
```

## Options

- `--verbose`: Show full file diffs
- `--phase N`: Preview only specific phase changes
- `--json`: Output in JSON format for tooling

## Path Resolution:
- This command automatically uses repository-relative paths
- All paths resolve to the repository root when in a git repository
- Falls back to current directory when not in a repository
- Set `CLAUDE_OUTPUT_ROOT` environment variable to override

## Safety Features

- Never modifies actual files (preview only)
- Detects uncommitted changes in target files
- Warns about overwriting existing files
- Shows exact line numbers for conflicts
- Respects .gitignore patterns

This command ensures you know exactly what will happen before integrating PRD results.