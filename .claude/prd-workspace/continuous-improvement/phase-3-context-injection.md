# Phase 3: Context Injection System

## Objective
Modify existing slash commands to automatically include relevant historical context and learned patterns.

## Dependencies
- Phase 1: Learning Store (for historical data retrieval)
- Phase 2: Pattern Recognition (for relevant patterns)

## Deliverables
- [ ] Context injection framework
- [ ] Modified command loader with context awareness
- [ ] Dynamic context templates
- [ ] Performance optimization (caching)
- [ ] Integration tests with existing commands
- [ ] Migration guide for commands

## Technical Specifications

### Context Injection Framework
```javascript
class ContextInjector {
    constructor(learningStore, patternRecognizer) {
        this.store = learningStore;
        this.patterns = patternRecognizer;
        this.cache = new Map(); // Performance optimization
    }
    
    // Inject context into command
    async enhanceCommand(commandName, originalContent) {
        const relevantHistory = await this.getRelevantHistory(commandName);
        const patterns = await this.patterns.getCommandPatterns(commandName);
        
        return this.injectContext(originalContent, {
            history: relevantHistory,
            patterns: patterns,
            knowledge: await this.getRelevantKnowledge(commandName)
        });
    }
    
    // Smart context selection
    async getRelevantHistory(command, params) {
        // Use semantic matching for similar issues
        // Limit to most recent/relevant 3-5 items
        // Include success rate and common solutions
    }
}
```

### Modified Command Structure
```markdown
# /fix - Enhanced with Learning

<!-- INJECTED: SIMILAR_ISSUES -->
Found 3 similar issues in project history:
1. "auth timeout" - Fixed by updating Redis connection (2 days ago, 15min)
2. "auth timeout" - Fixed by increasing token TTL (1 week ago, 45min)
3. "auth fail" - Fixed by checking OAuth scopes (2 weeks ago, 2hrs)
<!-- END_INJECTED -->

<!-- INJECTED: TEAM_KNOWLEDGE -->
Team knowledge: "Auth timeouts often caused by Redis connection pool exhaustion"
<!-- END_INJECTED -->

[Original command content continues...]
```

### Performance Considerations
- Cache frequently accessed patterns (5min TTL)
- Asynchronous context loading
- Fallback to original command if injection fails
- Max 200ms latency for context injection

## Success Criteria
- [ ] All commands load with relevant context
- [ ] Context injection adds <200ms latency
- [ ] Graceful fallback on errors
- [ ] Users report finding context helpful
- [ ] No disruption to existing workflows

## Context for Next Phase
Phase 4 will add new meta commands to interact with the learning system:
- Need API for manual knowledge entry
- Metrics calculation from stored data
- Command suggestion interface