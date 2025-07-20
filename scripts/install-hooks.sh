#!/bin/bash
# Install git hooks for the professional workflow

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}Installing Git Hooks for Professional Workflow...${NC}"

# Get paths
REPO_ROOT="$(dirname "$(dirname "$0")")"
HOOKS_SOURCE="$REPO_ROOT/hooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not in a git repository root!${NC}"
    echo -e "${YELLOW}Please run from the repository root directory.${NC}"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$GIT_HOOKS_DIR"

# Copy hooks
for hook in pre-commit commit-msg; do
    source="$HOOKS_SOURCE/$hook"
    dest="$GIT_HOOKS_DIR/$hook"
    
    if [ -f "$source" ]; then
        cp "$source" "$dest"
        chmod +x "$dest"
        echo -e "${GREEN}✓ Installed $hook hook${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: $hook not found in $HOOKS_SOURCE${NC}"
    fi
done

# Install for current repo only or globally?
echo -n "Install hooks globally for all future repos? (y/N) "
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    # Set up global hooks
    GLOBAL_HOOKS_DIR="$HOME/.git-hooks"
    
    # Create global hooks directory
    mkdir -p "$GLOBAL_HOOKS_DIR"
    
    # Copy hooks to global directory
    for hook in pre-commit commit-msg; do
        source="$HOOKS_SOURCE/$hook"
        dest="$GLOBAL_HOOKS_DIR/$hook"
        if [ -f "$source" ]; then
            cp "$source" "$dest"
            chmod +x "$dest"
        fi
    done
    
    # Configure git to use global hooks
    git config --global core.hooksPath "$GLOBAL_HOOKS_DIR"
    echo -e "${GREEN}✓ Hooks installed globally in $GLOBAL_HOOKS_DIR${NC}"
    echo -e "  All new repos will use these hooks automatically"
fi

echo -e "\n${GREEN}✓ Git hooks installation complete!${NC}"
echo -e "\n${CYAN}The following hooks are now active:${NC}"
echo -e "  • pre-commit: Runs quick verification on changed files"
echo -e "  • commit-msg: Ensures proper commit format and adds [✓ VERIFIED] badge"
echo -e "\n${YELLOW}To bypass hooks in emergency: git commit --no-verify${NC}"