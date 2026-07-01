#!/usr/bin/env bash
# install.sh — Installs the ai-skills collection for one or more AI coding tools.
#
# Preferred alternatives (no clone needed):
#   npx skills add solvelab/ai-skills            # open Agent Skills CLI, 70+ agents
#   /plugin marketplace add solvelab/ai-skills   # Claude Code plugin marketplace
#
# This script clones the repo to ~/ai-skills and wires each tool:
#   claude   symlinks skills into ~/.claude/skills/ (native discovery)
#            --legacy appends the Skills block to ~/.claude/CLAUDE.md instead
#   codex    appends the Skills block to ~/.codex/AGENTS.md
#   cursor   points at cursor/rules/*.mdc (copy per project)
#   copilot  points at copilot/instructions/ (copy per project)
set -euo pipefail

REPO_URL="https://github.com/solvelab/ai-skills.git"
INSTALL_DIR="$HOME/ai-skills"
LEGACY=0

# --- Tool-specific configurations ---

setup_claude() {
    if [ "$LEGACY" -eq 1 ]; then
        setup_claude_legacy
        return
    fi

    local TARGET_DIR="$HOME/.claude/skills"
    mkdir -p "$TARGET_DIR"

    local linked=0 skipped=0
    for skill_dir in "$INSTALL_DIR"/skills/*/; do
        [ -f "$skill_dir/SKILL.md" ] || continue
        local name link
        name="$(basename "$skill_dir")"
        link="$TARGET_DIR/$name"

        if [ -L "$link" ] && [ "$(readlink "$link")" = "${skill_dir%/}" ]; then
            skipped=$((skipped + 1))
            continue
        fi
        if [ -e "$link" ] && [ ! -L "$link" ]; then
            echo "  ⚠️  Claude Code: ~/.claude/skills/$name exists and is not a symlink. Skipping (remove it to let ai-skills manage it)."
            continue
        fi
        ln -sfn "${skill_dir%/}" "$link"
        linked=$((linked + 1))
    done
    echo "  ✏️  Claude Code: $linked skill(s) symlinked into ~/.claude/skills/ ($skipped already up to date)."
}

setup_claude_legacy() {
    local CLAUDE_DIR="$HOME/.claude"
    local CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
    local SKILLS_BLOCK='## Skills

Skills are located at ~/ai-skills/claude/skills/.
Each skill has a SKILL.md file. Read the relevant skill before performing any matching task.'

    mkdir -p "$CLAUDE_DIR"
    [ -f "$CLAUDE_MD" ] || touch "$CLAUDE_MD"

    if grep -q "## Skills" "$CLAUDE_MD"; then
        echo "  ⏭️  Claude Code (legacy): Skills section already exists. Skipping."
    else
        echo "  ✏️  Claude Code (legacy): Adding Skills section to ~/.claude/CLAUDE.md..."
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
    echo "  💡 Cursor: rules are in ~/ai-skills/cursor/rules/"
    echo "  💡 Copy the relevant .mdc files to your project's .cursor/rules/ directory,"
    echo "     or use: npx skills add solvelab/ai-skills -a cursor"
}

setup_copilot() {
    echo "  💡 Copilot: instructions are in ~/ai-skills/copilot/instructions/"
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
        --legacy)
            LEGACY=1
            shift
            ;;
        --help|-h)
            echo "Usage: install.sh [--tool <tool>] [--legacy]"
            echo ""
            echo "Tools: claude (default), codex, cursor, copilot, all"
            echo ""
            echo "Options:"
            echo "  --legacy   Claude Code: append Skills block to ~/.claude/CLAUDE.md"
            echo "             instead of symlinking into ~/.claude/skills/"
            echo ""
            echo "Examples:"
            echo "  ./install.sh                # Install for Claude Code (native symlinks)"
            echo "  ./install.sh --tool codex   # Install for OpenAI Codex"
            echo "  ./install.sh --tool all     # Install for all supported tools"
            echo ""
            echo "Prefer npx? Run: npx skills add solvelab/ai-skills"
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
echo "🔧 Configuring for: $TOOL (version $(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo unknown))"
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
echo "   Update later with: cd ~/ai-skills && ./update.sh"
