# Slash Command Validation Hook

## Purpose
This hook validates slash commands before Claude processes them, preventing the execution of unrecognized commands like `/save` when you meant `/safe`.

## How It Works
1. Intercepts every user prompt before Claude sees it
2. If the prompt starts with `/`, validates it against available commands
3. Blocks invalid commands with helpful suggestions
4. Allows valid commands and non-slash prompts through

## Installation

### Step 1: Verify Files
Ensure these files exist and are executable:
```bash
ls -la ~/.claude/hooks/slash_command_validator.py
ls -la ~/.claude/hooks/test_slash_command_validator.py
```

### Step 2: Add Hook to Settings
Edit or create `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/slash_command_validator.py"
          }
        ]
      }
    ]
  }
}
```

### Step 3: Restart Claude Code
The hook will take effect after restarting Claude Code.

## Testing

After installation, test with these commands:

1. **Invalid command** - Type: `/save`
   - Expected: Blocked with "Did you mean: /safe"

2. **Valid command** - Type: `/safe test`
   - Expected: Executes normally

3. **Unknown command** - Type: `/xyz123`
   - Expected: Blocked with "No similar commands found"

4. **Normal text** - Type: `Hello world`
   - Expected: Works normally (not a slash command)

## How It Prevents Issues

Before this hook:
```
User: /save
Claude: [Makes assumptions and executes unintended actions]
```

After this hook:
```
User: /save
System: ❌ Unrecognized command: /save

Did you mean:
  /safe

Type /help for available commands.
[Message blocked - Claude never sees it]
```

## Technical Details

- **Script**: `slash_command_validator.py`
- **Tests**: `test_slash_command_validator.py` (8 tests, all passing)
- **Hook Type**: UserPromptSubmit
- **Behavior**: Fail-open (if hook errors, allows prompt through)

## Troubleshooting

If the hook isn't working:

1. Check Claude Code logs for hook errors
2. Verify Python 3 is installed: `python3 --version`
3. Test manually: 
   ```bash
   echo '{"prompt": "/save test"}' | python3 ~/.claude/hooks/slash_command_validator.py
   ```
4. Ensure settings.json has correct JSON syntax

## Benefits

1. **Prevents Mistakes**: No more accidental execution of wrong commands
2. **Helpful Suggestions**: Shows similar commands when you mistype
3. **Safety First**: Aligns with repository's core principles
4. **Transparent**: Only blocks invalid slash commands, everything else works normally

This hook ensures Claude follows the core principle: "Do exactly what's asked - nothing more, nothing less."