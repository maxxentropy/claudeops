#!/usr/bin/env python3
"""
Update all PRD workflow commands to use consistent path resolution.
This script removes hardcoded paths and ensures all commands use the path resolver.
"""

import os
import re
from pathlib import Path

# PRD workflow commands to update
PRD_COMMANDS = [
    'prd-preview.md',
    'prd-integrate.md',
    'prd-rollback.md',
    'prd-decompose.md',
    'prd-kickstart.md',
    'prd-parallel.md',
    'prd-progress.md',
    'prd-integrate-v2.md',
    'prd-integrate-enhanced.md',
    'prd-analyze.md'
]

COMMANDS_DIR = Path(os.path.expanduser('~/.claude/commands/workflow'))

def update_command_file(filepath):
    """Update a single command file to use consistent paths."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace common path patterns
    replacements = [
        # Remove ${REPO_ROOT} prefix
        (r'\$\{REPO_ROOT\}/\.claude/prd-workspace/', '.claude/prd-workspace/'),
        (r'\$\{REPO_ROOT\}/docs/prds/', 'docs/prds/'),
        (r'\$\{REPO_ROOT\}/', ''),
        
        # Update backtick paths
        (r'`\.claude/prd-workspace/([^`]+)`', r'`.claude/prd-workspace/\1` (repository-relative)'),
        (r'`docs/prds/([^`]+)`', r'`docs/prds/\1` (repository-relative)'),
        
        # Update specific patterns
        (r'Save to: docs/prds/', 'Save to: docs/prds/ (automatically resolves to repository root)'),
        (r'Create workspace: \.claude/prd-workspace/', 'Create workspace: .claude/prd-workspace/ (automatically resolves to repository root)'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Add path resolution note if not present
    if '## Path Resolution:' not in content and content != original_content:
        # Find a good place to add it (before the last section or at the end)
        sections = re.split(r'\n## ', content)
        if len(sections) > 1:
            # Insert before the last section
            sections[-1] = """Path Resolution:
- This command automatically uses repository-relative paths
- All paths resolve to the repository root when in a git repository
- Falls back to current directory when not in a repository
- Set `CLAUDE_OUTPUT_ROOT` environment variable to override

## """ + sections[-1]
            content = '\n## '.join(sections)
        else:
            # Add at the end
            content += """

## Path Resolution:
- This command automatically uses repository-relative paths
- All paths resolve to the repository root when in a git repository
- Falls back to current directory when not in a repository
- Set `CLAUDE_OUTPUT_ROOT` environment variable to override
"""
    
    # Only write if changed
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False


def main():
    """Update all PRD workflow commands."""
    updated_files = []
    
    for command_file in PRD_COMMANDS:
        filepath = COMMANDS_DIR / command_file
        if filepath.exists():
            if update_command_file(filepath):
                updated_files.append(command_file)
                print(f"✓ Updated: {command_file}")
            else:
                print(f"  No changes needed: {command_file}")
        else:
            print(f"  Not found: {command_file}")
    
    print(f"\nUpdated {len(updated_files)} files")
    if updated_files:
        print("\nFiles updated:")
        for f in updated_files:
            print(f"  - {f}")


if __name__ == "__main__":
    main()