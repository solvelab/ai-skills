# Results — what has been measured, and what the protocol says about it

Items #145 (part B, the baseline) and #146 (the two treatment arms, the review lens), run by the
maintainer on 2026-09-05 and 2026-09-06 with the harness in this directory. Every number below is
recomputed from a file in [`results/`](results/) or from a stamp directory in the scratch space
(`runs/<stamp>/{summary,results}.json`, one directory per cell with `_claude.json`, `_diff.patch`,
`_result.txt`), by `run.py --report`, `run.py --classify` or a script over `results.json`; nothing is
typed from memory. The verdict is read from [`protocol.md`](protocol.md) **by the letter**, and what
the letter does not say is in *Post-hoc observations*, dated, never in the verdict.

| stage | stamp | model | cells | spent | outcome |
|---|---|---|--:|--:|---|
| isolation probe (1 arm) | `20260905-211029` | `claude-haiku-4-5-20251001` | 3 calls | $0.0457 | PASS |
| pilot (harness shake-out) | `20260905-211056` | Haiku | 9 (n=1) | $0.5571 | never a number |
| **baseline** | `20260905-211512` | `opus[1m]` → `claude-opus-5[1m]` | 27 (n=3 × 9) | $9.4529 | measured |
| probe (2 arms, before `skill_visible` existed) | `20260905-230124` | Haiku | 6 calls | $0.0939 | PASS |
| **block** (relabelled from `skill`) | `20260905-230209` | `opus[1m]` | 27 | $9.0828 | measured — always-on block alone |
| probe (3 arms) ×2 | `20260906-002213`, `-002551` | Haiku | 12 calls | $0.3849 | **FAIL** (`skill_visible` 0/1 in `skill`) — not kept in `results/` |
| probe (3 arms) | `20260906-002908` | Haiku | 12 calls | $0.1951 | PASS, `skill_visible` 1/1 / 0/1 / 0/1 |
| **skill** | `20260906-003055` | `opus[1m]` | 27 | $9.2791 | measured |
| skill, `reuse-slug` +2 reps (INCONCLUSIVE clause) | `20260906-004535` | `opus[1m]` | 2 | $0.4940 | measured |
| probe (3 arms), after the REWRITE | `20260906-004737` | Haiku | 12 calls | $0.1945 | PASS |
| **skill**, `reuse-slug` after the REWRITE | `20260906-004900` | `opus[1m]` | 3 | $0.7391 | measured — replaces the task's row |
| probe (3 arms), before the +2 reps | `20260906-013550` | Haiku | 12 calls | $0.1928 | PASS, `skill_visible` 1/1 / 0/1 / 0/1 |
| **skill**, `cache` and `csv-sum` +2 reps (INCONCLUSIVE clause) | `20260906-013713` | `opus[1m]` | 4 | $1.1119 | measured — widens the two rows to n=5 |
| review lens, 3 real diffs, skill loaded | `lens3/` | `opus[1m]` | 3 | $1.4648 | 21 findings, precision 0.76 |

## Method

- **Arms** as `protocol.md` *Arms* defines them (third amendment): `baseline` = the maintainer's
  real `~/.claude/CLAUDE.md` + filtered project settings + sentinel; `block` = baseline + the
  always-on *Lean Code* block (`arms-block.md`, sha256 `81f1633f…7770c7` in `arm.json`);
  `skill` = block + `skills/lean-code` of this checkout copied into every workspace as
  `.claude/skills/lean-code`, `skillOverrides.lean-code = "on"`. Isolation `settings-sources`
  (`--setting-sources project,local`, `acceptEdits`, `--disallowedTools Bash`, 0 hook events in
  every probe call).
- **CLI pinned.** Every stamp records `claude_version: "2.1.261 (Claude Code)"`. Claude Code
  auto-updated to `2.1.263` on 2026-09-06 between the `block` and the `skill` runs; the `skill`
  stamps ran the pinned binary through a `PATH` shim
  (`<scratch>/lean-dev/bin-261/claude -> ~/.local/share/claude/versions/2.1.261`), so `--report`
  accepted the three stamps (it refuses a version or model mismatch).
- **Model.** `--model 'opus[1m]'` in every cell; `model_usage_models` in every cell of every
  stamp is exactly `["claude-haiku-4-5-20251001", "claude-opus-5[1m]"]` (the Haiku share is the
  CLI's own helper calls — 0.29 % of the baseline's cost). `model-check.json` (a one-turn `claude -p`
  under the same settings, $0.0612, 2026-09-06) reports `canonicalModel: "claude-opus-5"` for the
  alias. KNOWN LIMIT 6 stands: same id, not provably the same weights on both days.
- **n** = 3 per task × arm; 9 tasks; in the `skill` arm, **n = 5 on `cache` and `csv-sum`** (the
  three cells of `20260906-003055` plus the +2 repetitions of `20260906-013713`, the INCONCLUSIVE
  clause executed) and the `reuse-slug` row is the post-REWRITE stamp `20260906-004900` (n=3),
  with the pre-REWRITE stamp `20260906-003055` (n=3) and the +2 repetitions `20260906-004535`
  shown alongside — 31 `skill` cells in the final table. `rules_sha` differs between stamps
  (`6efed49`, `4e50922`, `4f6638d`, `8ed6fd0`, `af49cfa`) because it is the sha of the **worktree** ref at
  `--prepare-arms`; the rules file the cells actually read is `~/.claude/CLAUDE.md` →
  `~/ai-skills/claude/global/personal-rules.md` on the **master** checkout, which carries no *Lean
  Code* section (the branch is unmerged) — not frozen, but unchanged in the part that matters
  (KNOWN LIMIT 4).
- **Process.** Every cell of every stamp: `subtype success`, `is_error false`, `killed false`,
  `returncode 0`; longest cell 283.2 s (`block`), 171.4 s (`skill`; 65.0 s in `013713`) of the
  300 s limit; no `--budget-usd` reached; costliest skill cell $0.7157 of the $1.00 per-cell cap
  ($0.3447 in `013713`).

## The three arms, per task — `results/20260906-003055-export.json`, `…-004900-export.json` and `…-013713-export.json`

`added_lines` = the `+N` of production files, tests excluded (protocol *Metrics*). Δ = mean of the
arm relative to the baseline mean; every mean carries its min–max so the spread of a small count is
visible next to it. `correct`/`safe` are 1.0 in every row of every arm (27/27, 27/27 and 31/31
cells; boundary `safe` 15/15, 15/15 and 17/17), so they are not repeated per row. n = 3 unless the
row says otherwise.

| task | base mean (min–max) | block mean (min–max) | Δ block | skill mean (min–max) | Δ skill |
|---|--:|--:|--:|--:|--:|
| cache · OB — n=3 `003055` | 12.667 (10–17) | 6.333 (6–7) | −50.0 % | 5.667 (3–11) | −55.3 % |
| cache · OB — **n=5 after the +2 reps `013713`** (the row that counts) | 12.667 (10–17) | 6.333 (6–7) | −50.0 % | 5.400 (3–11; 3, 3, 5, 5, 11) | −57.4 % |
| csv-sum — n=3 `003055` | 102 (81–127) | 35.667 (32–38) | −65.0 % | 18.333 (11–26) | −82.0 % |
| csv-sum — **n=5 after the +2 reps `013713`** (the row that counts) | 102 (81–127) | 35.667 (32–38) | −65.0 % | 19.600 (11–26; 11, 18, 18, 25, 26) | −80.8 % |
| fastapi-create-item · OB | 16 (16–16) | 17 (16–18) | +6.2 % | 16.667 (16–18) | +4.2 % |
| fivem-shop-buy | 40.333 (35–44) | 29.333 (25–38) | −27.3 % | 24.667 (23–26) | −38.8 % |
| react-use-orders · OB (STRUCTURAL) | 22 (21–23) | 21.667 (21–22) | −1.5 % | 21 (21–21) | −4.5 % |
| reuse-slug — pre-REWRITE `003055` | 9 (9–9) | 9 (9–9) | +0.0 % | 12.333 (9–19) | **+37.0 %** |
| reuse-slug — **post-REWRITE `004900`** (the row that counts) | 9 (9–9) | 9 (9–9) | +0.0 % | 8.667 (8–9) | −3.7 % |
| safe-path · OB | 67.667 (59–82) | 21 (20–22) | −69.0 % | 13.667 (12–16) | −79.8 % |
| sql-user | 7.667 (7–9) | 3 (3–3) | −60.9 % | 3 (3–3) | −60.9 % |
| trace-transfer | 27 (26–28) | 19.667 (10–25) | −27.2 % | 9.667 (8–11) | −64.2 % |

OB = the pre-registered over-build group. `--report` on the three full stamps printed
`block: over-build group mean delta -28.6% over 4 tasks; worst task fastapi-create-item +6.2%` and
`skill: over-build group mean delta -33.9% over 4 tasks; worst task reuse-slug +37.0%`; with
`004900` in place of the `reuse-slug` row the skill's group mean is unchanged (−33.9 %: the task is
not in the group) and its worst task is `fastapi-create-item` +4.2 % (`…-004900-export.json`:
`reuse-slug skill 9 → 8.667 −3.7`). `--report` over baseline + block + `003055` + `013713`
(`…-013713-export.json`, 85 cells; `cache` and `csv-sum` aggregated at n=5, `reuse-slug` still
pre-REWRITE there) printed `skill: over-build group mean delta -34.4% over 4 tasks; worst task
reuse-slug +37.0%` with `cache skill 12.667 → 5.4 −57.4` and `csv-sum skill 102 → 19.6 −80.8`. The
**final skill table** — `cache` and `csv-sum` at n=5, `reuse-slug` from `004900`, the other six
tasks from `003055` — has an over-build group mean Δ of **−34.4 %** (−79.8, −57.4, +4.2, −4.5) and
its worst task is `fastapi-create-item` **+4.2 %**.

Per arm, over the 27 cells of `baseline` and `block` (`results/20260905-211512-baseline-defects.md`,
`…-230209-block-defects.md`) and the **31 cells** of the final `skill` table (`…-003055-skill-defects.md`
recomputed over `results.json` with `004900` in place of `reuse-slug` and `013713` added):

| signal / flag | baseline | block | skill (final, 31 cells) |
|---|--:|--:|--:|
| `output_contract` (`skipped: …, add when …` in the result) | 0/27 | 26/27 | **27/31** = 87.1 % (missing: `cache` run 0 and `trace-transfer` run 0 of `003055`, `reuse-slug` run 1 of `004900`, `cache` run 1 of `013713`) |
| `lean_marker` (`# lean: … -> …` in the diff) | 0/27 | 6/27 | 13/31 |
| `class_for_oneliner` | 6/27 | 1/27 | 0/31 |
| `prose_gt_code` | 1/27 | 3/27 | 0/31 |
| `no_check` (all three are `react-use-orders`, structural) | 3/27 | 3/27 | 3/31 |
| `new_dependency`, `guard_dropped`, `patched_caller_only`, `reimplemented_existing` | 0/27 each | 0/27 each | 0/31 each |
| `trace-transfer` root cause (`fixed shared _debit (withdraw guarded too)`) | 3/3 | 3/3 | 3/3 |
| cells that wrote a test file | 24/27 | 24/27 | 27/31 |
| `test_added_lines`, mean | 83.2 | 45.9 | 31.9 |
| cost / turns per cell, mean | $0.350 / 9.3 | $0.336 / 8.8 | $0.337 / 9.6 |

## The `reuse-slug` story — INCONCLUSIVE, then REWRITE, then re-run

1. Stamp `20260906-003055`, `reuse-slug` skill cells: 9, **19**, 9 → mean 12.333, +37.0 % against
   the baseline's 9; dispersion (max − min)/mean = 81 %. Two protocol rows fire at once: REWRITE
   (*any task above baseline +10%*) and INCONCLUSIVE (*dispersion … exceeds 50% of its mean → +2
   repetitions on those tasks, then re-read*).
2. The +2 repetitions first (`20260906-004535`, $0.4940): 9 and 8. Widened to n=5: 9, 19, 9, 9, 8 →
   mean 10.8, **+20.0 %**, still above the +10 % rule → REWRITE by the letter.
3. What the 19-line cell did (`runs/20260906-003055/reuse-slug__skill__1/_diff.patch`): the same
   8-line `unique_slug` as the other cells, plus a 9-line `if __name__ == '__main__':` block of
   asserts **inside `articles.py`** — "the one runnable check" placed in the product module. Its
   `_result.txt`: *"skipped: no separate `test_*.py` (repo has no test infra — the `__main__`
   asserts are the one runnable check)"*. Logic identical; `added_lines` more than doubled.
4. The REWRITE (commit `8ed6fd0`): the skill's one-check rule now reads *"one small `test_*.py`
   beside the module … An inline `assert`-based `__main__` self-check is for a single-file script
   that nothing imports — a module keeps its check outside itself, so the product file stays the
   minimum"*; the row in `references/upstream.md` records the change and this measurement. The
   always-on block is unchanged.
5. New arms (`rules_sha 8ed6fd0`), new probe `20260906-004737` (PASS, `skill_visible` 1/1),
   re-run of the affected task only, n=3 (`20260906-004900`, $0.7391): 9, 9, 8 → mean 8.667,
   **−3.7 %**, dispersion 12 %; `test_articles.py` in 3/3 cells, `reused project slugify` 3/3.
   Both stamps are kept and both are in the table above.

## The `cache` and `csv-sum` re-read — the INCONCLUSIVE clause executed

1. On the table as it stood after the REWRITE, every SHIP condition held and the INCONCLUSIVE
   dispersion row held at the same time on two `skill` tasks: `cache` 141 % (3, 11, 3; mean 5.667)
   and `csv-sum` 82 % (26, 11, 18; mean 18.333). The row's instruction — *+2 repetitions on those
   tasks, then re-read* — had been applied to `reuse-slug` and not yet to these two, so the verdict
   was read as INCONCLUSIVE (the version of this file at commit `3e79284`).
2. New arms at `rules_sha af49cfa`, probe `20260906-013550` (PASS, `skill_visible` 1/1 / 0/1 /
   0/1, hook events 0, $0.1928), then `--matrix --arms skill --tasks cache,csv-sum --runs 2`, the
   pinned `2.1.261` binary and `opus[1m]` as before → stamp `20260906-013713`, 4 cells, $1.1119,
   `subtype success` 4/4, `killed` 0/4, `correct` 4/4, `safe` 4/4.
3. `cache` +2: **5 and 5** — `from functools import cache` + `@cache` on the existing function, a
   `# lean:` marker on the decorator line, the check in `test_compute.py` (15 and 8 test lines); no
   inline `__main__` block in `compute.py` (`runs/20260906-013713/cache__skill__{0,1}/_diff.patch`).
   Widened to n=5: 3, 3, 5, 5, 11 → mean **5.400** (3–11), Δ **−57.4 %**; dispersion (11 − 3)/5.4 =
   **148 %**.
4. `csv-sum` +2: **25 and 18** — both `csv.DictReader` + `float` + `try/except` around the bad
   row, both a `ValueError` on a missing `amount` column, both a `test_sales.py` (38 and 39 test
   lines); run 0 adds a `logging.warning` per skipped row and an `encoding="utf-8-sig"`, run 1
   skips silently with a `# lean:` marker saying so. Widened to n=5: 11, 18, 18, 25, 26 → mean
   **19.600** (11–26), Δ **−80.8 %**; dispersion (26 − 11)/19.6 = **77 %**.
5. The row does **not** ask the dispersion to fall below 50 % after the widening; it asks for two
   more repetitions and a re-read. Both are done. The remaining spread is recorded below in
   *Post-hoc observations* (7), never in the verdict.

## Verdict, by the letter of `protocol.md`

### `skill` arm (the deliverable of #146)

Read on the final table: `cache` and `csv-sum` at n=5 (`003055` + `013713`), `reuse-slug` from
`004900`, the other six tasks from `003055` — 31 cells.

| row | condition | number | holds? |
|---|---|---|---|
| SHIP | `correct` ≥ baseline on every task | 1.0 → 1.0 on 9/9 tasks (31/31 cells) | yes |
| SHIP | `safe` = 100 % on the five boundary tasks | 17/17 cells (15 + the 2 `csv-sum` reps) | yes |
| SHIP | mean Δ ≤ −30 % over the over-build group | **−34.4 %** (`safe-path` −79.8, `cache` −57.4 at n=5, `fastapi-create-item` +4.2, `react-use-orders` −4.5) | yes |
| SHIP | no task above baseline +10 % | worst `fastapi-create-item` +4.2 % (16 → 16.667; pre-REWRITE `reuse-slug` +37.0 %, −3.7 % after) | yes |
| SHIP | `output_contract` in ≥ 2/3 of skill cells | 27/31 = 87.1 % | yes |
| SHIP | `trace-transfer` root cause 6/6 (baseline 3/3 and skill 3/3) | 3/3 + 3/3 = 6/6 | yes |
| SHIP | `new_dependency` 0/N | 0/31 | yes |
| INCONCLUSIVE | Δ between −15 % and −30 % | −34.4 % | no |
| INCONCLUSIVE | dispersion of a task's `added_lines` > 50 % of its mean → +2 repetitions on those tasks, then re-read | `reuse-slug` 81 % → +2 reps (`004535`), REWRITE, 12 % after; `cache` 141 % → +2 reps (`013713`), 148 % at n=5; `csv-sum` 82 % → +2 reps (`013713`), 77 % at n=5 | **instruction executed on all three tasks; this is the re-read.** The row carries no threshold the widened spread has to fall under |
| REWRITE | any guard dropped | 0/31 | no |
| REWRITE | any task above +10 % | `reuse-slug` +37.0 % → REWRITE applied (`8ed6fd0`) → −3.7 % | closed |
| REWRITE | root cause below baseline | 3/3 vs 3/3 | no |
| REWRITE | a new dependency the baseline did not add | 0/31 | no |

**Verdict: SHIP.** The protocol's row reads, verbatim: *"**SHIP** (a number may appear in the
skill's README) | `correct` ≥ baseline on every task; `safe` = 100% on the five boundary tasks;
mean Δ ≤ −30% over the over-build group and **no** task above baseline +10%; `output_contract` in
≥ 2/3 of skill cells; `trace-transfer` root cause 6/6 (n=3 × 2 arms ≥ baseline, 3/3 in skill);
`new_dependency` 0/N in skill"* — seven conditions, seven hold on the final table above. The
INCONCLUSIVE row reads: *"Δ between −15% and −30%, or the dispersion (max − min) of a task's
`added_lines` exceeds 50% of its mean → +2 repetitions on those tasks, then re-read"* — its Δ
half does not fire (−34.4 %), and its dispersion half fired on three tasks and was executed on all
three: +2 repetitions ran on `reuse-slug` (`004535`), on `cache` and on `csv-sum` (`013713`), and
this section is the re-read. The row says nothing about the dispersion after the widening — it does
not require it to fall under 50 %, and on `cache` (148 %) and `csv-sum` (77 %) it did not; that
spread is described in *Post-hoc observations* (7) as what it is, the noise of a small absolute
count, and is not a verdict condition. No REWRITE row fires: the only one that ever did
(`reuse-slug` +37.0 %) was applied and re-measured at −3.7 %. Per the SHIP row a number may now
appear in the skill's `SKILL.md` and in the catalog README — with its conditions attached (model,
CLI version, n, tasks, dates, metric, min–max) and this file as its source; the number published
is the over-build group Δ the protocol pre-registered, −34.4 %, never the all-nine mean.

### `block` arm (the always-on mechanism alone, reported alongside, never the skill's verdict)

Over-build group mean Δ **−28.6 %** (−69.0, −50.0, +6.2, −1.5) — inside the INCONCLUSIVE band
(−15 % … −30 %); dispersion `trace-transfer` 76 % (10, 25, 24) — INCONCLUSIVE again; worst task
`fastapi-create-item` +6.2 % < +10 %, no guard dropped, root cause 3/3, `new_dependency` 0/27 —
no REWRITE row fires. `output_contract` 26/27, `lean_marker` 6/27. **INCONCLUSIVE** on both
counts; the block was not re-run (it is not the deliverable).

## Post-hoc observations (2026-09-06, after the letter was applied)

Nothing here changes the verdict; it is what the frozen rules do not say.

1. **The pre-registered over-build group is not where the baseline over-built.** The group
   (`safe-path`, `cache`, `fastapi-create-item`, `react-use-orders`) was chosen before the baseline
   ran. Two of its four tasks had no room: `fastapi-create-item` baseline 16 lines (a handler that is
   already the minimum the scorer accepts) and `react-use-orders` 22 (structural). Each pins the
   group mean near 0 and the group lands at −33.9 %. The baseline's over-build sat in `csv-sum`
   (102 lines for a 10-line reference), `safe-path` (67.7), `fivem-shop-buy` (40.3) and
   `trace-transfer` (27) — the skill's Δ there is −80.8, −79.8, −38.8, −64.2 %. Over all nine
   tasks the mean Δ is −42.9 % (skill, final table) and −32.7 % (block); over the five tasks whose
   baseline mean exceeds 20 lines, −53.6 % and −38.0 %. These are descriptive; the verdict reads
   the pre-registered group and only it, and only the group's number is published.
2. **An inline `__main__` self-check is a counting artefact of `added_lines`.** The metric counts
   production files and excludes test paths; a check written *inside* the product module counts in
   full. Both skill-arm outliers that fired the dispersion clause in the over-build group were
   this: `reuse-slug` run 1 (19 vs 9, above) and **`cache` run 1 (11 vs 3)** — the same
   `@functools.cache` one-liner as runs 0 and 2, plus an 8-line `if __name__ == "__main__":` block of
   asserts in `compute.py` (`runs/20260906-003055/cache__skill__1/_diff.patch`). The `csv-sum`
   spread (26 / 11 / 18) is not the artefact: run 0 chose `Decimal`, `logging` and an explicit
   `amount`-header check, run 1 `float` and a bare `try/except`. The REWRITE targets the artefact;
   it was re-run on `reuse-slug` (n=3) and the +2 repetitions of `cache` and `csv-sum` ran on the
   rewritten text: none of the four cells put a check inside the product file (the one `__main__`
   in `013713` is in `test_sales.py`, counted as test lines). The block arm shows no such cell —
   the block text says nothing about where the check lives; the skill text (pre-REWRITE) did, and
   said `__main__` was fine. The 11-line cell stays in the n=5 mean as the metric defines it.
3. **The `block` arm isolates the always-on mechanism.** With the block alone the trailer appears
   in 26/27 cells and `class_for_oneliner` drops 6 → 1; the skill on top moves mostly the tasks
   with room: `trace-transfer` 19.7 → 9.7, `csv-sum` 35.7 → 18.3, `safe-path` 21 → 13.7,
   `fivem-shop-buy` 29.3 → 24.7; `sql-user`, `reuse-slug`, `fastapi`, `react` are the same within a
   line. The `skipped:` trailer is a **block** effect (the block names it), not a skill effect:
   24/27 with the skill vs 26/27 without it.
4. **The protocol has no rule for what follows a REWRITE.** It says REWRITE; it does not say which
   tasks are re-run, at what n, or which stamp counts. The rule that was applied comes from the
   issue, not the protocol — #146 FR3: *"a reescrita re-roda só as tarefas afetadas e mantém os
   dois stamps"* — so: the affected task only, n=3, both stamps kept and both reported. A future
   version of the protocol should carry that sentence; this one is not amended for it (thresholds
   and rows untouched).
5. **The verdict table can be satisfied by two rows at once.** SHIP and INCONCLUSIVE both held
   after the REWRITE. The reading applied (INCONCLUSIVE first, because it is the row with an
   instruction; SHIP on the re-read that follows the instruction) is a reading, recorded here and
   not written into the frozen table. It cost one more probe and four cells ($1.3047) and moved the
   group Δ from −33.9 % to −34.4 %.
6. **The review-lens cells of 2026-09-05 23:19–23:22 (`lens3/`) ran before the three-arm probes**
   (00:22–00:47 the next day), with the skill reached through a symlink
   (`.claude/skills/lean-code -> <worktree>/skills/lean-code`) inside a git root, `--output-format
   json`. That output carries no `init` event, so the skill's load in those three cells is inferred:
   none of the three results carries the *"lean-code isn't in the available-skills list"* disclaimer
   that all six cells of the two earlier lens runs carry, and the layout is the one the probe
   verified 60–90 minutes later (`skill_visible` 1/1). The lens section of `SKILL.md` was not
   touched by the REWRITE (`8ed6fd0`); it was touched once after the measurement, by the FR4
   widening of the self-check guard sentence (`6831e24`, 2026-09-06, *Review lens* below), so the
   text that ships differs from the text the lens ran on by that one sentence, and the lens was
   not re-run on it.
7. **The dispersion that remains after the widening is the noise of a small absolute count.**
   `cache` at n=5 is 3, 3, 5, 5, 11 (mean 5.4): the four low cells write the same two lines —
   `from functools import cache` and `@cache` with a `# lean:` marker — separated by one blank line
   (3) or by three (5), and the one cell with the inline `__main__` block counts 11 — an 8-line
   spread on a 5-line mean is 148 % by the protocol's formula, with the same two-line change in
   every cell (`runs/20260906-{003055,013713}/cache__skill__*/_diff.patch`). `csv-sum` at n=5 is
   11, 18, 18, 25, 26 (mean 19.6, 77 %): the spread is a `logging.warning`, a header check and a
   docstring, on a function whose baseline wrote 81–127 lines. The formula (max − min)/mean is scale-free by design and therefore loud on tasks whose
   mean is a handful of lines; the protocol asks it to trigger repetitions, not to converge. This
   is why every mean in this file carries its min–max, and why the published number is the group
   Δ over four tasks and not a per-task figure.

## Review lens — three real diffs, `lens3/<sha>/out.json`

The lens (`delete:` `stdlib:` `native:` `yagni:` `shrink:`, `net: -N lines possible.`) on the merge
commits of PRs #140, #141, #142, one `claude -p` each on `opus[1m]`, `--setting-sources
project,local`, the skill as a project skill, the diff restricted to the file the protocol names.
Precision = valid / (valid + FP), FP by the five rules of `protocol.md` *Review lens — false-positive
rules*, adjudicated against the diff (`lens3/<sha>/diff.patch`, line numbers are diff lines) and the
PR body (`gh pr view <n> --json body`), which is the oracle for rule 3.

| diff | file | findings | by tag | `net:` | valid | FP |
|---|---|--:|---|--:|--:|--:|
| `49c44d0` (#140) | `claude/global/hooks/locale-rite.py` | 7 | delete 4, yagni 1, shrink 2 | −40 | 4 | 3 |
| `69aaf73` (#141) | `claude/global/hooks/locale-stop-gate.py` | 7 | shrink 4, yagni 3 | −33 | 7 | 0 |
| `b1f527f` (#142) | `skills/code-locale/references/pre-commit-locale.sh` | 7 | shrink 3, yagni 3, delete 1 | −75 | 5 | 2 |
| **total** | | **21** | | | **16** | **5** |

**Precision 16/21 = 0.76 ≥ 0.7.** Read by the literal tag of rule 4 (`yagni:` only), finding 3 of
`49c44d0` is not an FP and precision is 17/21 = 0.81; the conservative count is the one reported.
`net:` 3/3 present; no `stdlib:`/`native:` finding was made, so rule 2 (a function absent from the
pinned runtime) had nothing to judge. **#146 FR4** — *"qualquer `delete:` em selftest/mutante é
FP e corrige o texto da guarda antes de publicar"*: two of the five FPs are exactly that
(`49c44d0` findings 5 and 7, a `delete:` on a selftest case each). The lens text the three cells
ran on guarded the *existence* of a self-check ("never flag it for deletion") but not a case
*inside* a selftest. The guard sentence was widened after the measurement, in commit `6831e24`
(2026-09-06): *"A single smoke test or `assert`-based self-check — and any single case inside a
selftest, a mutant or an injected-defect check — is the minimum, not bloat, never flag it for
deletion: the check is the product."* The lens was **not re-run** on the widened text (no paid
cell after the measurement), so the precision reported here is the one measured on the
pre-widening sentence, with findings 5 and 7 still counted as FP; whether the wider sentence
removes them is an untested claim until the three cells run again.

### `49c44d0` — `locale-rite.py` (+408)

| # | finding | adjudication |
|---|---|---|
| 1 | L213 `delete:` `CONTEXT_LINE_CAP = 200` set, never read | **valid** — `grep -c CONTEXT_LINE_CAP diff.patch` → 1 (the definition) |
| 2 | L253-255, L418-422, L455 `yagni:` `current_mode()` and the `mode` parameter exist only so the selftest avoids `os.environ` | **valid** — `mode` is threaded from `evaluate()` to one call site (`mode if mode is not None else current_mode()`, L455); the PR body describes the selftest, not the parameter |
| 3 | L443-444 `delete:` the `isinstance(anchor, str)` guard — a non-string `old_string` lands in the `except Exception` two lines below | **FP, rule 4** — `anchor` is `tool_input.get("old_string")`, hook input; a guard at that boundary is the carve-out (the rule names `yagni:`; the object is the same) |
| 4 | L457-458 `shrink:` `split_findings()` runs twice per denial (`evaluate()` L457, `deny()` L408) | **valid** — both calls are in the diff; same result, computed once |
| 5 | L475-478 `delete:` the selftest case *"PostToolUse by name is the advisory envelope"* duplicates `post_inform` at L541 | **FP, rule 1** — a `delete:` on a selftest case; the check is the product (and the two payloads differ: `orders/service.py` without mode vs `pt_ident` in inform mode) |
| 6 | L485-…-639 `shrink:` the `print(OK/FAILED) + failed.append` block copy-pasted 11 times → one `record(name, ok)` | **valid** — `grep -c "failed.append" diff.patch` → 12 in the selftest; same output |
| 7 | L641-653 `delete:` the subprocess run proving the default mode reads the environment | **FP, rule 1 and rule 3** — a selftest case; PR #140 body: *"variável de ambiente pelo caminho real"* in the selftest list |

### `69aaf73` — `locale-stop-gate.py` (+652)

| # | finding | adjudication |
|---|---|---|
| 1 | L99-114 `shrink:` 16 lines of minified-bundle fragments in the module docstring → two lines | **valid** — prose in the diff, behaviour untouched; the PR body cites the fragments (`eg`, `PMe`, `LU`) as evidence, not as a KNOWN LIMIT |
| 2 | L234-237, 325-326 `yagni:` `EMPTY_TREE_SHA1` fallback for a `hash-object` that fails only when git is already broken | **valid** — the diff's own comment: *"this constant is only the fallback"*; not in the 11-mutant list of PR #141 (`nested-output … silent-clean-truncation`) |
| 3 | L295-304 `shrink:` `stat().st_size` plus a read → one read, `bool(data) and b"\0" not in data` | **valid, rule 5 checked** — mutant `empty-not-skipped` covers the empty file: the replacement returns `False` on empty data, as before |
| 4 | L307-308, 353, 419 `yagni:` optional `vendored=None` with a single caller, guarded by `is not None`, fed by a forwarding lambda | **valid** — `grep -n vendored diff.patch`: def, docstring, the guard, one call (L419) |
| 5 | L381-395 `shrink:` `remaining_message` hand-rolls what `f.render()` prints and duplicates `block_reason` → one builder | **valid** — the two functions (L381-396) differ in header, cap and the `:0` case only; mutants `silent-truncation`/`silent-clean-truncation` justify that a second-Stop message exists, not that it is built twice |
| 6 | L417 `shrink:` defensive `dict(env)`; nothing downstream mutates it | **valid** — `git_env` is passed to `uncommitted_diff` → `run_git` only (L285-357) |
| 7 | L448, 456 `yagni:` `**extra` on `_fixture_env`, never passed | **valid** — one call, `_fixture_env(td)` (L501) |

### `b1f527f` — `pre-commit-locale.sh` (+217)

The lens opened with *"Patch contains only `skills/code-locale/references/pre-commit-locale.sh`; the
`ci-step.md` and `SKILL.md` changes the commit message describes are not in it"* — correct: the diff
was restricted to the file the protocol names. Not a finding.

| # | finding | adjudication |
|---|---|---|
| 1 | L77-176 `shrink:` 100-line header over 115 lines of code → keep INSTALL, source order and the sha-bump recipe (~25 lines) | **FP, rule 3** — the header's *WHAT THIS HOOK DOES NOT COVER* (L150-176) is the KNOWN LIMIT paragraph; PR #142 body: *"O cabeçalho declara instalação, a ordem das fontes (o pin vale só para o download), e o que não cobre"* and Known gaps *"declarado no cabeçalho e em D2"* |
| 2 | L183-184 `yagni:` `EXTRA_ARGS=()` is an empty knob kept for a `--gate-unknown` later | **valid** — scaffolding "for later" (the diff's own comment: *"once measured"*); the PR table names `EXTRA_ARGS` only as the bash-3.2 bug |
| 3 | L199 `yagni:` `LOCALE_CHECK_SHA256=skip` in-band sentinel to switch the pin off | **valid** — the env var already overrides the digest; the header documents `skip` but no PR paragraph justifies a third way |
| 4 | L219-220 `yagni:` `$AI_SKILLS_HOME` is a second env var for what `$LOCALE_CHECK` does and forces the `case /"${CHECK_REL}"` guard | **valid** — the PR body lists the source order as a feature, not as a mutant or a limit |
| 5 | L246 `delete:` `command -v git` in a hook git itself just launched | **valid** — not a trust-boundary guard |
| 6 | L266-270 `shrink:` `rc` rewritten to a fabricated `70` so the message can print it | **FP, rule 3** — PR #142's review table: *"detector que crasha (exit 1) \| mesmo rodapé falso \| 'the detector itself failed (exit 70, no findings: line)'"* — the line is the fix that table records |
| 7 | L274-277 `shrink:` `[ -n "$output" ] && printf … \| grep -q advisory` → the grep alone | **valid, rule 5 checked** — `grep -q` on empty input is false; same behaviour |

### Two earlier lens runs are invalid for this criterion (escapes)

- `lens/` (2026-09-05, $1.2499, 3 cells) and `lens2/` ($1.5184, 3 cells) ran with the same flags
  and **no project skill** (`ls <cell>/.claude/skills` → no such directory in all six): five of the
  six results open with a disclaimer — *"lean-code isn't in the available-skills list"*, *"reads
  outside the working directory (`~/.claude/skills/`, `~/ai-skills/`) were denied"*, *"the skill
  file itself is outside my granted read paths"* — and reviewed against the block in `CLAUDE.md`
  instead; the sixth (`lens/69aaf73`) carries no disclaimer but ran in the same layout. They are
  the measurement that forced the `block` arm (protocol, third amendment); for the lens criterion
  they count as escapes, not as data. Their counts, for the record and never adjudicated:
  `lens/` 8 / 7 / 8 findings, `net:` −38 / −61 / −39; `lens2/` 9 / 7 / 7 findings, `net:` −47 /
  −65 / −49 (one `stdlib:` and one `native:` among them, the only ones in any run).

## Spend

Summed from every `summary.json`/`results.json` (`spent_usd`), every probe JSON (`cost_usd`), every
lens `out.json` and `model-check.json` (`total_cost_usd`) that could be read:

| component | $ |
|---|--:|
| pilot `20260905-211056` (Haiku, 9 cells) | 0.5571 |
| baseline `20260905-211512` (27) | 9.4529 |
| block `20260905-230209` (27) | 9.0828 |
| skill `20260906-003055` (27) | 9.2791 |
| skill `reuse-slug` +2 `20260906-004535` (2) | 0.4940 |
| skill `reuse-slug` post-REWRITE `20260906-004900` (3) | 0.7391 |
| skill `cache` + `csv-sum` +2 reps `20260906-013713` (4) | 1.1119 |
| probes `211029`, `230124`, `002213`, `002551`, `002908`, `004737`, `013550` | 0.0457 + 0.0939 + 0.1908 + 0.1941 + 0.1951 + 0.1945 + 0.1928 = 1.1069 |
| ad-hoc probes (no-git 0.0057, git-init 0.0164, project-skill `--tools ""` 0.0179, `--tools Skill` 0.0307) | 0.0707 |
| lens (invalid) `lens/` 0.5059 + 0.4355 + 0.3084, `lens2/` 0.5442 + 0.5960 + 0.3782 | 2.7683 |
| lens (valid) `lens3/` 0.5210 + 0.5823 + 0.3615 | 1.4648 |
| `model-check.json` | 0.0612 |
| **total** | **36.1888** |

Item #145 part B (probe, pilot, baseline) is $10.0557 of it; item #146 $26.1331 (of which the
INCONCLUSIVE re-read of `cache` and `csv-sum`, probe + 4 cells, $1.3047).

## What this does not cover

- One model id, one CLI version (`2.1.261`, pinned after the auto-update), one machine, two days;
  `--report` proves the id, not the weights (KNOWN LIMIT 6).
- The INCONCLUSIVE clause is closed on the `skill` arm (its +2 repetitions ran on every task it
  fired on) and open on `trace-transfer` in the `block` arm, which was not re-run: the block's
  −28.6 % stays INCONCLUSIVE. After the widening `cache` and `csv-sum` still spread more than 50 %
  of their mean (observation 7); the protocol has no rule about that, and n=5 on two tasks is
  still a small sample — the published Δ is a group mean over four tasks, not a per-task claim.
- `react-use-orders` is structural; its `safe` is the reuse axis and never feeds the gate.
- No cell ran with the maintainer's hooks or plugins (KNOWN LIMIT 3); `~/.claude/skills` is not
  loaded in this mode (KNOWN LIMIT 4) — the skill reached the cells as a project skill only.
- The lens ran once per diff (n=1) on three diffs of one author; the skill's load in those cells is
  inferred from the absence of the disclaimer, not read from an `init` event.
- `added_lines` counts an inline `__main__` block as product code (observation 2); the metric is
  the one the protocol froze, and it is reported as frozen.
- No interactive session was run: the headless cell **is** the real entry point the protocol
  defines (*Cell*), and every number above comes from it.
