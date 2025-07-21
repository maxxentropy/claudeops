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

# Create file with reference
script_content = f'source "{source}/core.sh"'
script_file = source / "test.sh"
script_file.write_text(script_content)

# Create core.sh
(source / "core.sh").write_text("echo core")

tool = migrate_tool.MigrationTool(str(source), str(dest), {})

print(f"Source: {source}")
print(f"Files to scan:")
for f in tool.get_files_to_scan():
    print(f"  {f}")

print(f"\nFile content: {script_file.read_text()}")
print(f"Source path to look for: {source}")

# Test is_relevant_path
print(f"\nTesting is_relevant_path:")
print(f'  "{source}/core.sh" -> {tool.is_relevant_path(str(source) + "/core.sh")}')

import shutil
shutil.rmtree(test_dir)