#!/usr/bin/env python3
"""Test suite for Phase 3 of consistent slash command paths implementation."""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
import unittest

# Add system utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from system.utils import (
    PathResolver,
    resolve,
    ensure_directory,
    get_prd_path,
    get_workspace_path,
    clear_cache
)


class TestPhase3PathResolution(unittest.TestCase):
    """Test Phase 3 features for path resolution."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a mock git repository
        git_dir = Path(self.test_dir) / '.git'
        git_dir.mkdir()
        
        # Clear any cached values
        clear_cache()
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        clear_cache()
        
    def test_project_overrides_loading(self):
        """Test loading project-specific overrides from .claude-paths.json."""
        # Create override file
        overrides = {
            "prds": "custom/requirements",
            "tests": "test_suite",
            "lib": "source"
        }
        
        override_path = Path(self.test_dir) / '.claude-paths.json'
        with open(override_path, 'w') as f:
            json.dump(overrides, f)
            
        # Create new resolver to load overrides
        resolver = PathResolver()
        
        # Test that overrides are applied
        prd_path = resolver.resolve('prds')
        self.assertTrue(str(prd_path).endswith('custom/requirements'))
        
        test_path = resolver.resolve('tests')
        self.assertTrue(str(test_path).endswith('test_suite'))
        
        lib_path = resolver.resolve('lib')
        self.assertTrue(str(lib_path).endswith('source'))
        
    def test_project_overrides_invalid_json(self):
        """Test handling of invalid .claude-paths.json."""
        # Create invalid JSON file
        override_path = Path(self.test_dir) / '.claude-paths.json'
        with open(override_path, 'w') as f:
            f.write("{ invalid json")
            
        # Should not raise exception, just use defaults
        resolver = PathResolver()
        prd_path = resolver.resolve('prds')
        self.assertTrue(str(prd_path).endswith('docs/prds'))
        
    def test_project_overrides_unknown_path_type(self):
        """Test handling of unknown path types in overrides."""
        # Create override with unknown path type
        overrides = {
            "prds": "custom/requirements",
            "unknown_type": "some/path",
            "_comment": "This is a comment"
        }
        
        override_path = Path(self.test_dir) / '.claude-paths.json'
        with open(override_path, 'w') as f:
            json.dump(overrides, f)
            
        # Should load valid overrides and ignore unknown
        resolver = PathResolver()
        prd_path = resolver.resolve('prds')
        self.assertTrue(str(prd_path).endswith('custom/requirements'))
        
        # Unknown type should raise ValueError
        with self.assertRaises(ValueError):
            resolver.resolve('unknown_type')
            
    def test_command_path_resolution_tdd(self):
        """Test that TDD command uses path resolution."""
        # Create tests directory
        test_dir = ensure_directory('tests')
        self.assertTrue(test_dir.exists())
        
        # Simulate TDD creating a test file
        test_file = resolve('tests', 'test_feature.py')
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Test file")
        
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.parent, test_dir)
        
    def test_command_path_resolution_api_crud(self):
        """Test that api-crud command uses path resolution."""
        # Test controller path - resolve takes path_type and optional filename
        controller_path = resolve('lib', 'controllers/UserController.cs')
        self.assertTrue(str(controller_path).endswith('controllers/UserController.cs'))
        
        # Test service path
        service_path = resolve('lib', 'services/UserService.cs')
        self.assertTrue(str(service_path).endswith('services/UserService.cs'))
        
        # Test DTO path
        dto_path = resolve('lib', 'dtos/UserDto.cs')
        self.assertTrue(str(dto_path).endswith('dtos/UserDto.cs'))
        
        # Test API test path
        test_path = resolve('tests', 'api/UserControllerTests.cs')
        self.assertTrue(str(test_path).endswith('api/UserControllerTests.cs'))
        
    def test_command_path_resolution_mobile_scaffold(self):
        """Test that mobile-scaffold command uses path resolution."""
        project_name = "TestMobileApp"
        
        # Test project root
        project_root = resolve('lib', project_name)
        self.assertTrue(str(project_root).endswith(f'{project_name}'))
        
        # Test module paths - resolve only takes path_type and filename
        auth_module = resolve('lib', f'{project_name}/Modules/Authentication/AuthenticationModule.cs')
        self.assertTrue('Modules/Authentication' in str(auth_module))
        
        # Test main program path
        maui_program = resolve('lib', f'{project_name}/MauiProgram.cs')
        self.assertTrue(str(maui_program).endswith('MauiProgram.cs'))
        
    def test_path_resolution_with_project_overrides(self):
        """Test complete path resolution with project overrides."""
        # Create project overrides
        overrides = {
            "prds": "documentation/requirements",
            "prd_workspace": ".project/workspaces",
            "tests": "test_suite",
            "lib": "src"
        }
        
        override_path = Path(self.test_dir) / '.claude-paths.json'
        with open(override_path, 'w') as f:
            json.dump(overrides, f)
            
        # Clear any cached resolver to force reload
        from system.utils.path_resolver import _resolver
        from system.utils.repo_detector import _detector
        _resolver._project_overrides_loaded = False
        _resolver._path_overrides.clear()
        _resolver._repo_root = None
        _detector._cache.clear()
        
        # Test PRD path with override
        prd_path = get_prd_path('test-feature')
        # Print for debugging
        print(f"PRD path: {prd_path}")
        print(f"Test dir: {self.test_dir}")
        self.assertTrue('documentation/requirements' in str(prd_path))
        self.assertTrue(prd_path.name.endswith('test-feature.md'))
        
        # Test workspace path with override
        workspace_path = get_workspace_path('test-feature')
        self.assertTrue('.project/workspaces' in str(workspace_path))
        self.assertTrue(str(workspace_path).endswith('test-feature'))
        
    def test_environment_override_precedence(self):
        """Test that environment variables take precedence over project overrides."""
        # Create project overrides
        overrides = {
            "prds": "documentation/requirements"
        }
        
        override_path = Path(self.test_dir) / '.claude-paths.json'
        with open(override_path, 'w') as f:
            json.dump(overrides, f)
            
        # Set environment override
        env_override = tempfile.mkdtemp()
        os.environ['CLAUDE_OUTPUT_ROOT'] = env_override
        
        try:
            # Clear cache and resolver state to force reload
            clear_cache()
            from system.utils.path_resolver import _resolver
            _resolver._project_overrides_loaded = False
            _resolver._path_overrides.clear()
            
            # Environment override should take precedence
            prd_path = resolve('prds')
            prd_path_resolved = str(prd_path.resolve())
            env_resolved = str(Path(env_override).resolve())
            self.assertTrue(prd_path_resolved.startswith(env_resolved))
            self.assertFalse('documentation/requirements' in str(prd_path))
            
        finally:
            del os.environ['CLAUDE_OUTPUT_ROOT']
            shutil.rmtree(env_override)
            
    def test_multiple_path_type_resolution(self):
        """Test resolving multiple path types in one session."""
        # This simulates a command that creates files in multiple locations
        paths = {
            'Controller': resolve('lib', 'controllers', 'TestController.cs'),
            'Service': resolve('lib', 'services', 'TestService.cs'),
            'Test': resolve('tests', 'TestControllerTests.cs'),
            'Documentation': resolve('docs', 'api', 'test-api.md')
        }
        
        # All paths should be resolved correctly
        for desc, path in paths.items():
            self.assertTrue(path.is_absolute())
            self.assertIsInstance(path, Path)
            
        # Ensure directories can be created
        for path in paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
            self.assertTrue(path.parent.exists())


class TestPathInfoCommand(unittest.TestCase):
    """Test the /path-info command functionality."""
    
    def test_path_info_output_structure(self):
        """Test that path-info command produces expected output structure."""
        # This test verifies the command logic rather than executing it
        from system.utils import PathResolver, find_repo_root
        
        # Test getting repository info
        repo_root = find_repo_root()
        self.assertIsNotNone(repo_root)
        
        # Test resolver can list all path types
        resolver = PathResolver()
        self.assertIn('prds', resolver.DEFAULT_PATHS)
        self.assertIn('tests', resolver.DEFAULT_PATHS)
        self.assertIn('lib', resolver.DEFAULT_PATHS)
        
        # Test checking for overrides
        if hasattr(resolver, '_path_overrides'):
            self.assertIsInstance(resolver._path_overrides, dict)


def run_phase3_tests():
    """Run all Phase 3 tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPhase3PathResolution))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPathInfoCommand))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_phase3_tests()
    sys.exit(0 if success else 1)