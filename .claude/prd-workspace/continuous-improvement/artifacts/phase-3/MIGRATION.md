# Migration Guide: Integrating Learning System with Slash Commands

## Overview

This guide explains how to integrate the Continuously Improving Claude System with existing slash commands.

## Quick Start

```javascript
const { getEnhancer } = require('./phase-3/command-enhancer');

// Get the enhancer instance
const enhancer = getEnhancer();

// Enhance a command
const result = await enhancer.enhanceCommand('fix', { issue: 'timeout' });
console.log(result.content); // Enhanced command with context
```

## Integration Steps

### 1. Update Slash Command Loader

Modify your slash command system to use the enhancer:

```javascript
// Before: Load command directly
const commandContent = await fs.readFile(`${command}.md`, 'utf-8');

// After: Load with enhancement
const { getEnhancer } = require('./continuous-improvement/phase-3/command-enhancer');
const enhancer = getEnhancer();
const result = await enhancer.enhanceCommand(command, parameters);
const commandContent = result.content;
```

### 2. Track Command Outcomes

Record the outcome of command executions:

```javascript
// Start of command execution
const result = await enhancer.enhanceCommand('fix', params);
const executionId = result.executionId;

try {
    // Execute command...
    
    // Record success
    await enhancer.recordOutcome(executionId, 'success', {
        duration_ms: Date.now() - startTime,
        user_feedback: 'Fixed the issue'
    });
} catch (error) {
    // Record failure
    await enhancer.recordOutcome(executionId, 'failure', {
        duration_ms: Date.now() - startTime,
        error_message: error.message
    });
}
```

### 3. Add Knowledge Capture

Allow users to save learnings:

```javascript
// In your /learn command implementation
async function learnCommand(key, value, category) {
    const enhancer = getEnhancer();
    await enhancer.addKnowledge(key, value, category);
    console.log(`Knowledge saved: ${key}`);
}
```

### 4. Display Metrics

Show learning system metrics:

```javascript
// In your /metrics command
async function metricsCommand(timeframe = '30d') {
    const enhancer = getEnhancer();
    const metrics = await enhancer.getMetrics(timeframe);
    
    console.log(`Total Commands: ${metrics.summary.totalExecutions}`);
    console.log(`Success Rate: ${metrics.summary.successRate}`);
    console.log(`Patterns Found: ${metrics.summary.patternsDetected}`);
    // ... display more metrics
}
```

## Configuration

### Environment Variables

```bash
# Optional: Custom paths
CLAUDE_LEARNING_DB_PATH=.claude/learning/claude-learning.db
CLAUDE_COMMANDS_PATH=.claude
```

### Initialization Options

```javascript
const enhancer = new CommandEnhancer({
    commandsPath: '.claude',           // Where command files are stored
    dbPath: '.claude/learning/db.sqlite' // Learning database location
});
```

## Context Injection Format

Enhanced commands will include these sections:

```markdown
# /command-name

<!-- LEARNING_CONTEXT: SIMILAR_ISSUES -->
📚 **Recent Similar Executions:**
1. ✓ /fix (issue: timeout) - 2 hours ago, 15s
2. ✗ /fix (issue: connection) - Error: Port blocked - 1 day ago, 45s
<!-- END_LEARNING_CONTEXT -->

<!-- LEARNING_CONTEXT: TEAM_KNOWLEDGE -->
💡 **Team Knowledge:**
- **timeout-fix**: Always check Redis connection pool first
<!-- END_LEARNING_CONTEXT -->

<!-- LEARNING_CONTEXT: COMMON_PATTERNS -->
🔄 **Common Patterns:**
- `/fix,/test,/commit` (used 12 times)
<!-- END_LEARNING_CONTEXT -->

<!-- LEARNING_CONTEXT: NEXT_SUGGESTIONS -->
➡️ **Likely Next Commands:**
- `/test → /commit` (85% confidence)
<!-- END_LEARNING_CONTEXT -->

[Original command content continues...]
```

## Performance Considerations

- Context injection adds <200ms latency
- Context is cached for 5 minutes
- Database queries are indexed for speed
- Graceful fallback if enhancement fails

## Gradual Migration

### Phase 1: Read-Only Integration
Just add context to commands without tracking:

```javascript
// Only enhance, don't track
const result = await enhancer.enhanceCommand(command, params);
// Don't call recordOutcome
```

### Phase 2: Tracking Integration
Start recording executions:

```javascript
// Track outcomes
await enhancer.recordOutcome(executionId, outcome);
```

### Phase 3: Full Integration
Add knowledge capture and metrics:

```javascript
// Full features
await enhancer.addKnowledge(key, value);
const metrics = await enhancer.getMetrics();
```

## Testing

Test the integration:

```javascript
// Test enhancement
const enhanced = await enhancer.enhanceCommand('test-command');
assert(enhanced.content.includes('LEARNING_CONTEXT'));

// Test metrics
const metrics = await enhancer.getMetrics('1d');
assert(metrics.summary.totalExecutions >= 0);
```

## Troubleshooting

### Enhancement Fails
- Check database permissions
- Verify command file exists
- Check error in result.error

### No Context Appears
- Ensure there's execution history
- Check cache isn't stale
- Verify database has data

### Performance Issues
- Check database size (run cleanup)
- Verify indexes exist
- Consider increasing cache timeout

## Maintenance

### Regular Cleanup
```javascript
// Clean data older than 90 days
await enhancer.cleanup(90);
```

### Export/Import
```javascript
// Export learning data
const data = await enhancer.exportLearningData();
fs.writeFileSync('learning-backup.json', JSON.stringify(data));

// Import (not yet implemented)
// await enhancer.importLearningData(data);
```

## Example Integration

Here's a complete example of integrating with a slash command:

```javascript
const { getEnhancer } = require('./continuous-improvement/phase-3/command-enhancer');

async function executeSlashCommand(commandName, parameters) {
    const enhancer = getEnhancer();
    const startTime = Date.now();
    
    // Enhance command with learning context
    const result = await enhancer.enhanceCommand(commandName, parameters);
    
    if (!result.enhanced) {
        console.warn(`Enhancement failed: ${result.error}`);
    }
    
    try {
        // Execute the enhanced command
        const output = await runCommand(result.content, parameters);
        
        // Record success
        if (result.executionId) {
            await enhancer.recordOutcome(result.executionId, 'success', {
                duration_ms: Date.now() - startTime
            });
        }
        
        return output;
        
    } catch (error) {
        // Record failure
        if (result.executionId) {
            await enhancer.recordOutcome(result.executionId, 'failure', {
                duration_ms: Date.now() - startTime,
                error_message: error.message
            });
        }
        
        throw error;
    }
}
```

## Benefits

After integration, users will see:
- Historical context for similar issues
- Team knowledge surfaced automatically
- Pattern-based suggestions
- Time-saving metrics
- Continuous improvement of workflows