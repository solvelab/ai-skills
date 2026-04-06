#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/solvelab/ai-skills.git"
INSTALL_DIR="$HOME/ai-skills"

# --- Tool-specific configurations ---

setup_claude() {
    local CLAUDE_DIR="$HOME/.claude"
    local CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
    local SKILLS_BLOCK='## Skills

Skills are located at ~/ai-skills/claude/skills/.
Each skill has a SKILL.md file. Read the relevant skill before performing any matching task.'

    mkdir -p "$CLAUDE_DIR"
    [ -f "$CLAUDE_MD" ] || touch "$CLAUDE_MD"

    if grep -q "## Skills" "$CLAUDE_MD"; then
        echo "  ⏭️  Claude Code: Skills section already exists. Skipping."
    else
        echo "  ✏️  Claude Code: Adding Skills section to ~/.claude/CLAUDE.md..."
        printf '\n%s\n' "$SKILLS_BLOCK" >> "$CLAUDE_MD"
    fi
}

setup_codex() {
    local CODEX_DIR="$HOME/.codex"
    local CODEX_MD="$CODEX_DIR/AGENTS.md"
    local SKILLS_BLOCK='# AI Skills

Skills are located at ~/ai-skills/codex/skills/.
Each skill has an AGENTS.md file with instructions for specific tasks.'

    mkdir -p "$CODEX_DIR"
    [ -f "$CODEX_MD" ] || touch "$CODEX_MD"

    if grep -q "# AI Skills" "$CODEX_MD"; then
        echo "  ⏭️  Codex: Skills section already exists. Skipping."
    else
        echo "  ✏️  Codex: Adding Skills section to ~/.codex/AGENTS.md..."
        printf '\n%s\n' "$SKILLS_BLOCK" >> "$CODEX_MD"
    fi
}

setup_cursor() {
    echo "  ✏️  Cursor: Generating inline .mdc rule files..."
    if [ -x "$INSTALL_DIR/generate.sh" ]; then
        "$INSTALL_DIR/generate.sh"
    else
        echo "  ⚠️  generate.sh not found or not executable. Run: chmod +x ~/ai-skills/generate.sh"
    fi
    echo "  💡 Cursor: Copy cursor/rules/*.mdc to your project's .cursor/rules/ directory."
}

setup_copilot() {
    echo "  💡 Copilot: Skill wrappers are in ~/ai-skills/copilot/instructions/"
    echo "  💡 Copy the relevant .instructions.md files to your project's .github/instructions/ directory."
}

# --- Main ---

TOOL="claude"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tool)
            TOOL="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: install.sh [--tool <tool>]"
            echo ""
            echo "Tools: claude (default), codex, cursor, copilot, all"
            echo ""
            echo "Examples:"
            echo "  ./install.sh                # Install for Claude Code"
            echo "  ./install.sh --tool codex   # Install for OpenAI Codex"
            echo "  ./install.sh --tool all     # Install for all supported tools"
            exit 0
            ;;
        *)
            echo "Unknown option: $1. Use --help for usage."
            exit 1
            ;;
    esac
done

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

echo ""
echo "🔧 Configuring for: $TOOL"
echo ""

case "$TOOL" in
    claude)
        setup_claude
        ;;
    codex)
        setup_codex
        ;;
    cursor)
        setup_cursor
        ;;
    copilot)
        setup_copilot
        ;;
    all)
        setup_claude
        setup_codex
        setup_cursor
        setup_copilot
        ;;
    *)
        echo "❌ Unknown tool: $TOOL. Supported: claude, codex, cursor, copilot, all"
        exit 1
        ;;
esac

echo ""
echo "✅ ai-skills installed successfully for $TOOL! Restart your tool to apply."
