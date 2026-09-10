# Protocol — measuring i-have-adhd against the incumbent, on the maintainer's own model

**Frozen** at base `fef050d` (master at the branch point of `backlog/246-i-have-adhd-research`,
2026-09-10), by the commit that introduces this file. The verdict thresholds below were written
**before any paid cell ran**. A later edit to a threshold is a new protocol version; numbers
measured under different versions are not compared.

What is measured: the **response text** a headless Claude Code session returns to the fourteen
chat prompts the upstream (`ayghri/i-have-adhd`, commit `ff690b6`, `vendor/i-have-adhd/PIN`) ships
as its evaluation cases — bare, with the incumbent the maintainer already runs (`caveman` 2.3.1,
`vendor/caveman/PIN`), and with the candidate — scored by the upstream's own blind paired judge
and by two counters, on the model the maintainer uses every day, through two injection paths.
What is not measured: anything the session writes to disk (the cases run with tools disabled),
agentic behaviour, execution speed, the maintainer's user-level hooks, the quality of the judge
itself (it is the same model family as the generator, see *What this does not cover*).

The method — conditions proven isolated by a probe before spending, a verdict table written
before the number, exports stripped of session identifiers — is `research/lean-code/protocol.md`.
This file states only what differs: the instrument is a judge, not a counter, and the treatment
enters through a hook, not through `CLAUDE.md`.

## Conditions

| condition | what the session sees, beyond the bare prompt |
|---|---|
| `baseline` | nothing. The bare task prompt, no plugin, no style instruction |
| `comparator` | the incumbent: `caveman` — the plugin installed on the maintainer's machine (`plugin` mode) or its `skills/caveman/SKILL.md` (`prompt` mode), at level `full`, the level this maintainer runs |
| `candidate` | `i-have-adhd` — the vendored plugin at the pinned commit (`plugin` mode) or its `skills/i-have-adhd/SKILL.md` (`prompt` mode) |

The comparator is a condition and not a footnote because the question the item asks is not
"does the candidate beat nothing" but "does it beat what is already running".

## Injection modes

Every number carries the mode it came from. The two modes are two treatments, not two views of
one.

| mode | how the treatment enters | why it exists |
|---|---|---|
| `prompt` | the upstream's own path: the skill body (frontmatter stripped) wrapped in `<response_style>…</response_style>` ahead of `<task>…</task>` in the user prompt (`run_evals._condition_prompt`, unchanged) | comparability with the upstream's published run, which used exactly this |
| `plugin` | the real path: the plugin loaded with `--plugin-dir <dir>` into a session whose `CLAUDE_CONFIG_DIR` is a scratch directory per condition; the `SessionStart` hook of the plugin injects the rules. The candidate's config dir carries the empty flag file `.i-have-adhd-always` that `hooks/always-on.mjs` reads; the comparator's cell env carries `CAVEMAN_DEFAULT_MODE=full` so the level is pinned and not read from the operator's machine; the baseline's config dir is empty and no plugin is loaded. The prompt is bare in all three | what the maintainer would actually install |

In both modes every cell passes `--setting-sources ""`, the upstream's isolation flag: the user,
project and local settings files are not read, so none of the maintainer's hooks, plugins or
skills reach the cell. In `plugin` mode the only plugin in the session is the one `--plugin-dir`
names. The cell's working directory is an empty temporary directory (`run_evals._neutral_cwd`).

## Cell

One cell = one `(case, trial, condition, mode)`. The runner is the upstream's
`evals/runners.example.json` `claude` entry with the model pinned to the maintainer's, verbatim
otherwise:

```text
claude --disable-slash-commands --print --output-format json --no-session-persistence
       --setting-sources "" --model claude-fable-5-1 --tools ""
       [--plugin-dir <dir>]                       # plugin mode, treated conditions only
       --max-budget-usd <remaining>  <prompt>
```

`--tools ""` disables every tool: the cases are chat prompts and the response text is the whole
output. The model id is the `model` of the maintainer's `~/.claude/settings.json` without its
context-window suffix. `total_cost_usd` and `usage` are read from the CLI's JSON result. A cell
that returns non-zero after three attempts is recorded as failed and the matrix continues; a
missing condition makes the `(case, trial)` group unjudgeable and the judge reports it.

Every cell's exact command is written to `<cell>/command.txt` before it runs; stdout and stderr
are kept beside it; the run stops when the reported spend reaches `--budget-usd` (at most 25 per
invocation, the upstream harness's own ceiling) and resumes from the completed keys on the next
invocation. The whole item was authorised up to $40 in total (pilot, probes, matrices and
judging); amendment of 2026-09-10, after five daily-model cells and before any judged one, a
budget and not a threshold: the first five cells measured a mean of $0.129 per cell (the CLI
re-creates the system-prompt cache in every `--print` process: `cache_read_input_tokens` 0,
`cache_creation_input_tokens` 4.4–6.8k), which projects the protocol as written at $47–50, and
the maintainer raised the ceiling to **$55** rather than cut `n` or change the judge. The results
file records what was spent.

## Isolation probe (paid, small, before any matrix cell)

Three calls per condition per mode on `claude-haiku-4-5-20251001` (hook firing does not depend
on the model), prompt `Reply with the single word DONE.`, `--output-format stream-json --verbose
--include-hook-events`, `--max-budget-usd 0.05`. `parse_stream` of `research/lean-code/run.py`
lists the hook lifecycle events. The probe **passes** a mode only when:

| mode | `candidate` | `comparator` | `baseline` |
|---|---|---|---|
| `plugin` | a hook event naming `SessionStart` in 3/3 calls, and the `result` present | same, 3/3, and `.caveman-active` present in its config dir afterwards | hook events 0/3, no `.caveman-active` |
| `prompt` | hook events 0/3 | hook events 0/3 | hook events 0/3 |

A failed probe stops the matrix for that mode. If `--plugin-dir` turns out not to fire
`SessionStart` under `--print`, that is the finding for `plugin` mode: it is recorded and the
mode does not run; nothing is substituted for it.

## Metrics per response

**Judged** — the upstream's rubric (`vendor/i-have-adhd/evals/rubric.md`, sha256
`ba3887f8dbb0492cabac58ef07b9be57df71085a2324a97768103efe2676241a`, recorded with every stamp),
unchanged: `correctness` 35 %, `autonomy` 25 %, `actionability` 20 %, `safety` 10 %, `concision`
10 %, each 1–5, plus `blocker` (true/false) and a one-sentence note. The judge is the upstream's
`scripts/judge.py`, unchanged: one call per `(case, trial)` group grading the three conditions
side by side, labels `A/B/C` permuted by a digest of the group key, only the `judge:begin/end`
region of the rubric sent. Judge model: `claude-fable-5-1`, the same as the generator; the judge
runs with no plugin and a scratch config dir. `weighted` = the rubric's weighted mean.

**Counted** — on the same response text, never judged:

- `output_tokens`: `usage.output_tokens` from the CLI's JSON result of that cell.
- `forbidden_phrase_hits`: occurrences, case-insensitive, of the phrases the candidate's own rule
  10 forbids, taken literally from `skills/i-have-adhd/SKILL.md`: `Great question`, `Let me`,
  `I'll`, `Sure!`, `Looking at your`, `To answer your question`, `I've now done`, `Let me know if
  you need anything else`, `Hope this helps`, `Happy to clarify`, `Feel free to ask`. A crude
  counter (`Let me` also matches ordinary prose); it is reported as the shape the treatment was
  asked to produce, not as quality.

## Cases and trials

The fourteen cases of `vendor/i-have-adhd/evals/cases.jsonl`, unchanged, three trials each, so
that the numbers are comparable with the upstream's published run. `agent-owned-edit` is kept
although the upstream itself recorded that no run can pass it with tools disabled; the aggregate
includes it (as the upstream's does) and the per-case table shows it apart. Per-case deltas
below 0.5 are noise at three trials — the upstream measured per-case standard deviations up to
0.95 — and the verdict is read on the per-condition aggregate only.

Rows per mode: 14 cases × 3 conditions × 3 trials = 126 responses, 42 judge groups.

## Sequence

1. `run.py --selftest` (offline): vendor hashes against both `PIN`s, the upstream's own unit
   tests, the import contract, the counters and the verdict table on synthetic scores.
2. `run.py --prepare-conditions --conditions-root <outside the repository>`.
3. Pilot: `--matrix --mode <each> --model claude-haiku-4-5-20251001 --trials 1 --case
   direct-answer --case error-report` — proves the loop, the parsing and the judge end to end.
   **Never reported.**
4. `run.py --probe --mode <each>` — the table above; a failed mode does not proceed.
5. `run.py --selftest --matrix --mode prompt`, then `--mode plugin`, on `claude-fable-5-1`,
   `--trials 3`, within `--budget-usd`.
6. `run.py --judge --mode <each>`.
7. `run.py --report <stamps> --export results/<stamp>-export.json`; `results.md` reads the table
   below by the letter.

## Verdict (written before the number)

Read per mode on the per-condition means over all 42 rows, then combined. `W` is the weighted
score; `Δ` is `W(candidate) − W(comparator)`.

| verdict | condition, read by the letter |
|---|---|
| **ADOPT** | in **both** modes: `Δ ≥ +0.2`; `correctness(candidate) ≥ correctness(baseline) − 0.1`; `safety(candidate) ≥ safety(baseline) − 0.1`; candidate blockers outside `agent-owned-edit` = 0 |
| **REJECT** | in **any** mode: `Δ < 0`; **or** the candidate carries `blocker: true` on `partial-success` in 2 or more of its 3 trials — the regression the upstream's own run found, and the grounding failure `verify-before-claiming` exists to stop |
| **NO-CLAIM** | everything else: `0 ≤ Δ < 0.2`, a correctness or safety regression beyond 0.1, a candidate blocker outside `agent-owned-edit`, or modes that disagree |

Consequences, also decided now: **ADOPT** opens item 2 (what to adopt and how — a decision, not
this item); **REJECT** and **NO-CLAIM** open nothing. Under NO-CLAIM and REJECT no number from
this measurement appears in any README or SKILL.md; under ADOPT the number appears with the mode,
the model id, the CLI version, `n`, the judge model and this file beside it. The `release_gate`
that the upstream's `summarize_scores` computes (candidate vs baseline) is reported as the
upstream's gate, for comparability, and is not the verdict.

## What this does not cover

- **Chat without tools.** Every cell runs `--tools ""`. Nothing here measures what either plugin
  does to an agentic session — the item's phase 3, if there is one.
- **A judge of the same family.** The grader is the model being graded, blind to the condition
  but not to its own taste. A cross-family judge is the natural next control; not this item.
- **Three trials.** Enough for the aggregate, not for a per-case claim.
- **The comparator at one level.** `caveman` is measured at level `full` through its hooks; its
  other levels and the maintainer's user-level hooks (`locale-rite`, `backlog-rite`,
  `verify-rite`) are not in any condition. Amendment of 2026-09-10, after the probe and before
  any daily-model cell, a fact and not a threshold: the probe showed that in a `--print` session
  the plugin's `UserPromptSubmit` tracker fires too (`CAVEMAN MODE ACTIVE (full) — session
  ruleset applies`), so the comparator cell carries both of the plugin's hooks, as the maintainer's
  sessions do; the earlier text of this bullet said the tracker was outside the cell.
- **`agent-owned-edit`.** Impassable with tools disabled, by the upstream's own finding; kept for
  comparability, shown apart.
- **The upstream's number.** `evals/RESULTS.md` of the upstream (opus-4-8, Claude Code 2.1.220,
  2026-08-02) is the upstream's, cited with its conditions; nothing here is compared with it
  across models.
