#!/usr/bin/env python3
"""Test the path resolution utilities for consistent slash command paths."""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add system utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from system.utils import (
    find_repo_root,
    resolve_path,
    is_in_repo,
    get_prd_path,
    get_workspace_path,
    ensure_directory,
    format_output_message
)


def test_repo_detection():
    """Test repository root detection."""
    print("Testing repository root detection...")
    
    # Test from current directory
    repo_root = find_repo_root()
    print(f"  From current dir: {repo_root}")
    assert repo_root is not None, "Should find repo root from .claude directory"
    assert repo_root.name == '.claude', "Should find .claude as repo root"
    
    # Test from subdirectory
    subdir = repo_root / 'tests'
    repo_from_subdir = find_repo_root(subdir)
    print(f"  From subdir: {repo_from_subdir}")
    assert repo_from_subdir == repo_root, "Should find same root from subdirectory"
    
    print("✓ Repository detection tests passed\n")


def test_path_resolution():
    """Test path resolution functionality."""
    print("Testing path resolution...")
    
    # Test PRD path resolution
    prd_path = get_prd_path('test-feature')
    print(f"  PRD path: {prd_path}")
    assert 'docs/prds' in str(prd_path), "PRD path should contain docs/prds"
    assert prd_path.name.endswith('test-feature.md'), "PRD filename should end with feature slug"
    
    # Test workspace path resolution
    workspace_path = get_workspace_path('test-feature')
    print(f"  Workspace path: {workspace_path}")
    assert '.claude/prd-workspace' in str(workspace_path), "Workspace path should contain .claude/prd-workspace"
    assert workspace_path.name == 'test-feature', "Workspace directory should match feature slug"
    
    print("✓ Path resolution tests passed\n")


def test_env_override():
    """Test environment variable override."""
    print("Testing environment variable override...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Set environment variable
        os.environ['CLAUDE_OUTPUT_ROOT'] = tmpdir
        
        # Clear any cached values
        from system.utils.repo_detector import clear_cache
        clear_cache()
        
        # Test that paths resolve to override directory
        try:
            resolved = resolve_path('docs/prds')
            print(f"  Override path: {resolved}")
            # Resolve both paths to handle symlinks
            resolved_str = str(resolved.resolve())
            tmpdir_resolved = str(Path(tmpdir).resolve())
            assert resolved_str.startswith(tmpdir_resolved), f"Path {resolved_str} should start with override directory: {tmpdir_resolved}"
            
            # Test PRD path with override
            prd_path = get_prd_path('override-test')
            print(f"  Override PRD path: {prd_path}")
            assert tmpdir_resolved in str(prd_path.resolve()), "PRD path should use override directory"
            
        finally:
            # Clean up
            if 'CLAUDE_OUTPUT_ROOT' in os.environ:
                del os.environ['CLAUDE_OUTPUT_ROOT']
            clear_cache()
    
    print("✓ Environment override tests passed\n")


def test_directory_creation():
    """Test directory creation functionality."""
    print("Testing directory creation...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['CLAUDE_OUTPUT_ROOT'] = tmpdir
        from system.utils.repo_detector import clear_cache
        clear_cache()
        
        try:
            # Test ensuring PRD directory exists
            prd_dir = ensure_directory('prds')
            print(f"  Created PRD dir: {prd_dir}")
            assert prd_dir.exists(), "PRD directory should exist"
            assert prd_dir.is_dir(), "PRD path should be a directory"
            
            # Test ensuring workspace directory exists
            workspace_dir = ensure_directory('prd_workspace')
            print(f"  Created workspace dir: {workspace_dir}")
            assert workspace_dir.exists(), "Workspace directory should exist"
            assert workspace_dir.is_dir(), "Workspace path should be a directory"
            
        finally:
            if 'CLAUDE_OUTPUT_ROOT' in os.environ:
                del os.environ['CLAUDE_OUTPUT_ROOT']
            clear_cache()
    
    print("✓ Directory creation tests passed\n")


def test_output_formatting():
    """Test output message formatting."""
    print("Testing output message formatting...")
    
    # Create test paths
    paths = {
        'PRD saved to': get_prd_path('test-feature'),
        'Workspace created': get_workspace_path('test-feature'),
        'Index updated': resolve_path('docs/prds/index.md')
    }
    
    # Format the message
    message = format_output_message(paths)
    print("  Formatted output:")
    for line in message.split('\n'):
        print(f"    {line}")
    
    # Check that paths are shown as relative when possible
    assert 'docs/prds' in message, "Should show relative paths"
    assert not message.startswith('/'), "Should not show absolute paths when in repo"
    
    print("✓ Output formatting tests passed\n")


def test_non_repo_fallback():
    """Test behavior when not in a git repository."""
    print("Testing non-repository fallback...")
    
    # Create a temporary directory without git
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to non-git directory
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            from system.utils.repo_detector import clear_cache
            clear_cache()
            
            # Test that we're not in a repo
            assert not is_in_repo(), "Should not detect repository in temp directory"
            
            # Test fallback to current directory
            resolved = resolve_path('docs/prds')
            print(f"  Fallback path: {resolved}")
            # Resolve both paths to handle symlinks
            resolved_str = str(resolved.resolve())
            tmpdir_resolved = str(Path(tmpdir).resolve())
            assert resolved_str.startswith(tmpdir_resolved), f"Should fall back to current directory: {resolved_str} should start with {tmpdir_resolved}"
            
        finally:
            os.chdir(original_cwd)
            clear_cache()
    
    print("✓ Non-repository fallback tests passed\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Path Resolution for Consistent Slash Commands")
    print("=" * 60)
    print()
    
    try:
        test_repo_detection()
        test_path_resolution()
        test_env_override()
        test_directory_creation()
        test_output_formatting()
        test_non_repo_fallback()
        
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()