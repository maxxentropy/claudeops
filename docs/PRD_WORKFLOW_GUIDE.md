# PRD Decomposition & Implementation Workflow

## Overview

This system breaks down large PRDs into context-window-optimized phases that can be implemented step-by-step using existing slash commands. It ensures no context is lost, progress is tracked, and work can be resumed across sessions.

## Complete Workflow

### Step 1: Create PRD
```bash
# Quick 1-page PRD
ccprdq "implement user dashboard with real-time updates"

# Creates: docs/prds/YYYY-MM-DD-user-dashboard.md
```

### Step 2: Auto-Generate Implementation Phases  
```bash
# Break PRD into optimal phases
cckick user-dashboard

# Creates workspace: .claude/prd-workspace/user-dashboard/
# - prd-original.md (copy of PRD)
# - prd-tracker.md (progress tracking)  
# - phase-1-foundation.md (phase specs)
# - phase-2-component.md
# - phase-N-integration.md
# - artifacts/ (directory for outputs)
```

### Step 3: Implement Phases Step-by-Step
```bash
# Start with foundation phase
ccphase user-dashboard phase-1

# Continue with each subsequent phase
ccphase user-dashboard phase-2
ccphase user-dashboard phase-3
# ... etc
```

### Step 4: Review & Integrate Results
```bash
# Preview what would be integrated
ccpreview user-dashboard

# Integrate sandbox results into your repository
ccintegrate user-dashboard

# If issues arise, rollback changes
ccrollback user-dashboard
```

### Step 5: Monitor Progress
```bash
# See all projects
cctrack

# See specific project detail  
cctrack user-dashboard

# Resume work where you left off
cctrack user-dashboard resume
```

## Example: Real Implementation

### 1. Create PRD for Authentication System
```bash
ccprdq "implement secure user authentication with JWT tokens, password reset, and session management"
```

### 2. Auto-Generate 5 Phases
```bash
cckick user-auth

# Output:
# ✓ 5 phases generated (7.5 hours estimated)
# Phase 1: Database Schema & Models (1.5h)
# Phase 2: Core Auth Logic (2h) 
# Phase 3: API Endpoints (1h)
# Phase 4: Frontend Integration (2h)
# Phase 5: Testing & Security (1h)
```

### 3. Implement Each Phase
```bash
# Foundation first
ccphase user-auth phase-1
# Builds: User table, auth models, migrations

# Core logic 
ccphase user-auth phase-2  
# Builds: Login/logout functions, JWT handling
# References: Phase 1 models automatically

# API layer
ccphase user-auth phase-3
# Builds: REST endpoints
# References: Phase 1 models + Phase 2 logic

# Frontend
ccphase user-auth phase-4
# Builds: Login forms, auth guards
# References: Phase 3 endpoints

# Final testing
ccphase user-auth phase-5
# Tests: All previous phases together
```

### 4. Track Progress Throughout
```bash
cctrack user-auth

# Shows:
# Phase 1: ✓ COMPLETE (1.2h actual)
# Phase 2: ✓ COMPLETE (1.8h actual)  
# Phase 3: → IN_PROGRESS (30 mins elapsed)
# Phase 4: ⏳ WAITING (depends on Phase 3)
# Phase 5: ⏳ WAITING (depends on Phase 4)
```

## Key Benefits

### 🧠 **Context Window Optimization**
- Each phase sized to fit comfortably in context
- Previous phases automatically loaded when needed
- No information loss between implementations

### 📊 **Full Progress Tracking**  
- See exactly what's been built
- Resume work from any point
- Track time estimates vs actual
- Identify bottlenecks early

### 🔗 **Dependency Management**
- Later phases explicitly reference earlier outputs
- Clear prerequisites for each phase
- No duplicate work or missing dependencies

### 👥 **Team Collaboration**
- Multiple people can work on independent phases
- Clear handoffs between phases
- Shared progress visibility

### 🛡️ **Safety & Quality**
- Each phase uses existing verified slash commands
- Built-in testing and verification
- Sandbox isolation prevents accidental changes
- Preview before integration
- Full rollback capability if issues found

### 🏗️ **Sandbox Implementation**
- All work happens in isolated sandbox directory
- Repository remains untouched during development
- Explicit integration step with preview
- Works with any repository structure

## File Structure

```
docs/prds/                          # PRD storage
├── 2025-01-20-user-auth.md        # Original PRD
├── 2025-01-21-dashboard.md        # Another PRD  
└── index.md                       # PRD catalog

.claude/prd-workspace/              # Active implementations
├── user-auth/                     # Project workspace
│   ├── prd-original.md           # Copy of PRD
│   ├── prd-tracker.md            # Progress tracking
│   ├── phase-1-foundation.md     # Phase specifications
│   ├── phase-2-core-logic.md     
│   ├── phase-3-api-layer.md
│   ├── phase-4-frontend.md
│   ├── phase-5-testing.md
│   ├── sandbox/                  # ISOLATED IMPLEMENTATION
│   │   ├── src/                  # Source code
│   │   ├── tests/               # Test files
│   │   ├── commands/            # New commands
│   │   └── docs/                # Documentation
│   ├── artifacts/                # Phase reference outputs
│   │   ├── phase-1/              # Database, models
│   │   ├── phase-2/              # Auth logic
│   │   ├── phase-3/              # API endpoints
│   │   ├── phase-4/              # Frontend code
│   │   └── phase-5/              # Tests, docs
│   ├── integration/              # Integration control
│   │   ├── mapping.json          # File destinations
│   │   └── conflicts.log         # Conflict tracking
│   └── backups/                  # Rollback points
│       └── 2025-01-21-143052/    # Timestamped backups
└── dashboard/                    # Another project
```

## Shell Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `ccprdq` | Create quick PRD | `ccprdq "implement user notifications"` |
| `cckick` | Generate phases | `cckick user-notifications` |
| `ccphase` | Implement phase | `ccphase user-notifications phase-1` |
| `ccpreview` | Preview integration | `ccpreview user-notifications` |
| `ccintegrate` | Apply to repository | `ccintegrate user-notifications` |
| `ccrollback` | Undo integration | `ccrollback user-notifications` |
| `cctrack` | Monitor progress | `cctrack user-notifications` |
| `cchelp` | Show all commands | `cchelp` |

## Advanced Usage

### Parallel Development
```bash
# Team member A works on Phase 1
ccphase project-x phase-1

# Once Phase 1 complete, member B can start Phase 2
cctrack project-x  # Shows Phase 1 done
ccphase project-x phase-2
```

### Resume After Break
```bash
# See where you left off
cctrack

# Resume specific project
cctrack project-x resume
# Automatically loads context and continues current phase
```

### Handle Blockers
```bash
# If external dependency blocks current phase
cctrack project-x
# Shows: Phase 3 BLOCKED (waiting for API key)

# Work on independent Phase 4 in parallel
ccphase project-x phase-4  # If no Phase 3 dependency
```

This system ensures complex features are built systematically, with full context preservation and team coordination.
