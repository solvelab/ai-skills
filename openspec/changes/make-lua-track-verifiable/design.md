# Design — an example the text can run, and a declaration that ages visibly

## Context

The Lua track answers both conditional layers with a probed "no". That answer is correct and dated,
and it has two soft spots: the doctrine it puts in their place is stated without a form, and the
probes behind the "no" are never re-run.

## Goals / Non-Goals

**Goals:**

- One source of truth for the example: the track. The script reads it from there.
- A single command that re-establishes every claim the track publishes, and fails naming the one that
  stopped holding.
- The example proves it catches something, not merely that it runs.

**Non-Goals:**

- A CI gate. The script needs `luarocks`, network access and a rock install.
- Touching the `.NET` track: no SDK here, nothing has changed since the tracks landed.
- Any change to the stack-agnostic doctrine.

## Decisions

**D1 — The example lives in the track and the script extracts it.** A copy under `scripts/` would be
a second source that drifts silently; the drift would be invisible precisely because both would keep
passing. Extraction makes the published text the thing under test.

**D2 — The script proves the witness by breaking the code.** Running the example green says the spec
executes. Moving the limit constant by one and requiring red says the spec *witnesses the limit*,
which is the property the section demands and the only one worth publishing. This is the scoring idea
of `bug-hunter` applied by hand, in an ecosystem with no tool to do it.

**D3 — A missing `luarocks` is a skip, never a pass.** The same rule
`scripts/validate-agents.py` applies to a missing PyYAML: a check that cannot run reports that it did
not run. A script that exits zero when it did nothing is worse than no script.

**D4 — Not in CI, and the header says why.** Wiring it in would make this repository's builds depend
on `luarocks.org` being reachable and on a rock install succeeding. That is a third party's
availability deciding whether a documentation change merges.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Enumerate / generate / score, and the witness a limit owes | `bug-hunter` | already canonical — this change makes its Lua track demonstrate what it prescribes |
| Re-measure a dated claim instead of trusting it; report a skip as a skip | `verify-before-claiming` | link — D3 and the re-probe apply it |
| Do not create a second source for the same content | `lean-code` | link — D1 applies it |
| The trust boundary and runtime rules of the Lua stack | `fivem-lua` | link — already cross-linked from the track |

## Risks / Trade-offs

- **The extraction can break when the track is reworded.** It fails loudly on not finding the blocks,
  rather than passing on an empty extraction — the failure mode that would make the script useless.
- **The example adds length to a short track.** Ten lines of module and five cases; the section
  already asks every reader to write exactly that.
- **A maintainer command can be forgotten.** True, and the alternative — a gate on a third party's
  uptime — is worse. The header names the trade.

## Open questions

- None.
