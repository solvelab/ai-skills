# Results — i-have-adhd against caveman, on the maintainer's model

Reproduce with the commands in [README.md](README.md); the rules the numbers are read by are in
[protocol.md](protocol.md), frozen before any daily-model cell ran. Everything below is measured;
where a number is the upstream's it says so.

## Method

Three conditions (`baseline`, `comparator` = the installed `caveman` 2.3.1 at level `full`,
`candidate` = `i-have-adhd` at commit `ff690b6`), two injection modes (`prompt`: the skill body
wrapped in the upstream's `<response_style>` block; `plugin`: `--plugin-dir` plus the plugin's own
`SessionStart` hook into a scratch `CLAUDE_CONFIG_DIR`), the upstream's fourteen chat cases, three
trials, `--tools ""`, `--setting-sources ""`. Judged by the upstream's blind paired judge (one call
per `(case, trial)` group, labels permuted per group, rubric sha256
`ba3887f8…`), on the same model as the generator. Counted beside the judge: `output_tokens` and
`forbidden_phrase_hits`. Generator and judge: `claude-fable-5-1`; Claude Code `2.1.267`;
Python 3.14.5; node v26.0.0.

## Offline instruments — 2026-09-10

`python3 research/i-have-adhd/run.py --selftest` -> `vendor 2/2  upstream 2/2  contract 14/14
counters 5/5  verdict 18/18  stripper 3/3  preflight 10/10  selftest 54/54` (0.8 s). The
`upstream` group runs the vendored `tests/` of ayghri/i-have-adhd with `unittest`; the `vendor`
group re-hashes every file of both `PIN`s, including the four installed caveman files the hook
loads.

## Isolation probe — `results/20260909-222459-probe.json`

Model `claude-haiku-4-5-20251001`, three calls per condition per mode, `--output-format
stream-json --verbose --include-hook-events`, $0.2707 in total.

| mode | condition | `SessionStart` fired | hook events per call | `.caveman-active` after | verdict |
|---|---|---:|---|---|---|
| `prompt` | baseline / comparator / candidate | 0/3 each | 0 / 0 / 0 | no | PASS |
| `plugin` | baseline | 0/3 | 0 / 0 / 0 | no | PASS |
| `plugin` | comparator | 3/3 | 4 / 4 / 4 | **yes** | PASS |
| `plugin` | candidate | 3/3 | 2 / 2 / 2 | no | PASS |

What the stream carried: in `plugin/candidate` the `hook_response` of `SessionStart:startup`
begins `ADHD MODE ACTIVE (always-on). The ruleset below applies to every response.` and
`system/init` lists `{'name': 'i-have-adhd', 'version': '0.3.0'}`; in `plugin/comparator` the
`SessionStart` response begins `CAVEMAN MODE ACTIVE — level: full` and a second hook,
`UserPromptSubmit`, answers `CAVEMAN MODE ACTIVE (full) — session ruleset applies.` — the
plugin's tracker fires in a `--print` session too, which the first text of the protocol had
assumed it would not (amended, dated, no threshold touched). The baseline's `system/init` lists
`plugins: []`. So `--plugin-dir` does fire `SessionStart` under `--print` with
`--setting-sources ""` and a scratch `CLAUDE_CONFIG_DIR`, and the rules the treated conditions
see are the plugins' own text, not a paraphrase.

## Pilot — never reported

Two Haiku runs (`20260909-222611-prompt`, `20260909-222653-plugin`), one trial, two cases, three
conditions, judged by Haiku: 12 cells, 4 judge groups, $0.3382. They proved the loop, the parsing,
the judge call and the export end to end; by protocol their scores are not reported.

## The daily model — stamp `fable-01`, `results/fable-01-export.json`

Generator `claude-fable-5-1`, Claude Code `2.1.267`, three trials, `--tools ""`. The `prompt` mode
ran to completion and was judged; the `plugin` mode was stopped by the maintainer at 101 of 126
responses, unjudged, when the spend passed what the question was worth (see *Spend*). Every number
below says which mode it came from.

### Mode `prompt` — 126 responses, 42 judged groups, judge `claude-fable-5-1`

| condition | rows | correctness | autonomy | actionability | safety | concision | **weighted** | blockers | blockers excl. `agent-owned-edit` | output_tokens | of which thinking | forbidden hits | tool markup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 42 | 3.690 | 3.595 | 3.286 | 4.405 | 3.381 | **3.626** | 9 | 9 | 670.9 | 92.7 | 0.48 | 11/42 |
| `comparator` (caveman) | 42 | 3.881 | 3.810 | 3.548 | 4.548 | 3.667 | **3.842** | 6 | 5 | 716.4 | 126.2 | 0.00 | 14/42 |
| `candidate` (i-have-adhd) | 42 | 3.810 | 3.762 | 3.762 | 4.405 | 3.929 | **3.860** | 5 | 4 | 2763.8 | 157.6 | 0.00 | 10/42 |

Δ (candidate − comparator, weighted) = **+0.018**. Candidate `partial-success` blocker trials: 0.
The upstream's own release gate (candidate vs baseline) fails on *"Candidate has blocking safety or
correctness findings"* — the same rule it failed on in the upstream's run.

Per case (weighted mean over three trials; deltas below 0.5 are noise at this `n`):

| case | baseline | comparator | candidate | cand − comp |
|---|---:|---:|---:|---:|
| `agent-owned-edit` (impassable without tools) | 2.85 | 3.02 | 2.65 | −0.37 |
| `casual-message` | 4.52 | 4.37 | 4.93 | +0.57 |
| `code-answer` | 5.00 | 5.00 | 5.00 | 0.00 |
| `complex-plan` | 2.38 | 3.58 | 4.18 | +0.60 |
| `concept-explanation` | 4.83 | 4.00 | 4.78 | +0.78 |
| `debugging-cause` | 2.35 | 3.58 | 1.38 | **−2.20** |
| `destructive-action` | 3.22 | 3.33 | 3.55 | +0.22 |
| `direct-answer` | 5.00 | 5.00 | 5.00 | 0.00 |
| `error-report` | 2.55 | 2.07 | 3.35 | +1.28 |
| `long-form-request` | 4.80 | 4.38 | 4.82 | +0.43 |
| `medical-boundary` | 4.65 | 3.97 | 4.73 | +0.77 |
| `multi-step-progress` | 2.20 | 3.80 | 3.63 | −0.17 |
| `partial-success` | 4.45 | 4.58 | 3.15 | **−1.43** |
| `real-ambiguity` | 1.97 | 3.10 | 2.87 | −0.23 |

### Mode `plugin` — 101 responses (34 / 34 / 33), not judged

Counted only:

| condition | rows | output_tokens | of which thinking | visible | forbidden hits | tool markup |
|---|---:|---:|---:|---:|---:|---:|
| `baseline` | 34 | 787.9 | 113.5 | 674.4 | 0.53 | 11/34 |
| `comparator` (caveman, both hooks) | 34 | 891.6 | 147.9 | 743.7 | 0.00 | 12/34 |
| `candidate` (i-have-adhd, hook) | 33 | 1081.4 | 252.5 | 828.9 | 0.00 | 5/33 |

## Verdict, by the letter of `protocol.md`: **NO-CLAIM**

- `prompt`: Δ = +0.018 < +0.2; and the candidate carries 4 blockers outside `agent-owned-edit`.
- `plugin`: 101 responses, none judged — the mode was not measured to the end.
- REJECT did not trigger: Δ is not negative, and the candidate drew no `partial-success` blocker.

Read plainly: on the maintainer's model, through the upstream's own injection path, `i-have-adhd`
and the incumbent `caveman` land within two hundredths of each other on the judged score, both
about +0.2 above the bare baseline, and the candidate gets there writing about four times the
output tokens of the comparator (2764 vs 716, prompt mode; 1081 vs 892 by hook). Nothing here says
the candidate is worse; nothing here says it adds anything the incumbent does not already give.

## Post-hoc observations (2026-09-10, after the letter was applied)

- **Tool-call markup as text is the dominant failure, in every condition.** With `--tools ""`
  the model still "calls" tools: `<invoke name="Bash">…` blocks, or a bare tool name followed by
  a JSON object, written into the answer. 11/42 baseline, 14/42 comparator, 10/42 candidate
  responses in prompt mode carry it (11/34, 12/34, 5/33 by hook). Most blockers the judge raised
  are this: *"issues tool calls but never returns a diagnosis"*, *"ran the same directory listing
  ten times and never produced a plan"*. The upstream saw 3 of 84 such responses on opus-4-8; on
  `claude-fable-5-1` the rate is an order of magnitude higher. It hits the two treated conditions
  harder than the bare baseline in prompt mode, so a rule that says "do the work" pushes a
  tool-less session into pretending to. This is a harness artifact of chat-only evaluation of an
  agentic CLI, not a property of either skill — and it is the reason no number here should be
  read as agentic behaviour.
- **Four runaway cells.** One response ran to 64,000 output tokens (`real-ambiguity`,
  candidate, plugin mode) looping on the markup above; three others were cut by the per-call cap
  ($3.34 before the cap existed, then $4.25, $4.34, $4.44). They are counted in the spend and
  their `(case, trial)` groups are unjudgeable.
- **`debugging-cause` and `partial-success` are where the candidate loses to the incumbent**
  (−2.20 and −1.43). On `debugging-cause` all three candidate trials ended in tool-call text with
  no diagnosis (correctness 1/5 each). On `partial-success` the judge wrote *"states a guessed
  cause as fact"* in two of three trials — the mechanism the upstream itself suspected behind its
  own regression on this case (rule 8, *state cause and fix*) — without marking a blocker, so the
  REJECT rule did not fire. Directionally it is the same finding as the upstream's.
- **Where the candidate wins** (`error-report` +1.28, `concept-explanation` +0.78,
  `medical-boundary` +0.77, `complex-plan` +0.60, `casual-message` +0.57) the comparator's
  compression is what the judge penalised: caveman's fragments read as missing substance on
  explanatory prompts. The candidate spends four times the tokens to get there.
- **`forbidden_phrase_hits` went to zero under both treatments** (0.48 baseline → 0.00), so the
  shape both rules ask for is produced; the judged score says the shape is not what separates them.

## Verbosity — the question the maintainer actually asked (post hoc, no new spend)

The item's judged score answers "is it better"; the maintainer's question was "does it make the
model less verbose than what I already run". Length, counted on the same responses, responses
that carry tool-call markup excluded (they are loops, not answers):

| mode | condition | clean responses | median chars | median words | median visible tokens |
|---|---|---:|---:|---:|---:|
| `prompt` | baseline | 31 | 226 | 31 | 112 |
| `prompt` | comparator (caveman) | 28 | 402 | 59 | 213 |
| `prompt` | candidate (i-have-adhd) | 27 | 597 | 97 | 214 |
| `plugin` | baseline | 23 | 210 | 29 | 146 |
| `plugin` | comparator (caveman) | 22 | 453 | 69 | 243 |
| `plugin` | candidate (i-have-adhd) | 28 | 479 | 83 | 194 |

Paired, same `(case, trial)`, both responses clean:

| mode | pairs | candidate shorter than caveman | median chars ratio cand/caveman | pairs | candidate shorter than baseline | median ratio cand/baseline |
|---|---:|---:|---:|---:|---:|---:|
| `prompt` | 25 | 7 | 1.11 | 24 | 12 | 0.98 |
| `plugin` | 20 | 9 | 1.00 | 21 | 14 | 0.89 |

Read plainly: on `claude-fable-5-1`, `i-have-adhd` is **not less verbose than `caveman`** — equal by
hook, 11 % longer by prompt, shorter in fewer than half the pairs — and against no skill at all
it is a coin flip (shorter in 12 of 24 and 14 of 21 pairs, −2 % and −11 % at the median). Both
skills make the bare model write *more* characters on these fourteen prompts, not fewer: numbered
steps, restated state and a closing "Next:" line cost characters, and the bare model's answers to
the short cases were already terse. The candidate's own README says as much — *"Output is not
just brief. It is shaped"* — it is a shape rule, not a brevity rule; the brevity rule is the one
already installed. The judged `concision` dimension (candidate 3.93 > caveman 3.67 > baseline
3.38, prompt mode) measures filler and tangents, not length, and moved the other way.

## Spend

| item | estimated cost (CLI `total_cost_usd`) |
|---|---:|
| probe (Haiku, 18 calls) | $0.27 |
| pilot (Haiku, 12 cells + 4 judge groups) | $0.34 |
| `prompt` generation, 126 cells (incl. one $3.34 failed call) | $28.62 |
| `prompt` judge, 42 groups | $8.06 |
| `plugin` generation, 101 cells + 3 failed calls ($13.03) | $29.36 |
| `plugin` judge | $0.00 (not run) |
| **total** | **$66.64** |

The account is a subscription (`subscriptionType: max`), so these are the CLI's estimates, not
invoices. The ceiling moved four times ($40 → 55 → 70 → 78) as the per-cell cost, the judge cost
and the runaway cells surfaced; the maintainer stopped the spend at $66.64 with the plugin mode
unjudged. Two subscription session limits (01:01 and ~13:30 local) stopped the matrices; the
resumable key absorbed both. Attempts killed at the 300 s timeout before the accounting fix may
have spent without being counted; the number above is a floor.

## What this does not cover

Everything in `protocol.md`, *What this does not cover*, plus: the `plugin` mode has no judged
score at all, so the real installation path is measured only by its counters; and the tool-markup
artifact above means the judged score in prompt mode is partly a measurement of how each rule
behaves when the model believes it has tools and does not.

