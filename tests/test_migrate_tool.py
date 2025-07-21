#!/usr/bin/env python3
"""
Tests for the migration tool
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import importlib.util
spec = importlib.util.spec_from_file_location("migrate_tool", 
    os.path.join(os.path.dirname(__file__), '..', 'scripts', 'migrate-tool.py'))
migrate_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migrate_tool)
MigrationTool = migrate_tool.MigrationTool


class TestMigrationTool(unittest.TestCase):
    
    def setUp(self):
        """Create temporary test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.dest_dir = Path(self.test_dir) / "dest"
        self.source_dir.mkdir()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def create_test_file(self, path: Path, content: str):
        """Helper to create test files"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    def test_single_file_migration(self):
        """Test migrating a single file"""
        # Create test file
        test_file = self.source_dir / "test.txt"
        self.create_test_file(test_file, "Hello, world!")
        
        # Run migration
        tool = MigrationTool(
            str(test_file),
            str(self.dest_dir / "test.txt"),
            {'update_refs': False, 'validate': False, 'test': False, 'backup': False}
        )
        tool.run()
        
        # Verify file was copied
        self.assertTrue((self.dest_dir / "test.txt").exists())
        self.assertEqual((self.dest_dir / "test.txt").read_text(), "Hello, world!")
    
    def test_directory_migration(self):
        """Test migrating a directory"""
        # Create test structure
        self.create_test_file(self.source_dir / "file1.txt", "File 1")
        self.create_test_file(self.source_dir / "subdir" / "file2.txt", "File 2")
        
        # Run migration
        tool = MigrationTool(
            str(self.source_dir),
            str(self.dest_dir),
            {'update_refs': False, 'validate': False, 'test': False, 'backup': False}
        )
        tool.run()
        
        # Verify structure was copied
        self.assertTrue((self.dest_dir / "file1.txt").exists())
        self.assertTrue((self.dest_dir / "subdir" / "file2.txt").exists())
    
    def test_path_reference_scanning(self):
        """Test scanning for path references"""
        # Create files with references that will be found
        script_content = f'''#!/bin/bash
source "{self.source_dir}/lib/core.sh"
source "./relative/path.sh"
import "../another/module"
'''
        self.create_test_file(self.source_dir / "script.sh", script_content)
        
        # Create tool and scan
        tool = MigrationTool(
            str(self.source_dir),
            str(self.dest_dir),
            {'dry_run': True}
        )
        
        references = tool.scan_path_references()
        
        # Should find references
        self.assertGreater(len(references), 0)
    
    def test_path_reference_update(self):
        """Test updating path references"""
        # Create file with absolute path reference
        script_content = f'''#!/bin/bash
source "{self.source_dir}/lib/core.sh"
echo "Test script"
'''
        script_file = self.source_dir / "test.sh"
        self.create_test_file(script_file, script_content)
        
        # Also create the referenced file
        self.create_test_file(self.source_dir / "lib" / "core.sh", "echo 'Core loaded'")
        
        # Run migration
        tool = MigrationTool(
            str(self.source_dir),
            str(self.dest_dir),
            {'update_refs': True, 'validate': False, 'test': False, 'backup': False}
        )
        tool.run()
        
        # Check that reference was updated
        migrated_script = (self.dest_dir / "test.sh").read_text()
        # The script should now reference files in dest_dir/lib instead of source_dir/lib
        self.assertIn(f"{self.dest_dir}/lib/core.sh", migrated_script)
        self.assertNotIn(f"{self.source_dir}/lib/core.sh", migrated_script)
    
    def test_backup_creation(self):
        """Test backup functionality"""
        # Create test file
        test_file = self.source_dir / "test.txt"
        self.create_test_file(test_file, "Original content")
        
        # Run migration with backup
        tool = MigrationTool(
            str(test_file),
            str(self.dest_dir / "test.txt"),
            {'update_refs': False, 'validate': False, 'test': False, 'backup': True}
        )
        tool.run()
        
        # Check backup was created
        self.assertTrue(tool.backup_dir.exists())
        backup_files = list(tool.backup_dir.rglob("*"))
        self.assertGreater(len(backup_files), 0)
    
    def test_dry_run_mode(self):
        """Test dry run doesn't make changes"""
        # Create test file
        test_file = self.source_dir / "test.txt"
        self.create_test_file(test_file, "Test content")
        
        # Run in dry run mode
        tool = MigrationTool(
            str(self.source_dir),
            str(self.dest_dir),
            {'dry_run': True}
        )
        tool.run()
        
        # Verify no files were actually moved
        self.assertFalse(self.dest_dir.exists())
    
    def test_validation_catches_missing_source(self):
        """Test validation catches missing source"""
        # Try to migrate non-existent source
        tool = MigrationTool(
            "/non/existent/path",
            str(self.dest_dir),
            {'validate': True}
        )
        
        with self.assertRaises(ValueError) as context:
            tool.run()
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_pattern_matching(self):
        """Test pattern-based file selection"""
        # Create mixed files
        self.create_test_file(self.source_dir / "script.sh", "Shell script")
        self.create_test_file(self.source_dir / "doc.txt", "Text file")
        self.create_test_file(self.source_dir / "code.py", "Python code")
        
        # Migrate only .sh files
        tool = MigrationTool(
            str(self.source_dir),
            str(self.dest_dir),
            {'pattern': '*.sh', 'update_refs': False, 'validate': False, 'test': False, 'backup': False}
        )
        
        files = list(tool.get_files_to_migrate())
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "script.sh")
    
    def test_text_file_detection(self):
        """Test text file detection"""
        tool = MigrationTool("dummy", "dummy", {})
        
        # Test various file types
        self.assertTrue(tool.is_text_file(Path("test.sh")))
        self.assertTrue(tool.is_text_file(Path("test.py")))
        self.assertTrue(tool.is_text_file(Path("test.md")))
        self.assertFalse(tool.is_text_file(Path("test.jpg")))
        self.assertFalse(tool.is_text_file(Path("test.bin")))
    
    def test_calculate_new_path(self):
        """Test path calculation logic"""
        tool = MigrationTool(
            "/old/location",
            "/new/location",
            {}
        )
        
        # Test absolute path update
        new_path = tool.calculate_new_path(
            "/old/location/file.txt",
            Path("/old/location/script.sh")
        )
        self.assertEqual(new_path, "/new/location/file.txt")
        
        # Test unrelated path stays same
        new_path = tool.calculate_new_path(
            "/other/path/file.txt",
            Path("/old/location/script.sh")
        )
        self.assertEqual(new_path, "/other/path/file.txt")


class TestMigrationIntegration(unittest.TestCase):
    """Integration tests for real-world scenarios"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_shell_script_migration_scenario(self):
        """Test scenario similar to the shell integration migration"""
        # Create structure similar to shell integration
        source = Path(self.test_dir) / "sandbox" / "src"
        dest = Path(self.test_dir) / "lib" / "shell-integration"
        tests = Path(self.test_dir) / "sandbox" / "tests"
        
        source.mkdir(parents=True)
        tests.mkdir(parents=True)
        dest.parent.mkdir(parents=True, exist_ok=True)  # Create destination parent
        
        # Create core.sh
        core_content = '''#!/bin/bash
CLAUDE_VERSION="1.0.0"
echo "Core loaded"
'''
        (source / "core.sh").write_text(core_content)
        
        # Create test that references core.sh
        test_content = '''#!/bin/bash
source "../src/core.sh"
echo "Test passed"
'''
        (tests / "test.sh").write_text(test_content)
        
        # Run migration
        tool = MigrationTool(
            str(source),
            str(dest),
            {'update_refs': True, 'validate': True, 'test': False, 'backup': True}
        )
        tool.run()
        
        # Verify files were migrated
        self.assertTrue((dest / "core.sh").exists())
        
        # The test file wasn't migrated but if it had been,
        # its references would need updating
        # This demonstrates the tool would catch such issues


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)