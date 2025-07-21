#!/usr/bin/env python3
"""
Slash command validation for use in hooks.
Returns non-zero exit code if command is invalid.
"""

import sys
import os
from pathlib import Path
from typing import List, Optional, Tuple
import re


def find_available_commands(commands_dir: Path = None) -> List[str]:
    """Find all available slash commands."""
    if commands_dir is None:
        commands_dir = Path(os.path.expanduser("~/.claude/commands"))
    
    commands = []
    
    for md_file in commands_dir.rglob("*.md"):
        if md_file.name in ['newcmd.md', 'README.md', 'template.md']:
            continue
            
        command_name = md_file.stem
        commands.append(command_name)
    
    return sorted(list(set(commands)))


def find_similar_commands(typed_command: str, available_commands: List[str]) -> List[str]:
    """Find commands similar to what was typed."""
    from difflib import SequenceMatcher
    
    similar = []
    
    for cmd in available_commands:
        similarity = SequenceMatcher(None, typed_command.lower(), cmd.lower()).ratio()
        
        if typed_command.lower() in cmd.lower() or cmd.lower() in typed_command.lower():
            similarity = max(similarity, 0.7)
        
        if similarity >= 0.6:
            similar.append((cmd, similarity))
    
    return [cmd for cmd, _ in sorted(similar, key=lambda x: x[1], reverse=True)[:3]]


def main():
    """Main validation function for hook usage."""
    if len(sys.argv) < 2:
        sys.exit(0)  # No input, allow through
    
    user_input = sys.argv[1]
    
    # Only validate slash commands
    if not user_input.startswith('/'):
        sys.exit(0)  # Not a slash command, allow through
    
    # Extract command
    command_parts = user_input[1:].split()
    if not command_parts:
        sys.exit(0)
    
    command_name = command_parts[0].lower()
    
    # Get available commands
    available = find_available_commands()
    
    # Check if valid
    if command_name in available:
        sys.exit(0)  # Valid command, allow through
    
    # Invalid command - format error message
    similar = find_similar_commands(command_name, available)
    
    error_lines = [f"Unrecognized command: /{command_name}"]
    
    if similar:
        error_lines.append("\nDid you mean:")
        for cmd in similar:
            error_lines.append(f"  /{cmd}")
    else:
        error_lines.append("\nNo similar commands found.")
    
    error_lines.append("\nType /help for available commands.")
    
    # Print error and exit with non-zero code to block
    print("\n".join(error_lines))
    sys.exit(1)


if __name__ == "__main__":
    main()