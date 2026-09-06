# Change: Validate the `Probed on` date, not only its shape

## Why

Since #157 the C5 check requires the literal `Probed on YYYY-MM-DD` inside the normalised
`Verified against` block. It matches a **shape**, never a value: `Probed on 2026-13-45` (no such
month), `Probed on 2099-01-01` (the future) and `Probed on 2020-01-01` (six years before the
repository existed) all pass today. The check's own docstring says so — "a date is checked for
shape only, never for plausibility (a future or unrelated date passes)" — and #153 and #157 both
recorded it as the follow-up they were deliberately not doing.

A typo in the probe date is indistinguishable from a correct one, which defeats the reason the date
is there: telling the reader how old the pin is.

Measured on 2026-09-06 across the 32 blocks: three distinct probe dates (`2026-08-06`, `2026-08-30`,
`2026-09-05`), each a real calendar date, none in the future, none before the repository's first
commit `1e95262` of 2026-03-13 (`git log --reverse --format='%cs %h' | head -1`). Dry-running the
three rules over the catalogue reports **no** implausible date, so no skill needs editing — this
change adds the gate, not a backfill.

## What Changes

- **C5 validates each captured probe date** — every `[Pp]robed on (20\d\d-\d\d-\d\d)` in the
  normalised block — against three rules, each with its own finding:
  - **P1 calendar**: `date.fromisoformat` parses it, else `Probed on 2026-13-45 is not a calendar date`.
  - **P2 not future**: `<= datetime.now(timezone.utc).date()`, else `… is in the future`.
  - **P3 not before the repository**: `>= REPO_INCEPTION`, else `… predates the repository (first commit 2026-03-13)`.
  `REPO_INCEPTION = date(2026, 3, 13)` is a constant carrying the command that measured it: the
  validator imports no git, and a shallow clone would not have the history to derive it.
  Dates in the block that do **not** follow `Probed on` (commits and releases the block cites) are
  untouched.
- **Selftest**: three mutations on `observability`, one per rule.
- **Docstring**: the plausibility half of the KNOWN LIMIT is removed; what remains is stated (a
  plausible date for a probe nobody ran still passes).
- **README**: the C5 sentence says the date is plausible; the selftest count moves 24 → 27.
- **No skill changes**: all 32 probe dates already satisfy the three rules.

## Deliberately not done

- An age report or expiry policy for pins (how many days since the probe) — a different decision,
  out of scope by the item.
- Validating the block's other dates (cited commits and releases).
- Deriving the inception date from git at runtime.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: MODIFIED **Versioned external APIs are pinned** — the probe date is a real
  calendar date, not in the future and not before the repository existed; an impossible date is a
  defect the validator reports.

## Impact

- `scripts/validate-skills.py`, `scripts/selftest-validate-skills.py`, `README.md`.
- No `skills/` file changes; no wrapper changes; catalog composition untouched.
