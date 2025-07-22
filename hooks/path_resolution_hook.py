#!/usr/bin/env python3
"""
Path resolution hook for slash commands.
Intercepts path references in commands and resolves them to repository-relative paths.
"""

import sys
import json
import re
import os
from pathlib import Path

# Add system utils to path
sys.path.insert(0, os.path.expanduser('~/.claude'))

try:
    from system.utils import path_resolver, repo_detector
except ImportError:
    # Fallback if imports fail
    print(json.dumps({"exit_code": 0}))
    sys.exit(0)


def resolve_path_variables(content):
    """Replace path variables with resolved paths."""
    # Get repository root
    repo_root = repo_detector.find_repo_root()
    
    if repo_root:
        # Replace ${REPO_ROOT} with actual path
        content = content.replace('${REPO_ROOT}', str(repo_root))
        
        # Common path patterns to resolve
        path_patterns = [
            (r'docs/prds/', 'prds'),
            (r'\.claude/prd-workspace/', 'prd_workspace'),
            (r'\.claude/', None),  # Direct .claude reference
        ]
        
        for pattern, path_type in path_patterns:
            if path_type:
                # Use path resolver for known types
                resolved = path_resolver.resolve(path_type)
                content = re.sub(pattern, str(resolved) + '/', content)
    
    return content


def main():
    """Main hook entry point."""
    try:
        # Read the hook payload
        payload = json.loads(sys.stdin.read())
        user_prompt = payload.get("user_prompt", "")
        
        # Check if this is a slash command
        if not user_prompt.startswith('/'):
            print(json.dumps({"exit_code": 0}))
            return
        
        # Extract command and arguments
        parts = user_prompt.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        # Commands that need path resolution
        path_commands = [
            '/prd', '/prdq', '/prd-implement', '/prd-preview', 
            '/prd-integrate', '/prd-rollback', '/prd-decompose',
            '/prd-kickstart', '/prd-parallel', '/prd-progress'
        ]
        
        # Check if this command needs path resolution
        if command in path_commands:
            # Add path context to the prompt
            repo_root = repo_detector.find_repo_root()
            if repo_root:
                # Inject path context
                context = f"\n\n[Path Context: Repository root is {repo_root}]"
                new_prompt = user_prompt + context
                
                # Return modified prompt
                print(json.dumps({
                    "exit_code": 0,
                    "user_prompt": new_prompt
                }))
                return
        
        # No modification needed
        print(json.dumps({"exit_code": 0}))
        
    except Exception as e:
        # Log error but don't block
        print(json.dumps({
            "exit_code": 0,
            "error": str(e)
        }), file=sys.stderr)
        print(json.dumps({"exit_code": 0}))


if __name__ == "__main__":
    main()