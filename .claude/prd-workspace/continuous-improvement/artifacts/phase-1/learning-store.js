const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs').promises;

class LearningStore {
    constructor(dbPath = '.claude/learning/claude-learning.db') {
        this.dbPath = dbPath;
        this.db = null;
    }

    async initialize() {
        // Ensure directory exists
        const dir = path.dirname(this.dbPath);
        await fs.mkdir(dir, { recursive: true });

        return new Promise((resolve, reject) => {
            this.db = new sqlite3.Database(this.dbPath, async (err) => {
                if (err) {
                    reject(err);
                    return;
                }
                
                try {
                    await this.createSchema();
                    resolve();
                } catch (schemaErr) {
                    reject(schemaErr);
                }
            });
        });
    }

    async createSchema() {
        const schema = `
            -- Command executions table
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_sequence TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                suggested_command TEXT
            );

            -- Knowledge entries table  
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            );

            -- Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_command ON executions(command);
            CREATE INDEX IF NOT EXISTS idx_timestamp ON executions(timestamp);
            CREATE INDEX IF NOT EXISTS idx_pattern_freq ON patterns(frequency);
        `;

        const statements = schema.split(';').filter(s => s.trim());
        
        for (const statement of statements) {
            await this.run(statement);
        }
    }

    // Helper method to promisify db.run
    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.run(sql, params, function(err) {
                if (err) reject(err);
                else resolve({ id: this.lastID, changes: this.changes });
            });
        });
    }

    // Helper method to promisify db.get
    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.get(sql, params, (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
    }

    // Helper method to promisify db.all
    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, params, (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }

    // Core operations
    async recordExecution(command, params, outcome, options = {}) {
        const { duration_ms, error_message, user_feedback, project_context } = options;
        
        const sql = `
            INSERT INTO executions (command, parameters, outcome, duration_ms, error_message, user_feedback, project_context)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `;
        
        const result = await this.run(sql, [
            command,
            JSON.stringify(params),
            outcome,
            duration_ms || null,
            error_message || null,
            user_feedback || null,
            project_context || null
        ]);
        
        return result.id;
    }

    async getRecentExecutions(command = null, limit = 10) {
        let sql = `
            SELECT * FROM executions
            ${command ? 'WHERE command = ?' : ''}
            ORDER BY timestamp DESC
            LIMIT ?
        `;
        
        const params = command ? [command, limit] : [limit];
        const rows = await this.all(sql, params);
        
        return rows.map(row => ({
            ...row,
            parameters: row.parameters ? JSON.parse(row.parameters) : null
        }));
    }

    async getSimilarIssues(keywords, limit = 5) {
        // Simple keyword matching - can be enhanced with full-text search
        const keywordList = Array.isArray(keywords) ? keywords : keywords.split(' ');
        const conditions = keywordList.map(() => 
            "(command LIKE ? OR parameters LIKE ? OR error_message LIKE ?)"
        ).join(' OR ');
        
        const sql = `
            SELECT * FROM executions
            WHERE ${conditions}
            ORDER BY timestamp DESC
            LIMIT ?
        `;
        
        const params = [];
        keywordList.forEach(keyword => {
            const pattern = `%${keyword}%`;
            params.push(pattern, pattern, pattern);
        });
        params.push(limit);
        
        const rows = await this.all(sql, params);
        
        return rows.map(row => ({
            ...row,
            parameters: row.parameters ? JSON.parse(row.parameters) : null
        }));
    }

    // Knowledge management
    async addKnowledge(key, value, category = null) {
        const sql = `
            INSERT INTO knowledge (key, value, category)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                usage_count = usage_count + 1
        `;
        
        await this.run(sql, [key, value, category]);
        return true;
    }

    async getKnowledge(key) {
        const sql = `
            UPDATE knowledge SET usage_count = usage_count + 1 WHERE key = ?;
            SELECT * FROM knowledge WHERE key = ?
        `;
        
        await this.run(`UPDATE knowledge SET usage_count = usage_count + 1 WHERE key = ?`, [key]);
        return await this.get(`SELECT * FROM knowledge WHERE key = ?`, [key]);
    }

    async searchKnowledge(query) {
        const sql = `
            SELECT * FROM knowledge
            WHERE key LIKE ? OR value LIKE ? OR category LIKE ?
            ORDER BY usage_count DESC
        `;
        
        const pattern = `%${query}%`;
        return await this.all(sql, [pattern, pattern, pattern]);
    }

    // Pattern tracking
    async recordPattern(sequence) {
        // Check if pattern exists
        const existing = await this.get(
            'SELECT * FROM patterns WHERE pattern_sequence = ?',
            [sequence]
        );
        
        if (existing) {
            // Update frequency
            await this.run(
                'UPDATE patterns SET frequency = frequency + 1, last_seen = CURRENT_TIMESTAMP WHERE id = ?',
                [existing.id]
            );
            return existing.id;
        } else {
            // Insert new pattern
            const result = await this.run(
                'INSERT INTO patterns (pattern_sequence) VALUES (?)',
                [sequence]
            );
            return result.id;
        }
    }

    async getFrequentPatterns(threshold = 3) {
        const sql = `
            SELECT * FROM patterns
            WHERE frequency >= ?
            ORDER BY frequency DESC, last_seen DESC
        `;
        
        return await this.all(sql, [threshold]);
    }

    // Utility methods
    async getExecutionsInWindow(timeWindow = '7d') {
        // Parse time window (e.g., '7d', '24h', '1w')
        const match = timeWindow.match(/(\d+)([dhw])/);
        if (!match) throw new Error('Invalid time window format');
        
        const [, amount, unit] = match;
        const hours = unit === 'h' ? amount : unit === 'd' ? amount * 24 : amount * 24 * 7;
        
        const sql = `
            SELECT * FROM executions
            WHERE datetime(timestamp) > datetime('now', '-${hours} hours')
            ORDER BY timestamp ASC
        `;
        
        const rows = await this.all(sql);
        return rows.map(row => ({
            ...row,
            parameters: row.parameters ? JSON.parse(row.parameters) : null
        }));
    }

    async close() {
        return new Promise((resolve, reject) => {
            if (this.db) {
                this.db.close((err) => {
                    if (err) reject(err);
                    else resolve();
                });
            } else {
                resolve();
            }
        });
    }
}

module.exports = LearningStore;