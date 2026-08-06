# Change: Make the status line's token segment a session total, not a per-turn snapshot

## Why

The status line's `↑ In … · ♻️ … · ↓ Out …` segment reads
`context_window.current_usage.*`, which is the **current turn's** usage. It therefore
resets every turn instead of accumulating, so it answers "what did the last response
cost" when the question worth asking is "what has this session cost so far".

There is no cumulative token field to switch to. `references/fields.md` already records
that `context_window.total_input_tokens` / `total_output_tokens` stopped being cumulative
in v2.1.132, and `cost.total_cost_usd` is the only running total the payload carries — it
is a single number with no input/output or cache breakdown.

So the total has to be accumulated by the script, and the accumulation has one non-obvious
trap: **the status line re-renders many times per turn**. A naive `+=` on every render
multiplies the turn's usage by however many times the UI repainted.

## What Changes

- `references/statusline.sh`: the token segment now shows the **session total**.
  - State lives in `~/.claude/statusline-usage/<session_id>` — `session_id` is documented as
    stable per session, which is exactly what a state filename needs.
  - A turn is banked only when **`prompt_id` changes**, which is the only field that moves
    once per turn. Re-renders of the same turn leave the totals alone.
  - The display is `banked turns + the turn in flight`, so it stays live rather than lagging
    one turn behind.
  - **Costs are banked per turn at that turn's rates**, so switching model mid-session does
    not reprice history.
  - Stale state files are pruned (>30 days) on the first render of a new session — a cheap
    moment, and it stops the directory growing for the life of the machine.
- `references/fields.md`: records that no cumulative token field exists, and how to
  accumulate one correctly.
- `claude-statusline` → 1.2.0.

## Verification

Driven with synthetic payloads, three identical turns of 121k in / 500 out:

| event | displayed |
|---|---|
| turn 1 | `↑ In 121k $0.18 · ↓ Out 500 $0.01` |
| same turn, re-rendered twice | **unchanged** — no multiplication |
| turn 2 (new `prompt_id`) | `↑ In 242k $0.36 · ↓ Out 1k $0.03` |
| turn 3 | `↑ In 363k $0.54 · ↓ Out 2k $0.04` |

Degradation, each checked:

| condition | behaviour |
|---|---|
| no `prompt_id` (older CLI, or before first input) | falls back to the previous per-turn display, no crash |
| no `session_id` | no state written, no crash |
| model switched mid-session | Opus turns held at `$0.36`; a Haiku turn added `$0.04`, not a repriced total |
| corrupt state file | ignored, self-heals on the next write |

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-catalog`: `claude-statusline` ships a status line whose token segment reports the
  session total rather than the last turn.

## Impact

- `skills/claude-statusline/references/statusline.sh` and `references/fields.md`; regenerated
  wrappers. Anyone already running the shipped script gets session totals after copying the
  new version; no configuration change is required.
