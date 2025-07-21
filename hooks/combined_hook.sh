#!/bin/bash
# Combined hook that runs all UserPromptSubmit actions

# Echo processing message
echo "Processing request..."

# Read input for Python scripts
input=$(cat)

# Run validator (silent unless blocking)
echo "$input" | python3 ~/.claude/hooks/slash_command_validator.py

# Run command visibility (shows header for slash commands)
echo "$input" | python3 ~/.claude/hooks/command_visibility_hook.py