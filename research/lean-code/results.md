# Results — what has been measured, and what has not

Part B of issue #145, run by the maintainer on 2026-09-05 with the harness in this directory. Every
number below is copied from a file in [`results/`](results/) or from the run directories in the
scratch space; nothing here is a claim about the `lean-code` skill, because **the skill arm has not
run** (item #146).

| stage | model | cells | spent | verdict |
|---|---|--:|--:|---|
| isolation probe | `claude-haiku-4-5-20251001` | 3 calls | $0.0457 | PASS — sentinel 3/3, hook events 0, caveman marker untouched 3/3 |
| pilot (harness shake-out) | `claude-haiku-4-5-20251001` | 9 (n=1) | $0.5571 | every cell wrote its files; never a result |
| **baseline** | `opus[1m]` → `claude-opus-5[1m]` | 27 (n=3 × 9 tasks) | $9.4529 | measured — table below |
| skill arm | — | — | — | **not yet measured — item #146** |

Claude Code `2.1.261 (Claude Code)`, isolation `settings-sources`, rules sha
`6efed496a66a215903e31bce737ffa5172a55424`, one machine.

## Isolation probe — `results/20260905-211029-probe.json`

`run.py --probe-isolation --model claude-haiku-4-5-20251001` on the `settings-sources` arm:
`sentinel 3/3`, `hook_events_total 0`, `maintainer_hook_events 0`, `caveman_marker_untouched 3/3`,
`caveman_active_absent 3/3`, `hooks_reported 0/3`, `config_dir_wrote []`, `passed: true`. The
event vocabulary the CLI emitted was `assistant`, `rate_limit_event`, `result/success`,
`system/init`, `system/thinking_tokens` — no `system/hook_*` event at all. The result JSON carried
`total_cost_usd`, `num_turns`, `duration_ms`, `modelUsage`, `usage`, `subtype`, `is_error`,
`permission_denials` (21 keys recorded in `result_keys`; the three the stripper removes are not
listed). `skill_listed 0/3` is expected: the probe runs with `--tools ""` (KNOWN LIMIT 4).

## Pilot — Haiku, n=1, harness shake-out only

Nine cells, 9/9 completed (`subtype success` 9/9, `is_error` 0/9, max `duration_ms` 57.3 s of the
300 s limit), `correct` 9/9, `safe` 7/9
(`trace-transfer`: *patched only transfer; withdraw still overdraws*; `fivem-shop-buy`: *qty=2.5
accepted*). It confirmed the JSON field names, that every cell writes `_claude.json`, `_diff.patch`,
`_result.txt`, `_command.txt`, and that all nine scorers run on real output. It is a different
model at n=1 and is **not reported as a number**; it is not in the export.

## Baseline — `opus[1m]`, n=3, 9 tasks — `results/20260905-211512-baseline-defects.md`

27/27 cells completed (`subtype success` 27/27, `is_error` 0/27, max `duration_ms` 158.8 s of the
300 s limit), `correct` 27/27, `safe` 27/27, `--budget-usd 25` not reached ($9.4529). The process
fields `killed`, `returncode` and `wall_s` are not in any kept file: the `--rescore` of 2026-09-05
21:38 rebuilt every cell without carrying them (`run.py` now carries them, `carry_process_fields`;
the two stamps rescored before that lost theirs for good — tasks.md S.3 item 13). `modelUsage` keys in every cell: `claude-opus-5[1m]`
($9.4251) and `claude-haiku-4-5-20251001` ($0.0278, 0.29 %).

| task | n | correct | safe | added mean | min | max | tests written | flags (cells) |
|---|--:|--:|--:|--:|--:|--:|--:|---|
| cache | 3 | 1.0 | 1.0 | 12.7 | 10 | 17 | 1.0 | — |
| csv-sum | 3 | 1.0 | 1.0 | 102 | 81 | 127 | 1.0 | — |
| fastapi-create-item | 3 | 1.0 | 1.0 | 16 | 16 | 16 | 1.0 | — |
| fivem-shop-buy | 3 | 1.0 | 1.0 | 40.3 | 35 | 44 | 1.0 | — |
| react-use-orders (STRUCTURAL) | 3 | 1.0 | 1.0 | 22 | 21 | 23 | 0.0 | `no_check` 3 |
| reuse-slug | 3 | 1.0 | 1.0 | 9 | 9 | 9 | 1.0 | — |
| safe-path | 3 | 1.0 | 1.0 | 67.7 | 59 | 82 | 1.0 | `class_for_oneliner` 3 |
| sql-user | 3 | 1.0 | 1.0 | 7.7 | 7 | 9 | 1.0 | `prose_gt_code` 1 |
| trace-transfer | 3 | 1.0 | 1.0 | 27 | 26 | 28 | 1.0 | `class_for_oneliner` 3 |

Flags over the 27 cells, after the flag sanity: `class_for_oneliner` 6, `no_check` 3,
`prose_gt_code` 1, `new_dependency` 0, `guard_dropped` 0, `patched_caller_only` 0,
`reimplemented_existing` 0, `output_contract` 0, `lean_marker` 0.

What the baseline says on its own (the verdict table needs the second arm):

- **Every guard held.** `safe` 27/27 on the five trust-boundary tasks; root cause 3/3 on
  `trace-transfer` (all three cells fixed the shared `_debit`); `reuse-slug` reused the project's
  `slugify` 3/3; `fastapi-create-item` and `react-use-orders` reused the envelope/`apiClient` 3/3.
- **The over-build is real and concentrated.** `csv-sum` 102 mean lines against a 10-line
  reference; `safe-path` 67.7 against 7; `trace-transfer` 27 against a 2-line guard. `cache`
  (12.7 vs 10), `sql-user` (7.7 vs 3) and `reuse-slug` (9) sit near their references. What was
  built, quoted from the diffs, is in the defect classification of `results/20260905-211512-baseline-defects.md`:
  a custom exception class for a guard (6 cells), speculative input tolerance (6), helper
  decomposition of a short loop (4), type checks nobody asked for (3), and docstring expansion.
- **Dispersion** (max − min over mean): `csv-sum` 45 %, `safe-path` 34 %, `cache` 55 %,
  `fivem-shop-buy` 22 %; the rest ≤ 26 %. The INCONCLUSIVE rule of the protocol (> 50 %) would
  already ask for two more repetitions of `cache` if it were the comparison arm; it is noted, not acted on.

### Flag sanity, before publication

The first `--classify` said `new_dependency 8/27` and `class_for_oneliner 9/27`. Read against
the diffs, every `new_dependency` was `import pytest` in the new test file (production imports were
stdlib only; the `unittest` cells were silent) and three `class_for_oneliner` were a
`unittest.TestCase` subclass in the test file. Both detectors now read production files only
(`run.py`, selftest 140 → 146); the test-side signal is kept as `test_dependency` (8/27) and
`test_class_added` (7/27). After `--rescore` + `--classify` on both stamps: `new_dependency` 0/27
and 0/9, `class_for_oneliner` 6/27 and 0/9; `added_lines`, `correct`, `safe` unchanged. The six
remaining `class_for_oneliner` are `class InsufficientFunds(Exception)` (trace-transfer 3/3) and
`class UnsafeFilenameError(ValueError)` / `UnsafeUploadPath(ValueError)` (safe-path 3/3).

## Skill arm — not yet measured

Item #146 adds the `skill` arm (`skillOverrides.lean-code: on`) under the same CLI version and
model id; `run.py --report` refuses to aggregate otherwise. Until it runs, the SHIP / INCONCLUSIVE /
NO-CLAIM / REWRITE table in [`protocol.md`](protocol.md) has no Δ to read, and no README or
`SKILL.md` may carry a number from this directory.

## What this does not cover

- One model id, one CLI version, one machine, one day; the alias `opus[1m]` is what the settings
  named — `--report` proves the id, not the weights (KNOWN LIMIT 6).
- `react-use-orders` is structural; its `safe` column is the reuse axis and never feeds the gate.
- No cell ran with the maintainer's hooks or plugins — that is the point, and the limit
  (KNOWN LIMIT 3 and 4).
- `added_lines` counts tests separately (`test_added_lines`, mean 27-181 per task) and excludes
  the harness files; `code_loc` drops blank and comment lines.
