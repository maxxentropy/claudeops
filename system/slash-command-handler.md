# Slash Command Handler Protocol

## CRITICAL: Unrecognized Command Handling

When a user types a slash command that is NOT recognized:

### 1. **STOP IMMEDIATELY**
- Do NOT proceed with any action
- Do NOT make assumptions about intent
- Do NOT try to "be helpful" by guessing

### 2. **Search for Similar Commands**
```
1. Use Grep to search for available slash commands in /commands/
2. Find commands that are similar to what was typed
3. List the closest matches
```

### 3. **Response Template**
```
❌ Unrecognized command: /[typed-command]

Did you mean one of these?
- /safe - Run any task safely with verification
- /save-state - Save current state (if exists)
- /[other-similar] - Description

Available commands: /help
```

### 4. **If No Similar Commands Found**
```
❌ Unrecognized command: /[typed-command]

This command does not exist. 
Type /help for available commands.
```

## VIOLATIONS TO AVOID

❌ **NEVER** interpret an unrecognized command as a request
❌ **NEVER** proceed with actions based on assumptions  
❌ **NEVER** create functionality for non-existent commands
❌ **NEVER** say "I'll implement what you probably meant"

## Core Principle Alignment

This protocol ensures:
- **No shortcuts**: Verify command exists before ANY action
- **Exactly what's asked**: Invalid command = no action
- **No assumptions**: Never guess user intent
- **Safety first**: Prevent unintended actions

## Example Scenarios

### User types: /save
```
❌ Unrecognized command: /save

Did you mean:
- /safe - Run any task safely with verification

Type /help for available commands.
```

### User types: /quickfix
```
❌ Unrecognized command: /quickfix

Did you mean:
- /quick - Execute simple tasks efficiently
- /fix - Fix code issues with safety checks

Type /help for available commands.
```

### User types: /xyz123
```
❌ Unrecognized command: /xyz123

This command does not exist.
Type /help for available commands.
```

## Implementation Check

Before responding to ANY slash command:
1. Check if command exists in /commands/ directory
2. If not found, follow this protocol
3. NEVER proceed without valid command match