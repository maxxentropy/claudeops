# /prd-progress - Monitor and Resume PRD Implementation

🎯 **COMMAND**: /prd-progress | 📋 **WORKFLOW**: progress - Monitor and Resume PRD Implementation | 👤 **PERSONAS**: Project Manager + Software Architect

Embody these expert personas:
<!-- INCLUDE: system/personas.md#PROJECT_MANAGER -->
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->

Monitor implementation progress and intelligently resume work on PRD phases:

## Workflow:

1. **Status Overview**:
   - Show all active PRD workspaces
   - Display phase completion status
   - Highlight current bottlenecks/blockers
   - Show estimated time remaining

2. **Detailed Project View** (when given project slug):
   ```
   PRD: User Authentication System
   Status: IN_PROGRESS (Phase 2 of 5)
   Started: 2025-01-20
   Estimated Completion: 2025-01-22 (6 hours remaining)
   
   Phase Progress:
   ✓ Phase 1: Database Schema (COMPLETE - 1.2 hrs)
     └── Artifacts: models.js, schema.sql, migrations/
   
   → Phase 2: Core Auth Logic (IN_PROGRESS - 45 mins elapsed)
     └── Next: Complete JWT token implementation
   
   ⏳ Phase 3: API Endpoints (WAITING - Depends on Phase 2)
   ⏳ Phase 4: Frontend Integration (WAITING - Depends on Phase 3)  
   ⏳ Phase 5: Testing & Hardening (WAITING - Depends on Phase 4)
   
   Blockers: None
   Team: Sean (all phases)
   ```

3. **Smart Resume Suggestions**:
   ```
   Ready to continue:
   → /prd-implement user-auth phase-2
   
   Context loaded: Phase 1 outputs + current progress
   Next deliverable: JWT service implementation
   ```

4. **Cross-Project Dependencies**:
   - Identify shared components across PRDs
   - Suggest parallel work opportunities
   - Flag dependency conflicts

## Commands:

### View All Projects
```bash
/prd-progress
# Shows summary of all active implementations
```

### View Specific Project  
```bash
/prd-progress user-auth
# Shows detailed status for user-auth project
```

### Resume Work
```bash
/prd-progress user-auth resume
# Loads context and resumes at current phase
```

## Example Output:

### All Projects Summary:
```
Active PRD Implementations (3):

📊 user-auth          Phase 2/5  40% complete    6h remaining
🔄 payment-gateway    Phase 1/4  25% complete    9h remaining  
⚠️  real-time-dash     Phase 3/6  BLOCKED        dependency wait

Completion this week: user-auth (Tuesday)
Ready to resume: user-auth (phase-2), payment-gateway (phase-1)
```

### Detailed Project View:
```
🔍 PRD: Real-Time Dashboard System
📅 Started: Jan 18  Target: Jan 25  
📈 Progress: 50% (3 of 6 phases complete)

Recent Activity:
✓ Jan 18: Phase 1 complete (WebSocket infrastructure)
✓ Jan 19: Phase 2 complete (Data pipeline) 
✓ Jan 20: Phase 3 complete (Frontend components)

🔄 Currently: Phase 4 - Real-time Integration
   Started: 2 hours ago
   Progress: Connecting components, 60% done
   
⚠️ Blocker: External API rate limits affecting testing
   Resolution: Waiting for API key upgrade (ETA: tomorrow)

Next Steps:
1. Complete Phase 4 integration testing
2. Begin Phase 5 (Performance optimization)  
3. Final Phase 6 (Deployment & monitoring)

→ /prd-implement real-time-dash phase-4  # Resume current
```

## Integration Benefits:

- **Never lose context** between sessions
- **Clear visibility** into progress across all projects
- **Smart resumption** with proper context loading
- **Dependency tracking** prevents conflicts
- **Time estimation** helps with planning
- **Team coordination** shows who's working on what

## Auto-Generated Insights:

- **Velocity tracking**: "Phase 2 typically takes 1.5x estimated time"
- **Pattern recognition**: "API phases often blocked by external dependencies"
- **Resource optimization**: "Consider parallel work on independent phases"
- **Risk identification**: "Phase 4 critical path - monitor closely"

This ensures complex PRD implementations stay on track and can be resumed efficiently across multiple sessions and team members.

## Path Resolution:
- This command automatically uses repository-relative paths
- PRD workspaces are scanned from `.claude/prd-workspace/` at repository root
- Progress tracking is based on workspace tracker files
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

# List all PRD workspaces
workspace_root = path_resolver.resolve('prd_workspace')

if not workspace_root.exists():
    print("No PRD workspaces found")
    return

# Find all active projects
active_projects = []
for project_dir in workspace_root.iterdir():
    if project_dir.is_dir() and (project_dir / "prd-tracker.md").exists():
        active_projects.append(project_dir.name)

# For specific project progress
if project_name:
    workspace_path = path_resolver.get_workspace_path(project_name)
    
    if not workspace_path.exists():
        print(f"No workspace found for project: {project_name}")
        return
    
    # Load tracker and phase files
    tracker_path = workspace_path / "prd-tracker.md"
    prd_path = workspace_path / "prd-original.md"
    
    # Find phase files and their status
    phase_files = sorted(workspace_path.glob("phase-*.md"))
    
    # Check artifacts directory for completed phases
    artifacts_dir = workspace_path / "artifacts"
    
    # Load sandbox for in-progress work
    sandbox_dir = workspace_path / "sandbox"

# Format output with relative paths
output_paths = {
    "Workspace root": workspace_root,
    f"Active projects ({len(active_projects)})": ", ".join(active_projects)
}
print(path_resolver.format_output_message(output_paths))

# For resume functionality
if resume:
    print(f"Loading context from: {workspace_path}")
    print(f"Next phase to implement: phase-{next_phase_num}")
    print(f"Run: /prd-implement {project_name} phase-{next_phase_num}")
```

**Important**: Never hardcode paths like `.claude/prd-workspace/`. Always use the path resolver to ensure paths work correctly from any directory.
