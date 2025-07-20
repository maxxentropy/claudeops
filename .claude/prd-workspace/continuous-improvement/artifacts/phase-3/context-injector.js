const LearningStore = require('../phase-1/learning-store');
const PatternRecognizer = require('../phase-2/pattern-recognizer');

class ContextInjector {
    constructor(learningStore, patternRecognizer) {
        if (!learningStore || !patternRecognizer) {
            throw new Error('LearningStore and PatternRecognizer instances are required');
        }
        
        this.store = learningStore;
        this.patterns = patternRecognizer;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
        this.maxContextItems = 5;
        this.maxLatency = 200; // ms
    }

    /**
     * Enhance a command with relevant context
     */
    async enhanceCommand(commandName, originalContent, parameters = {}) {
        const startTime = Date.now();
        
        try {
            // Check cache first
            const cacheKey = this.getCacheKey(commandName, parameters);
            const cached = this.getFromCache(cacheKey);
            if (cached) {
                return this.injectContext(originalContent, cached);
            }

            // Gather context with timeout
            const contextPromise = this.gatherContext(commandName, parameters);
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Context timeout')), this.maxLatency)
            );

            const context = await Promise.race([contextPromise, timeoutPromise])
                .catch(err => {
                    console.warn(`Context gathering failed: ${err.message}`);
                    return this.getEmptyContext();
                });

            // Cache the context
            this.setCache(cacheKey, context);

            // Inject into command
            return this.injectContext(originalContent, context);

        } catch (error) {
            console.error('Context injection failed:', error);
            // Fallback to original content
            return originalContent;
        } finally {
            const duration = Date.now() - startTime;
            if (duration > this.maxLatency) {
                console.warn(`Context injection took ${duration}ms (limit: ${this.maxLatency}ms)`);
            }
        }
    }

    /**
     * Gather all relevant context for a command
     */
    async gatherContext(commandName, parameters) {
        const [history, patterns, knowledge, suggestions] = await Promise.all([
            this.getRelevantHistory(commandName, parameters),
            this.getRelevantPatterns(commandName),
            this.getRelevantKnowledge(commandName, parameters),
            this.getCommandSuggestions(commandName)
        ]);

        return {
            history,
            patterns,
            knowledge,
            suggestions,
            timestamp: new Date()
        };
    }

    /**
     * Get relevant execution history
     */
    async getRelevantHistory(commandName, parameters) {
        try {
            // Get recent executions of this command
            const recentExecutions = await this.store.getRecentExecutions(commandName, 20);
            
            // If parameters provided, find similar ones
            let relevantExecutions = recentExecutions;
            if (parameters && Object.keys(parameters).length > 0) {
                relevantExecutions = await this.findSimilarExecutions(recentExecutions, parameters);
            }

            // Format for display
            return relevantExecutions
                .slice(0, this.maxContextItems)
                .map(exec => this.formatExecution(exec));
        } catch (error) {
            console.error('Failed to get history:', error);
            return [];
        }
    }

    /**
     * Find executions with similar parameters
     */
    async findSimilarExecutions(executions, targetParams) {
        const scored = executions.map(exec => {
            const score = this.calculateParameterSimilarity(exec.parameters, targetParams);
            return { exec, score };
        });

        return scored
            .sort((a, b) => b.score - a.score)
            .filter(item => item.score > 0.3)
            .map(item => item.exec);
    }

    /**
     * Calculate similarity between parameter sets
     */
    calculateParameterSimilarity(params1, params2) {
        if (!params1 || !params2) return 0;

        const p1 = typeof params1 === 'string' ? JSON.parse(params1) : params1;
        const p2 = params2;

        const keys1 = Object.keys(p1);
        const keys2 = Object.keys(p2);
        const allKeys = new Set([...keys1, ...keys2]);

        let matches = 0;
        for (const key of allKeys) {
            if (p1[key] === p2[key]) {
                matches++;
            } else if (typeof p1[key] === 'string' && typeof p2[key] === 'string') {
                // Partial string matching
                const similarity = this.stringSimilarity(p1[key], p2[key]);
                matches += similarity;
            }
        }

        return matches / allKeys.size;
    }

    /**
     * Simple string similarity calculation
     */
    stringSimilarity(str1, str2) {
        const longer = str1.length > str2.length ? str1 : str2;
        const shorter = str1.length > str2.length ? str2 : str1;
        
        if (longer.length === 0) return 1.0;
        
        const editDistance = this.levenshteinDistance(longer, shorter);
        return (longer.length - editDistance) / longer.length;
    }

    /**
     * Levenshtein distance for string comparison
     */
    levenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }

    /**
     * Format execution for display
     */
    formatExecution(exec) {
        const timeAgo = this.getTimeAgo(new Date(exec.timestamp));
        const duration = exec.duration_ms ? `${Math.round(exec.duration_ms / 1000)}s` : 'unknown';
        const outcome = exec.outcome === 'success' ? '✓' : '✗';
        
        let description = `${outcome} ${exec.command}`;
        if (exec.parameters) {
            const params = typeof exec.parameters === 'string' 
                ? JSON.parse(exec.parameters) 
                : exec.parameters;
            const paramStr = Object.entries(params)
                .map(([k, v]) => `${k}: ${v}`)
                .join(', ');
            description += ` (${paramStr})`;
        }
        
        if (exec.error_message) {
            description += ` - Error: ${exec.error_message}`;
        }
        
        return `${description} - ${timeAgo}, ${duration}`;
    }

    /**
     * Get human-readable time ago
     */
    getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60
        };
        
        for (const [unit, secondsInUnit] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / secondsInUnit);
            if (interval >= 1) {
                return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
            }
        }
        
        return 'just now';
    }

    /**
     * Get relevant patterns
     */
    async getRelevantPatterns(commandName) {
        try {
            const allPatterns = await this.store.getFrequentPatterns(2);
            
            // Filter patterns that include this command
            const relevantPatterns = allPatterns.filter(pattern => 
                pattern.pattern_sequence.includes(commandName)
            );

            return relevantPatterns
                .slice(0, 3)
                .map(pattern => ({
                    sequence: pattern.pattern_sequence,
                    frequency: pattern.frequency,
                    suggestion: pattern.suggested_command
                }));
        } catch (error) {
            console.error('Failed to get patterns:', error);
            return [];
        }
    }

    /**
     * Get relevant knowledge entries
     */
    async getRelevantKnowledge(commandName, parameters) {
        try {
            const searchTerms = [commandName];
            
            // Add parameter values as search terms
            if (parameters) {
                Object.values(parameters).forEach(value => {
                    if (typeof value === 'string' && value.length > 2) {
                        searchTerms.push(value);
                    }
                });
            }

            const knowledgeEntries = [];
            for (const term of searchTerms) {
                const results = await this.store.searchKnowledge(term);
                knowledgeEntries.push(...results);
            }

            // Deduplicate and sort by usage
            const unique = Array.from(
                new Map(knowledgeEntries.map(k => [k.key, k])).values()
            );

            return unique
                .sort((a, b) => b.usage_count - a.usage_count)
                .slice(0, 3)
                .map(k => ({
                    key: k.key,
                    value: k.value,
                    category: k.category
                }));
        } catch (error) {
            console.error('Failed to get knowledge:', error);
            return [];
        }
    }

    /**
     * Get command suggestions based on current context
     */
    async getCommandSuggestions(commandName) {
        try {
            const recentCommands = await this.store.getRecentExecutions(null, 5);
            const recentCommandNames = recentCommands.map(e => e.command);
            
            const suggestions = await this.patterns.suggestCommands({
                recentCommands: recentCommandNames.slice(1), // Exclude current
                currentCommand: commandName
            });

            return suggestions.slice(0, 2);
        } catch (error) {
            console.error('Failed to get suggestions:', error);
            return [];
        }
    }

    /**
     * Inject context into command content
     */
    injectContext(originalContent, context) {
        let enhanced = originalContent;

        // Find injection point (after first heading)
        const firstHeadingMatch = enhanced.match(/^#[^#\n]+\n/m);
        const injectionPoint = firstHeadingMatch 
            ? firstHeadingMatch.index + firstHeadingMatch[0].length 
            : 0;

        // Build context sections
        const contextSections = [];

        // Add history section
        if (context.history && context.history.length > 0) {
            contextSections.push(
                '<!-- LEARNING_CONTEXT: SIMILAR_ISSUES -->',
                '📚 **Recent Similar Executions:**',
                ...context.history.map((h, i) => `${i + 1}. ${h}`),
                '<!-- END_LEARNING_CONTEXT -->\n'
            );
        }

        // Add knowledge section
        if (context.knowledge && context.knowledge.length > 0) {
            contextSections.push(
                '<!-- LEARNING_CONTEXT: TEAM_KNOWLEDGE -->',
                '💡 **Team Knowledge:**',
                ...context.knowledge.map(k => `- **${k.key}**: ${k.value}`),
                '<!-- END_LEARNING_CONTEXT -->\n'
            );
        }

        // Add patterns section
        if (context.patterns && context.patterns.length > 0) {
            contextSections.push(
                '<!-- LEARNING_CONTEXT: COMMON_PATTERNS -->',
                '🔄 **Common Patterns:**',
                ...context.patterns.map(p => 
                    `- \`${p.sequence}\` (used ${p.frequency} times)`
                ),
                '<!-- END_LEARNING_CONTEXT -->\n'
            );
        }

        // Add suggestions section
        if (context.suggestions && context.suggestions.length > 0) {
            contextSections.push(
                '<!-- LEARNING_CONTEXT: NEXT_SUGGESTIONS -->',
                '➡️ **Likely Next Commands:**',
                ...context.suggestions.map(s => 
                    `- \`${s.nextCommands.join(' → ')}\` (${Math.round(s.confidence * 100)}% confidence)`
                ),
                '<!-- END_LEARNING_CONTEXT -->\n'
            );
        }

        // Inject context at the appropriate point
        if (contextSections.length > 0) {
            const contextBlock = '\n' + contextSections.join('\n') + '\n';
            enhanced = enhanced.slice(0, injectionPoint) + 
                      contextBlock + 
                      enhanced.slice(injectionPoint);
        }

        return enhanced;
    }

    /**
     * Cache management
     */
    getCacheKey(commandName, parameters) {
        const paramStr = parameters ? JSON.stringify(parameters) : '';
        return `${commandName}:${paramStr}`;
    }

    getFromCache(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;

        const age = Date.now() - cached.timestamp;
        if (age > this.cacheTimeout) {
            this.cache.delete(key);
            return null;
        }

        return cached.data;
    }

    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });

        // Limit cache size
        if (this.cache.size > 100) {
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
        }
    }

    clearCache() {
        this.cache.clear();
    }

    /**
     * Get empty context for fallback
     */
    getEmptyContext() {
        return {
            history: [],
            patterns: [],
            knowledge: [],
            suggestions: [],
            timestamp: new Date()
        };
    }

    /**
     * Remove injected context from content (for testing)
     */
    removeContext(content) {
        return content.replace(
            /<!-- LEARNING_CONTEXT:[\s\S]*?<!-- END_LEARNING_CONTEXT -->\n\n/g,
            ''
        );
    }
}

module.exports = ContextInjector;