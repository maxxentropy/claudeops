# ClaudeOps - Professional Claude Code Configuration

Drop-dead simple Claude Code configuration with embedded workflows that ensure professional standards.

## 🚀 Installation (30 seconds)

### Option 1: Direct Clone (Recommended)
```bash
# Clone directly as your Claude configuration
git clone https://github.com/maxxentropy/claudeops ~/.claude
```

### Option 2: Traditional Install
```bash
# Clone and install
git clone https://github.com/maxxentropy/claudeops
cd claudeops
./install.sh
```

That's it! Your slash commands are ready to use.

## 🎯 What This Solves

**Problem**: Claude prioritizes immediate commands over background context, leading to skipped steps and inconsistent quality.

**Solution**: Embed complete workflows directly in slash commands, turning Claude's behavior into an advantage.

## 📋 Essential Commands

### Daily Development
- `/commit` - Safe commits with full verification
- `/fix` - Systematic debugging
- `/test` - Generate comprehensive tests
- `/safe` - Wrap any task in safety checks

### Code Generation
- `/api-crud` - Complete REST APIs with tests
- `/mobile-scaffold` - MAUI apps with Prism
- `/create-docs` - Auto-generate documentation

### Advanced Workflows
- `/prd` → `/prd-decompose` → `/prd-implement` - Full PRD workflow
- `/tdd` - Test-driven development
- `/refactor-safe` - Safe incremental refactoring

## 🏗️ How It Works

Each command:
1. **Embodies expert personas** (Senior Test Engineer, Software Architect, etc.)
2. **Includes complete workflows** that can't be skipped
3. **Enforces verification** before marking complete
4. **Stops on any failure** instead of continuing blindly

## 📁 Repository Structure

```
claudeops/
├── commands/           # All slash commands
│   ├── core/          # Essential commands
│   ├── workflow/      # Multi-step processes
│   ├── development/   # Programming workflows
│   └── generation/    # Code generation
├── system/            # Supporting components
│   ├── personas.md    # Expert mindsets
│   ├── principles.md  # Reusable workflows
│   └── scripts/       # Utilities
├── config/            # Configuration files
├── data/              # User data (gitignored)
├── cache/             # Temporary files
└── docs/              # Documentation
```

## 🛠️ Configuration

### Git Aliases
Add to your `.gitconfig`:
```ini
[include]
    path = ~/.claude/config/gitconfig-aliases
```

### PowerShell
```powershell
# Add to your profile
. ~/.claude/scripts/shell-integration/powershell-profile.ps1
```

## 📈 Results

- ✅ **No skipped steps** - Workflows embedded in commands
- ✅ **Expert-level quality** - Professional personas
- ✅ **Consistent execution** - Shared principles
- ✅ **Immediate feedback** - Stops on failures

## 🔧 Creating Custom Commands

1. Copy template: `system/templates/newcmd.md`
2. Add to appropriate `commands/` subdirectory
3. Include relevant personas and principles
4. Test thoroughly

## 📚 Documentation

- [Complete Overview](docs/README.md)
- [Architecture](docs/architecture.md)
- [Why It Works](docs/rationale.md)
- [Command Reference](docs/commands.md)

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add/improve commands
4. Submit pull request

## 📄 License

MIT License - See LICENSE file

---

**Transform Claude from an assistant into a professional development partner.** 🚀