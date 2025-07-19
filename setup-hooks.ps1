#!/usr/bin/env pwsh
# Setup Claude Code hooks for usage tracking

$CLAUDE_HOME = Join-Path $HOME ".claude"
$HOOKS_DIR = Join-Path $CLAUDE_HOME "hooks"

# Create hooks directory
if (-not (Test-Path $HOOKS_DIR)) {
    New-Item -ItemType Directory -Path $HOOKS_DIR -Force | Out-Null
}

# Create post-command hook for usage tracking
$postCommandHook = @'
#!/usr/bin/env node
// Post-command hook for usage tracking

const fs = require('fs');
const path = require('path');
const os = require('os');

const logFile = path.join(os.homedir(), '.claude', 'logs', 'usage.jsonl');
const logsDir = path.dirname(logFile);

// Ensure logs directory exists
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

// Extract command info from environment or args
const command = process.env.CLAUDE_COMMAND || process.argv[2] || 'unknown';
const tokens = parseInt(process.env.CLAUDE_TOKENS || '1000');
const estimatedCost = parseFloat(process.env.CLAUDE_COST || '0.02');

// Log usage
const entry = {
    timestamp: new Date().toISOString(),
    command: command,
    tokens: tokens,
    estimatedCost: estimatedCost,
    platform: process.platform
};

fs.appendFileSync(logFile, JSON.stringify(entry) + '\n');
'@

# Write the hook file
$hookPath = Join-Path $HOOKS_DIR "post-command.js"
Set-Content -Path $hookPath -Value $postCommandHook -Encoding UTF8

# Make executable on Unix-like systems
if ($IsLinux -or $IsMacOS) {
    chmod +x $hookPath
}

Write-Host "Claude Code hooks configured successfully!" -ForegroundColor Green
Write-Host "Usage will be tracked in: $(Join-Path $CLAUDE_HOME 'logs/usage.jsonl')" -ForegroundColor Cyan