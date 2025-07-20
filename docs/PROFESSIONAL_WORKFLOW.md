# Professional Development Workflow

## The Three-Stage Verification Pipeline

### Stage 1: Rapid Development (Inner Loop)
**Goal**: Fast feedback while coding
```bash
# Watch mode for immediate feedback
dotnet watch test --filter "FullyQualifiedName~CurrentClass"
# or
npm run test:watch -- --testNamePattern="current feature"
```
**Frequency**: Continuously (saves on file change)
**Duration**: <2 seconds

### Stage 2: Pre-Commit Verification
**Goal**: Ensure local changes are solid
```bash
# Run via git hook or manually
./verify-changes.sh  # Only tests/lints changed files
```
**Frequency**: Before each commit
**Duration**: <30 seconds

### Stage 3: Full Verification
**Goal**: Ensure entire system integrity
```bash
# Run before pushing or creating PR
./verify-all.sh  # Full build, all tests, coverage, linting
```
**Frequency**: Before push/PR
**Duration**: 2-5 minutes

## Smart Git Investigation

### Decision Tree
```
Is this a bug fix?
├─ YES → Check last 3 changes to this file (30 seconds)
└─ NO → Is this a refactor?
    ├─ YES → Check full file history (2 minutes)
    └─ NO → Skip investigation (new feature)
```

### Investigation Commands (Aliased)
```bash
# Super quick check
giq <file>  # Shows last 3 commits with stats

# Standard investigation  
gi <file>   # Shows last 10 commits with context

# Deep investigation (rare)
gid <file>  # Full history with diffs
```

## Commit Strategy

### 1. Micro-commits During Development
```bash
# Work-in-progress commits (not pushed)
git add -p  # Stage specific changes
git commit -m "wip: add user validation"

# These get squashed before pushing
```

### 2. Verified Commits Before Push
```bash
# Interactive rebase to clean history
git rebase -i origin/main

# Final commit with verification
git commit -m "feat: Add user validation - prevents duplicate emails

- Added unique constraint to database
- Frontend shows real-time validation
- API returns 409 for duplicates

[✓ VERIFIED]"
```

## Automation Scripts

### verify-changes.sh
```bash
#!/bin/bash
# Smart verification - only what changed

CHANGED_FILES=$(git diff --cached --name-only)

# Run targeted tests
if echo "$CHANGED_FILES" | grep -q "\.cs$"; then
    dotnet test --filter "FullyQualifiedName~$(echo $CHANGED_FILES | grep .cs | sed 's/\.cs//')"
fi

if echo "$CHANGED_FILES" | grep -q "\.ts$\|\.js$"; then
    npm run test -- --findRelatedTests $CHANGED_FILES
fi

# Quick lint
if [ -n "$CHANGED_FILES" ]; then
    dotnet format --include $CHANGED_FILES 2>/dev/null || true
    npm run lint -- $CHANGED_FILES 2>/dev/null || true
fi
```

### Git Hooks Setup
```bash
# .git/hooks/pre-commit
#!/bin/bash
./verify-changes.sh || {
    echo "❌ Verification failed. Fix issues or use --no-verify to skip."
    exit 1
}

# Auto-add verification badge if all passes
if git diff --cached --name-only | grep -q "\."; then
    COMMIT_MSG_FILE=".git/COMMIT_EDITMSG"
    if ! grep -q "\[✓ VERIFIED\]" "$COMMIT_MSG_FILE"; then
        echo "" >> "$COMMIT_MSG_FILE"
        echo "[✓ VERIFIED]" >> "$COMMIT_MSG_FILE"
    fi
fi
```

## The 10-Minute Rule

For any task, allocate time proportionally:
- **Investigation**: 10% (1 minute for 10-minute task)
- **Implementation**: 60% (6 minutes)
- **Testing**: 20% (2 minutes)
- **Verification**: 10% (1 minute)

## Red Flags to Avoid

1. **Spending more time on process than code**
2. **Running full test suite after every line change**
3. **Writing commit messages longer than the changeset**
4. **Investigating history for obvious bugs**
5. **Chasing 100% coverage on generated code**

## The Professional's Shortcuts

### Valid Shortcuts (Use These)
1. **Snapshot testing** for UI components
2. **Property-based testing** for algorithms  
3. **Approval testing** for complex outputs
4. **Mutation testing** to verify test quality (not coverage)
5. **Parallel test execution** to save time

### Invalid Shortcuts (Never Use)
1. Skipping tests "just this once"
2. Committing with "fix stuff" messages
3. Ignoring compiler warnings
4. Copy-pasting without understanding
5. Testing only the happy path

## Success Metrics

Track these instead of raw coverage:
1. **Defect escape rate** (bugs found in production)
2. **Mean time to fix** (how fast you fix bugs)
3. **Test execution time** (keep under 2 minutes)
4. **Build break frequency** (should be near zero)

## The One-Line Summary

**"Make it work, verify it works, commit proof it works, then make it better."**