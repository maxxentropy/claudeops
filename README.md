# ClaudeOps - Professional Claude Code Configuration

A comprehensive slash command system that transforms Claude Code from a stateless assistant into a disciplined development partner with embedded professional workflows.

## 🎯 What This Solves

**The Core Problem**: Claude prioritizes immediate commands over background context, leading to skipped verification steps and inconsistent workflows.

**The Solution**: Embed complete workflows directly in slash commands, leveraging Claude's natural behavior instead of fighting it.

**Before**: 
- User: "Always test before committing" (background context)
- Later: "commit these changes"
- Claude: *commits without testing* ❌

**After**:
- User: `/commit`
- Claude: *reads commit.md with embedded testing workflow* ✅

## 🏗️ Architecture

### Core Components

1. **Tagged Principles System** (`.claude/principles.md`)
   - Reusable workflow sections referenced via tags
   - `<!-- CORE_PRINCIPLES -->`, `<!-- VERIFICATION_STEPS -->`, etc.
   - Eliminates duplication across commands

2. **Expert Personas** (`.claude/personas.md`)
   - Commands embody specific professional mindsets
   - Senior Test Engineer, Software Architect, Security Engineer, etc.
   - Ensures top 1% professional decision-making

3. **Complete Embedded Workflows**
   - Commands contain ALL steps, not just reminders
   - Failure stops execution immediately
   - No assumptions or "this should work" shortcuts

## 📋 Available Commands

### Core Safety Commands
- `/safe [task]` - Universal safe wrapper with full verification
- `/commit` - Verified commit process with mandatory testing
- `/fix [issue]` - Systematic debugging with investigation phase
- `/config [type]` - Safe configuration changes with API version checks

### Development Commands  
- `/test [target]` - Generate comprehensive tests (80% coverage)
- `/build [platform]` - Platform-specific builds (.NET, Node.js, mobile)
- `/pattern [type]` - Implement standard code patterns

### PRD Workflow
- `/prdq [feature]` - Quick requirements document for immediate work
- `/prd [feature]` - Comprehensive PRD for team planning
- `/prd-decompose [prd]` - Break PRD into phases with dependencies
- `/prd-implement [project] [phase]` - Execute with context preservation

### Specialized Commands
- `/api-crud` - Generate complete CRUD APIs with validation
- `/mobile-scaffold` - MAUI app scaffolding with Prism framework
- `/context-prime` - Comprehensive codebase understanding
- `/git-investigate` - Analyze code history and evolution
- `/refactor-safe` - Safe, incremental refactoring process
- `/tdd` - Test-driven development workflow

## 🚀 Quick Start

### Option 1: Use Installation Scripts
```bash
# PowerShell (Windows)
.\install-claude-config.ps1

# Bash (Linux/Mac/WSL)
./install-claude-config.sh
```

### Option 2: Manual Setup
1. Copy `.claude/` directory to your global Claude directory (`~/.claude`)
2. Restart Claude Code
3. Test with: `/safe 'echo Hello World'`

## 📁 Repository Structure

```
claudeops/
├── .claude/                          # Complete Claude configuration
│   ├── README-slash-commands.md      # Complete system overview
│   ├── slash-command-rationale.md    # Why this approach works
│   ├── commands.md                   # Command reference guide
│   ├── principles.md                 # Reusable tagged sections
│   ├── personas.md                   # Expert mindsets
│   ├── newcmd.md                     # How to create new commands
│   ├── settings.json                 # Claude Code configuration
│   ├── CLAUDE.md                     # Global development standards
│   ├── safe.md                       # Core safety commands
│   ├── commit.md                     # Verified commit workflow
│   ├── fix.md                        # Systematic debugging
│   ├── config.md                     # Configuration changes
│   ├── test.md                       # Test generation
│   ├── build.md                      # Platform builds
│   ├── pattern.md                    # Code patterns
│   ├── prd.md                        # PRD workflow commands
│   ├── prdq.md                       # Quick PRD
│   ├── prd-decompose.md              # PRD breakdown
│   ├── prd-implement.md              # PRD execution
│   ├── prd-tracker-template.md       # Progress tracking
│   └── commands/                     # Specialized command library
│       ├── backend/
│       │   └── api-crud.md
│       ├── mobile/
│       │   └── mobile-scaffold.md
│       └── shared/
│           ├── context-prime.md
│           ├── create-docs.md
│           ├── fix-and-test.md
│           ├── git-investigate.md
│           ├── refactor-safe.md
│           ├── review-pr.md
│           └── tdd.md
├── install-claude-config.ps1         # PowerShell installer
├── install-claude-config.sh          # Bash installer
└── README.md                         # This file
```

## 🎨 Command Structure Pattern

Each command follows this proven structure:

```markdown
# /command-name - Brief Description

Embody these expert personas:
<!-- INCLUDE: personas.md#PERSONA_NAME -->

First, load principles:
<!-- INCLUDE: principles.md#RELEVANT_TAGS -->

Execute complete workflow:
1. **Investigation Phase**: Understand context
2. **Implementation Phase**: Apply changes systematically  
3. **Verification Phase**: Test, build, lint
4. **Completion Phase**: Confirm all criteria met

CRITICAL: If ANY step fails, STOP and report.
```

## 🔧 Key Features

### 1. No Skipped Steps
Workflows are embedded in commands, so verification steps can't be forgotten.

### 2. Expert-Level Decision Making
Each command applies the mindset of senior professionals in relevant disciplines.

### 3. Failure Safety
Commands stop immediately on any verification failure - no partial implementations.

### 4. Context Preservation
PRD workflow maintains context across phases for complex implementations.

### 5. Composability
Commands work together: `/prdq` → `/prd-decompose` → `/prd-implement`

## 🔄 Workflow Examples

### Safe Commit Process
```
User: /commit
Claude: 
1. Runs git status and git diff
2. Analyzes all changes for security issues
3. Runs build: dotnet build
4. Runs tests: dotnet test
5. Runs linting: dotnet format
6. Creates commit with verification badge
7. Only proceeds if ALL steps pass
```

### Systematic Bug Fix
```
User: /fix "login not working"
Claude:
1. Investigates recent commits (last 3)
2. Analyzes error patterns and logs
3. Identifies minimal change approach
4. Implements fix with proper error handling
5. Creates comprehensive tests
6. Verifies fix resolves issue
7. Full verification before completion
```

### PRD-Driven Development
```
User: /prdq "user notifications"
Claude: Creates quick PRD document

User: /prd-decompose
Claude: Breaks into phases (DB, API, UI, Testing)

User: /prd-implement notifications phase-1
Claude: Implements database layer with full context
```

## 🧠 Expert Personas

Commands embody these professional mindsets:

- **Senior Test Engineer**: "If it can break, I'll find how"
- **Software Architect**: "How will this scale and evolve?"
- **Security Engineer**: "Trust nothing, verify everything"
- **DevOps Engineer**: "If I do it twice, I automate it"
- **Code Reviewer**: "Code is read hundreds of times"
- **SRE Engineer**: "Minimize blast radius of changes"

## 📈 Results

This system transforms Claude into a development partner that:

✅ **Never skips verification steps** (embedded in commands)  
✅ **Applies expert-level thinking** (through personas)  
✅ **Maintains consistency** (through shared principles)  
✅ **Preserves context** (through workspace management)  
✅ **Scales to teams** (through PRD system)

## 🔧 Configuration Integration

### Hooks in settings.json
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "echo 'Executing command...'"}]
    }],
    "PostToolUse": [{
      "matcher": "Edit|Write|MultiEdit", 
      "hooks": [{"type": "command", "command": "dotnet format --verify-no-changes || true"}]
    }]
  }
}
```

### Environment Variables
- `DOTNET_CLI_TELEMETRY_OPTOUT: "1"`
- `NODE_ENV: "development"`

## 🎯 Creating New Commands

1. **Identify repeated workflows** where steps get skipped
2. **Choose appropriate expert personas** for the domain
3. **Reference existing principle tags** for consistency
4. **Embed complete workflow** (not just reminders)
5. **Test thoroughly** before integration

See `.claude/newcmd.md` for detailed instructions.

## 📖 Further Reading

- [Complete System Documentation](.claude/README-slash-commands.md)
- [Command Reference Guide](.claude/commands.md)
- [Why Slash Commands Work](.claude/slash-command-rationale.md)
- [Creating New Commands](.claude/newcmd.md)

## 🤝 Contributing

1. Fork this repository
2. Create your feature branch
3. Add new commands following the established patterns
4. Test thoroughly with real workflows
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.

---

**Transform your Claude Code experience from inconsistent helper to disciplined development partner.** 🚀