#!/usr/bin/env bash
# generate.sh — Generates tool-specific wrappers from the canonical skills/ directory.
#
# Source of truth: skills/<name>/SKILL.md (self-contained, open Agent Skills standard).
# Generated outputs (committed for backward compatibility):
#   claude/skills/<name>/SKILL.md          thin wrapper → ~/ai-skills/skills/<name>/SKILL.md
#   codex/skills/<name>/AGENTS.md          @-include of the canonical SKILL.md
#   cursor/rules/<name>.mdc                content inlined (Cursor has no file includes);
#                                          references/ linked by repository URL
#   copilot/instructions/<name>.instructions.md  markdown link to the canonical SKILL.md;
#                                          references/ linked by repository URL
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

# VERSION is validated here, before the first file is written, so that a malformed value never
# reaches a generated manifest: `2.15.1dirtychange` once did, because the read below only stripped
# whitespace. The regex is anchored at both ends and is the same literal scripts/set-version.sh
# uses — the two readers must agree on what a version is.
SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'
VERSION_STR="$(tr -d '[:space:]' < "${SCRIPT_DIR}/VERSION" 2>/dev/null || true)"
[[ "$VERSION_STR" =~ $SEMVER_RE ]] || {
    echo "❌ VERSION is '${VERSION_STR}' — expected MAJOR.MINOR.PATCH with an optional -prerelease suffix. Nothing was written."
    exit 1
}

# The theme is the ONLY hand-written part of a plugin's published description. The skill names and
# their count are read from plugins/<group>/skills/ at generation time, so a skill that changes
# category moves in every published description on the next run. Keep names and numbers out of
# these strings: scripts/validate-repo-hygiene.py (H3) compares the generated parenthetical against
# the tree, and a name here would be published twice and drift once.
declare -A GROUP_THEME=(
  [backend]="Backend service conventions, dependency resilience, observability and log-event collection"
  [testing]="Adversarial testing rite and REST negative/fuzz/contract testing"
  [fivem]="FiveM/CitizenFX Lua conventions and Lua-side resilience patterns"
  [game]="React Three Fiber and AssettoServer game-dev conventions"
  [devops]="Kubernetes/Helm migration, cluster resource tuning and AssettoServer operations"
  [docs]="Three-tier project documentation generation"
  [workflow]="Commit format, OpenSpec spec-driven workflow, the backlog rite, the anti-guessing rite and the code-locale rule"
  [nui]="FiveM/RedM NUI React conventions — Lua↔React bridge, CEF rendering quirks, tokens design system"
  [frontend]="React SPA API-client conventions and physically-grounded SVG/CSS animation"
  [tooling]="AI-assistant developer tooling — Claude Code status line setup and customization"
)

group_of() {
  case "$1" in
    git|process) echo "workflow" ;;
    *) echo "$1" ;;
  esac
}

category_of() {
  grep -m1 '^  category:' "$1" | sed 's/^  category: *//'
}

# Every plugin group the tree will produce must already have a theme, checked HERE — before the
# first mkdir/>, before `rm -rf plugins/` — so that a new category stops the generator with the
# working tree untouched, the same guarantee the VERSION guard gives. Checked inside the plugins/
# loop (as it once was) the failure came after the wrappers were written and after plugins/ was
# wiped, leaving the tree half-generated.
for skill_md in "$SKILLS"/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  group="$(group_of "$(category_of "$skill_md")")"
  [[ -v GROUP_THEME[$group] ]] || {
    echo "❌ generate.sh: no GROUP_THEME for plugin group '${group}' (from $(basename "$(dirname "$skill_md")")/SKILL.md) — add its theme to GROUP_THEME in generate.sh. Nothing was written." >&2
    exit 1
  }
done

mkdir -p "$CURSOR_OUT" "$COPILOT_OUT"

# The Cursor and Copilot wrappers are the two outputs the README tells users to COPY into a project
# (`cp cursor/rules/*.mdc .cursor/rules/`), so a path relative to this tree (`../../skills/<name>/`)
# dangles the moment the file leaves the checkout — measured on 30 of 35 rules (issue #121). Their
# references/ links therefore point at the repository, not at the tree. claude/ (symlink into the
# clone), codex/ (@-include, read in place) and plugins/ (the skill copied whole) keep their paths.
REPO_BLOB_URL="https://github.com/solvelab/ai-skills/blob/master"
REPO_TREE_URL="https://github.com/solvelab/ai-skills/tree/master"

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
        # Cursor has no file includes, and the .mdc is copied out of this tree, so a relative
        # "references/x.md" link would dangle twice over. Links are rewritten to the repository URL;
        # the sed touches only markdown links — inline `references/x.md` mentions in the prose stay
        # as written, which is why the line below tells the reader where that directory lives.
        if [ "$has_refs" -eq 1 ]; then
            echo "Reference files (\`references/…\` below) live at ${REPO_TREE_URL}/skills/${name}/references/"
            echo ""
        fi
        body "$skill_md" | sed -E "s#\\]\\(references/#](${REPO_BLOB_URL}/skills/${name}/references/#g"
    } > "$CURSOR_OUT/${name}.mdc"

    # --- GitHub Copilot ---
    {
        echo "# ${name}"
        echo ""
        echo "Follow the instructions in [SKILL.md](../../skills/${name}/SKILL.md)"
        if [ "$has_refs" -eq 1 ]; then
            echo ""
            echo "Reference files: [references/](${REPO_TREE_URL}/skills/${name}/references/)"
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

for skill_md in "$SKILLS"/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  group="$(group_of "$(category_of "$skill_md")")"
  mkdir -p "$PLUGINS_OUT/$group/skills"
  cp -r --no-preserve=mode "$skill_dir" "$PLUGINS_OUT/$group/skills/$name"
done

# "<theme> (<N> skills: <names>)" — names sorted under LC_ALL=C so the output is identical on every
# machine and a second run produces no diff. The theme lookup is guarded a second time on purpose,
# even though the pre-write check above already refused any group without one: the old
# `:-Skill group <g>` fallback would have published a placeholder for a new category without a
# word, and this is the line that would do it again if the check above were ever removed.
group_description() {
  local group="$1" names count
  [[ -v GROUP_THEME[$group] ]] || {
    echo "❌ generate.sh: no GROUP_THEME for plugin group '${group}' — add its theme to GROUP_THEME in generate.sh." >&2
    return 1
  }
  names="$(ls -1 "$PLUGINS_OUT/$group/skills" | LC_ALL=C sort | paste -sd, - | sed 's/,/, /g')"
  count="$(ls -1 "$PLUGINS_OUT/$group/skills" | wc -l | tr -d ' ')"
  printf '%s (%s %s: %s)' "${GROUP_THEME[$group]}" "$count" "$([ "$count" -eq 1 ] && echo skill || echo skills)" "$names"
}

plugin_count=0
group_args=()
for gdir in "$PLUGINS_OUT"/*/; do
  group="$(basename "$gdir")"
  description="$(group_description "$group")"
  mkdir -p "$gdir/.claude-plugin"
  cat > "$gdir/.claude-plugin/plugin.json" <<PLUGIN
{
  "name": "ai-skills-${group}",
  "displayName": "AI Skills — ${group}",
  "version": "${VERSION_STR}",
  "description": "${description}",
  "author": { "name": "didevlab", "url": "https://github.com/solvelab" },
  "repository": "https://github.com/solvelab/ai-skills",
  "license": "MIT"
}
PLUGIN
  group_args+=("$group" "$description" "${GROUP_THEME[$group]}")
  plugin_count=$((plugin_count + 1))
done

# The marketplace and the root manifest are hand-written files, but their `description` fields say
# the same thing the per-group manifests say, so they are rewritten here from the same data. Only
# `description` is touched: `version` stays owned by scripts/set-version.sh, which runs its sed
# BEFORE calling this script, and the JSON round-trip below reproduces the file byte for byte
# (measured), so the `"version": "X.Y.Z"` form that sed matches survives and a second run is a no-op.
# Every plugin entry must map to a group in the tree and every group must have an entry: adding or
# removing a plugin is a human decision, so either mismatch fails instead of being papered over.
python3 - "$SCRIPT_DIR" "$generated" "$plugin_count" "${group_args[@]}" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
total_skills, plugin_count = int(sys.argv[2]), int(sys.argv[3])
rest = sys.argv[4:]
groups = {rest[i]: (rest[i + 1], rest[i + 2]) for i in range(0, len(rest), 3)}


def rewrite(path: Path, mutate) -> None:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    mutate(data)
    out = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if out != raw:
        path.write_text(out, encoding="utf-8")


def marketplace(data: dict) -> None:
    seen = set()
    for entry in data["plugins"]:
        source = entry.get("source", "")
        if source == "./":
            entry["description"] = (
                f"FULL bundle (all {total_skills} skills). Prefer the per-domain plugins — "
                "enable only what fits the project."
            )
            continue
        group = source.removeprefix("./plugins/")
        if group not in groups:
            sys.exit(f"❌ generate.sh: marketplace entry '{entry.get('name')}' points at '{source}', "
                     "which is not a plugin group in plugins/.")
        entry["description"] = groups[group][0]
        seen.add(group)
    missing = sorted(set(groups) - seen)
    if missing:
        sys.exit(f"❌ generate.sh: plugin group(s) with no marketplace entry: {', '.join(missing)} — "
                 "add the entry to .claude-plugin/marketplace.json.")


def root_manifest(data: dict) -> None:
    themes = "; ".join(f"{g}: {groups[g][1]}" for g in sorted(groups))
    data["description"] = (
        f"Reusable AI skills for coding assistants — all {total_skills} skills across "
        f"{plugin_count} per-domain plugins: {themes}."
    )


rewrite(root / ".claude-plugin" / "marketplace.json", marketplace)
rewrite(root / ".claude-plugin" / "plugin.json", root_manifest)
PY

echo "Generated wrappers for ${generated} skills:"
echo "  claude/skills/  codex/skills/  cursor/rules/  copilot/instructions/"
echo "Generated ${plugin_count} category plugins in plugins/ (descriptions derived from the tree)"
