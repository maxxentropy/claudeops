#Requires -Version 5.1
# Claude Code Usage Analyzer
# Tracks and analyzes your Claude usage for ROI calculations

param(
    [string]$Period = "month",  # day, week, month, year
    [switch]$Detailed,
    [switch]$Export
)

$logPath = Join-Path $HOME ".claude/logs/usage.jsonl"
$now = Get-Date

# Initialize if log doesn't exist
if (-not (Test-Path $logPath)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $logPath) | Out-Null
    New-Item -ItemType File -Force -Path $logPath | Out-Null
}

# Read and parse usage logs
$logs = Get-Content $logPath | Where-Object { $_ } | ForEach-Object {
    $_ | ConvertFrom-Json
}

# Filter by period
$startDate = switch ($Period) {
    "day"   { $now.AddDays(-1) }
    "week"  { $now.AddDays(-7) }
    "month" { $now.AddMonths(-1) }
    "year"  { $now.AddYears(-1) }
    default { $now.AddMonths(-1) }
}

$filteredLogs = $logs | Where-Object { 
    [DateTime]$_.timestamp -gt $startDate 
}

# Calculate statistics
$stats = @{
    TotalCommands = $filteredLogs.Count
    TotalTokens = ($filteredLogs | Measure-Object -Property tokens -Sum).Sum
    EstimatedCost = ($filteredLogs | Measure-Object -Property estimatedCost -Sum).Sum
    UniqueCommands = ($filteredLogs | Select-Object -Property command -Unique).Count
    AverageTokensPerCommand = if ($filteredLogs.Count -gt 0) { 
        ($filteredLogs | Measure-Object -Property tokens -Average).Average 
    } else { 0 }
}

# Calculate time saved (assuming 10 minutes saved per command)
$timeSavedHours = [Math]::Round($stats.TotalCommands * 10 / 60, 2)
$valueSaved = $timeSavedHours * 100  # $100/hour
$roi = if ($stats.EstimatedCost -gt 0) { 
    [Math]::Round(($valueSaved - $stats.EstimatedCost) / $stats.EstimatedCost * 100, 2) 
} else { 0 }

# Display results
Write-Host "`nClaude Code Usage Report ($Period)" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Period: $($startDate.ToString('yyyy-MM-dd')) to $($now.ToString('yyyy-MM-dd'))" -ForegroundColor White
Write-Host ""
Write-Host "Commands Run: $($stats.TotalCommands)" -ForegroundColor Green
Write-Host "Unique Commands: $($stats.UniqueCommands)" -ForegroundColor Green
Write-Host "Total Tokens: $($stats.TotalTokens)" -ForegroundColor Yellow
Write-Host "Avg Tokens/Command: $([Math]::Round($stats.AverageTokensPerCommand, 0))" -ForegroundColor Yellow
Write-Host ""
Write-Host "Estimated Cost: `$$([Math]::Round($stats.EstimatedCost, 2))" -ForegroundColor Red
Write-Host "Time Saved: $timeSavedHours hours" -ForegroundColor Green
Write-Host "Value Created: `$$valueSaved" -ForegroundColor Green
Write-Host "ROI: $roi%" -ForegroundColor $(if ($roi -gt 0) { "Green" } else { "Red" })

if ($Detailed) {
    Write-Host "`nTop Commands:" -ForegroundColor Cyan
    $filteredLogs | Group-Object command | 
        Sort-Object Count -Descending | 
        Select-Object -First 10 | 
        ForEach-Object {
            Write-Host "  $($_.Count)x - $($_.Name)" -ForegroundColor White
        }
}

if ($Export) {
    $exportPath = "claude-usage-$(Get-Date -Format 'yyyy-MM-dd').csv"
    $filteredLogs | Export-Csv -Path $exportPath -NoTypeInformation
    Write-Host "`nExported to: $exportPath" -ForegroundColor Green
}