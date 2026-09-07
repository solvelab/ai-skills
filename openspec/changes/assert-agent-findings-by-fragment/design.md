# Design — asserting the message, not only the check

## Context

The agents self-test declares `(label, check, plant)` and asserts `f"[{check}" in out`. The skills
self-test declares `(relpath, mutate, (expect, fragment))` and asserts the fragment too, reading the
optional third element with `entry[2] if len(entry) > 2`. Two suites, one idea, one of them missing.

## Goals / Non-Goals

**Goals:**

- A case can require the exact message, without rewriting the 54 that do not need it.
- The two frontmatter paths become distinguishable, and the offset mutants that hide behind them die.
- The re-measurement is published as it comes out.

**Non-Goals:**

- Touching `scripts/validate-agents.py`. Nothing about its behaviour is wrong here.
- Chasing the 16 survivors that are `|` inside type annotations. They have no runtime effect, and
  hunting equivalent mutants is the anti-pattern the `bug-hunter` skill names in the same breath as
  the technique.
- A second format. The skills suite's shape is adopted as-is.

## Decisions

**D1 — Optional fourth element, not a new tuple everywhere.** `len(entry) > 3` reads the fragment,
absent means "assert the check id only". Rewriting 54 working cases to carry an empty string would
be churn with no defect behind it.

**D2 — The fragment is asserted in addition to the check id, never instead of it.** A defect caught
by the right message under the wrong check is still a defect, and that is the property the suite has
had since #205.

**D3 — Two frontmatter documents, because one does not separate the offsets.** The degenerate
`---` immediately followed by `---` distinguishes the offset `4` from the offset `3`: at 4 the closing
delimiter is not found and the finding is "no YAML frontmatter", at 3 it is found and the frontmatter
is empty, so the finding is "not a mapping". It does **not** separate 4 from 5, because from either
offset the match is missed on that input. A document whose frontmatter opens with an empty line does:
at 4 the closing delimiter is found immediately, at 5 it is missed.

**D4 — What the measurement says is what gets written.** Some of these mutants may be genuinely
equivalent — `text[3:end]` prepends a newline to a YAML document, which parses identically, and there
is no input that separates it. Where that is the finding, it is stated as the finding, not converted
into a contrived case whose only purpose is to move a number.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Reading survivors by class, and not chasing equivalent mutants | `bug-hunter` | already canonical — this change applies its scoring layer |
| Reuse the shape that exists instead of inventing a second one | `lean-code` | link — D1 and the "no second format" non-goal apply it |
| Publish the measurement as measured, including when it disagrees | `verify-before-claiming` | link — D4 applies it |
| What the self-test that gates the agent validator must prove | `agents-catalog` (spec) | already canonical — this change modifies it |

## Risks / Trade-offs

- **A fragment makes a case brittle against message rewording.** Accepted, and it is the point: a
  message a case depends on is a contract, and changing it should require looking at the case.
- **The four mutants may not all die.** Then the ones that survive are named with the reason, which
  is the same treatment #229 gave them.

## Open questions

- None. What is unknown here is a measurement, and the change runs it.
