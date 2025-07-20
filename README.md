# Claude Code Configuration Hub

Your personal Claude Code configuration repository for maximizing productivity across Windows, Mac, and Linux development environments.

## 🚀 Quick Start

1. **Clone this repository**:
   ```bash
   git clone git@github.com:maxxentropy/claudeops.git ~/claudeops
   ```

2. **Run the sync script**:
   
   **PowerShell (Windows):**
   ```powershell
   ~/claudeops/sync.ps1
   ```
   
   **Bash (Mac/Linux):**
   ```bash
   ~/claudeops/sync.sh
   ```

3. **Set your API key** (if using API authentication):
   
   **PowerShell:**
   ```powershell
   $env:CLAUDE_API_KEY = 'your-api-key-here'
   [Environment]::SetEnvironmentVariable('CLAUDE_API_KEY', 'your-api-key-here', 'User')
   ```
   
   **Bash:**
   ```bash
   export CLAUDE_API_KEY='your-api-key-here'
   echo "export CLAUDE_API_KEY='your-api-key-here'" >> ~/.bashrc
   ```

4. **Reload your shell**:
   
   **PowerShell:**
   ```powershell
   # Restart PowerShell or run:
   . $PROFILE
   ```
   
   **Bash:**
   ```bash
   source ~/.bashrc  # or ~/.zshrc on Mac
   ```

## 📁 Repository Structure

```
claudeops/
├── CLAUDE.md                 # Master instructions for Claude
├── settings/
│   ├── global.json          # Cross-platform settings
│   ├── windows.json         # Windows-specific settings
│   ├── macos.json          # macOS-specific settings
│   └── linux.json          # Linux-specific settings
├── commands/
│   ├── mobile/             # Mobile development commands
│   ├── backend/            # Backend/API commands
│   ├── webservices/        # Web service commands
│   └── shared/             # Shared commands
├── sync.sh                 # Cross-platform sync script
└── powershell-profile.ps1  # PowerShell shortcuts
```

## 🛠️ Features

### Custom Commands
- `/mobile-scaffold` - Create Prism-based MAUI app structure
- `/api-crud` - Generate complete CRUD API with tests
- `/fix-and-test` - Intelligent debugging with xUnit test generation
- `/context-prime` - Deep project analysis and understanding
- `/tdd` - Guided Test-Driven Development workflow
- `/create-docs` - Auto-generate comprehensive documentation
- `/review-pr` - Systematic pull request review
- `/refactor-safe` - Safe, incremental refactoring process

### Shell Aliases
- `cc` - Quick Claude access (project-aware)
- `cct` - Claude with thinking mode
- `ccpr` - Create PR with current changes
- `ccfix` - Run fix-and-test command
- `ccsync` - Sync configurations
- `ccusage` - View usage statistics and ROI
- `cc-init-project` - Initialize project with CLAUDE.md

### Git Investigation Commands
- `gi <file>` - Investigate file history interactively
- `gsearch <pattern>` - Search commits and code changes
- `gwhy <file> [line]` - Show who changed what (enhanced blame)
- `gcontext [path]` - Show recent activity and contributors

### Development Workflow Commands
- `verify` - Quick verification of changed files only
- `qc "msg"` - Quick commit with auto-verification

### Development Standards
- Prism framework for MAUI mobile apps
- xUnit for all testing
- Conventional commits with auto-verification
- Platform-specific optimizations

## 💻 Platform Setup

### Windows (via WSL)
1. Install WSL2: `wsl --install`
2. Install Node.js in WSL
3. Install Claude Code: `npm install -g @anthropic-ai/claude-code`
4. Add PowerShell profile shortcuts

### macOS
1. Install Node.js via Homebrew
2. Install Claude Code: `npm install -g @anthropic-ai/claude-code`
3. Use zsh configuration

### Linux
1. Install Node.js
2. Install Claude Code: `npm install -g @anthropic-ai/claude-code`
3. Use bash configuration

## 🔧 Customization

### Adding Custom Commands
1. Create a new `.md` file in `commands/[category]/`
2. Define the command workflow
3. Run `ccsync` to update

### Modifying Settings
1. Edit the appropriate settings file
2. Run `ccsync` to apply changes
3. Restart Claude Code if needed

## 📊 Usage Tracking

The configuration includes usage tracking to monitor your ROI:
```bash
# View usage logs
cat ~/.claude/logs/usage.jsonl | jq
```

## 🔒 Security

- Never commit API keys
- Use environment variables for secrets
- Keep work and personal configs separate
- Review `.gitignore` before committing

## 🤝 Best Practices

1. **Clear context frequently**: Use `/clear` between tasks
2. **Use thinking modes**: Add "think" for complex problems
3. **Batch operations**: Queue multiple related tasks
4. **Regular syncing**: Run `ccsync` weekly

## 📈 ROI Tracking

Based on typical usage:
- Time saved per month: ~20 hours
- Value at $100/hour: $2,000
- Monthly cost: $100
- **ROI: 2000%**

## 🔄 Daily Development Workflow

Once setup is complete, use these commands for efficient development:

### Quick Commands
```bash
# Before starting work - check recent changes
gi <file>          # Investigate file history
gcontext           # See recent activity

# While coding
verify             # Quick check of your changes (30 seconds)

# Ready to commit  
qc "fix: description"  # Auto-verify and commit with proper format

# Or manually
git add .
git commit -m "feat: add new feature"  # Hooks auto-verify
```

### The 3-Stage Workflow
1. **Rapid feedback** (during coding): `dotnet watch test` or `npm run test:watch`
2. **Pre-commit** (before committing): `verify` - checks only changed files
3. **Full verification** (before PR): Run complete test suite

## 🎯 Optional: Git Hooks Setup

For automatic verification on every commit:
```bash
# One-time setup
./scripts/install-hooks.ps1  # Windows
./scripts/install-hooks.sh   # Mac/Linux
```

This installs:
- **pre-commit**: Runs `verify` automatically
- **commit-msg**: Ensures proper format, adds [✓ VERIFIED] badge

## 🆘 Troubleshooting

### Claude Code not found
```bash
npm install -g @anthropic-ai/claude-code
```

### API key not working
```bash
export CLAUDE_API_KEY='your-actual-key'
echo "export CLAUDE_API_KEY='your-actual-key'" >> ~/.bashrc
```

### Sync issues
```bash
cd ~/claudeops
git status
git pull origin main
```

## 📝 License

This configuration is personalized for your development workflow. Feel free to modify and extend as needed.