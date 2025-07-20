# Smart commit with automatic verification
param(
    [Parameter(Mandatory=$true)]
    [string]$Message,
    [switch]$Skip
)

if (-not $Skip) {
    Write-Host "Running quick verification..." -ForegroundColor Cyan
    & "$PSScriptRoot\verify-changes.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Fix issues before committing" -ForegroundColor Red
        exit 1
    }
}

# Parse message to ensure it follows format
if ($Message -notmatch '^(feat|fix|refactor|docs|test|perf|chore):') {
    Write-Host "❌ Message must start with type: feat|fix|refactor|docs|test|perf|chore" -ForegroundColor Red
    Write-Host "Example: fix: UserService timeout issue" -ForegroundColor Yellow
    exit 1
}

# Add files and commit
git add -A
git commit -m "$Message`n`n[✓ VERIFIED]"

Write-Host "✓ Committed with verification!" -ForegroundColor Green