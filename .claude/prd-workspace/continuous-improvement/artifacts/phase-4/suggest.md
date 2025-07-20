# /suggest - Command Pattern Recommendations

Embody these expert personas:
<!-- INCLUDE: personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: personas.md#PRODUCT_ENGINEER -->

Discover opportunities to create new commands based on detected usage patterns.

## Usage

```
/suggest [threshold]
```

### Options:
- `threshold` - Minimum pattern frequency (default: 3)

### Examples:
- `/suggest` - Show patterns used 3+ times
- `/suggest 5` - Show patterns used 5+ times
- `/suggest 10` - Only highly frequent patterns

## Process

1. **Analyze Patterns**:
   - Identify frequently used command sequences
   - Calculate time savings potential
   - Check for existing similar commands

2. **Generate Suggestions**:
   - Create meaningful command names
   - Estimate implementation effort
   - Calculate ROI (time saved vs effort)

3. **Prioritize**:
   - Sort by potential impact
   - Consider team needs
   - Factor in complexity

4. **Provide Action Steps**:
   - Show how to create each command
   - Include sample implementation
   - Link to /newcmd for creation

## Output Format

```
# 💡 Suggested New Commands

Based on your usage patterns, consider creating these commands:

## 1. `/fix-auth` ⭐ HIGH IMPACT
**Pattern**: `/fix → /test → /commit` (used 15 times)
**Time Savings**: ~10 min per use
**Confidence**: 92%

**What it would do**:
- Check Redis connection pool
- Verify OAuth token expiry
- Test auth endpoints
- Commit with proper message

**Common context**:
- Usually involves: auth.js, token-manager.js
- Typical errors: "Token expired", "401 Unauthorized"
- Average resolution time: 18 minutes

**To create**:
```
/newcmd fix-auth
```

## 2. `/deploy-safe` 🚀 MEDIUM IMPACT
**Pattern**: `/test all → /build prod → /commit → /deploy` (used 8 times)
**Time Savings**: ~15 min per use
**Confidence**: 85%

**What it would do**:
- Run full test suite
- Build production bundle
- Create deployment commit
- Deploy with rollback ready

**Risk mitigation**:
- Always happens before Friday deploys
- Includes your pre-flight checklist
- Adds extra monitoring

**To create**:
```
/newcmd deploy-safe
```

## 3. `/morning-setup` ☕ QUALITY OF LIFE
**Pattern**: `/pull → /install → /test` (used 22 times)
**Time Savings**: ~5 min per day
**Confidence**: 78%

**What it would do**:
- Pull latest changes
- Install dependencies if changed
- Run quick smoke tests
- Show recent commits

**Daily workflow enhancement**:
- Detected as first commands each day
- Would include coffee timer ☕
- Shows team updates

---

## 📊 Pattern Summary
- Total patterns detected: 12
- Actionable patterns: 5
- Potential time savings: ~4 hours/week
- Recommended implementations: 3

## 🎯 Quick Actions
1. Review suggestions with team
2. Start with highest impact command
3. Use `/newcmd` to implement
4. Track usage with `/metrics`

💡 **Tip**: Patterns with 5+ uses and >80% success rate make the best commands!
```

## Integration

The suggest command:
- Queries pattern database for frequent sequences
- Analyzes execution context for each pattern
- Estimates time savings based on historical data
- Generates actionable recommendations

## Best Practices

- Review suggestions weekly
- Involve the team in prioritization
- Start with simple, high-impact commands
- Measure actual vs predicted savings
- Iterate based on usage

## Suggestion Algorithm

1. **Pattern Frequency**: How often is it used?
2. **Success Rate**: Does it usually work?
3. **Time Investment**: How long does it take?
4. **Context Similarity**: Is it always the same?
5. **Error Reduction**: Does it prevent failures?

Commands are scored on these factors and presented in priority order.