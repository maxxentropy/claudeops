#!/usr/bin/env python3
"""
Command visibility hook for Claude Code V2.
Shows workflow name and active personas when slash commands are invoked.
This version properly outputs JSON to modify the prompt.
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple


def find_command_file(command_name: str, commands_dir: Path = None) -> Optional[Path]:
    """
    Find the .md file for a given command.
    
    Args:
        command_name: Name of the command (without slash)
        commands_dir: Optional commands directory
        
    Returns:
        Path to the command file if found, None otherwise
    """
    if commands_dir is None:
        env_dir = os.environ.get('CLAUDE_COMMANDS_DIR')
        if env_dir:
            commands_dir = Path(env_dir)
        else:
            commands_dir = Path(os.path.expanduser("~/.claude/commands"))
    
    if not commands_dir.exists():
        return None
    
    # Handle path-based format (e.g., "core:commit")
    if ':' in command_name:
        # Split into path parts
        parts = command_name.split(':')
        # Construct the path
        command_path = commands_dir
        for part in parts[:-1]:
            command_path = command_path / part
        command_path = command_path / f"{parts[-1]}.md"
        
        if command_path.exists():
            return command_path
    
    # Search for the command file by name only
    for md_file in commands_dir.rglob("*.md"):
        if md_file.stem == command_name:
            return md_file
    
    return None


def extract_personas(content: str) -> List[str]:
    """
    Extract persona references from command content.
    
    Args:
        content: The command file content
        
    Returns:
        List of persona names found
    """
    personas = []
    
    # Pattern to match persona includes
    # Matches: <!-- INCLUDE: system/personas.md#PERSONA_NAME -->
    pattern = r'<!-- INCLUDE:\s*system/personas\.md#(\w+)\s*-->'
    
    for match in re.finditer(pattern, content):
        persona_id = match.group(1)
        
        # Convert ID to readable name
        persona_map = {
            'SENIOR_TEST_ENGINEER': 'Senior Test Engineer (Bug Hunter)',
            'SOFTWARE_ARCHITECT': 'Software Architect (Systems Thinker)',
            'SECURITY_ENGINEER': 'Security Engineer (Paranoid Guardian)',
            'DEVOPS_ENGINEER': 'DevOps Engineer (Automation Advocate)',
            'CODE_REVIEWER': 'Code Reviewer (Quality Guardian)',
            'SRE_ENGINEER': 'SRE Engineer (Incident Commander)',
            'PRODUCT_ENGINEER': 'Product Engineer (User Advocate)',
            'PERFORMANCE_ENGINEER': 'Performance Engineer (Speed Optimizer)'
        }
        
        readable_name = persona_map.get(persona_id, persona_id.replace('_', ' ').title())
        personas.append(readable_name)
    
    return personas


def extract_workflow_description(command_name: str, content: str) -> str:
    """
    Extract or generate workflow description from command content.
    
    Args:
        command_name: Name of the command
        content: The command file content
        
    Returns:
        Workflow description
    """
    # Try to extract from the title line
    title_match = re.search(r'^#\s*/\w+\s*-\s*(.+)$', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    
    # Fallback descriptions for known commands
    workflow_map = {
        'safe': 'Safe General Workflow',
        'commit': 'Safe Git Commit with Pre-commit Verification',
        'fix': 'Systematic Debugging with Root Cause Analysis',
        'test': 'Generate Comprehensive Test Suite (80% Coverage Target)',
        'build': 'Platform-specific Build Verification',
        'config': 'Safe Configuration Changes with API Checks',
        'prd': 'Comprehensive Product Requirements Document Creation',
        'prdq': 'Quick PRD for Immediate Implementation',
        'refactor-safe': 'Incremental Refactoring with Verification',
        'review-pr': 'Systematic Pull Request Review',
        'tdd': 'Test-Driven Development Workflow',
        'pattern': 'Implement Standard Code Patterns',
        'git-investigate': 'Analyze Code History and Evolution'
    }
    
    return workflow_map.get(command_name, f'{command_name.title()} Workflow')


def format_command_header(command_name: str, workflow: str, personas: List[str]) -> str:
    """
    Format the command visibility header.
    
    Args:
        command_name: Name of the command
        workflow: Workflow description
        personas: List of active personas
        
    Returns:
        Formatted header string
    """
    persona_str = ' + '.join(personas) if personas else 'None Specified'
    
    return f"""
=====================================
🎯 COMMAND: /{command_name}
📋 WORKFLOW: {workflow}
👤 PERSONAS: {persona_str}
=====================================

Starting command execution...
"""


def main():
    """
    Main entry point for the hook.
    Reads JSON from stdin, processes it, and outputs modified JSON.
    
    For UserPromptSubmit hooks:
    - Exit code 0 with JSON output modifies the prompt
    - Exit code 2 blocks with error message
    - Other exit codes show stderr to user
    """
    # Debug logging to verify hook execution
    debug_log = os.environ.get('CLAUDE_HOOK_DEBUG', '/tmp/command_visibility_hook.log')
    if debug_log:
        with open(debug_log, 'a') as f:
            f.write(f"Hook V2 executed at {__import__('datetime').datetime.now()}\n")
    
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        prompt = input_data.get('prompt', '').strip()
        
        # Only process if it starts with a slash
        if not prompt.startswith('/'):
            # Not a slash command, pass through unchanged
            sys.exit(0)
        
        # Extract command name
        parts = prompt.split()
        if not parts or len(parts[0]) <= 1:
            sys.exit(0)
        
        command_name = parts[0][1:].lower()
        
        # Debug logging
        if debug_log:
            with open(debug_log, 'a') as f:
                f.write(f"Processing command: /{command_name}\n")
        
        # Find command file
        command_file = find_command_file(command_name)
        if not command_file:
            # Command doesn't exist, let validator handle it
            sys.exit(0)
        
        # Read command content
        content = command_file.read_text(encoding='utf-8')
        
        # Extract information
        personas = extract_personas(content)
        workflow = extract_workflow_description(command_name, content)
        
        # Create header
        header = format_command_header(command_name, workflow, personas)
        
        # Option 1: Show header to user via stderr (non-blocking)
        print(header.strip(), file=sys.stderr)
        sys.stderr.flush()
        
        # Option 2: Also prepend to the prompt so Claude sees it
        # This ensures the context is visible even if stderr isn't shown
        modified_prompt = header + "\n" + prompt
        
        # Output modified input data
        output_data = input_data.copy()
        output_data['prompt'] = modified_prompt
        
        # Write JSON to stdout
        print(json.dumps(output_data))
        
        # Exit with code 0 to indicate successful processing
        sys.exit(0)
        
    except Exception as e:
        # On any error, log and exit quietly to not interfere
        if debug_log:
            with open(debug_log, 'a') as f:
                f.write(f"Error in hook: {e}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()