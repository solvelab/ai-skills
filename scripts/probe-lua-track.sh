#!/usr/bin/env bash
# Re-establishes everything skills/bug-hunter/references/track-fivem-lua.md claims.
#
# That track publishes three probed facts about the Lua ecosystem, each carrying a date, and a worked
# example of the boundary witness it prescribes in place of the tools that do not exist. A dated fact
# nobody re-measures decays into the guessing this catalog refuses, and an example nobody executes
# rots the same way — so this script re-runs both, from the published text.
#
#   1. `lua-quickcheck` still does not reach the Lua the runtime uses
#   2. no mutation-testing rock exists
#   3. the example in the track runs green, AND turns red when the limit constant moves by one
#
# The third is the one that matters. Running the example green only says it executes; requiring it to
# fail on a moved constant says it WITNESSES the limit, which is the property the track prescribes.
#
# KNOWN LIMIT — what this does NOT do.
#   1. It is NOT in CI, on purpose. It needs `luarocks`, network access and a rock install; a gate on
#      those fails this repository's builds whenever luarocks.org is unreachable, which is a third
#      party deciding whether a documentation change merges. It is a maintainer command.
#   2. It proves the example still behaves; it does not prove the prose around it is still true.
#   3. It reads the FIRST two ```lua blocks of the track. A third block inserted before them changes
#      what runs, which is why a failure to extract is loud rather than silent.
#   4. A missing `luarocks` is a SKIP with a non-success exit, never a pass.
#
# Usage: bash scripts/probe-lua-track.sh     (from anywhere)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRACK="$ROOT/skills/bug-hunter/references/track-fivem-lua.md"
fail=0
note() { printf '  %-8s %s\n' "$1" "$2"; }

[ -f "$TRACK" ] || { note "ERROR" "track not found at $TRACK"; exit 1; }

if ! command -v luarocks >/dev/null 2>&1; then
  note "SKIP" "luarocks is not installed — this is a SKIPPED probe, not a pass."
  note "" "install it (brew install luarocks) and re-run."
  exit 2
fi
eval "$(luarocks path --bin)" 2>/dev/null || true
note "env" "luarocks $(luarocks --version 2>/dev/null | head -1 | awk '{print $2}')  $(lua -v 2>&1)"

# ── 1 and 2: the ecosystem claims the track publishes ──────────────────────────────────────
qc="$(luarocks install lua-quickcheck --check-lua-versions 2>&1 || true)"
if grep -q 'supports only Lua 5.1 and Lua 5.2' <<<"$qc"; then
  note "OK" "claim 1 holds: lua-quickcheck still supports only Lua 5.1 and 5.2"
else
  note "CHANGED" "claim 1 NO LONGER HOLDS — the track says lua-quickcheck supports only 5.1 and 5.2."
  note "" "luarocks now answers: $(head -3 <<<"$qc" | tr '\n' ' ')"
  fail=1
fi

for rock in mutmut mutation-testing luamutant; do
  hits="$(luarocks search "$rock" 2>/dev/null | sed -n '4,$p' | grep -c '[a-z]' || true)"
  if [ "${hits:-0}" -eq 0 ]; then
    note "OK" "claim 2 holds for '$rock': no result"
  else
    note "CHANGED" "claim 2 NO LONGER HOLDS — 'luarocks search $rock' now returns $hits line(s)."
    fail=1
  fi
done

# ── 3: the example, extracted from the track and run ───────────────────────────────────────
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
mkdir -p "$work/spec"
awk '/^```lua$/{n++; inb=1; next} /^```$/{inb=0} inb && n==1 {print > "'"$work"'/clamp.lua"} inb && n==2 {print > "'"$work"'/spec/clamp_spec.lua"}' "$TRACK"

for f in "$work/clamp.lua" "$work/spec/clamp_spec.lua"; do
  if [ ! -s "$f" ]; then
    note "ERROR" "could not extract $(basename "$f") from the track — the fenced lua blocks moved or were renamed"
    exit 1
  fi
done
note "extract" "$(wc -l < "$work/clamp.lua") lines of module, $(wc -l < "$work/spec/clamp_spec.lua") lines of spec"

if ! command -v busted >/dev/null 2>&1; then
  note "SKIP" "busted is not installed — 'luarocks --local install busted' then re-run. Not a pass."
  exit 2
fi

green="$(cd "$work" && busted 2>&1)"
if grep -qE '^[0-9]+ successes / 0 failures / 0 errors' <<<"$green"; then
  note "OK" "the published example runs green: $(grep -oE '[0-9]+ successes / [0-9]+ failures / [0-9]+ errors' <<<"$green")"
else
  note "FAIL" "the published example does not run green:"; sed 's/^/           /' <<<"$green"; fail=1
fi

# The witness: move the limit by one and require red. An example that passes but catches nothing
# demonstrates nothing, which is the whole reason the track publishes the case AT the value.
sed -i 's/^local MIN, MAX = 1, 100$/local MIN, MAX = 1, 101/' "$work/clamp.lua"
red="$(cd "$work" && busted 2>&1)"
if grep -qE '/ 0 failures / 0 errors' <<<"$red"; then
  note "FAIL" "the example did NOT witness the moved limit — MAX 100 -> 101 left the suite green."
  note "" "the case at the value is not doing its job; fix the spec in the track."
  fail=1
else
  note "OK" "the example witnesses the moved limit: $(grep -oE '[0-9]+ successes? / [0-9]+ failures?' <<<"$red" | head -1)"
fi

if [ "$fail" -ne 0 ]; then
  echo "lua-track probe FAILED — the track says something that is no longer true."
  exit 1
fi
echo "lua-track probe OK — every claim the track publishes still holds."
