#!/usr/bin/env python3
"""
Test that slash commands use path resolution correctly.
This tests the actual path resolution behavior from different directories.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import subprocess
import json

# Add parent directory to path
sys.path.insert(0, os.path.expanduser('~/.claude'))

from system.utils import path_resolver, repo_detector


def test_path_resolution_from_subdirectory():
    """Test that paths resolve correctly when run from a subdirectory."""
    print("Testing path resolution from subdirectory...")
    
    # Create a temporary git repository
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
        
        # Create some subdirectories
        subdir = repo_path / 'src' / 'components'
        subdir.mkdir(parents=True)
        
        # Change to subdirectory
        original_cwd = os.getcwd()
        os.chdir(subdir)
        
        try:
            # Test repo detection
            detected_root = repo_detector.find_repo_root()
            # Resolve both paths to handle symlinks
            assert detected_root.resolve() == repo_path.resolve(), f"Expected {repo_path}, got {detected_root}"
            print("✓ Repository root detected correctly from subdirectory")
            
            # Test path resolution
            prd_path = path_resolver.get_prd_path('test-feature')
            # Check that path is within repo (use resolve to handle symlinks)
            assert str(prd_path.resolve()).startswith(str(repo_path.resolve())), f"PRD path not in repo: {prd_path}"
            print("✓ PRD path resolves to repository root")
            
            # Test workspace path
            workspace_path = path_resolver.get_workspace_path('test-feature')
            expected_ws = repo_path / '.claude' / 'prd-workspace' / 'test-feature'
            assert workspace_path.resolve() == expected_ws.resolve(), f"Expected {expected_ws}, got {workspace_path}"
            print("✓ Workspace path resolves correctly")
            
        finally:
            os.chdir(original_cwd)


def test_environment_override():
    """Test that CLAUDE_OUTPUT_ROOT environment variable works."""
    print("\nTesting CLAUDE_OUTPUT_ROOT override...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        override_path = Path(tmpdir) / 'custom-output'
        override_path.mkdir()
        
        # Set environment variable
        original_env = os.environ.get('CLAUDE_OUTPUT_ROOT')
        os.environ['CLAUDE_OUTPUT_ROOT'] = str(override_path)
        
        try:
            # Clear cache to force re-detection
            repo_detector.clear_cache()
            
            # Test that paths use the override
            detected_root = repo_detector.find_repo_root()
            assert detected_root.resolve() == override_path.resolve(), f"Expected {override_path}, got {detected_root}"
            print("✓ CLAUDE_OUTPUT_ROOT override detected")
            
            # Test path resolution with override
            prd_path = path_resolver.get_prd_path('test-feature')
            assert str(prd_path.resolve()).startswith(str(override_path.resolve())), f"Path not using override: {prd_path}"
            print("✓ Paths use override directory")
            
        finally:
            # Restore environment
            if original_env is None:
                os.environ.pop('CLAUDE_OUTPUT_ROOT', None)
            else:
                os.environ['CLAUDE_OUTPUT_ROOT'] = original_env
            repo_detector.clear_cache()


def test_non_repo_fallback():
    """Test behavior when not in a git repository."""
    print("\nTesting non-repository fallback...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to non-repo directory
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # Clear cache
            repo_detector.clear_cache()
            
            # Test that we don't find a repo
            detected_root = repo_detector.find_repo_root()
            assert detected_root is None, f"Unexpectedly found repo: {detected_root}"
            print("✓ Correctly detected not in repository")
            
            # Test path resolution fallback
            prd_path = path_resolver.get_prd_path('test-feature')
            # Resolve paths to handle symlinks
            assert str(prd_path.resolve()).startswith(Path(tmpdir).resolve().as_posix()), f"Path not using current dir: {prd_path}"
            print("✓ Paths fall back to current directory")
            
        finally:
            os.chdir(original_cwd)
            repo_detector.clear_cache()


def test_path_formatting():
    """Test output message formatting."""
    print("\nTesting path formatting...")
    
    # Create test paths
    test_paths = {
        "PRD saved to": Path("/Users/test/repo/docs/prds/feature.md"),
        "Workspace created": Path("/Users/test/repo/.claude/prd-workspace/feature/"),
        "Tests added": Path("/Users/test/repo/tests/test_feature.py")
    }
    
    # Format message
    message = path_resolver.format_output_message(test_paths)
    
    # Check formatting
    lines = message.split('\n')
    assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
    assert all(line.startswith('✓') for line in lines), "All lines should start with ✓"
    print("✓ Output formatting works correctly")
    print("\nExample output:")
    print(message)


def test_command_paths():
    """Test that specific commands would use correct paths."""
    print("\nTesting command path patterns...")
    
    # Test various path types
    path_types = {
        'prds': 'docs/prds',
        'prd_workspace': '.claude/prd-workspace',
        'docs': 'docs',
        'tests': 'tests',
        'lib': 'lib'
    }
    
    for path_type, expected_relative in path_types.items():
        resolved = path_resolver.resolve(path_type)
        # Check that it ends with the expected path
        assert str(resolved).endswith(expected_relative), f"{path_type}: {resolved} doesn't end with {expected_relative}"
        print(f"✓ {path_type} → {expected_relative}")


def main():
    """Run all tests."""
    print("=== Path Resolution Tests for Slash Commands ===\n")
    
    try:
        test_path_resolution_from_subdirectory()
        test_environment_override()
        test_non_repo_fallback()
        test_path_formatting()
        test_command_paths()
        
        print("\n✅ All tests passed!")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())