# research/lean-code

Backing evidence for issue #145: a harness that measures what the `lean-code` doctrine (adopted
from DietrichGebert/ponytail, MIT) does to the code a real headless Claude Code session leaves
behind — on the maintainer's own model and CLI version, with arms proven isolated from the
maintainer's hooks and plugins, and with the verdict written before the number.

This directory sits **outside `skills/`** on purpose. `generate.sh` publishes only `skills/`, so
everything here is versioned and reviewable without being shipped to any project that enables a
plugin. The skill itself is item 2 (`add-lean-code-doctrine`); it will cite the counts produced
here, not the upstream's.

## Read in this order

| File | What it is |
|---|---|
| [`protocol.md`](protocol.md) | **The point of all of this.** Arms, cell, metrics, flags, the nine tasks, the sequence, and the SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE thresholds — frozen before any paid cell ran. |
| [`run.py`](run.py) | The harness. `--selftest` proves every instrument offline; `--prepare-arms` (with `--claude-block <file>` for the `block` and `skill` arms), `--probe-isolation`, `--matrix`, `--classify`, `--rescore`, `--report --export` (deltas of each treatment arm vs baseline), `--relabel-arm` (offline rename of an arm in a finished stamp, reason recorded). Three isolation modes (`settings-sources` by default, `config-dir`, `home`); its docstring carries the KNOWN LIMIT list. |
| [`tasks/`](tasks/) | The three catalog tasks (`fastapi-create-item`, `fivem-shop-buy`, `react-use-orders`): seed, good/bad reference, executing `score()` — the React one is structural and says so. |
| [`vendor/ponytail/`](vendor/ponytail/PIN) | The six upstream tasks (`tasks.py`), the LOC oracle (`loc.js`), the licence and the pin (commit, date, sha256). |
| [`fixtures/examples/`](fixtures/examples/README.md) | Eleven upstream before/after transcripts, used only to prove the LOC counter against `loc.js`. |
| [`scorer-venv.txt`](scorer-venv.txt) | The pinned `fastapi`/`httpx`/`pydantic`/`starlette` the FastAPI scorer ran under. The venv is never committed. |
| [`arms-block.md`](arms-block.md) | The always-on *Lean Code* block (the `personal-rules.md` section without its heading) that `--claude-block` appends to the `block` and `skill` arms' `CLAUDE.md` snippet; the baseline never sees it. |
| [`results.md`](results.md) | **What has been measured.** The three arms per task with Δ and min–max, the `reuse-slug` INCONCLUSIVE → REWRITE → re-run story, the `cache`/`csv-sum` +2 repetitions and the re-read, the verdict read by the letter (skill **SHIP**, block INCONCLUSIVE), the dated post-hoc observations, the review lens on three real diffs against the pre-registered false-positive rules, the spend, and what it does not cover — the source of the one number (the over-build group Δ) that `SKILL.md` and the catalog README carry. |
| [`results/`](results/README.md) | The files behind it: probe records, per-arm defect counts (baseline with the hand-read classification, block, skill), stripped exports of every reported stamp. |

## Running things

```bash
# 1. prove the instruments (offline; node for the loc.js oracle, lua 5.5, the scorer venv)
python3 -m venv /tmp/lean-venv && /tmp/lean-venv/bin/pip install -r research/lean-code/scorer-venv.txt
python3 research/lean-code/run.py --selftest --scorer-venv /tmp/lean-venv

# 2. arms, outside the repository (default --isolation settings-sources: three files per arm, nothing copied).
#    Without --claude-block only `baseline`; with it, `block` (sentinel + always-on block) and `skill`
#    (block + skills/lean-code of THIS checkout copied into every workspace as .claude/skills/lean-code —
#    ~/.claude/skills is not read: a cell run with --setting-sources project,local cannot see it, KNOWN LIMIT 4)
python3 research/lean-code/run.py --prepare-arms --arms-root /tmp/lean-arms --rules-ref <sha> \
    --skill lean-code --claude-block research/lean-code/arms-block.md

# 3. PAID, small: prove the arms are isolated (per arm: 3 sentinel calls + 1 skills-list call on Haiku, $0.05 each;
#    pass = sentinel 3/3, hook events 0, caveman marker untouched 3/3, skill_visible 1/1 in skill and 0/1 elsewhere)
python3 research/lean-code/run.py --probe-isolation --arms-root /tmp/lean-arms --model claude-haiku-4-5-20251001

# 4. PAID: the matrix (refuses without a green selftest in the same invocation, a passed probe covering the arm,
#    and — for --arms skill — skill_visible 1/1 in that probe)
python3 research/lean-code/run.py --selftest --matrix --arms skill --tasks all --model <id> --runs 3 \
    --arms-root /tmp/lean-arms --runs-root /tmp/lean-runs --budget-usd 15 --scorer-venv /tmp/lean-venv

# 5. offline again: per-flag counts; the report over 1-3 stamps (baseline, block, skill) prints each treatment
#    arm's delta of mean added_lines vs baseline and refuses stamps whose `claude --version` or model differ
python3 research/lean-code/run.py --classify /tmp/lean-runs/<stamp>
python3 research/lean-code/run.py --report /tmp/lean-runs/<baseline> /tmp/lean-runs/<block> /tmp/lean-runs/<skill> \
    --export research/lean-code/results/<stamp>-export.json
# an arm that measured something other than its label: rename it in a FINISHED stamp, reason recorded in results.json
python3 research/lean-code/run.py --relabel-arm /tmp/lean-runs/<stamp> skill block --reason "<why>"
```

Every cell command is written to `<cell>/_command.txt` before it runs; every cell's
`total_cost_usd` is summed and the run stops at `--budget-usd`.

## What the selftest proved on 2026-09-06

`python3 research/lean-code/run.py --selftest` → `selftest: 183/183 OK` in 2.2 s: LOC port equal
to `loc.js` on 22/22 sections; `Without > With` on 8/8 of the line-count examples and the three
dependency-removal examples (`infinite-scroll`, `number-formatting`, `url-params`) pinned as such —
the plan had assumed 11/11 and the upstream's own counter says otherwise on those three; scorers
25/25 (good passes, bad caught on its axis, and the 7 declared variants of the good reference score
as decided: partial validation and a body `tenant_id` are unsafe on FastAPI, rejecting a forged
`playerId` and `clampNum`+`floor` are safe on FiveM, `clampNum` without `floor` is not); detectors
29/29 (since the baseline: `import pytest` in a test file and a `unittest.TestCase` subclass are
recorded as `test_dependency`/`test_class_added`, never flagged; a production import or class still
fires); legacy arm preflight 15/15; the `settings-sources` mode 42/42 (three arms carry filtered
project settings with `skillOverrides.lean-code` off/off/on and no credentials; the block sits in
`block` and `skill` only and hashes to `arm.json`; `project_skill_path` only in `skill`, refused
when missing, without `SKILL.md`, or present in another arm; the skill workspace commits
`.claude/skills/lean-code` as a real directory copied from the checkout and the counters ignore
edits inside it; command has `--setting-sources project,local` + `acceptEdits` and no
`bypassPermissions`; stream parser counts hook events by name; the skills-line parser reads
`SKILLS: …`, the bare `lean-code\nDONE`, `none`, and a mention outside the line); export stripper
3/3; tree-kill 1/1; refusals 13/13 (probe gate: no probe, another `rules_sha`, layout mismatch, an
arm the probe did not cover, `--arms skill` without `skill_visible` 1/1); metrics 4/4; rescore 3/3;
relabel 8/8 (unfinished, unknown destination, stopped run refused; dirs renamed, `arm` rewritten in
the three files, reason recorded); report deltas 5/5.

## Status

Everything paid has run (2026-09-05 → 2026-09-06, Claude Code `2.1.261` pinned, `opus[1m]` →
`claude-opus-5[1m]`, one machine): isolation probes, the Haiku pilot (shake-out only), **baseline**
(27 cells, $9.4529), **block** — the always-on block alone, relabelled from `skill` (27 cells,
$9.0828) — and **skill** (27 cells, $9.2791; `reuse-slug` re-measured with +2 repetitions and, after
a REWRITE of the skill's one-check rule, n=3 again, $1.2331; `cache` and `csv-sum` widened to n=5
by the +2 repetitions the dispersion clause asks for, probe + 4 cells, $1.3047), plus the review
lens on the three real diffs, twice — on the pre-widening guard text ($1.4648, 21 findings,
precision 16/21) and, for item #174, on the published skill ($1.5668, 17 findings, precision 13/17
= 0.76, no `delete:` on a selftest case) — and the `block` arm's `trace-transfer` widened to n=5
(2 cells, $0.7916; $38.5472 in all). The verdict, read by the letter of
[`protocol.md`](protocol.md) in [`results.md`](results.md): **skill SHIP** on the re-read that
follows the +2 repetitions — every SHIP condition holds on the widened table, over-build group Δ
−34.4 %, `correct`/`safe` 31/31, no REWRITE row open; **block INCONCLUSIVE by the Δ half** (−28.6 %,
inside the band; its dispersion half executed and closed at n=5, `trace-transfer` 22.4, −17.0 %) —
informational, never the skill's verdict. Per the SHIP row, `SKILL.md` and the catalog README
carry that one group Δ with its conditions; every per-task mean with its min–max, the review-lens
precision and the spend live in `results.md` only. Built against Lua `5.5.0`, node `v26.0.0`,
Python 3.14 (harness) / 3.12 (scorer venv); Claude Code auto-updated to `2.1.263` on 2026-09-06,
so the skill stamps ran the pinned `2.1.261` binary first on `PATH` (`--report` refuses a version
mismatch).
