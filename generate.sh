#!/usr/bin/env bash
# generate.sh — Generates tool-specific wrappers from the canonical skills/ directory.
#
# Source of truth: skills/<name>/SKILL.md (self-contained, open Agent Skills standard).
# Generated outputs (committed for backward compatibility):
#   claude/skills/<name>/SKILL.md          thin wrapper → ~/ai-skills/skills/<name>/SKILL.md
#   codex/skills/<name>/AGENTS.md          @-include of the canonical SKILL.md
#   cursor/rules/<name>.mdc                content inlined (Cursor has no file includes)
#   copilot/instructions/<name>.instructions.md  markdown link to the canonical SKILL.md
#   plugins/<group>/                       category-grouped Claude Code plugins (skills copied;
#                                          group = metadata.category, git+process -> workflow)
#
# Usage: ./generate.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="${SCRIPT_DIR}/skills"
CLAUDE_OUT="${SCRIPT_DIR}/claude/skills"
CODEX_OUT="${SCRIPT_DIR}/codex/skills"
CURSOR_OUT="${SCRIPT_DIR}/cursor/rules"
COPILOT_OUT="${SCRIPT_DIR}/copilot/instructions"

[ -d "$SKILLS" ] || { echo "❌ skills/ directory not found."; exit 1; }

mkdir -p "$CURSOR_OUT" "$COPILOT_OUT"

# Extract the YAML frontmatter block (including delimiters) from a SKILL.md
frontmatter() {
    awk 'NR==1 && $0=="---"{inFM=1; print; next} inFM && $0=="---"{print; exit} inFM{print}' "$1"
}

# Extract the body (everything after the closing frontmatter delimiter)
body() {
    awk 'NR==1 && $0=="---"{inFM=1; next} inFM && $0=="---"{inFM=0; started=1; next} started{print}' "$1"
}

# Extract a frontmatter field value (e.g. description).
# Handles both inline values and folded block scalars (>-).
field() {
    awk -v key="$2" '
        $0 ~ "^" key ":" {
            val = $0
            sub("^" key ": *", "", val)
            if (val == ">-" || val == ">" || val == "|" || val == "|-") {
                inBlock = 1; next
            }
            print val; exit
        }
        inBlock {
            if ($0 ~ /^[^ ]/) exit
            line = $0
            sub(/^ +/, "", line)
            printf "%s%s", (printed ? " " : ""), line
            printed = 1
        }
        END { if (printed) print "" }
    ' "$1"
}

generated=0

# Codex global index (regenerated in full)
CODEX_INDEX="${SCRIPT_DIR}/codex/AGENTS.md"
{
    echo "# AI Skills — Codex Configuration"
    echo ""
    echo "This directory contains skill wrappers for OpenAI Codex CLI."
    echo ""
    echo "Each skill @-includes the canonical skill from \`skills/<name>/SKILL.md\` — no duplication."
    echo ""
    echo "## Available Skills"
    echo ""
    echo "| Skill | Path |"
    echo "|-------|------|"
} > "$CODEX_INDEX"

for skill_md in "$SKILLS"/*/SKILL.md; do
    [ -f "$skill_md" ] || continue
    skill_dir="$(dirname "$skill_md")"
    name="$(basename "$skill_dir")"
    description="$(field "$skill_md" description)"

    has_refs=0
    [ -d "$skill_dir/references" ] && has_refs=1

    # --- Claude Code (legacy path for pre-1.0 installs configured via ~/.claude/CLAUDE.md) ---
    mkdir -p "$CLAUDE_OUT/$name"
    {
        frontmatter "$skill_md"
        echo ""
        echo "Read and follow all instructions in ~/ai-skills/skills/${name}/SKILL.md"
        if [ "$has_refs" -eq 1 ]; then
            echo ""
            echo "Reference files are in ~/ai-skills/skills/${name}/references/ — read them when the skill instructions point to them."
        fi
    } > "$CLAUDE_OUT/$name/SKILL.md"

    # --- OpenAI Codex ---
    mkdir -p "$CODEX_OUT/$name"
    {
        echo "# ${name}"
        echo ""
        echo "@../../skills/${name}/SKILL.md"
    } > "$CODEX_OUT/$name/AGENTS.md"

    # --- Cursor (content inlined) ---
    {
        cat <<HEADER
---
description: >-
  ${description}
alwaysApply: false
---

HEADER
        body "$skill_md"
    } > "$CURSOR_OUT/${name}.mdc"

    # --- GitHub Copilot ---
    {
        echo "# ${name}"
        echo ""
        echo "Follow the instructions in [SKILL.md](../../skills/${name}/SKILL.md)"
        if [ "$has_refs" -eq 1 ]; then
            echo ""
            echo "Reference files: [references/](../../skills/${name}/references/)"
        fi
    } > "$COPILOT_OUT/${name}.instructions.md"

    echo "| \`${name}\` | \`codex/skills/${name}/AGENTS.md\` |" >> "$CODEX_INDEX"

    generated=$((generated + 1))
done

{
    echo ""
    echo "## Setup"
    echo ""
    echo "Configure Codex to use these skills by adding the skill paths to your \`~/.codex/config.toml\` or referencing them from your project's \`AGENTS.md\`."
} >> "$CODEX_INDEX"

# ── Category-grouped Claude Code plugins ────────────────────────────────────
# One plugin per skill group so projects enable ONLY coherent sets
# (enabledPlugins in .claude/settings.json) instead of the full bundle.
PLUGINS_OUT="${SCRIPT_DIR}/plugins"
rm -rf "$PLUGINS_OUT"
declare -A GROUP_DESC=(
  [backend]="Backend service conventions and resilience (python-rest-api, backend-resilience)"
  [testing]="Adversarial and API testing (bug-hunter, api-resilience-testing)"
  [fivem]="FiveM/CitizenFX Lua conventions and resilience (fivem-lua, fivem-fallback)"
  [game]="React Three Fiber skills (10 topics)"
  [devops]="Kubernetes/Helm skills (helm-migration)"
  [docs]="Documentation generation (documentation)"
  [workflow]="Commit format and OpenSpec spec-driven workflow (conventional-commit, openspec, openspec-drivezone)"
  [nui]="FiveM/RedM NUI React conventions — bridge, CEF quirks, tokens design system (fivem-nui-react)"
  [frontend]="React SPA API-client conventions — typed envelope, auth store, realtime facade (react-api-client)"
  [tooling]="AI-assistant developer tooling — Claude Code status line setup and customization (claude-statusline)"
)

group_of() {
  case "$1" in
    git|process) echo "workflow" ;;
    *) echo "$1" ;;
  esac
}

for skill_md in "$SKILLS"/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  cat="$(grep -m1 '^  category:' "$skill_md" | sed 's/^  category: *//')"
  group="$(group_of "$cat")"
  mkdir -p "$PLUGINS_OUT/$group/skills"
  cp -r --no-preserve=mode "$skill_dir" "$PLUGINS_OUT/$group/skills/$name"
done

VERSION_STR="$(tr -d '[:space:]' < "${SCRIPT_DIR}/VERSION" 2>/dev/null || echo 0.0.0)"
plugin_count=0
for gdir in "$PLUGINS_OUT"/*/; do
  group="$(basename "$gdir")"
  mkdir -p "$gdir/.claude-plugin"
  cat > "$gdir/.claude-plugin/plugin.json" <<PLUGIN
{
  "name": "ai-skills-${group}",
  "displayName": "AI Skills — ${group}",
  "version": "${VERSION_STR}",
  "description": "${GROUP_DESC[$group]:-Skill group ${group}}",
  "author": { "name": "didevlab", "url": "https://github.com/solvelab" },
  "repository": "https://github.com/solvelab/ai-skills",
  "license": "MIT"
}
PLUGIN
  plugin_count=$((plugin_count + 1))
done

echo "Generated wrappers for ${generated} skills:"
echo "  claude/skills/  codex/skills/  cursor/rules/  copilot/instructions/"
echo "Generated ${plugin_count} category plugins in plugins/"
