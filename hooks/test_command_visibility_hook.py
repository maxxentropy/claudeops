#!/usr/bin/env python3
"""
Tests for the command visibility hook.
"""

import json
import tempfile
import unittest
from pathlib import Path
from command_visibility_hook import (
    find_command_file,
    extract_personas,
    extract_workflow_description,
    format_command_header,
    process_prompt
)


class TestCommandVisibilityHook(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary commands directory with test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.commands_dir = Path(self.temp_dir) / "commands"
        self.commands_dir.mkdir()
        
        # Create test command files
        safe_content = """# /safe - Safe General Workflow

Embody these expert personas:
<!-- INCLUDE: system/personas.md#CODE_REVIEWER -->
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->

Execute any task with full safety checks.
"""
        (self.commands_dir / "safe.md").write_text(safe_content)
        
        fix_content = """# /fix - Systematic Debugging

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SENIOR_TEST_ENGINEER -->
<!-- INCLUDE: system/personas.md#SRE_ENGINEER -->
"""
        (self.commands_dir / "fix.md").write_text(fix_content)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_find_command_file(self):
        """Test finding command files."""
        # Test existing command
        safe_file = find_command_file("safe", self.commands_dir)
        self.assertIsNotNone(safe_file)
        self.assertEqual(safe_file.name, "safe.md")
        
        # Test non-existent command
        fake_file = find_command_file("nonexistent", self.commands_dir)
        self.assertIsNone(fake_file)
    
    def test_extract_personas(self):
        """Test extracting personas from content."""
        content = """
<!-- INCLUDE: system/personas.md#CODE_REVIEWER -->
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
Some other content
<!-- INCLUDE: system/personas.md#SECURITY_ENGINEER -->
"""
        personas = extract_personas(content)
        self.assertEqual(len(personas), 3)
        self.assertIn("Code Reviewer (Quality Guardian)", personas)
        self.assertIn("Software Architect (Systems Thinker)", personas)
        self.assertIn("Security Engineer (Paranoid Guardian)", personas)
    
    def test_extract_workflow_description(self):
        """Test extracting workflow descriptions."""
        # Test with title line
        content = "# /safe - Safe General Workflow\nOther content"
        workflow = extract_workflow_description("safe", content)
        self.assertEqual(workflow, "Safe General Workflow")
        
        # Test fallback for known command
        workflow = extract_workflow_description("commit", "")
        self.assertEqual(workflow, "Safe Git Commit with Pre-commit Verification")
        
        # Test unknown command
        workflow = extract_workflow_description("unknown", "")
        self.assertEqual(workflow, "Unknown Workflow")
    
    def test_format_command_header(self):
        """Test formatting the command header."""
        header = format_command_header(
            "safe",
            "Safe General Workflow",
            ["Code Reviewer", "Software Architect"]
        )
        self.assertIn("🎯 COMMAND: /safe", header)
        self.assertIn("📋 WORKFLOW: Safe General Workflow", header)
        self.assertIn("👤 PERSONAS: Code Reviewer + Software Architect", header)
        self.assertIn("=====================================", header)
    
    def test_process_prompt_with_command(self):
        """Test processing a slash command prompt."""
        input_data = {"prompt": "/safe refactor authentication"}
        result = process_prompt(input_data, self.commands_dir)
        
        self.assertIsNotNone(result)
        self.assertIn("🎯 COMMAND: /safe", result['prompt'])
        self.assertIn("📋 WORKFLOW:", result['prompt'])
        self.assertIn("👤 PERSONAS:", result['prompt'])
        self.assertIn("refactor authentication", result['prompt'])
    
    def test_process_prompt_without_command(self):
        """Test processing a non-command prompt."""
        input_data = {"prompt": "Just regular text"}
        result = process_prompt(input_data, self.commands_dir)
        self.assertIsNone(result)
    
    def test_process_prompt_unknown_command(self):
        """Test processing an unknown command."""
        input_data = {"prompt": "/unknown some args"}
        result = process_prompt(input_data, self.commands_dir)
        self.assertIsNone(result)  # Should pass through for validator hook
    
    def test_header_prepended_correctly(self):
        """Test that header is prepended, not replacing original prompt."""
        input_data = {"prompt": "/safe important task with args"}
        result = process_prompt(input_data, self.commands_dir)
        
        self.assertIsNotNone(result)
        # Should contain both header and original command
        self.assertIn("🎯 COMMAND: /safe", result['prompt'])
        self.assertIn("/safe important task with args", result['prompt'])
        
        # Header should come before the original command
        header_pos = result['prompt'].find("🎯 COMMAND: /safe")
        command_pos = result['prompt'].find("/safe important task with args")
        self.assertLess(header_pos, command_pos)


if __name__ == "__main__":
    unittest.main()