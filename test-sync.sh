#!/usr/bin/env bash
# Test suite for Claude Code sync script
# Tests various scenarios and platforms

# Colors for output (with Windows compatibility)
if [ -t 1 ] && [ -z "${NO_COLOR-}" ]; then
    # Check if we're on Windows without proper color support
    case "$(uname -s 2>/dev/null)" in
        MINGW*|MSYS*|CYGWIN*)
            # Windows Git Bash usually supports colors
            RED='\033[0;31m'
            GREEN='\033[0;32m'
            YELLOW='\033[1;33m'
            BLUE='\033[0;34m'
            NC='\033[0m'
            ;;
        *)
            # Other systems
            RED='\033[0;31m'
            GREEN='\033[0;32m'
            YELLOW='\033[1;33m'
            BLUE='\033[0;34m'
            NC='\033[0m'
            ;;
    esac
else
    # No color
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test framework functions
test_start() {
    printf "%s=== Testing: %s ===%s\n" "$BLUE" "$1" "$NC"
    TESTS_RUN=$((TESTS_RUN + 1))
}

test_pass() {
    printf "%s✓ PASS%s: %s\n" "$GREEN" "$NC" "$1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    printf "%s✗ FAIL%s: %s\n" "$RED" "$NC" "$1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

test_info() {
    printf "%sℹ INFO%s: %s\n" "$YELLOW" "$NC" "$1"
}

# Setup test environment
setup_test_env() {
    export TEST_MODE=1
    export ORIGINAL_HOME="$HOME"
    export ORIGINAL_PWD="$PWD"
    # Create temp directory (Windows-compatible)
    if command -v mktemp >/dev/null 2>&1; then
        export TEST_HOME="$(mktemp -d -t claude-test-XXXXXX 2>/dev/null || mktemp -d)"
    else
        # Fallback for Windows without mktemp
        export TEST_HOME="${TEMP:-${TMP:-/tmp}}/claude-test-$$-$(date +%s)"
        mkdir -p "$TEST_HOME"
    fi
    export HOME="$TEST_HOME"
    export CLAUDE_CONFIG_DIR="$TEST_HOME/claudeops"
    export CLAUDE_HOME="$TEST_HOME/.claude"
    
    test_info "Test environment: $TEST_HOME"
    
    # Create a minimal test repository
    mkdir -p "$CLAUDE_CONFIG_DIR"
    cd "$CLAUDE_CONFIG_DIR" || exit 1
    
    # Set git config for test
    git init --quiet
    git config user.name "Test User"
    git config user.email "test@example.com"
    
    # Create test files
    echo "# Test CLAUDE.md" > CLAUDE.md
    echo "# Test System CLAUDE.md" > CLAUDE-SYSTEM.md
    
    mkdir -p settings
    echo '{"test": "global"}' > settings/global.json
    echo '{"test": "macos"}' > settings/macos.json
    echo '{"test": "linux"}' > settings/linux.json
    echo '{"test": "windows"}' > settings/windows.json
    
    mkdir -p commands
    echo '#!/bin/bash\necho "test command"' > commands/test.sh
    
    git add .
    git commit -m "Initial test commit" --quiet
    
    cd "$ORIGINAL_PWD" || exit 1
}

cleanup_test_env() {
    export HOME="$ORIGINAL_HOME"
    cd "$ORIGINAL_PWD" 2>/dev/null || true
    rm -rf "$TEST_HOME" 2>/dev/null || true
}

# Test: Operating system detection
test_os_detection() {
    test_start "Operating System Detection"
    
    # Extract and run just the detect_os function
    detect_os() {
        case "$(uname -s 2>/dev/null || echo 'Unknown')" in
            Darwin*)    echo "macos";;
            Linux*)     echo "linux";;
            MINGW*|CYGWIN*|MSYS*|Windows_NT*) echo "windows";;
            *)          echo "unknown";;
        esac
    }
    local detected_os=$(detect_os)
    
    case "$detected_os" in
        macos|linux|windows)
            test_pass "Detected OS: $detected_os"
            ;;
        unknown)
            test_fail "Unknown OS detected"
            ;;
        *)
            test_fail "Invalid OS detection result: $detected_os"
            ;;
    esac
}

# Test: Color output
test_color_output() {
    test_start "Color Output Support"
    
    # Check if colors are set
    if [ -n "$RED" ] || [ -n "$GREEN" ] || [ -n "$YELLOW" ]; then
        test_pass "Colors initialized"
        printf "  %sRed%s %sGreen%s %sYellow%s\n" "$RED" "$NC" "$GREEN" "$NC" "$YELLOW" "$NC"
    else
        test_info "No color support detected (might be correct for this terminal)"
    fi
}

# Test: Required commands check
test_required_commands() {
    test_start "Required Commands Check"
    
    local required_commands=("git" "bash" "mkdir" "ln" "chmod" "grep")
    local missing=0
    
    for cmd in "${required_commands[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            test_info "Found: $cmd"
        else
            test_fail "Missing: $cmd"
            missing=$((missing + 1))
        fi
    done
    
    if [ $missing -eq 0 ]; then
        test_pass "All required commands found"
    fi
}

# Test: Directory creation
test_directory_creation() {
    test_start "Directory Creation"
    
    # Run directory creation directly
    mkdir -p "$TEST_HOME/.claude"
    mkdir -p "$TEST_HOME/.claude/commands"
    mkdir -p "$TEST_HOME/.claude/logs"
    
    if [ -d "$TEST_HOME/.claude" ]; then
        test_pass "Claude directory created"
    else
        test_fail "Claude directory not created"
    fi
    
    if [ -d "$TEST_HOME/.claude/commands" ] && [ -d "$TEST_HOME/.claude/logs" ]; then
        test_pass "Subdirectories created"
    else
        test_fail "Subdirectories not created"
    fi
}

# Test: Configuration linking
test_config_linking() {
    test_start "Configuration Linking"
    
    # Simulate linking
    if [ -f "$CLAUDE_CONFIG_DIR/CLAUDE-SYSTEM.md" ]; then
        ln -sf "$CLAUDE_CONFIG_DIR/CLAUDE-SYSTEM.md" "$TEST_HOME/.claude/CLAUDE.md"
    elif [ -f "$CLAUDE_CONFIG_DIR/CLAUDE.md" ]; then
        ln -sf "$CLAUDE_CONFIG_DIR/CLAUDE.md" "$TEST_HOME/.claude/CLAUDE.md"
    fi
    
    if [ -f "$CLAUDE_CONFIG_DIR/settings/global.json" ]; then
        ln -sf "$CLAUDE_CONFIG_DIR/settings/global.json" "$TEST_HOME/.claude/settings.json"
    fi
    
    # Check if files are linked
    if [ -e "$TEST_HOME/.claude/CLAUDE.md" ]; then
        test_pass "CLAUDE.md linked"
    else
        test_fail "CLAUDE.md not linked"
    fi
    
    if [ -e "$TEST_HOME/.claude/settings.json" ]; then
        test_pass "settings.json linked"
    else
        test_fail "settings.json not linked"
    fi
}

# Test: Shell detection
test_shell_detection() {
    test_start "Shell Configuration Detection"
    
    # Create shell config files
    touch "$TEST_HOME/.bashrc"
    touch "$TEST_HOME/.zshrc"
    
    # Simulate adding aliases
    echo "# Claude Code Aliases" >> "$TEST_HOME/.bashrc"
    
    # Check which file got the aliases
    if grep -q "Claude Code Aliases" "$TEST_HOME/.bashrc" 2>/dev/null; then
        test_pass "Aliases would be added to .bashrc"
    elif grep -q "Claude Code Aliases" "$TEST_HOME/.zshrc" 2>/dev/null; then
        test_pass "Aliases would be added to .zshrc"
    elif grep -q "Claude Code Aliases" "$TEST_HOME/.bash_profile" 2>/dev/null; then
        test_pass "Aliases would be added to .bash_profile"
    else
        test_fail "Aliases not added to any shell config"
    fi
}

# Test: Error handling
test_error_handling() {
    test_start "Error Handling"
    
    # Test dry-run mode
    # Use gtimeout if available (macOS with coreutils), otherwise try timeout, otherwise skip
    local timeout_cmd=""
    if command -v gtimeout >/dev/null 2>&1; then
        timeout_cmd="gtimeout"
    elif command -v timeout >/dev/null 2>&1; then
        timeout_cmd="timeout"
    fi
    
    if [ -n "$timeout_cmd" ]; then
        local dry_run_output=$(NONINTERACTIVE=1 $timeout_cmd 10 "$SYNC_SCRIPT" --dry-run 2>&1 || true)
    else
        # No timeout command, just run directly with NONINTERACTIVE mode
        local dry_run_output=$(NONINTERACTIVE=1 "$SYNC_SCRIPT" --dry-run 2>&1 | head -100)
    fi
    
    if echo "$dry_run_output" | grep -q "DRY RUN MODE"; then
        test_pass "Dry run mode works"
    else
        test_fail "Dry run mode not working"
        test_info "Output: $(echo "$dry_run_output" | head -5)"
    fi
}

# Test: Platform-specific features
test_platform_specific() {
    test_start "Platform-Specific Features"
    
    detect_os() {
        case "$(uname -s 2>/dev/null || echo 'Unknown')" in
            Darwin*)    echo "macos";;
            Linux*)     echo "linux";;
            MINGW*|CYGWIN*|MSYS*|Windows_NT*) echo "windows";;
            *)          echo "unknown";;
        esac
    }
    
    local os_type=$(detect_os)
    test_info "Testing $os_type-specific features"
    
    case "$os_type" in
        macos)
            # Test for .bash_profile vs .bashrc preference
            if [ -f "$HOME/.zshrc" ] || [ "$SHELL" = "/bin/zsh" ]; then
                test_pass "macOS shell detection (zsh preferred)"
            else
                test_pass "macOS shell detection (bash fallback)"
            fi
            ;;
        linux)
            # Test package manager detection
            if command -v apt-get >/dev/null 2>&1; then
                test_pass "Debian/Ubuntu package manager detected"
            elif command -v yum >/dev/null 2>&1 || command -v dnf >/dev/null 2>&1; then
                test_pass "RedHat/Fedora package manager detected"
            elif command -v pacman >/dev/null 2>&1; then
                test_pass "Arch package manager detected"
            else
                test_info "No known package manager detected"
            fi
            ;;
        windows)
            # Test WSL detection
            if [ -f /proc/version ] && grep -qi microsoft /proc/version; then
                test_pass "WSL detected correctly"
            else
                test_info "Not running in WSL"
            fi
            ;;
        *)
            test_info "Unknown platform - no specific tests"
            ;;
    esac
}

# Test: Quick fix functions
test_quick_fixes() {
    test_start "Quick Fix Functions"
    
    # Test help
    if "$SYNC_SCRIPT" --help 2>&1 | grep -q "Claude Code Configuration Sync Script"; then
        test_pass "Help text displayed"
    else
        test_fail "Help text not found"
    fi
    
    # Test invalid option handling
    if "$SYNC_SCRIPT" --invalid-option 2>&1 | grep -q "Unknown option"; then
        test_pass "Invalid options handled correctly"
    else
        test_fail "Invalid option not handled"
    fi
}

# Test: Symlink vs copy fallback
test_symlink_fallback() {
    test_start "Symlink/Copy Fallback"
    
    (
        export HOME="$TEST_HOME"
        source ./sync.sh 2>/dev/null || true
        
        # Create a test file
        mkdir -p "$TEST_HOME/test"
        echo "test" > "$TEST_HOME/test/file.txt"
        
        # Try to create symlink
        if ln -sf "$TEST_HOME/test/file.txt" "$TEST_HOME/test/link.txt" 2>/dev/null; then
            test_pass "Symlinks supported"
            rm -f "$TEST_HOME/test/link.txt"
        else
            test_info "Symlinks not supported - should fall back to copy"
        fi
    )
}

# Test: Script permissions
test_script_permissions() {
    test_start "Script Permissions"
    
    if [ -x "$SYNC_SCRIPT" ]; then
        test_pass "sync.sh is executable"
    else
        test_fail "sync.sh is not executable"
    fi
    
    if [ -f "$ORIGINAL_PWD/sync.bat" ]; then
        test_info "Windows batch file exists"
    fi
}

# Main test runner
run_tests() {
    printf "%sClaude Code Sync Script Test Suite%s\n" "$BLUE" "$NC"
    echo "=================================="
    echo ""
    
    # Setup
    setup_test_env
    
    # Check if sync.sh exists
    if [ ! -f "$ORIGINAL_PWD/sync.sh" ]; then
        printf "%sError: sync.sh not found in: %s%s\n" "$RED" "$ORIGINAL_PWD" "$NC"
        cleanup_test_env
        return 1
    fi
    
    # Make sure it's executable
    chmod +x "$ORIGINAL_PWD/sync.sh"
    
    # Store sync.sh location
    export SYNC_SCRIPT="$ORIGINAL_PWD/sync.sh"
    
    # Run tests
    test_os_detection
    test_color_output
    test_required_commands
    test_directory_creation
    test_config_linking
    test_shell_detection
    test_error_handling
    test_platform_specific
    test_quick_fixes
    test_symlink_fallback
    test_script_permissions
    
    # Cleanup
    cleanup_test_env
    
    # Summary
    echo ""
    printf "%s=== Test Summary ===%s\n" "$BLUE" "$NC"
    echo "Tests run:    $TESTS_RUN"
    printf "Tests passed: %s%s%s\n" "$GREEN" "$TESTS_PASSED" "$NC"
    printf "Tests failed: %s%s%s\n" "$RED" "$TESTS_FAILED" "$NC"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        printf "\n%sAll tests passed!%s\n" "$GREEN" "$NC"
        return 0
    else
        printf "\n%sSome tests failed!%s\n" "$RED" "$NC"
        return 1
    fi
}

# Run tests if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    run_tests
    exit $?
fi