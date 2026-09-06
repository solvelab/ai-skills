# Protocol — measuring a code-volume doctrine on the maintainer's own model

**Frozen** at base `7709622` (master at the branch point of `backlog/145-lean-code-research`,
2026-09-05), by the commit that introduces this file. The verdict thresholds below were written
**before any paid cell ran**. A later edit to a threshold is a new protocol version; numbers
measured under different versions are not compared. Amendment of 2026-09-05, still before any paid
cell: the `safe` semantics of the two catalog scorers were refined after review (see *Tasks*); no
threshold moved. Second amendment of 2026-09-05, still before any paid cell: the default isolation
mode changed from `CLAUDE_CONFIG_DIR` to `--setting-sources project,local` (see *Arms* — *Why the
default changed*); metrics, tasks and thresholds untouched. Third amendment of 2026-09-06, after the
baseline and one treatment arm had run and **before any `skill` cell**: the treatment split into
two arms, `block` and `skill` (see *Arms* — *Why `block` exists*), because the arm labelled `skill`
in stamp `20260905-230209` measured the always-on block alone — `--setting-sources project,local`
does not load `~/.claude/skills`, so `skillOverrides.lean-code = "on"` enabled nothing; the stamp
was relabelled `block` with `run.py --relabel-arm` (reason recorded in its `results.json`). Metrics,
tasks and thresholds untouched; the verdict table is read for the `skill` arm, and the same table
read for `block` isolates the always-on mechanism. Fourth amendment of 2026-09-06, **after every
paid cell ran**, facts only: (a) a project skill under `.claude/skills/<skill>` is discovered only
when the cwd is a git repository root (measured, *Isolation probe*); (b) the probe reads the skills
list from the CLI's `system/init` event, not from the model's answer — on probe `20260906-002551`
`init` listed `lean-code` and the model answered `SKILLS: none` (`run.py`, commit `229a260`);
(c) `added_lines` counts an inline `__main__` self-check written into a product file as product
code — `reuse-slug` 9 → 19 and `cache` 3 → 11 in the `skill` arm with identical logic (see
*Metrics*). Thresholds, rows, groups and tasks untouched; the metric is reported as frozen. How the
verdict table was read when two of its rows held at once is recorded in `results.md`, not here.

What is measured: the code a real headless Claude Code session leaves behind in a seeded git
repository, with and without the `lean-code` doctrine, on the model the maintainer uses every day.
What is not measured: chat output (the metric the upstream retracted), execution speed, quality as
judged by an LLM, anything under the maintainer's `caveman` plugin.

## Arms

| arm | what the session sees (default mode, `settings-sources`) | when |
|---|---|---|
| `baseline` | the maintainer's real `~/.claude/CLAUDE.md` (personal-rules + RTK + TalkToMe); project `settings.json` = the maintainer's `~/.claude/settings.json` minus `hooks`, `enabledPlugins`, `extraKnownMarketplaces`, `statusLine`, `permissions` (keeps `model`, `effortLevel`, `modelSettings`, `skillOverrides`) **plus `skillOverrides.lean-code = "off"`**; `CLAUDE.md` = the sentinel line; no `.claude/skills` | item 1 (this) and item 2 |
| `block` | same, with the always-on *Lean Code* block appended to the cell's `CLAUDE.md` after the sentinel (`--prepare-arms --claude-block research/lean-code/arms-block.md`; the block's sha256 in `arm.json`), `skillOverrides.lean-code = "off"`, no `.claude/skills` — the always-on mechanism alone, the equivalent of ponytail's `SessionStart` injection | item 2 — stamp `20260905-230209`, relabelled from `skill` |
| `skill` | same as `block` **plus** the skill as a project skill: `skills/lean-code` of the checkout copied into the workspace as `.claude/skills/lean-code` (`project_skill_path` in `arm.json`) and `skillOverrides.lean-code = "on"` — the mechanism the upstream measured, a rule always present plus a skill the router can pick, without the block having to enter the maintainer's real `personal-rules.md` first | item 2 |
| `ponytail-ref` | baseline plus the upstream plugin via `--plugin-dir` | optional, item 2, off by default |

In the default mode an arm is three files outside the repository — `arm.json` (the `rules_sha` of
`--rules-ref` for provenance, `claude_block_sha256` in `block` and `skill`, `project_skill_path` in
`skill`), `project-settings.json`, `claude-snippet.md` (the line `BENCH-SENTINEL: <arm>`; in `block`
and `skill` followed by the always-on block from `--claude-block`, verbatim) — and **nothing is
copied** into the arm: no credentials, no `CLAUDE.md`, nothing from `~/.claude/skills`. The
preflight refuses a `baseline` snippet that carries anything beyond the sentinel, a `block`/`skill`
snippet whose block does not hash to `arm.json`, a `skill` arm whose `project_skill_path` is missing
or has no `SKILL.md`, and a `baseline`/`block` arm that names one (amendments of 2026-09-05 and
2026-09-06 for item #146, before any `skill` cell ran; metrics, tasks and thresholds untouched).
Each cell writes the settings and the snippet into its workspace as `.claude/settings.json` and
`CLAUDE.md` and, in the `skill` arm, copies the skill directory to `.claude/skills/lean-code` —
copied, not symlinked, so an `acceptEdits` cell cannot write through into the checkout and the
seed commit records the exact skill text the cell saw — commits all of it in the seed commit
(force-added: the maintainer's global gitignore drops `**/.claude/`), and runs `claude -p` with
`--setting-sources project,local`, which on Claude Code 2.1.261 drops the user settings file —
hooks, `enabledPlugins` and the caveman `SessionStart` hook with it (measured: 0 hook events under
`--include-hook-events`) — and does not load `~/.claude/skills` (measured, *Why `block` exists*).
The harness paths (`CLAUDE.md`, `.claude/`) are excluded from every counter and from the
detectors' text.

Two explicit alternatives keep the earlier layout: `--isolation config-dir` (arm dir as
`CLAUDE_CONFIG_DIR`: its own `settings.json`, `CLAUDE.md` = `personal-rules.md` at the ref +
sentinel, `skills/` symlinked from `git archive <ref>`, credentials copied with mode 600) and
`--isolation home` (`HOME=<arm>/home`, `home/.claude -> arm`). The layout is fixed at
`--prepare-arms` and recorded in `arms.json`; the probe and the matrix read it from there.

`skillOverrides` is kept on purpose: it turns 16 skills off in the maintainer's real sessions; a
baseline without it would measure a user who does not exist. Values are the strings the CLI
compares against (`on`, `name-only`, `user-invocable-only`, `off` — read from the 2.1.261 binary).
In this mode it governs the project skill only: the user skills it names are not loaded anyway
(below), so it is not the isolation — the arm layout is.

#### Why the default changed (2026-09-05)

Three reasons, written the day the mode was added, before any paid cell:

1. **The measurement could not run from a subagent.** The `config-dir`/`home` cells copy
   `~/.claude/.credentials.json` into each arm and run `--permission-mode bypassPermissions`; the
   harness's safety classifier blocks a subagent from doing either. The maintainer measured, in
   the main session, that a cell runs with `--setting-sources project,local`, no config-dir
   override and `acceptEdits`: rc 0, 0 hook events, result JSON with `total_cost_usd`,
   `num_turns`, `duration_ms`, `modelUsage`, `result`, `subtype`.
2. **No credential copies.** Nothing sensitive leaves `~/.claude`; an arm can be committed, pasted
   or deleted without a thought.
3. **The baseline is the maintainer's real setup.** The real `~/.claude/CLAUDE.md` loads (the
   real skills directory does not — measured a day later, below). The `config-dir` arm was a
   reconstruction of that setup from a git ref; this is the setup itself. The cost is written in
   *What this protocol does not cover*: the user's rules file is not frozen by the arm (the
   `rules_sha` in `arm.json` makes a drift visible, not impossible), and the skill under test
   reaches the cell only as a project skill, in the `skill` arm (next section).

#### Why `block` exists, and what was measured about skills (2026-09-06)

The upstream's mechanism is a rule that is **always present** (its skill text is copied into every
host's `CLAUDE.md`/adapter by a `SessionStart` hook), not a skill the router chooses. The `block`
arm carries exactly that — the eight-line *Lean Code* section of `personal-rules.md`, appended to
the cell's `CLAUDE.md` — and nothing else, so its Δ against `baseline` is the always-on mechanism
alone. The `skill` arm adds the skill on top; its Δ is the deliverable of item #146, and the
difference between the two is what the router-picked skill adds over the rule.

The split was forced by a measurement. Under `--setting-sources project,local` the user skills dir
is not loaded: on 2026-09-05, Claude Code 2.1.261, three review-lens cells run that way reported
"lean-code isn't in the available-skills list" and denied reads under `~/.claude/skills/` and
`~/ai-skills/`, so `skillOverrides.lean-code = "on"` in the project settings enabled nothing. The 27
cells of stamp `20260905-230209` ($9.08) therefore measured sentinel + block, and were relabelled
`block`. A **project** skill works: with `<cwd>/.claude/skills/lean-code` pointing at the checkout's
`skills/lean-code` (plus the same project settings and `CLAUDE.md`), a Haiku cell with `--tools ""`
listed exactly `lean-code` as available ($0.018), and one with `--tools "Skill"` loaded it and
returned its first heading verbatim, `# Lean code — the best code is the code never written`
($0.031). That is the layout the `skill` arm now uses, and the probe's fourth criterion re-checks
it before any matrix.

### Isolation probe (paid, before any matrix)

> Measured 2026-09-06 (Claude Code 2.1.261, Haiku): a project skill under `.claude/skills/<skill>` is
> discovered **only when the cwd is a git repository root**. The same skill-arm cwd answered
> `SKILLS: none` without `git init` ($0.006) and `SKILLS: bench-sentinel, lean-code` with it ($0.016).
> Every cell workspace is a git repo already; the probe cwd is initialised the same way.

Three calls per arm on Haiku, `--tools ""`, `--max-budget-usd 0.05`, on `--output-format
stream-json --verbose --include-hook-events`.

Default mode (`settings-sources`): each call runs in a throwaway cwd carrying the sentinel
`CLAUDE.md` and the arm's `.claude/settings.json`, with `--setting-sources project,local`; the
prompt asks for the sentinel line and `DONE`. Recorded per call: `BENCH-SENTINEL: <arm>` echoed;
every hook lifecycle event in the stream (`system/hook_started`, `hook_response`, …) with its
`hook_name`, and how many of them name one of the maintainer's hooks (`locale-rite`,
`backlog-rite`, `verify-rite`, `rtk`, `caveman`, `memory-autopush`); the mtime of the real
`~/.claude/.caveman-active` before and after (the plugin's `SessionStart` hook rewrites it under
`$CLAUDE_CONFIG_DIR || ~/.claude`); the JSON field names the CLI emitted. A fourth call per arm,
same flags, in the same kind of throwaway cwd (which in the `skill` arm carries
`.claude/skills/lean-code`), asks for the comma-separated names of the skills in the
available-skills list — only names in that list, never a skill merely mentioned in `CLAUDE.md`,
because the block names `lean-code` in prose. **Pass** = sentinel 3/3, hook events 0 (so the
maintainer's 0/3), marker mtime unchanged 3/3, and `skill_visible` 1/1 in `skill`, 0/1 in
`baseline` and `block`. `--matrix --arms skill` refuses unless the last probe recorded
`skill_visible: 1/1` for the skill arm — a probe from before the criterion (the one stamp
`20260905-230209` ran under) does not qualify.

Legacy modes (`config-dir`, `home`): the prompt also asks for the skills whose name contains
"lean" and whether any hook or rite injected text; recorded per call: sentinel echoed;
`<arm>/.caveman-active` absent; hook events; the model's own `HOOKS:` answer; files the CLI created
under the arm dir. **Pass** = sentinel 3/3, `.caveman-active` absent 3/3, hook events 0, `HOOKS:
yes` 0/3, `lean-code` listed 0/3 in `baseline` and 3/3 in `skill`. `--isolation auto` tries
`config-dir` first and `home` second.

In every mode the pass is recorded in `arms.json` with the `rules_sha` it was probed under and the
arms it covered, and `--matrix` refuses to run unless that sha is the arms' current one, the probed
mode matches the arm layout, and every requested arm was covered.

The lesson this encodes: the upstream's first agentic run had its `SessionStart` hook firing on
every arm, so the baseline was secretly running the skill (`benchmarks/results/2026-06-18-agentic.md`,
"A contamination bug we found in our own numbers").

## Cell

One cell = one task × one arm × one repetition, in a fresh git repository seeded from the task
and committed, then:

```
claude -p "<task prompt>" --model <id> --output-format json
       --setting-sources project,local --permission-mode acceptEdits          # default mode
       --disallowedTools Bash --strict-mcp-config --no-session-persistence --max-budget-usd 1.00
       --append-system-prompt "<NO_RUN + backlog-rite waiver>"
```

with the environment untouched except `CLAUDECODE` popped, `cwd` = the seeded repository (which
carries the arm's `.claude/settings.json` and the sentinel `CLAUDE.md` in its seed commit), stdout
to `_claude.json`, tree-killed after 300 s. In the legacy modes the two flags on the second line
are replaced by `--permission-mode bypassPermissions` and the environment carries
`CLAUDE_CONFIG_DIR=<arm>` (or `HOME=<arm>/home`). `NO_RUN` (ported from the upstream) tells every arm to
write the implementation, include tests if it normally would, and not run anything; the waiver
sentence tells the maintainer's rules that the backlog rite does not apply to the benchmark task,
so the baseline does not spend its turns asking for an issue.

Two budget layers: `--max-budget-usd 1.00` per cell, `--budget-usd` per run (the matrix stops and
reports when the summed `total_cost_usd` crosses it).

## Metrics per cell

| metric | source | note |
|---|---|---|
| `added_lines` | `git diff --cached --numstat HEAD`, code-suffix files that are not tests | **primary**: the `+N` a PR shows, comments included |
| `code_loc` | same diff, blank and comment lines dropped | secondary |
| `test_added_lines`, `test_files` | same diff, test paths (`tests/`, `test_*.py`, `*.test.*`, `*.spec.*`) | tests are a positive signal, never bloat |
| `correct`, `safe` | the task's `score()` executing the produced code (structural for `react-use-orders`, declared) | gates |
| `reuse` | fastapi (envelope + registered code), react (client + zod + no new dep) | reuse axis |
| `total_cost_usd`, `num_turns`, `duration_ms`, `usage.*`, `modelUsage` keys | `_claude.json` | field names verified by the probe on this CLI version |
| detectors | regex over the diff and the result text | `output_contract` (`skipped: X, add when Y`), `one_check`, `new_dependency`, `prose_gt_code`, `lean_marker` (`lean: <ceiling> -> <trigger>`), `class_added` |

*Amendment, 2026-09-06, after every cell (fact, not a rule):* `added_lines` reads the production
files of the diff, so a runnable check placed inside the product module (an `if __name__ ==
"__main__":` block of asserts) counts in full, while the same check in `test_*.py` counts in
`test_added_lines` only. Seen twice in the `skill` arm (`reuse-slug` run 1: 19 vs 9; `cache` run 1:
11 vs 3), never in `baseline` or `block`. The number is reported as the metric defines it; the
artefact is named in `results.md`, *Post-hoc observations*.

`vendor/ponytail/loc.js` is **not** a cell metric. It counts fenced code in chat output and is
kept only as the oracle the selftest compares the Python port against (22/22 sections).

### Flags (`--classify`)

| flag | rule |
|---|---|
| `prose_gt_code` | non-fenced result lines > `added_lines`, when `added_lines > 0` |
| `no_check` | no test lines and no `assert`/`__main__`/`def test_`/`it(`/`describe(` in the diff, when code was added |
| `new_dependency` | an import, a `package.json`/`requirements.txt` line, or an install command naming a package the seed did not declare |
| `guard_dropped` | a trust-boundary task with `safe = 0` (never the structural task) |
| `patched_caller_only` | `trace-transfer` with `correct = 1`, `safe = 0` (the named caller was guarded, the shared helper was not) |
| `reimplemented_existing` | `reuse-slug` with `safe = 0`; `fastapi-create-item` / `react-use-orders` with `reuse = 0` |
| `class_for_oneliner` | a `class` added in a task whose seed has none |
| `output_contract`, `lean_marker` | positive signals, counted, not judged |

*Amendment, 2026-09-05, after the baseline's flag sanity (`results.md`):* `new_dependency` reads
imports in production files only, and `class_for_oneliner` reads a `class` in production files
only. An `import pytest` or a `unittest.TestCase` subclass inside the test file the cell prompt
invites is recorded (`test_dependency`, `test_class_added`) and never flagged — the first
classification had 8/27 and 3/27 of exactly that. A manifest line or an install command still
counts wherever it appears. The frozen rules above are otherwise unchanged.

## Tasks (9)

| task | source | room | boundary | axis of the bad reference | scorer |
|---|---|---|---|---|---|
| `safe-path` | ponytail | over-build (helper vs framework) | yes | `../../etc/passwd` escapes | executes |
| `sql-user` | ponytail | surgical | yes | `' OR '1'='1` leaks rows | executes (sqlite) |
| `csv-sum` | ponytail | surgical | yes | a malformed row crashes the sum | executes |
| `cache` | ponytail | over-build (`lru_cache` vs a TTL class) | no | axis `correct`: no caching added | executes |
| `reuse-slug` | ponytail | surgical | no | re-implemented `slugify` diverges on accents | executes |
| `trace-transfer` | ponytail | surgical | no | only the named caller guarded | executes |
| `fastapi-create-item` | catalog | over-build | yes | any of `name ""`, `quantity -1`, `3.7`, `"abc"` (each alone) → 201/500; body `tenant_id` overrides the header; tenant B sees A | executes under the pinned venv (`fastapi.testclient`) |
| `fivem-shop-buy` | catalog | surgical | yes | forged `playerId` lands on the forged id; a `qty` of `-5`/`1e9`/`2.5`/`0` leaves a credit outside `[1, maxQty]` or a non-integer one | executes under `lua` 5.5 + stub |
| `react-use-orders` | catalog | over-build | no (reuse) | new dependency, raw `fetch`, no zod, no `apiClient` | **STRUCTURAL**, labelled |

Groups the verdict reads: **over-build** = `safe-path`, `cache`, `fastapi-create-item`,
`react-use-orders`; **trust boundary** = `safe-path`, `sql-user`, `csv-sum`, `fastapi-create-item`,
`fivem-shop-buy`; **root cause** = `trace-transfer`; **reuse** = `reuse-slug`, `react-use-orders`,
`fastapi-create-item`.

Every scorer proves itself before any spend: `run.py --selftest` requires the good reference to
score `correct = 1, safe = 1` and the bad reference to be caught on its declared axis, 18/18, plus
the `VARIANTS` each catalog task declares (the good reference with one decision changed and the
verdict written in `task.py`), 7/7.

`safe` on the two boundary tasks of the catalog judges the **state the code leaves behind**, not
the defensive style: on `fivem-shop-buy` rejecting an out-of-range `qty` and clamping it into
`[1, maxQty]` (the `Helpers.clampNum` the `fivem-lua` skill teaches, plus `floor`) are both safe,
and a forged `playerId` may be rejected or credited to `source` — which one happened is recorded in
`outcomes`, never scored. On `fastapi-create-item` every invalid body is fired alone, so a handler
that validates one field and stores the other is caught, and a `tenant_id` in the body must never
override the header. Neither the PROMPT nor the seed says "reject, do not clamp": that would test
instruction-following, not the doctrine.

## Sequence

1. `run.py --selftest` green (offline).
2. `run.py --prepare-arms --arms-root <scratch>/arms --rules-ref <sha>` (default
   `--isolation settings-sources`); preflight OK per arm.
3. `run.py --probe-isolation --arms-root <scratch>/arms --model claude-haiku-4-5-20251001` → pass
   (the mode is read from `arms.json`).
4. Pilot: Haiku, `n = 1`, 9 tasks, baseline only. Never reported as a number; its job is to
   confirm the JSON field names and that every cell writes a file.
5. Baseline: the maintainer's daily model as `--model` resolved from `~/.claude/settings.json`
   (`opus[1m]` on 2026-09-05), `n = 3`, 9 tasks, `--budget-usd 25` → `--classify` →
   `results/<stamp>-baseline-defects.md`. This is item 1's deliverable and the input to the
   skill's `proposal.md`.
6. Item 2: `run.py --prepare-arms --skill lean-code --claude-block research/lean-code/arms-block.md
   --rules-ref <sha>` — `baseline` unchanged, `block` with the block, `skill` with the block and
   `project_skill_path` = `skills/lean-code` of the checkout (nothing under `~/.claude/skills` is
   needed or read); the probe again (the arms moved, and the `skill` arm needs `skill_visible`
   1/1); arms `block` and `skill`, same `claude --version` as the baseline, same model id, `n = 3`
   (stamp `20260905-230209` is the `block` arm, relabelled); `--report <baseline> <block> <skill>`
   prints each treatment arm's Δ against the baseline and refuses to aggregate stamps whose
   version or model differ.

## Verdict (written before the number)

Let Δ = mean `added_lines` of `skill` relative to `baseline`, per task, over the over-build group.
The table is read for the `skill` arm; read for `block` it isolates the always-on mechanism and is
reported alongside, never as the skill's verdict.

| verdict | condition |
|---|---|
| **SHIP** (a number may appear in the skill's README) | `correct` ≥ baseline on every task; `safe` = 100% on the five boundary tasks; mean Δ ≤ −30% over the over-build group and **no** task above baseline +10%; `output_contract` in ≥ 2/3 of skill cells; `trace-transfer` root cause 6/6 (n=3 × 2 arms ≥ baseline, 3/3 in skill); `new_dependency` 0/N in skill |
| **INCONCLUSIVE** | Δ between −15% and −30%, or the dispersion (max − min) of a task's `added_lines` exceeds 50% of its mean → +2 repetitions on those tasks, then re-read |
| **NO-CLAIM** | Δ better than −15% but not enough for SHIP → the skill may ship for its review lens alone; no number in any README or SKILL.md |
| **REWRITE** | any guard dropped (`safe` < baseline on a boundary task); any task above baseline +10%; root cause below baseline; a new dependency the baseline did not add |

`react-use-orders` never feeds the `safe` gate (structural); it counts in Δ and in the reuse
flags only.

## Review lens — false-positive rules (written before the lens runs, item 2)

The lens (`delete:` `stdlib:` `native:` `yagni:` `shrink:`, closing `net: -N lines possible.`) is
run on the three real diffs of 2026-09-04 (`locale-rite.py` +408, `locale-stop-gate.py` +652,
`pre-commit-locale.sh` +217). Precision ≥ 0.7 with these findings counted as **false positives**:

1. a `delete:` on a selftest, a mutant, or an injected-defect case — the check is the product;
2. a `stdlib:`/`native:` naming a function absent from the runtime pinned by the repository
   (Python 3.14 stdlib, bash on the CI runner) — verify against the pin, not memory;
3. a line justified by the pull request's own mutant table or by a `KNOWN LIMIT` paragraph;
4. a `yagni:` on a guard at a trust boundary (validation of hook input, of a PR body, of a path
   from the environment) — carve-out, not bloat;
5. a `shrink:` whose replacement changes behaviour on an input the diff's tests cover.

## What this protocol does not cover

- One model id, one CLI version, one machine, one maintainer's rules file. Another model, another
  version or another rules file is another measurement.
- The interaction with `caveman` (stripped) and with the maintainer's hooks (stripped) is not
  measured; a session that runs them may behave differently.
- In the default mode the user's `~/.claude/CLAUDE.md` is the real one, not a copy frozen at a
  ref: a rules file that changes between two runs changes the baseline (`arm.json` keeps the
  `rules_sha` so the drift is visible). `~/.claude/skills/` is not loaded at all in this mode, so
  the skill under test reaches only the `skill` arm, as a project skill. That `--setting-sources
  project,local` drops the user hooks and plugins and skips the user skills dir was measured on
  Claude Code 2.1.261 only; another version re-runs the probe (the harness refuses a matrix whose
  `claude --version` differs from the arms', and a report whose stamps differ).
- Structural scoring for React; heuristic detectors for the marker and the contract.
- Nine tasks. A deterministic safety scorer is a floor, not a proof of security.
