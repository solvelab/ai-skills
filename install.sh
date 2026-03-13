#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/solvelab/ai-skills.git"
INSTALL_DIR="$HOME/ai-skills"
CLAUDE_DIR="$HOME/.claude"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

SKILLS_BLOCK='## Skills

Skills are located at ~/ai-skills/claude/skills/.
Each skill has a SKILL.md file. Read the relevant skill before performing any matching task.'

# Check git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed. Please install git first."
    exit 1
fi

# Clone or pull the repository
if [ -d "$INSTALL_DIR" ]; then
    echo "📦 ~/ai-skills already exists. Pulling latest changes..."
    git -C "$INSTALL_DIR" pull
else
    echo "📦 Cloning ai-skills into ~/ai-skills..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Create ~/.claude directory if needed
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "📁 Creating ~/.claude/ directory..."
    mkdir -p "$CLAUDE_DIR"
fi

# Create CLAUDE.md if it doesn't exist
if [ ! -f "$CLAUDE_MD" ]; then
    echo "📄 Creating ~/.claude/CLAUDE.md..."
    touch "$CLAUDE_MD"
fi

# Append skills section if not already present
if grep -q "## Skills" "$CLAUDE_MD"; then
    echo "⏭️  Skills section already exists in ~/.claude/CLAUDE.md. Skipping."
else
    echo "✏️  Adding Skills section to ~/.claude/CLAUDE.md..."
    printf '\n%s\n' "$SKILLS_BLOCK" >> "$CLAUDE_MD"
fi

echo ""
echo "✅ ai-skills installed successfully! Restart Claude Code to apply."
