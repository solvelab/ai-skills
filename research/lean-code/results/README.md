# results/

Aggregated, anonymised outputs of paid runs land here, written by `run.py --export`:

- `<stamp>-probe.json` — the isolation probe (sentinel, hook side-effects, event vocabulary,
  JSON field names observed on this CLI version).
- `<stamp>-baseline-defects.md` — per-flag defect counts, per-task mean/min/max of `added_lines`,
  `n`, model id, `claude --version`, written by `run.py --classify`.
- `<stamp>-export.json` — the stripped aggregate (`--report --export`): no session id, no result
  text, no uuids, no absolute home paths.

Present since part B of issue #145 ran on 2026-09-05 (read [`../results.md`](../results.md) first):

| file | what |
|---|---|
| `20260905-211029-probe.json` | isolation probe, Haiku, 3 calls, PASS, $0.0457 |
| `20260905-211512-baseline-defects.md` | the baseline (`opus[1m]`, n=3, 27 cells) as `--classify` wrote it after the flag sanity, plus the hand-read sections: flag sanity before/after, defect classification with the offending diff lines, over-build read from the diffs |
| `20260905-211512-export.json` | the stripped aggregate of the same stamp (27 `cells_detail`, 9 `summary` rows) |

The Haiku pilot (`20260905-211056`) is not exported: harness shake-out, never a number.
Workspaces (`runs/<stamp>/<task>__<arm>__<run>/`) stay in the scratch directory and are never committed.
