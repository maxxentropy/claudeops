const ContextInjector = require('./context-injector');
const LearningStore = require('../phase-1/learning-store');
const PatternRecognizer = require('../phase-2/pattern-recognizer');
const fs = require('fs').promises;

const TEST_DB_PATH = '.claude/learning/test-context-injector.db';

describe('ContextInjector', () => {
    let store;
    let recognizer;
    let injector;

    beforeEach(async () => {
        // Clean up any existing test database
        try {
            await fs.unlink(TEST_DB_PATH);
        } catch (err) {
            // Ignore
        }
        
        store = new LearningStore(TEST_DB_PATH);
        await store.initialize();
        recognizer = new PatternRecognizer(store);
        injector = new ContextInjector(store, recognizer);
    });

    afterEach(async () => {
        if (store) {
            await store.close();
        }
        try {
            await fs.unlink(TEST_DB_PATH);
        } catch (err) {
            // Ignore
        }
    });

    describe('Constructor', () => {
        test('should require both store and recognizer', () => {
            expect(() => new ContextInjector()).toThrow();
            expect(() => new ContextInjector(store)).toThrow();
            expect(() => new ContextInjector(null, recognizer)).toThrow();
        });

        test('should initialize with default settings', () => {
            expect(injector.cacheTimeout).toBe(5 * 60 * 1000);
            expect(injector.maxContextItems).toBe(5);
            expect(injector.maxLatency).toBe(200);
        });
    });

    describe('Context Enhancement', () => {
        test('should enhance command with history', async () => {
            // Add some execution history
            await store.recordExecution('/fix', { issue: 'bug1' }, 'success', {
                duration_ms: 5000,
                error_message: null
            });
            await store.recordExecution('/fix', { issue: 'bug2' }, 'failure', {
                duration_ms: 10000,
                error_message: 'Connection timeout'
            });

            const originalContent = '# /fix\n\nFix issues in the codebase.';
            const enhanced = await injector.enhanceCommand('/fix', originalContent);

            expect(enhanced).toContain('Recent Similar Executions');
            expect(enhanced).toContain('bug1');
            expect(enhanced).toContain('Connection timeout');
        });

        test('should enhance command with knowledge', async () => {
            // Add knowledge entries
            await store.addKnowledge('fix-timeout', 'Check Redis connection pool', 'debugging');
            await store.addKnowledge('fix-auth', 'Verify OAuth scopes', 'security');

            const originalContent = '# /fix\n\nFix issues.';
            const enhanced = await injector.enhanceCommand('/fix', originalContent);

            expect(enhanced).toContain('Team Knowledge');
            expect(enhanced).toContain('fix-timeout');
            expect(enhanced).toContain('Check Redis connection pool');
        });

        test('should enhance command with patterns', async () => {
            // Create a pattern
            for (let i = 0; i < 3; i++) {
                await store.recordPattern('/fix,/test,/commit');
            }

            const originalContent = '# /fix\n\nFix issues.';
            const enhanced = await injector.enhanceCommand('/fix', originalContent);

            expect(enhanced).toContain('Common Patterns');
            expect(enhanced).toContain('/fix,/test,/commit');
            expect(enhanced).toContain('used 3 times');
        });

        test('should include command suggestions', async () => {
            // Set up pattern for suggestions
            for (let i = 0; i < 5; i++) {
                await store.recordPattern('/fix,/test,/commit');
            }

            // Add recent executions
            await store.recordExecution('/fix', {}, 'success');

            const originalContent = '# /test\n\nRun tests.';
            const enhanced = await injector.enhanceCommand('/test', originalContent);

            // Should suggest /commit as next command
            expect(enhanced).toContain('Likely Next Commands');
        });

        test('should handle timeout gracefully', async () => {
            // Override max latency to force timeout
            injector.maxLatency = 1;

            // Add lots of data to slow down queries
            for (let i = 0; i < 100; i++) {
                await store.recordExecution('/test', { i }, 'success');
            }

            const originalContent = '# /test\n\nTest command.';
            const enhanced = await injector.enhanceCommand('/test', originalContent);

            // Should return original content on timeout
            expect(enhanced).toBe(originalContent);
        });
    });

    describe('Context Gathering', () => {
        test('should find similar executions by parameters', async () => {
            await store.recordExecution('/fix', { file: 'auth.js', type: 'bug' }, 'success');
            await store.recordExecution('/fix', { file: 'auth.js', type: 'feature' }, 'success');
            await store.recordExecution('/fix', { file: 'payment.js', type: 'bug' }, 'success');

            const history = await injector.getRelevantHistory('/fix', { file: 'auth.js' });

            expect(history.length).toBeGreaterThanOrEqual(2);
            expect(history[0]).toContain('auth.js');
        });

        test('should calculate parameter similarity correctly', () => {
            const params1 = { file: 'auth.js', type: 'bug', priority: 'high' };
            const params2 = { file: 'auth.js', type: 'bug', priority: 'low' };
            const params3 = { file: 'payment.js', type: 'feature' };

            const similarity1 = injector.calculateParameterSimilarity(params1, params2);
            const similarity2 = injector.calculateParameterSimilarity(params1, params3);

            expect(similarity1).toBeGreaterThan(similarity2);
            expect(similarity1).toBeGreaterThan(0.5);
            expect(similarity2).toBeLessThan(0.5);
        });

        test('should format execution history correctly', () => {
            const exec = {
                command: '/fix',
                parameters: JSON.stringify({ issue: 'timeout' }),
                outcome: 'success',
                duration_ms: 5000,
                timestamp: new Date(Date.now() - 3600000), // 1 hour ago
                error_message: null
            };

            const formatted = injector.formatExecution(exec);

            expect(formatted).toContain('✓');
            expect(formatted).toContain('/fix');
            expect(formatted).toContain('issue: timeout');
            expect(formatted).toContain('5s');
            expect(formatted).toContain('hour');
        });

        test('should get relevant patterns for command', async () => {
            await store.recordPattern('/build,/test,/deploy');
            await store.recordPattern('/fix,/test,/commit');
            await store.recordPattern('/fix,/test,/commit');
            await store.recordPattern('/fix,/test,/commit');

            const patterns = await injector.getRelevantPatterns('/fix');

            expect(patterns.length).toBeGreaterThan(0);
            expect(patterns[0].sequence).toContain('/fix');
            expect(patterns[0].frequency).toBe(3);
        });

        test('should search knowledge by command and parameters', async () => {
            await store.addKnowledge('auth-fix', 'Check token expiry', 'security');
            await store.addKnowledge('timeout-fix', 'Increase connection pool', 'performance');

            const knowledge = await injector.getRelevantKnowledge('/fix', { issue: 'auth' });

            expect(knowledge.length).toBeGreaterThan(0);
            expect(knowledge[0].key).toBe('auth-fix');
        });
    });

    describe('Context Injection', () => {
        test('should inject context after first heading', () => {
            const original = '# Command Title\n\nCommand description.\n\n## Usage';
            const context = {
                history: ['Fix 1', 'Fix 2'],
                knowledge: [{ key: 'tip', value: 'helpful hint' }],
                patterns: [{ sequence: '/fix,/test', frequency: 3 }],
                suggestions: []
            };

            const injected = injector.injectContext(original, context);

            expect(injected).toContain('# Command Title\n\n<!-- LEARNING_CONTEXT');
            expect(injected).toContain('Command description');
            expect(injected).toContain('## Usage');
        });

        test('should handle empty context gracefully', () => {
            const original = '# Command\n\nDescription.';
            const context = injector.getEmptyContext();

            const injected = injector.injectContext(original, context);

            expect(injected).toBe(original);
        });

        test('should remove context sections', () => {
            const withContext = `# Command

<!-- LEARNING_CONTEXT: SIMILAR_ISSUES -->
📚 **Recent Similar Executions:**
1. Some execution
<!-- END_LEARNING_CONTEXT -->

Command description.`;

            const removed = injector.removeContext(withContext);

            expect(removed).toBe('# Command\n\nCommand description.');
        });
    });

    describe('Caching', () => {
        test('should cache context results', async () => {
            // Add data
            await store.recordExecution('/fix', { issue: 'bug' }, 'success');

            // First call - should hit database
            const start1 = Date.now();
            await injector.enhanceCommand('/fix', '# /fix\n\nTest', { issue: 'bug' });
            const time1 = Date.now() - start1;

            // Second call - should hit cache
            const start2 = Date.now();
            await injector.enhanceCommand('/fix', '# /fix\n\nTest', { issue: 'bug' });
            const time2 = Date.now() - start2;

            expect(time2).toBeLessThan(time1);
        });

        test('should expire cache after timeout', async () => {
            injector.cacheTimeout = 100; // 100ms for testing

            await store.recordExecution('/fix', {}, 'success');
            
            // First call
            await injector.enhanceCommand('/fix', '# /fix\n\nTest');
            
            // Wait for cache to expire
            await new Promise(resolve => setTimeout(resolve, 150));
            
            // Should not find in cache
            const cacheKey = injector.getCacheKey('/fix', {});
            const cached = injector.getFromCache(cacheKey);
            
            expect(cached).toBeNull();
        });

        test('should limit cache size', () => {
            // Add many cache entries
            for (let i = 0; i < 150; i++) {
                injector.setCache(`key${i}`, { data: i });
            }

            expect(injector.cache.size).toBeLessThanOrEqual(100);
        });
    });

    describe('Performance', () => {
        test('should meet latency requirements', async () => {
            // Add reasonable amount of data
            for (let i = 0; i < 20; i++) {
                await store.recordExecution('/test', { index: i }, 'success', {
                    duration_ms: Math.random() * 10000
                });
            }

            const start = Date.now();
            await injector.enhanceCommand('/test', '# /test\n\nTest command.');
            const duration = Date.now() - start;

            expect(duration).toBeLessThan(200); // Max latency requirement
        });

        test('should handle large datasets efficiently', async () => {
            // Add lots of data
            const promises = [];
            for (let i = 0; i < 100; i++) {
                promises.push(
                    store.recordExecution('/cmd', { i }, 'success')
                );
            }
            await Promise.all(promises);

            // Should still be fast with cache
            const start = Date.now();
            await injector.enhanceCommand('/cmd', '# /cmd\n\nCommand.');
            const duration = Date.now() - start;

            expect(duration).toBeLessThan(300);
        });
    });

    describe('String Similarity', () => {
        test('should calculate Levenshtein distance correctly', () => {
            expect(injector.levenshteinDistance('kitten', 'sitting')).toBe(3);
            expect(injector.levenshteinDistance('saturday', 'sunday')).toBe(3);
            expect(injector.levenshteinDistance('', 'abc')).toBe(3);
            expect(injector.levenshteinDistance('abc', 'abc')).toBe(0);
        });

        test('should calculate string similarity correctly', () => {
            expect(injector.stringSimilarity('hello', 'hello')).toBe(1);
            expect(injector.stringSimilarity('hello', 'hallo')).toBeGreaterThan(0.7);
            expect(injector.stringSimilarity('abc', 'xyz')).toBe(0);
        });
    });

    describe('Time Formatting', () => {
        test('should format time ago correctly', () => {
            const now = new Date();
            
            expect(injector.getTimeAgo(now)).toBe('just now');
            expect(injector.getTimeAgo(new Date(now - 30000))).toBe('just now');
            expect(injector.getTimeAgo(new Date(now - 120000))).toBe('2 minutes ago');
            expect(injector.getTimeAgo(new Date(now - 3600000))).toBe('1 hour ago');
            expect(injector.getTimeAgo(new Date(now - 86400000))).toBe('1 day ago');
        });
    });
});