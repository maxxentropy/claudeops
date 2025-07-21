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
print(f"Source resolved: {source.resolve()}")
print(f"Tool source: {tool.source}")
print(f"File content: {script_file.read_text()}")

# Test string matching
path_in_file = f"{source}/core.sh"
print(f"\nPath in file: {path_in_file}")
print(f"str(tool.source): {str(tool.source)}")
print(f"Source in path: {str(tool.source) in path_in_file}")

# Test is_relevant_path with debug
print(f"\nTesting is_relevant_path with debug:")
print(f'  Input: "{path_in_file}"')
print(f'  Contains source: {str(tool.source) in path_in_file}')
print(f'  Contains ..: {".." in path_in_file}')
print(f'  Contains ./: {"./" in path_in_file}')
print(f'  Result: {tool.is_relevant_path(path_in_file)}')

import shutil
shutil.rmtree(test_dir)