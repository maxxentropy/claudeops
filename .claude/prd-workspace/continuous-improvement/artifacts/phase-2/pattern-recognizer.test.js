const PatternRecognizer = require('./pattern-recognizer');
const LearningStore = require('../phase-1/learning-store');
const fs = require('fs').promises;

// Test database path
const TEST_DB_PATH = '.claude/learning/test-pattern-recognizer.db';

describe('PatternRecognizer', () => {
    let store;
    let recognizer;

    beforeEach(async () => {
        // Clean up any existing test database
        try {
            await fs.unlink(TEST_DB_PATH);
        } catch (err) {
            // File doesn't exist, which is fine
        }
        
        store = new LearningStore(TEST_DB_PATH);
        await store.initialize();
        recognizer = new PatternRecognizer(store);
    });

    afterEach(async () => {
        if (store) {
            await store.close();
        }
        try {
            await fs.unlink(TEST_DB_PATH);
        } catch (err) {
            // Ignore errors
        }
    });

    describe('Constructor', () => {
        test('should require a LearningStore instance', () => {
            expect(() => new PatternRecognizer()).toThrow('LearningStore instance is required');
        });

        test('should initialize with default settings', () => {
            expect(recognizer.minPatternLength).toBe(2);
            expect(recognizer.minFrequency).toBe(3);
            expect(recognizer.maxPatternLength).toBe(5);
            expect(recognizer.sessionTimeoutMs).toBe(30 * 60 * 1000);
        });
    });

    describe('Session Grouping', () => {
        test('should group executions into sessions based on time gaps', () => {
            const now = new Date();
            const executions = [
                { command: '/fix', timestamp: new Date(now - 60000) },  // 1 min ago
                { command: '/test', timestamp: new Date(now - 30000) }, // 30 sec ago
                { command: '/commit', timestamp: new Date(now) },        // now
                { command: '/fix', timestamp: new Date(now + 3600000) }, // 1 hour later
                { command: '/test', timestamp: new Date(now + 3630000) } // 1 hour 30 sec later
            ];

            const sessions = recognizer.groupIntoSessions(executions);
            
            expect(sessions).toHaveLength(2);
            expect(sessions[0]).toHaveLength(3); // First session
            expect(sessions[1]).toHaveLength(2); // Second session
        });

        test('should filter out single-command sessions', () => {
            const now = new Date();
            const executions = [
                { command: '/fix', timestamp: new Date(now) },
                { command: '/test', timestamp: new Date(now + 3600000) }, // 1 hour later
                { command: '/commit', timestamp: new Date(now + 7200000) } // 2 hours later
            ];

            const sessions = recognizer.groupIntoSessions(executions);
            expect(sessions).toHaveLength(0); // All are single commands
        });
    });

    describe('Pattern Detection', () => {
        test('should detect sequential patterns', async () => {
            // Create a pattern that occurs 3 times
            const pattern = ['/fix', '/test', '/commit'];
            const now = Date.now();

            for (let i = 0; i < 3; i++) {
                const baseTime = now + (i * 3600000); // Each session 1 hour apart
                for (let j = 0; j < pattern.length; j++) {
                    await store.recordExecution(
                        pattern[j],
                        { session: i },
                        'success',
                        { duration_ms: 1000 }
                    );
                    // Small delay to ensure order
                    await new Promise(resolve => setTimeout(resolve, 10));
                }
            }

            const patterns = await recognizer.detectPatterns('1d');
            
            expect(patterns.length).toBeGreaterThan(0);
            const mainPattern = patterns.find(p => p.sequence === '/fix,/test,/commit');
            expect(mainPattern).toBeDefined();
            expect(mainPattern.count).toBe(3);
        });

        test('should identify interesting patterns only', () => {
            const executions = [
                { command: '/fix' },
                { command: '/fix' },
                { command: '/fix' }
            ];

            expect(recognizer.isInterestingPattern(executions)).toBe(false);

            const mixedExecutions = [
                { command: '/fix' },
                { command: '/test' },
                { command: '/commit' }
            ];

            expect(recognizer.isInterestingPattern(mixedExecutions)).toBe(true);
        });

        test('should not consider alternating patterns as interesting', () => {
            const alternating = [
                { command: '/fix' },
                { command: '/test' },
                { command: '/fix' },
                { command: '/test' }
            ];

            expect(recognizer.isInterestingPattern(alternating)).toBe(false);
        });
    });

    describe('Metadata Extraction', () => {
        test('should calculate success rate correctly', () => {
            const executions = [
                { outcome: 'success' },
                { outcome: 'success' },
                { outcome: 'failure' },
                { outcome: 'success' }
            ];

            const metadata = recognizer.extractMetadata(executions);
            expect(metadata.successRate).toBe(0.75);
        });

        test('should calculate average duration', () => {
            const executions = [
                { duration_ms: 1000 },
                { duration_ms: 2000 },
                { duration_ms: 3000 }
            ];

            const metadata = recognizer.extractMetadata(executions);
            expect(metadata.averageDuration).toBe(2000);
        });

        test('should find common parameters', () => {
            const executions = [
                { parameters: JSON.stringify({ file: 'auth.js', type: 'bug' }) },
                { parameters: JSON.stringify({ file: 'auth.js', type: 'feature' }) },
                { parameters: JSON.stringify({ file: 'auth.js', type: 'bug' }) }
            ];

            const metadata = recognizer.extractMetadata(executions);
            expect(metadata.commonParameters).toContain('file:auth.js');
        });

        test('should extract common error keywords', () => {
            const executions = [
                { outcome: 'failure', error_message: 'Connection timeout error' },
                { outcome: 'failure', error_message: 'Database connection failed' },
                { outcome: 'success' }
            ];

            const metadata = recognizer.extractMetadata(executions);
            expect(metadata.commonErrors).toContain('connection');
        });
    });

    describe('Pattern Scoring', () => {
        test('should score patterns based on frequency and success', () => {
            const pattern1 = {
                count: 5,
                commands: ['/fix', '/test', '/commit'],
                instances: [
                    { metadata: { successRate: 1.0 } },
                    { metadata: { successRate: 0.8 } }
                ]
            };

            const pattern2 = {
                count: 3,
                commands: ['/fix', '/commit'],
                instances: [
                    { metadata: { successRate: 0.5 } }
                ]
            };

            const score1 = recognizer.calculatePatternScore(pattern1);
            const score2 = recognizer.calculatePatternScore(pattern2);

            expect(score1).toBeGreaterThan(score2);
        });
    });

    describe('Command Suggestions', () => {
        test('should suggest next commands based on pattern', async () => {
            // Create a pattern
            await store.recordPattern('/fix,/test,/commit');
            await store.recordPattern('/fix,/test,/commit');
            await store.recordPattern('/fix,/test,/commit');

            const context = {
                recentCommands: ['/fix'],
                currentCommand: '/test'
            };

            const suggestions = await recognizer.suggestCommands(context);
            
            expect(suggestions.length).toBeGreaterThan(0);
            expect(suggestions[0].nextCommands).toContain('/commit');
        });

        test('should match context correctly', () => {
            const pattern = ['/fix', '/test', '/commit'];
            const context1 = ['/fix', '/test'];
            const context2 = ['/test', '/commit'];

            expect(recognizer.matchesContext(pattern, context1)).toBe(true);
            expect(recognizer.matchesContext(pattern, context2)).toBe(false);
        });

        test('should calculate confidence based on frequency', async () => {
            const pattern = {
                pattern_sequence: '/fix,/test',
                frequency: 10,
                last_seen: new Date()
            };

            const confidence = recognizer.calculateConfidence(pattern, ['/fix']);
            expect(confidence).toBeGreaterThan(0.5);
            expect(confidence).toBeLessThanOrEqual(0.95);
        });
    });

    describe('Real-time Pattern Checking', () => {
        test('should detect known patterns in real-time', async () => {
            // Create a known pattern
            for (let i = 0; i < 3; i++) {
                await store.recordPattern('/fix,/test,/commit');
            }

            const result = await recognizer.checkForPattern(['/fix', '/test', '/commit']);
            
            expect(result).not.toBeNull();
            expect(result.pattern).toBe('/fix,/test,/commit');
            expect(result.frequency).toBe(3);
        });

        test('should return null for unknown patterns', async () => {
            const result = await recognizer.checkForPattern(['/unknown', '/pattern']);
            expect(result).toBeNull();
        });
    });

    describe('Pattern Insights', () => {
        test('should find error patterns', async () => {
            // Create error pattern
            await store.recordExecution('/setup', {}, 'success');
            await store.recordExecution('/deploy', {}, 'failure', { error_message: 'Config missing' });
            await store.recordExecution('/setup', {}, 'success');
            await store.recordExecution('/deploy', {}, 'failure', { error_message: 'Config invalid' });

            const executions = await store.getExecutionsInWindow('1d');
            const errorPatterns = await recognizer.findErrorPatterns(executions);
            
            expect(errorPatterns.length).toBeGreaterThan(0);
            expect(errorPatterns[0].pattern).toBe('/setup → /deploy');
            expect(errorPatterns[0].count).toBe(2);
        });

        test('should find time-based patterns', async () => {
            // Create time-based pattern (always run /backup at hour 2)
            const date = new Date();
            date.setHours(2);
            
            for (let i = 0; i < 5; i++) {
                await store.recordExecution('/backup', { day: i }, 'success');
                // Manipulate timestamp (this is a hack for testing)
                await store.run(
                    `UPDATE executions SET timestamp = ? WHERE id = last_insert_rowid()`,
                    [date.toISOString()]
                );
            }

            const executions = await store.getExecutionsInWindow('7d');
            const timePatterns = await recognizer.findTimeBasedPatterns(executions);
            
            expect(timePatterns.peakHours.length).toBeGreaterThan(0);
            expect(timePatterns.peakHours[0].command).toBe('/backup');
            expect(timePatterns.peakHours[0].hour).toBe(2);
        });
    });

    describe('Performance', () => {
        test('should handle large datasets efficiently', async () => {
            // Create many executions
            const commands = ['/fix', '/test', '/build', '/deploy', '/commit'];
            
            for (let i = 0; i < 500; i++) {
                const command = commands[i % commands.length];
                await store.recordExecution(command, { index: i }, 'success');
            }

            const startTime = Date.now();
            const patterns = await recognizer.detectPatterns('1d');
            const duration = Date.now() - startTime;
            
            expect(duration).toBeLessThan(5000); // Should complete in under 5 seconds
            expect(patterns).toBeDefined();
        });

        test('should generate suggestions quickly', async () => {
            // Create patterns
            for (let i = 0; i < 10; i++) {
                await store.recordPattern(`/cmd${i},/cmd${i+1},/cmd${i+2}`);
            }

            const startTime = Date.now();
            const suggestions = await recognizer.suggestCommands({
                recentCommands: ['/cmd1', '/cmd2']
            });
            const duration = Date.now() - startTime;
            
            expect(duration).toBeLessThan(100); // Should be very fast
        });
    });

    describe('Edge Cases', () => {
        test('should handle empty execution history', async () => {
            const patterns = await recognizer.detectPatterns('1d');
            expect(patterns).toEqual([]);
        });

        test('should handle malformed parameters gracefully', () => {
            const executions = [
                { parameters: 'invalid json' },
                { parameters: null },
                { parameters: JSON.stringify({ valid: 'json' }) }
            ];

            expect(() => recognizer.extractMetadata(executions)).not.toThrow();
        });

        test('should handle patterns with no duration data', () => {
            const executions = [
                { outcome: 'success' },
                { outcome: 'success' }
            ];

            const metadata = recognizer.extractMetadata(executions);
            expect(metadata.averageDuration).toBeNull();
        });
    });
});