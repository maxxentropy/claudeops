# Phase 1: Repository Detection Utility

## Objective
Create a robust repository root detection utility that can find the nearest `.git` directory and handle edge cases gracefully.

## Dependencies
- None (foundation phase)

## Deliverables
- [x] `system/utils/repo_detector.py` with core detection logic
- [x] Support for nested repositories (find nearest parent)
- [x] Caching mechanism for performance
- [x] Unit tests covering all scenarios

## Success Criteria
- [x] Correctly identifies git root from any subdirectory
- [x] Returns None for non-git directories
- [x] Handles symlinks correctly
- [x] Performance: < 10ms for cached lookups
- [x] Thread-safe implementation

## Implementation Details

```python
# system/utils/repo_detector.py
import os
from pathlib import Path
from typing import Optional
import threading

class RepoDetector:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def get_repo_root(self, start_path: Optional[str] = None) -> Optional[Path]:
        """Find the nearest git repository root."""
        # Implementation details...
```

## Context for Next Phase
The path resolution service in Phase 2 will use this detector to convert relative paths to repository-relative paths.