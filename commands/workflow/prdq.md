# /prdq - Quick Product Requirements (You & Claude)

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
   - Save to: `docs/prds/[filename]`
   - Create workspace: `.claude/prd-workspace/[feature-slug]/`
   - Update PRD index: `docs/prds/index.md`

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