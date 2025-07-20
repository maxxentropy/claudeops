# ClaudeOps - Professional Claude Code Configuration

Drop-dead simple Claude Code configuration with embedded workflows that ensure professional standards.

## 🚀 Installation (30 seconds)

### macOS / Linux

#### Option 1: Direct Clone (Recommended)
```bash
# Remove existing configuration if present
rm -rf ~/.claude

# Clone directly as your Claude configuration
git clone https://github.com/maxxentropy/claudeops ~/.claude

# Make scripts executable (Linux/macOS)
chmod +x ~/.claude/system/scripts/*.sh
```

#### Option 2: Traditional Install
```bash
# Clone anywhere
git clone https://github.com/maxxentropy/claudeops
cd claudeops

# Run installer
./install.sh
```

### Windows

#### PowerShell
```powershell
# Remove existing configuration if present
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude" -ErrorAction SilentlyContinue

# Clone directly
git clone https://github.com/maxxentropy/claudeops "$env:USERPROFILE\.claude"
```

#### Git Bash
```bash
# Same as macOS/Linux
git clone https://github.com/maxxentropy/claudeops ~/.claude
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

### Git Aliases (All Platforms)
Add to your `.gitconfig`:
```ini
[include]
    path = ~/.claude/config/gitconfig-aliases
```

### Shell Integration

#### macOS / Linux (Bash)
Add to your `~/.bashrc` or `~/.bash_profile`:
```bash
# Claude Code aliases and functions
if [ -f ~/.claude/scripts/shell-integration/bash-profile.sh ]; then
    . ~/.claude/scripts/shell-integration/bash-profile.sh
fi
```

#### macOS / Linux (Zsh)
Add to your `~/.zshrc`:
```zsh
# Claude Code aliases and functions
if [ -f ~/.claude/scripts/shell-integration/zsh-profile.sh ]; then
    . ~/.claude/scripts/shell-integration/zsh-profile.sh
fi
```

#### Windows (PowerShell)
Add to your PowerShell profile:
```powershell
# Find your profile location
echo $PROFILE

# Add this line to the profile
. "$env:USERPROFILE\.claude\scripts\shell-integration\powershell-profile.ps1"
```

### Environment Variables (Optional)

#### macOS / Linux
Add to your shell profile:
```bash
export CLAUDE_API_KEY="your-api-key-here"
export CLAUDE_MODEL="claude-opus-4-20250514"
```

#### Windows
Set via PowerShell:
```powershell
[Environment]::SetEnvironmentVariable("CLAUDE_API_KEY", "your-api-key-here", "User")
[Environment]::SetEnvironmentVariable("CLAUDE_MODEL", "claude-opus-4-20250514", "User")
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

## 🔍 Troubleshooting

### Command Not Found
If you get "claude: command not found":

**macOS/Linux:**
```bash
# Check if claude is in PATH
which claude

# If not found, add to PATH
export PATH="$PATH:/path/to/claude"
```

**Windows:**
```powershell
# Check if claude is available
where.exe claude

# If not found, install via the official installer
```

### Permission Denied
**macOS/Linux:**
```bash
# Fix script permissions
chmod +x ~/.claude/system/scripts/*.sh
chmod +x ~/.claude/install.sh
```

### Slash Commands Not Working
1. Ensure you're using the latest Claude Code version
2. Check that ~/.claude exists and contains the commands
3. Try running: `claude /safe 'echo test'`

## 📄 License

MIT License - See LICENSE file

---

**Transform Claude from an assistant into a professional development partner.** 🚀