"""Repository root detection utility for consistent path resolution."""

import os
import subprocess
from pathlib import Path
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


class RepoDetector:
    """Detects repository root and provides path resolution utilities."""
    
    def __init__(self):
        self._cache = {}
    
    def find_repo_root(self, start_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
        """
        Find the root directory of the git repository.
        
        Args:
            start_path: Starting directory for search (defaults to current directory)
            
        Returns:
            Path to repository root or None if not in a git repository
        """
        # Check for environment variable override
        env_override = os.environ.get('CLAUDE_OUTPUT_ROOT')
        if env_override:
            override_path = Path(env_override).expanduser().resolve()
            if override_path.exists() and override_path.is_dir():
                logger.debug(f"Using CLAUDE_OUTPUT_ROOT override: {override_path}")
                return override_path
            else:
                logger.warning(f"CLAUDE_OUTPUT_ROOT set but invalid: {env_override}")
        
        # Determine starting directory
        if start_path is None:
            start_path = Path.cwd()
        else:
            start_path = Path(start_path).expanduser().resolve()
        
        # Check cache
        cache_key = str(start_path)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try git command first (most reliable)
        repo_root = self._find_repo_root_git_command(start_path)
        
        # Fallback to directory traversal if git command fails
        if repo_root is None:
            repo_root = self._find_repo_root_traverse(start_path)
        
        # Cache the result
        if repo_root is not None:
            self._cache[cache_key] = repo_root
            
        return repo_root
    
    def _find_repo_root_git_command(self, start_path: Path) -> Optional[Path]:
        """Use git rev-parse to find repository root."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                cwd=str(start_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                repo_root = Path(result.stdout.strip()).resolve()
                logger.debug(f"Found repo root via git command: {repo_root}")
                return repo_root
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logger.debug(f"Git command failed: {e}")
            
        return None
    
    def _find_repo_root_traverse(self, start_path: Path) -> Optional[Path]:
        """Traverse up directory tree looking for .git directory."""
        current = start_path
        
        while current != current.parent:
            git_dir = current / '.git'
            if git_dir.exists() and (git_dir.is_dir() or git_dir.is_file()):
                logger.debug(f"Found repo root via traversal: {current}")
                return current
            current = current.parent
            
        return None
    
    def resolve_path(self, relative_path: str, fallback_to_cwd: bool = True) -> Path:
        """
        Resolve a path relative to the repository root.
        
        Args:
            relative_path: Path relative to repository root
            fallback_to_cwd: If True, use current directory when not in a repo
            
        Returns:
            Resolved absolute path
        """
        repo_root = self.find_repo_root()
        
        if repo_root is None:
            if fallback_to_cwd:
                logger.info("Not in a git repository, using current directory")
                base_path = Path.cwd()
            else:
                raise ValueError("Not in a git repository and fallback disabled")
        else:
            base_path = repo_root
            
        resolved = (base_path / relative_path).resolve()
        logger.debug(f"Resolved {relative_path} to {resolved}")
        return resolved
    
    def is_in_repo(self, path: Optional[Union[str, Path]] = None) -> bool:
        """Check if the given path (or current directory) is in a git repository."""
        return self.find_repo_root(path) is not None
    
    def clear_cache(self):
        """Clear the repository root cache."""
        self._cache.clear()


# Singleton instance for convenience
_detector = RepoDetector()

# Convenience functions
find_repo_root = _detector.find_repo_root
resolve_path = _detector.resolve_path
is_in_repo = _detector.is_in_repo
clear_cache = _detector.clear_cache