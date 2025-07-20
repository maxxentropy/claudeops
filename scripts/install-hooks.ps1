# Install git hooks for the professional workflow

$ErrorActionPreference = "Stop"

# Colors
Write-Host "Installing Git Hooks for Professional Workflow..." -ForegroundColor Cyan

# Get paths
$RepoRoot = Split-Path -Parent $PSScriptRoot
$HooksSource = Join-Path $RepoRoot "hooks"
$GitHooksDir = Join-Path $RepoRoot ".git/hooks"

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "Error: Not in a git repository root!" -ForegroundColor Red
    Write-Host "Please run from the repository root directory." -ForegroundColor Yellow
    exit 1
}

# Create hooks directory if it doesn't exist
if (-not (Test-Path $GitHooksDir)) {
    New-Item -ItemType Directory -Path $GitHooksDir -Force | Out-Null
}

# Copy hooks
$hooks = @("pre-commit", "commit-msg")
foreach ($hook in $hooks) {
    $source = Join-Path $HooksSource $hook
    $dest = Join-Path $GitHooksDir $hook
    
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $dest -Force
        Write-Host "✓ Installed $hook hook" -ForegroundColor Green
        
        # Make executable on Unix-like systems
        if ($IsLinux -or $IsMacOS) {
            chmod +x $dest
        }
    } else {
        Write-Host "⚠ Warning: $hook not found in $HooksSource" -ForegroundColor Yellow
    }
}

# Install for current repo only or globally?
$response = Read-Host "Install hooks globally for all future repos? (y/N)"
if ($response -match '^[Yy]') {
    # Set up global hooks
    $globalHooksDir = Join-Path $HOME ".git-hooks"
    
    # Create global hooks directory
    if (-not (Test-Path $globalHooksDir)) {
        New-Item -ItemType Directory -Path $globalHooksDir -Force | Out-Null
    }
    
    # Copy hooks to global directory
    foreach ($hook in $hooks) {
        $source = Join-Path $HooksSource $hook
        $dest = Join-Path $globalHooksDir $hook
        if (Test-Path $source) {
            Copy-Item -Path $source -Destination $dest -Force
        }
    }
    
    # Configure git to use global hooks
    git config --global core.hooksPath $globalHooksDir
    Write-Host "✓ Hooks installed globally in $globalHooksDir" -ForegroundColor Green
    Write-Host "  All new repos will use these hooks automatically" -ForegroundColor Gray
}

Write-Host "`n✓ Git hooks installation complete!" -ForegroundColor Green
Write-Host "`nThe following hooks are now active:" -ForegroundColor Cyan
Write-Host "  • pre-commit: Runs quick verification on changed files" -ForegroundColor White
Write-Host "  • commit-msg: Ensures proper commit format and adds [✓ VERIFIED] badge" -ForegroundColor White
Write-Host "`nTo bypass hooks in emergency: git commit --no-verify" -ForegroundColor Gray