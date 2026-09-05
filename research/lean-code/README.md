# research/lean-code

Backing evidence for issue #145: a harness that measures what the `lean-code` doctrine (adopted
from DietrichGebert/ponytail, MIT) does to the code a real headless Claude Code session leaves
behind — on the maintainer's own model and CLI version, with arms proven isolated from the
maintainer's hooks and plugins, and with the verdict written before the number.

This directory sits **outside `skills/`** on purpose. `generate.sh` publishes only `skills/`, so
everything here is versioned and reviewable without being shipped to any project that enables a
plugin. The skill itself is item 2 (`add-lean-code-doctrine`); it will cite the counts produced
here, not the upstream's.

## Read in this order

| File | What it is |
|---|---|
| [`protocol.md`](protocol.md) | **The point of all of this.** Arms, cell, metrics, flags, the nine tasks, the sequence, and the SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE thresholds — frozen before any paid cell ran. |
| [`run.py`](run.py) | The harness. `--selftest` proves every instrument offline; `--prepare-arms`, `--probe-isolation`, `--matrix`, `--classify`, `--rescore`, `--report --export`. Its docstring carries the KNOWN LIMIT list. |
| [`tasks/`](tasks/) | The three catalog tasks (`fastapi-create-item`, `fivem-shop-buy`, `react-use-orders`): seed, good/bad reference, executing `score()` — the React one is structural and says so. |
| [`vendor/ponytail/`](vendor/ponytail/PIN) | The six upstream tasks (`tasks.py`), the LOC oracle (`loc.js`), the licence and the pin (commit, date, sha256). |
| [`fixtures/examples/`](fixtures/examples/README.md) | Eleven upstream before/after transcripts, used only to prove the LOC counter against `loc.js`. |
| [`scorer-venv.txt`](scorer-venv.txt) | The pinned `fastapi`/`httpx`/`pydantic`/`starlette` the FastAPI scorer ran under. The venv is never committed. |
| [`results/`](results/README.md) | Where the probe record, the baseline defect counts and the stripped export land (part B). |

## Running things

```bash
# 1. prove the instruments (offline; node for the loc.js oracle, lua 5.5, the scorer venv)
python3 -m venv /tmp/lean-venv && /tmp/lean-venv/bin/pip install -r research/lean-code/scorer-venv.txt
python3 research/lean-code/run.py --selftest --scorer-venv /tmp/lean-venv

# 2. arms, outside the repository, frozen at a sha
python3 research/lean-code/run.py --prepare-arms --arms-root /tmp/lean-arms --rules-ref <sha>

# 3. PAID, small: prove the arms are isolated (3 calls per arm on Haiku, $0.05 each)
python3 research/lean-code/run.py --probe-isolation --arms-root /tmp/lean-arms --model claude-haiku-4-5-20251001

# 4. PAID: the matrix (refuses without a green selftest in the same invocation and a passed probe)
python3 research/lean-code/run.py --selftest --matrix --arms baseline --tasks all --model <id> --runs 3 \
    --arms-root /tmp/lean-arms --runs-root /tmp/lean-runs --budget-usd 25 --scorer-venv /tmp/lean-venv

# 5. offline again
python3 research/lean-code/run.py --classify /tmp/lean-runs/<stamp>
python3 research/lean-code/run.py --report /tmp/lean-runs/<stamp> --export research/lean-code/results/<stamp>-export.json
```

Every cell command is written to `<cell>/_command.txt` before it runs; every cell's
`total_cost_usd` is summed and the run stops at `--budget-usd`.

## What the selftest proved on 2026-09-05

`python3 research/lean-code/run.py --selftest` → `selftest: 101/101 OK` in 0.7 s: LOC port equal
to `loc.js` on 22/22 sections; `Without > With` on 8/8 of the line-count examples and the three
dependency-removal examples (`infinite-scroll`, `number-formatting`, `url-params`) pinned as such —
the plan had assumed 11/11 and the upstream's own counter says otherwise on those three; scorers
18/18 (good passes, bad caught on its axis); detectors 20/20; arm preflight 15/15; export stripper
3/3; tree-kill 1/1; refusals 5/5; metrics 4/4.

## Status

Harness only (part A of #145). **No paid cell has run.** The isolation probe, the Haiku pilot and
the baseline on the maintainer's daily model are part B; until they run, `results/` holds only its
README and nothing here is a measurement of any model. Built against Claude Code `2.1.261`, Lua
`5.5.0`, node `v26.0.0`, Python 3.14 (harness) / 3.12 (scorer venv), on one machine.
