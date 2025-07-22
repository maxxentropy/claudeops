# Phase 1: Repository Root Detection Utility

## Objective
Create a robust repository root detection utility that finds the nearest `.git` directory and handles edge cases gracefully.

## Dependencies
- No dependencies on other phases
- Python 3.6+ (standard library only)
- Git command-line tool (for validation)

## Deliverables

### 1. Core Detection Module
**File**: `system/utils/repo_detector.py`

```python
class RepoDetector:
    def __init__(self, cache_ttl=300):
        """Initialize with optional cache TTL in seconds"""
        
    def find_repo_root(self, start_path=None):
        """Find the nearest git repository root"""
        # Start from current working directory if not specified
        # Walk up directory tree looking for .git
        # Handle symlinks correctly
        # Return absolute path or None
        
    def get_repo_root_with_override(self, start_path=None):
        """Get repo root with environment variable override"""
        # Check CLAUDE_OUTPUT_ROOT first
        # Fall back to find_repo_root
        # Validate result is a directory
        
    def invalidate_cache(self):
        """Clear the cache when directory changes"""
```

### 2. Edge Case Handlers
- **Submodules**: Detect `.git` file (not directory) and resolve parent
- **Bare repositories**: Handle repos without working tree
- **Symlinks**: Follow symlinks correctly
- **Network drives**: Handle slow filesystem access
- **Permission errors**: Graceful fallback when can't read directories

### 3. Performance Optimization
- **Caching**: Cache results with TTL and path-based keys
- **Early termination**: Stop at filesystem boundaries
- **Lazy loading**: Don't import heavy modules unless needed

### 4. Unit Tests
**File**: `tests/test_repo_detector.py`

Test cases:
- [ ] Normal repository detection
- [ ] Submodule detection
- [ ] No repository (returns None)
- [ ] Environment variable override
- [ ] Cache behavior
- [ ] Symlink handling
- [ ] Permission errors
- [ ] Deep nesting (performance)

## Success Criteria
- [ ] Finds repo root from any subdirectory
- [ ] Handles all edge cases without crashes
- [ ] Performance: < 10ms for cached lookups
- [ ] Performance: < 100ms for uncached lookups
- [ ] 100% test coverage for core logic

## Implementation Notes

### Algorithm
1. Start from current working directory (or provided path)
2. Check for `.git` directory or file
3. If file, read it to find real git directory
4. If not found, move to parent directory
5. Stop at filesystem root or home directory
6. Cache result with path as key

### Cache Design
```python
cache = {
    "/path/to/start": {
        "result": "/path/to/repo",
        "timestamp": 1234567890
    }
}
```

### Environment Variable
- `CLAUDE_OUTPUT_ROOT`: Override detected root
- Validate it's a directory that exists
- No validation that it's a git repo (intentional)

## Context for Next Phase
The path resolver in Phase 2 will use this module to:
- Get the repository root for path resolution
- Handle cases where no repo is found
- Build absolute paths from templates