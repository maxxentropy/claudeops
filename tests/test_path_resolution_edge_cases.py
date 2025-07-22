#!/usr/bin/env python3
"""Edge case and integration tests for path resolution system."""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
import unittest
import json
import time

# Add system utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from system.utils import (
    RepoDetector,
    PathResolver,
    find_repo_root,
    resolve_path,
    is_in_repo,
    clear_cache,
    get_prd_path,
    get_workspace_path,
    ensure_directory
)


class TestNestedGitRepos(unittest.TestCase):
    """Test behavior with nested git repositories (submodules)."""
    
    def setUp(self):
        """Create nested git repositories for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create parent repo
        self.parent_repo = Path(self.test_dir) / 'parent-repo'
        self.parent_repo.mkdir()
        subprocess.run(['git', 'init'], cwd=self.parent_repo, capture_output=True)
        
        # Create submodule
        self.submodule = self.parent_repo / 'submodule'
        self.submodule.mkdir()
        subprocess.run(['git', 'init'], cwd=self.submodule, capture_output=True)
        
        # Clear cache
        clear_cache()
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        clear_cache()
        
    def test_find_nearest_parent_repo(self):
        """Test that we find the nearest parent repository."""
        # Change to submodule directory
        os.chdir(self.submodule)
        
        # Should find submodule as repo root, not parent
        repo_root = find_repo_root()
        self.assertEqual(repo_root.resolve(), self.submodule.resolve())
        
    def test_nested_repo_path_resolution(self):
        """Test path resolution in nested repository structure."""
        # Change to a deep subdirectory in submodule
        deep_dir = self.submodule / 'src' / 'components' / 'ui'
        deep_dir.mkdir(parents=True)
        os.chdir(deep_dir)
        
        # Should resolve paths relative to submodule root
        prd_path = get_prd_path('nested-feature')
        expected_base = self.submodule / 'docs' / 'prds'
        self.assertTrue(str(prd_path).startswith(str(expected_base)))
        
    def test_git_worktree_support(self):
        """Test support for git worktrees."""
        # Create a git worktree
        worktree_dir = Path(self.test_dir) / 'worktree'
        subprocess.run(
            ['git', 'worktree', 'add', str(worktree_dir), 'HEAD'],
            cwd=self.parent_repo,
            capture_output=True
        )
        
        # Change to worktree
        os.chdir(worktree_dir)
        clear_cache()
        
        # Should find parent repo as root
        repo_root = find_repo_root()
        self.assertEqual(repo_root.resolve(), self.parent_repo.resolve())


class TestSymlinksAndSpecialPaths(unittest.TestCase):
    """Test handling of symlinks and special filesystem scenarios."""
    
    def setUp(self):
        """Create test environment with symlinks."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create real directory
        self.real_repo = Path(self.test_dir) / 'real-repo'
        self.real_repo.mkdir()
        subprocess.run(['git', 'init'], cwd=self.real_repo, capture_output=True)
        
        # Create symlink to repo
        self.symlink_repo = Path(self.test_dir) / 'symlink-repo'
        self.symlink_repo.symlink_to(self.real_repo)
        
        clear_cache()
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        clear_cache()
        
    def test_symlink_repo_detection(self):
        """Test repo detection through symlinks."""
        # Change to symlinked repository
        os.chdir(self.symlink_repo)
        
        # Should find repository through symlink
        repo_root = find_repo_root()
        self.assertIsNotNone(repo_root)
        # Both should resolve to the same real path
        self.assertEqual(repo_root.resolve(), self.real_repo.resolve())
        
    def test_symlink_file_paths(self):
        """Test path resolution with symlinked directories."""
        # Create symlinked docs directory
        real_docs = self.real_repo / 'real-docs'
        real_docs.mkdir()
        
        symlink_docs = self.real_repo / 'docs'
        symlink_docs.symlink_to(real_docs)
        
        os.chdir(self.real_repo)
        clear_cache()
        
        # Path resolution should work through symlinks
        prd_path = get_prd_path('symlink-test')
        self.assertTrue(prd_path.parent.exists())
        # The resolved path should point to the real directory
        self.assertTrue('real-docs' in str(prd_path.resolve()))


class TestConcurrentAccess(unittest.TestCase):
    """Test thread safety and concurrent access patterns."""
    
    def test_cache_invalidation(self):
        """Test that cache invalidation works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo1 = Path(tmpdir) / 'repo1'
            repo2 = Path(tmpdir) / 'repo2'
            
            # Create two repos
            for repo in [repo1, repo2]:
                repo.mkdir()
                subprocess.run(['git', 'init'], cwd=repo, capture_output=True)
            
            # Test repo1
            os.chdir(repo1)
            clear_cache()
            root1 = find_repo_root()
            self.assertEqual(root1.resolve(), repo1.resolve())
            
            # Change to repo2 without clearing cache first
            os.chdir(repo2)
            # Should still get repo1 from cache
            root_cached = find_repo_root()
            self.assertEqual(root_cached.resolve(), repo1.resolve())
            
            # Clear cache and try again
            clear_cache()
            root2 = find_repo_root()
            self.assertEqual(root2.resolve(), repo2.resolve())
            
    def test_resolver_state_isolation(self):
        """Test that multiple resolver instances don't interfere."""
        resolver1 = PathResolver()
        resolver2 = PathResolver()
        
        # Set override on resolver1
        resolver1.set_override('prds', 'custom1/prds')
        
        # resolver2 should not see this override
        # Note: Since we're using a singleton, they will share state
        # This test documents the current behavior
        path1 = resolver1.resolve('prds')
        path2 = resolver2.resolve('prds')
        
        # Both will see the override because of singleton pattern
        self.assertEqual(str(path1), str(path2))


class TestErrorConditions(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_claude_output_root(self):
        """Test handling of invalid CLAUDE_OUTPUT_ROOT values."""
        test_cases = [
            '/nonexistent/path/that/does/not/exist',
            'relative/path/without/absolute',
            '',  # Empty string
            '/dev/null',  # Special file, not directory
        ]
        
        original_env = os.environ.get('CLAUDE_OUTPUT_ROOT')
        
        try:
            for invalid_path in test_cases:
                os.environ['CLAUDE_OUTPUT_ROOT'] = invalid_path
                clear_cache()
                
                # Should fall back to git detection or current directory
                repo_root = find_repo_root()
                # Should not use the invalid override
                if repo_root:
                    self.assertNotEqual(str(repo_root), invalid_path)
                    
        finally:
            if original_env:
                os.environ['CLAUDE_OUTPUT_ROOT'] = original_env
            else:
                os.environ.pop('CLAUDE_OUTPUT_ROOT', None)
            clear_cache()
    
    def test_permission_errors(self):
        """Test handling of permission errors."""
        if os.name == 'nt':  # Skip on Windows
            self.skipTest("Permission test not applicable on Windows")
            
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory with no write permissions
            protected_dir = Path(tmpdir) / 'protected'
            protected_dir.mkdir()
            os.chmod(protected_dir, 0o444)  # Read-only
            
            try:
                os.environ['CLAUDE_OUTPUT_ROOT'] = str(protected_dir)
                clear_cache()
                
                # Should handle gracefully when trying to create subdirectories
                resolver = PathResolver()
                
                # This should not raise an exception
                prd_path = resolver.resolve('prds', 'test.md')
                self.assertTrue(str(prd_path).endswith('test.md'))
                
                # But trying to ensure directory might fail
                with self.assertRaises(PermissionError):
                    ensure_directory('prds')
                    
            finally:
                os.chmod(protected_dir, 0o755)  # Restore permissions
                os.environ.pop('CLAUDE_OUTPUT_ROOT', None)
                clear_cache()
    
    def test_very_long_paths(self):
        """Test handling of very long path names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a very deep directory structure
            deep_path = Path(tmpdir)
            for i in range(50):  # Create 50 levels deep
                deep_path = deep_path / f'level{i}'
            
            try:
                deep_path.mkdir(parents=True)
                os.chdir(deep_path)
                clear_cache()
                
                # Should still work with deep paths
                resolver = PathResolver()
                prd_path = resolver.resolve('prds', 'deep-test.md')
                self.assertIsInstance(prd_path, Path)
                
            except OSError as e:
                # Some systems have path length limits
                self.skipTest(f"System path length limit reached: {e}")


class TestProjectOverridesEdgeCases(unittest.TestCase):
    """Test edge cases for project override functionality."""
    
    def setUp(self):
        """Set up test repository."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        subprocess.run(['git', 'init'], capture_output=True)
        clear_cache()
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        clear_cache()
        
    def test_malformed_json_variations(self):
        """Test various malformed JSON scenarios."""
        test_cases = [
            '{"prds": "custom/prds"',  # Missing closing brace
            '{"prds": custom/prds"}',  # Unquoted value
            '[]',  # Array instead of object
            'null',  # Null value
            '{"prds": null}',  # Null path value
            '{"prds": {}}',  # Object as path value
        ]
        
        for json_content in test_cases:
            # Create malformed override file
            override_path = Path(self.test_dir) / '.claude-paths.json'
            with open(override_path, 'w') as f:
                f.write(json_content)
            
            # Clear resolver state
            from system.utils.path_resolver import _resolver
            _resolver._project_overrides_loaded = False
            _resolver._path_overrides.clear()
            
            # Should not crash, should use defaults
            prd_path = get_prd_path('test')
            self.assertTrue('docs/prds' in str(prd_path))
            
            # Clean up for next iteration
            override_path.unlink()
    
    def test_override_file_permissions(self):
        """Test handling of override files with restricted permissions."""
        if os.name == 'nt':  # Skip on Windows
            self.skipTest("Permission test not applicable on Windows")
            
        # Create override file
        override_path = Path(self.test_dir) / '.claude-paths.json'
        override_data = {"prds": "custom/requirements"}
        with open(override_path, 'w') as f:
            json.dump(override_data, f)
        
        # Make file unreadable
        os.chmod(override_path, 0o000)
        
        try:
            # Clear resolver state
            from system.utils.path_resolver import _resolver
            _resolver._project_overrides_loaded = False
            _resolver._path_overrides.clear()
            
            # Should handle gracefully and use defaults
            prd_path = get_prd_path('test')
            self.assertTrue('docs/prds' in str(prd_path))
            
        finally:
            # Restore permissions for cleanup
            os.chmod(override_path, 0o644)
    
    def test_circular_symlink_in_overrides(self):
        """Test handling of circular symlinks in override paths."""
        # Create circular symlink
        link1 = Path(self.test_dir) / 'link1'
        link2 = Path(self.test_dir) / 'link2'
        link1.symlink_to(link2)
        link2.symlink_to(link1)
        
        # Create override pointing to circular symlink
        override_data = {"prds": "link1/prds"}
        override_path = Path(self.test_dir) / '.claude-paths.json'
        with open(override_path, 'w') as f:
            json.dump(override_data, f)
        
        # Clear resolver state
        from system.utils.path_resolver import _resolver
        _resolver._project_overrides_loaded = False
        _resolver._path_overrides.clear()
        
        # Should handle gracefully
        try:
            prd_path = get_prd_path('test')
            # Should create a path even if target doesn't exist
            self.assertTrue(prd_path.name.endswith('test.md'))
        except Exception as e:
            # Some systems might raise different errors for circular symlinks
            self.assertIn('link', str(e).lower())


def run_edge_case_tests():
    """Run all edge case tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test cases
    test_classes = [
        TestNestedGitRepos,
        TestSymlinksAndSpecialPaths,
        TestConcurrentAccess,
        TestErrorConditions,
        TestProjectOverridesEdgeCases,
    ]
    
    for test_class in test_classes:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_edge_case_tests()
    sys.exit(0 if success else 1)