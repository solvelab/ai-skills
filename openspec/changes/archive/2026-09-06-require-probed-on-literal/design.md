## Context

`scripts/validate-skills.py:280-286` (read 2026-09-06, HEAD f1e4b02) isolates the block as raw text
and searches `ISO_DATE` in it. Raw text keeps the `> ` prefixes and the line breaks the 97-column
wrap introduced, so a phrase can straddle two lines. Measured: `assettoserver-csp-lua` and
`react-api-client` carry `Probed on` at a line end and the date on the next line; `k8s-tune-resources`
carries a second `>` paragraph after a bare `>` line, which normalises to an extra space.

## Goals / Non-Goals

**Goals:**
- The date C5 proves is the probe's, named as such.
- A correct block never fails because of where the wrap broke a line.

**Non-Goals:**
- Plausibility of the date; rewording blocks that already carry the literal.

## Decisions

1. **Normalise, then match.** Strip `^> ?` per line, join with a single space, run both date rules
   on the result. Alternative — forbid the wrap from splitting the phrase — rejected: it moves a
   gate's problem into every author's editor.
2. **Two findings, not one.** "carries no date" (no ISO date at all) stays with its fragment, which
   the existing `undated block` mutation asserts; "names no `Probed on <date>`" is added for a block
   that has dates but not the literal. A reader of the finding knows which sentence to write.
3. **Case-insensitive `[Pp]robed on`.** `verify-before-claiming` says "was probed on 2026-08-06";
   the phrase is the same fact in running prose, and demanding the capital would edit a correct block
   for the regex's sake.
4. **Reword only the two blocks that lack the literal**, keeping their facts: `api-resilience-testing`
   keeps "re-measuring", `svg-animation` keeps "Not re-run on 2026-09-05".
5. **Patch bumps** on the two reworded skills: a block sentence changed, nothing else.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| The probe date is named with `Probed on <date>` | `skills-authoring` spec + C5 docstring | already canonical — blocks carry the sentence, not the rule |
| Dated claims | `verify-before-claiming` | already canonical — nothing restated |

## Risks / Trade-offs

- [A block writes `Probed on <date>` for a run nobody made] → unchanged from every other C5 rule:
  presence, not honesty; the review judges.
- [Normalisation joins two paragraphs of a block] → harmless: the literal is searched anywhere in the
  joined text; `k8s-tune-resources` is the measured case.

## Open Questions

None.
