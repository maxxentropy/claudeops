# /test-hooks - Verify Hook Configuration

Verify that your Claude Code hooks are properly configured and firing.

## Testing Process

1. **Test UserPromptSubmit Hook**
   - This hook should have already fired when you ran this command
   - Look for "Processing request..." output above

2. **Test PreToolUse Hook (Bash)**
   - Run a simple bash command and verify the pre-hook fires
   - Should see "Executing bash command..." before the command runs

3. **Test PostToolUse Hook (Edit/Write)**
   - Create or edit a file to trigger the post-hook
   - Should run dotnet format (or fail gracefully if not in a .NET project)

4. **Verify Slash Command Validation**
   - The slash command validator should have validated this command
   - Invalid commands like `/invalid-command` should be blocked

## Running the Tests

Execute each test step:

```bash
# Step 1: UserPromptSubmit already fired when you ran /test-hooks

# Step 2: Test PreToolUse hook for Bash
echo "Testing PreToolUse hook - you should see 'Executing bash command...' above this"

# Step 3: Test PostToolUse hook for file operations
# Create a temporary test file
echo "Test content for hook verification" > /tmp/hook-test-file.txt

# Step 4: Try an invalid command (should be blocked)
# Run: /this-is-not-a-valid-command
```

## Expected Output

✅ **UserPromptSubmit**: "Processing request..." shown when command started
✅ **PreToolUse (Bash)**: "Executing bash command..." before bash runs  
✅ **PostToolUse (Edit)**: dotnet format attempt after file write
✅ **Slash Validator**: This command validated successfully

## Hook Configuration Location

Your hooks are configured in: `~/.claude/settings.json`

Current hooks:
- **PreToolUse**: Bash commands show execution message
- **PostToolUse**: File edits trigger dotnet format
- **UserPromptSubmit**: Shows processing message + validates slash commands

## Troubleshooting

If hooks aren't firing:
1. Ensure settings.json is at `~/.claude/settings.json` (not in config/)
2. Check that hook commands have proper permissions
3. Verify Python is available for validator hooks
4. Try restarting Claude Code to reload settings