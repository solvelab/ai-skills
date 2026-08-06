## Context

The shipped status line reports six things; five of them are already session-scoped
(`cost.total_cost_usd`, duration, lines changed, context %, rate limits). The token segment was the
odd one out — it read the current turn and therefore reset every prompt, which made it look like the
session was cheap no matter how long it ran.

## Goals / Non-Goals

**Goals**
- The token and cost figures answer "this session", matching the rest of the line.
- Accumulation survives the way the status line is actually invoked.
- Every failure mode degrades to the old behaviour rather than to a broken line.

**Non-Goals**
- Not replacing `💰 total_cost_usd`. That stays the authoritative session cost; the In/Out split is a
  breakdown, and the two are computed differently on purpose.
- Not persisting anything beyond token counts and their prices. No prompts, no paths, no content.
- Not reconstructing history for sessions already in progress — accumulation starts when the new
  script does.

## Decisions

**D1 — Accumulate in the script, because the payload has nothing to accumulate from.** Documented in
`fields.md` and re-confirmed here: `total_input_tokens` / `total_output_tokens` are the current
context, not a running total, and `cost.total_cost_usd` is a single figure with no input/output or
cache breakdown. There is nothing to read; there is only something to keep.

**D2 — `prompt_id` is the commit key, and this is the whole trick.** The status line re-renders many
times per turn. Keying on anything else — a timestamp, the usage values themselves — either multiplies
a turn or misses one. `prompt_id` moves exactly once per turn, which is the definition of what a turn
boundary is here. Verified by rendering the same turn three times and watching the total not move.

**D3 — Display banked + in-flight.** Committing only on turn change would leave the current response
invisible until the next prompt. Adding the live snapshot on top keeps the number honest while it is
being earned, and the commit then replaces the estimate with the same figure.

**D4 — Bank the cost, not just the tokens.** Re-deriving cost from cumulative tokens would apply the
current model's rate to every historical token, so switching from Opus to Haiku mid-session would
silently rewrite what the earlier turns cost. Pricing each turn as it closes keeps history intact —
checked: an Opus session at `$0.36` grew by `$0.04` when a Haiku turn was added, not to a repriced
total.

**D5 — Key the state on `session_id`, which the reference already recommends for exactly this.** It is
stable per session, unlike `$$`, which changes on every render.

**D6 — Degrade to the old behaviour, never to a broken line.** A status line that errors is worse than
one that shows less. Missing `prompt_id` (older CLI, or before the first input) means nothing is
banked and the display is the current turn — precisely what it did before. Missing `session_id` means
no file is written. A corrupt state file is ignored and overwritten on the next render.

**D7 — Prune on session creation.** Once per session is rare enough that a `find` costs nothing, and
it is the only moment the script knows a new file is appearing. The alternative — pruning on every
render — would put a filesystem walk in a hot path that runs several times a second.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Status line script, its segments and installation | `claude-statusline` | already canonical — token segment reworked |
| The JSON fields the harness passes, and their semantics | `claude-statusline/references/fields.md` | already canonical — records that no cumulative token field exists |
| Bounded state for a long-lived process | `log-event-collector` | link in spirit — same class of defect, different subject; the pruning rule here follows its bounded-ring reasoning |
| Shipped-script state disclosure | `openspec/specs/skills-catalog` | spec delta |

## Risks / Trade-offs

- [State can drift if a session is resumed after the prune window] → 30 days is far beyond a working
  session; a pruned session simply starts counting again, which is the same as a new session.
- [Two Claude Code windows on the same session id would share the file] → they share the session, so
  sharing the total is correct.
- [The In/Out cost split can diverge slightly from `total_cost_usd`] → it always could; they are
  computed from different inputs. The 💰 figure remains authoritative and is unchanged.
