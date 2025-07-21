#!/usr/bin/env python3
"""
Command visibility hook v3 - Shows context then allows execution
Uses a clever workaround to display information to users.
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import List, Optional

def find_command_file(command_name: str) -> Optional[Path]:
    """Find the .md file for a given command."""
    commands_dir = Path(os.path.expanduser("~/.claude/commands"))
    
    if not commands_dir.exists():
        return None
    
    # Handle path-based format (e.g., "core:commit")
    if ':' in command_name:
        parts = command_name.split(':')
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
    """Extract persona references from command content."""
    personas = []
    pattern = r'<!-- INCLUDE:\s*system/personas\.md#(\w+)\s*-->'
    
    persona_map = {
        'SENIOR_TEST_ENGINEER': 'Test Engineer',
        'SOFTWARE_ARCHITECT': 'Architect',
        'SECURITY_ENGINEER': 'Security',
        'DEVOPS_ENGINEER': 'DevOps',
        'CODE_REVIEWER': 'Reviewer',
        'SRE_ENGINEER': 'SRE',
        'PRODUCT_ENGINEER': 'Product',
        'PERFORMANCE_ENGINEER': 'Performance'
    }
    
    for match in re.finditer(pattern, content):
        persona_id = match.group(1)
        readable_name = persona_map.get(persona_id, persona_id.replace('_', ' ').title())
        personas.append(readable_name)
    
    return personas

def extract_workflow_description(command_name: str, content: str) -> str:
    """Extract workflow description."""
    title_match = re.search(r'^#\s*/\w+\s*-\s*(.+)$', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    
    workflow_map = {
        'safe': 'Safe General Workflow',
        'commit': 'Safe Git Commit',
        'fix': 'Systematic Debugging',
        'test': 'Generate Tests (80% Coverage)',
        'config': 'Safe Configuration'
    }
    
    return workflow_map.get(command_name, f'{command_name.title()} Workflow')

def main():
    """
    Main hook entry point.
    Strategy: Use JSON output to display context information.
    """
    try:
        input_data = json.load(sys.stdin)
        prompt = input_data.get('prompt', '').strip()
        
        if not prompt.startswith('/'):
            sys.exit(0)
        
        parts = prompt.split()
        if not parts or len(parts[0]) <= 1:
            sys.exit(0)
        
        command_name = parts[0][1:].lower()
        command_file = find_command_file(command_name)
        
        if not command_file:
            sys.exit(0)
        
        try:
            content = command_file.read_text(encoding='utf-8')
            personas = extract_personas(content)
            workflow = extract_workflow_description(command_name, content)
            
            persona_str = ' + '.join(personas) if personas else 'Standard'
            
            # Create context message
            context_msg = f"""
=====================================
🎯 COMMAND: /{command_name}
📋 WORKFLOW: {workflow}
👤 PERSONAS: {persona_str}
=====================================
"""
            
            # Use JSON output to add context to the conversation
            # This approach adds the context as a system message
            output = {
                "continue": True,  # Allow execution to continue
                "additionalContext": context_msg
            }
            
            print(json.dumps(output))
            sys.exit(0)
            
        except Exception:
            sys.exit(0)
            
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()