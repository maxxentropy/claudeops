## Quick Requirements: Unified Cross-Platform Shell Integration

### Problem
Shell integration is inconsistent across platforms with feature disparities, missing commands, and different path conventions, preventing users from having a seamless experience with ClaudeOps slash commands.

### Solution Approach
- Create unified shell module system with core functionality in shell-agnostic scripts
- Implement platform-specific adapters (bash, zsh, powershell, fish)
- Standardize all command aliases across platforms
- Auto-detect and configure based on user's shell
- Generate shell integration from slash command definitions

### Success Criteria
- [ ] 100% command parity across bash, zsh, and PowerShell
- [ ] Single-command installation that auto-detects shell
- [ ] All 30+ slash commands have consistent aliases
- [ ] Shell integration updates automatically with new commands
- [ ] Works on macOS, Linux, Windows without dependencies

### Out of Scope
- GUI configuration tools
- Shell-specific advanced features (keep to common denominator)
- IDE-specific integrations (that's separate)
- Legacy shells (sh, csh, cmd.exe)

### Implementation Notes
- Create `scripts/shell-integration/core.sh` with shared functions
- Use JSON manifest for command definitions
- Generate shell-specific files from templates
- Unify path to `~/.claude` across all platforms
- Add shell detection to install.ps1/install.sh
- Create comprehensive shell integration documentation