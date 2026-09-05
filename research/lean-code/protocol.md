# Protocol — measuring a code-volume doctrine on the maintainer's own model

**Frozen** at base `7709622` (master at the branch point of `backlog/145-lean-code-research`,
2026-09-05), by the commit that introduces this file. The verdict thresholds below were written
**before any paid cell ran**. A later edit to a threshold is a new protocol version; numbers
measured under different versions are not compared.

What is measured: the code a real headless Claude Code session leaves behind in a seeded git
repository, with and without the `lean-code` doctrine, on the model the maintainer uses every day.
What is not measured: chat output (the metric the upstream retracted), execution speed, quality as
judged by an LLM, anything under the maintainer's `caveman` plugin.

## Arms

| arm | what the session sees | when |
|---|---|---|
| `baseline` | `CLAUDE.md` = `claude/global/personal-rules.md` at the pinned ref + sentinel; `skills/` = every catalog skill at that ref **except** `lean-code`; `settings.json` = the maintainer's minus `hooks`, `enabledPlugins`, `extraKnownMarketplaces`, `statusLine`, `permissions` (keeps `model`, `effortLevel`, `modelSettings`, `skillOverrides`) | item 1 (this) and item 2 |
| `skill` | same, plus `skills/lean-code` and the *Lean Code* block in `personal-rules.md` at the ref that carries them | item 2 |
| `ponytail-ref` | baseline plus the upstream plugin via `--plugin-dir` | optional, item 2, off by default |

Each arm is a directory outside the repository, used as `CLAUDE_CONFIG_DIR` (or as `HOME/.claude`
when the probe says the variable does not redirect everything). Credentials are copied with mode
600. The rules file and the skills tree come from `git archive <ref>`, never from the working tree,
so an arm is frozen at a sha even while the repository moves.

`skillOverrides` is kept on purpose: it turns 16 skills off in the maintainer's real sessions; a
baseline without it would measure a user who does not exist.

### Isolation probe (paid, before any matrix)

Three calls per arm on Haiku, `--tools ""`, `--max-budget-usd 0.05`, prompt asking for the
sentinel line, the skills whose name contains "lean", and whether any hook or rite injected text.
Recorded per call: `BENCH-SENTINEL: <arm>` echoed; `<arm>/.caveman-active` absent (the maintainer's
plugin writes it under `CLAUDE_CONFIG_DIR` at `SessionStart`); stream events mentioning a hook;
the model's own `HOOKS:` answer; the JSON field names the CLI emitted; files the CLI created under
the arm dir. **Pass** = sentinel 3/3, `.caveman-active` absent 3/3, hook events 0, `HOOKS: yes` 0/3,
`lean-code` listed 0/3 in `baseline` and 3/3 in `skill`. Auto mode tries `config-dir` first and
`home` second; `--matrix` refuses to run until `arms.json` records a pass.

The lesson this encodes: the upstream's first agentic run had its `SessionStart` hook firing on
every arm, so the baseline was secretly running the skill (`benchmarks/results/2026-06-18-agentic.md`,
"A contamination bug we found in our own numbers").

## Cell

One cell = one task × one arm × one repetition, in a fresh git repository seeded from the task
and committed, then:

```
claude -p "<task prompt>" --model <id> --output-format json --permission-mode bypassPermissions
       --disallowedTools Bash --strict-mcp-config --no-session-persistence --max-budget-usd 1.00
       --append-system-prompt "<NO_RUN + backlog-rite waiver>"
```

with `CLAUDE_CONFIG_DIR=<arm>` (or `HOME=<arm>/home`), `cwd` = the seeded repository, stdout to
`_claude.json`, tree-killed after 300 s. `NO_RUN` (ported from the upstream) tells every arm to
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

## Tasks (9)

| task | source | room | boundary | axis of the bad reference | scorer |
|---|---|---|---|---|---|
| `safe-path` | ponytail | over-build (helper vs framework) | yes | `../../etc/passwd` escapes | executes |
| `sql-user` | ponytail | surgical | yes | `' OR '1'='1` leaks rows | executes (sqlite) |
| `csv-sum` | ponytail | surgical | yes | a malformed row crashes the sum | executes |
| `cache` | ponytail | over-build (`lru_cache` vs a TTL class) | no | axis `correct`: no caching added | executes |
| `reuse-slug` | ponytail | surgical | no | re-implemented `slugify` diverges on accents | executes |
| `trace-transfer` | ponytail | surgical | no | only the named caller guarded | executes |
| `fastapi-create-item` | catalog | over-build | yes | `{"name": "", "quantity": -1}` → 201, or tenant B sees A | executes under the pinned venv (`fastapi.testclient`) |
| `fivem-shop-buy` | catalog | surgical | yes | forged `playerId` credited; `qty` `-5`/`"10"`/`1e9` accepted | executes under `lua` 5.5 + stub |
| `react-use-orders` | catalog | over-build | no (reuse) | new dependency, raw `fetch`, no zod, no `apiClient` | **STRUCTURAL**, labelled |

Groups the verdict reads: **over-build** = `safe-path`, `cache`, `fastapi-create-item`,
`react-use-orders`; **trust boundary** = `safe-path`, `sql-user`, `csv-sum`, `fastapi-create-item`,
`fivem-shop-buy`; **root cause** = `trace-transfer`; **reuse** = `reuse-slug`, `react-use-orders`,
`fastapi-create-item`.

Every scorer proves itself before any spend: `run.py --selftest` requires the good reference to
score `correct = 1, safe = 1` and the bad reference to be caught on its declared axis, 18/18.

## Sequence

1. `run.py --selftest` green (offline).
2. `run.py --prepare-arms --arms-root <scratch>/arms --rules-ref <sha>`; preflight OK per arm.
3. `run.py --probe-isolation --arms-root <scratch>/arms --model claude-haiku-4-5-20251001` → pass.
4. Pilot: Haiku, `n = 1`, 9 tasks, baseline only. Never reported as a number; its job is to
   confirm the JSON field names and that every cell writes a file.
5. Baseline: the maintainer's daily model as `--model` resolved from `~/.claude/settings.json`
   (`opus[1m]` on 2026-09-05), `n = 3`, 9 tasks, `--budget-usd 25` → `--classify` →
   `results/<stamp>-baseline-defects.md`. This is item 1's deliverable and the input to the
   skill's `proposal.md`.
6. Item 2: arms `baseline` + `skill`, same `claude --version`, same model id, `n = 3`;
   `--report` refuses to aggregate stamps whose version or model differ.

## Verdict (written before the number)

Let Δ = mean `added_lines` of `skill` relative to `baseline`, per task, over the over-build group.

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
- Structural scoring for React; heuristic detectors for the marker and the contract.
- Nine tasks. A deterministic safety scorer is a floor, not a proof of security.
