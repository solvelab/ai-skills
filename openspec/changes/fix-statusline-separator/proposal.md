# Change: Fix the separator bug that silently reset the status line's session total

## Why

#57 made the status line's token segment a session total. It shipped with a defect that resets that
total, reported from real use: the figure read `$4.XX` and then dropped to `$0.87`.

**Cause.** Both the payload parse and the state file were split with `IFS=$'\t'`. Tab is an IFS
*whitespace* character, so bash collapses runs of it and **drops empty fields**, shifting every later
field left. Demonstrated:

```
printf 'a\tb\t\td\n' | { IFS=$'\t' read -r F1 F2 F3 F4; ... }
  →  F1=[a] F2=[b] F3=[d] F4=[]        # expected F3=[] F4=[d]
```

Two consequences, both observed in the live state directory:

1. **The state file starts with `LAST_PROMPT`, which is empty on the first write.** On the next read
   that empty field vanished, so every value shifted one slot — the accumulator read garbage and the
   totals reset. That is the `$4.XX → $0.87` the user saw.
2. **The payload parse shifted too.** With `session_id` absent and `prompt_id` present, `SESSION_ID`
   received the prompt id — a state file literally named `x` was found in the directory, keyed on a
   prompt id instead of a session.

`#57`'s own tests missed it because every synthetic payload supplied **both** ids and the state file
was always freshly written in the same process — the empty-field case never occurred.

## What Changes

- Separator is `\x1f` (unit separator) everywhere — payload parse, state read, state write. It is
  non-whitespace, so `read` preserves empty fields, and it cannot occur in the data.
- The whole accumulation block was rewritten as one unit rather than patched line by line, after
  three partial edits left the read, the write and a guard on **three different separators** —
  which broke accumulation entirely until it was caught.
- A state line whose last field is missing or non-numeric is **discarded whole**, so a file in the old
  tab format (or a truncated one) restarts cleanly instead of accumulating onto shifted values.
- `references/fields.md` records the trap next to the accumulation note.

## Verification

Six turns with re-renders, after the fix:

| | displayed |
|---|---|
| turn 1 | `↑ In 121k $0.18` |
| turn 2 (+ re-render) | `↑ In 242k $0.36` — re-render does not move it |
| turn 3 | `↑ In 363k $0.54` |
| turn 4 (+ re-render) | `↑ In 484k $0.72` |
| turn 5 | `↑ In 605k $0.90` |
| turn 6 | `↑ In 726k $1.08` |

Monotonic, and the on-disk record carries 12 separators / 13 fields.

Edge cases, each re-run against the rewritten block:

| condition | behaviour |
|---|---|
| no `prompt_id` | current turn only, no crash |
| no `session_id` | **no file written** — the `x`-style misfiling is gone |
| state file in the old tab format | discarded, restarts cleanly |
| garbage state file | discarded |
| model switched mid-session | `$0.54` + a Haiku turn = `$0.58`, not repriced |

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-catalog`: the shipped status line's session total survives an empty field.

## Impact

- `skills/claude-statusline/references/statusline.sh` and `references/fields.md`; regenerated wrappers.
- Anyone running the #57 version has a total that resets unpredictably; this replaces it.
- A state file written by the #57 version is discarded on first read, so its accumulation is lost.
  `cost.total_cost_usd` (the 💰 segment) was never affected and remains the authoritative session cost.
