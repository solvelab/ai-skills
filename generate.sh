#!/usr/bin/env bash
# generate.sh — Generates inline skill files for tools that don't support file includes.
# Currently: Cursor (.mdc files)
#
# Usage: ./generate.sh
#
# This script reads shared skill content from shared/skills/ and generates
# tool-specific wrappers with the content inlined.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED="${SCRIPT_DIR}/shared/skills"
CURSOR_OUT="${SCRIPT_DIR}/cursor/rules"

mkdir -p "$CURSOR_OUT"

generated=0

# Process top-level skills (documentation, helm-migration)
for content_file in "$SHARED"/*/content.md; do
    [ -f "$content_file" ] || continue
    skill_name=$(basename "$(dirname "$content_file")")

    {
        cat <<HEADER
---
description: ${skill_name} skill — auto-generated from shared/skills/${skill_name}/content.md
alwaysApply: false
---

HEADER
        cat "$content_file"
    } > "$CURSOR_OUT/${skill_name}.mdc"

    generated=$((generated + 1))
done

# Process nested skills (game/r3f-*)
for content_file in "$SHARED"/game/*/content.md; do
    [ -f "$content_file" ] || continue
    skill_name=$(basename "$(dirname "$content_file")")

    {
        cat <<HEADER
---
description: ${skill_name} skill — auto-generated from shared/skills/game/${skill_name}/content.md
alwaysApply: false
---

HEADER
        cat "$content_file"
    } > "$CURSOR_OUT/${skill_name}.mdc"

    generated=$((generated + 1))
done

echo "Generated ${generated} Cursor .mdc files in ${CURSOR_OUT}/"
