# Learning Store API Documentation

## Overview
The Learning Store provides persistent storage for Claude's command executions, patterns, and team knowledge. It uses SQLite for local, file-based storage.

## Installation

```bash
npm install
```

## Usage

```javascript
const LearningStore = require('./learning-store');

// Initialize store
const store = new LearningStore();
await store.initialize();

// Use the store
await store.recordExecution('/fix', { issue: 'bug' }, 'success');

// Clean up
await store.close();
```

## API Reference

### Constructor

#### `new LearningStore(dbPath?)`
Creates a new learning store instance.

- `dbPath` (optional): Path to SQLite database file. Default: `.claude/learning/claude-learning.db`

### Initialization

#### `async initialize()`
Initializes the database connection and creates schema if needed.

```javascript
const store = new LearningStore();
await store.initialize();
```

### Command Execution Tracking

#### `async recordExecution(command, params, outcome, options?)`
Records a command execution.

**Parameters:**
- `command` (string): The command executed (e.g., '/fix')
- `params` (object): Parameters passed to the command
- `outcome` (string): One of 'success', 'failure', 'partial'
- `options` (object, optional):
  - `duration_ms` (number): Execution duration in milliseconds
  - `error_message` (string): Error message if failed
  - `user_feedback` (string): User feedback about the execution
  - `project_context` (string): Project-specific context

**Returns:** Execution ID (number)

```javascript
const id = await store.recordExecution(
    '/fix',
    { issue: 'memory leak' },
    'success',
    { duration_ms: 1500, project_context: 'my-app' }
);
```

#### `async getRecentExecutions(command?, limit?)`
Retrieves recent command executions.

**Parameters:**
- `command` (string, optional): Filter by specific command
- `limit` (number, optional): Maximum results. Default: 10

**Returns:** Array of execution objects

```javascript
// Get last 10 executions of any command
const recent = await store.getRecentExecutions();

// Get last 5 /fix executions
const fixes = await store.getRecentExecutions('/fix', 5);
```

#### `async getSimilarIssues(keywords, limit?)`
Finds executions with similar issues based on keywords.

**Parameters:**
- `keywords` (string | string[]): Keywords to search for
- `limit` (number, optional): Maximum results. Default: 5

**Returns:** Array of execution objects

```javascript
// Find issues related to authentication
const authIssues = await store.getSimilarIssues('auth timeout');

// Multiple keywords
const dbIssues = await store.getSimilarIssues(['database', 'connection']);
```

### Knowledge Management

#### `async addKnowledge(key, value, category?)`
Adds or updates a knowledge entry.

**Parameters:**
- `key` (string): Unique identifier for the knowledge
- `value` (string): The knowledge content
- `category` (string, optional): Category for organization

**Returns:** true

```javascript
await store.addKnowledge(
    'redis-timeout-fix',
    'Check connection pool size - it\'s always the pool',
    'debugging'
);
```

#### `async getKnowledge(key)`
Retrieves a specific knowledge entry.

**Parameters:**
- `key` (string): Knowledge identifier

**Returns:** Knowledge object or null

```javascript
const tip = await store.getKnowledge('redis-timeout-fix');
// { key, value, category, created_at, usage_count }
```

#### `async searchKnowledge(query)`
Searches knowledge entries.

**Parameters:**
- `query` (string): Search query

**Returns:** Array of knowledge objects

```javascript
const authTips = await store.searchKnowledge('auth');
```

### Pattern Tracking

#### `async recordPattern(sequence)`
Records a command sequence pattern.

**Parameters:**
- `sequence` (string): Comma-separated command sequence

**Returns:** Pattern ID (number)

```javascript
// Record a common workflow
await store.recordPattern('/fix,/test,/commit');
```

#### `async getFrequentPatterns(threshold?)`
Gets patterns that occur frequently.

**Parameters:**
- `threshold` (number, optional): Minimum frequency. Default: 3

**Returns:** Array of pattern objects

```javascript
const patterns = await store.getFrequentPatterns(5);
// Returns patterns seen 5+ times
```

### Utility Methods

#### `async getExecutionsInWindow(timeWindow)`
Gets executions within a time window.

**Parameters:**
- `timeWindow` (string): Time window format (e.g., '24h', '7d', '1w')

**Returns:** Array of execution objects

```javascript
// Get executions from last 24 hours
const recent = await store.getExecutionsInWindow('24h');

// Last week
const weekly = await store.getExecutionsInWindow('7d');
```

#### `async close()`
Closes the database connection.

```javascript
await store.close();
```

## Database Schema

### Tables

#### executions
Stores command execution history.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| command | TEXT | Command name |
| parameters | TEXT | JSON parameters |
| timestamp | DATETIME | Execution time |
| duration_ms | INTEGER | Duration in ms |
| outcome | TEXT | success/failure/partial |
| error_message | TEXT | Error if failed |
| user_feedback | TEXT | User feedback |
| project_context | TEXT | Project context |

#### patterns
Stores detected command patterns.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| pattern_sequence | TEXT | Command sequence |
| frequency | INTEGER | Times observed |
| last_seen | DATETIME | Last occurrence |
| suggested_command | TEXT | Suggested optimization |

#### knowledge
Stores team knowledge and solutions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| key | TEXT | Unique identifier |
| value | TEXT | Knowledge content |
| category | TEXT | Category |
| created_at | DATETIME | Creation time |
| usage_count | INTEGER | Access count |

## Error Handling

The store throws errors for:
- Invalid outcome values (must be 'success', 'failure', or 'partial')
- Database connection failures
- Invalid time window formats
- Closed database operations

Always wrap operations in try-catch blocks:

```javascript
try {
    await store.recordExecution('/test', {}, 'success');
} catch (error) {
    console.error('Failed to record execution:', error);
}
```

## Performance Considerations

- Indexes on command, timestamp, and pattern frequency
- Queries optimized for <50ms response time
- Bulk operations should use transactions (future enhancement)
- Consider periodic cleanup of old data (>90 days)