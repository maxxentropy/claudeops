#!/usr/bin/env python3
"""
Command visibility hook for Claude Code.
Shows workflow name and active personas when slash commands are invoked.
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
        'safe': 'Safe General Workflow with Full Verification',
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


def process_prompt(input_data: Dict, commands_dir: Path = None) -> Optional[Dict]:
    """
    Process a user prompt to add command visibility.
    
    Args:
        input_data: Hook input containing 'prompt' and other fields
        commands_dir: Optional commands directory for testing
        
    Returns:
        Modified input with prepended visibility info, or None if no changes
    """
    prompt = input_data.get('prompt', '').strip()
    
    # Only process if it starts with a slash
    if not prompt.startswith('/'):
        return None
    
    # Extract command name
    parts = prompt.split()
    if not parts or len(parts[0]) <= 1:
        return None
    
    command_name = parts[0][1:].lower()
    
    # Find command file
    command_file = find_command_file(command_name, commands_dir)
    if not command_file:
        # Command doesn't exist, let the validator hook handle it
        return None
    
    try:
        # Read command content
        content = command_file.read_text(encoding='utf-8')
        
        # Extract information
        personas = extract_personas(content)
        workflow = extract_workflow_description(command_name, content)
        
        # Create header
        header = format_command_header(command_name, workflow, personas)
        
        # Prepend header to the original prompt
        # This way Claude sees both the header and the command
        modified_prompt = header + "\n" + prompt
        
        # Return modified input
        result = input_data.copy()
        result['prompt'] = modified_prompt
        return result
        
    except Exception:
        # On any error, allow original prompt through
        return None


def main():
    """
    Main entry point for the hook.
    Reads JSON from stdin, prints visibility header to stdout.
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        prompt = input_data.get('prompt', '').strip()
        
        # Only process if it starts with a slash
        if not prompt.startswith('/'):
            return
        
        # Extract command name
        parts = prompt.split()
        if not parts or len(parts[0]) <= 1:
            return
        
        command_name = parts[0][1:].lower()
        
        # Find command file
        command_file = find_command_file(command_name)
        if not command_file:
            return
        
        try:
            # Read command content
            content = command_file.read_text(encoding='utf-8')
            
            # Extract information
            personas = extract_personas(content)
            workflow = extract_workflow_description(command_name, content)
            
            # Create and print header directly to stdout
            # This will appear as hook output in Claude Code
            header = format_command_header(command_name, workflow, personas)
            print(header.strip())
            
        except Exception:
            # On any error, stay silent
            pass
            
    except Exception:
        # On error, allow through (fail open)
        pass


if __name__ == "__main__":
    main()