## Context

`skills-authoring` grew four requirements across three audits, each earned by a measured defect. All
four were convention: a reviewer could apply them, CI could not. The spec itself already forbids that
posture — *"Advisory mechanisms are not sold as hard gates"* — so the gap was self-evident once the
requirements existed.

Roughly half of each requirement is mechanically checkable (does this path exist, does this block
parse, does this description contradict the body) and half is not (is the simulation meaningful, is
the rule right). This change automates the first half and leaves the second to review, saying so
explicitly rather than implying full coverage.

## Goals / Non-Goals

**Goals**
- Every mechanically checkable authoring rule fails a PR when violated.
- The validator's own correctness is demonstrated, not asserted.
- The catalog is at zero findings when the gate lands.

**Non-Goals**
- No judgement calls automated. C4 and C5 are heuristics; they flag a *shape* for a human to confirm,
  and both were deliberately narrowed after producing false positives on correct skills.
- No new doctrine in any skill. Content changes here are corrections the validator found, nothing else.
- No attempt to check prose quality, teaching value or triggering accuracy.

## Decisions

**D1 — Fix the instrument before trusting it.** The first run produced 31 findings; 22 were the
validator's bugs. Reporting those as catalog defects would have produced 22 pointless edits and
damaged trust in every future run. Each false positive was traced to a specific parsing assumption and
fixed in the validator, not worked around in the skills.

**D2 — The gate is itself gated.** `selftest-validate-skills.py` copies the catalog, injects one known
defect per check, and asserts the validator fires — currently 10/10. Without it, a regression that
silently disables a check would look identical to a clean catalog. This is the same discipline the
`bug-hunter` rite applies to code.

**D3 — Degrade loudly, not silently.** When `luac` or PyYAML is absent the corresponding check is
skipped and the skip is printed. CI installs both, so the skip path is a local-development
convenience, never a silent pass.

**D4 — Cross-skill references name their owner.** `references/track-python-pytest.md` written inside
`python-rest-api` reads as a local file and is not one; it lives in `bug-hunter/references/`. Prefixing
with the owning skill is both correct and checkable, and it matches how the catalog already links
sibling skills by name.

**D5 — `jsonc` over splitting the payload variants.** The five negative-test blocks list several
annotated payloads to be read side by side; splitting them into single documents would lose the
comparison the section is teaching. The tag was the thing that was wrong.

**D6 — Heuristic checks state their own limits.** C4 fires only when an absolute promise carries no
condition in the description itself; C5 accepts a stated stack ("pydantic v2, SQLAlchemy 2") as a pin
and skips skills that explicitly defer to a local source of truth. Both narrowings came from false
positives on skills that were already correct.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Authoring conventions for skills (frontmatter, locale, canonical home, verified claims) | `openspec/specs/skills-authoring` | already canonical — gains the enforcement requirement |
| Rite gate structure (mandatory groups per change) | `scripts/validate-rite.sh` | already canonical — the new script sits beside it, same job, different subject |
| Adversarial testing of a change | `bug-hunter` | link (already canonical) — the self-test applies its discipline to the validator |
| Per-skill doctrine (backend, docs, r3f, fivem, …) | the skill itself | unchanged; only validator-found corrections applied |

## Risks / Trade-offs

- [A heuristic check false-positives on a future correct skill] → both heuristics were already
  narrowed by real false positives; when one fires wrongly the fix is to narrow it again, and the
  self-test guards against narrowing it into uselessness.
- [Contributors bypass the checks locally] → CI runs them on every PR; local runs are a convenience.
- [The self-test copies the whole repo ten times] → it runs in seconds and excludes `.git` and
  `node_modules`; correctness of the gate is worth the cost.
- [Half the authoring spec stays unenforced] → stated plainly here and in the proposal, rather than
  letting the green check imply full coverage.
