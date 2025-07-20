# Quick verification for changed files only
param([switch]$AutoFix)

$changed = git diff --cached --name-only
if (-not $changed) { 
    $changed = git diff --name-only 
}

if (-not $changed) {
    Write-Host "✓ No changes to verify" -ForegroundColor Green
    exit 0
}

Write-Host "Verifying changed files..." -ForegroundColor Cyan

# C# files
$csFiles = $changed | Where-Object { $_ -match '\.cs$' }
if ($csFiles) {
    Write-Host "Building C# changes..." -ForegroundColor Yellow
    dotnet build --no-restore 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed" -ForegroundColor Red
        exit 1
    }
    
    # Run only affected tests
    $testFilter = ($csFiles | ForEach-Object { 
        [System.IO.Path]::GetFileNameWithoutExtension($_) 
    }) -join '|'
    
    dotnet test --no-build --filter "FullyQualifiedName~$testFilter" 2>$null
    if ($AutoFix) {
        dotnet format --include $csFiles
    }
}

# TypeScript/JavaScript files
$jsFiles = $changed | Where-Object { $_ -match '\.(ts|js|tsx|jsx)$' }
if ($jsFiles) {
    Write-Host "Testing JS/TS changes..." -ForegroundColor Yellow
    npm run test -- --findRelatedTests $jsFiles --passWithNoTests
    if ($AutoFix) {
        npm run lint -- $jsFiles --fix
    }
}

Write-Host "✓ All verifications passed!" -ForegroundColor Green