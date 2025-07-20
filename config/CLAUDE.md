# Claude Code System Configuration - Sean's Global Defaults

# CRITICAL COMPLETION CRITERIA
**NEVER claim a task is done unless ALL are verified:**

1. **NEVER TAKE SHORTCUTS**: Every step must be executed fully. If tempted to skip tests, skip verification, use a hacky solution, or say "this should work" without proving it - STOP. Do it right or not at all. No assumptions, no partial implementations, no "we can fix it later"
2. **Full Request Satisfaction**: Every requirement implemented completely
3. **Zero Compilation Errors**: Build command succeeds without errors
4. **Zero Warnings**: No linter/compiler warnings
5. **Meaningful Test Coverage**: Tests verify happy path, edge cases, and error handling. Critical paths must be tested.
6. **CHECKPOINT COMMIT RULE**: The moment ALL above criteria pass, commit immediately. No additional changes before this commit. This is your safety net. Follow standard format: `<type>: <component> <what-and-why> [VERIFIED: build clean, 0 warnings, X% coverage]`

## Verification Process (MANDATORY)
1. Run build: `dotnet build` / `npm run build`
2. Run tests: `dotnet test` / `npm test`
3. Run coverage analysis
4. Run linting: `dotnet format` / `npm run lint`
5. Manually verify each requirement
6. **COMMIT IMMEDIATELY**: Once all checks pass, commit before ANY other changes. This checkpoint is sacred.

# Core Principles
- Do exactly what's asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- Think before coding on complex problems
- Test everything - no exceptions
- Document complex logic only
- **Smart git investigation**: For bugs, check last 3 commits (30s). For refactors, check full history (2min). Skip for new features.
- **Write searchable commit messages**: Include context, reasons, and keywords for future investigation

## Development Standards

### Code Style
- **C# (.NET)**: 4 spaces, Microsoft naming conventions
- **TypeScript/JavaScript**: 2 spaces
- **All languages**: SOLID principles, async/await for I/O

### Testing
- **Framework**: xUnit (.NET) as primary
- **Coverage**: 80% minimum
- **Pattern**: AAA (Arrange, Act, Assert)
- **Naming**: `MethodName_Scenario_ExpectedOutcome`

### Git & Security
- **Searchable commits**: `<type>: <component> <what-and-why>`
  - Types: feat:, fix:, refactor:, docs:, test:, perf:, chore:
  - Include: Problem, solution, consequences, references
  - Examples:
    - `fix: UserService auth failing for OAuth - added retry logic`
    - `refactor: OrderService extract payment logic - reduces coupling [VERIFIED: build clean, 0 warnings, 92% coverage]`
    - `feat: Add email notifications - implements issue #123 [VERIFIED: build clean, 0 warnings, 85% coverage]`
- Run tests before committing
- NEVER commit secrets/keys - use environment variables
- Always validate input, use HTTPS in production

### Performance
- Profile before optimizing
- Use async/await properly
- Implement strategic caching
- Paginate large datasets

## Common Commands
```bash
# .NET
dotnet build && dotnet test && dotnet format

# Node.js  
npm install && npm test && npm run lint
```

## Quick Commands
- "Review this code for best practices"
- "Generate unit tests with 80% coverage"
- "Fix all warnings and errors"

## Slash Commands (Enforced Workflows)
Use these to ensure workflows are followed automatically:
- `/commit` - Full verification before committing
- `/fix` - Systematic debugging with verification
- `/config` - API version check before config changes
- `/safe` - Any task with full safety protocols

Example: Instead of "commit changes", just use `/commit`

## API Version Tracking and Verification

### CRITICAL: Always Check API Version Before Configuration Changes
**Before modifying any Claude Code settings, hooks, or API-related configuration:**

1. **Check Current API Version**: Always verify the current API version using the documentation
2. **Compare with Tracked Version**: Check against our last known version
3. **Update Rules if Needed**: If API has changed, update configuration rules BEFORE making changes
4. **Document Version**: Track the API version and date checked

### Current API Versions (Last Updated: 2025-01-20)
```yaml
claude_code_cli:
  version: "1.0.56"
  settings_api_version: "2024-12-15"  # Hooks format with matchers
  last_checked: "2025-01-20"
  
claude_api:
  model_version: "claude-3-opus-20240229"
  api_version: "2023-06-01"
  last_checked: "2025-01-20"
  
hooks_api:
  format_version: "v2"  # Array format with matchers
  events: ["PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop"]
  last_checked: "2025-01-20"
```

### Version Check Workflow
```bash
# Before ANY settings/hooks changes:
1. Check docs: https://docs.anthropic.com/en/docs/claude-code/settings
2. Verify hooks format: https://docs.anthropic.com/en/docs/claude-code/hooks
3. Compare with tracked versions above
4. If newer version found:
   - Update API version tracking
   - Review all configuration rules
   - Update examples and patterns
   - THEN make the requested changes
```

### Version Change Indicators
Watch for these signs that API might have changed:
- Settings validation errors mentioning "new format"
- Deprecated field warnings
- Unexpected behavior after Claude Code updates
- New features mentioned in `/doctor` output
- Changes in documentation examples

## Claude Code Settings Configuration

### Valid settings.json Fields
Only use these fields in `~/.claude/settings.json`:
- `model`: Override default model (e.g., "claude-3-opus-20240229")
- `includeCoAuthoredBy`: Include Claude byline in commits (boolean)
- `cleanupPeriodDays`: Chat transcript retention period (number)
- `env`: Environment variables for sessions (object)
- `permissions`: Tool usage rules (object with tools sub-object)
- `hooks`: Custom commands for tool events (see format below)
- `apiKeyHelper`: Custom script to generate auth value
- `forceLoginMethod`: Restrict login method
- `enableAllProjectMcpServers`: Auto-approve MCP servers (boolean)
- `enabledMcpjsonServers`: Specific MCP servers to approve (array)
- `disabledMcpjsonServers`: Specific MCP servers to reject (array)

### Hooks Configuration Rules

#### MANDATORY: Pre-Hook Creation Checklist
1. **Version Check** (ALWAYS DO FIRST):
   ```bash
   # Check current hooks documentation
   WebFetch https://docs.anthropic.com/en/docs/claude-code/hooks
   # Compare format with our tracked version
   # If different, update tracked version and rules
   ```

2. **Validate Against Current Format**:
   - Confirm array-based format is still current
   - Check if new event types are available
   - Verify matcher patterns still work the same way

3. **Test in Isolation**:
   - Create minimal test hook first
   - Verify it works before adding complex logic

### Hooks Format (Version: v2, Last Verified: 2025-01-20)
```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",  // Optional for some events
        "hooks": [
          {
            "type": "command",
            "command": "your-command",
            "timeout": 60  // Optional, in seconds
          }
        ]
      }
    ]
  }
}
```

**Hook Events**: PreToolUse, PostToolUse, UserPromptSubmit, Stop, etc.
**Matchers**: Tool names or regex patterns (e.g., "Bash", "Edit|Write")
**Note**: Never use `"matcher": "*"` - use empty string or omit instead

### Hook Creation Examples (Version-Checked)
```json
// Example 1: Simple pre-bash hook
"PreToolUse": [{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "echo 'Running bash command'",
    "timeout": 5
  }]
}]

// Example 2: Post-edit formatting
"PostToolUse": [{
  "matcher": "Edit|Write|MultiEdit",
  "hooks": [{
    "type": "command",
    "command": "dotnet format --verify-no-changes || true",
    "timeout": 30
  }]
}]

// Example 3: User prompt hook (no matcher needed)
"UserPromptSubmit": [{
  "hooks": [{
    "type": "command",
    "command": "date +%Y-%m-%d_%H:%M:%S",
    "timeout": 2
  }]
}]
```

### Common Invalid Fields (DO NOT USE)
- apiKey, temperature, maxTokens, theme, notifications
- tools (use permissions.tools instead)
- customCommands, defaultContext
- Old string-format hooks (must use array format)

## Example: Complete Hook Creation Workflow

### Scenario: User requests new hook for test automation
```bash
# Step 1: Check API version FIRST
WebFetch https://docs.anthropic.com/en/docs/claude-code/hooks "Get current hooks format and version"

# Step 2: Compare with tracked version
# If hooks_api.format_version != documented version:
#   - Update API version tracking in CLAUDE.md
#   - Review all format changes
#   - Update examples

# Step 3: Create test hook
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "echo 'Edit completed'",
        "timeout": 5
      }]
    }]
  }
}

# Step 4: Test the hook works
# Edit a file and verify hook executes

# Step 5: Implement full hook
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "npm test -- --findRelatedTests",
        "timeout": 60
      }]
    }]
  }
}
```

### API Deprecation Handling
If API version check reveals deprecation:
1. Document the deprecation date
2. Update to new format immediately
3. Test thoroughly
4. Update all examples in CLAUDE.md
5. Note migration path for future reference