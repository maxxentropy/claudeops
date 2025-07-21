#!/usr/bin/env python3
"""
Slash command validation to prevent execution of unrecognized commands.
This is a critical safety component of the Claude Code system.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
import re


def find_available_commands(commands_dir: Path = None) -> List[str]:
    """
    Find all available slash commands by scanning the commands directory.
    
    Returns:
        List of available command names (without the slash)
    """
    if commands_dir is None:
        commands_dir = Path(os.path.expanduser("~/.claude/commands"))
    
    commands = []
    
    for md_file in commands_dir.rglob("*.md"):
        # Skip template files and non-command files
        if md_file.name in ['newcmd.md', 'README.md', 'template.md']:
            continue
            
        # Extract command name from filename
        command_name = md_file.stem
        
        # Also check if it's a valid command by looking for slash in content
        try:
            content = md_file.read_text()
            if f"/{command_name}" in content or "slash command" in content.lower():
                commands.append(command_name)
        except:
            pass
    
    return sorted(list(set(commands)))


def find_similar_commands(typed_command: str, available_commands: List[str], threshold: float = 0.6) -> List[Tuple[str, float]]:
    """
    Find commands similar to what was typed using string similarity.
    
    Args:
        typed_command: The command user typed (without slash)
        available_commands: List of valid commands
        threshold: Minimum similarity score (0-1)
        
    Returns:
        List of (command, similarity_score) tuples, sorted by score
    """
    from difflib import SequenceMatcher
    
    similar = []
    
    for cmd in available_commands:
        # Calculate similarity
        similarity = SequenceMatcher(None, typed_command.lower(), cmd.lower()).ratio()
        
        # Also check if typed command is substring or vice versa
        if typed_command.lower() in cmd.lower() or cmd.lower() in typed_command.lower():
            similarity = max(similarity, 0.7)
        
        if similarity >= threshold:
            similar.append((cmd, similarity))
    
    # Sort by similarity score (highest first)
    return sorted(similar, key=lambda x: x[1], reverse=True)[:5]


def validate_slash_command(user_input: str) -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate if a slash command exists and find suggestions if not.
    
    Args:
        user_input: The full user input (e.g., "/save")
        
    Returns:
        Tuple of (is_valid, command_name, suggestions)
    """
    # Extract command from input
    if not user_input.startswith('/'):
        return False, None, []
    
    # Remove slash and any arguments
    command_parts = user_input[1:].split()
    if not command_parts:
        return False, None, []
    
    command_name = command_parts[0].lower()
    
    # Get available commands
    available = find_available_commands()
    
    # Check if exact match
    if command_name in available:
        return True, command_name, []
    
    # Find similar commands
    similar = find_similar_commands(command_name, available)
    suggestions = [cmd for cmd, score in similar]
    
    return False, None, suggestions


def format_command_error(typed_command: str, suggestions: List[str]) -> str:
    """
    Format an error message for unrecognized commands.
    
    Args:
        typed_command: What the user typed
        suggestions: List of similar valid commands
        
    Returns:
        Formatted error message
    """
    lines = [f"❌ Unrecognized command: {typed_command}", ""]
    
    if suggestions:
        lines.append("Did you mean one of these?")
        for cmd in suggestions:
            lines.append(f"- /{cmd}")
    else:
        lines.append("This command does not exist.")
    
    lines.extend(["", "Type /help for available commands."])
    
    return "\n".join(lines)


# Example usage and testing
if __name__ == "__main__":
    # Test the validation
    test_cases = ["/save", "/safe", "/quickfix", "/xyz123", "/build", "/prdq"]
    
    print("Slash Command Validation Tests")
    print("=" * 50)
    
    for test in test_cases:
        valid, cmd, suggestions = validate_slash_command(test)
        
        print(f"\nInput: {test}")
        if valid:
            print(f"✅ Valid command: {cmd}")
        else:
            print(format_command_error(test, suggestions))
    
    print("\n" + "=" * 50)
    print("\nAvailable commands:")
    for cmd in find_available_commands()[:10]:  # Show first 10
        print(f"  /{cmd}")
    print("  ... and more")