#!/bin/bash

# Claude Code Configuration Installer
# Installs slash command system from claudeops repository to global Claude directory

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_PATH="${SCRIPT_DIR}/.claude"
TARGET_PATH="${HOME}/.claude"
BACKUP_PATH="${HOME}/.claude-backup-$(date +%Y%m%d-%H%M%S)"

# Flags
FORCE=false
BACKUP=false
DRY_RUN=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${CYAN}$1${NC}"; }
log_success() { echo -e "${GREEN}$1${NC}"; }
log_warning() { echo -e "${YELLOW}$1${NC}"; }
log_error() { echo -e "${RED}$1${NC}"; }
log_header() { echo -e "${MAGENTA}$1${NC}"; }

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Installs Claude Code configuration from claudeops repository to user's global Claude directory.

OPTIONS:
    -f, --force     Overwrite existing files without prompting
    -b, --backup    Create backup of existing configuration
    -d, --dry-run   Show what would be copied without making changes
    -h, --help      Show this help message

EXAMPLES:
    $0                      # Install with user prompts
    $0 -f -b               # Force install with backup
    $0 -d                  # Dry run to see what would be copied

EOF
}

check_prerequisites() {
    log_info "🔍 Checking prerequisites..."
    
    if [[ ! -d "$SOURCE_PATH" ]]; then
        log_error "❌ Source .claude directory not found at: $SOURCE_PATH"
        log_error "   Make sure you're running this script from the claudeops repository root."
        return 1
    fi
    
    log_success "✅ Source directory found"
    return 0
}

create_backup() {
    if [[ "$BACKUP" != "true" ]]; then
        return 0
    fi
    
    if [[ -d "$TARGET_PATH" ]]; then
        log_info "📦 Creating backup at: $BACKUP_PATH"
        
        if [[ "$DRY_RUN" != "true" ]]; then
            if cp -r "$TARGET_PATH" "$BACKUP_PATH"; then
                log_success "✅ Backup created successfully"
            else
                log_error "❌ Failed to create backup"
                return 1
            fi
        else
            log_info "   [DRY RUN] Would create backup"
        fi
    else
        log_info "ℹ️  No existing configuration to backup"
    fi
    
    return 0
}

copy_configuration() {
    log_info "📋 Analyzing files to copy..."
    
    # Count files
    local file_count=$(find "$SOURCE_PATH" -type f | wc -l)
    log_info "   Found $file_count files to copy"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_header ""
        log_header "📝 DRY RUN - Files that would be copied:"
        
        while IFS= read -r -d '' file; do
            local relative_path="${file#$SOURCE_PATH/}"
            local target_file="$TARGET_PATH/$relative_path"
            
            if [[ -f "$target_file" ]]; then
                log_info "   [OVERWRITE] $relative_path"
            else
                log_info "   [NEW] $relative_path"
            fi
        done < <(find "$SOURCE_PATH" -type f -print0)
        
        return 0
    fi
    
    # Create target directory
    if [[ ! -d "$TARGET_PATH" ]]; then
        log_info "📁 Creating target directory: $TARGET_PATH"
        mkdir -p "$TARGET_PATH"
    fi
    
    # Copy files
    local copied_count=0
    local skipped_count=0
    
    while IFS= read -r -d '' file; do
        local relative_path="${file#$SOURCE_PATH/}"
        local target_file="$TARGET_PATH/$relative_path"
        local target_dir="$(dirname "$target_file")"
        
        # Create target directory if needed
        mkdir -p "$target_dir"
        
        # Check if file exists and handle accordingly
        if [[ -f "$target_file" && "$FORCE" != "true" ]]; then
            echo -n "File exists: $relative_path. Overwrite? (y/N/a=all): "
            read -r response
            case "$response" in
                [Aa]*)
                    FORCE=true
                    ;;
                [Yy]*)
                    ;;
                *)
                    log_warning "   ⏭️  Skipped: $relative_path"
                    ((skipped_count++))
                    continue
                    ;;
            esac
        fi
        
        if cp "$file" "$target_file"; then
            log_success "   ✅ Copied: $relative_path"
            ((copied_count++))
        else
            log_error "   ❌ Failed to copy: $relative_path"
        fi
        
    done < <(find "$SOURCE_PATH" -type f -print0)
    
    log_header ""
    log_header "📊 Copy Summary:"
    log_success "   ✅ Files copied: $copied_count"
    [[ $skipped_count -gt 0 ]] && log_warning "   ⏭️  Files skipped: $skipped_count"
    
    return 0
}

show_post_install() {
    log_header ""
    log_header "🎉 Claude Configuration Installation Complete!"
    log_info ""
    log_info "Your slash command system is now available in all Claude sessions:"
    
    log_header ""
    log_header "📋 Core Commands Available:"
    log_info "   /safe [task]     - Execute any task with full safety protocols"
    log_info "   /commit          - Verified commit with full testing"
    log_info "   /fix [issue]     - Systematic debugging workflow"
    log_info "   /config [type]   - Safe configuration changes"
    log_info "   /test [target]   - Generate comprehensive tests"
    log_info "   /build [platform]- Platform-specific builds"
    
    log_header ""
    log_header "📋 PRD Workflow Commands:"
    log_info "   /prdq [feature]  - Quick requirements document"
    log_info "   /prd [feature]   - Formal PRD creation"
    log_info "   /prd-decompose   - Break PRD into phases"
    log_info "   /prd-implement   - Execute PRD phases"
    
    log_header ""
    log_header "📋 Specialized Commands:"
    log_info "   /api-crud        - Generate CRUD APIs"
    log_info "   /mobile-scaffold - MAUI app scaffolding"
    log_info "   /context-prime   - Understand codebase"
    log_info "   /git-investigate - Analyze code history"
    log_info "   /refactor-safe   - Safe refactoring process"
    log_info "   /tdd             - Test-driven development"
    
    log_header ""
    log_header "📚 Documentation:"
    log_info "   Check .claude/README-slash-commands.md for complete documentation"
    log_info "   Use .claude/commands.md for command reference"
    
    if [[ "$BACKUP" == "true" && -d "$BACKUP_PATH" ]]; then
        log_header ""
        log_header "💾 Backup Location:"
        log_info "   Your previous configuration was backed up to:"
        log_info "   $BACKUP_PATH"
    fi
    
    log_header ""
    log_header "🚀 Next Steps:"
    log_info "   1. Restart Claude Code or start a new session"
    log_info "   2. Test with: /safe 'echo Hello World'"
    log_info "   3. Read the documentation in .claude/README-slash-commands.md"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE=true
            shift
            ;;
        -b|--backup)
            BACKUP=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_header "🔧 Claude Code Configuration Installer"
    log_info "   Repository: claudeops"
    log_info "   Target: $TARGET_PATH"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "   Mode: DRY RUN (no changes will be made)"
    fi
    
    echo ""
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    # Create backup if requested
    if ! create_backup; then
        exit 1
    fi
    
    # Copy configuration
    if ! copy_configuration; then
        log_error "❌ Configuration installation failed"
        exit 1
    fi
    
    # Show post-install instructions
    if [[ "$DRY_RUN" != "true" ]]; then
        show_post_install
    else
        log_success ""
        log_success "✅ DRY RUN completed successfully"
        log_info "   Run without -d to perform actual installation"
    fi
}

# Run main function
main "$@"