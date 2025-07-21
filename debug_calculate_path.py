#!/usr/bin/env python3
import tempfile
from pathlib import Path
import sys
import importlib.util

# Load migration tool
spec = importlib.util.spec_from_file_location("migrate_tool", "/Users/sean/.claude/scripts/migrate-tool.py")
migrate_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migrate_tool)

# Create test
test_dir = tempfile.mkdtemp()
source = Path(test_dir) / "old_location"
dest = Path(test_dir) / "new_location"
source.mkdir()

tool = migrate_tool.MigrationTool(str(source), str(dest), {})

# Test calculate_new_path
old_path = f"{source}/core.sh"
from_file = dest / "test.sh"  # The file that contains the reference

print(f"Source: {source}")
print(f"Source resolved: {source.resolve()}")
print(f"Tool source: {tool.source}")
print(f"Destination: {dest}")
print(f"Tool destination: {tool.destination}")
print(f"Old path: {old_path}")
print(f"From file: {from_file}")

new_path = tool.calculate_new_path(old_path, from_file)
print(f"New path: {new_path}")

# Debug the logic in calculate_new_path
print(f"\nDebug calculate_new_path logic:")
print(f"str(tool.source): {str(tool.source)}")
print(f"str(tool.source) in old_path: {str(tool.source) in old_path}")

if str(tool.source) in old_path:
    expected = old_path.replace(str(tool.source), str(tool.destination))
    print(f"Expected replacement: {expected}")
else:
    print("Source not found in old_path - checking why...")
    # Check character by character
    source_str = str(tool.source)
    print(f"Source string length: {len(source_str)}")
    print(f"Old path length: {len(old_path)}")
    print(f"Source chars: {list(source_str)}")
    print(f"Old path chars: {list(old_path)}")

import shutil
shutil.rmtree(test_dir)