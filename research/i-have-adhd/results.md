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

<!-- daily-model sections are appended by the matrices and the judge -->
