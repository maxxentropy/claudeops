#!/usr/bin/env pwsh
# Claude Code Configuration Sync Script (PowerShell Version)
# Syncs configurations across Windows, Mac, and Linux environments

$ErrorActionPreference = "Stop"

# Configuration
$CLAUDE_CONFIG_REPO = if ($env:CLAUDE_CONFIG_REPO) { $env:CLAUDE_CONFIG_REPO } else { "git@github.com:maxxentropy/claudeops.git" }
$CLAUDE_CONFIG_DIR = Join-Path $HOME "claudeops"
$CLAUDE_HOME = Join-Path $HOME ".claude"

# Colors for output
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Green }
function Write-Warn { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Detect operating system
function Get-OS {
    if ($IsWindows -or $env:OS -match "Windows") { return "windows" }
    elseif ($IsMacOS) { return "macos" }
    elseif ($IsLinux) { return "linux" }
    else { return "unknown" }
}

# Create Claude directory if it doesn't exist
function Initialize-ClaudeDir {
    if (-not (Test-Path $CLAUDE_HOME)) {
        Write-Info "Creating Claude home directory: $CLAUDE_HOME"
        New-Item -ItemType Directory -Path $CLAUDE_HOME -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $CLAUDE_HOME "commands") -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $CLAUDE_HOME "logs") -Force | Out-Null
    }
}

# Clone or update configuration repository
function Sync-Repo {
    if (Test-Path (Join-Path $CLAUDE_CONFIG_DIR ".git")) {
        Write-Info "Updating existing configuration repository..."
        Push-Location $CLAUDE_CONFIG_DIR
        try {
            git pull origin main 2>$null || git pull origin master
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Info "Cloning configuration repository..."
        git clone $CLAUDE_CONFIG_REPO $CLAUDE_CONFIG_DIR
    }
}

# Create symbolic links (Windows requires admin or developer mode)
function New-SymbolicLink {
    param($Target, $Path)
    
    # Remove existing item if it exists
    if (Test-Path $Path) {
        Remove-Item $Path -Force
    }
    
    # Try to create symbolic link
    try {
        if ($IsWindows -or $env:OS -match "Windows") {
            # Try mklink first (requires admin)
            $result = cmd /c mklink /D "$Path" "$Target" 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "mklink failed"
            }
        }
        else {
            # Unix-style symlink
            ln -sf $Target $Path
        }
        Write-Info "Created link: $Path -> $Target"
    }
    catch {
        # Fallback to copying
        Write-Warn "Could not create symbolic link, copying instead: $Path"
        if (Test-Path $Target -PathType Container) {
            Copy-Item -Path $Target -Destination $Path -Recurse -Force
        }
        else {
            Copy-Item -Path $Target -Destination $Path -Force
        }
    }
}

# Link configuration files
function Link-Configs {
    $os_type = Get-OS
    
    Write-Info "Detected OS: $os_type"
    
    # Link CLAUDE.md (use CLAUDE-SYSTEM.md as the system-level config)
    Write-Info "Linking CLAUDE.md..."
    $claudeMdSource = if (Test-Path (Join-Path $CLAUDE_CONFIG_DIR "CLAUDE-SYSTEM.md")) {
        Join-Path $CLAUDE_CONFIG_DIR "CLAUDE-SYSTEM.md"
    }
    else {
        Join-Path $CLAUDE_CONFIG_DIR "CLAUDE.md"
    }
    
    Copy-Item -Path $claudeMdSource -Destination (Join-Path $CLAUDE_HOME "CLAUDE.md") -Force
    
    # Link global settings
    Write-Info "Linking global settings..."
    $globalSettings = Join-Path $CLAUDE_CONFIG_DIR "settings/global.json"
    if (Test-Path $globalSettings) {
        Copy-Item -Path $globalSettings -Destination (Join-Path $CLAUDE_HOME "settings.json") -Force
    }
    
    # Link platform-specific settings
    if ($os_type -ne "unknown") {
        Write-Info "Linking $os_type-specific settings..."
        $platformSettings = Join-Path $CLAUDE_CONFIG_DIR "settings/$os_type.json"
        if (Test-Path $platformSettings) {
            Copy-Item -Path $platformSettings -Destination (Join-Path $CLAUDE_HOME "settings.local.json") -Force
        }
    }
    else {
        Write-Warn "Unknown OS detected, skipping platform-specific settings"
    }
}

# Sync custom commands
function Sync-Commands {
    Write-Info "Syncing custom commands..."
    
    $commandsSource = Join-Path $CLAUDE_CONFIG_DIR "commands"
    $commandsDest = Join-Path $CLAUDE_HOME "commands"
    
    if (Test-Path $commandsSource) {
        # Copy all commands, preserving directory structure
        Get-ChildItem -Path $commandsSource -Recurse | ForEach-Object {
            $relativePath = $_.FullName.Substring($commandsSource.Length + 1)
            $destPath = Join-Path $commandsDest $relativePath
            
            if ($_.PSIsContainer) {
                New-Item -ItemType Directory -Path $destPath -Force | Out-Null
            }
            else {
                $destDir = Split-Path $destPath -Parent
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Copy-Item -Path $_.FullName -Destination $destPath -Force
            }
        }
        
        Write-Info "Commands synced successfully"
    }
    else {
        Write-Warn "No commands directory found in config repo"
    }
}

# Setup PowerShell aliases
function Setup-Aliases {
    $profilePath = $PROFILE.CurrentUserAllHosts
    
    # Create profile if it doesn't exist
    if (-not (Test-Path $profilePath)) {
        New-Item -ItemType File -Path $profilePath -Force | Out-Null
    }
    
    # Check if aliases are already added
    $profileContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
    if ($profileContent -match "Claude Code Configuration") {
        Write-Info "Claude aliases already configured in PowerShell profile"
        return
    }
    
    Write-Info "Adding Claude configuration to PowerShell profile..."
    
    # Add source command to profile
    Add-Content -Path $profilePath -Value @"

# Claude Code Configuration
. "$CLAUDE_CONFIG_DIR\powershell-profile.ps1"
"@
    
    Write-Info "PowerShell profile updated. Restart PowerShell to load aliases."
}

# Create usage tracking script
function Create-UsageTracker {
    Write-Info "Setting up usage tracking..."
    
    # The tracker is already in PowerShell format in ccusage.ps1
    Write-Info "Usage tracking configured"
}

# Verify installation
function Test-Installation {
    Write-Info "Verifying installation..."
    
    $errors = 0
    
    # Check if Claude is installed
    if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
        Write-Error "Claude Code is not installed. Install with: npm install -g @anthropic-ai/claude-code"
        $errors++
    }
    else {
        Write-Info "✓ Claude Code is installed"
    }
    
    # Check configuration files
    if (Test-Path (Join-Path $CLAUDE_HOME "CLAUDE.md")) {
        Write-Info "✓ CLAUDE.md is linked"
    }
    else {
        Write-Error "✗ CLAUDE.md is not linked"
        $errors++
    }
    
    if (Test-Path (Join-Path $CLAUDE_HOME "settings.json")) {
        Write-Info "✓ Settings are configured"
    }
    else {
        Write-Error "✗ Settings are not configured"
        $errors++
    }
    
    # Check API key (if using API auth)
    if (-not $env:CLAUDE_API_KEY) {
        Write-Warn "CLAUDE_API_KEY environment variable is not set"
        Write-Warn "If using API auth, set with: `$env:CLAUDE_API_KEY = 'your-key-here'"
    }
    else {
        Write-Info "✓ API key is configured"
    }
    
    if ($errors -eq 0) {
        Write-Info "Installation verified successfully!"
    }
    else {
        Write-Error "Installation verification failed with $errors errors"
        exit 1
    }
}

# Main execution
function Main {
    Write-Info "Starting Claude Code configuration sync..."
    
    Initialize-ClaudeDir
    Sync-Repo
    Link-Configs
    Sync-Commands
    Setup-Aliases
    Create-UsageTracker
    Test-Installation
    
    Write-Info "Sync completed successfully!"
    Write-Info "Restart PowerShell to load aliases"
}

# Run main function
Main