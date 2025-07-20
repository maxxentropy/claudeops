# Phase 4: Learning Meta Commands

## Objective
Create new commands that allow users to interact with and benefit from the learning system.

## Dependencies
- Phase 1: Learning Store (for data storage/retrieval)
- Phase 2: Pattern Recognition (for suggestions)
- Phase 3: Context Injection (for enhanced commands)

## Deliverables
- [ ] `/learn` command implementation
- [ ] `/metrics` command with dashboard
- [ ] `/suggest` command for new patterns
- [ ] `/history` command for audit trail
- [ ] User documentation
- [ ] Integration tests

## Command Specifications

### `/learn [key] [knowledge]`
Capture team knowledge for future reference.

```javascript
// Example usage:
/learn redis-timeout "Check connection pool size first - it's always the pool"
/learn deploy-friday "Never deploy on Friday after 3pm"

// Implementation
class LearnCommand {
    async execute(key, knowledge) {
        // Validate input
        // Store in knowledge base
        // Tag with category
        // Return confirmation
    }
}
```

### `/metrics [timeframe]`
Display impact metrics and system value.

```markdown
# Output format:
## Slash Command Metrics (Last 30 days)

### Efficiency Gains
- Commands executed: 342
- Average time saved: 15 min/command
- Total time saved: 85.5 hours
- Bugs prevented: 12 (estimated)

### Most Used Commands
1. /fix (98 times, 87% success rate)
2. /safe (76 times, 100% success rate)
3. /commit (65 times, prevented 8 bad commits)

### Learning System Impact
- Patterns detected: 23
- Knowledge entries: 45
- Context hits: 89% (helped find solution)
- Suggested optimizations: 5

### Team Patterns
- Peak usage: Tue-Thu, 10am-12pm
- Most common issues: Auth (23%), Database (19%), API (15%)
- Average resolution time: 12 min (down from 47 min)
```

### `/suggest`
Recommend new commands based on patterns.

```markdown
# Output format:
## Suggested New Commands

Based on your usage patterns, consider creating:

1. **/fix-auth** (used 15 times in last month)
   - Always runs: check Redis, verify tokens, test endpoints
   - Would save ~10 min each time
   
2. **/deploy-safe** (pattern detected 8 times)
   - Combines: /test all, /build prod, /commit, notify team
   - Includes your custom pre-deploy checklist

To create: /newcmd fix-auth
```

### `/history [command] [filter]`
View command execution history and outcomes.

```markdown
# Example output:
## History for /fix (last 10)

1. /fix cors error (2 hours ago)
   - Duration: 15 min
   - Outcome: SUCCESS
   - Solution: Added localhost to allowed origins
   
2. /fix memory leak (1 day ago)
   - Duration: 45 min
   - Outcome: SUCCESS
   - Solution: Fixed event listener cleanup
   
[... more entries ...]
```

## Success Criteria
- [ ] Commands integrate seamlessly with learning system
- [ ] Metrics accurately reflect value delivered
- [ ] Suggestions are actionable and relevant
- [ ] Knowledge capture is frictionless
- [ ] History provides useful audit trail

## Context for Next Phase
Phase 5 will integrate everything and ensure system reliability:
- End-to-end testing of all components
- Performance optimization
- Documentation and training materials