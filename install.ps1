# Claude Configuration Installer for Windows
# Simple, clean installation of claudeops to ~/.claude

Write-Host "🚀 Installing Claude configuration..." -ForegroundColor Cyan

$claudeDir = "$env:USERPROFILE\.claude"

# Backup existing configuration if present
if (Test-Path $claudeDir) {
    $backupDir = "$env:USERPROFILE\.claude.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "📦 Backing up existing ~/.claude to $backupDir" -ForegroundColor Yellow
    Move-Item $claudeDir $backupDir -Force
}

# Create target directory
New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null

# Copy all Claude configuration files
Write-Host "📋 Copying configuration files..." -ForegroundColor White
$items = @('commands', 'system', 'config', 'docs', 'data', 'cache', 'STRUCTURE.md')
foreach ($item in $items) {
    Copy-Item -Path $item -Destination $claudeDir -Recurse -Force
}

# Create .gitignore in target to protect user data
$gitignoreContent = @'
# User data
data/conversations/*
data/workspaces/*
data/todos/*
data/logs/*
!data/**/.gitkeep

# Cache files
cache/shell-snapshots/*
cache/statsig/*
!cache/**/.gitkeep

# Platform-specific
.DS_Store
Thumbs.db

# Editor files
*.swp
*.bak
*~
'@

Set-Content -Path "$claudeDir\.gitignore" -Value $gitignoreContent

Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Claude configuration is now available in ~/.claude" -ForegroundColor White
Write-Host "Your slash commands are ready to use!" -ForegroundColor White
Write-Host ""
Write-Host "Try: claude /safe 'echo Hello from Claude!'" -ForegroundColor Cyan