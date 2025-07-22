# Phase 5: Testing & Documentation

## Objective
Create comprehensive tests for all edge cases, document the new path resolution behavior, and provide migration guidance for existing users.

## Dependencies
- All previous phases completed
- Working implementation of path resolution
- Updated commands with new path behavior

## Deliverables

### 1. Comprehensive Test Suite
**File**: `tests/test_consistent_paths_integration.py`

Test scenarios:

**Repository Structure Tests:**
- [ ] Single repository - normal case
- [ ] Nested repositories (submodules)
- [ ] Bare repository (no working tree)
- [ ] Repository with symlinks
- [ ] Repository on network drive

**Command Execution Tests:**
- [ ] Run from repository root
- [ ] Run from deep subdirectory
- [ ] Run from outside any repository
- [ ] Run with `CLAUDE_OUTPUT_ROOT` set
- [ ] Run with invalid environment variable

**Edge Case Tests:**
- [ ] No write permissions to repo root
- [ ] Repository on read-only filesystem
- [ ] Very long path names
- [ ] Unicode in repository paths
- [ ] Concurrent command execution

**Performance Tests:**
- [ ] Cache hit performance < 10ms
- [ ] Cache miss performance < 100ms
- [ ] No performance regression in commands

### 2. Documentation Updates

**File**: `docs/path-resolution.md`
```markdown
# Path Resolution in Claude Code

## Overview
Claude Code uses intelligent path resolution to ensure consistent file output locations regardless of where you run commands.

## How It Works
1. Detects nearest Git repository root
2. All paths resolve relative to repository
3. Falls back to current directory if not in repo
4. Override with CLAUDE_OUTPUT_ROOT variable

## Examples
[Include practical examples]

## Migration Guide
[For existing users]
```

**Update**: `README.md`
- Add section on path resolution
- Update examples to show new behavior
- Add troubleshooting section

**Update**: `docs/commands.md`
- Document path behavior for each command
- Show example outputs with absolute paths

### 3. Migration Guide
**File**: `docs/migration/consistent-paths-v1.md`

Contents:
- What changed and why
- Impact on existing workflows
- How to migrate existing PRDs
- Environment variable usage
- Troubleshooting common issues

### 4. Error Handling Documentation
Document all error cases:
- Repository detection failures
- Permission errors
- Path resolution errors
- Fallback behavior

### 5. Shell Integration Tests
**File**: `tests/test_shell_integration.sh`

Test in different shells:
```bash
# Test in Bash
bash -c "cd /repo/subdir && claude /prd Test"

# Test in Zsh
zsh -c "cd /repo/subdir && claude /prd Test"

# Test with environment override
CLAUDE_OUTPUT_ROOT=/custom/path claude /prd Test
```

## Success Criteria
- [ ] All test scenarios pass
- [ ] Documentation is clear and complete
- [ ] Migration guide helps existing users
- [ ] Performance benchmarks are met
- [ ] No regressions in existing functionality

## Test Execution Plan

### 1. Unit Test Coverage
- Minimum 90% code coverage
- All error paths tested
- Mock filesystem for edge cases

### 2. Integration Test Suite
```python
class TestConsistentPaths:
    def test_prd_from_subdirectory(self):
        # Change to subdirectory
        # Run /prd command
        # Verify file in repo root
        
    def test_fallback_no_repo(self):
        # Run in temp directory
        # Verify fallback to CWD
        # Check warning message
```

### 3. Manual Testing Checklist
- [ ] Test on macOS
- [ ] Test on Linux
- [ ] Test on Windows (WSL)
- [ ] Test with real projects
- [ ] Test with various repo sizes

### 4. Performance Benchmarks
```python
def benchmark_path_resolution():
    # Time 1000 resolutions
    # Compare with/without cache
    # Measure hook overhead
    # Generate performance report
```

## Documentation Standards

### User-Facing Docs
- Clear examples for each use case
- Troubleshooting section
- FAQ for common questions
- Visual diagrams where helpful

### Developer Docs
- Architecture decisions
- Extension points
- Performance considerations
- Future improvement ideas

## Release Checklist
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Migration guide published
- [ ] Performance acceptable
- [ ] Backward compatibility verified
- [ ] Release notes written