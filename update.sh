#!/usr/bin/env bash
# update.sh — Force-sync ~/ai-skills to the latest published rules/skills.
# Companion to install.sh: install wires the tool once; update pulls new content.
#
# Usage:
#   ./update.sh           # fast-forward pull + regenerate Cursor rules
#   ./update.sh --force   # discard local changes, hard-reset to origin
#   ./update.sh --help
set -euo pipefail

INSTALL_DIR="$HOME/ai-skills"
FORCE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force|-f) FORCE=1; shift ;;
        --help|-h)
            echo "Usage: update.sh [--force]"
            echo ""
            echo "Pulls the latest ai-skills into ~/ai-skills and regenerates Cursor rules."
            echo "  (no flag)   fast-forward pull; aborts if local changes diverge"
            echo "  --force     discard local changes and hard-reset to origin"
            echo ""
            echo "After updating, restart your AI tool — global rules load at session start."
            exit 0 ;;
        *) echo "Unknown option: $1. Use --help."; exit 1 ;;
    esac
done

command -v git >/dev/null 2>&1 || { echo "❌ git not installed."; exit 1; }

if [ ! -d "$INSTALL_DIR/.git" ]; then
    echo "❌ ~/ai-skills not found (or not a git repo). Run install.sh first."
    exit 1
fi

echo "📦 Updating ~/ai-skills..."
git -C "$INSTALL_DIR" fetch --quiet origin

BEFORE=$(git -C "$INSTALL_DIR" rev-parse HEAD)

if [ "$FORCE" -eq 1 ]; then
    UPSTREAM=$(git -C "$INSTALL_DIR" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo "origin/master")
    echo "  ⚠️  --force: discarding local changes, resetting to $UPSTREAM"
    git -C "$INSTALL_DIR" reset --hard "$UPSTREAM" --quiet
else
    if ! git -C "$INSTALL_DIR" pull --ff-only --quiet; then
        echo "  ❌ Fast-forward failed — local changes diverge from origin."
        echo "     Re-run with --force to discard them: ./update.sh --force"
        exit 1
    fi
fi

AFTER=$(git -C "$INSTALL_DIR" rev-parse HEAD)

# Regenerate Cursor .mdc wrappers from updated shared content (best-effort)
if [ -f "$INSTALL_DIR/generate.sh" ]; then
    echo "🔧 Regenerating Cursor rules..."
    bash "$INSTALL_DIR/generate.sh" >/dev/null && echo "  ✅ Cursor rules regenerated."
fi

echo ""
if [ "$BEFORE" = "$AFTER" ]; then
    echo "✅ Already up to date."
else
    echo "✅ Updated:"
    git -C "$INSTALL_DIR" --no-pager log --oneline "$BEFORE..$AFTER"
    echo ""
    echo "↻ Restart your AI tool — global rules (CLAUDE.md @-includes) load at session start."
fi
