#!/bin/bash
# Smart commit with automatic verification

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Usage: $0 \"<type>: <message>\"${NC}"
    echo -e "${YELLOW}Example: $0 \"fix: UserService timeout issue\"${NC}"
    exit 1
fi

MESSAGE="$1"
SKIP_VERIFY=${2:-false}

# Verify message format
if ! echo "$MESSAGE" | grep -qE "^(feat|fix|refactor|docs|test|perf|chore|build|ci|style|revert):"; then
    echo -e "${RED}❌ Message must start with type: feat|fix|refactor|docs|test|perf|chore${NC}"
    echo -e "${YELLOW}Example: fix: UserService timeout issue${NC}"
    exit 1
fi

# Run verification unless skipped
if [ "$SKIP_VERIFY" != "--skip" ]; then
    echo -e "${CYAN}Running quick verification...${NC}"
    SCRIPT_DIR="$(dirname "$0")"
    if ! "$SCRIPT_DIR/verify-changes.sh"; then
        echo -e "${RED}❌ Fix issues before committing${NC}"
        exit 1
    fi
fi

# Add all changes and commit
git add -A
git commit -m "$MESSAGE

[✓ VERIFIED]"

echo -e "${GREEN}✓ Committed with verification!${NC}"