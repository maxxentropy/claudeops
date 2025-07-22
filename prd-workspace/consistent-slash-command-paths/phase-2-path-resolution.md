# Phase 2: Path Resolution Service

## Objective
Implement a path resolution service that converts relative paths to repository-relative paths using the repository detector from Phase 1.

## Dependencies
- Required from Phase 1: `system/utils/repo_detector.py`
- Python standard library: `pathlib`, `os`

## Deliverables
- [x] `system/utils/path_resolver.py` with resolution logic
- [x] Support for environment variable override (CLAUDE_OUTPUT_ROOT)
- [x] Fallback behavior for non-git directories
- [x] Integration tests with repo detector

## Success Criteria
- [x] Correctly resolves paths relative to repo root
- [x] Respects CLAUDE_OUTPUT_ROOT when set
- [x] Falls back to current directory when not in a repo
- [x] Handles absolute paths appropriately
- [x] Thread-safe and performant

## Implementation Details

```python
# system/utils/path_resolver.py
import os
from pathlib import Path
from typing import Optional, Union
from .repo_detector import RepoDetector

class PathResolver:
    def __init__(self, repo_detector: Optional[RepoDetector] = None):
        self.repo_detector = repo_detector or RepoDetector()
        self._override_root = os.environ.get('CLAUDE_OUTPUT_ROOT')
    
    def resolve_path(self, relative_path: Union[str, Path], 
                     fallback_to_cwd: bool = True) -> Path:
        """Resolve a relative path to repository-relative path."""
        # Implementation details...
```

## Context for Next Phase
Phase 3 will integrate this path resolver into the hook infrastructure to make it available to all commands.