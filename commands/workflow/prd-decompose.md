# /prd-decompose - Break PRD into Implementable Phases

🎯 **COMMAND**: /prd-decompose | 📋 **WORKFLOW**: decompose - Break PRD into Implementable Phases | 👤 **PERSONAS**: Software Architect + Product Engineer

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#PRODUCT_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->

Transform PRDs into tracked, phased implementations:

## Workflow:

1. **Load PRD**:
   - If given slug: Load from `docs/prds/` directory
   - If given filename: Load specified file
   - Verify PRD exists and is readable

2. **Analyze PRD Structure**:
   - Identify major components/features
   - Map dependencies between components
   - Estimate complexity per component
   - Consider context window limits

2. **Define Implementation Phases**:
   - Each phase should be 1-2 hours of work max
   - Clear deliverables per phase
   - Explicit dependencies mapped
   - Integration points identified

3. **Create Tracking Structure**:
```markdown
.claude/prd-workspace/[feature-slug]/
├── prd-original.md          # Copy of original PRD
├── prd-tracker.md           # Overall progress tracking
├── phase-1-foundation.md    # Detailed phase spec
├── phase-2-component.md     # Next phase spec
└── artifacts/               # Output from each phase
    ├── phase-1/
    └── phase-2/
```

Note: Original PRD remains in `docs/prds/`, workspace in `.claude/`

4. **Phase Specification Template**:
```markdown
# Phase [N]: [Name]

## Objective
[Single clear goal for this phase]

## Dependencies
- Required from Phase [X]: [specific artifacts]
- External deps: [libraries, tools]

## Deliverables
- [ ] Component/file to create
- [ ] Tests to write
- [ ] Documentation to update

## Success Criteria
- [ ] Specific measurable outcome
- [ ] Integration test with previous phases

## Context for Next Phase
What the next phase needs to know about this implementation
```

5. **Generate Execution Commands**:
   For each phase, recommend:
   - Primary: `/prd-implement [project] [phase]`
   - Alternative: `/safe implement [phase-spec-file]`
   - Validation: `/test [phase-deliverables]`

## Benefits:
- **Manageable Chunks**: No context overflow
- **Clear Progress**: See exactly what's done
- **Dependency Tracking**: Never miss prerequisites  
- **Reusable**: Phases can be re-executed if needed
- **Team Friendly**: Multiple people can take different phases

## Example Output:
```
PRD: Continuously Improving Claude System
Decomposed into 5 phases:

Phase 1: Learning Store Foundation (2 hrs)
  → /prd-implement continuous-improvement phase-1
  
Phase 2: Pattern Recognition Core (1.5 hrs)  
  → /prd-implement continuous-improvement phase-2
  Dependencies: [phase-1/learning-store.js]

Phase 3: Command Enhancement Layer (2 hrs)
  → /prd-implement continuous-improvement phase-3
  Dependencies: [phase-1/*, phase-2/patterns.js]
  
[Continue...]
```

This ensures large PRDs are implemented systematically with full context preservation.

## Path Resolution:
- This command automatically uses repository-relative paths
- PRDs are loaded from `docs/prds/` at repository root
- Workspace created at `.claude/prd-workspace/` at repository root
- If not in a git repository, falls back to current directory
- Set `CLAUDE_OUTPUT_ROOT` environment variable to override

## Implementation Note:
When implementing this command, always use the path resolution utilities to ensure consistent paths:

```python
# Import path resolution utilities
import sys
import os
sys.path.insert(0, os.path.expanduser('~/.claude'))
from system.utils import path_resolver

# Load PRD from proper location
if feature_slug:
    # Find PRD by slug in the prds directory
    prds_dir = path_resolver.resolve('prds')
    prd_files = list(prds_dir.glob(f"*-{feature_slug}.md"))
    if prd_files:
        prd_path = prd_files[0]  # Use most recent if multiple
else:
    # Direct file path provided
    prd_path = Path(filename).resolve()

# Create workspace for the project
workspace_path = path_resolver.get_workspace_path(feature_slug)
workspace_path.mkdir(parents=True, exist_ok=True)

# Copy PRD to workspace
import shutil
shutil.copy2(prd_path, workspace_path / "prd-original.md")

# Create phase files
for i, phase in enumerate(phases, 1):
    phase_path = workspace_path / f"phase-{i}-{phase['name']}.md"
    phase_path.write_text(phase_content)

# Create tracker
tracker_path = workspace_path / "prd-tracker.md"
tracker_path.write_text(tracker_content)

# Format output message
output_paths = {
    "PRD loaded from": prd_path,
    "Workspace created": workspace_path,
    "Tracker created": tracker_path
}
print(path_resolver.format_output_message(output_paths))
```

**Important**: Never hardcode paths like `docs/prds/` or `.claude/prd-workspace/`. Always use the path resolver to ensure paths work correctly from any directory.