# research/tdd

Backing evidence for issue #182: a harness that measures whether an always-on **test-order**
doctrine changes the order in which a real headless Claude Code session writes files, and whether
the code it leaves behind gets better or worse for it — on the maintainer's own model and CLI
version, with arms proven isolated by probe, and with the verdict written before the number.

This directory sits **outside `skills/`** on purpose. `generate.sh` publishes only `skills/`
(`generate.sh:224-234`), so everything here is versioned and reviewable without being shipped to
any project that enables a plugin. The skill itself is item #183 (`add-tdd-skill`); it will cite the
counts produced here, not folklore.

## Read in this order

| File | What it is |
|---|---|
| [`protocol.md`](protocol.md) | **The point of all of this.** Arms, cell, metrics, the six tasks, the sequence, and the SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE thresholds — frozen before any paid cell ran. |
| [`run.py`](run.py) | The harness. `--selftest` proves every instrument offline with an injected defect; `--prepare-arms`, `--probe-isolation`, `--matrix`, `--report --export`. Its docstring carries the KNOWN LIMIT list. |
| [`PIN`](PIN) | What this harness **imports** from `research/lean-code/run.py` instead of copying, and the exact blob it was read at. The contract is enforced by the `contract` group of `--selftest`, which gates `--matrix`. |
| [`arms-block.md`](arms-block.md) | The always-on doctrine block that defines the `block` arm. The baseline never sees it. |
| [`tasks/`](tasks/) | Six Python/pytest tasks: `seed/`, `good/`, `bad/` and a `hidden/` suite the cell never sees. No prompt mentions tests — the selftest asserts that. |
| [`scorer-venv.txt`](scorer-venv.txt) | The pinned pytest the hidden suites run under. The venv is never committed. |
| [`results.md`](results.md) | **What has been measured.** Per task and arm, with the verdict read by the letter of the protocol. |
| [`results/`](results/) | The files behind it: probe records and stripped exports of every reported stamp. |

## Running things

```bash
# 1. the pinned scorer venv (pytest is not in the system interpreter)
python3 -m venv /tmp/tdd-venv && /tmp/tdd-venv/bin/pip install -r research/tdd/scorer-venv.txt

# 2. prove the instruments, offline
python3 research/tdd/run.py --selftest --scorer-venv /tmp/tdd-venv

# 3. arms, outside the repository (baseline + block; the skill arm needs skills/tdd, which is #183)
python3 research/tdd/run.py --prepare-arms --arms-root /tmp/tdd-arms --rules-ref <sha> \
    --claude-block research/tdd/arms-block.md

# 4. PAID, small: prove the arms are isolated
python3 research/tdd/run.py --probe-isolation --arms-root /tmp/tdd-arms \
    --model claude-haiku-4-5-20251001

# 5. PAID: pilot first (does stream-json expose the write order at all?), then the matrix
python3 research/tdd/run.py --selftest --matrix --arms baseline,block --tasks parse-duration \
    --runs 1 --model claude-haiku-4-5-20251001 --arms-root /tmp/tdd-arms --runs-root /tmp/tdd-runs \
    --budget-usd 2 --scorer-venv /tmp/tdd-venv
python3 research/tdd/run.py --selftest --matrix --arms baseline,block --tasks all --runs 3 \
    --model <daily> --arms-root /tmp/tdd-arms --runs-root /tmp/tdd-runs --budget-usd 20 \
    --scorer-venv /tmp/tdd-venv

# 6. offline: the report and the stripped export
python3 research/tdd/run.py --report /tmp/tdd-runs/<stamp> \
    --export research/tdd/results/<stamp>-export.json
```

`--matrix` refuses without a green `--selftest` in the same invocation, without a passed probe,
without a scorer venv, and when `claude --version` differs from the version the arms were prepared
under.

## What the selftest proved on 2026-09-06

`python3 research/tdd/run.py --selftest --scorer-venv <venv>` -> **70/70**, under
`claude 2.1.263`, Python `3.14.5`, pytest `9.1.1`:

```
  contract   8/8      every imported lean-code symbol exists and still behaves
  tasks     13/13     six tasks wired; no prompt mentions tests
  order      8/8      transcript order, both directions, harness dirs ignored, mtime fallback marked
  red        9/9      a real test on the seed is red; a vacuous test is not; no test file is not
  scorers   18/18     six tasks x seed/good/bad, every reference scored as declared
  refusals   8/8      matrix gate, report conditions, arms-root inside the repo, probe_gate
  export     2/2      session id, result text and uuids stripped; numbers survive
  aggregate  4/4      rates, fallback counting, test-line factor, no-baseline case
```

Two defects the instruments caught in this repository's own artifacts before any cell ran: the
`slug-truncate` **good** reference returned a truncated word instead of the empty string for a
single word longer than `max_len`; and `research/lean-code/run.py` cannot be executed by
`importlib` unless it is registered in `sys.modules` first, because it decorates a class with
`@dataclass`.

## Status

**No paid cell has run.** The instruments are green offline; the probe, the pilot and the matrix
are the next steps in `protocol.md`, and `results.md` says what has and has not been measured.
