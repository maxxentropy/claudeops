# Claude Code PowerShell Profile
# Add this to your PowerShell profile: notepad $PROFILE

# Claude Code Aliases
# cc is now a function defined below for project awareness
function cct { claude think }
function ccth { claude "think hard" }
function cchthr { claude "think harder" }
function ccu { claude ultrathink }
function ccpr { claude "Create a PR with all current changes" }
function ccfix { claude /fix-and-test }
function ccsync { 
    $syncScript = Join-Path $HOME "claudeops/sync.ps1"
    if (Test-Path $syncScript) {
        & $syncScript
    } else {
        # Fallback to bash script if on Unix-like system
        bash (Join-Path $HOME "claudeops/sync.sh")
    }
}
function ccclear { claude /clear }

# Claude Quick Commands
function ccnew {
    param([string]$projectType)
    claude "Create a new $projectType project with best practices and proper structure"
}

function cctest {
    claude "Generate comprehensive xUnit tests for the current file or selection"
}

function ccrefactor {
    claude "Refactor this code for better performance and maintainability"
}

function ccreview {
    claude "Review this code for bugs, security issues, and best practices"
}

# Development Shortcuts
function build { dotnet build }
function test { dotnet test }
function watch { dotnet watch run }
function restore { dotnet restore }

# Git shortcuts
function gs { git status }
function ga { git add . }
function gc { param([string]$message) git commit -m $message }
function gp { git push }
function gl { git pull }
function gco { param([string]$branch) git checkout $branch }
function gb { git branch }

# Navigation helpers
function repos { Set-Location "C:\Users\sean_\source\repos" }
function claudeops { Set-Location "C:\Users\sean_\source\repos\claudeops" }

# Project specific
function run-android { dotnet build -t:Run -f net8.0-android }
function run-ios { dotnet build -t:Run -f net8.0-ios }
function run-windows { dotnet build -t:Run -f net8.0-windows10.0.19041.0 }

# Utility functions
function touch {
    param([string]$file)
    New-Item -ItemType File -Name $file -Force
}

function mkcd {
    param([string]$dir)
    New-Item -ItemType Directory -Name $dir -Force
    Set-Location $dir
}

# Environment check
function Check-ClaudeSetup {
    Write-Host "Checking Claude Code Setup..." -ForegroundColor Cyan
    
    # Check Claude installation
    if (Get-Command claude -ErrorAction SilentlyContinue) {
        Write-Host "✓ Claude Code is installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Claude Code is not installed" -ForegroundColor Red
        Write-Host "  Install with: npm install -g @anthropic-ai/claude-code" -ForegroundColor Yellow
    }
    
    # Check API key
    if ($env:CLAUDE_API_KEY) {
        Write-Host "✓ CLAUDE_API_KEY is set" -ForegroundColor Green
    } else {
        Write-Host "✗ CLAUDE_API_KEY is not set" -ForegroundColor Red
        Write-Host "  Set with: `$env:CLAUDE_API_KEY = 'your-key-here'" -ForegroundColor Yellow
    }
    
    # Check config directory
    if (Test-Path "~/claudeops") {
        Write-Host "✓ Claude config directory exists" -ForegroundColor Green
    } else {
        Write-Host "✗ Claude config directory not found" -ForegroundColor Red
        Write-Host "  Run sync script to set up" -ForegroundColor Yellow
    }
}

# Project-aware Claude function
function cc {
    param([Parameter(ValueFromRemainingArguments=$true)]$args)
    
    # Check if we're in a project with its own CLAUDE.md
    if (Test-Path "./CLAUDE.md") {
        Write-Host "Using project-specific CLAUDE.md" -ForegroundColor Green
    } else {
        Write-Host "Using system-level configuration" -ForegroundColor Cyan
    }
    
    # Run claude with all arguments
    & claude $args
}

# Initialize new project with Claude support
function cc-init-project {
    param([string]$projectType = "generic")
    
    if (Test-Path "./CLAUDE.md") {
        Write-Host "CLAUDE.md already exists in this project" -ForegroundColor Yellow
        return
    }
    
    $templatePath = Join-Path $HOME "claudeops/templates/CLAUDE-PROJECT.md"
    
    if (Test-Path $templatePath) {
        Copy-Item $templatePath "./CLAUDE.md"
        Write-Host "Created CLAUDE.md for this project" -ForegroundColor Green
        Write-Host "Edit ./CLAUDE.md to customize project-specific settings" -ForegroundColor Cyan
    } else {
        Write-Host "Template not found at $templatePath" -ForegroundColor Red
    }
}

# Usage tracking
function ccusage {
    param([string]$Period = "month", [switch]$Detailed, [switch]$Export)
    $usageScript = Join-Path $HOME "claudeops/commands/shared/ccusage.ps1"
    if (Test-Path $usageScript) {
        & $usageScript -Period $Period -Detailed:$Detailed -Export:$Export
    } else {
        Write-Host "Usage tracking script not found at: $usageScript" -ForegroundColor Red
    }
}

# Show Claude shortcuts on startup
Write-Host "Claude Code shortcuts loaded! Key commands:" -ForegroundColor Cyan
Write-Host "  cc              - Run Claude (project-aware)" -ForegroundColor White
Write-Host "  cc-init-project - Create project CLAUDE.md" -ForegroundColor White
Write-Host "  cct      - Claude with thinking" -ForegroundColor White
Write-Host "  ccfix    - Fix and test code" -ForegroundColor White
Write-Host "  ccpr     - Create pull request" -ForegroundColor White
Write-Host "  ccsync   - Sync configurations" -ForegroundColor White
Write-Host "  ccusage  - View usage statistics" -ForegroundColor White
Write-Host "Run Check-ClaudeSetup to verify installation" -ForegroundColor Gray