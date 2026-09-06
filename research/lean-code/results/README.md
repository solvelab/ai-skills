# results/

Aggregated, anonymised outputs of paid runs land here, written by `run.py --export`:

- `<stamp>-probe.json` — the isolation probe (sentinel, hook side-effects, event vocabulary,
  JSON field names observed on this CLI version).
- `<stamp>-baseline-defects.md` — per-flag defect counts, per-task mean/min/max of `added_lines`,
  `n`, model id, `claude --version`, written by `run.py --classify`.
- `<stamp>-export.json` — the stripped aggregate (`--report --export`): no session id, no result
  text, no uuids, no absolute home paths.

Present since part B of issue #145 (2026-09-05), the two treatment arms of issue #146
(2026-09-06) and the re-measurements of issue #174 (2026-09-06) — read
[`../results.md`](../results.md) first:

| file | what |
|---|---|
| `20260905-211029-probe.json` | isolation probe, 1 arm, Haiku, 3 calls, PASS, $0.0457 |
| `20260905-211512-baseline-defects.md` | the baseline (`opus[1m]`, n=3, 27 cells) as `--classify` wrote it after the flag sanity, plus the hand-read sections: flag sanity before/after, defect classification with the offending diff lines, over-build read from the diffs |
| `20260905-211512-export.json` | the stripped aggregate of the baseline stamp (27 `cells_detail`, 9 `summary` rows) |
| `20260905-230124-probe-skill.json` | probe, 2 arms (`baseline`, the arm then labelled `skill`), before the `skill_visible` criterion existed, PASS, $0.0939 — the probe stamp `20260905-230209` ran under |
| `20260905-230209-block-defects.md` | `--classify` of the `block` arm (relabelled from `skill`; reason in the stamp's `results.json`): `output_contract` 26/27, `lean_marker` 6/27, `class_for_oneliner` 1/27 |
| `20260906-002908-probe-3arms.json` | probe, 3 arms, PASS with `skill_visible` 1/1 in `skill` and 0/1 elsewhere, $0.1951 — the probe stamps `20260906-003055` and `-004535` ran under |
| `20260906-003055-export.json` | `--report` over baseline + block + skill (81 cells): summary, per-task Δ of each treatment arm, group deltas |
| `20260906-003055-skill-defects.md` | `--classify` of the `skill` arm: `output_contract` 24/27, `lean_marker` 8/27, every negative flag 0/27 except `no_check` 3/27 (the structural task) |
| `20260906-004535-export.json` | the +2 repetitions of `reuse-slug` (INCONCLUSIVE clause), 2 cells, 9 and 8 lines |
| `20260906-004737-probe-3arms.json` | probe, 3 arms, after the REWRITE (`rules_sha 8ed6fd0`), PASS, $0.1945 |
| `20260906-004900-export.json` | `--report` over baseline + block + the post-REWRITE `reuse-slug` stamp (57 cells): `reuse-slug skill 9 → 8.667, −3.7 %` — the row that replaces the task in the final table |
| `20260906-013550-probe-3arms.json` | probe, 3 arms, at `rules_sha af49cfa`, before the +2 repetitions of `cache` and `csv-sum`, PASS with `skill_visible` 1/1 / 0/1 / 0/1, $0.1928 |
| `20260906-013713-export.json` | `--report` over baseline + block + `003055` + the +2 repetitions stamp `013713` (85 cells): `cache` and `csv-sum` aggregated at n=5 (`cache skill 12.667 → 5.4, −57.4 %`; `csv-sum skill 102 → 19.6, −80.8 %`), skill over-build group Δ −34.4 %; `reuse-slug` is pre-REWRITE there — the final table takes it from `004900` |
| `20260906-024406-export.json` | item #174: `--report` over baseline + block `230209` + the block's +2 repetitions of `trace-transfer` (`024406`, 30 and 23 lines; 56 cells): `trace-transfer block 27 → 22.4, −17.0 %` at n=5, block over-build group Δ unchanged at −28.6 % |
| `20260906-lens4-findings.md` | item #174: the review lens on the three real diffs with the **published** skill (master `e7f5fe8`, the widened guard sentence): the 17 finding lines and the three `net:` lines verbatim, per-cell cost — adjudicated in `../results.md` (precision 13/17) |

Two three-arm probes that **failed** (`20260906-002213`: the probe cwd was not a git root;
`20260906-002551`: `init` listed `lean-code` and the model answered `none`) are not kept here; they
live in the scratch space and are cited by path and counts in the change's `tasks.md` (S.3).

The Haiku pilot (`20260905-211056`) is not exported: harness shake-out, never a number.
Workspaces (`runs/<stamp>/<task>__<arm>__<run>/`) stay in the scratch directory and are never committed.
