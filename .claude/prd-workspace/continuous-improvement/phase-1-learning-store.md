# Phase 1: Learning Store Foundation

## Objective
Create a persistent storage system to track command executions, outcomes, and metadata for future reference.

## Dependencies
- None (first phase)

## Deliverables
- [ ] Learning store module with SQLite backend
- [ ] Schema for command executions, outcomes, and metadata
- [ ] Basic CRUD operations (create, read, update, delete)
- [ ] Index by command type and issue keywords
- [ ] Unit tests for all store operations
- [ ] Documentation for store API

## Technical Specifications

### Database Schema
```sql
-- Command executions table
CREATE TABLE executions (
    id INTEGER PRIMARY KEY,
    command TEXT NOT NULL,
    parameters TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER,
    outcome TEXT CHECK(outcome IN ('success', 'failure', 'partial')),
    error_message TEXT,
    user_feedback TEXT,
    project_context TEXT
);

-- Patterns table
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY,
    pattern_sequence TEXT NOT NULL,
    frequency INTEGER DEFAULT 1,
    last_seen DATETIME,
    suggested_command TEXT
);

-- Knowledge entries table  
CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

-- Indexes for performance
CREATE INDEX idx_command ON executions(command);
CREATE INDEX idx_timestamp ON executions(timestamp);
CREATE INDEX idx_pattern_freq ON patterns(frequency);
```

### API Interface
```javascript
class LearningStore {
    // Core operations
    async recordExecution(command, params, outcome)
    async getRecentExecutions(command, limit = 10)
    async getSimilarIssues(keywords, limit = 5)
    
    // Knowledge management
    async addKnowledge(key, value, category)
    async getKnowledge(key)
    async searchKnowledge(query)
    
    // Pattern tracking
    async recordPattern(sequence)
    async getFrequentPatterns(threshold = 3)
}
```

## Success Criteria
- [ ] Store initializes with proper schema
- [ ] Can record and retrieve executions
- [ ] Search by keywords returns relevant results
- [ ] Performance: <50ms for common queries
- [ ] 95% test coverage

## Context for Next Phase
Phase 2 will build pattern recognition on top of this store, requiring:
- Efficient sequence queries
- Ability to update pattern frequencies
- Fast retrieval of similar past executions