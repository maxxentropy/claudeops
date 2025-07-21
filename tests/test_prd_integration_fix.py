#!/usr/bin/env python3
"""
Comprehensive tests for PRD integration fix module.
Tests path sanitization, import transformation, and integration workflow.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys
import os

# Add lib directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from prd_integration_fix import (
    sanitize_python_path,
    transform_imports,
    detect_import_issues,
    create_init_files,
    validate_python_imports,
    generate_enhanced_mapping,
    apply_integration_fixes,
    create_integration_preview
)


class TestPathSanitization(unittest.TestCase):
    """Test Python path sanitization functions."""
    
    def test_sanitize_directory_with_hyphen(self):
        """Test that hyphens in directory names are converted to underscores."""
        self.assertEqual(sanitize_python_path('lib/prd-parallel/'), 'lib/prd_parallel/')
        self.assertEqual(sanitize_python_path('tests/prd-parallel/'), 'tests/prd_parallel/')
        
    def test_sanitize_nested_directories(self):
        """Test sanitization of nested directory structures."""
        path = 'lib/prd-parallel/sub-module/another-dir/'
        expected = 'lib/prd_parallel/sub_module/another_dir/'
        self.assertEqual(sanitize_python_path(path), expected)
        
    def test_preserve_python_filenames(self):
        """Test that .py file names are not modified."""
        path = 'lib/prd-parallel/my-test-file.py'
        expected = 'lib/prd_parallel/my-test-file.py'
        self.assertEqual(sanitize_python_path(path), expected)
        
    def test_no_change_needed(self):
        """Test paths that don't need sanitization."""
        self.assertEqual(sanitize_python_path('lib/my_package/'), 'lib/my_package/')
        self.assertEqual(sanitize_python_path('test.py'), 'test.py')


class TestImportTransformation(unittest.TestCase):
    """Test import statement transformations."""
    
    def test_transform_from_imports(self):
        """Test transformation of 'from x import y' statements."""
        code = """
from models.parallel_execution import PhaseInfo
from analyzers.wave_calculator import WaveCalculator
from core.resource_manager import Lock
"""
        expected = """
from prd_parallel.models.parallel_execution import PhaseInfo
from prd_parallel.analyzers.wave_calculator import WaveCalculator
from prd_parallel.core.resource_manager import Lock
"""
        result = transform_imports(code, 'prd_parallel')
        self.assertEqual(result.strip(), expected.strip())
        
    def test_transform_import_statements(self):
        """Test transformation of 'import x' statements."""
        code = """
import models.parallel_execution
import analyzers.wave_calculator
"""
        expected = """
import prd_parallel.models.parallel_execution
import prd_parallel.analyzers.wave_calculator
"""
        result = transform_imports(code, 'prd_parallel')
        self.assertEqual(result.strip(), expected.strip())
        
    def test_preserve_stdlib_imports(self):
        """Test that standard library imports are not modified."""
        code = """
import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        result = transform_imports(code, 'prd_parallel')
        self.assertEqual(result.strip(), code.strip())
        
    def test_mixed_imports(self):
        """Test file with mix of imports."""
        code = """
import os
from models.base import BaseModel
import sys
from analyzers.engine import analyze
from typing import Optional
"""
        expected = """
import os
from prd_parallel.models.base import BaseModel
import sys
from prd_parallel.analyzers.engine import analyze
from typing import Optional
"""
        result = transform_imports(code, 'prd_parallel')
        self.assertEqual(result.strip(), expected.strip())


class TestImportDetection(unittest.TestCase):
    """Test detection of import issues."""
    
    def test_detect_relative_imports(self):
        """Test detection of relative imports that need transformation."""
        code = """
import os
from models.base import BaseModel
from analyzers.engine import Engine
"""
        issues = detect_import_issues('test.py', code)
        self.assertEqual(len(issues), 2)
        self.assertIn('models.base', issues[0])
        self.assertIn('analyzers.engine', issues[1])
        
    def test_no_issues_with_absolute_imports(self):
        """Test that properly formatted imports are not flagged."""
        code = """
import os
from prd_parallel.models.base import BaseModel
from typing import List
"""
        issues = detect_import_issues('test.py', code)
        self.assertEqual(len(issues), 0)


class TestEnhancedMapping(unittest.TestCase):
    """Test enhanced mapping generation."""
    
    def test_generate_mapping_with_sanitized_name(self):
        """Test mapping generation converts project name correctly."""
        mapping = generate_enhanced_mapping('my-awesome-project')
        self.assertEqual(mapping['python_package_name'], 'my_awesome_project')
        self.assertIn('lib/my_awesome_project/', mapping['mappings']['src/'])
        
    def test_integration_rules_included(self):
        """Test that all integration rules are included."""
        mapping = generate_enhanced_mapping('test-project')
        rules = mapping['integration_rules']
        self.assertTrue(rules['sanitize_python_names'])
        self.assertTrue(rules['transform_imports'])
        self.assertTrue(rules['create_init_files'])
        self.assertTrue(rules['validate_imports'])


class TestIntegrationWorkflow(unittest.TestCase):
    """Test the complete integration workflow."""
    
    def setUp(self):
        """Create temporary directories for testing."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.source_dir = self.test_dir / 'sandbox' / 'src'
        self.target_dir = self.test_dir / 'integrated'
        self.source_dir.mkdir(parents=True)
        
    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.test_dir)
        
    def test_create_init_files(self):
        """Test automatic creation of __init__.py files."""
        # Create directory structure
        (self.source_dir / 'models').mkdir()
        (self.source_dir / 'analyzers').mkdir()
        (self.source_dir / 'models' / 'test.py').write_text('# Test file')
        (self.source_dir / 'analyzers' / 'engine.py').write_text('# Engine')
        
        # Create init files
        created = create_init_files(self.source_dir)
        
        # Verify init files were created
        self.assertTrue((self.source_dir / 'models' / '__init__.py').exists())
        self.assertTrue((self.source_dir / 'analyzers' / '__init__.py').exists())
        # Should create init files for: root, models, analyzers
        self.assertGreaterEqual(len(created), 2)
        
    def test_apply_integration_fixes(self):
        """Test the complete integration fix process."""
        # Create source structure with hyphenated names
        models_dir = self.source_dir / 'models'
        models_dir.mkdir()
        
        # Create a Python file with relative imports
        test_file = models_dir / 'base.py'
        test_file.write_text("""
from models.core import Core
from analyzers.engine import Engine

class BaseModel:
    pass
""")
        
        # Create mapping config
        mapping = {
            'python_package_name': 'test_package',
            'integration_rules': {
                'sanitize_python_names': True,
                'transform_imports': True,
                'create_init_files': True
            }
        }
        
        # Apply integration fixes
        files_processed, issues = apply_integration_fixes(
            self.source_dir, self.target_dir, mapping
        )
        
        # Verify results
        self.assertGreater(files_processed, 0)
        
        # Check that file was copied and transformed
        target_file = self.target_dir / 'models' / 'base.py'
        self.assertTrue(target_file.exists())
        
        # Check that imports were transformed
        content = target_file.read_text()
        self.assertIn('from test_package.models.core import Core', content)
        self.assertIn('from test_package.analyzers.engine import Engine', content)
        
        # Check that __init__.py was created
        self.assertTrue((self.target_dir / 'models' / '__init__.py').exists())
        
    def test_integration_preview(self):
        """Test preview generation."""
        # Create test structure
        (self.source_dir / 'test-module').mkdir()
        (self.source_dir / 'test-module' / 'core.py').write_text("""
from models.base import Base
import analyzers.engine
""")
        
        mapping = generate_enhanced_mapping('test-project')
        preview = create_integration_preview(self.source_dir, mapping)
        
        # Verify preview contains expected information
        self.assertIn('Python files found:', preview)
        self.assertIn('Python Module Name Corrections:', preview)
        self.assertIn('Import Transformations:', preview)


class TestEndToEndScenario(unittest.TestCase):
    """Test a complete realistic scenario."""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_realistic_prd_integration(self):
        """Test integration of a realistic PRD project structure."""
        # Create sandbox structure mimicking the parallel-prd project
        sandbox = self.test_dir / 'sandbox' / 'src'
        sandbox.mkdir(parents=True)
        
        # Create project structure with at least one file in each
        for dir_name in ['models', 'analyzers', 'core', 'orchestrator']:
            dir_path = sandbox / dir_name
            dir_path.mkdir()
            # Add a dummy file to ensure directory is copied
            (dir_path / '__init__.py').write_text('# Package init')
            
        # Create files with problematic imports
        (sandbox / 'models' / 'execution.py').write_text("""
from models.state import State
from core.manager import Manager

class Execution:
    def __init__(self):
        self.state = State()
        self.manager = Manager()
""")
        
        (sandbox / 'analyzers' / 'calculator.py').write_text("""
from models.execution import Execution
import orchestrator.parallel

def calculate():
    exec = Execution()
    return exec
""")
        
        # Create target directory
        target = self.test_dir / 'lib'
        
        # Generate mapping
        mapping = generate_enhanced_mapping('prd-parallel')
        
        # Apply fixes
        files_processed, issues = apply_integration_fixes(sandbox, target, mapping)
        
        # Verify structure
        self.assertTrue((target / 'models' / 'execution.py').exists())
        self.assertTrue((target / 'analyzers' / 'calculator.py').exists())
        
        # Verify imports were transformed
        exec_content = (target / 'models' / 'execution.py').read_text()
        self.assertIn('from prd_parallel.models.state import State', exec_content)
        self.assertIn('from prd_parallel.core.manager import Manager', exec_content)
        
        calc_content = (target / 'analyzers' / 'calculator.py').read_text()
        self.assertIn('from prd_parallel.models.execution import Execution', calc_content)
        self.assertIn('import prd_parallel.orchestrator.parallel', calc_content)
        
        # Verify __init__.py files created
        for dir_name in ['models', 'analyzers', 'core', 'orchestrator']:
            init_file = target / dir_name / '__init__.py'
            if not init_file.exists():
                # Debug: list what files are in the directory
                dir_path = target / dir_name
                if dir_path.exists():
                    files = list(dir_path.iterdir())
                    print(f"\nDebug: {dir_name} contains: {files}")
                else:
                    print(f"\nDebug: {dir_name} directory doesn't exist!")
            self.assertTrue(init_file.exists(), f"Missing {init_file}")


if __name__ == '__main__':
    # Run all tests with verbose output
    unittest.main(verbosity=2)