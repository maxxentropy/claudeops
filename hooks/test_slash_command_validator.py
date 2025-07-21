#!/usr/bin/env python3
"""
Tests for slash command validation hook.
Run with: python3 test_slash_command_validator.py
"""

import unittest
import json
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the validator (will create next)
# from slash_command_validator import validate_prompt


class TestSlashCommandValidator(unittest.TestCase):
    """Test the slash command validation hook."""
    
    def setUp(self):
        """Create a temporary commands directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.commands_dir = Path(self.temp_dir) / "commands"
        self.commands_dir.mkdir()
        
        # Create some test command files
        (self.commands_dir / "safe.md").write_text("# /safe command")
        (self.commands_dir / "build.md").write_text("# /build command")
        (self.commands_dir / "prdq.md").write_text("# /prdq command")
        
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
        
    def test_valid_slash_command(self):
        """Test that valid commands are allowed through."""
        from slash_command_validator import validate_prompt
        
        # Test input
        input_data = {
            "prompt": "/safe run tests",
            "session_id": "test-123",
            "cwd": "/test"
        }
        
        result = validate_prompt(input_data, self.commands_dir)
        
        # Should return None or empty dict to allow
        self.assertIn(result, [None, {}])
        
    def test_invalid_slash_command(self):
        """Test that invalid commands are blocked."""
        from slash_command_validator import validate_prompt
        
        # Test input with invalid command
        input_data = {
            "prompt": "/save something",
            "session_id": "test-123",
            "cwd": "/test"
        }
        
        result = validate_prompt(input_data, self.commands_dir)
        
        # Should return block decision
        self.assertIsInstance(result, dict)
        self.assertEqual(result["decision"], "block")
        self.assertIn("Unrecognized command: /save", result["reason"])
        self.assertIn("/safe", result["reason"])  # Should suggest similar
        
    def test_non_slash_command(self):
        """Test that non-slash commands pass through."""
        from slash_command_validator import validate_prompt
        
        # Test input without slash
        input_data = {
            "prompt": "just a normal message",
            "session_id": "test-123",
            "cwd": "/test"
        }
        
        result = validate_prompt(input_data, self.commands_dir)
        
        # Should allow through
        self.assertIn(result, [None, {}])
        
    def test_empty_slash_command(self):
        """Test handling of just a slash."""
        from slash_command_validator import validate_prompt
        
        input_data = {
            "prompt": "/ ",
            "session_id": "test-123",
            "cwd": "/test"
        }
        
        result = validate_prompt(input_data, self.commands_dir)
        
        # Should allow through (not a real command)
        self.assertIn(result, [None, {}])
        
    def test_command_with_arguments(self):
        """Test commands with arguments are validated correctly."""
        from slash_command_validator import validate_prompt
        
        # Valid command with args
        input_data = {
            "prompt": "/prdq create user authentication system",
            "session_id": "test-123",
            "cwd": "/test"
        }
        
        result = validate_prompt(input_data, self.commands_dir)
        self.assertIn(result, [None, {}])
        
    def test_case_insensitive_matching(self):
        """Test that command matching is case insensitive."""
        from slash_command_validator import validate_prompt
        
        input_data = {
            "prompt": "/SAFE run tests",
            "session_id": "test-123",
            "cwd": "/test"
        }
        
        result = validate_prompt(input_data, self.commands_dir)
        self.assertIn(result, [None, {}])
        
    def test_similar_command_suggestions(self):
        """Test that similar commands are suggested."""
        from slash_command_validator import validate_prompt
        
        # Create a command similar to what user might mistype
        (self.commands_dir / "fix.md").write_text("# /fix command")
        
        input_data = {
            "prompt": "/quickfix something",
            "session_id": "test-123",
            "cwd": "/test"
        }
        
        result = validate_prompt(input_data, self.commands_dir)
        
        self.assertEqual(result["decision"], "block")
        self.assertIn("/fix", result["reason"])
        
    def test_hook_json_format(self):
        """Test the complete hook flow with JSON input/output."""
        from slash_command_validator import main
        
        # Simulate hook input
        hook_input = {
            "prompt": "/invalid-command test",
            "session_id": "test-123",
            "transcript_path": "/tmp/transcript.txt",
            "cwd": "/test",
            "hook_event_name": "UserPromptSubmit"
        }
        
        # Mock stdin and capture stdout
        import io
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        
        try:
            sys.stdin = io.StringIO(json.dumps(hook_input))
            sys.stdout = io.StringIO()
            
            # Set commands dir via environment
            os.environ['CLAUDE_COMMANDS_DIR'] = str(self.commands_dir)
            
            # Run main
            main()
            
            # Get output
            output = sys.stdout.getvalue()
            
            # Should be valid JSON
            result = json.loads(output)
            self.assertEqual(result["decision"], "block")
            
        finally:
            sys.stdin = old_stdin
            sys.stdout = old_stdout
            if 'CLAUDE_COMMANDS_DIR' in os.environ:
                del os.environ['CLAUDE_COMMANDS_DIR']


if __name__ == '__main__':
    unittest.main(verbosity=2)