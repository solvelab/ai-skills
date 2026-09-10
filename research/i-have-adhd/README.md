# research/i-have-adhd

Backing evidence for issue #246: does `i-have-adhd` (ayghri/i-have-adhd, MIT, a response-style
skill) do better than the incumbent the maintainer already runs (`caveman`), on the maintainer's
own model, through the real installation path — measured before anything is adopted, with the
verdict written before the number.

This directory sits **outside `skills/`** on purpose. `generate.sh` publishes only `skills/`, so
everything here is versioned and reviewable without being shipped to any project that enables a
plugin. Nothing in the catalog cites a number from here unless the verdict below allows it.

## Read in this order

| File | What it is |
|---|---|
| [`protocol.md`](protocol.md) | **The point of all of this.** Conditions, the two injection modes, the cell, the probe, the metrics, the fourteen cases, the sequence, and the ADOPT / NO-CLAIM / REJECT table — frozen before any paid cell ran; amendments dated. |
| [`run.py`](run.py) | The instrument. `--selftest` proves it offline; `--prepare-conditions`, `--probe`, `--matrix`, `--judge`, `--report --export`, `--teardown`. Its docstring carries the KNOWN LIMIT list. |
| [`PIN`](PIN) | What `run.py` imports from `research/lean-code/run.py` and from the vendored upstream, and the exact state each was read at. The `contract` selftest group enforces it. |
| [`vendor/i-have-adhd/`](vendor/i-have-adhd/PIN) | The upstream's harness, cases, rubric, tests and the plugin itself, unmodified, with commit and sha256 per file. |
| [`vendor/caveman/`](vendor/caveman/PIN) | The comparator's skill text and licence, plus the hashes of the installed plugin files the hook loads. |
| [`results.md`](results.md) | **What has been measured.** The probe, the per-mode tables, the counters, the verdict read by the letter, the spend, and what it does not cover. |
| [`results/`](results/README.md) | The stripped files behind it. |

## Running things

```bash
# 1. prove the instruments (offline, < 5 s): PIN hashes, the upstream's unit tests, the import
#    contract, the counters, the verdict table on synthetic scores, the stripper, the preflight
python3 research/i-have-adhd/run.py --selftest

# 2. conditions, OUTSIDE the repository: one CLAUDE_CONFIG_DIR per (mode, condition), the
#    always-on flag in plugin/candidate, a mode-600 copy of ~/.claude/.credentials.json in each
python3 research/i-have-adhd/run.py --prepare-conditions --conditions-root /tmp/ihadhd/conds

# 3. PAID, small (18 Haiku calls, ~$0.27): the hook fires where it must and nowhere else
python3 research/i-have-adhd/run.py --probe --conditions-root /tmp/ihadhd/conds \
    --probe-out research/i-have-adhd/results/<stamp>-probe.json

# 4. PAID: one mode at a time; refuses without a green selftest in the same invocation and a
#    passed probe for that mode; resumable with --stamp; stops at --budget-usd (<= 25)
python3 research/i-have-adhd/run.py --selftest --matrix --mode prompt --model claude-fable-5-1 \
    --trials 3 --stamp <stamp> --conditions-root /tmp/ihadhd/conds --runs-root /tmp/ihadhd/runs --budget-usd 18
python3 research/i-have-adhd/run.py --selftest --matrix --mode plugin ...   # same, plugin mode

# 5. PAID: the upstream's blind judge, one call per (case, trial) group, three conditions each
python3 research/i-have-adhd/run.py --judge /tmp/ihadhd/runs/<stamp>-prompt --conditions-root /tmp/ihadhd/conds

# 6. offline: one run per mode; refuses runs whose CLI version, model, rubric or skill hashes differ
python3 research/i-have-adhd/run.py --report /tmp/ihadhd/runs/<stamp>-prompt /tmp/ihadhd/runs/<stamp>-plugin \
    --export research/i-have-adhd/results/<stamp>-export.json

# 7. delete the scratch conditions (the credential copies with them)
python3 research/i-have-adhd/run.py --teardown --conditions-root /tmp/ihadhd/conds
```

## Status

**Measured on 2026-09-10. Verdict: NO-CLAIM.** Probe PASS in both injection modes (the plugin's
`SessionStart` hook fires under `--print` via `--plugin-dir`); `prompt` mode complete and judged
on `claude-fable-5-1` / Claude Code `2.1.267` (126 responses, 42 groups): candidate 3.860 vs
comparator 3.842 vs baseline 3.626 weighted, Δ +0.018; `plugin` mode stopped by the maintainer at
101 responses, unjudged; $66.64 estimated. No number from here enters any README or SKILL.md.
