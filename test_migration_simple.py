#!/usr/bin/env python3
"""
Simple test to verify migration tool works
"""

import tempfile
import shutil
from pathlib import Path

# Create test environment
test_dir = tempfile.mkdtemp()
source = Path(test_dir) / "old_location"
dest = Path(test_dir) / "new_location"

print(f"Test directory: {test_dir}")
print(f"Source: {source}")
print(f"Destination: {dest}")

# Create source structure
source.mkdir()
(source / "core.sh").write_text('echo "This is core.sh"')

# Create a script that references the core.sh
script_content = f'''#!/bin/bash
# This script sources core.sh
source "{source}/core.sh"
echo "Script executed"
'''

script_file = source / "test_script.sh"
script_file.write_text(script_content)

print("\nBefore migration:")
print(f"Script content:\n{script_file.read_text()}")

# Test the migration tool
import sys
import os
sys.path.append('/Users/sean/.claude/scripts')

import importlib.util
spec = importlib.util.spec_from_file_location("migrate_tool", "/Users/sean/.claude/scripts/migrate-tool.py")
migrate_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migrate_tool)

# Run migration
tool = migrate_tool.MigrationTool(
    str(source),
    str(dest),
    {'update_refs': True, 'validate': False, 'test': False, 'backup': False}
)

print("\n" + "="*50)
print("RUNNING MIGRATION")
print("="*50)

tool.run()

print("\nAfter migration:")
if (dest / "test_script.sh").exists():
    print(f"Migrated script content:\n{(dest / 'test_script.sh').read_text()}")
else:
    print("Script not found in destination")

# Clean up
shutil.rmtree(test_dir)
print(f"\nTest completed. Cleaned up {test_dir}")