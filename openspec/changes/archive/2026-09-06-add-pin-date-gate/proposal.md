# Change: Require the date inside every `Verified against` block, and date the 14 blocks that predate #131

## Why

`skills-authoring` (*Versioned external APIs are pinned*) already says a `Verified against` block
names "each tool and the version it was probed against, what was run, and the date". The gate that
reads the block does not ask for the date: C5 in `scripts/validate-skills.py` checks the literal
phrase only, and its docstring lists "the date the block owes is not checked" as a KNOWN LIMIT —
deliberately left out of #131 to keep that item's scope.

Measured on 2026-09-05: 14 of 35 skills carry a block with no ISO date — the ten `r3f-*`,
`observability`, `k8s-tune-resources`, `fivem-nui-react` and `python-rest-api` (a single prose line,
`SKILL.md:183`). All 14 blocks entered the tree on 2026-08-06: `a18758c` (#26, `harden-r3f-skills`),
`9afef67` (#39, `pin-probed-skills`), `d1e22a4` (#33, `onboard-k8s-tune-resources`), `60eb0be`
(#53, `add-observability-skill`), `c27ca79` (#51, `add-async-lane-rule`). A pin without a date does
not say when it stopped being trustworthy; a gate that declares it does not check the date is a
gap the reader has to remember.

## What Changes

- **C5 requires an ISO date inside the block.** The block is the text from the line carrying
  `Verified against` to the next blank line — the blockquote form and the one-line prose form both
  fit; `\b20\d\d-\d\d-\d\d\b` must occur in it. The `does not depend on a tool version` declaration
  owes no date. The docstring drops the date KNOWN LIMIT and keeps the others.
- **Selftest**: a new mutation strips the date from a dated block and asserts the `no date` finding.
- **14 skills** gain one sentence at the end of the block: `Probed on 2026-08-06 (change
  <id>, commit <sha>)` — the date the history proves, said as a record, never as a new probe. No
  pinned version changes. `python-rest-api`'s prose line gets the same sentence.
- **README**: the validator paragraph names the date requirement; the selftest count moves 22 → 23.
- **Skill versions**: waived on the pull request with `Skill-version: none — 14 blocks gain the
  date the history already records; no rule, example or pinned version changes` — the sweep case
  `validate-skill-version.py` wrote the waiver line for.

## Deliberately not done

- Re-probing the 14 skills against newer versions. The date is the recorded probe's, not today's.
- A date on the declaration form, or any plausibility check on the date (future, too old).

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: MODIFIED **Versioned external APIs are pinned** — a `Verified against` block
  without an ISO date is reported by the validator; the date may be the recorded probe's when it is
  named as such.

## Impact

- `scripts/validate-skills.py`, `scripts/selftest-validate-skills.py`, `README.md`,
  `skills/{r3f-animation,r3f-assets,r3f-fundamentals,r3f-geometry,r3f-interaction,r3f-lighting,
  r3f-materials,r3f-physics,r3f-postprocessing,r3f-shaders,observability,k8s-tune-resources,
  fivem-nui-react,python-rest-api}/SKILL.md`, regenerated wrappers.
- No skill added, removed or repurposed; no description changes.
