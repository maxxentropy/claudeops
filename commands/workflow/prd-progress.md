# /prd-progress - Monitor and Resume PRD Implementation

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
