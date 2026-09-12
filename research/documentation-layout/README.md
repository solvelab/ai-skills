# research/documentation-layout

Backing evidence for issue #251: what a fleet of repositories documented under the `documentation`
skill actually looks like, whether each rule of the new layout detector finds real defects, and what
a real session leaves behind when it runs the changed skill through a real install path.

This directory sits **outside `skills/`** on purpose. `generate.sh` publishes only `skills/`, so
everything here is versioned and reviewable without being shipped to any project that enables a
plugin. The skill cites the counts produced here; it publishes no number this directory cannot
re-produce.

## Read in this order

| File | What it is |
|---|---|
| [`protocol.md`](protocol.md) | **The point of all of this.** The question, the thresholds and the verdict, all fixed before any number existed. |
| [`survey.py`](survey.py) | The harness. `--selftest` proves every counter; `--inventory` counts names; the full run aggregates the detector. |
| [`results.md`](results.md) | **What was measured.** The fleet inventory and the per-rule findings, each confirmed by hand. |
| [`simulation.md`](simulation.md) | What a real session left behind when it ran the changed skill, and what that cost. |

## Re-running it

```bash
python3 research/documentation-layout/survey.py --selftest
python3 research/documentation-layout/survey.py --root <workspace> --inventory --markdown
python3 research/documentation-layout/survey.py --root <workspace> --markdown
```

The workspace measured in `results.md` is a private directory of the maintainer's, so the numbers
are re-producible by whoever holds it and not by a stranger. What a stranger can re-run is the
self-test, which proves the counters, and the detector's own `--selftest`, which proves every rule
still fires. That asymmetry is a limit of the measurement, recorded rather than hidden.

## What this directory does not claim

- **Not a claim about documentation quality.** Everything here counts files, names, sections and
  header rows. Whether a document is well written is not measured, and no rule in the skill pretends
  it is.
- **Not a general result.** One maintainer, one fleet, one writing culture. A different fleet would
  produce different names for the same concepts; what generalizes is the shape of the problem —
  conditions decide whether a document is earned and say nothing about what it is called — not the
  specific counts.
- **Not a before/after comparison.** The fleet was documented under earlier versions of the skill,
  but the repositories were written over more than a year by sessions of several models, so
  attributing the layout to any one version of the skill would be an inference this data cannot
  support.
