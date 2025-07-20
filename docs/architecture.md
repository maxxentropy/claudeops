# Claude Slash Command System Architecture

## Overview

The Claude slash command system is designed to embed complete workflows directly into commands, leveraging Claude's natural behavior of prioritizing immediate commands over background context.

## Directory Structure

```
.claude/
├── commands/           # Executable slash commands
├── system/            # Supporting components
├── config/            # Configuration files
├── data/              # User-generated data
├── cache/             # Temporary data
└── docs/              # Documentation
```

## Component Architecture

### 1. Commands (`/commands`)

Commands are the primary interface for users. They are organized by purpose:

- **core/** - Essential daily commands
- **workflow/** - Multi-step processes
- **development/** - Programming workflows
- **generation/** - Code/content generation

Each command is a self-contained workflow that:
1. References expert personas for decision-making
2. Includes reusable principles via INCLUDE tags
3. Defines a complete, verifiable workflow
4. Cannot skip steps due to embedded structure

### 2. System Components (`/system`)

Supporting files that commands reference:

- **personas.md** - Expert mindsets (Senior Test Engineer, Software Architect, etc.)
- **principles.md** - Reusable workflow components (VERIFICATION_STEPS, SECURITY_RULES, etc.)
- **templates/** - Templates for PRDs, commands, etc.
- **scripts/** - Utility scripts for usage tracking and analysis

### 3. Configuration (`/config`)

User and system configuration:

- **CLAUDE.md** - User instructions and preferences
- **settings.json** - Global Claude settings
- **settings.local.json** - Platform-specific settings

### 4. Data Storage (`/data`)

User-generated content:

- **conversations/** - Chat histories by project
- **workspaces/** - Active PRD workspaces
- **todos/** - Task tracking states
- **logs/** - Usage and activity logs

### 5. Cache (`/cache`)

Temporary data:

- **shell-snapshots/** - Shell state captures
- **statsig/** - Feature flag cache

## Design Principles

### 1. Embedded Workflows
Commands contain complete workflows that cannot be skipped, solving the problem of Claude ignoring background instructions.

### 2. Composability
Commands reference shared components (personas, principles) via INCLUDE tags, enabling:
- Consistency across commands
- Easy updates to shared behavior
- DRY principle adherence

### 3. Expert-Driven
Each command embodies specific expert personas, ensuring professional-grade decision making.

### 4. Verification-First
All commands include mandatory verification steps that must pass before marking completion.

### 5. Clear Organization
Commands are organized by purpose, making them easy to discover and understand.

## Command Anatomy

```markdown
# /command-name - Brief Description

Embody these expert personas:
<!-- INCLUDE: personas.md#PERSONA_NAME -->

First, load and follow these principles:
<!-- INCLUDE: principles.md#PRINCIPLE_TAG -->

Execute the COMPLETE workflow:
1. **Phase Name**:
   - Specific steps
   - Verification requirements

CRITICAL: If ANY step fails, STOP and report.
```

## Integration Points

### 1. Git Aliases
Git aliases can invoke slash commands:
```bash
cc-commit = !claude "/commit"
```

### 2. Shell Functions
PowerShell and Bash profiles include functions for common workflows.

### 3. Installation Scripts
Automated installation scripts copy the entire structure to user's Claude directory.

## Future Extensibility

The architecture supports:
1. Adding new command categories
2. Creating domain-specific personas
3. Extending principles for new workflows
4. Plugin-style command additions
5. Team-shared command libraries