# Protocol — measuring a test-order doctrine on the maintainer's own model

**Frozen** at base `fdfc655` (`backlog/182-tdd-research`, 2026-09-06), by the commit that
introduces this file. The verdict thresholds in the last section were written **before any paid
cell ran**. A later edit to a threshold is a new protocol version; numbers measured under different
versions are not compared. Amendments are appended dated and numbered, never rewritten in place.

The question is narrow and stated once: **does an always-on test-order doctrine change the order in
which a headless Claude Code session writes files, and does the code it leaves behind get better or
worse for it?**

## Arms

Two. `baseline` and `block`. The arm ids are the ones `research/lean-code` uses, because this
harness imports that experiment's arm preparation and preflight, and `ARM_LAYOUT` over there is
keyed by those ids — an arm named anything else silently carries no block at all
(`research/lean-code/run.py:280`, asserted by this harness's contract selftest).

| arm | what the session sees |
|---|---|
| `baseline` | the maintainer's real `~/.claude/CLAUDE.md`; project `settings.json` = the maintainer's `~/.claude/settings.json` minus `hooks`, `enabledPlugins`, `extraKnownMarketplaces`, `statusLine`, `permissions`; the cell's `CLAUDE.md` = the sentinel line alone; `skillOverrides.tdd = "off"`; no `.claude/skills` |
| `block` | the same, plus the doctrine of `research/tdd/arms-block.md` appended after the sentinel line, its sha256 recorded in `arm.json` |

The `skill` arm — the published `skills/tdd` loaded as a project skill — **does not run here**. It
belongs to the item that writes the skill (#183). `--prepare-arms` produces it only when
`skills/tdd/SKILL.md` exists in the checkout, and in this checkout it does not.

### Isolation probe (paid, before any matrix)

Reused verbatim from `research/lean-code` (`cmd_probe`). Per arm: sentinel echoed 3/3, hook events
0, the maintainer's caveman marker untouched, and the available-skills list not naming `tdd`
(`skill_visible` `0/1` in both arms, since neither carries a project skill). `--matrix` refuses to
run without a passed probe under the arms' current `rules_sha` — the gate is `probe_gate`, imported.

The reason this exists is not hypothetical: the upstream of the lean-code experiment published a
baseline that was secretly running the skill through a `SessionStart` hook, and the maintainer's
own `~/.claude/settings.json` carries hooks on `PreToolUse`, `UserPromptSubmit`, `PostToolUse`,
`Notification` and `Stop`, plus the `caveman` plugin on `SessionStart`.

## Cell

One cell = one task × one arm × one repetition, in a fresh git repository seeded from the task and
committed before the session starts.

```
claude -p "<task prompt>" --model <id> --output-format stream-json --verbose
       --setting-sources project,local --permission-mode acceptEdits
       --disallowedTools Bash --strict-mcp-config --no-session-persistence
       --max-budget-usd 1.00 --append-system-prompt "<NO_RUN_TDD>"
```

Two differences from the lean-code cell, both deliberate:

1. `--output-format stream-json` instead of `json`. Order does not survive in the final diff, which
   shows state and not sequence; the transcript is the only place the sequence exists.
2. `NO_RUN_TDD` instead of `NO_RUN`. The lean-code text says *"include tests if you normally would"*
   and *"Only the code you write is measured, not its execution"*. In an experiment about test
   order the second sentence tells the model that tests do not count — a treatment variable, not a
   neutral frame. The replacement forbids execution and says nothing about tests. It is **identical
   in both arms**, and it reads, verbatim:

   > Do not run a dev server, install dependencies, run a database, or open a browser: write files
   > and stop. Backlog rite explicitly waived for this benchmark task: edit the files directly,
   > without an issue, a branch or an OpenSpec change.

Bash stays disallowed, inherited from the isolation apparatus. See *What this protocol does not
cover*.

## Metrics per cell

| metric | how it is measured | what disqualifies it |
|---|---|---|
| `order` | the first `Write`/`Edit`/`MultiEdit` whose path satisfies `is_test_path` precedes the first one in a production path, read from the transcript's `tool_use` events | a cell with no test write, or no production write, is `False` — nothing preceded anything |
| `order_source` | `"transcript"` or `"mtime"` | a cell scored from mtime is a **fallback** and is reported separately; a fallback-backed figure is never published as a measurement of order |
| `red` | the test files the cell wrote, applied **alone** on the pristine seed, must FAIL | a suite that passes with no implementation is `red=False`; pytest's "no tests collected" (exit 5) is `red=False` |
| `green` | the **hidden suite**, which the cell never sees, run against the final `src/` in the pinned venv | scored in a harness-owned workspace with a harness-owned `pytest.ini`, so nothing the cell wrote to `pytest.ini` or `conftest.py` can influence it |
| `test_added_lines` | added lines in test paths, from the imported `git_diff_stats` | the guard against buying order with an inflated suite |

`green` is never scored by the suite the cell itself wrote: scoring a model on its own tests rewards
writing weak ones, which is the opposite of what the doctrine claims.

## Tasks (6)

All Python, all pytest, all stdlib. Each carries a committed `seed/`, a `PROMPT`, a `good/` and a
`bad/` reference, and a `hidden/` suite the cell never sees. The selftest proves every scorer
against `good` and `bad` before any paid cell runs.

| id | kind | the behaviour the prompt states | room to get it wrong |
|---|---|---|---|
| `parse-duration` | specified | `"1h30m"` → 5400; three rejection cases | a bare number and a trailing fragment are accepted by the obvious regex |
| `money-round` | specified | two decimal places, half **away from zero** | Python's default rounding is half-even; 2.325 becomes 2.32 |
| `date-range` | boundary | start inclusive, end exclusive | `while current <= end` is the natural loop and is off by one |
| `chunk-list` | boundary | chunks of at most `size`; `size <= 0` raises | the only failure mode is the non-positive size |
| `slug-truncate` | boundary | cut at a word boundary, never trailing `-`, single long word → `""` | hard truncation leaves half a word or a hyphen |
| `fix-percent-bug` | bugfix | zero baseline raises `ValueError`; `0 → 0` returns `0.0` | the report names `ZeroDivisionError`; the cheap patch returns `0.0` and lies |

No task prompt mentions tests, TDD, pytest or assertions. That is asserted by the selftest
(`tasks` group): the treatment lives in the `block` arm's `CLAUDE.md` and nowhere else.

## Sequence

1. `run.py --selftest --scorer-venv <dir>` — offline, every instrument with an injected defect.
2. `run.py --prepare-arms --arms-root <outside-repo> --rules-ref <sha> --claude-block research/tdd/arms-block.md`
3. `run.py --probe-isolation --arms-root <...> --model claude-haiku-4-5-20251001` — paid, minimal.
4. Pilot: `--matrix --arms baseline,block --tasks parse-duration --runs 1` on Haiku. Its purpose is
   to answer the one question the offline instruments cannot: whether `stream-json` exposes the
   write sequence at all. A pilot in which every cell falls back to mtime stops the run.
5. `--selftest --matrix --arms baseline,block --tasks all --model <daily> --runs 3 --budget-usd 20`
6. `--report <stamps> --export research/tdd/results/<stamp>-export.json`

`--matrix` refuses without a green selftest in the same invocation, without a passed probe, without
a scorer venv, and when `claude --version` differs from the version the arms were prepared under.

## Verdict (written before the number)

Read by the letter, on the final table, over the six tasks. `order` figures count transcript-scored
cells only; if fallback cells are more than a third of any arm, the reading is INCONCLUSIVE by
instrument regardless of the numbers.

| verdict | conditions |
|---|---|
| **SHIP** — a number may appear in the skill and in the README | `order` in the `block` arm ≥ 0.80 of cells **and** ≥ 3× the baseline rate; `red` ≥ 0.80 among the block cells where `order` is true; `green` in `block` ≥ `green` in `baseline` on **every** task, and strictly greater on at least one; `test_added_lines` mean in `block` ≤ 2.0× the baseline on every task |
| **INCONCLUSIVE** | `order` in `block` between 0.50 and 0.80, or below 3× the baseline while above it, or the dispersion (max − min) of a task's `test_added_lines` exceeds 50% of its mean → +2 repetitions on the affected tasks, then re-read this table once |
| **NO-CLAIM** | `order` rises to the SHIP bar but `green` does not: equal to baseline everywhere and greater nowhere. The doctrine may still ship for the discipline alone, and **no number** appears in any README or SKILL.md |
| **REWRITE** | `green` in `block` below `baseline` on **any** task; or `test_added_lines` above 2.0× the baseline on any task; or `red` below 0.50 among block cells where `order` is true — a doctrine that produces test-shaped files that pass without the code is worse than none |

## What this protocol does not cover

- **The red-green feedback loop.** Bash is disallowed in every cell, inherited from the isolation
  apparatus of `research/lean-code`, whose settings-sources layout runs under
  `--permission-mode acceptEdits`; allowing Bash would mean `bypassPermissions` and arbitrary
  commands in an unattended headless loop on the maintainer's machine. The agent therefore never
  runs a test and never watches red turn green. What is measured is the **order in which artifacts
  were written** and the **quality of what remained**. The bias is identical in both arms, so the
  comparison holds; the absolute value of `green` is a floor, not the model's capability.
- **Anything outside Python and pytest.** Six tasks, one stack.
- **The published skill.** The `block` arm measures an always-on doctrine block, which is the
  mechanism, not the artifact. Whether `skills/tdd` reproduces the effect is #183's measurement.
- **Structure.** The hidden suites score behaviour named in the prompt. An implementation that is
  correct but organised differently passes, by design.
- **Long-horizon work.** One prompt, one file, one function. Nothing here says what the doctrine
  does across a multi-step change.
