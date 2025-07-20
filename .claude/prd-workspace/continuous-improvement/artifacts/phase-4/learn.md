# /learn - Capture Team Knowledge

Embody these expert personas:
<!-- INCLUDE: personas.md#SENIOR_TEST_ENGINEER -->

Save valuable insights and solutions for the entire team to benefit from.

## Usage

```
/learn <key> <knowledge>
```

### Examples:
- `/learn redis-timeout "Check connection pool size first - it's always the pool"`
- `/learn deploy-friday "Never deploy on Friday after 3pm"`
- `/learn auth-debug "Enable verbose logging in OAuth provider settings"`

## Process

1. **Parse Input**:
   - Extract key (identifier for the knowledge)
   - Extract knowledge value (the actual insight)
   - Auto-detect category based on keywords

2. **Validate**:
   - Key must be unique and descriptive
   - Knowledge must be actionable
   - Check for duplicates

3. **Store Knowledge**:
   - Save to learning system
   - Tag with appropriate category
   - Track creation timestamp

4. **Confirm**:
   - Show what was saved
   - Indicate where it will appear (which commands)

## Categories

Knowledge is automatically categorized:
- **debugging**: Contains "debug", "fix", "error", "issue"
- **performance**: Contains "slow", "optimize", "cache", "speed"
- **security**: Contains "auth", "token", "secure", "permission"
- **deployment**: Contains "deploy", "release", "production"
- **testing**: Contains "test", "coverage", "mock"
- **general**: Everything else

## Integration

Saved knowledge will automatically appear in relevant commands when:
- The command name matches keywords in the knowledge
- Parameters match the knowledge context
- Similar issues are being debugged

## Best Practices

- Keep knowledge **actionable** - what to DO, not just what's wrong
- Use **descriptive keys** - "redis-timeout-fix" not "fix1"
- Include **context** - when this applies
- Be **specific** - concrete steps, not vague advice

## Output Format

```
✅ Knowledge saved successfully!

Key: redis-timeout-fix
Value: Check connection pool size first - it's always the pool
Category: debugging

This knowledge will appear in commands like:
- /fix (when dealing with Redis issues)
- /debug (when investigating timeouts)

Total team knowledge entries: 46
```