# ClaudeOps Directory Structure

## Repository = Your ~/.claude Directory

After installation, the repository contents become your `~/.claude` configuration.

```
claudeops/ (repo) → ~/.claude/ (installed)
├── commands/                       # All executable slash commands
│   ├── core/                      # Essential daily commands
│   │   ├── commit.md             # Safe commit workflow
│   │   ├── fix.md                # Systematic debugging
│   │   ├── test.md               # Test generation (80% coverage)
│   │   ├── build.md              # Platform-specific builds
│   │   ├── safe.md               # Universal safety wrapper
│   │   └── config.md             # Configuration changes
│   ├── workflow/                  # Multi-step processes
│   │   ├── prd.md                # Full PRD creation
│   │   ├── prdq.md               # Quick PRD
│   │   ├── prd-decompose.md      # Break down PRDs
│   │   └── prd-implement.md      # Execute PRD phases
│   ├── development/               # Programming workflows
│   │   ├── refactor-safe.md      # Safe refactoring
│   │   ├── review-pr.md          # PR reviews
│   │   ├── tdd.md                # Test-driven development
│   │   ├── pattern.md            # Code patterns
│   │   ├── git-investigate.md    # Git history analysis
│   │   └── fix-and-test.md       # Legacy fix command
│   ├── generation/                # Code/content generation
│   │   ├── api-crud.md           # REST API generation
│   │   ├── mobile-scaffold.md    # MAUI app scaffolding
│   │   ├── create-docs.md        # Documentation generation
│   │   └── context-prime.md      # Codebase understanding
│   └── README.md                  # Command reference
│
├── system/                        # Supporting components
│   ├── personas.md               # Expert mindsets
│   ├── principles.md             # Reusable principles
│   ├── templates/                # Templates
│   │   ├── prd-index.md         # PRD index template
│   │   ├── prd-tracker.md       # PRD tracker template
│   │   └── newcmd.md            # New command template
│   └── scripts/                  # Utility scripts
│       ├── track-usage.js       # Usage tracking
│       └── ccusage.ps1          # Usage analysis
│
├── settings.json                # Global Claude Code settings
├── config/                       # Additional configuration files
│   ├── CLAUDE.md                # Project-specific instructions
│   └── gitconfig-aliases        # Git command aliases
│
├── data/                         # User-generated data
│   ├── conversations/           # Chat histories
│   ├── workspaces/             # Active PRD workspaces
│   ├── todos/                  # Todo states
│   └── logs/                   # Usage logs
│
├── cache/                       # Temporary data
│   ├── shell-snapshots/        # Shell state captures
│   └── statsig/                # Feature flags
│
├── docs/                        # Documentation
│   ├── README.md               # Main documentation
│   ├── rationale.md            # Why slash commands work
│   ├── architecture.md         # System design
│   ├── commands.md             # Command reference
│   ├── simplified.md           # Simplified guide
│   └── migration/              # Migration guides
│       └── credentials.md      # Credential restore
│
└── STRUCTURE.md                # This file
```

## Quick Navigation

### By Purpose

**Daily Development**
- `/commit` - Safe commits with verification
- `/fix` - Debug issues systematically
- `/test` - Generate comprehensive tests
- `/build` - Build projects

**Code Generation**
- `/api-crud` - Generate REST APIs
- `/mobile-scaffold` - Create mobile apps
- `/create-docs` - Generate documentation

**Advanced Workflows**
- `/prd` → `/prd-decompose` → `/prd-implement` - Full PRD workflow
- `/tdd` - Test-driven development
- `/refactor-safe` - Safe refactoring

**Safety & Review**
- `/safe` - Wrap any task in safety checks
- `/review-pr` - Review pull requests
- `/config` - Safe configuration changes

### By Skill Level

**Beginner**
- Start with `/safe` for any task
- Use `/commit` for all commits
- Try `/test` for test generation

**Intermediate**
- Use `/fix` for debugging
- Try `/api-crud` for API generation
- Explore `/tdd` workflow

**Advanced**
- Full PRD workflow (`/prd*` commands)
- `/pattern` for design patterns
- `/git-investigate` for history analysis

## Key Files

### Configuration
- `settings.json` - Global Claude Code settings (hooks, permissions, model)
- `config/CLAUDE.md` - Project-specific Claude instructions
- `config/gitconfig-aliases` - Git command aliases

### References
- `system/personas.md` - Expert mindsets used by commands
- `system/principles.md` - Reusable workflow components
- `commands/README.md` - Command reference guide

### Documentation
- `docs/README.md` - Complete system overview
- `docs/architecture.md` - System design details
- `docs/rationale.md` - Why this approach works

## Data Storage

### User Data (gitignored)
- `data/conversations/` - Chat histories by project
- `data/workspaces/` - Active PRD workspaces
- `data/todos/` - Task tracking
- `data/logs/` - Usage tracking

### Temporary (auto-cleaned)
- `cache/shell-snapshots/` - Shell states
- `cache/statsig/` - Feature flags

## Adding New Commands

1. Choose appropriate category in `commands/`
2. Copy template from `system/templates/newcmd.md`
3. Include relevant personas and principles
4. Test thoroughly before use

## Best Practices

1. **Use `/safe`** when unsure about any task
2. **Always `/commit`** instead of manual git commit
3. **Start with `/prdq`** for new features
4. **Check logs** with `ccusage` command
5. **Read docs** in `docs/` for deep understanding