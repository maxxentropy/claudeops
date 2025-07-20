#!/usr/bin/env bash
# Manual test script for sync.sh

echo "=== Testing Claude Code Sync Script ==="
echo ""

echo "1. Testing help:"
./sync.sh --help | head -5
echo ""

echo "2. Testing dry-run mode:"
timeout 10 ./sync.sh --dry-run 2>&1 | grep -E "(DRY RUN MODE|Would create|Would link|Would clone)"
echo ""

echo "3. Testing on current platform:"
uname -s
echo ""

echo "=== Tests complete ==="