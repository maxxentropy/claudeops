# The Core Problem: Why Slash Commands?

## The Fundamental Issue

### The Context vs. Command Priority Problem

Claude (and similar AI assistants) have a critical behavioral pattern:
**Immediate user commands override background context rules.**

This creates a frustrating cycle:

1. **User creates detailed memory/rules** → "Always run tests before committing"
2. **User gives direct command** → "commit these changes"
3. **Claude follows the immediate command** → Commits without testing
4. **User frustrated** → "Why didn't you follow the rules?"

### Why This Happens

The AI's attention system prioritizes:
1. **Direct user input** (highest weight)
2. **Recent conversation** (medium weight)
3. **Background context/memory** (lowest weight)

When a user says "commit changes," the AI's response generation is dominated by that immediate instruction, not by a rule buried in memory saying "always test first."

## Traditional Approaches That Don't Work

### 1. More Detailed Memory Files
**Attempt**: Add more rules, make them more emphatic
**Result**: Still ignored when user gives direct commands
**Why**: Doesn't change the attention priority problem

### 2. Constant Reminders
**Attempt**: User reminds Claude of rules each time
**Result**: Works but defeats the purpose of automation
**Why**: Requires user discipline instead of system discipline

### 3. Hoping for "Better Discipline"
**Attempt**: Expect Claude to check memory before acting
**Result**: Inconsistent at best
**Why**: Fighting against the model's fundamental behavior

## The Slash Command Solution

### How It Works

Instead of fighting the attention system, we **use it to our advantage**:

1. **User types**: `/commit`
2. **Claude receives**: An immediate command that CONTAINS the full workflow
3. **Result**: The workflow steps are in the highest-priority attention slot

### Why This Is Brilliant

1. **Leverages Natural Behavior**: Uses Claude's tendency to follow immediate commands
2. **Embeds Workflows**: The command itself contains all the steps
3. **User Convenience**: Actually easier to type `/commit` than "commit these changes"
4. **Guaranteed Execution**: Can't skip steps that are part of the command itself

### The Key Insight

**We're not trying to make Claude remember rules.
We're making the rules part of the command.**

## Example: The Difference

### Old Way (Fails)
```
Memory: "Always run tests before committing"
User: "commit the changes"
Claude: *git add -A && git commit -m "Update"* ❌
```

### New Way (Works)
```
User: "/commit"
Claude reads commit.md which says:
1. Run tests
2. Check build
3. Then commit
Claude: *Executes full workflow* ✅
```

## Additional Benefits

### 1. Single Source of Truth
- Principles in `principles.md`
- Commands reference principles via tags
- Update once, affects everywhere

### 2. Explicit Over Implicit
- No hidden expectations
- User knows exactly what `/commit` will do
- Claude can't misinterpret

### 3. Composable Workflows
- `/prdq` → `/safe implement`
- Each command focused and reusable
- Build complex workflows from simple parts

### 4. Self-Documenting
- `/commands` shows all available workflows
- Each command file explains its purpose
- No need to remember complex rules

## The Psychology

### For Users
- **Less typing**: `/fix` vs "investigate the bug, find root cause, fix it, test thoroughly"
- **More confidence**: Know exactly what will happen
- **Less frustration**: No more "why didn't you test?"

### For Claude
- **Clear instructions**: No ambiguity about what to do
- **Enforced workflows**: Steps are mandatory, not optional
- **Better outcomes**: Following proper process every time

## Summary

The slash command strategy solves a fundamental mismatch between:
- How users want Claude to work (remember and follow all rules)
- How Claude actually works (prioritize immediate commands)

By embedding the rules IN the commands, we align these two realities and create a system that works reliably 100% of the time without requiring discipline from either party.