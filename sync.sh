#!/bin/bash
# Claude Code Configuration Sync Script
# Syncs configurations across Windows, Mac, and Linux environments

set -e

# Configuration
CLAUDE_CONFIG_REPO="${CLAUDE_CONFIG_REPO:-https://github.com/YOUR_USERNAME/claude-config.git}"
CLAUDE_CONFIG_DIR="$HOME/.claude-config"
CLAUDE_HOME="$HOME/.claude"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect operating system
detect_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos";;
        Linux*)     echo "linux";;
        MINGW*|CYGWIN*|MSYS*) echo "windows";;
        *)          echo "unknown";;
    esac
}

# Create Claude directory if it doesn't exist
init_claude_dir() {
    if [ ! -d "$CLAUDE_HOME" ]; then
        log_info "Creating Claude home directory: $CLAUDE_HOME"
        mkdir -p "$CLAUDE_HOME"
        mkdir -p "$CLAUDE_HOME/commands"
        mkdir -p "$CLAUDE_HOME/logs"
    fi
}

# Clone or update configuration repository
sync_repo() {
    if [ -d "$CLAUDE_CONFIG_DIR/.git" ]; then
        log_info "Updating existing configuration repository..."
        cd "$CLAUDE_CONFIG_DIR"
        git pull origin main || git pull origin master
    else
        log_info "Cloning configuration repository..."
        git clone "$CLAUDE_CONFIG_REPO" "$CLAUDE_CONFIG_DIR"
    fi
}

# Link configuration files
link_configs() {
    local os_type=$(detect_os)
    
    log_info "Detected OS: $os_type"
    
    # Link CLAUDE.md
    log_info "Linking CLAUDE.md..."
    ln -sf "$CLAUDE_CONFIG_DIR/CLAUDE.md" "$CLAUDE_HOME/CLAUDE.md"
    
    # Link global settings
    log_info "Linking global settings..."
    ln -sf "$CLAUDE_CONFIG_DIR/settings/global.json" "$CLAUDE_HOME/settings.json"
    
    # Link platform-specific settings
    if [ "$os_type" != "unknown" ]; then
        log_info "Linking $os_type-specific settings..."
        ln -sf "$CLAUDE_CONFIG_DIR/settings/$os_type.json" "$CLAUDE_HOME/settings.local.json"
    else
        log_warn "Unknown OS detected, skipping platform-specific settings"
    fi
}

# Sync custom commands
sync_commands() {
    log_info "Syncing custom commands..."
    
    # Copy all commands, preserving directory structure
    if [ -d "$CLAUDE_CONFIG_DIR/commands" ]; then
        cp -r "$CLAUDE_CONFIG_DIR/commands/"* "$CLAUDE_HOME/commands/" 2>/dev/null || true
        
        # Make command files executable
        find "$CLAUDE_HOME/commands" -type f -name "*.sh" -exec chmod +x {} \;
        
        log_info "Commands synced successfully"
    else
        log_warn "No commands directory found in config repo"
    fi
}

# Setup shell aliases
setup_aliases() {
    local shell_rc=""
    local os_type=$(detect_os)
    
    # Determine shell configuration file
    if [ -n "$ZSH_VERSION" ]; then
        shell_rc="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        shell_rc="$HOME/.bashrc"
    fi
    
    if [ -z "$shell_rc" ] || [ ! -f "$shell_rc" ]; then
        log_warn "Could not determine shell configuration file"
        return
    fi
    
    # Check if aliases are already added
    if grep -q "# Claude Code Aliases" "$shell_rc"; then
        log_info "Claude aliases already configured in $shell_rc"
        return
    fi
    
    log_info "Adding Claude aliases to $shell_rc..."
    
    cat >> "$shell_rc" << 'EOF'

# Claude Code Aliases
alias cc='claude'
alias cct='claude think'
alias ccth='claude think hard'
alias cchthr='claude think harder'
alias ccu='claude ultrathink'
alias ccpr='claude "Create a PR with all current changes"'
alias ccfix='claude /fix-and-test'
alias ccsync='~/.claude-config/sync.sh'
alias cclog='tail -f ~/.claude/logs/claude.log'
alias ccclear='claude /clear'

# Claude quick commands
ccnew() {
    claude "Create a new $1 project with best practices and proper structure"
}

cctest() {
    claude "Generate comprehensive unit tests for the current file or selection"
}

ccrefactor() {
    claude "Refactor this code for better performance and maintainability"
}

ccreview() {
    claude "Review this code for bugs, security issues, and best practices"
}

EOF
    
    log_info "Aliases added. Run 'source $shell_rc' to apply them immediately"
}

# Create usage tracking script
create_usage_tracker() {
    log_info "Setting up usage tracking..."
    
    cat > "$CLAUDE_HOME/track-usage.js" << 'EOF'
#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const logFile = path.join(process.env.HOME, '.claude', 'logs', 'usage.jsonl');

function trackUsage(command, tokens, estimatedCost) {
    const entry = {
        timestamp: new Date().toISOString(),
        command: command,
        tokens: tokens,
        estimatedCost: estimatedCost,
        platform: process.platform
    };
    
    fs.appendFileSync(logFile, JSON.stringify(entry) + '\n');
}

// Export for use in hooks
module.exports = { trackUsage };

// CLI usage
if (require.main === module) {
    const [,, command, tokens, cost] = process.argv;
    if (command && tokens && cost) {
        trackUsage(command, parseInt(tokens), parseFloat(cost));
        console.log('Usage tracked successfully');
    } else {
        console.log('Usage: track-usage <command> <tokens> <cost>');
    }
}
EOF
    
    chmod +x "$CLAUDE_HOME/track-usage.js"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check if Claude is installed
    if ! command -v claude &> /dev/null; then
        log_error "Claude Code is not installed. Install with: npm install -g @anthropic-ai/claude-code"
        ((errors++))
    else
        log_info "✓ Claude Code is installed"
    fi
    
    # Check configuration files
    if [ -f "$CLAUDE_HOME/CLAUDE.md" ]; then
        log_info "✓ CLAUDE.md is linked"
    else
        log_error "✗ CLAUDE.md is not linked"
        ((errors++))
    fi
    
    if [ -f "$CLAUDE_HOME/settings.json" ]; then
        log_info "✓ Settings are configured"
    else
        log_error "✗ Settings are not configured"
        ((errors++))
    fi
    
    # Check API key
    if [ -z "$CLAUDE_API_KEY" ]; then
        log_warn "CLAUDE_API_KEY environment variable is not set"
        log_warn "Add to your shell configuration: export CLAUDE_API_KEY='your-key-here'"
    else
        log_info "✓ API key is configured"
    fi
    
    if [ $errors -eq 0 ]; then
        log_info "Installation verified successfully!"
    else
        log_error "Installation verification failed with $errors errors"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting Claude Code configuration sync..."
    
    init_claude_dir
    sync_repo
    link_configs
    sync_commands
    setup_aliases
    create_usage_tracker
    verify_installation
    
    log_info "Sync completed successfully!"
    log_info "Run 'source ~/.bashrc' or 'source ~/.zshrc' to load aliases"
}

# Run main function
main "$@"