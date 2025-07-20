const LearningStore = require('../phase-1/learning-store');

class PatternRecognizer {
    constructor(learningStore) {
        if (!learningStore) {
            throw new Error('LearningStore instance is required');
        }
        this.store = learningStore;
        this.minPatternLength = 2;
        this.minFrequency = 3;
        this.maxPatternLength = 5;
        this.sessionTimeoutMs = 30 * 60 * 1000; // 30 minutes
    }

    /**
     * Detect command sequence patterns from execution history
     */
    async detectPatterns(timeWindow = '7d') {
        const executions = await this.store.getExecutionsInWindow(timeWindow);
        const sessions = this.groupIntoSessions(executions);
        const sequences = this.extractSequences(sessions);
        const patterns = await this.analyzeSequences(sequences);
        
        // Store detected patterns
        for (const pattern of patterns) {
            await this.store.recordPattern(pattern.sequence);
        }
        
        return patterns;
    }

    /**
     * Group executions into sessions based on time gaps
     */
    groupIntoSessions(executions) {
        if (!executions || executions.length === 0) {
            return [];
        }

        const sessions = [];
        let currentSession = [executions[0]];

        for (let i = 1; i < executions.length; i++) {
            const prevTime = new Date(executions[i - 1].timestamp);
            const currTime = new Date(executions[i].timestamp);
            const timeDiff = currTime - prevTime;

            if (timeDiff <= this.sessionTimeoutMs) {
                currentSession.push(executions[i]);
            } else {
                if (currentSession.length >= this.minPatternLength) {
                    sessions.push(currentSession);
                }
                currentSession = [executions[i]];
            }
        }

        if (currentSession.length >= this.minPatternLength) {
            sessions.push(currentSession);
        }

        return sessions;
    }

    /**
     * Extract command sequences from sessions
     */
    extractSequences(sessions) {
        const sequences = [];

        for (const session of sessions) {
            // Extract all possible subsequences
            for (let length = this.minPatternLength; length <= Math.min(this.maxPatternLength, session.length); length++) {
                for (let start = 0; start <= session.length - length; start++) {
                    const subsequence = session.slice(start, start + length);
                    const commands = subsequence.map(exec => exec.command);
                    
                    // Check if this is an interesting pattern
                    if (this.isInterestingPattern(subsequence)) {
                        sequences.push({
                            commands: commands,
                            sequence: commands.join(','),
                            executions: subsequence,
                            metadata: this.extractMetadata(subsequence)
                        });
                    }
                }
            }
        }

        return sequences;
    }

    /**
     * Determine if a sequence is interesting (not all the same command, etc.)
     */
    isInterestingPattern(executions) {
        const commands = executions.map(e => e.command);
        
        // Not interesting if all commands are the same
        const uniqueCommands = new Set(commands);
        if (uniqueCommands.size === 1) {
            return false;
        }

        // Not interesting if it's just back-and-forth between two commands
        if (commands.length >= 4 && uniqueCommands.size === 2) {
            const [cmd1, cmd2] = Array.from(uniqueCommands);
            const isAlternating = commands.every((cmd, i) => 
                cmd === (i % 2 === 0 ? cmd1 : cmd2)
            );
            if (isAlternating) {
                return false;
            }
        }

        return true;
    }

    /**
     * Extract metadata about the pattern
     */
    extractMetadata(executions) {
        const outcomes = executions.map(e => e.outcome);
        const durations = executions
            .map(e => e.duration_ms)
            .filter(d => d != null);

        return {
            successRate: outcomes.filter(o => o === 'success').length / outcomes.length,
            averageDuration: durations.length > 0 
                ? durations.reduce((a, b) => a + b, 0) / durations.length 
                : null,
            commonParameters: this.findCommonParameters(executions),
            commonErrors: this.findCommonErrors(executions)
        };
    }

    /**
     * Find common parameters across executions
     */
    findCommonParameters(executions) {
        const paramCounts = {};
        
        for (const exec of executions) {
            if (exec.parameters) {
                const params = typeof exec.parameters === 'string' 
                    ? JSON.parse(exec.parameters) 
                    : exec.parameters;
                
                for (const [key, value] of Object.entries(params)) {
                    const paramKey = `${key}:${value}`;
                    paramCounts[paramKey] = (paramCounts[paramKey] || 0) + 1;
                }
            }
        }

        return Object.entries(paramCounts)
            .filter(([_, count]) => count >= executions.length * 0.5)
            .map(([param]) => param);
    }

    /**
     * Find common errors in failed executions
     */
    findCommonErrors(executions) {
        const errors = executions
            .filter(e => e.outcome === 'failure' && e.error_message)
            .map(e => e.error_message);

        const errorCounts = {};
        for (const error of errors) {
            // Simple keyword extraction
            const keywords = error.toLowerCase().match(/\b\w+\b/g) || [];
            for (const keyword of keywords) {
                if (keyword.length > 3) { // Skip short words
                    errorCounts[keyword] = (errorCounts[keyword] || 0) + 1;
                }
            }
        }

        return Object.entries(errorCounts)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 5)
            .map(([keyword]) => keyword);
    }

    /**
     * Analyze sequences to find frequent patterns
     */
    async analyzeSequences(sequences) {
        const patternCounts = {};
        
        // Count occurrences
        for (const seq of sequences) {
            const key = seq.sequence;
            if (!patternCounts[key]) {
                patternCounts[key] = {
                    sequence: key,
                    commands: seq.commands,
                    count: 0,
                    instances: [],
                    metadata: seq.metadata
                };
            }
            patternCounts[key].count++;
            patternCounts[key].instances.push(seq);
        }

        // Filter by minimum frequency and calculate scores
        const patterns = Object.values(patternCounts)
            .filter(p => p.count >= this.minFrequency)
            .map(p => ({
                ...p,
                score: this.calculatePatternScore(p),
                suggestion: this.generateSuggestion(p)
            }))
            .sort((a, b) => b.score - a.score);

        return patterns;
    }

    /**
     * Calculate a score for pattern importance
     */
    calculatePatternScore(pattern) {
        let score = pattern.count * 10; // Base score from frequency

        // Bonus for high success rate
        const avgSuccessRate = pattern.instances
            .map(i => i.metadata.successRate)
            .reduce((a, b) => a + b, 0) / pattern.instances.length;
        score += avgSuccessRate * 20;

        // Bonus for longer patterns
        score += (pattern.commands.length - this.minPatternLength) * 5;

        // Penalty for very common commands
        const commonCommands = ['/commit', '/test'];
        const commonCount = pattern.commands.filter(cmd => 
            commonCommands.includes(cmd)
        ).length;
        score -= commonCount * 2;

        return Math.max(0, score);
    }

    /**
     * Generate a suggestion for a pattern
     */
    generateSuggestion(pattern) {
        const cmdNames = pattern.commands.map(cmd => cmd.replace('/', ''));
        const suggestedName = `/${cmdNames.join('-')}`;
        
        return {
            name: suggestedName,
            description: `Combines ${pattern.commands.join(' → ')}`,
            timeSaved: this.estimateTimeSaved(pattern),
            confidence: Math.min(0.95, pattern.count / 10)
        };
    }

    /**
     * Estimate time saved by creating a custom command
     */
    estimateTimeSaved(pattern) {
        const avgDuration = pattern.instances
            .map(i => i.metadata.averageDuration)
            .filter(d => d != null)
            .reduce((a, b) => a + b, 0) / pattern.instances.length;

        // Assume 20% time saving from automation
        return avgDuration ? Math.round(avgDuration * 0.2) : null;
    }

    /**
     * Generate command suggestions based on current context
     */
    async suggestCommands(currentContext) {
        const { recentCommands = [], currentCommand = null } = currentContext;
        
        if (recentCommands.length === 0 && !currentCommand) {
            return [];
        }

        // Get frequent patterns
        const patterns = await this.store.getFrequentPatterns(this.minFrequency);
        const suggestions = [];

        for (const pattern of patterns) {
            const commands = pattern.pattern_sequence.split(',');
            
            // Check if recent commands match the beginning of this pattern
            if (this.matchesContext(commands, recentCommands, currentCommand)) {
                const confidence = this.calculateConfidence(pattern, recentCommands);
                const nextCommands = this.getNextCommands(commands, recentCommands);
                
                if (nextCommands.length > 0) {
                    suggestions.push({
                        pattern: pattern.pattern_sequence,
                        nextCommands: nextCommands,
                        confidence: confidence,
                        frequency: pattern.frequency,
                        lastUsed: pattern.last_seen
                    });
                }
            }
        }

        return suggestions.sort((a, b) => b.confidence - a.confidence);
    }

    /**
     * Check if a pattern matches the current context
     */
    matchesContext(patternCommands, recentCommands, currentCommand) {
        const contextCommands = currentCommand 
            ? [...recentCommands, currentCommand]
            : recentCommands;

        if (contextCommands.length === 0 || contextCommands.length >= patternCommands.length) {
            return false;
        }

        // Check if context matches the beginning of the pattern
        for (let i = 0; i < contextCommands.length; i++) {
            if (contextCommands[i] !== patternCommands[i]) {
                return false;
            }
        }

        return true;
    }

    /**
     * Get the next commands in a pattern
     */
    getNextCommands(patternCommands, recentCommands) {
        return patternCommands.slice(recentCommands.length);
    }

    /**
     * Calculate confidence for a suggestion
     */
    calculateConfidence(pattern, recentCommands) {
        let confidence = 0.5; // Base confidence

        // Higher frequency = higher confidence
        confidence += Math.min(0.3, pattern.frequency / 20);

        // More matching commands = higher confidence
        confidence += (recentCommands.length / 10) * 0.2;

        return Math.min(0.95, confidence);
    }

    /**
     * Check for patterns in real-time as commands are executed
     */
    async checkForPattern(recentCommands) {
        if (recentCommands.length < this.minPatternLength) {
            return null;
        }

        const sequence = recentCommands.join(',');
        const existing = await this.store.getFrequentPatterns(1);
        
        // Check if this sequence is already a known pattern
        const match = existing.find(p => p.pattern_sequence === sequence);
        
        if (match && match.frequency >= this.minFrequency) {
            return {
                pattern: sequence,
                frequency: match.frequency,
                suggestion: match.suggested_command || this.generateSuggestion({
                    commands: recentCommands,
                    count: match.frequency,
                    instances: []
                })
            };
        }

        return null;
    }

    /**
     * Analyze patterns for specific insights
     */
    async getPatternInsights() {
        const patterns = await this.store.getFrequentPatterns(this.minFrequency);
        const executions = await this.store.getExecutionsInWindow('30d');

        return {
            totalPatterns: patterns.length,
            mostFrequent: patterns.slice(0, 5),
            errorPatterns: await this.findErrorPatterns(executions),
            timeBasedPatterns: await this.findTimeBasedPatterns(executions),
            recommendations: await this.generateRecommendations(patterns)
        };
    }

    /**
     * Find patterns that often lead to errors
     */
    async findErrorPatterns(executions) {
        const errorSequences = [];
        
        for (let i = 1; i < executions.length; i++) {
            if (executions[i].outcome === 'failure' && executions[i - 1].outcome === 'success') {
                errorSequences.push({
                    trigger: executions[i - 1].command,
                    failure: executions[i].command,
                    error: executions[i].error_message
                });
            }
        }

        // Group by pattern
        const patterns = {};
        for (const seq of errorSequences) {
            const key = `${seq.trigger} → ${seq.failure}`;
            if (!patterns[key]) {
                patterns[key] = { count: 0, errors: [] };
            }
            patterns[key].count++;
            if (seq.error && !patterns[key].errors.includes(seq.error)) {
                patterns[key].errors.push(seq.error);
            }
        }

        return Object.entries(patterns)
            .filter(([_, data]) => data.count >= 2)
            .map(([pattern, data]) => ({ pattern, ...data }))
            .sort((a, b) => b.count - a.count);
    }

    /**
     * Find time-based patterns (e.g., commands used at specific times)
     */
    async findTimeBasedPatterns(executions) {
        const hourlyDistribution = {};
        const dayDistribution = {};

        for (const exec of executions) {
            const date = new Date(exec.timestamp);
            const hour = date.getHours();
            const day = date.getDay();

            const hourKey = `${exec.command}-${hour}`;
            const dayKey = `${exec.command}-${day}`;

            hourlyDistribution[hourKey] = (hourlyDistribution[hourKey] || 0) + 1;
            dayDistribution[dayKey] = (dayDistribution[dayKey] || 0) + 1;
        }

        return {
            peakHours: this.findPeaks(hourlyDistribution, 'hour'),
            peakDays: this.findPeaks(dayDistribution, 'day')
        };
    }

    /**
     * Find peaks in time-based distribution
     */
    findPeaks(distribution, type) {
        const threshold = Object.values(distribution).reduce((a, b) => a + b, 0) / 
                         Object.keys(distribution).length * 2;

        return Object.entries(distribution)
            .filter(([_, count]) => count > threshold)
            .map(([key, count]) => {
                const [command, time] = key.split('-');
                return { command, [type]: parseInt(time), count };
            })
            .sort((a, b) => b.count - a.count);
    }

    /**
     * Generate recommendations based on patterns
     */
    async generateRecommendations(patterns) {
        const recommendations = [];

        for (const pattern of patterns.slice(0, 10)) {
            const commands = pattern.pattern_sequence.split(',');
            
            if (pattern.frequency >= 5) {
                recommendations.push({
                    type: 'create_command',
                    pattern: pattern.pattern_sequence,
                    suggestion: this.generateSuggestion({
                        commands: commands,
                        count: pattern.frequency,
                        instances: []
                    }),
                    reason: `This sequence has been used ${pattern.frequency} times`
                });
            }
        }

        return recommendations;
    }
}

module.exports = PatternRecognizer;