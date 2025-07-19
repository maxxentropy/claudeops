# Claude Code PowerShell Profile
# Add this to your PowerShell profile: notepad $PROFILE

# Claude Code Aliases
Set-Alias cc claude
function cct { claude think }
function ccth { claude "think hard" }
function cchthr { claude "think harder" }
function ccu { claude ultrathink }
function ccpr { claude "Create a PR with all current changes" }
function ccfix { claude /fix-and-test }
function ccsync { ~/.claude-config/sync.sh }
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
function claude-config { Set-Location "~/.claude-config" }

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
    if (Test-Path "~/.claude-config") {
        Write-Host "✓ Claude config directory exists" -ForegroundColor Green
    } else {
        Write-Host "✗ Claude config directory not found" -ForegroundColor Red
        Write-Host "  Run sync script to set up" -ForegroundColor Yellow
    }
}

# Show Claude shortcuts on startup
Write-Host "Claude Code shortcuts loaded! Key commands:" -ForegroundColor Cyan
Write-Host "  cc       - Run Claude" -ForegroundColor White
Write-Host "  cct      - Claude with thinking" -ForegroundColor White
Write-Host "  ccfix    - Fix and test code" -ForegroundColor White
Write-Host "  ccpr     - Create pull request" -ForegroundColor White
Write-Host "  ccsync   - Sync configurations" -ForegroundColor White
Write-Host "Run Check-ClaudeSetup to verify installation" -ForegroundColor Gray