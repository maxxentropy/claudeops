#!/usr/bin/env python3
"""
Slash command validation hook for Claude Code.
Validates slash commands before execution to prevent unrecognized commands.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from difflib import SequenceMatcher


def find_available_commands(commands_dir: Path = None) -> List[str]:
    """
    Find all available slash commands by scanning the commands directory.
    
    Returns:
        List of available command names (without the slash)
    """
    if commands_dir is None:
        # Check environment variable first
        env_dir = os.environ.get('CLAUDE_COMMANDS_DIR')
        if env_dir:
            commands_dir = Path(env_dir)
        else:
            commands_dir = Path(os.path.expanduser("~/.claude/commands"))
    
    commands = []
    
    if not commands_dir.exists():
        return commands
    
    for md_file in commands_dir.rglob("*.md"):
        # Skip template files and non-command files
        if md_file.name in ['newcmd.md', 'README.md', 'template.md']:
            continue
            
        # Extract command name from filename
        command_name = md_file.stem
        commands.append(command_name)
        
        # Also add the path-based format (e.g., "core:commit" for commands/core/commit.md)
        relative_path = md_file.relative_to(commands_dir)
        if relative_path.parent != Path('.'):
            # Has a subdirectory
            path_parts = list(relative_path.parent.parts)
            path_command = ':'.join(path_parts + [command_name])
            commands.append(path_command)
    
    return sorted(list(set(commands)))


def find_similar_commands(typed_command: str, available_commands: List[str], threshold: float = 0.6) -> List[str]:
    """
    Find commands similar to what was typed using string similarity.
    
    Args:
        typed_command: The command user typed (without slash)
        available_commands: List of valid commands
        threshold: Minimum similarity score (0-1)
        
    Returns:
        List of similar command names, sorted by similarity
    """
    similar = []
    
    for cmd in available_commands:
        # Calculate similarity
        similarity = SequenceMatcher(None, typed_command.lower(), cmd.lower()).ratio()
        
        # Boost score if one is substring of the other
        if typed_command.lower() in cmd.lower() or cmd.lower() in typed_command.lower():
            similarity = max(similarity, 0.7)
        
        if similarity >= threshold:
            similar.append((cmd, similarity))
    
    # Sort by similarity score (highest first) and return just names
    return [cmd for cmd, _ in sorted(similar, key=lambda x: x[1], reverse=True)[:3]]


def validate_prompt(input_data: Dict, commands_dir: Path = None) -> Optional[Dict]:
    """
    Validate a user prompt for slash commands.
    
    Args:
        input_data: Hook input containing 'prompt' and other fields
        commands_dir: Optional commands directory for testing
        
    Returns:
        None/empty dict to allow, or {"decision": "block", "reason": "..."} to block
    """
    prompt = input_data.get('prompt', '').strip()
    
    # Only validate if it starts with a slash
    if not prompt.startswith('/'):
        return None  # Allow non-slash commands
    
    # Extract command parts
    parts = prompt.split()
    if not parts or len(parts[0]) <= 1:
        return None  # Just "/" or empty after slash
    
    # Get command name (without slash)
    command_name = parts[0][1:].lower()
    
    # Get available commands
    available = find_available_commands(commands_dir)
    
    # Check if valid
    if command_name in available:
        return None  # Valid command, allow
    
    # Invalid command - build error message
    similar = find_similar_commands(command_name, available)
    
    error_lines = [f"Unrecognized command: /{command_name}"]
    
    if similar:
        error_lines.append("\nDid you mean:")
        for cmd in similar:
            error_lines.append(f"  /{cmd}")
    else:
        error_lines.append("\nNo similar commands found.")
    
    error_lines.append("\nType /help for available commands.")
    
    # Return block decision
    return {
        "decision": "block",
        "reason": "\n".join(error_lines)
    }


def main():
    """
    Main entry point for the hook.
    Reads JSON from stdin, validates, writes JSON to stdout.
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Validate the prompt
        result = validate_prompt(input_data)
        
        # If result is None or empty, allow through (no output needed)
        if result:
            # Output the block decision
            print(json.dumps(result))
            
    except Exception as e:
        # On error, allow through (fail open, not closed)
        # Could log the error if logging is set up
        pass


if __name__ == "__main__":
    main()