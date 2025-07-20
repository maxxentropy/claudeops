#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Installs Claude Code configuration from claudeops repository to user's global Claude directory.

.DESCRIPTION
    This script copies the entire .claude configuration directory from the claudeops repository
    to the user's global Claude Code configuration directory (~/.claude), enabling the slash
    command system and development workflows across all Claude sessions.

.PARAMETER Force
    Overwrites existing files without prompting for confirmation.

.PARAMETER Backup
    Creates a backup of existing configuration before installing new one.

.PARAMETER DryRun
    Shows what would be copied without actually performing the operation.

.EXAMPLE
    .\install-claude-config.ps1
    Installs the Claude configuration with user prompts for overwrites.

.EXAMPLE
    .\install-claude-config.ps1 -Force -Backup
    Creates backup and installs configuration, overwriting existing files.

.EXAMPLE
    .\install-claude-config.ps1 -DryRun
    Shows what files would be copied without making changes.
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$Backup,
    [switch]$DryRun
)

# Define paths
$SourcePath = Join-Path $PSScriptRoot ".claude"
$TargetPath = Join-Path $env:USERPROFILE ".claude"
$BackupPath = Join-Path $env:USERPROFILE ".claude-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Header = "Magenta"
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-Prerequisites {
    Write-ColorOutput "🔍 Checking prerequisites..." "Info"
    
    if (-not (Test-Path $SourcePath)) {
        Write-ColorOutput "❌ Source .claude directory not found at: $SourcePath" "Error"
        Write-ColorOutput "   Make sure you're running this script from the claudeops repository root." "Error"
        return $false
    }
    
    Write-ColorOutput "✅ Source directory found" "Success"
    return $true
}

function New-BackupIfRequested {
    if (-not $Backup) { return }
    
    if (Test-Path $TargetPath) {
        Write-ColorOutput "📦 Creating backup at: $BackupPath" "Info"
        
        if (-not $DryRun) {
            try {
                Copy-Item -Path $TargetPath -Destination $BackupPath -Recurse -Force
                Write-ColorOutput "✅ Backup created successfully" "Success"
            }
            catch {
                Write-ColorOutput "❌ Failed to create backup: $($_.Exception.Message)" "Error"
                return $false
            }
        } else {
            Write-ColorOutput "   [DRY RUN] Would create backup" "Info"
        }
    } else {
        Write-ColorOutput "ℹ️  No existing configuration to backup" "Info"
    }
    
    return $true
}

function Copy-ClaudeConfiguration {
    Write-ColorOutput "📋 Analyzing files to copy..." "Info"
    
    # Get all files to copy
    $FilesToCopy = Get-ChildItem -Path $SourcePath -Recurse -File
    $TotalFiles = $FilesToCopy.Count
    
    Write-ColorOutput "   Found $TotalFiles files to copy" "Info"
    
    if ($DryRun) {
        Write-ColorOutput "`n📝 DRY RUN - Files that would be copied:" "Header"
        foreach ($File in $FilesToCopy) {
            $RelativePath = $File.FullName.Substring($SourcePath.Length + 1)
            $TargetFile = Join-Path $TargetPath $RelativePath
            
            $Status = if (Test-Path $TargetFile) { "[OVERWRITE]" } else { "[NEW]" }
            Write-ColorOutput "   $Status $RelativePath" "Info"
        }
        return $true
    }
    
    # Create target directory if it doesn't exist
    if (-not (Test-Path $TargetPath)) {
        Write-ColorOutput "📁 Creating target directory: $TargetPath" "Info"
        New-Item -Path $TargetPath -ItemType Directory -Force | Out-Null
    }
    
    # Copy files
    $CopiedCount = 0
    $SkippedCount = 0
    
    foreach ($File in $FilesToCopy) {
        $RelativePath = $File.FullName.Substring($SourcePath.Length + 1)
        $TargetFile = Join-Path $TargetPath $RelativePath
        $TargetDir = Split-Path $TargetFile -Parent
        
        # Create target directory if needed
        if (-not (Test-Path $TargetDir)) {
            New-Item -Path $TargetDir -ItemType Directory -Force | Out-Null
        }
        
        # Check if file exists and handle accordingly
        if ((Test-Path $TargetFile) -and -not $Force) {
            $Response = Read-Host "File exists: $RelativePath. Overwrite? (y/N/a=all)"
            if ($Response -eq 'a') {
                $Force = $true
            } elseif ($Response -ne 'y') {
                Write-ColorOutput "   ⏭️  Skipped: $RelativePath" "Warning"
                $SkippedCount++
                continue
            }
        }
        
        try {
            Copy-Item -Path $File.FullName -Destination $TargetFile -Force
            Write-ColorOutput "   ✅ Copied: $RelativePath" "Success"
            $CopiedCount++
        }
        catch {
            Write-ColorOutput "   ❌ Failed to copy $RelativePath : $($_.Exception.Message)" "Error"
        }
    }
    
    Write-ColorOutput "`n📊 Copy Summary:" "Header"
    Write-ColorOutput "   ✅ Files copied: $CopiedCount" "Success"
    if ($SkippedCount -gt 0) {
        Write-ColorOutput "   ⏭️  Files skipped: $SkippedCount" "Warning"
    }
    
    return $CopiedCount -gt 0
}

function Show-PostInstallInstructions {
    Write-ColorOutput "`n🎉 Claude Configuration Installation Complete!" "Header"
    Write-ColorOutput "`nYour slash command system is now available in all Claude sessions:" "Info"
    
    Write-ColorOutput "`n📋 Core Commands Available:" "Header"
    Write-ColorOutput "   /safe [task]     - Execute any task with full safety protocols" "Info"
    Write-ColorOutput "   /commit          - Verified commit with full testing" "Info"
    Write-ColorOutput "   /fix [issue]     - Systematic debugging workflow" "Info"
    Write-ColorOutput "   /config [type]   - Safe configuration changes" "Info"
    Write-ColorOutput "   /test [target]   - Generate comprehensive tests" "Info"
    Write-ColorOutput "   /build [platform]- Platform-specific builds" "Info"
    
    Write-ColorOutput "`n📋 PRD Workflow Commands:" "Header"
    Write-ColorOutput "   /prdq [feature]  - Quick requirements document" "Info"
    Write-ColorOutput "   /prd [feature]   - Formal PRD creation" "Info"
    Write-ColorOutput "   /prd-decompose   - Break PRD into phases" "Info"
    Write-ColorOutput "   /prd-implement   - Execute PRD phases" "Info"
    
    Write-ColorOutput "`n📋 Specialized Commands:" "Header"
    Write-ColorOutput "   /api-crud        - Generate CRUD APIs" "Info"
    Write-ColorOutput "   /mobile-scaffold - MAUI app scaffolding" "Info"
    Write-ColorOutput "   /context-prime   - Understand codebase" "Info"
    Write-ColorOutput "   /git-investigate - Analyze code history" "Info"
    Write-ColorOutput "   /refactor-safe   - Safe refactoring process" "Info"
    Write-ColorOutput "   /tdd             - Test-driven development" "Info"
    
    Write-ColorOutput "`n📚 Documentation:" "Header"
    Write-ColorOutput "   Check .claude/README-slash-commands.md for complete documentation" "Info"
    Write-ColorOutput "   Use .claude/commands.md for command reference" "Info"
    
    if ($Backup -and (Test-Path $BackupPath)) {
        Write-ColorOutput "`n💾 Backup Location:" "Header"
        Write-ColorOutput "   Your previous configuration was backed up to:" "Info"
        Write-ColorOutput "   $BackupPath" "Info"
    }
    
    Write-ColorOutput "`n🚀 Next Steps:" "Header"
    Write-ColorOutput "   1. Restart Claude Code or start a new session" "Info"
    Write-ColorOutput "   2. Test with: /safe 'echo Hello World'" "Info"
    Write-ColorOutput "   3. Read the documentation in .claude/README-slash-commands.md" "Info"
}

# Main execution
try {
    Write-ColorOutput "🔧 Claude Code Configuration Installer" "Header"
    Write-ColorOutput "   Repository: claudeops" "Info"
    Write-ColorOutput "   Target: $TargetPath" "Info"
    
    if ($DryRun) {
        Write-ColorOutput "   Mode: DRY RUN (no changes will be made)" "Warning"
    }
    
    Write-ColorOutput ""
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    # Create backup if requested
    if (-not (New-BackupIfRequested)) {
        exit 1
    }
    
    # Copy configuration
    if (-not (Copy-ClaudeConfiguration)) {
        Write-ColorOutput "❌ Configuration installation failed" "Error"
        exit 1
    }
    
    # Show post-install instructions
    if (-not $DryRun) {
        Show-PostInstallInstructions
    } else {
        Write-ColorOutput "`n✅ DRY RUN completed successfully" "Success"
        Write-ColorOutput "   Run without -DryRun to perform actual installation" "Info"
    }
    
} catch {
    Write-ColorOutput "❌ Installation failed: $($_.Exception.Message)" "Error"
    exit 1
}