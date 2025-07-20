#!/bin/bash
# Claude Configuration Installer
# Simple, clean installation of claudeops to ~/.claude

set -e

echo "🚀 Installing Claude configuration..."

# Backup existing configuration if present
if [ -d "$HOME/.claude" ]; then
    echo "📦 Backing up existing ~/.claude to ~/.claude.backup-$(date +%Y%m%d-%H%M%S)"
    mv "$HOME/.claude" "$HOME/.claude.backup-$(date +%Y%m%d-%H%M%S)"
fi

# Create target directory
mkdir -p "$HOME/.claude"

# Copy all Claude configuration files
echo "📋 Copying configuration files..."
cp -r commands system config docs data cache STRUCTURE.md "$HOME/.claude/"

# Create .gitignore in target to protect user data
cat > "$HOME/.claude/.gitignore" << 'EOF'
# User data
data/conversations/*
data/workspaces/*
data/todos/*
data/logs/*
!data/**/.gitkeep

# Cache files
cache/shell-snapshots/*
cache/statsig/*
!cache/**/.gitkeep

# Platform-specific
.DS_Store
Thumbs.db

# Editor files
*.swp
*.bak
*~
EOF

echo "✅ Installation complete!"
echo ""
echo "Claude configuration is now available in ~/.claude"
echo "Your slash commands are ready to use!"
echo ""
echo "Try: claude /safe 'echo Hello from Claude!'"