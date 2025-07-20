#!/bin/bash
# Claude Code Shell Integration for Bash
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
    # Show available commands
    echo "Claude Code Commands:"
    echo "  cc              - Run Claude"
    echo "  cct/ccth/ccthr  - Think modes"
    echo "  ccu             - Ultrathink mode"
    echo ""
    echo "Workflow Commands:"
    echo "  cccommit        - Safe commit workflow"
    echo "  ccfix           - Fix issues systematically"
    echo "  cctest          - Generate tests"
    echo "  ccsafe          - Run any task safely"
    echo "  ccbuild         - Build project"
    echo ""
    echo "Development:"
    echo "  cctdd           - Test-driven development"
    echo "  ccrefactor      - Safe refactoring"
    echo "  ccreview        - Review pull request"
    echo "  ccdocs          - Generate documentation"
    echo ""
    echo "PRD Workflow:"
    echo "  ccprd           - Create full PRD"
    echo "  ccprdq          - Quick PRD"
    echo ""
    echo "Functions:"
    echo "  ccnew <type>    - Create new project"
    echo "  cchelp          - Show this help"
}

# Quick verification function
ccverify() {
    # Verify changes before commit
    echo "Verifying changes..."
    if [ -f "package.json" ]; then
        npm test
    elif [ -f "*.csproj" ]; then
        dotnet test
    else
        echo "No test command found"
    fi
}

# Usage tracking
ccusage() {
    # Show Claude usage statistics
    if [ -f ~/.claude/system/scripts/ccusage.ps1 ]; then
        pwsh ~/.claude/system/scripts/ccusage.ps1 "$@"
    else
        echo "Usage tracking not available"
    fi
}

# Show Claude shortcuts on new terminal
echo "Claude Code ready! Type 'cchelp' for available commands."