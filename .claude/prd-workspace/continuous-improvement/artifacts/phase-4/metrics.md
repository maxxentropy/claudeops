# /metrics - Learning System Dashboard

Embody these expert personas:
<!-- INCLUDE: personas.md#SRE_ENGINEER -->
<!-- INCLUDE: personas.md#PRODUCT_ENGINEER -->

View comprehensive metrics showing the value and impact of the learning system.

## Usage

```
/metrics [timeframe]
```

### Timeframe Options:
- `1d` - Last 24 hours
- `7d` - Last 7 days (default)
- `30d` - Last 30 days
- `90d` - Last 90 days

### Examples:
- `/metrics` - Show last 7 days
- `/metrics 30d` - Show last 30 days
- `/metrics 1d` - Show last 24 hours

## Metrics Displayed

### 📊 Efficiency Gains
- Total commands executed
- Success rate percentage
- Average execution time
- Estimated time saved through patterns
- Bugs potentially prevented

### 🏆 Most Used Commands
- Command frequency ranking
- Success rates per command
- Average duration per command
- Failure patterns

### 🧠 Learning System Impact
- Patterns detected and used
- Knowledge entries created
- Context hit rate (how often historical context helped)
- Suggested optimizations accepted

### 👥 Team Patterns
- Peak usage times
- Most common issue types
- Average resolution times
- Improvement trends

### 💡 Insights
- Commands that often fail together
- Time-based usage patterns
- Knowledge most frequently accessed
- Opportunities for new commands

## Output Format

```
# 📊 Slash Command Metrics (Last 30 days)

## 🚀 Efficiency Gains
- **Commands executed**: 342
- **Success rate**: 87.3% ↑ 5.2%
- **Average duration**: 12.4s ↓ 3.1s
- **Time saved**: ~85.5 hours
- **Errors prevented**: ~12 (estimated)

## 🏆 Most Used Commands
1. **`/fix`** - 98 executions (87% success)
   - Avg duration: 15.2s
   - Common params: timeout, auth, connection

2. **`/safe`** - 76 executions (100% success)
   - Avg duration: 8.1s
   - Zero production incidents

3. **`/commit`** - 65 executions (95% success)
   - Prevented 8 bad commits
   - Avg duration: 5.3s

## 🧠 Learning System Impact
- **Patterns detected**: 23 (5 new this period)
- **Knowledge entries**: 45 (+12 this period)
- **Context hit rate**: 89% (helped find solution)
- **Pattern suggestions**: 15 (8 implemented)

## 👥 Team Patterns
- **Peak usage**: Tue-Thu, 10am-12pm
- **Issue breakdown**:
  - Authentication: 23%
  - Database: 19%
  - API/Network: 15%
  - Other: 43%
- **Resolution time**: 12 min avg (↓ from 47 min)

## 💡 Key Insights
1. **Error Correlation**: `/deploy` failures often follow `/config` changes
2. **Time Pattern**: Friday deployments have 3x higher failure rate
3. **Knowledge Gap**: No documented solutions for WebSocket issues
4. **Automation Opportunity**: `/fix-auth` pattern used 15 times

## 📈 Trends
- Command usage: ↑ 23% from previous period
- Success rate: ↑ 5.2% improvement
- Time to resolution: ↓ 35% faster
- Knowledge base growth: +35% entries

---
💡 **Tip**: Run `/suggest` to see recommended new commands based on these patterns
```

## Integration

The metrics command pulls data from:
- Execution history (success rates, durations)
- Pattern detection (frequency, suggestions)
- Knowledge base (entries, usage)
- Time-series analysis (trends, patterns)

## Best Practices

- Review metrics weekly to spot trends
- Act on automation opportunities
- Share insights with the team
- Use data to justify new commands
- Track improvement over time