const { CommandEnhancer, getEnhancer } = require('./command-enhancer');
const fs = require('fs').promises;
const path = require('path');

const TEST_DB_PATH = '.claude/learning/test-command-enhancer.db';
const TEST_COMMANDS_PATH = '.claude/test-commands';

describe('CommandEnhancer', () => {
    let enhancer;
    let commandsCreated = [];

    beforeEach(async () => {
        // Clean up test database
        try {
            await fs.unlink(TEST_DB_PATH);
        } catch (err) {
            // Ignore
        }

        // Create test commands directory
        await fs.mkdir(TEST_COMMANDS_PATH, { recursive: true });

        enhancer = new CommandEnhancer({
            commandsPath: TEST_COMMANDS_PATH,
            dbPath: TEST_DB_PATH
        });

        // Create some test commands
        await createTestCommand('fix', '# /fix\n\nFix issues in the codebase.\n\n## Usage\nDescribe the issue.');
        await createTestCommand('test', '# /test\n\nRun tests.\n\n## Options\n- target: Test target');
        await createTestCommand('commit', '# /commit\n\nCommit changes.\n\n## Process\n1. Stage\n2. Commit');
    });

    afterEach(async () => {
        if (enhancer) {
            await enhancer.close();
        }

        // Clean up test files
        for (const cmd of commandsCreated) {
            try {
                await fs.unlink(path.join(TEST_COMMANDS_PATH, cmd));
            } catch (err) {
                // Ignore
            }
        }

        try {
            await fs.rmdir(TEST_COMMANDS_PATH);
            await fs.unlink(TEST_DB_PATH);
        } catch (err) {
            // Ignore
        }

        commandsCreated = [];
    });

    async function createTestCommand(name, content) {
        const filename = `${name}.md`;
        await fs.writeFile(path.join(TEST_COMMANDS_PATH, filename), content);
        commandsCreated.push(filename);
    }

    describe('Initialization', () => {
        test('should initialize on first use', async () => {
            expect(enhancer.initialized).toBe(false);
            
            await enhancer.enhanceCommand('fix');
            
            expect(enhancer.initialized).toBe(true);
            expect(enhancer.store).toBeDefined();
            expect(enhancer.patterns).toBeDefined();
            expect(enhancer.injector).toBeDefined();
        });

        test('should handle missing command gracefully', async () => {
            const result = await enhancer.enhanceCommand('nonexistent');
            
            expect(result.enhanced).toBe(false);
            expect(result.error).toContain('not found');
            expect(result.content).toContain('Command enhancement failed');
        });
    });

    describe('Command Enhancement', () => {
        test('should enhance command with context', async () => {
            // Add some history
            await enhancer.initialize();
            await enhancer.store.recordExecution('/fix', { bug: 'timeout' }, 'success', {
                duration_ms: 5000
            });

            const result = await enhancer.enhanceCommand('fix', { bug: 'connection' });
            
            expect(result.enhanced).toBe(true);
            expect(result.content).toContain('# /fix');
            expect(result.content).toContain('Recent Similar Executions');
            expect(result.executionId).toBeGreaterThan(0);
        });

        test('should normalize command names', async () => {
            const result1 = await enhancer.enhanceCommand('/fix');
            const result2 = await enhancer.enhanceCommand('fix');
            
            expect(result1.commandName).toBe('fix');
            expect(result2.commandName).toBe('fix');
        });

        test('should cache command content', async () => {
            // First load
            await enhancer.loadCommand('fix');
            expect(enhancer.commandCache.has('fix')).toBe(true);

            // Modify file
            await createTestCommand('fix', '# Modified');
            
            // Should still get cached version
            const content = await enhancer.loadCommand('fix');
            expect(content).toContain('Fix issues');
        });
    });

    describe('Execution Tracking', () => {
        test('should record execution start', async () => {
            await enhancer.initialize();
            
            const result = await enhancer.enhanceCommand('test', { target: 'unit' });
            
            const execution = await enhancer.store.get(
                'SELECT * FROM executions WHERE id = ?',
                [result.executionId]
            );
            
            expect(execution.command).toBe('/test');
            expect(execution.parameters).toBe(JSON.stringify({ target: 'unit' }));
            expect(execution.outcome).toBe('started');
        });

        test('should record execution outcome', async () => {
            await enhancer.initialize();
            
            const result = await enhancer.enhanceCommand('fix');
            await enhancer.recordOutcome(result.executionId, 'success', {
                duration_ms: 3000,
                user_feedback: 'Worked great!'
            });
            
            const execution = await enhancer.store.get(
                'SELECT * FROM executions WHERE id = ?',
                [result.executionId]
            );
            
            expect(execution.outcome).toBe('success');
            expect(execution.duration_ms).toBe(3000);
            expect(execution.user_feedback).toBe('Worked great!');
        });
    });

    describe('Pattern Detection', () => {
        test('should detect patterns after executions', async () => {
            await enhancer.initialize();
            
            // Create a pattern
            const commands = ['/fix', '/test', '/commit'];
            for (let i = 0; i < 3; i++) {
                for (const cmd of commands) {
                    await enhancer.store.recordExecution(cmd, {}, 'success');
                }
            }

            // Mock console.log to capture pattern detection
            const originalLog = console.log;
            let detectedPattern = '';
            console.log = (msg) => {
                if (msg.includes('Pattern detected')) {
                    detectedPattern = msg;
                }
            };

            await enhancer.checkAndRecordPattern();
            
            console.log = originalLog;
            
            expect(detectedPattern).toContain('/fix,/test,/commit');
        });
    });

    describe('Suggestions', () => {
        test('should get command suggestions', async () => {
            await enhancer.initialize();
            
            // Create pattern
            for (let i = 0; i < 5; i++) {
                await enhancer.store.recordPattern('/fix,/test,/commit');
            }

            const suggestions = await enhancer.getSuggestions(['/fix', '/test']);
            
            expect(suggestions.length).toBeGreaterThan(0);
            expect(suggestions[0].nextCommands).toContain('/commit');
        });
    });

    describe('Knowledge Management', () => {
        test('should add knowledge entries', async () => {
            const result = await enhancer.addKnowledge(
                'fix-tip',
                'Always check logs first',
                'debugging'
            );
            
            expect(result).toBe(true);
            
            const knowledge = await enhancer.store.getKnowledge('fix-tip');
            expect(knowledge.value).toBe('Always check logs first');
        });
    });

    describe('Metrics', () => {
        test('should calculate metrics', async () => {
            await enhancer.initialize();
            
            // Add test data
            await enhancer.store.recordExecution('/fix', {}, 'success', { duration_ms: 5000 });
            await enhancer.store.recordExecution('/test', {}, 'success', { duration_ms: 3000 });
            await enhancer.store.recordExecution('/fix', {}, 'failure', { 
                error_message: 'Timeout'
            });
            await enhancer.store.recordPattern('/fix,/test');
            await enhancer.store.addKnowledge('tip', 'helpful hint');

            const metrics = await enhancer.getMetrics('7d');
            
            expect(metrics.summary.totalExecutions).toBe(3);
            expect(metrics.summary.successRate).toBe('66.7%');
            expect(metrics.summary.avgDuration).toBe('4000ms');
            expect(metrics.summary.knowledgeEntries).toBe(1);
            expect(metrics.commands.mostUsed[0].command).toBe('/fix');
            expect(metrics.commands.mostUsed[0].count).toBe(2);
        });

        test('should handle empty metrics gracefully', async () => {
            const metrics = await enhancer.getMetrics('1d');
            
            expect(metrics.summary.totalExecutions).toBe(0);
            expect(metrics.summary.successRate).toBe('N/A');
            expect(metrics.commands.mostUsed).toEqual([]);
        });

        test('should estimate time saved', async () => {
            await enhancer.initialize();
            
            // Add patterns
            for (let i = 0; i < 10; i++) {
                await enhancer.store.recordPattern('/fix,/test,/commit');
            }
            
            const patterns = await enhancer.store.getFrequentPatterns(1);
            const timeSaved = await enhancer.estimateTimeSaved([], patterns);
            
            expect(timeSaved).toContain('hours');
        });
    });

    describe('Data Management', () => {
        test('should export learning data', async () => {
            await enhancer.initialize();
            
            await enhancer.store.recordExecution('/test', {}, 'success');
            await enhancer.store.recordPattern('/test,/commit');
            await enhancer.store.addKnowledge('tip', 'test tip');

            const data = await enhancer.exportLearningData();
            
            expect(data.executions.length).toBe(1);
            expect(data.patterns.length).toBe(1);
            expect(data.knowledge.length).toBe(1);
            expect(data.exportDate).toBeDefined();
        });

        test('should cleanup old data', async () => {
            await enhancer.initialize();
            
            // Add old execution
            const oldDate = new Date();
            oldDate.setDate(oldDate.getDate() - 100);
            
            await enhancer.store.recordExecution('/old', {}, 'success');
            await enhancer.store.run(
                'UPDATE executions SET timestamp = ? WHERE command = ?',
                [oldDate.toISOString(), '/old']
            );
            
            // Add recent execution
            await enhancer.store.recordExecution('/recent', {}, 'success');
            
            await enhancer.cleanup(90);
            
            const executions = await enhancer.store.all('SELECT * FROM executions');
            expect(executions.length).toBe(1);
            expect(executions[0].command).toBe('/recent');
        });
    });

    describe('Singleton Pattern', () => {
        test('should return same instance', () => {
            const instance1 = getEnhancer({ dbPath: 'test1.db' });
            const instance2 = getEnhancer({ dbPath: 'test2.db' });
            
            expect(instance1).toBe(instance2);
            // Note: Options are only used on first call
        });
    });

    describe('Error Handling', () => {
        test('should handle store errors gracefully', async () => {
            await enhancer.initialize();
            await enhancer.store.close();
            
            // Should not throw
            const result = await enhancer.enhanceCommand('fix');
            expect(result.enhanced).toBe(false);
        });

        test('should handle missing command file', async () => {
            const result = await enhancer.loadCommand('missing');
            expect(result).toBeNull();
        });
    });
});