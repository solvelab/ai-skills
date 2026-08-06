## 1. Establish that accumulation is necessary

- [x] 1.1 Confirm the segment reads `context_window.current_usage.*` (per turn)
- [x] 1.2 Confirm no cumulative token field exists in the payload
- [x] 1.3 Confirm `session_id` is stable and `prompt_id` moves once per turn

## 2. Implement

- [x] 2.1 Parse `session_id` and `prompt_id` out of the payload
- [x] 2.2 State file keyed on `session_id`
- [x] 2.3 Bank a turn only when `prompt_id` changes
- [x] 2.4 Display banked + in-flight
- [x] 2.5 Bank cost per turn at that turn's rates
- [x] 2.6 Prune state older than 30 days on the first render of a new session

## 3. Verify

- [x] 3.1 Three turns accumulate: 121k -> 242k -> 363k
- [x] 3.2 Re-rendering the same turn does not move the total
- [x] 3.3 No `prompt_id`: falls back to the per-turn display, no crash
- [x] 3.4 No `session_id`: no state written, no crash
- [x] 3.5 Model switch mid-session does not reprice history ($0.36 + $0.04)
- [x] 3.6 Corrupt state file is ignored and self-heals
- [x] 3.7 `bash -n` clean

## 4. Document and sync

- [x] 4.1 `fields.md` records that no cumulative token field exists and how to accumulate one
- [x] 4.2 Shipped `statusline.sh` matches the installed one
- [x] 4.3 `claude-statusline` bumped to 1.2.0

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers unchanged
- [x] Q.4 No duplicated doctrine: bounded-state reasoning links `log-event-collector`, not restated
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 Description states no policy the body contradicts
- [x] Q.7 No README change — the script's segments are unchanged in shape

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate cumulative-statusline-tokens --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync
- [x] V.4 `scripts/validate-skills.py` 0 findings across 32 skills
- [x] V.5 `scripts/selftest-validate-skills.py` 12/12
- [x] V.6 `scripts/scan-secrets.py` clean
- [x] V.7 `openspec archive cumulative-statusline-tokens --yes` after review
