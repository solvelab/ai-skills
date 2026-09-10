# results/

The files behind `../results.md`. Every export went through `strip_export` of
`research/lean-code/run.py`: no session identifiers, no uuids, no response text, home paths
rewritten to `~`. The raw cells (stdout of every call, the exact command, stderr) stay in the
scratch runs root outside the repository and are not committed.

| file | what it is |
|---|---|
| `<stamp>-probe.json` | the isolation probe: per mode and condition, the hook events each of the three calls recorded, whether `SessionStart` fired, whether the caveman flag file appeared, cost |
| `<stamp>-export.json` | `run.py --report --export` over one run per mode: per-condition means on the five judged dimensions, weighted score, blockers, the two counters, per-case weighted means, the verdict per mode and combined, the upstream's own release gate for comparability, spend |
