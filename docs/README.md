# Claude Slash Commands System

A sophisticated workflow automation system that transforms Claude from a stateless assistant into a disciplined, continuously improving development partner.

## Quick Start

```bash
# See all available commands
/commands

# Create a quick PRD
/prdq implement user authentication system

# Decompose and implement
/prd-decompose user-authentication
/prd-implement user-authentication phase-1
```

## Core Concept: Why Slash Commands?

Traditional problem: Claude prioritizes immediate commands over background rules.
- You: "Always test before committing"
- Later: "commit these changes"
- Claude: *commits without testing* ❌

Our solution: Embed the workflow IN the command.
- You: `/commit`
- Claude: *runs tests, then commits* ✅

[Read the full rationale](./slash-command-rationale.md)

## System Architecture

### 1. **Principles** (`principles.md`)
Reusable tagged sections that commands reference:
- `<!-- CORE_PRINCIPLES -->` - Never take shortcuts, etc.
- `<!-- VERIFICATION_STEPS -->` - Build, test, lint workflow
- `<!-- LANG_STANDARDS -->` - Language-specific conventions

### 2. **Personas** (`personas.md`)
Expert mindsets that commands embody:
- Senior Test Engineer - "If it can break, I'll find how"
- Software Architect - "How will this scale and evolve?"
- Security Engineer - "Trust nothing, verify everything"

### 3. **Commands** (Individual `.md` files)
Each command:
- Embodies 1-2 expert personas
- References principle tags (no duplication)
- Contains complete workflow (not just reminders)
- Produces predictable outcomes

## PRD Workflow

### Creating PRDs

```bash
# Quick PRD for immediate work
/prdq implement new feature

# Formal PRD for team planning  
/prd multi-tenant architecture
```

PRDs are automatically saved to:
- `docs/prds/YYYY-MM-DD-feature-name.md` (version controlled)
- `.claude/prd-workspace/feature-name/` (working directory)

### Implementing PRDs

```bash
# 1. Decompose into phases
/prd-decompose feature-name

# 2. Implement phase by phase
/prd-implement feature-name phase-1
/prd-implement feature-name phase-2

# Each phase loads context from previous phases automatically
```

## Command Reference

### Development Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/safe` | Any task with full safety protocols | `/safe refactor auth module` |
| `/commit` | Verify, test, then commit | `/commit` |
| `/fix` | Debug with root cause analysis | `/fix memory leak` |
| `/config` | Update configuration safely | `/config hooks` |
| `/test` | Generate comprehensive tests | `/test UserService` |
| `/build` | Platform-specific builds | `/build android` |
| `/pattern` | Implement design patterns | `/pattern repository User` |

### Planning Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/prdq` | Quick requirements (1 page) | `/prdq auth system` |
| `/prd` | Formal PRD (comprehensive) | `/prd payment gateway` |
| `/prd-decompose` | Break PRD into phases | `/prd-decompose auth-system` |
| `/prd-implement` | Execute PRD phase | `/prd-implement auth phase-1` |

### Meta Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/newcmd` | Create new slash command | `/newcmd api validation` |
| `/commands` | List all commands | `/commands` |

## Project Structure

```
your-project/
├── docs/
│   └── prds/                        # Version controlled PRDs
│       ├── index.md                 # PRD registry
│       └── YYYY-MM-DD-feature.md    # Individual PRDs
│
├── .claude/                         # Claude workspace (gitignored)
│   ├── *.md                         # Slash command definitions
│   ├── principles.md                # Reusable principles
│   ├── personas.md                  # Expert personas
│   └── prd-workspace/               # Active PRD implementations
│       └── feature-name/
│           ├── prd-tracker.md       # Progress tracking
│           ├── phase-1-spec.md      # Phase specifications
│           └── artifacts/           # Implementation outputs
```

## Best Practices

### 1. **Use Commands for Repeated Workflows**
Instead of: "fix the bug, test it, make sure it works"
Use: `/fix authentication timeout`

### 2. **Let Commands Enforce Quality**
The command contains verification steps - you can't skip them.

### 3. **Decompose Large Tasks**
Use `/prd-decompose` to break big features into manageable phases.

### 4. **Track Everything**
PRDs and their implementation are tracked automatically.

### 5. **Create Custom Commands**
Use `/newcmd` when you notice repeated patterns.

## Advanced Features

### Context Preservation
- Each `/prd-implement` loads all previous phase artifacts
- No lost context between work sessions
- Perfect for complex, multi-day implementations

### Expert Personas
- Commands think like top 1% professionals
- `/fix` combines Test Engineer + SRE mindsets
- `/commit` applies Code Reviewer + Security Engineer standards

### Extensibility
- Add new personas to `personas.md`
- Create project-specific principles
- Build custom commands for your workflow

## Troubleshooting

**Q: Command not found?**
A: Check `/commands` for exact syntax

**Q: PRD not saving?**
A: Ensure `docs/prds/` directory exists

**Q: Phase failing prerequisites?**
A: Previous phases must be marked COMPLETE in tracker

## Future: Continuously Improving Claude

The roadmap includes making Claude learn from every interaction:
- Track what fixes actually worked
- Suggest new commands based on patterns
- Build project-specific knowledge base
- Measure time saved and bugs prevented

See [Continuous Improvement PRD](./docs/prds/2025-01-20-continuous-improvement.md)

## Contributing

To add new commands:
1. Use `/newcmd` to create properly structured command
2. Test the command thoroughly
3. Update documentation
4. Share with team

---

Remember: The goal is to make Claude reliable through explicit workflows, not memory and discipline.