# Results — what has been measured, and what the protocol says about it

**Nothing paid has run yet.** This file exists so that the claim "not yet measured" is written
down rather than implied by an absent file, and so the shape of the table is fixed before the
numbers arrive — the same discipline as the verdict in `protocol.md`.

## Method

Read `protocol.md` first: it fixes the arms, the cell, the four metrics and the four verdicts. In
one paragraph: two arms (`baseline`, `block`) differing only by an always-on doctrine block in the
cell's `CLAUDE.md`; six Python/pytest tasks with hidden suites the cell never sees; `order` read
from the session transcript, `red` and `green` measured outside the cell by the harness, and
`test_added_lines` taken from the diff. Bash is disallowed in every cell, so what is measured is
the order in which artifacts were written and the quality of what remained — not the feedback loop.

## Offline instruments — 2026-09-06

`python3 research/tdd/run.py --selftest --scorer-venv <venv>` -> **70/70**.
Conditions: `claude 2.1.263`, Python `3.14.5`, pytest `9.1.1`, base `fdfc655`.

Group counts and what each group proves are in `README.md`. Two defects the selftest caught in
this repository's own artifacts, both fixed before this file was written:

1. The `slug-truncate` **good** reference returned `"antid"` where the prompt requires `""` for a
   single word longer than `max_len`. Caught by the `scorers` group, which requires the good
   reference to pass the hidden suite whole.
2. `research/lean-code/run.py` raised `AttributeError: 'NoneType' object has no attribute
   '__dict__'` when executed through `importlib` without being registered in `sys.modules`, because
   `dataclasses` resolves `cls.__module__` through that table. Recorded in `PIN`.

## The two arms, per task

*Not yet measured.* The table will carry one row per task and arm:

| task | arm | n | order | red | green | testLOC mean (min–max) | $/cell |
|---|---|--:|--:|--:|--:|--:|--:|

`order` counts transcript-scored cells only; cells that fell back to mtime are reported in their
own column and are never folded into a published order figure.

## Verdict, by the letter of `protocol.md`

*Not yet read.* The four verdicts and their thresholds are fixed in `protocol.md` and will be
quoted here verbatim and checked condition by condition, as `research/lean-code/results.md` does.

## Spend

*Nothing spent.* No probe, no pilot, no matrix cell has run.

## What this does not cover

The list is `protocol.md`'s, not a new one: the red-green feedback loop (Bash disallowed), anything
outside Python and pytest, the published skill as opposed to the doctrine block, internal structure
as opposed to stated behaviour, and work longer than one prompt.
