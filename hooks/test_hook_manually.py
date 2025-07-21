#!/usr/bin/env python3
import json
import sys

# Test the hook manually
test_input = {
    "prompt": "/safe testing the hook"
}

# Run the hook
import subprocess
result = subprocess.run(
    ["python3", "/Users/sean/.claude/hooks/command_visibility_hook.py"],
    input=json.dumps(test_input),
    capture_output=True,
    text=True
)

print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")