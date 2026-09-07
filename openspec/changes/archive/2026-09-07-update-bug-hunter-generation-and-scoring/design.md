# Design — generation and scoring in the adversarial rite

## Context

The rite has one gear: a human or an agent enumerates scenarios. `skills/bug-hunter/SKILL.md` (2.4.0)
carries eleven defect classes and three stack tracks; `agents/bug-hunter-analyst.md` returns
`ATTACKS` / `TESTS TO WRITE` / `TRIED AND FOUND NOTHING`. Both are by-example.

Two techniques from outside the catalog answer the two questions enumeration cannot: **property-based
testing** generates inputs from a stated invariant instead of a list, and **mutation testing** scores
an existing suite by breaking the code and asking whether the suite noticed. Neither was measured
here before this change, so neither could be prescribed — `skills-authoring` forbids a quantified
claim without its measurement, and forbids a checklist item without the defect that earned it.

## Goals / Non-Goals

**Goals:**

- Separate three activities the rite conflates today: enumerate, generate, score.
- Give each added technique a condition under which it pays and a `lean:` ceiling, so the rite stays
  proportional to the change in hand.
- Publish only numbers measured on this repository, including the ones that came out unfavourable.

**Non-Goals:**

- Making mutation testing a CI gate of this repository. This change ships doctrine, not pipeline.
- New stack tracks. The three that exist are enough to demonstrate the shape.
- Moving REST fuzzing doctrine out of `api-resilience-testing`. The rite links it; it does not
  absorb it.
- Removing the write-tool boundary of `bug-hunter-analyst`. The agent still returns what to write.

## Decisions

**D1 — Three layers, not a longer checklist.** Adding property-based testing as a twelfth bullet of
the universal checklist would read as a twelfth thing to enumerate, which is the opposite of what it
is. The section is structural: enumerate is the default and always applies; generate and score are
conditional and each states its condition.

**D2 — The condition for generating is a stateable invariant, not a code category.** Measured here:
four invariants over the catalog's own tokenizer
(`skills/code-locale/references/check-identifier-locale.py`) at 3000 generated cases each — 12000
inputs — found **zero** defects. A fifth invariant, positional blanking, failed on the three-character
input `"'"`, and the failure was a **wrong assumption about the contract**, not a bug: the function
collapses a string literal to a single space rather than blanking it in place, and no caller depends
on column positions (`scan_text` reports line numbers only). The yield on hardened code is therefore
not defects — it is being forced to state the invariant precisely enough to test it. The doctrine
says that, rather than promising bugs.

**D3 — Scoring is diff-scoped, and the wrong command is named.** A mutation run over a repository is
a different, much more expensive activity than scoring one change; the rite's unit is one implemented
change, so the prescribed scope is the module that change touched. The plausible-but-wrong command is
named in the track because it is what a reader reaches for first: the ecosystem's best-known tool
defaults to a `pytest` runner and to guessing the source paths, and in a repository that runs neither
it fails before mutating anything.

**D4 — Only the Python track gets a command.** Nothing was measured for Lua or .NET during this
change, and a track that names an unprobed tool would be the exact defect this change is written
against.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Adversarial methodology, defect classes, the rite's exit criteria | `bug-hunter` | already canonical |
| How much test a change owes at minimum (the one-check floor) | `lean-code` | link — the new section names the floor and points there |
| Whether the test is written before the code | `tdd` | link — unchanged, already cross-linked |
| REST negative, fuzz and contract suites, Schemathesis/Hypothesis for schemas | `api-resilience-testing` | link — the generate layer points there for API surfaces instead of restating |
| Measuring a claim before publishing it; reporting what could not be measured | `verify-before-claiming` | link — already cross-linked |
| Whether the analysis is dispatched to a subagent, and what that subagent may hold | `agent-delegation` | link — already cross-linked |

## Risks / Trade-offs

- **The rite gets heavier.** Mitigated by making enumerate the default and giving each conditional
  technique an explicit `lean:` ceiling with its upgrade trigger.
- **The measured yield of property-based testing here was zero defects.** Publishing that honestly
  makes the technique look weaker than the literature claims. It is the correct trade: a technique
  sold on someone else's number is the failure mode `skills-authoring` was written to stop, and the
  contract-clarification yield is real and reproducible.
- **The mutation number is one module of one repository.** Stated with its conditions — the module,
  the suite, the tool, the operator set — so a reader can refute it rather than inherit it.

## Open questions

- Whether metamorphic testing and fault injection earn a place was not settled: neither was measured
  during this change, so neither is prescribed. Recorded as a follow-up, not as doctrine.
