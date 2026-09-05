# results/

Aggregated, anonymised outputs of paid runs land here, written by `run.py --export`:

- `<stamp>-probe.json` — the isolation probe (sentinel, hook side-effects, event vocabulary,
  JSON field names observed on this CLI version).
- `<stamp>-baseline-defects.md` — per-flag defect counts, per-task mean/min/max of `added_lines`,
  `n`, model id, `claude --version`, written by `run.py --classify`.
- `<stamp>-export.json` — the stripped aggregate (`--report --export`): no session id, no result
  text, no uuids, no absolute home paths.

Empty until part B of issue #145 runs. Workspaces (`runs/<stamp>/<task>__<arm>__<run>/`) stay in
the scratch directory and are never committed.
