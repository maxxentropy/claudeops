#!/usr/bin/env python3
"""Minimal test hook to verify output behavior"""
import json
import sys

# Read input
input_data = json.load(sys.stdin)
prompt = input_data.get('prompt', '')

# Only process slash commands
if prompt.startswith('/'):
    print("TEST: This message is on stderr", file=sys.stderr)
    sys.exit(1)  # Non-zero exit should show stderr to user

# Exit normally for non-slash commands
sys.exit(0)