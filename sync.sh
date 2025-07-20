#!/usr/bin/env bash
# Claude Code Configuration Sync Script
# Syncs configurations across Windows, Mac, and Linux environments

# Configuration
CLAUDE_CONFIG_REPO="${CLAUDE_CONFIG_REPO:-git@github.com:maxxentropy/claudeops.git}"

# Handle HOME directory for Windows
if [ -z "$HOME" ] && [ -n "$USERPROFILE" ]; then
    export HOME="$USERPROFILE"
fi

CLAUDE_CONFIG_DIR="$HOME/claudeops"
CLAUDE_HOME="$HOME/.claude"

# Dry run mode
DRY_RUN=false

# Colors for output (check if terminal supports colors)
if [ -t 1 ]; then
    # Try tput first (most reliable)
    if command -v tput >/dev/null 2>&1 && [ -n "$TERM" ]; then
        RED=$(tput setaf 1 2>/dev/null || echo '')
        GREEN=$(tput setaf 2 2>/dev/null || echo '')
        YELLOW=$(tput setaf 3 2>/dev/null || echo '')
        NC=$(tput sgr0 2>/dev/null || echo '')
    else
        # Fallback to ANSI codes
        case "$TERM" in
            *color*|xterm*|screen*|linux|rxvt*)
                RED='\033[0;31m'
                GREEN='\033[0;32m'
                YELLOW='\033[1;33m'
                NC='\033[0m'
                ;;
            *)
                RED=''
                GREEN=''
                YELLOW=''
                NC=''
                ;;
        esac
    fi
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

# Logging functions
log_info() {
    printf "%s[INFO]%s %s\n" "$GREEN" "$NC" "$1"
}

log_warn() {
    printf "%s[WARN]%s %s\n" "$YELLOW" "$NC" "$1"
}

log_error() {
    printf "%s[ERROR]%s %s\n" "$RED" "$NC" "$1" >&2
}

# Detect operating system
detect_os() {
    local uname_out="$(uname -s 2>/dev/null || echo 'Unknown')"
    case "$uname_out" in
        Darwin*)    echo "macos";;
        Linux*)     echo "linux";;
        MINGW*|CYGWIN*|MSYS*|Windows*) echo "windows";;
        *)          echo "unknown";;
    esac
}

# Detect if running in WSL
is_wsl() {
    if [ -f /proc/version ]; then
        grep -qi microsoft /proc/version
    else
        false
    fi
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
check_requirements() {
    local missing_tools=()
    local warnings=()
    local os_type=$(detect_os)
    
    log_info "Checking system requirements..."
    
    # Essential tools (script won't work without these)
    local essential_tools=("git" "ln" "mkdir" "chmod" "grep")
    
    for tool in "${essential_tools[@]}"; do
        if ! command_exists "$tool"; then
            missing_tools+=("$tool")
        fi
    done
    
    # Check for Node.js and npm (required for Claude Code)
    if ! command_exists "node"; then
        warnings+=("Node.js is not installed. Claude Code requires Node.js.")
        warnings+=("  Install from: https://nodejs.org/")
    else
        local node_version=$(node --version 2>/dev/null | cut -d'v' -f2)
        log_info "✓ Node.js $node_version found"
    fi
    
    if ! command_exists "npm"; then
        warnings+=("npm is not installed. Required to install Claude Code.")
    else
        local npm_version=$(npm --version 2>/dev/null)
        log_info "✓ npm $npm_version found"
    fi
    
    # Check for Claude Code
    if ! command_exists "claude"; then
        warnings+=("Claude Code is not installed.")
        warnings+=("  Install with: npm install -g @anthropic-ai/claude-code")
    else
        log_info "✓ Claude Code is installed"
    fi
    
    # Platform-specific checks
    case "$os_type" in
        macos)
            # Check for Xcode Command Line Tools (provides git and other tools)
            if ! xcode-select -p >/dev/null 2>&1; then
                warnings+=("Xcode Command Line Tools not installed.")
                warnings+=("  Install with: xcode-select --install")
            fi
            ;;
        windows)
            # Check if we're in a proper shell environment
            if [ -z "$HOME" ]; then
                log_error "HOME environment variable not set"
                return 1
            fi
            # Git Bash specific checks
            if [ -n "$MSYSTEM" ]; then
                log_info "Detected Git Bash environment: $MSYSTEM"
            elif is_wsl; then
                log_info "Detected WSL environment"
            fi
            ;;
        linux)
            # Check for specific package managers to provide better help
            if command_exists "apt-get"; then
                log_info "Detected Debian/Ubuntu-based system"
            elif command_exists "yum" || command_exists "dnf"; then
                log_info "Detected RedHat/Fedora-based system"
            elif command_exists "pacman"; then
                log_info "Detected Arch-based system"
            fi
            ;;
    esac
    
    # Check for SSH key (needed for git@github.com URLs)
    local ssh_dir="$HOME/.ssh"
    if [ "$os_type" = "windows" ] && [ -n "$USERPROFILE" ]; then
        # Windows might use USERPROFILE/.ssh
        [ -d "$USERPROFILE/.ssh" ] && ssh_dir="$USERPROFILE/.ssh"
    fi
    
    # Check for various SSH key patterns
    local ssh_key_found=false
    if [ -d "$ssh_dir" ]; then
        # Check for standard key names and common patterns
        for key_pattern in "id_rsa" "id_ed25519" "id_ecdsa" "id_dsa" "id_*_github" "github_*"; do
            if ls "$ssh_dir"/$key_pattern 2>/dev/null | grep -v ".pub$" >/dev/null; then
                ssh_key_found=true
                break
            fi
        done
    fi
    
    if [ "$ssh_key_found" = false ]; then
        warnings+=("No SSH key found. You may have issues cloning with git@github.com URLs.")
        warnings+=("  Generate with: ssh-keygen -t ed25519 -C 'your-email@example.com'")
        warnings+=("  Or change CLAUDE_CONFIG_REPO to use HTTPS URL")
    fi
    
    # Report missing essential tools
    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install these tools before running this script."
        return 1
    fi
    
    # Report warnings
    if [ ${#warnings[@]} -gt 0 ]; then
        echo ""
        log_warn "=== Important Warnings ==="
        for warning in "${warnings[@]}"; do
            log_warn "$warning"
        done
        echo ""
        
        # Ask user if they want to continue (skip in dry-run or non-interactive mode)
        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY RUN] Would prompt for continuation"
        elif [ -n "${NONINTERACTIVE-}" ]; then
            log_info "Non-interactive mode: continuing despite warnings"
        else
            printf "%sWould you like to continue anyway? (y/N):%s " "$YELLOW" "$NC"
            read -r response < /dev/tty || read -r response
            case "$response" in
                [yY][eE][sS]|[yY])
                    log_info "Continuing with setup..."
                    ;;
                *)
                    log_info "Setup cancelled. Please install missing tools and try again."
                    show_install_help
                    return 1
                    ;;
            esac
        fi
    fi
    
    log_info "All essential requirements met!"
    return 0
}

# Provide platform-specific installation help
show_install_help() {
    local os_type=$(detect_os)
    
    echo ""
    log_info "=== Installation Help ==="
    
    case "$os_type" in
        macos)
            log_info "On macOS, you can install missing tools with:"
            log_info "  1. Install Homebrew: /bin/bash -c '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'"
            log_info "  2. Install Node.js: brew install node"
            log_info "  3. Install Claude Code: npm install -g @anthropic-ai/claude-code"
            log_info "  4. Generate SSH key: ssh-keygen -t ed25519 -C 'your-email@example.com'"
            ;;
        linux)
            log_info "On Linux, install missing tools with your package manager:"
            log_info "  Ubuntu/Debian: sudo apt update && sudo apt install git nodejs npm"
            log_info "  Fedora/RHEL: sudo dnf install git nodejs npm"
            log_info "  Arch: sudo pacman -S git nodejs npm"
            log_info "  Then: npm install -g @anthropic-ai/claude-code"
            ;;
        windows)
            if is_wsl; then
                log_info "On WSL, install missing tools with:"
                log_info "  sudo apt update && sudo apt install git nodejs npm"
                log_info "  Then: npm install -g @anthropic-ai/claude-code"
            else
                log_info "On Windows (Git Bash/MSYS2), install:"
                log_info "  1. Git: https://git-scm.com/download/win"
                log_info "  2. Node.js: https://nodejs.org/en/download/"
                log_info "  3. Then: npm install -g @anthropic-ai/claude-code"
                log_info ""
                log_info "Alternative: Use winget (Windows Package Manager):"
                log_info "  winget install Git.Git"
                log_info "  winget install OpenJS.NodeJS"
            fi
            ;;
    esac
    
    echo ""
}

# Create Claude directory if it doesn't exist
init_claude_dir() {
    if [ ! -d "$CLAUDE_HOME" ]; then
        log_info "Creating Claude home directory: $CLAUDE_HOME"
        mkdir -p "$CLAUDE_HOME"
    fi
    
    # Always ensure commands and logs directories exist
    mkdir -p "$CLAUDE_HOME/commands"
    mkdir -p "$CLAUDE_HOME/logs"
}

# Clone or update configuration repository
sync_repo() {
    if [ -d "$CLAUDE_CONFIG_DIR/.git" ]; then
        log_info "Updating existing configuration repository..."
        cd "$CLAUDE_CONFIG_DIR" || return 1
        
        # Get current branch
        local current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
        
        # Try to pull, handle errors gracefully
        if ! git pull origin "${current_branch:-main}" 2>/dev/null; then
            if ! git pull origin master 2>/dev/null; then
                log_warn "Could not update repository, continuing with existing version"
                log_warn "You may want to manually update with: cd $CLAUDE_CONFIG_DIR && git pull"
            fi
        else
            log_info "Repository updated successfully"
        fi
        cd "$OLDPWD" || true
    else
        log_info "Cloning configuration repository..."
        log_info "From: $CLAUDE_CONFIG_REPO"
        log_info "To: $CLAUDE_CONFIG_DIR"
        
        # Test SSH connection first if using git@github.com
        if [[ "$CLAUDE_CONFIG_REPO" == git@github.com:* ]]; then
            log_info "Testing SSH connection to GitHub..."
            if ! ssh -o ConnectTimeout=5 -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
                log_warn "SSH authentication to GitHub may not be configured"
                log_warn "You can either:"
                log_warn "  1. Set up SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
                log_warn "  2. Use HTTPS URL: export CLAUDE_CONFIG_REPO='https://github.com/maxxentropy/claudeops.git'"
                
                # On Windows, provide additional help
                if [ "$os_type" = "windows" ]; then
                    log_warn ""
                    log_warn "On Windows, make sure:"
                    log_warn "  - SSH agent is running: eval \$(ssh-agent -s)"
                    log_warn "  - Your key is added: ssh-add ~/.ssh/id_ed25519"
                fi
            fi
        fi
        
        if ! git clone "$CLAUDE_CONFIG_REPO" "$CLAUDE_CONFIG_DIR"; then
            log_error "Failed to clone configuration repository"
            log_error "This might be due to:"
            log_error "  1. No SSH key configured (run: ssh-keygen -t ed25519)"
            log_error "  2. SSH key not added to GitHub"
            log_error "  3. Repository doesn't exist or is private"
            log_error "  4. Network connectivity issues"
            echo ""
            log_info "Try using HTTPS instead:"
            log_info "  export CLAUDE_CONFIG_REPO='https://github.com/maxxentropy/claudeops.git'"
            log_info "  Then run this script again"
            return 1
        fi
        
        log_info "Repository cloned successfully"
    fi
}

# Link configuration files
link_configs() {
    local os_type=$(detect_os)
    
    log_info "Detected OS: $os_type"
    
    # Link CLAUDE.md (use CLAUDE-SYSTEM.md as the system-level config)
    log_info "Linking CLAUDE.md..."
    # Remove existing file/link if it exists
    [ -e "$CLAUDE_HOME/CLAUDE.md" ] && rm -f "$CLAUDE_HOME/CLAUDE.md"
    
    # Use cp instead of ln on Windows if symlinks aren't supported
    local link_cmd="ln -sf"
    if [ "$os_type" = "windows" ] && ! ln -sf "$0" "$0.test" 2>/dev/null; then
        rm -f "$0.test" 2>/dev/null
        link_cmd="cp -f"
        log_info "Note: Using file copy instead of symlinks (Windows limitation)"
    fi
    rm -f "$0.test" 2>/dev/null
    
    if [ -f "$CLAUDE_CONFIG_DIR/CLAUDE-SYSTEM.md" ]; then
        $link_cmd "$CLAUDE_CONFIG_DIR/CLAUDE-SYSTEM.md" "$CLAUDE_HOME/CLAUDE.md"
    elif [ -f "$CLAUDE_CONFIG_DIR/CLAUDE.md" ]; then
        $link_cmd "$CLAUDE_CONFIG_DIR/CLAUDE.md" "$CLAUDE_HOME/CLAUDE.md"
    else
        log_warn "No CLAUDE.md file found in config repository"
    fi
    
    # Link global settings
    log_info "Linking global settings..."
    [ -e "$CLAUDE_HOME/settings.json" ] && rm -f "$CLAUDE_HOME/settings.json"
    
    if [ -f "$CLAUDE_CONFIG_DIR/settings/global.json" ]; then
        $link_cmd "$CLAUDE_CONFIG_DIR/settings/global.json" "$CLAUDE_HOME/settings.json"
    else
        log_warn "No global settings found"
    fi
    
    # Link platform-specific settings
    [ -e "$CLAUDE_HOME/settings.local.json" ] && rm -f "$CLAUDE_HOME/settings.local.json"
    
    if [ "$os_type" != "unknown" ] && [ -f "$CLAUDE_CONFIG_DIR/settings/$os_type.json" ]; then
        log_info "Linking $os_type-specific settings..."
        $link_cmd "$CLAUDE_CONFIG_DIR/settings/$os_type.json" "$CLAUDE_HOME/settings.local.json"
    else
        log_warn "No platform-specific settings found for $os_type"
    fi
}

# Sync custom commands
sync_commands() {
    log_info "Syncing custom commands..."
    
    # Copy all commands, preserving directory structure
    if [ -d "$CLAUDE_CONFIG_DIR/commands" ] && [ "$(ls -A "$CLAUDE_CONFIG_DIR/commands" 2>/dev/null)" ]; then
        # Use different copy command based on OS
        if [ "$(detect_os)" = "windows" ]; then
            # Windows might not handle cp -r well
            xcopy "$CLAUDE_CONFIG_DIR/commands" "$CLAUDE_HOME/commands" /E /I /Y 2>/dev/null || \
            cp -r "$CLAUDE_CONFIG_DIR/commands/"* "$CLAUDE_HOME/commands/" 2>/dev/null || true
        else
            cp -r "$CLAUDE_CONFIG_DIR/commands/"* "$CLAUDE_HOME/commands/" 2>/dev/null || true
        fi
        
        # Make command files executable (skip on Windows as it doesn't use execute bit)
        if [ "$(detect_os)" != "windows" ] || is_wsl; then
            find "$CLAUDE_HOME/commands" -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
        fi
        
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
    case "$os_type" in
        macos)
            # macOS uses zsh by default since Catalina
            if [ -f "$HOME/.zshrc" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
                shell_rc="$HOME/.zshrc"
            elif [ -f "$HOME/.bash_profile" ]; then
                # macOS prefers .bash_profile over .bashrc
                shell_rc="$HOME/.bash_profile"
            else
                shell_rc="$HOME/.zshrc"  # Default to zsh on modern macOS
            fi
            ;;
        windows)
            # Windows Git Bash/MSYS2/Cygwin
            if [ -f "$HOME/.bashrc" ]; then
                shell_rc="$HOME/.bashrc"
            elif [ -f "$HOME/.bash_profile" ]; then
                shell_rc="$HOME/.bash_profile"
            else
                shell_rc="$HOME/.bashrc"
            fi
            # WSL might use different shell
            if is_wsl; then
                if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
                    shell_rc="$HOME/.zshrc"
                fi
            fi
            ;;
        linux)
            # Linux systems
            if [ -n "$ZSH_VERSION" ]; then
                shell_rc="$HOME/.zshrc"
            elif [ -n "$BASH_VERSION" ]; then
                shell_rc="$HOME/.bashrc"
            elif [ -f "$HOME/.zshrc" ] && command_exists "zsh"; then
                shell_rc="$HOME/.zshrc"
            elif [ -f "$HOME/.bashrc" ]; then
                shell_rc="$HOME/.bashrc"
            else
                shell_rc="$HOME/.bashrc"  # Default to bash
            fi
            ;;
        *)
            # Unknown system, try to detect
            if [ -n "$ZSH_VERSION" ]; then
                shell_rc="$HOME/.zshrc"
            elif [ -n "$BASH_VERSION" ]; then
                shell_rc="$HOME/.bashrc"
            else
                shell_rc="$HOME/.bashrc"
            fi
            ;;
    esac
    
    if [ -z "$shell_rc" ]; then
        case "$os_type" in
            macos)    shell_rc="$HOME/.zshrc" ;;
            windows)  shell_rc="$HOME/.bashrc" ;;
            linux)    shell_rc="$HOME/.bashrc" ;;
            *)        shell_rc="$HOME/.bashrc" ;;
        esac
    fi
    
    # Create file if it doesn't exist
    if [ ! -f "$shell_rc" ]; then
        log_info "Creating shell configuration file: $shell_rc"
        mkdir -p "$(dirname "$shell_rc")"
        touch "$shell_rc" || {
            log_error "Failed to create $shell_rc"
            return 1
        }
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
alias ccsync='$HOME/claudeops/sync.sh'
alias cclog='tail -f $HOME/.claude/logs/claude.log 2>/dev/null || echo "No log file found"'
alias ccclear='claude /clear'

# Claude quick commands (POSIX-compatible functions)
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

# Windows-specific: Add .exe extension if needed
if [ "$(uname -s)" = *"MINGW"* ] || [ "$(uname -s)" = *"MSYS"* ]; then
    alias claude='claude.exe 2>/dev/null || claude'
fi

# Git investigation aliases and functions
git-investigate() {
    local file="$1"
    local lines="${2:-10}"
    echo -e "\n${GREEN}Investigating $file...${NC}"
    echo -e "\n${YELLOW}Recent commits:${NC}"
    git log --oneline -n "$lines" -- "$file"
    echo -e "\n${YELLOW}Press Enter to see detailed changes...${NC}"
    read
    git log -p -n 5 -- "$file"
}

git-search() {
    local pattern="$1"
    local path="${2:-.}"
    echo -e "${GREEN}Searching for '$pattern' in commit history...${NC}"
    git log --all --grep="$pattern" --oneline
    echo -e "\n${GREEN}Searching in code changes...${NC}"
    git log -p -S "$pattern" --oneline "$path"
}

git-why() {
    local file="$1"
    local line="$2"
    if [ -n "$line" ]; then
        git blame -L "$line,$line" "$file"
    else
        git blame "$file" | less
    fi
}

git-context() {
    local file="${1:-.}"
    echo -e "${GREEN}Recent activity summary:${NC}"
    git log --since="2 weeks ago" --oneline --graph "$file"
    echo -e "\n${GREEN}Active contributors:${NC}"
    git shortlog -sn --since="1 month ago" "$file"
    echo -e "\n${GREEN}Recent fixes:${NC}"
    git log --grep="^fix:" --oneline -10 "$file"
}

# Short aliases
alias gi='git-investigate'
alias gsearch='git-search'
alias gwhy='git-why'
alias gcontext='git-context'

# Development workflow helpers
alias verify='$HOME/claudeops/scripts/verify-changes.sh'
alias qc='$HOME/claudeops/scripts/quick-commit.sh'

EOF
    
    log_info "Aliases added. Run 'source $shell_rc' to apply them immediately"
}

# Create usage tracking script
create_usage_tracker() {
    log_info "Setting up usage tracking..."
    
    # Check if Node.js is installed
    if ! command_exists "node"; then
        log_warn "Node.js not found, skipping usage tracker setup"
        return
    fi
    
    # On Windows, check for node.exe as well
    if [ "$(detect_os)" = "windows" ] && ! command_exists "node.exe"; then
        log_warn "Node.js not found (node.exe), skipping usage tracker setup"
        return
    fi
    
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
    
    # Make executable (skip on Windows non-WSL)
    if [ "$(detect_os)" != "windows" ] || is_wsl; then
        chmod +x "$CLAUDE_HOME/track-usage.js" 2>/dev/null || true
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check if Claude is installed
    if ! command -v claude &> /dev/null; then
        log_warn "Claude Code is not installed. Install with: npm install -g @anthropic-ai/claude-code"
    else
        log_info "✓ Claude Code is installed"
    fi
    
    # Check configuration files
    if [ -f "$CLAUDE_HOME/CLAUDE.md" ]; then
        log_info "✓ CLAUDE.md is linked"
    else
        log_warn "✗ CLAUDE.md is not linked"
    fi
    
    if [ -f "$CLAUDE_HOME/settings.json" ]; then
        log_info "✓ Settings are configured"
    else
        log_warn "✗ Settings are not configured"
    fi
    
    # Check API key
    if [ -z "$CLAUDE_API_KEY" ]; then
        log_warn "CLAUDE_API_KEY environment variable is not set"
        log_warn "Add to your shell configuration: export CLAUDE_API_KEY='your-key-here'"
    else
        log_info "✓ API key is configured"
    fi
    
    log_info "Installation verification completed"
}

# Show what the script will do
show_plan() {
    local os_type=$(detect_os)
    
    echo ""
    log_info "=== Claude Code Configuration Sync Plan ==="
    log_info "This script will:"
    log_info "  1. Create ~/.claude directory structure"
    log_info "  2. Clone/update config from: $CLAUDE_CONFIG_REPO"
    log_info "  3. Create symbolic links for:"
    log_info "     - CLAUDE.md configuration"
    log_info "     - Global settings (settings.json)"
    log_info "     - Platform settings for $os_type"
    log_info "  4. Sync custom commands"
    log_info "  5. Add shell aliases to your shell config"
    log_info "  6. Create usage tracking script"
    log_info "  7. Verify the installation"
    echo ""
}

# Main execution
main() {
    log_info "Starting Claude Code configuration sync..."
    
    # Show the plan
    show_plan
    
    # Check requirements first
    if ! check_requirements; then
        log_error "Requirements check failed. Exiting."
        return 1
    fi
    
    init_claude_dir
    sync_repo || { log_error "Failed to sync repository"; return 1; }
    link_configs
    sync_commands
    setup_aliases
    create_usage_tracker
    verify_installation
    
    log_info "Sync completed successfully!"
    
    # Provide appropriate source command based on what was configured
    local shell_rc=""
    if [ -f "$HOME/.zshrc" ] && grep -q "# Claude Code Aliases" "$HOME/.zshrc" 2>/dev/null; then
        shell_rc="~/.zshrc"
    elif [ -f "$HOME/.bash_profile" ] && grep -q "# Claude Code Aliases" "$HOME/.bash_profile" 2>/dev/null; then
        shell_rc="~/.bash_profile"
    elif [ -f "$HOME/.bashrc" ] && grep -q "# Claude Code Aliases" "$HOME/.bashrc" 2>/dev/null; then
        shell_rc="~/.bashrc"
    fi
    
    if [ -n "$shell_rc" ]; then
        log_info "Run 'source $shell_rc' to load aliases"
        
        # Windows-specific note
        if [ "$(detect_os)" = "windows" ] && ! is_wsl; then
            log_info "Note: On Windows, you may need to restart your terminal"
        fi
    fi
}

# Quick fix function for common issues
quick_fix() {
    local issue="$1"
    
    case "$issue" in
        "ssh")
            log_info "Generating SSH key..."
            mkdir -p "$HOME/.ssh"
            chmod 700 "$HOME/.ssh"
            
            local email=$(git config --global user.email || echo 'your-email@example.com')
            if ! ssh-keygen -t ed25519 -C "$email" -f "$HOME/.ssh/id_ed25519" -N ""; then
                # Fallback to RSA if ed25519 fails
                log_warn "Ed25519 failed, trying RSA..."
                ssh-keygen -t rsa -b 4096 -C "$email" -f "$HOME/.ssh/id_rsa" -N ""
            fi
            
            log_info "SSH key generated. Add it to GitHub:"
            log_info "  1. Copy your public key:"
            if [ -f "$HOME/.ssh/id_ed25519.pub" ]; then
                log_info "     cat ~/.ssh/id_ed25519.pub"
            else
                log_info "     cat ~/.ssh/id_rsa.pub"
            fi
            log_info "  2. Go to https://github.com/settings/keys"
            log_info "  3. Click 'New SSH key' and paste the key"
            
            # Windows-specific SSH setup
            if [ "$os_type" = "windows" ]; then
                log_info ""
                log_info "On Windows, also run:"
                log_info "  eval \$(ssh-agent -s)"
                log_info "  ssh-add ~/.ssh/id_ed25519"
            fi
            ;;
        "https")
            log_info "Switching to HTTPS URL..."
            export CLAUDE_CONFIG_REPO="https://github.com/maxxentropy/claudeops.git"
            log_info "Set CLAUDE_CONFIG_REPO to: $CLAUDE_CONFIG_REPO"
            log_info "Re-running sync..."
            main
            ;;
        "node")
            local os_type=$(detect_os)
            if [ "$os_type" = "macos" ] && command_exists "brew"; then
                log_info "Installing Node.js via Homebrew..."
                brew install node
            elif [ "$os_type" = "windows" ]; then
                log_info "Installing Node.js on Windows..."
                log_info "Option 1: Download from https://nodejs.org/"
                log_info "Option 2: Use Chocolatey: choco install nodejs"
                log_info "Option 3: Use Scoop: scoop install nodejs"
            else
                log_info "Please install Node.js from: https://nodejs.org/"
            fi
            ;;
        *)
            log_error "Unknown fix option: $issue"
            log_info "Available fixes: ssh, https, node"
            ;;
    esac
}

# Show help
show_help() {
    echo "Claude Code Configuration Sync Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --dry-run, -n    Show what would be done without making changes"
    echo "  --fix <issue>    Quick fix for common issues (ssh, https, node)"
    echo "  --test           Run basic functionality tests"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0               # Run normal sync"
    echo "  $0 --dry-run     # Preview changes without applying"
    echo "  $0 --fix ssh     # Generate SSH key for GitHub"
    echo "  $0 --fix https   # Switch to HTTPS repository URL"
    echo ""
    echo "Environment variables:"
    echo "  CLAUDE_CONFIG_REPO   Repository URL (default: git@github.com:maxxentropy/claudeops.git)"
    echo "  CLAUDE_CONFIG_DIR    Local config directory (default: ~/claudeops)"
    echo "  CLAUDE_HOME          Claude home directory (default: ~/.claude)"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            if [ -n "$2" ]; then
                quick_fix "$2"
                exit $?
            else
                echo "Error: --fix requires an argument (ssh, https, node)"
                exit 1
            fi
            ;;
        --dry-run|-n)
            DRY_RUN=true
            echo "DRY RUN MODE: No changes will be made"
            echo ""
            shift
            ;;
        --test)
            if [ -f "./test-sync.sh" ]; then
                exec ./test-sync.sh
            else
                echo "Error: test-sync.sh not found"
                exit 1
            fi
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"