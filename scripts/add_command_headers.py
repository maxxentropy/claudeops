#!/usr/bin/env python3
"""
Add visible headers to all slash command files.
A world-class solution that makes command context visible directly in the output.
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional

# Persona mapping for readable names
PERSONA_MAP = {
    'SENIOR_TEST_ENGINEER': 'Test Engineer',
    'SOFTWARE_ARCHITECT': 'Software Architect',
    'SECURITY_ENGINEER': 'Security Engineer',
    'DEVOPS_ENGINEER': 'DevOps Engineer',
    'CODE_REVIEWER': 'Code Reviewer',
    'SRE_ENGINEER': 'SRE Engineer',
    'PRODUCT_ENGINEER': 'Product Engineer',
    'PERFORMANCE_ENGINEER': 'Performance Engineer'
}

def extract_command_info(file_path: Path) -> Tuple[str, str, List[str]]:
    """
    Extract command name, workflow description, and personas from a command file.
    
    Returns:
        Tuple of (command_name, workflow_description, personas)
    """
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Extract command name from filename
    command_name = file_path.stem
    
    # Extract workflow description from title
    workflow_desc = "Workflow"
    title_match = re.match(r'^#\s*/\w+\s*-\s*(.+)$', lines[0] if lines else '')
    if title_match:
        workflow_desc = title_match.group(1).strip()
    
    # Extract personas from INCLUDE directives
    personas = []
    persona_pattern = r'<!-- INCLUDE:\s*system/personas\.md#(\w+)\s*-->'
    
    for line in lines[:20]:  # Check first 20 lines for personas
        match = re.search(persona_pattern, line)
        if match:
            persona_id = match.group(1)
            readable_name = PERSONA_MAP.get(persona_id, persona_id.replace('_', ' ').title())
            personas.append(readable_name)
    
    return command_name, workflow_desc, personas

def create_header(command_name: str, workflow_desc: str, personas: List[str]) -> str:
    """
    Create the visible header line for a command.
    """
    persona_str = ' + '.join(personas) if personas else 'Default'
    return f"🎯 **COMMAND**: /{command_name} | 📋 **WORKFLOW**: {workflow_desc} | 👤 **PERSONAS**: {persona_str}"

def has_visible_header(content: str) -> bool:
    """
    Check if a command file already has a visible header.
    """
    return '🎯 **COMMAND**:' in content

def update_command_file(file_path: Path, dry_run: bool = False) -> Optional[str]:
    """
    Update a single command file with a visible header.
    
    Returns:
        The action taken, or None if no action needed
    """
    content = file_path.read_text(encoding='utf-8')
    
    # Skip if already has a visible header
    if has_visible_header(content):
        return None
    
    lines = content.split('\n')
    if not lines:
        return None
    
    # Extract info
    command_name, workflow_desc, personas = extract_command_info(file_path)
    
    # Create header
    header = create_header(command_name, workflow_desc, personas)
    
    # Insert header after title (line 0) and empty line (line 1)
    if len(lines) > 1:
        lines.insert(2, header)
        lines.insert(3, '')  # Add blank line after header
    
    new_content = '\n'.join(lines)
    
    if not dry_run:
        file_path.write_text(new_content, encoding='utf-8')
    
    return f"Added header to {file_path.name}: {len(personas)} personas"

def main():
    """
    Update all command files with visible headers.
    """
    commands_dir = Path.home() / '.claude' / 'commands'
    if not commands_dir.exists():
        print(f"Commands directory not found: {commands_dir}")
        return
    
    # Find all .md files
    command_files = list(commands_dir.rglob('*.md'))
    
    # Skip non-command files
    skip_files = {'README.md', 'template.md', 'newcmd.md'}
    command_files = [f for f in command_files if f.name not in skip_files]
    
    print(f"Found {len(command_files)} command files")
    print("=" * 60)
    
    updated = 0
    skipped = 0
    
    for file_path in sorted(command_files):
        relative_path = file_path.relative_to(commands_dir)
        action = update_command_file(file_path, dry_run=False)
        
        if action:
            print(f"✅ {relative_path}: {action}")
            updated += 1
        else:
            print(f"⏭️  {relative_path}: Already has header")
            skipped += 1
    
    print("=" * 60)
    print(f"Summary: {updated} updated, {skipped} skipped")
    
    # Create a backup of the hook files since we're not using them
    hooks_dir = Path.home() / '.claude' / 'hooks'
    if hooks_dir.exists():
        print("\n📦 Moving unused hook files to backup...")
        backup_dir = hooks_dir / 'backup'
        backup_dir.mkdir(exist_ok=True)
        
        hook_files = [
            'command_visibility_hook.py',
            'command_visibility_hook_v2.py',
            'command_visibility_hook_v3.py',
            'command_visibility_hook_blocking.py',
            'command_visibility_pretool.py',
            'test_minimal_hook.py'
        ]
        
        for hook_file in hook_files:
            hook_path = hooks_dir / hook_file
            if hook_path.exists():
                backup_path = backup_dir / hook_file
                hook_path.rename(backup_path)
                print(f"  Moved {hook_file} to backup/")

if __name__ == "__main__":
    main()