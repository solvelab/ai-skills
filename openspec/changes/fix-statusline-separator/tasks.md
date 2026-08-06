## 1. Find the real cause

- [x] 1.1 Reproduce the reset from the live state directory (`CUM_IN_COST = 0.869` = the reported $0.87)
- [x] 1.2 Demonstrate that `IFS=$'\t'` drops an empty field and shifts the rest
- [x] 1.3 Confirm the second symptom: a state file named after a `prompt_id` (`x`), from the same shift
- [x] 1.4 Establish why #57's tests missed it — every synthetic payload supplied both ids

## 1b. Find the cause the synthetic tests could not reach

- [x] 1b.1 Instrument the running status line to record every real payload
- [x] 1b.2 Observe that `current_usage` is per API CALL, not per turn: same `prompt_id` produced
      `out = 627 -> 480 -> 587`, then `1854 -> 633` — non-monotonic
- [x] 1b.3 Conclude that banking on `prompt_id` keeps only the last call of each turn
- [x] 1b.4 Re-key the accumulator on the usage tuple; drop `prompt_id` entirely

## 2. Fix

- [x] 2.1 Switch payload parse, state read and state write to `\x1f`
- [x] 2.2 Rewrite the accumulation block as one unit after partial patches left three separators
- [x] 2.3 Discard a record whose tail field is missing or non-numeric
- [x] 2.4 Drop the awk-based field-count guard (`-F'\x1f'` is not portable) in favour of the tail check

## 3. Verify

- [x] 3.1 Six turns accumulate monotonically: 121k → 726k
- [x] 3.2 Re-renders do not move the total
- [x] 3.3 No `prompt_id`: current turn only
- [x] 3.4 No `session_id`: no file written — the `x` misfiling is gone
- [x] 3.5 Old tab-format state: discarded, restarts cleanly
- [x] 3.6 Garbage state: discarded
- [x] 3.7 Model switch: `$0.54` + Haiku turn = `$0.58`, not repriced
- [x] 3.8 `bash -n` clean; on-disk record carries 12 fields
- [x] 3.9 Replay the 9 REAL captured payloads through the real script — monotonic, never dropped,
      identical consecutive payloads bank nothing
- [x] 3.10 Live check in the reporting session: `CUM_CR` 1 815 596 -> 3 634 233 and `CUM_OUT`
      1 004 -> 1 846 across real turns
- [x] 3.11 Capture tap removed from the shipped script

## 4. Document and sync

- [x] 4.1 `fields.md` records the separator trap beside the accumulation note
- [x] 4.2 Shipped script matches the installed one
- [x] 4.3 `claude-statusline` bumped to 1.2.1

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers unchanged
- [x] Q.4 No duplicated doctrine: bounded-state reasoning still links `log-event-collector`
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 Description states no policy the body contradicts
- [x] Q.7 No README change — segments unchanged in shape

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate fix-statusline-separator --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync
- [x] V.4 `scripts/validate-skills.py` 0 findings across 32 skills
- [x] V.5 `scripts/selftest-validate-skills.py` 12/12
- [x] V.6 `scripts/scan-secrets.py` clean
- [ ] V.7 `openspec archive fix-statusline-separator --yes` after review
