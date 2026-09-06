# Change: Require the literal `Probed on <date>` in every `Verified against` block, matched on the normalised block

## Why

Since #153, C5 requires an ISO date inside the `Verified against` block — any ISO date. The block of
`fivem-lua` dates the citizenfx commits it names (`(2026-09-02)`, `(2026-08-17)`) and would pass
with its own probe date removed; the selftest mutation had to move to `observability` for that
reason (recorded in `2026-09-06-add-pin-date-gate/tasks.md`, S.3). The date the gate proves present
is therefore not necessarily the date of the probe.

Measured on 2026-09-06 over the 32 blocks, normalised (leading `> ` stripped, lines joined by a
space): 30 carry `Probed on YYYY-MM-DD` or `probed on YYYY-MM-DD`; 2 do not —
`api-resilience-testing` ("re-measured on 2026-09-05") and `svg-animation` ("driven … on 2026-08-30
and 2026-08-31 … Not re-run on 2026-09-05"). Matched on the raw text instead, two correct blocks
would fail: the 97-column wrap leaves `Probed on` at the end of one line and the date at the start
of the next in `assettoserver-csp-lua/SKILL.md:26-27` and `react-api-client/SKILL.md:18-19`.

## What Changes

- **C5 normalises the block** — `" ".join(re.sub(r"^> ?", "", l) for l in block.splitlines())` —
  before both date rules, and adds a second rule: a block with a date but no
  `[Pp]robed on YYYY-MM-DD` is reported as naming no probe date. The "carries no date" finding stays
  for blocks with no date at all. Docstring names the normalisation and why (the wrap).
- **Selftest**: mutation `C5 no version pin (date but no Probed on)` on `observability`
  (`Probed on 2026-08-06` → `Dated 2026-08-06`); the `undated block` mutation stays.
- **Two blocks reworded**, patch bump each: `api-resilience-testing` ("Probed on 2026-09-05,
  re-measuring the nine rows …") and `svg-animation` ("Probed on 2026-08-30 and 2026-08-31 …
  Not re-run on 2026-09-05"). `verify-before-claiming` already matches (`probed on 2026-08-06`).
- **README**: C5 sentence names the `Probed on <date>` line; selftest count 23 → 24.

## Deliberately not done

- Date plausibility; a date on the declaration form; rewording the 30 blocks that already match.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: MODIFIED **Versioned external APIs are pinned** — the probe date is named
  with the literal `Probed on YYYY-MM-DD`; other dates in the block do not stand in for it.

## Impact

- `scripts/validate-skills.py`, `scripts/selftest-validate-skills.py`, `README.md`,
  `skills/api-resilience-testing/SKILL.md`, `skills/svg-animation/SKILL.md`, regenerated wrappers.
- No skill added, removed or repurposed; no description changes.
