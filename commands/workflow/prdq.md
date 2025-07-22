# /prdq - Quick Product Requirements (You & Claude)

🎯 **COMMAND**: /prdq | 📋 **WORKFLOW**: Quick Product Requirements (You & Claude) | 👤 **PERSONAS**: Product Engineer + Software Architect

Embody these expert personas:
<!-- INCLUDE: system/personas.md#PRODUCT_ENGINEER -->
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->

Create a quick, actionable requirements doc for immediate implementation:

## Workflow:

1. **Gather Information**:
   - **Core Need**: What problem are we solving?
   - **Success Criteria**: How do we know when it's done?
   - **Constraints**: What limitations exist (time, tech, dependencies)?

2. **Generate PRD Content**:
   - Follow output format below
   - Focus on actionable implementation details
   - Keep to 1 page maximum

3. **Save PRD to Project**:
   - Create filename: `YYYY-MM-DD-[feature-slug].md`
   - Save to: `docs/prds/[filename]` (automatically resolves to repository root)
   - Create workspace: `.claude/prd-workspace/[feature-slug]/`
   - Update PRD index: `docs/prds/index.md`
   - Note: All paths are automatically resolved relative to repository root
   - If `CLAUDE_OUTPUT_ROOT` is set, it will be used as the base directory

## Output Format:
```markdown
## Quick Requirements: [Feature Name]

### Problem
[1-2 sentences on what we're solving]

### Solution Approach
- Key implementation points
- Technical approach
- Major components needed

### Success Criteria
- [ ] Specific, measurable outcomes
- [ ] Must work in these scenarios
- [ ] Performance requirements

### Out of Scope
- What we're NOT doing (important!)

### Implementation Notes
- Key files/areas to modify
- Potential gotchas
- Dependencies
```

## Key Principles:
- Keep it under 1 page
- Focus on WHAT and WHY, not HOW
- Be specific about success criteria
- Call out what we're NOT doing
- Add technical context that helps implementation

This is for quick alignment between us, not formal documentation.

## Path Resolution:
- This command uses repository-relative paths
- PRDs will be saved to the repository root's `docs/prds/` directory
- If not in a git repository, falls back to current directory
- Set `CLAUDE_OUTPUT_ROOT` environment variable to override

## Post-Creation Output:
After saving, display:
```
✓ PRD saved to: docs/prds/YYYY-MM-DD-[feature-slug].md
✓ Workspace created: .claude/prd-workspace/[feature-slug]/
✓ Added to PRD index

Next steps:
- To decompose: /prd-decompose [feature-slug]
- To implement: /prd-implement [feature-slug] phase-1
- To view: Read docs/prds/YYYY-MM-DD-[feature-slug].md
```

## Implementation Note:
When implementing this command, always use the path resolution utilities to ensure consistent paths:

```python
# Import path resolution utilities
import sys
import os
sys.path.insert(0, os.path.expanduser('~/.claude'))
from system.utils import path_resolver

# Get PRD path with automatic date prefix
prd_path = path_resolver.get_prd_path(feature_slug, date_prefix=True)

# Get workspace path  
workspace_path = path_resolver.get_workspace_path(feature_slug)

# Ensure directories exist
path_resolver.ensure_directory('prds')
path_resolver.ensure_directory('prd_workspace')

# Format output message with relative paths
output_paths = {
    "Quick PRD saved to": prd_path,
    "Workspace created": workspace_path
}
print(path_resolver.format_output_message(output_paths))
```

**Important**: Never hardcode paths like `docs/prds/`. Always use the path resolver to ensure paths work correctly from any directory.