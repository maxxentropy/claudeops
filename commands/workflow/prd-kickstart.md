# /prd-kickstart - Auto-Generate Implementation Phases from PRD

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#PRODUCT_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->

Take a PRD (from `/prdq` or manual) and automatically create a complete phase-based implementation plan optimized for context windows:

## Workflow:

1. **Load PRD Source**:
   - If given slug: Load from `docs/prds/[slug].md`  
   - If no arg: Find most recent PRD in `docs/prds/`
   - Parse PRD content for requirements analysis

2. **Analyze Context Window Needs**:
   - Estimate complexity of each component
   - Calculate dependencies between features  
   - Identify shared infrastructure needs
   - Map integration points

3. **Generate Optimal Phases** (Auto-sizing for context):
   - **Phase 1**: Always foundation/infrastructure (1-2 hrs max)
   - **Phase 2-N**: Feature components (1.5 hrs max each)
   - **Final Phase**: Integration and verification
   - Each phase must fit comfortably in context window

4. **Create Complete Workspace**:
   ```
   .claude/prd-workspace/[feature-slug]/
   ├── prd-original.md          # Copy of source PRD
   ├── prd-tracker.md           # Generated from template
   ├── phase-1-foundation.md    # Auto-generated phase spec
   ├── phase-2-component.md     # Auto-generated phase spec
   ├── phase-N-integration.md   # Final integration phase
   └── artifacts/               # Ready for outputs
       ├── phase-1/
       ├── phase-2/
       └── phase-N/
   ```

5. **Smart Phase Design**:
   ```markdown
   # Example Auto-Generation for "User Authentication System"
   
   Phase 1: Database Schema & Models (1.5 hrs)
   - User table, auth tokens, session management
   - Basic CRUD operations, no UI yet
   - Foundation for all auth features
   
   Phase 2: Core Auth Logic (2 hrs) 
   - Login/logout/registration functions
   - Password hashing, JWT tokens
   - Depends on: Phase 1 models
   
   Phase 3: API Endpoints (1 hr)
   - REST endpoints for auth operations
   - Input validation, error handling
   - Depends on: Phase 1 & 2
   
   Phase 4: Frontend Integration (1.5 hrs)
   - Login forms, auth guards, state management
   - Depends on: Phase 3 endpoints
   
   Phase 5: Testing & Security Hardening (1 hr)
   - Comprehensive tests, security review
   - Depends on: All previous phases
   ```

6. **Generate Execution Plan**:
   ```
   PRD: User Authentication System
   ✓ Workspace created: .claude/prd-workspace/user-auth/
   ✓ 5 phases generated (8 hours total estimated)
   
   Ready to implement:
   → /prd-implement user-auth phase-1
   
   Full sequence:
   /prd-implement user-auth phase-1  # Foundation
   /prd-implement user-auth phase-2  # Core Logic  
   /prd-implement user-auth phase-3  # API Layer
   /prd-implement user-auth phase-4  # Frontend
   /prd-implement user-auth phase-5  # Testing
   
   Progress tracking: .claude/prd-workspace/user-auth/prd-tracker.md
   ```

## Key Features:

- **Context-Optimized**: Each phase sized for comfortable context window
- **Dependency-Aware**: Later phases explicitly reference earlier outputs
- **Progress Tracking**: Full visibility into completion status
- **Resumable**: Can pause/resume at any phase boundary
- **Team-Friendly**: Multiple developers can work in parallel once dependencies met

## Integration with Existing System:

- Uses existing `/prd-implement` for execution
- Leverages existing tracker templates  
- Compatible with current PRD storage structure
- Works with both `/prdq` quick PRDs and full `/prd` documents

## Example Usage:
```bash
# Create PRD first
/prdq implement user dashboard with real-time updates

# Auto-generate phases
/prd-kickstart user-dashboard

# Start implementing 
/prd-implement user-dashboard phase-1
```

This bridges the gap between PRD creation and implementation, ensuring no context is lost and progress is always tracked.
