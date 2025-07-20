const fs = require('fs').promises;
const path = require('path');
const ContextInjector = require('./context-injector');
const LearningStore = require('../phase-1/learning-store');
const PatternRecognizer = require('../phase-2/pattern-recognizer');

class CommandEnhancer {
    constructor(options = {}) {
        this.commandsPath = options.commandsPath || '.claude';
        this.learningDbPath = options.dbPath || '.claude/learning/claude-learning.db';
        this.initialized = false;
        this.store = null;
        this.patterns = null;
        this.injector = null;
        this.commandCache = new Map();
    }

    /**
     * Initialize the command enhancer
     */
    async initialize() {
        if (this.initialized) return;

        // Initialize components
        this.store = new LearningStore(this.learningDbPath);
        await this.store.initialize();
        
        this.patterns = new PatternRecognizer(this.store);
        this.injector = new ContextInjector(this.store, this.patterns);
        
        this.initialized = true;
    }

    /**
     * Enhance a command file with learning context
     */
    async enhanceCommand(commandName, parameters = {}) {
        if (!this.initialized) {
            await this.initialize();
        }

        try {
            // Normalize command name (remove leading slash if present)
            const normalizedName = commandName.startsWith('/') 
                ? commandName.slice(1) 
                : commandName;

            // Get command content
            const commandContent = await this.loadCommand(normalizedName);
            if (!commandContent) {
                throw new Error(`Command ${normalizedName} not found`);
            }

            // Record execution start
            const executionId = await this.store.recordExecution(
                `/${normalizedName}`,
                parameters,
                'started',
                { timestamp: new Date() }
            );

            // Enhance with context
            const enhanced = await this.injector.enhanceCommand(
                `/${normalizedName}`,
                commandContent,
                parameters
            );

            // Return enhanced command with execution tracking
            return {
                content: enhanced,
                executionId,
                commandName: normalizedName,
                enhanced: true
            };

        } catch (error) {
            console.error(`Failed to enhance command ${commandName}:`, error);
            // Fallback to original command
            const original = await this.loadCommand(commandName);
            return {
                content: original || `# ${commandName}\n\nCommand enhancement failed.`,
                executionId: null,
                commandName,
                enhanced: false,
                error: error.message
            };
        }
    }

    /**
     * Load command content from file
     */
    async loadCommand(commandName) {
        // Check cache first
        if (this.commandCache.has(commandName)) {
            return this.commandCache.get(commandName);
        }

        try {
            const filePath = path.join(this.commandsPath, `${commandName}.md`);
            const content = await fs.readFile(filePath, 'utf-8');
            
            // Cache for future use
            this.commandCache.set(commandName, content);
            
            return content;
        } catch (error) {
            if (error.code === 'ENOENT') {
                return null;
            }
            throw error;
        }
    }

    /**
     * Record command execution outcome
     */
    async recordOutcome(executionId, outcome, options = {}) {
        if (!executionId || !this.store) return;

        try {
            const { duration_ms, error_message, user_feedback } = options;
            
            // Update the execution record
            await this.store.run(
                `UPDATE executions 
                 SET outcome = ?, duration_ms = ?, error_message = ?, user_feedback = ?
                 WHERE id = ?`,
                [outcome, duration_ms, error_message, user_feedback, executionId]
            );

            // If this completes a pattern, record it
            await this.checkAndRecordPattern();

        } catch (error) {
            console.error('Failed to record outcome:', error);
        }
    }

    /**
     * Check recent executions for patterns
     */
    async checkAndRecordPattern() {
        try {
            const recentExecutions = await this.store.getRecentExecutions(null, 10);
            const recentCommands = recentExecutions
                .filter(e => e.outcome === 'success')
                .map(e => e.command)
                .slice(0, 5);

            if (recentCommands.length >= 2) {
                const pattern = await this.patterns.checkForPattern(recentCommands);
                if (pattern && pattern.suggestion) {
                    console.log(`Pattern detected: ${pattern.pattern}`);
                    console.log(`Suggestion: Create ${pattern.suggestion.name}`);
                }
            }
        } catch (error) {
            console.error('Failed to check pattern:', error);
        }
    }

    /**
     * Get command suggestions for current context
     */
    async getSuggestions(recentCommands = []) {
        if (!this.initialized) {
            await this.initialize();
        }

        try {
            return await this.patterns.suggestCommands({
                recentCommands,
                currentCommand: recentCommands[recentCommands.length - 1]
            });
        } catch (error) {
            console.error('Failed to get suggestions:', error);
            return [];
        }
    }

    /**
     * Add knowledge entry
     */
    async addKnowledge(key, value, category = null) {
        if (!this.initialized) {
            await this.initialize();
        }

        return await this.store.addKnowledge(key, value, category);
    }

    /**
     * Get metrics for dashboard
     */
    async getMetrics(timeframe = '30d') {
        if (!this.initialized) {
            await this.initialize();
        }

        try {
            const executions = await this.store.getExecutionsInWindow(timeframe);
            const patterns = await this.store.getFrequentPatterns(3);
            const knowledge = await this.store.all('SELECT COUNT(*) as count FROM knowledge');

            // Calculate metrics
            const totalExecutions = executions.length;
            const successfulExecutions = executions.filter(e => e.outcome === 'success').length;
            const avgDuration = executions
                .filter(e => e.duration_ms)
                .reduce((sum, e) => sum + e.duration_ms, 0) / 
                executions.filter(e => e.duration_ms).length || 0;

            // Command frequency
            const commandCounts = {};
            executions.forEach(e => {
                commandCounts[e.command] = (commandCounts[e.command] || 0) + 1;
            });

            const mostUsedCommands = Object.entries(commandCounts)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([command, count]) => ({ command, count }));

            // Pattern insights
            const patternInsights = await this.patterns.getPatternInsights();

            return {
                summary: {
                    totalExecutions,
                    successRate: totalExecutions > 0 
                        ? (successfulExecutions / totalExecutions * 100).toFixed(1) + '%'
                        : 'N/A',
                    avgDuration: avgDuration ? Math.round(avgDuration) + 'ms' : 'N/A',
                    patternsDetected: patterns.length,
                    knowledgeEntries: knowledge[0].count
                },
                commands: {
                    mostUsed: mostUsedCommands,
                    recentFailures: executions
                        .filter(e => e.outcome === 'failure')
                        .slice(0, 5)
                        .map(e => ({
                            command: e.command,
                            error: e.error_message,
                            timestamp: e.timestamp
                        }))
                },
                patterns: {
                    frequent: patterns.slice(0, 5),
                    errorProne: patternInsights.errorPatterns.slice(0, 3),
                    suggestions: patternInsights.recommendations.slice(0, 3)
                },
                learning: {
                    contextHitRate: await this.calculateContextHitRate(executions),
                    timeSaved: await this.estimateTimeSaved(executions, patterns)
                }
            };
        } catch (error) {
            console.error('Failed to calculate metrics:', error);
            return null;
        }
    }

    /**
     * Calculate how often context was helpful
     */
    async calculateContextHitRate(executions) {
        // This is a simplified calculation
        // In reality, we'd track when users actually used suggested context
        const successfulWithContext = executions.filter(e => 
            e.outcome === 'success' && e.duration_ms < 30000
        ).length;
        
        return executions.length > 0
            ? Math.round(successfulWithContext / executions.length * 100) + '%'
            : 'N/A';
    }

    /**
     * Estimate time saved through patterns and suggestions
     */
    async estimateTimeSaved(executions, patterns) {
        // Calculate average time saved per pattern use
        const patternCount = patterns.reduce((sum, p) => sum + p.frequency, 0);
        const avgTimeSaved = 5 * 60 * 1000; // Assume 5 minutes saved per pattern use
        
        const totalSaved = patternCount * avgTimeSaved;
        const hours = Math.round(totalSaved / (1000 * 60 * 60));
        
        return `${hours} hours`;
    }

    /**
     * Export learning data
     */
    async exportLearningData() {
        if (!this.initialized) {
            await this.initialize();
        }

        const data = {
            executions: await this.store.all('SELECT * FROM executions'),
            patterns: await this.store.all('SELECT * FROM patterns'),
            knowledge: await this.store.all('SELECT * FROM knowledge'),
            exportDate: new Date().toISOString()
        };

        return data;
    }

    /**
     * Import learning data
     */
    async importLearningData(data) {
        if (!this.initialized) {
            await this.initialize();
        }

        // This would need proper conflict resolution and data validation
        // For now, it's a placeholder
        console.log('Import functionality not yet implemented');
        return false;
    }

    /**
     * Clear old data
     */
    async cleanup(olderThanDays = 90) {
        if (!this.initialized) {
            await this.initialize();
        }

        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);

        await this.store.run(
            'DELETE FROM executions WHERE timestamp < ?',
            [cutoffDate.toISOString()]
        );

        // Update pattern frequencies based on remaining data
        await this.patterns.detectPatterns(`${olderThanDays}d`);
    }

    /**
     * Close connections
     */
    async close() {
        if (this.store) {
            await this.store.close();
        }
        this.initialized = false;
    }
}

// Singleton instance for slash command integration
let enhancerInstance = null;

/**
 * Get or create the command enhancer instance
 */
function getEnhancer(options) {
    if (!enhancerInstance) {
        enhancerInstance = new CommandEnhancer(options);
    }
    return enhancerInstance;
}

module.exports = {
    CommandEnhancer,
    getEnhancer
};