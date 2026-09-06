## Context

`scripts/validate-skills.py` C5 (read 2026-09-06, HEAD c8f55f9) normalises the block and searches
`PROBED_ON = re.compile(r"\b[Pp]robed on 20\d\d-\d\d-\d\d\b")`. The module imports `json`, `re`,
`shutil`, `subprocess`, `sys`, `tempfile` and `pathlib.Path` — no `datetime`, and no git access of
any kind. The selftest already carries two mutations on `observability` and five C5 entries in
total, so a third and fourth on the same file follow an established shape.

Measured on the 32 blocks: `svg-animation` writes "Probed on 2026-08-30 and 2026-08-31" — one
literal, two dates, of which the capture takes the first; `fivem-lua` and `assettoserver-csp-lua`
carry cited commit dates (`2026-09-02`, `2026-08-17`) that must stay outside the rule.

## Goals / Non-Goals

**Goals:**
- A probe date that cannot be true is reported, naming which rule it broke.
- The rule reads only what follows the literal, so cited dates stay untouched.
- The remaining KNOWN LIMIT is written down rather than implied.

**Non-Goals:**
- Age reporting or expiry; git access inside the validator; validating cited dates.

## Decisions

1. **Three findings, not one.** Each rule names itself in the message. A single "implausible date"
   finding would make the author guess which of three things is wrong.
2. **`REPO_INCEPTION` as a constant with its command in the comment.** Alternatives: run
   `git log --reverse` at check time (the validator shells out for `bash -n`/`luac -p` already, but
   a shallow CI clone — `fetch-depth: 0` today, not guaranteed forever — would return nothing and
   the gate would silently lose P3); or drop P3 entirely (then `2020-01-01` passes and the typo
   class that P3 exists for survives). The constant is the honest trade: it is wrong only if the
   history is rewritten, and the comment says how to re-measure it.
3. **UTC and `<=` for P2.** The CI runner is UTC and the maintainer is UTC-3: a probe run late in
   the evening locally is already "tomorrow" in UTC. Comparing in UTC with `<=` means a date written
   for today never fails, and only a genuinely future date does.
4. **Capture per literal occurrence.** `PROBE_DATE.findall(block)` returns one date per
   `Probed on` — `svg-animation`'s second date (`2026-08-31`) is prose, not a second claim of a
   probe date, and demanding a literal for it would edit a correct block for the regex's sake.
5. **No backfill.** The dry run found zero implausible dates, so the change is gate-only. A change
   that edits nothing in `skills/` is the honest outcome, not a sign the rule is useless — it is a
   trap set for the next typo.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| What a `Verified against` block owes (literal, date, plausibility) | `skills-authoring` spec + C5 docstring | already canonical — skills carry the sentence, not the rule |
| A claim is dated and its date is checkable | `verify-before-claiming` | already canonical — nothing restated |

## Risks / Trade-offs

- [A plausible date for a probe nobody ran still passes] → unchanged and stated in the docstring;
  presence and possibility are machine-checkable, honesty is the review's job.
- [`REPO_INCEPTION` drifts if the history is rewritten] → the comment carries the command that
  re-measures it in one line.
- [Timezone edge] → UTC plus `<=`, documented in the docstring and exercised by no mutation (a
  "today" date is what every current block carries).

## Open Questions

None.
