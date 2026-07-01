#!/usr/bin/env bash
# set-version.sh — Propagates a version to every file that carries one.
# Single place where the version is written; called by semantic-release
# (see .releaserc.json "prepareCmd") so releases stay coherent.
#
# Usage: scripts/set-version.sh <X.Y.Z>
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

NEW="${1:-}"
[[ "$NEW" =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]] || { echo "❌ Usage: scripts/set-version.sh <X.Y.Z>"; exit 1; }

CURRENT="$(tr -d '[:space:]' < VERSION)"

printf '%s\n' "$NEW" > VERSION
sed -i "s/\"version\": \"$CURRENT\"/\"version\": \"$NEW\"/" .claude-plugin/plugin.json
sed -i "s/\"version\": \"$CURRENT\"/\"version\": \"$NEW\"/" .claude-plugin/marketplace.json

# Wrappers must always match skills/ at release time
bash generate.sh >/dev/null

# Coherence check
for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json; do
    grep -q "\"version\": \"$NEW\"" "$f" || { echo "❌ Version not propagated to $f"; exit 1; }
done

echo "✅ Version set: $CURRENT → $NEW"
