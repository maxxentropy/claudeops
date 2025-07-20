const { getEnhancer } = require('../phase-3/command-enhancer');

class LearnCommand {
    constructor() {
        this.enhancer = getEnhancer();
        this.categories = {
            debugging: ['debug', 'fix', 'error', 'issue', 'bug', 'crash', 'fail'],
            performance: ['slow', 'optimize', 'cache', 'speed', 'latency', 'perf'],
            security: ['auth', 'token', 'secure', 'permission', 'access', 'oauth'],
            deployment: ['deploy', 'release', 'production', 'rollout', 'ship'],
            testing: ['test', 'coverage', 'mock', 'unit', 'integration', 'e2e'],
        };
    }

    /**
     * Execute the learn command
     */
    async execute(args) {
        try {
            // Parse arguments
            const { key, knowledge } = this.parseArgs(args);
            
            if (!key || !knowledge) {
                return this.showHelp();
            }

            // Validate input
            const validation = this.validateInput(key, knowledge);
            if (!validation.valid) {
                return this.formatError(validation.error);
            }

            // Auto-detect category
            const category = this.detectCategory(key, knowledge);

            // Initialize enhancer if needed
            if (!this.enhancer.initialized) {
                await this.enhancer.initialize();
            }

            // Check for existing knowledge
            const existing = await this.enhancer.store.getKnowledge(key);
            if (existing) {
                return this.formatDuplicateWarning(key, existing);
            }

            // Store the knowledge
            await this.enhancer.addKnowledge(key, knowledge, category);

            // Get relevant commands
            const relevantCommands = await this.findRelevantCommands(key, knowledge);

            // Get total knowledge count
            const totalCount = await this.getTotalKnowledgeCount();

            // Format success response
            return this.formatSuccess(key, knowledge, category, relevantCommands, totalCount);

        } catch (error) {
            console.error('Learn command failed:', error);
            return this.formatError(`Failed to save knowledge: ${error.message}`);
        }
    }

    /**
     * Parse command arguments
     */
    parseArgs(args) {
        if (typeof args === 'string') {
            // Parse string format: "key value with spaces"
            const match = args.match(/^(\S+)\s+(.+)$/);
            if (match) {
                return {
                    key: match[1],
                    knowledge: match[2].trim()
                };
            }
        } else if (Array.isArray(args)) {
            // Parse array format: ["key", "value", "with", "spaces"]
            if (args.length >= 2) {
                return {
                    key: args[0],
                    knowledge: args.slice(1).join(' ')
                };
            }
        } else if (typeof args === 'object' && args.key && args.knowledge) {
            // Already parsed object
            return args;
        }

        return { key: null, knowledge: null };
    }

    /**
     * Validate input
     */
    validateInput(key, knowledge) {
        // Key validation
        if (key.length < 3) {
            return { valid: false, error: 'Key must be at least 3 characters long' };
        }

        if (key.length > 50) {
            return { valid: false, error: 'Key must be less than 50 characters' };
        }

        if (!/^[a-zA-Z0-9-_]+$/.test(key)) {
            return { valid: false, error: 'Key must contain only letters, numbers, hyphens, and underscores' };
        }

        // Knowledge validation
        if (knowledge.length < 10) {
            return { valid: false, error: 'Knowledge must be at least 10 characters long' };
        }

        if (knowledge.length > 500) {
            return { valid: false, error: 'Knowledge must be less than 500 characters' };
        }

        return { valid: true };
    }

    /**
     * Detect category based on content
     */
    detectCategory(key, knowledge) {
        const combined = `${key} ${knowledge}`.toLowerCase();

        for (const [category, keywords] of Object.entries(this.categories)) {
            for (const keyword of keywords) {
                if (combined.includes(keyword)) {
                    return category;
                }
            }
        }

        return 'general';
    }

    /**
     * Find commands that might show this knowledge
     */
    async findRelevantCommands(key, knowledge) {
        const keywords = this.extractKeywords(key, knowledge);
        const relevantCommands = new Set();

        // Check common command patterns
        const commandPatterns = {
            '/fix': ['fix', 'bug', 'error', 'issue', 'debug'],
            '/test': ['test', 'coverage', 'mock', 'assert'],
            '/deploy': ['deploy', 'release', 'ship', 'production'],
            '/config': ['config', 'setting', 'env', 'variable'],
            '/build': ['build', 'compile', 'bundle', 'package'],
            '/commit': ['commit', 'git', 'change', 'stage']
        };

        for (const [command, patterns] of Object.entries(commandPatterns)) {
            for (const pattern of patterns) {
                if (keywords.some(kw => kw.includes(pattern) || pattern.includes(kw))) {
                    relevantCommands.add(command);
                }
            }
        }

        // Also check against actual command history
        if (this.enhancer.store) {
            const recentCommands = await this.enhancer.store.getRecentExecutions(null, 20);
            for (const exec of recentCommands) {
                const params = exec.parameters ? JSON.parse(exec.parameters) : {};
                const paramStr = JSON.stringify(params).toLowerCase();
                
                if (keywords.some(kw => paramStr.includes(kw))) {
                    relevantCommands.add(exec.command);
                }
            }
        }

        return Array.from(relevantCommands).slice(0, 5);
    }

    /**
     * Extract keywords from key and knowledge
     */
    extractKeywords(key, knowledge) {
        const combined = `${key} ${knowledge}`.toLowerCase();
        const words = combined.match(/\b\w{3,}\b/g) || [];
        
        // Filter out common words
        const commonWords = ['the', 'and', 'for', 'with', 'this', 'that', 'from', 'but'];
        return words.filter(w => !commonWords.includes(w));
    }

    /**
     * Get total knowledge count
     */
    async getTotalKnowledgeCount() {
        try {
            const result = await this.enhancer.store.get(
                'SELECT COUNT(*) as count FROM knowledge'
            );
            return result.count;
        } catch (error) {
            return 0;
        }
    }

    /**
     * Format success message
     */
    formatSuccess(key, knowledge, category, relevantCommands, totalCount) {
        const commandList = relevantCommands.length > 0
            ? relevantCommands.map(cmd => `- ${cmd}`).join('\n')
            : '- Various commands based on context';

        return `✅ **Knowledge saved successfully!**

**Key**: ${key}
**Value**: ${knowledge}
**Category**: ${category}

This knowledge will appear in commands like:
${commandList}

Total team knowledge entries: ${totalCount}`;
    }

    /**
     * Format duplicate warning
     */
    formatDuplicateWarning(key, existing) {
        return `⚠️ **Knowledge with key "${key}" already exists**

**Existing value**: ${existing.value}
**Category**: ${existing.category}
**Created**: ${new Date(existing.created_at).toLocaleString()}
**Used**: ${existing.usage_count} times

To update this knowledge, first remove it with:
\`/unlearn ${key}\`

Then add the new version.`;
    }

    /**
     * Format error message
     */
    formatError(error) {
        return `❌ **Error**: ${error}

Use \`/learn <key> <knowledge>\` to save team insights.

Example:
\`/learn redis-timeout "Check connection pool size first"\``;
    }

    /**
     * Show help
     */
    showHelp() {
        return `# /learn - Capture Team Knowledge

## Usage
\`\`\`
/learn <key> <knowledge>
\`\`\`

## Examples
- \`/learn redis-timeout "Check connection pool size first - it's always the pool"\`
- \`/learn deploy-friday "Never deploy on Friday after 3pm"\`
- \`/learn auth-debug "Enable verbose logging in OAuth provider settings"\`

## Guidelines
- **Key**: Short, descriptive identifier (3-50 chars, letters/numbers/hyphens)
- **Knowledge**: Actionable insight or solution (10-500 chars)

## Categories
Knowledge is auto-categorized: debugging, performance, security, deployment, testing, or general

Saved knowledge appears automatically in relevant commands based on context.`;
    }
}

// Export for use in slash command system
module.exports = LearnCommand;