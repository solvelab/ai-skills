# Results — what has been measured, and what the protocol says about it

Read `protocol.md` first: it fixes the arms, the cell, the four metrics and the four verdicts,
frozen at `fdfc655` before any paid cell ran. This file reports numbers against that document and
reads the verdict by its letter.

**Verdict: NO-CLAIM.** The doctrine changes behaviour completely and reliably, and improves nothing
measurable on these six tasks. No number from this experiment may appear in a README or a
SKILL.md. Why, in full, below.

## Method

Two arms differing only by an always-on doctrine block in the cell's `CLAUDE.md`
(`arms-block.md`, sha256 `0f1cd750…`); six Python/pytest tasks with hidden suites the cell never
sees; `order` read from the session transcript, `red` and `green` measured outside the cell by the
harness, `test_added_lines` taken from the diff. Bash is disallowed in every cell, so what is
measured is the order in which artifacts were written and the quality of what remained — not the
feedback loop.

Conditions: model `opus[1m]`, Claude Code `2.1.263`, Python `3.14.5`, pytest `9.1.1`, arms at
`rules_sha 4dbc080`, isolation `settings-sources`, n=3, 36 cells, `$6.7351`.

## Offline instruments — 2026-09-06

`run.py --selftest --scorer-venv <venv>` -> **70/70** (`contract 8/8`, `tasks 13/13`, `order 8/8`,
`red 9/9`, `scorers 18/18`, `refusals 8/8`, `export 2/2`, `aggregate 4/4`), re-run green inside the
matrix invocation itself, which is the gate.

Two defects the instruments caught in this repository's own artifacts before any cell ran:

1. The `slug-truncate` **good** reference returned `"antid"` where the prompt requires `""` for a
   single word longer than `max_len`. Caught by the `scorers` group.
2. `research/lean-code/run.py` raised `AttributeError: 'NoneType' object has no attribute
   '__dict__'` when executed through `importlib` without being registered in `sys.modules` first,
   because `dataclasses` resolves `cls.__module__` through that table. Recorded in `PIN`.

## Isolation probe — `results/20260906-150743-probe.json`

Both arms PASS on Haiku, `$0.127`: sentinel echoed 3/3, hook events 0 (maintainer hooks 0), the
caveman marker untouched 3/3, and `SKILLS: none` in both — neither arm carries a project skill,
which is what `skill_visible 0/1` records.

## Pilot — `results/20260906-150825-pilot-export.json`

One task, both arms, n=1, Haiku, `$0.0903`. Its only job was to answer the question the offline
instruments cannot: **does `--output-format stream-json` expose the write sequence?** It does.
`order_source` was `transcript` in both cells, and the two arms already separated. The matrix ran
because of this.

## The two arms, per task — `results/20260906-150952-export.json`

n=3 per cell, `order_source` **`transcript` in 36/36 cells — zero fallback**.

| task | kind | arm | order | red | green | wrote tests | testLOC mean (min–max) | $/cell |
|---|---|---|--:|--:|--:|--:|--:|--:|
| `chunk-list` | boundary | baseline | 0/3 | 0/3 | 3/3 | 0/3 | 0 (0–0) | 0.1304 |
| `chunk-list` | boundary | block | 3/3 | 3/3 | 3/3 | 3/3 | 35.00 (33–37) | 0.2006 |
| `date-range` | boundary | baseline | 0/3 | 0/3 | 3/3 | 0/3 | 0 (0–0) | 0.1338 |
| `date-range` | boundary | block | 3/3 | 3/3 | 3/3 | 3/3 | 44.67 (44–45) | 0.1990 |
| `fix-percent-bug` | bugfix | baseline | 0/3 | 0/3 | 3/3 | 0/3 | 0 (0–0) | 0.1466 |
| `fix-percent-bug` | bugfix | block | 3/3 | 3/3 | 3/3 | 3/3 | 16.00 (16–16) | 0.2054 |
| `money-round` | specified | baseline | 0/3 | 0/3 | 3/3 | 0/3 | 0 (0–0) | 0.1576 |
| `money-round` | specified | block | 3/3 | 3/3 | 3/3 | 3/3 | 27.00 (27–27) | 0.2189 |
| `parse-duration` | specified | baseline | 0/3 | 0/3 | 3/3 | 0/3 | 0 (0–0) | 0.1930 |
| `parse-duration` | specified | block | 3/3 | 3/3 | 3/3 | 3/3 | 39.00 (39–39) | 0.2187 |
| `slug-truncate` | boundary | baseline | 0/3 | 0/3 | 3/3 | 0/3 | 0 (0–0) | 0.1709 |
| `slug-truncate` | boundary | block | 3/3 | 3/3 | 3/3 | 3/3 | 42.67 (37–53) | 0.2701 |

Totals: `baseline` order **0/18**, red **0/18**, green **18/18**, wrote a test **0/18**.
`block` order **18/18**, red **18/18**, green **18/18**, wrote a test **18/18**.

The behavioural effect is total and has no overlap between arms: the doctrine moved order from 0 %
to 100 % and test-writing from 0 % to 100 %, on every task, in every repetition. The correctness
effect is zero, because there was no room for one.

## Verdict, by the letter of `protocol.md`

The SHIP row reads, verbatim:

> **SHIP** — a number may appear in the skill and in the README | `order` in the `block` arm ≥ 0.80
> of cells **and** ≥ 3× the baseline rate; `red` ≥ 0.80 among the block cells where `order` is true;
> `green` in `block` ≥ `green` in `baseline` on **every** task, and strictly greater on at least
> one; `test_added_lines` mean in `block` ≤ 2.0× the baseline on every task

Four conditions, read one by one:

1. `order` ≥ 0.80 and ≥ 3× baseline — **holds**: 1.00 against a baseline of 0.00.
2. `red` ≥ 0.80 where `order` is true — **holds**: 18/18.
3. `green` ≥ baseline everywhere **and strictly greater on at least one task** — **fails**. Equal
   on all six, greater on none.
4. `test_added_lines` ≤ 2.0× baseline — **not applicable**: the baseline wrote 0 test lines, so the
   ratio is a division by zero. The harness itself reports `factor: null` for every task.

SHIP therefore does not hold, on condition 3.

The NO-CLAIM row reads, verbatim:

> **NO-CLAIM** | `order` rises to the SHIP bar but `green` does not: equal to baseline everywhere
> and greater nowhere. The doctrine may still ship for the discipline alone, and **no number**
> appears in any README or SKILL.md

That is exactly the measurement. INCONCLUSIVE does not fire: `order` is 1.00, not between 0.50 and
0.80, and the widest dispersion of `test_added_lines` is `slug-truncate` at 16 lines on a mean of
42.67 — 37.5 %, below the 50 % clause. REWRITE does not fire either: `green` is nowhere below
baseline and `red` is 1.00, far above 0.50. Its third clause — `test_added_lines` above 2.0× the
baseline — is the same undefined ratio as SHIP's condition 4 and cannot fire on a zero baseline;
see the amendment in `protocol.md`.

**NO-CLAIM.** For issue #183 this means the skill may be written for the discipline it enforces,
and it carries **no measured number**.

## Why `green` could not move — the ceiling, named

`opus[1m]` solved all six tasks in the baseline: **18/18 green with zero tests written**. A task set
where the control arm never fails cannot show a treatment arm doing better. The measurement is
sound and the reading is honest; the task set is the limitation, and it was chosen before the
baseline existed.

This is worth stating plainly rather than burying: **the experiment did not fail to find an effect
on correctness — it could not have found one.** The `green` half of the verdict is uninformative,
not negative. Any future protocol version that wants to test the correctness claim needs tasks the
baseline gets wrong at a measurable rate; picking them requires a baseline-only run first, so that
the tasks are not selected against the treatment.

## Post-hoc observations (2026-09-06, after the letter was applied)

- **The baseline wrote no test at all, in 18 of 18 cells** — under the maintainer's real
  `CLAUDE.md`, which includes the `lean-code` block and its floor of *one runnable check behind
  non-trivial logic*. Six of the tasks are branch-carrying, boundary-carrying logic. Whatever that
  floor achieves elsewhere, it did not put a check in the workspace here.
- **`red` tracked `order` perfectly**: every one of the 18 block cells wrote a test that genuinely
  failed on the pristine seed. The doctrine did not produce test-shaped files that pass vacuously,
  which was the REWRITE risk it was written against.
- **The cost of the doctrine is about 40 % more per cell** (`$0.1587` mean baseline vs `$0.2188`
  mean block, over 18 cells each) — more output tokens, because there is a test to write.
- **Dispersion is very low**: four of six tasks have identical `test_added_lines` across all three
  repetitions. The behaviour is not marginal.

## Spend

| step | model | cells | cost |
|---|---|--:|--:|
| isolation probe | `claude-haiku-4-5-20251001` | 8 calls | $0.1270 |
| pilot | `claude-haiku-4-5-20251001` | 2 | $0.0903 |
| matrix | `opus[1m]` | 36 | $6.7351 |
| **total** | | | **$6.9524** |

Under the `--budget-usd 20` ceiling; no cell was stopped by budget.

## What this does not cover

The list is `protocol.md`'s: the red-green feedback loop (Bash disallowed in every cell), anything
outside Python and pytest, the published skill as opposed to the doctrine block, internal structure
as opposed to stated behaviour, and work longer than one prompt. To which this run adds the one the
numbers exposed: **a task set with no headroom on `green`**, described above.
