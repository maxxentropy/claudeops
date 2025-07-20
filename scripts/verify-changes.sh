#!/bin/bash
# Quick verification for changed files only

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get changed files
CHANGED=$(git diff --cached --name-only)
if [ -z "$CHANGED" ]; then
    CHANGED=$(git diff --name-only)
fi

if [ -z "$CHANGED" ]; then
    echo -e "${GREEN}✓ No changes to verify${NC}"
    exit 0
fi

echo -e "${CYAN}Verifying changed files...${NC}"

# Track if we found files to verify
VERIFIED_SOMETHING=false

# C# files
CS_FILES=$(echo "$CHANGED" | grep '\.cs$' || true)
if [ -n "$CS_FILES" ]; then
    echo -e "${YELLOW}Building C# changes...${NC}"
    if dotnet build --no-restore >/dev/null 2>&1; then
        # Extract test filter from filenames
        TEST_FILTER=""
        for file in $CS_FILES; do
            BASENAME=$(basename "$file" .cs)
            if [ -z "$TEST_FILTER" ]; then
                TEST_FILTER="$BASENAME"
            else
                TEST_FILTER="$TEST_FILTER|$BASENAME"
            fi
        done
        
        echo -e "${YELLOW}Testing C# changes...${NC}"
        if dotnet test --no-build --filter "FullyQualifiedName~$TEST_FILTER" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ C# tests passed${NC}"
        else
            echo -e "${RED}❌ C# tests failed${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Build failed${NC}"
        exit 1
    fi
    VERIFIED_SOMETHING=true
fi

# TypeScript/JavaScript files
JS_FILES=$(echo "$CHANGED" | grep -E '\.(ts|js|tsx|jsx)$' || true)
if [ -n "$JS_FILES" ]; then
    echo -e "${YELLOW}Testing JS/TS changes...${NC}"
    if npm test -- --findRelatedTests $JS_FILES --passWithNoTests >/dev/null 2>&1; then
        echo -e "${GREEN}✓ JS/TS tests passed${NC}"
    else
        echo -e "${RED}❌ JS/TS tests failed${NC}"
        exit 1
    fi
    VERIFIED_SOMETHING=true
fi

# Python files
PY_FILES=$(echo "$CHANGED" | grep '\.py$' || true)
if [ -n "$PY_FILES" ]; then
    echo -e "${YELLOW}Testing Python changes...${NC}"
    if command -v pytest >/dev/null 2>&1; then
        if pytest $PY_FILES >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Python tests passed${NC}"
        else
            echo -e "${RED}❌ Python tests failed${NC}"
            exit 1
        fi
    fi
    VERIFIED_SOMETHING=true
fi

if [ "$VERIFIED_SOMETHING" = true ]; then
    echo -e "${GREEN}✓ All verifications passed!${NC}"
else
    echo -e "${YELLOW}No testable files in changes${NC}"
fi

exit 0