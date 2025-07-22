#!/usr/bin/env python3
"""Integration tests for slash commands to verify they use path resolution correctly."""

import os
import sys
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add system utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from system.utils import (
    PathResolver,
    clear_cache,
    get_prd_path,
    get_workspace_path,
    resolve,
    ensure_directory
)


class TestSlashCommandIntegration(unittest.TestCase):
    """Test that slash commands properly integrate with path resolution."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test git repo
        self.repo_root = Path(self.test_dir) / 'test-repo'
        self.repo_root.mkdir()
        subprocess.run(['git', 'init'], cwd=self.repo_root, capture_output=True)
        
        # Create subdirectory structure
        self.subdir = self.repo_root / 'src' / 'components'
        self.subdir.mkdir(parents=True)
        
        clear_cache()
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        clear_cache()
    
    def test_prd_command_paths(self):
        """Test that /prd command uses correct paths."""
        os.chdir(self.subdir)
        
        # Test PRD path resolution
        prd_path = get_prd_path('test-feature')
        
        # Should be relative to repo root, not current directory
        expected_prd_dir = self.repo_root / 'docs' / 'prds'
        self.assertTrue(str(prd_path).startswith(str(expected_prd_dir)))
        self.assertIn('test-feature.md', str(prd_path))
        
    def test_prd_workspace_command_paths(self):
        """Test that PRD workspace commands use correct paths."""
        os.chdir(self.subdir)
        
        # Test workspace path resolution
        workspace_path = get_workspace_path('test-feature')
        
        # Should be relative to repo root
        expected_ws_dir = self.repo_root / '.claude' / 'prd-workspace'
        self.assertTrue(str(workspace_path).startswith(str(expected_ws_dir)))
        self.assertEqual(workspace_path.name, 'test-feature')
        
    def test_prd_implement_command_paths(self):
        """Test that /prd-implement uses correct paths."""
        os.chdir(self.subdir)
        
        # Simulate /prd-implement creating files
        feature_slug = 'implement-test'
        
        # Should create workspace in repo root
        workspace = get_workspace_path(feature_slug)
        sandbox_dir = workspace / 'sandbox'
        
        # Test that paths are correct
        expected_sandbox = self.repo_root / '.claude' / 'prd-workspace' / feature_slug / 'sandbox'
        self.assertEqual(sandbox_dir.resolve(), expected_sandbox.resolve())
        
    def test_create_docs_command_paths(self):
        """Test that /create-docs uses correct paths."""
        os.chdir(self.subdir)
        
        # Test docs path resolution
        docs_path = resolve('docs', 'api/user-guide.md')
        
        # Should be relative to repo root
        expected_docs = self.repo_root / 'docs' / 'api' / 'user-guide.md'
        self.assertEqual(docs_path.resolve(), expected_docs.resolve())
        
    def test_api_crud_command_paths(self):
        """Test that /api-crud uses correct paths."""
        os.chdir(self.subdir)
        
        # Test various paths used by api-crud
        paths = {
            'controller': resolve('lib', 'controllers/UserController.cs'),
            'service': resolve('lib', 'services/UserService.cs'),
            'dto': resolve('lib', 'dtos/UserDto.cs'),
            'test': resolve('tests', 'api/UserControllerTests.cs'),
        }
        
        # All should be relative to repo root
        for path_type, path in paths.items():
            self.assertTrue(str(path).startswith(str(self.repo_root)))
            
    def test_mobile_scaffold_command_paths(self):
        """Test that /mobile-scaffold uses correct paths."""
        os.chdir(self.subdir)
        
        project_name = 'TestApp'
        
        # Test project root path
        project_path = resolve('lib', project_name)
        expected_project = self.repo_root / 'lib' / project_name
        self.assertEqual(project_path.resolve(), expected_project.resolve())
        
    def test_command_with_project_overrides(self):
        """Test commands respect project overrides."""
        # Create project overrides
        overrides = {
            "prds": "requirements/prds",
            "prd_workspace": ".project/workspaces",
            "docs": "documentation",
            "tests": "test_suite",
            "lib": "source"
        }
        
        override_file = self.repo_root / '.claude-paths.json'
        with open(override_file, 'w') as f:
            json.dump(overrides, f)
        
        # Change to subdirectory and clear resolver state
        os.chdir(self.subdir)
        clear_cache()
        from system.utils.path_resolver import _resolver
        _resolver._project_overrides_loaded = False
        _resolver._path_overrides.clear()
        _resolver._repo_root = None
        
        # Test that commands use overrides
        prd_path = get_prd_path('override-test')
        self.assertIn('requirements/prds', str(prd_path))
        
        workspace_path = get_workspace_path('override-test')
        self.assertIn('.project/workspaces', str(workspace_path))
        
        docs_path = resolve('docs', 'guide.md')
        self.assertIn('documentation', str(docs_path))
        
    def test_command_environment_override(self):
        """Test commands respect CLAUDE_OUTPUT_ROOT."""
        # Create override directory
        override_dir = Path(self.test_dir) / 'override-output'
        override_dir.mkdir()
        
        # Set environment variable
        os.environ['CLAUDE_OUTPUT_ROOT'] = str(override_dir)
        
        try:
            os.chdir(self.subdir)
            clear_cache()
            
            # All paths should now use override
            prd_path = get_prd_path('env-test')
            self.assertTrue(str(prd_path).startswith(str(override_dir)))
            
            workspace_path = get_workspace_path('env-test')
            self.assertTrue(str(workspace_path).startswith(str(override_dir)))
            
        finally:
            del os.environ['CLAUDE_OUTPUT_ROOT']
            clear_cache()
    
    def test_command_non_repo_fallback(self):
        """Test commands work outside git repositories."""
        # Create non-git directory
        non_repo_dir = Path(self.test_dir) / 'non-repo'
        non_repo_dir.mkdir()
        
        os.chdir(non_repo_dir)
        clear_cache()
        
        # Commands should fall back to current directory
        prd_path = get_prd_path('fallback-test')
        self.assertTrue(str(prd_path).startswith(str(non_repo_dir)))
        
        # Should create in current directory structure
        expected_prd = non_repo_dir / 'docs' / 'prds' / Path(prd_path).name
        self.assertEqual(prd_path.resolve(), expected_prd.resolve())


class TestCommandPathPatterns(unittest.TestCase):
    """Test specific path patterns used by different commands."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.test_dir) / 'test-repo'
        self.repo_root.mkdir()
        subprocess.run(['git', 'init'], cwd=self.repo_root, capture_output=True)
        os.chdir(self.repo_root)
        clear_cache()
        
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir)
        clear_cache()
    
    def test_prd_family_commands(self):
        """Test all PRD-related commands use consistent paths."""
        feature = 'test-feature'
        
        # All PRD commands should use same base paths
        commands_paths = {
            '/prd': get_prd_path(feature),
            '/prdq': get_prd_path(feature),
            '/prd-implement': get_workspace_path(feature),
            '/prd-decompose': get_workspace_path(feature),
            '/prd-analyze': get_workspace_path(feature),
            '/prd-integrate': get_workspace_path(feature),
            '/prd-progress': get_workspace_path(feature),
            '/prd-rollback': get_workspace_path(feature),
        }
        
        # Verify all PRD document paths are consistent
        prd_paths = [p for cmd, p in commands_paths.items() if cmd in ['/prd', '/prdq']]
        self.assertTrue(all(p == prd_paths[0] for p in prd_paths))
        
        # Verify all workspace paths are consistent
        ws_paths = [p for cmd, p in commands_paths.items() if 'workspace' in str(p)]
        self.assertTrue(all(p == ws_paths[0] for p in ws_paths))
    
    def test_generation_commands(self):
        """Test generation commands use appropriate paths."""
        # Test /create-docs paths
        docs_paths = [
            resolve('docs', 'README.md'),
            resolve('docs', 'api/reference.md'),
            resolve('docs', 'guides/quickstart.md'),
        ]
        
        for path in docs_paths:
            self.assertTrue(str(path).startswith(str(self.repo_root)))
            self.assertIn('docs', str(path))
        
        # Test /api-crud paths structure
        api_paths = {
            'controllers': resolve('lib', 'controllers/'),
            'services': resolve('lib', 'services/'),
            'dtos': resolve('lib', 'dtos/'),
            'tests': resolve('tests', 'api/'),
        }
        
        for path_type, path in api_paths.items():
            self.assertTrue(str(path).startswith(str(self.repo_root)))
    
    def test_path_consistency_across_invocations(self):
        """Test that paths remain consistent across multiple invocations."""
        feature = 'consistency-test'
        
        # Get paths multiple times
        paths1 = {
            'prd': get_prd_path(feature),
            'workspace': get_workspace_path(feature),
            'docs': resolve('docs', 'test.md'),
        }
        
        # Clear any potential caches
        clear_cache()
        
        # Get paths again
        paths2 = {
            'prd': get_prd_path(feature),
            'workspace': get_workspace_path(feature),
            'docs': resolve('docs', 'test.md'),
        }
        
        # Should be identical
        for key in paths1:
            self.assertEqual(paths1[key], paths2[key])


class TestPathResolutionOutput(unittest.TestCase):
    """Test output formatting and user-facing messages."""
    
    def test_relative_path_display(self):
        """Test that paths are displayed as relative when possible."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / 'repo'
            repo.mkdir()
            subprocess.run(['git', 'init'], cwd=repo, capture_output=True)
            os.chdir(repo)
            clear_cache()
            
            # Create some paths
            from system.utils.path_resolver import format_output_message
            
            paths = {
                'PRD created': get_prd_path('test'),
                'Workspace created': get_workspace_path('test'),
                'Docs updated': resolve('docs', 'README.md'),
            }
            
            # Format output
            output = format_output_message(paths)
            
            # Should show relative paths
            self.assertIn('docs/prds', output)
            self.assertIn('.claude/prd-workspace', output)
            self.assertNotIn(str(repo), output)  # Should not show absolute path
    
    def test_absolute_path_display_when_outside_repo(self):
        """Test that absolute paths are shown when outside repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            external_dir = Path(tmpdir) / 'external'
            external_dir.mkdir()
            
            repo = Path(tmpdir) / 'repo'
            repo.mkdir()
            subprocess.run(['git', 'init'], cwd=repo, capture_output=True)
            os.chdir(repo)
            clear_cache()
            
            from system.utils.path_resolver import format_output_message
            
            # Include a path outside the repo
            paths = {
                'Internal file': resolve('docs', 'internal.md'),
                'External file': external_dir / 'external.md',
            }
            
            output = format_output_message(paths)
            
            # Internal should be relative
            self.assertIn('docs/internal.md', output)
            # External should be absolute
            self.assertIn(str(external_dir), output)


def run_slash_command_tests():
    """Run all slash command integration tests."""
    suite = unittest.TestSuite()
    
    test_classes = [
        TestSlashCommandIntegration,
        TestCommandPathPatterns,
        TestPathResolutionOutput,
    ]
    
    for test_class in test_classes:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_slash_command_tests()
    sys.exit(0 if success else 1)