const LearningStore = require('./learning-store');
const fs = require('fs').promises;
const path = require('path');

// Test database path
const TEST_DB_PATH = '.claude/learning/test-claude-learning.db';

describe('LearningStore', () => {
    let store;

    beforeEach(async () => {
        // Clean up any existing test database
        try {
            await fs.unlink(TEST_DB_PATH);
        } catch (err) {
            // File doesn't exist, which is fine
        }
        
        store = new LearningStore(TEST_DB_PATH);
        await store.initialize();
    });

    afterEach(async () => {
        if (store) {
            await store.close();
        }
        // Clean up test database
        try {
            await fs.unlink(TEST_DB_PATH);
        } catch (err) {
            // Ignore errors
        }
    });

    describe('Initialization', () => {
        test('should create database file', async () => {
            const stats = await fs.stat(TEST_DB_PATH);
            expect(stats.isFile()).toBe(true);
        });

        test('should create all required tables', async () => {
            // Check tables exist by querying sqlite_master
            const tables = await store.all(
                "SELECT name FROM sqlite_master WHERE type='table'"
            );
            
            const tableNames = tables.map(t => t.name);
            expect(tableNames).toContain('executions');
            expect(tableNames).toContain('patterns');
            expect(tableNames).toContain('knowledge');
        });
    });

    describe('Command Execution Tracking', () => {
        test('should record execution successfully', async () => {
            const id = await store.recordExecution(
                '/fix',
                { issue: 'memory leak' },
                'success',
                { duration_ms: 1500, project_context: 'test-project' }
            );

            expect(id).toBeGreaterThan(0);
        });

        test('should retrieve recent executions', async () => {
            // Record multiple executions
            await store.recordExecution('/fix', { issue: 'bug1' }, 'success');
            await store.recordExecution('/test', { target: 'unit' }, 'success');
            await store.recordExecution('/fix', { issue: 'bug2' }, 'failure');

            const fixExecutions = await store.getRecentExecutions('/fix', 10);
            expect(fixExecutions).toHaveLength(2);
            expect(fixExecutions[0].command).toBe('/fix');
            expect(fixExecutions[0].parameters.issue).toBe('bug2'); // Most recent first
        });

        test('should find similar issues by keywords', async () => {
            await store.recordExecution(
                '/fix',
                { issue: 'authentication timeout' },
                'success',
                { error_message: 'Token expired' }
            );
            
            await store.recordExecution(
                '/fix',
                { issue: 'database connection' },
                'success'
            );

            await store.recordExecution(
                '/fix',
                { issue: 'auth failure' },
                'failure',
                { error_message: 'Invalid credentials' }
            );

            const similar = await store.getSimilarIssues('auth', 5);
            expect(similar).toHaveLength(2);
            expect(similar.every(e => 
                e.command.includes('auth') || 
                JSON.stringify(e.parameters).includes('auth') ||
                (e.error_message && e.error_message.includes('auth'))
            )).toBe(true);
        });

        test('should handle empty parameters gracefully', async () => {
            const id = await store.recordExecution('/commit', null, 'success');
            const executions = await store.getRecentExecutions();
            
            expect(executions[0].parameters).toBeNull();
        });
    });

    describe('Knowledge Management', () => {
        test('should add and retrieve knowledge', async () => {
            await store.addKnowledge(
                'redis-timeout-fix',
                'Check connection pool size - it\'s always the pool',
                'debugging'
            );

            const knowledge = await store.getKnowledge('redis-timeout-fix');
            expect(knowledge.value).toBe('Check connection pool size - it\'s always the pool');
            expect(knowledge.category).toBe('debugging');
            expect(knowledge.usage_count).toBe(1);
        });

        test('should update existing knowledge and increment usage', async () => {
            await store.addKnowledge('deploy-tip', 'Always backup first', 'deployment');
            await store.addKnowledge('deploy-tip', 'Always backup first and test', 'deployment');

            const knowledge = await store.getKnowledge('deploy-tip');
            expect(knowledge.value).toBe('Always backup first and test');
            expect(knowledge.usage_count).toBe(2); // Incremented on update
        });

        test('should search knowledge by query', async () => {
            await store.addKnowledge('auth-fix', 'Check OAuth scopes', 'security');
            await store.addKnowledge('db-optimization', 'Add indexes on foreign keys', 'performance');
            await store.addKnowledge('auth-debug', 'Enable verbose logging', 'debugging');

            const results = await store.searchKnowledge('auth');
            expect(results).toHaveLength(2);
            expect(results.every(k => 
                k.key.includes('auth') || 
                k.value.includes('auth')
            )).toBe(true);
        });
    });

    describe('Pattern Tracking', () => {
        test('should record new pattern', async () => {
            const id = await store.recordPattern('/fix,/test,/commit');
            expect(id).toBeGreaterThan(0);
        });

        test('should increment frequency for existing pattern', async () => {
            const pattern = '/fix,/test,/commit';
            
            await store.recordPattern(pattern);
            await store.recordPattern(pattern);
            await store.recordPattern(pattern);

            const patterns = await store.getFrequentPatterns(3);
            expect(patterns).toHaveLength(1);
            expect(patterns[0].pattern_sequence).toBe(pattern);
            expect(patterns[0].frequency).toBe(3);
        });

        test('should only return patterns above threshold', async () => {
            await store.recordPattern('/fix,/commit');
            await store.recordPattern('/fix,/commit');
            
            await store.recordPattern('/test,/commit');
            await store.recordPattern('/test,/commit');
            await store.recordPattern('/test,/commit');
            await store.recordPattern('/test,/commit');

            const frequentPatterns = await store.getFrequentPatterns(3);
            expect(frequentPatterns).toHaveLength(1);
            expect(frequentPatterns[0].pattern_sequence).toBe('/test,/commit');
        });
    });

    describe('Time Window Queries', () => {
        test('should parse time windows correctly', async () => {
            // Insert executions with specific timestamps
            const now = new Date();
            const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
            const lastWeek = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

            // We'll record some executions and test the window
            await store.recordExecution('/fix', { recent: true }, 'success');
            
            // Note: SQLite datetime handling might need adjustment for testing
            const executions = await store.getExecutionsInWindow('24h');
            expect(executions.length).toBeGreaterThan(0);
        });

        test('should handle different time window formats', async () => {
            await store.recordExecution('/test', {}, 'success');
            
            // Test different formats
            const hourly = await store.getExecutionsInWindow('1h');
            const daily = await store.getExecutionsInWindow('1d');
            const weekly = await store.getExecutionsInWindow('1w');
            
            // All should include our recent execution
            expect(hourly.length).toBeGreaterThanOrEqual(1);
            expect(daily.length).toBeGreaterThanOrEqual(1);
            expect(weekly.length).toBeGreaterThanOrEqual(1);
        });

        test('should throw error for invalid time window', async () => {
            await expect(store.getExecutionsInWindow('invalid'))
                .rejects.toThrow('Invalid time window format');
        });
    });

    describe('Performance', () => {
        test('should handle bulk operations efficiently', async () => {
            const startTime = Date.now();
            
            // Insert 100 executions
            const promises = [];
            for (let i = 0; i < 100; i++) {
                promises.push(
                    store.recordExecution(
                        '/test',
                        { index: i },
                        i % 2 === 0 ? 'success' : 'failure'
                    )
                );
            }
            
            await Promise.all(promises);
            
            // Query should be fast
            const queryStart = Date.now();
            const results = await store.getRecentExecutions('/test', 50);
            const queryTime = Date.now() - queryStart;
            
            expect(results).toHaveLength(50);
            expect(queryTime).toBeLessThan(50); // Should be under 50ms
        });
    });

    describe('Error Handling', () => {
        test('should handle invalid outcome values', async () => {
            await expect(
                store.recordExecution('/test', {}, 'invalid-outcome')
            ).rejects.toThrow();
        });

        test('should handle database errors gracefully', async () => {
            await store.close();
            
            // Try to use closed database
            await expect(
                store.recordExecution('/test', {}, 'success')
            ).rejects.toThrow();
        });
    });
});

// Test helpers for performance measurement
function measureTime(fn) {
    const start = Date.now();
    const result = fn();
    const duration = Date.now() - start;
    return { result, duration };
}