#!/usr/bin/env python3
"""
Command visibility hook v2 - More prominent output
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

def main():
    """Main entry point for the hook."""
    try:
        input_data = json.load(sys.stdin)
        prompt = input_data.get('prompt', '').strip()
        
        if not prompt.startswith('/'):
            return
        
        parts = prompt.split()
        if not parts or len(parts[0]) <= 1:
            return
        
        command_name = parts[0][1:].lower()
        command_file = find_command_file(command_name)
        
        if not command_file:
            return
        
        try:
            content = command_file.read_text(encoding='utf-8')
            personas = extract_personas(content)
            
            # More compact output format
            persona_str = ' + '.join(personas) if personas else 'Standard'
            
            # Print to stderr for more visibility?
            output = f"\n▶ /{command_name} | Personas: {persona_str}\n"
            print(output, file=sys.stderr)
            
        except Exception:
            pass
            
    except Exception:
        pass

if __name__ == "__main__":
    main()