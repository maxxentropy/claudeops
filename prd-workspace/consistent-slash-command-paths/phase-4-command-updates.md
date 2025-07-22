# Phase 4: Command Updates

## Objective
Update all slash commands to use repository-relative paths for their outputs, ensuring consistent file locations regardless of where Claude Code is invoked.

## Dependencies
- Required from Phase 1-3: Complete path resolution infrastructure
- Existing slash command implementations

## Deliverables
- [ ] Update `/prd` command to save to `${REPO_ROOT}/docs/prds/`
- [ ] Update `/prdq` command to save to `${REPO_ROOT}/docs/prds/`
- [ ] Update all `/prd-*` commands to use `${REPO_ROOT}/.claude/prd-workspace/`
- [ ] Update generation commands to use repository-relative paths
- [ ] Update any other commands that write files
- [ ] Maintain backward compatibility where needed

## Success Criteria
- [ ] All PRDs save to consistent location
- [ ] Workspaces created in consistent location
- [ ] Commands work from any subdirectory
- [ ] Clear error messages when paths can't be resolved
- [ ] No breaking changes for existing workflows

## Commands to Update

### PRD Commands
1. `/prd` - Save to `${REPO_ROOT}/docs/prds/`
2. `/prdq` - Save to `${REPO_ROOT}/docs/prds/`
3. `/prd-decompose` - Create workspace at `${REPO_ROOT}/.claude/prd-workspace/`
4. `/prd-implement` - Use workspace at `${REPO_ROOT}/.claude/prd-workspace/`
5. `/prd-analyze` - Read from `${REPO_ROOT}/docs/prds/`
6. `/prd-integrate` - Work with `${REPO_ROOT}/.claude/prd-workspace/`
7. `/prd-preview` - Read from `${REPO_ROOT}/docs/prds/`
8. `/prd-progress` - Read workspace from `${REPO_ROOT}/.claude/prd-workspace/`

### Other Generation Commands
- Check for any other commands that generate files
- Update them to use repository-relative paths

## Implementation Pattern

For each command:
```python
# Before
output_path = "docs/prds/new-prd.md"

# After
output_path = context['path_resolver'].resolve_path("docs/prds/new-prd.md")
```

Or in command markdown:
```markdown
# Before
Save to: docs/prds/${slug}.md

# After
Save to: ${REPO_ROOT}/docs/prds/${slug}.md
```

## Testing Checklist
- [ ] Test from repository root
- [ ] Test from nested subdirectory
- [ ] Test from outside git repository
- [ ] Test with CLAUDE_OUTPUT_ROOT set
- [ ] Test with symlinked directories

## Context for Next Phase
Phase 5 will add comprehensive tests and update documentation to reflect the new path behavior.