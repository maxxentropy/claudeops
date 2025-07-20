#!/bin/zsh
# Claude Code Shell Integration for Zsh
# Provides aliases and functions for Claude workflows

# Claude Code aliases
alias cc='claude'
alias cct='claude think'
alias ccth='claude think hard'
alias ccthr='claude think harder'
alias ccu='claude ultrathink'

# Slash command shortcuts
alias cccommit='claude /commit'
alias ccfix='claude /fix'
alias cctest='claude /test'
alias ccsafe='claude /safe'
alias ccpr='claude "Create a pull request with all current changes"'

# Development workflow aliases
alias ccbuild='claude /build'
alias cctdd='claude /tdd'
alias ccrefactor='claude /refactor-safe'
alias ccreview='claude /review-pr'
alias ccdocs='claude /create-docs'

# PRD workflow aliases
alias ccprd='claude /prd'
alias ccprdq='claude /prdq'

# Utility functions
ccnew() {
    # Create new project with Claude
    claude "/safe 'Create a new $1 project with best practices and proper structure'"
}

cchelp() {
    # Show available commands with colors
    print -P "%F{cyan}Claude Code Commands:%f"
    print -P "  %F{white}cc%f              - Run Claude"
    print -P "  %F{white}cct/ccth/ccthr%f  - Think modes"
    print -P "  %F{white}ccu%f             - Ultrathink mode"
    print ""
    print -P "%F{cyan}Workflow Commands:%f"
    print -P "  %F{white}cccommit%f        - Safe commit workflow"
    print -P "  %F{white}ccfix%f           - Fix issues systematically"
    print -P "  %F{white}cctest%f          - Generate tests"
    print -P "  %F{white}ccsafe%f          - Run any task safely"
    print -P "  %F{white}ccbuild%f         - Build project"
    print ""
    print -P "%F{cyan}Development:%f"
    print -P "  %F{white}cctdd%f           - Test-driven development"
    print -P "  %F{white}ccrefactor%f      - Safe refactoring"
    print -P "  %F{white}ccreview%f        - Review pull request"
    print -P "  %F{white}ccdocs%f          - Generate documentation"
    print ""
    print -P "%F{cyan}PRD Workflow:%f"
    print -P "  %F{white}ccprd%f           - Create full PRD"
    print -P "  %F{white}ccprdq%f          - Quick PRD"
    print ""
    print -P "%F{cyan}Functions:%f"
    print -P "  %F{white}ccnew <type>%f    - Create new project"
    print -P "  %F{white}cchelp%f          - Show this help"
}

# Quick verification function
ccverify() {
    # Verify changes before commit
    echo "Verifying changes..."
    if [[ -f "package.json" ]]; then
        npm test
    elif [[ -f *.csproj ]]; then
        dotnet test
    else
        echo "No test command found"
    fi
}

# Usage tracking
ccusage() {
    # Show Claude usage statistics
    if [[ -f ~/.claude/system/scripts/ccusage.ps1 ]]; then
        pwsh ~/.claude/system/scripts/ccusage.ps1 "$@"
    else
        echo "Usage tracking not available"
    fi
}

# Zsh-specific: Add completions
_claude_complete() {
    local -a commands
    commands=(
        '/commit:Safe commit with verification'
        '/fix:Systematic debugging'
        '/test:Generate comprehensive tests'
        '/safe:Wrap any task in safety'
        '/build:Build project'
        '/tdd:Test-driven development'
        '/refactor-safe:Safe refactoring'
        '/review-pr:Review pull request'
        '/prd:Create full PRD'
        '/prdq:Quick PRD'
    )
    _describe 'claude commands' commands
}

# Enable completion for claude command
compdef _claude_complete claude

# Show Claude shortcuts on new terminal (with color)
print -P "%F{cyan}Claude Code ready!%f Type %F{yellow}cchelp%f for available commands."