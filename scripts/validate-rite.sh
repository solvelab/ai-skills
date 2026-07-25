#!/usr/bin/env bash
# Hard gate for the skills-rite OpenSpec schema.
#
# `openspec validate --strict` (v1.6.0) checks delta-spec format but NOT custom
# template sections, so the schema's mandatory groups would be advisory only.
# This script makes them structural: every active change must carry the gates
# before it can merge or archive.
#
# Usage: scripts/validate-rite.sh   (from repo root; CI runs it on every PR)
set -uo pipefail

CHANGES_DIR="openspec/changes"
fail=0

for dir in "$CHANGES_DIR"/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  [ "$name" = "archive" ] && continue

  tasks="$dir/tasks.md"
  if [ -f "$tasks" ]; then
    grep -q 'Quality Gates (MANDATORY)' "$tasks" || {
      echo "::error file=$tasks::Missing mandatory group 'Quality Gates (MANDATORY)'"; fail=1; }
    grep -q 'Validation & Closure (MANDATORY)' "$tasks" || {
      echo "::error file=$tasks::Missing mandatory group 'Validation & Closure (MANDATORY)'"; fail=1; }
    last_group="$(grep '^## ' "$tasks" | tail -1)"
    case "$last_group" in
      *"Validation & Closure (MANDATORY)"*) ;;
      *) echo "::error file=$tasks::'Validation & Closure (MANDATORY)' must be the LAST task group (found last: ${last_group:-none})"; fail=1 ;;
    esac
  fi

  design="$dir/design.md"
  if [ -f "$design" ]; then
    grep -q 'Canonical Home & Cross-Links (MANDATORY)' "$design" || {
      echo "::error file=$design::Missing mandatory section 'Canonical Home & Cross-Links (MANDATORY)'"; fail=1; }
  fi
done

if command -v openspec >/dev/null 2>&1; then
  openspec validate --all --strict || fail=1
else
  npx -y @fission-ai/openspec@latest validate --all --strict || fail=1
fi

if [ "$fail" -ne 0 ]; then
  echo "rite gate FAILED"
  exit 1
fi
echo "rite gate OK"
