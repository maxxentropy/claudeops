#!/bin/bash
# Validates slash commands before Claude processes them
# This hook runs on every user prompt submission

# Get the user's input from stdin
USER_INPUT="$1"

# Check if input starts with a slash
if [[ "$USER_INPUT" =~ ^/ ]]; then
    # Extract the command name
    COMMAND=$(echo "$USER_INPUT" | cut -d' ' -f1 | sed 's/^///')
    
    # Run Python validation script
    VALIDATION_RESULT=$(python3 ~/.claude/lib/validate_slash_command_hook.py "$USER_INPUT" 2>&1)
    
    # Check if validation failed (exit code non-zero)
    if [ $? -ne 0 ]; then
        # Print error message that will be shown to user
        echo "❌ BLOCKED: $VALIDATION_RESULT"
        exit 1  # Non-zero exit blocks the command
    fi
fi

# If we get here, either it's not a slash command or it's valid
exit 0