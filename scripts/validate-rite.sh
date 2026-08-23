#!/usr/bin/env bash
# Hard gate for the skills-rite OpenSpec schema.
#
# `openspec validate --strict` (v1.6.0) checks delta-spec format but NOT custom
# template sections, so the schema's mandatory groups would be advisory only.
# This script makes them structural: every active change must carry the gates
# before it can merge or archive.
#
# KNOWN LIMIT: this checks that the gate SECTIONS are present and correctly
# positioned, and — through validate-spec-rite.py — that a change EXISTS at all.
# It cannot check that either was earned: a ticked box with no probe behind it
# looks identical to one with, and a change scaffolded to satisfy the gate passes
# it. Existence is not honesty. The gate makes both a required, reviewable
# artifact; the review is what judges them.
#
# Usage: scripts/validate-rite.sh              (from repo root; CI runs it on every PR)
#        scripts/validate-rite.sh --selftest   (inject one defect per rule the
#                                               new spec-rite check owns)
set -uo pipefail

CHANGES_DIR="openspec/changes"
fail=0

if [ "${1:-}" = "--selftest" ]; then
  exec python3 scripts/validate-spec-rite.py --selftest
fi

for dir in "$CHANGES_DIR"/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  [ "$name" = "archive" ] && continue

  tasks="$dir/tasks.md"
  if [ -f "$tasks" ]; then
    # Evidence & Sources lives in tasks.md, not design.md, on purpose: design.md is optional
    # (guarded by `[ -f ]` below), so a change without one would silently escape an evidence
    # gate placed there. tasks.md always exists — the schema tracks it for the apply phase.
    grep -q 'Evidence & Sources (MANDATORY)' "$tasks" || {
      echo "::error file=$tasks::Missing mandatory group 'Evidence & Sources (MANDATORY)'"; fail=1; }
    first_group="$(grep '^## ' "$tasks" | head -1)"
    case "$first_group" in
      *"Evidence & Sources (MANDATORY)"*) ;;
      *) echo "::error file=$tasks::'Evidence & Sources (MANDATORY)' must be the FIRST task group (found first: ${first_group:-none})"; fail=1 ;;
    esac
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

# Evidence shape of the mandatory groups + the density report. Separate file because it is a
# different KIND of check: this script asks whether the gate sections exist, that one asks whether
# a ticked box says what it ran. Its own header declares what it cannot do.
python3 scripts/validate-rite-evidence.py || fail=1

# Whether a change exists at all. Separate again, and for the reason the loop above makes obvious:
# every check up to here iterates over active changes, so a pull request that opened none passes
# them all vacuously. This one reads the diff instead of the changes directory.
python3 scripts/validate-spec-rite.py || fail=1

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
