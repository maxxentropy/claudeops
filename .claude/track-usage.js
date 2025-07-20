#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const logFile = path.join(process.env.HOME, '.claude', 'logs', 'usage.jsonl');

function trackUsage(command, tokens, estimatedCost) {
    const entry = {
        timestamp: new Date().toISOString(),
        command: command,
        tokens: tokens,
        estimatedCost: estimatedCost,
        platform: process.platform
    };
    
    fs.appendFileSync(logFile, JSON.stringify(entry) + '\n');
}

// Export for use in hooks
module.exports = { trackUsage };

// CLI usage
if (require.main === module) {
    const [,, command, tokens, cost] = process.argv;
    if (command && tokens && cost) {
        trackUsage(command, parseInt(tokens), parseFloat(cost));
        console.log('Usage tracked successfully');
    } else {
        console.log('Usage: track-usage <command> <tokens> <cost>');
    }
}
