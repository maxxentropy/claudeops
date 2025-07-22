"""Path resolution service for slash commands to ensure consistent output locations."""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Union
import logging
from .repo_detector import find_repo_root, resolve_path as repo_resolve_path

logger = logging.getLogger(__name__)


class PathResolver:
    """Resolves paths for slash commands using repository-relative paths."""
    
    # Default paths for various output types
    DEFAULT_PATHS = {
        'prds': 'docs/prds',
        'prd_workspace': '.claude/prd-workspace',
        'docs': 'docs',
        'tests': 'tests',
        'lib': 'lib',
        'commands': 'commands',
        'hooks': 'hooks',
        'system': 'system'
    }
    
    def __init__(self):
        self._repo_root = None
        self._path_overrides = {}
        self._project_overrides_loaded = False
    
    def get_repo_root(self) -> Optional[Path]:
        """Get the repository root, with caching."""
        if self._repo_root is None:
            self._repo_root = find_repo_root()
        return self._repo_root
    
    def _load_project_overrides(self):
        """Load project-specific path overrides from .claude-paths.json."""
        if self._project_overrides_loaded:
            return
            
        self._project_overrides_loaded = True
        repo_root = self.get_repo_root()
        
        if not repo_root:
            return
            
        config_path = repo_root / '.claude-paths.json'
        if not config_path.exists():
            logger.debug(f"No project overrides found at {config_path}")
            return
            
        try:
            with open(config_path, 'r') as f:
                overrides = json.load(f)
                
            if isinstance(overrides, dict):
                for path_type, override_path in overrides.items():
                    if path_type in self.DEFAULT_PATHS:
                        self._path_overrides[path_type] = override_path
                        logger.info(f"Loaded project override for {path_type}: {override_path}")
                    else:
                        logger.warning(f"Unknown path type in overrides: {path_type}")
                        
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load project overrides: {e}")
    
    def resolve(self, path_type: str, filename: Optional[str] = None, 
                custom_path: Optional[str] = None) -> Path:
        """
        Resolve a path for a specific output type.
        
        Args:
            path_type: Type of path (e.g., 'prds', 'prd_workspace')
            filename: Optional filename to append
            custom_path: Custom path to use instead of default
            
        Returns:
            Resolved absolute path
        """
        # Load project overrides if not already loaded
        self._load_project_overrides()
        
        # Use custom path if provided
        if custom_path:
            base_path = custom_path
        else:
            # Get default path for this type
            base_path = self.DEFAULT_PATHS.get(path_type)
            if not base_path:
                raise ValueError(f"Unknown path type: {path_type}")
        
        # Check for overrides (includes project overrides loaded above)
        if path_type in self._path_overrides:
            base_path = self._path_overrides[path_type]
        
        # Resolve to absolute path
        resolved = repo_resolve_path(base_path)
        
        # Append filename if provided
        if filename:
            resolved = resolved / filename
            
        logger.debug(f"Resolved {path_type} path to: {resolved}")
        return resolved
    
    def ensure_directory(self, path_type: str) -> Path:
        """
        Ensure a directory exists for the given path type.
        
        Args:
            path_type: Type of path (e.g., 'prds', 'prd_workspace')
            
        Returns:
            Path to the created/existing directory
        """
        dir_path = self.resolve(path_type)
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")
        return dir_path
    
    def set_override(self, path_type: str, override_path: str):
        """
        Set a custom override for a specific path type.
        
        Args:
            path_type: Type of path to override
            override_path: New path to use
        """
        self._path_overrides[path_type] = override_path
        logger.info(f"Set path override for {path_type}: {override_path}")
    
    def clear_overrides(self):
        """Clear all path overrides."""
        self._path_overrides.clear()
    
    def get_prd_path(self, feature_slug: str, date_prefix: bool = True) -> Path:
        """
        Get the path for a PRD file.
        
        Args:
            feature_slug: Feature identifier
            date_prefix: Whether to include date prefix in filename
            
        Returns:
            Path to the PRD file
        """
        if date_prefix:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"{date_str}-{feature_slug}.md"
        else:
            filename = f"{feature_slug}.md"
            
        return self.resolve('prds', filename)
    
    def get_workspace_path(self, feature_slug: str) -> Path:
        """
        Get the path for a PRD workspace.
        
        Args:
            feature_slug: Feature identifier
            
        Returns:
            Path to the workspace directory
        """
        return self.resolve('prd_workspace', feature_slug)
    
    def format_output_message(self, paths: Dict[str, Path]) -> str:
        """
        Format a message showing created/updated paths.
        
        Args:
            paths: Dictionary of path descriptions to Path objects
            
        Returns:
            Formatted output message
        """
        repo_root = self.get_repo_root()
        lines = []
        
        for desc, path in paths.items():
            # Try to show relative path if in repo
            if repo_root and path.is_absolute():
                try:
                    rel_path = path.relative_to(repo_root)
                    lines.append(f"✓ {desc}: {rel_path}")
                except ValueError:
                    # Path is outside repo
                    lines.append(f"✓ {desc}: {path}")
            else:
                lines.append(f"✓ {desc}: {path}")
                
        return '\n'.join(lines)


# Singleton instance
_resolver = PathResolver()

# Convenience functions
resolve = _resolver.resolve
ensure_directory = _resolver.ensure_directory
get_prd_path = _resolver.get_prd_path
get_workspace_path = _resolver.get_workspace_path
format_output_message = _resolver.format_output_message
set_override = _resolver.set_override
clear_overrides = _resolver.clear_overrides