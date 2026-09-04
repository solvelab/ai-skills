#!/usr/bin/env bash
# update.sh — Force-sync ~/ai-skills to the latest published rules/skills.
# Companion to install.sh: install wires the tool once; update pulls new content.
#
# Usage:
#   ./update.sh           # fast-forward pull + regenerate all tool wrappers
#   ./update.sh --force   # discard local changes, hard-reset to origin
#   ./update.sh --help
#
# The wrappers are regenerated only when the generator's INPUTS are clean in the index:
# `git status --porcelain --untracked-files=no -- VERSION skills/` must be empty. A dirty VERSION
# would otherwise be written into every tracked plugins/*/.claude-plugin/plugin.json. The pull
# still happens either way, and the script still exits 0: the README tells users to edit
# claude/global/personal-rules.md in this clone, and that edit must never block an update.
#
# WHAT THE GUARD DOES NOT COVER: untracked files (a new skills/<name>/ that was never `git add`ed
# is not seen, and the generator will happily emit wrappers for it), and edits anywhere outside
# VERSION and skills/ (they do not feed the generator, so they are not checked). A regeneration
# that ran is proof that those two paths were clean in the index, nothing more.
# There is no interactive prompt on purpose: the README runs this script via `curl | bash`, where
# stdin is the script itself.
set -euo pipefail

INSTALL_DIR="$HOME/ai-skills"
FORCE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force|-f) FORCE=1; shift ;;
        --help|-h)
            echo "Usage: update.sh [--force]"
            echo ""
            echo "Pulls the latest ai-skills into ~/ai-skills and regenerates all tool wrappers."
            echo "  (no flag)   fast-forward pull; aborts if local commits diverge from origin;"
            echo "              skips the wrapper regeneration while VERSION or skills/ are modified"
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

echo "📦 Updating ~/ai-skills (current: v$(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo '?'))..."
git -C "$INSTALL_DIR" fetch --quiet origin

BEFORE=$(git -C "$INSTALL_DIR" rev-parse HEAD)

if [ "$FORCE" -eq 1 ]; then
    UPSTREAM=$(git -C "$INSTALL_DIR" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo "origin/master")
    echo "  ⚠️  --force: discarding local changes, resetting to $UPSTREAM"
    git -C "$INSTALL_DIR" reset --hard "$UPSTREAM" --quiet
else
    # advice.diverging=false drops git's nine `hint:` lines; the `fatal:` line is kept as an
    # indented detail because on a network failure it is the only useful information.
    if ! PULL_ERR="$(git -C "$INSTALL_DIR" -c advice.diverging=false pull --ff-only --quiet 2>&1)"; then
        echo "  ❌ Fast-forward failed — local changes diverge from origin."
        echo "     Re-run with --force to discard them: cd ~/ai-skills && ./update.sh --force"
        [ -z "$PULL_ERR" ] || printf '     git: %s\n' "$PULL_ERR"
        exit 1
    fi
fi

AFTER=$(git -C "$INSTALL_DIR" rev-parse HEAD)

# Regenerate tool wrappers from the canonical skills/ content — only over clean inputs (see header).
if [ -f "$INSTALL_DIR/generate.sh" ]; then
    DIRTY_INPUTS="$(git -C "$INSTALL_DIR" status --porcelain --untracked-files=no -- VERSION skills/)"
    if [ -n "$DIRTY_INPUTS" ]; then
        echo "⏭️  Skipping wrapper regeneration: the generator's inputs have uncommitted changes:"
        printf '     %s\n' "$DIRTY_INPUTS"
        echo "     Clean them with: git -C ~/ai-skills checkout -- VERSION skills/"
        echo "     (or discard every local change with: cd ~/ai-skills && ./update.sh --force)"
    else
        echo "🔧 Regenerating tool wrappers..."
        # Not `generate.sh && echo`: under set -e a failure on the left of && is swallowed and the
        # script carries on as if the wrappers were regenerated.
        if GEN_OUT="$(bash "$INSTALL_DIR/generate.sh" 2>&1)"; then
            echo "  ✅ Wrappers regenerated."
        else
            GEN_RC=$?
            printf '%s\n' "$GEN_OUT"
            echo "  ❌ generate.sh failed (exit $GEN_RC). The pull succeeded; the wrappers were not regenerated."
            exit "$GEN_RC"
        fi
    fi
fi

echo ""
if [ "$BEFORE" = "$AFTER" ]; then
    echo "✅ Already up to date (v$(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo '?'))."
else
    echo "✅ Updated to v$(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo '?'):"
    git -C "$INSTALL_DIR" --no-pager log --oneline "$BEFORE..$AFTER"
    echo ""
    echo "↻ Restart your AI tool — global rules (CLAUDE.md @-includes) load at session start."
fi
