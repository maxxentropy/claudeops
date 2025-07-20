# Claude Code Critical Context - Sean's Configuration

## FUNDAMENTAL RULES (These Override Everything)

### 1. NEVER TAKE SHORTCUTS
If tempted to skip tests, skip verification, or say "this should work" - STOP.
Do it right or not at all. No assumptions, no partial implementations.

### 2. EXACT EXECUTION
Do exactly what's asked; nothing more, nothing less.
NEVER create files unless absolutely necessary.

### 3. SLASH COMMANDS ARE MANDATORY
When user's request matches a slash command purpose, USE THE COMMAND.
Type `/commands` to see all available workflows.

## Critical Standards (For Quick Reference)

**Languages**: C# (4 spaces), JS/TS (2 spaces)
**Security**: NEVER commit secrets. Use env vars.
**Testing**: 80% coverage minimum, xUnit/Jest
**Commits**: `<type>: <component> <what-and-why> [VERIFIED]`

## API Version Tracking (Update When Checked)

```yaml
claude_code_cli: v1.0.56 (2025-01-20)
claude_api: claude-3-opus-20240229 (2025-01-20)
hooks_api: v2 array format (2025-01-20)
```

## Available Slash Commands

**Core**: `/safe`, `/commit`, `/fix`, `/config`
**Specialized**: `/test`, `/build`, `/pattern`
**Planning**: `/prdq`, `/prd`

All detailed workflows are in slash commands.
All reusable principles are in principles.md.

## Why This Structure?

1. You respond to immediate input (slash commands)
2. Tagged principles prevent duplication
3. Memory only contains what can't be in commands
4. Workflows are enforced, not remembered

REMEMBER: If there's a slash command for it, use the command.