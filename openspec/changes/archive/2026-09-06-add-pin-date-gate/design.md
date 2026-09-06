## Context

`scripts/validate-skills.py` C5 (read 2026-09-05, HEAD 85c453d) matches `Verified against` /
`does not depend on a tool version` and, for the declaration, applies the code-heavy rule. It reads
the whole `SKILL.md` and never isolates the block. The 14 undated blocks have two shapes: a
blockquote of 4–6 lines (13 skills; `k8s-tune-resources` continues with a second `>` paragraph
after a bare `>` line) and one prose line (`python-rest-api/SKILL.md:183`).

## Goals / Non-Goals

**Goals:**
- Every `Verified against` block states a date a reader can compare with today.
- The gate proves the date is present; the review keeps judging whether it is honest.
- The backfilled dates are the ones the history proves, and the sentence says so.

**Non-Goals:**
- Re-probing; date plausibility; dating the declaration form.

## Decisions

1. **Block = from the `Verified against` line to the next blank line.** Both shapes fit, and a bare
   `>` line is not blank, so `k8s-tune-resources`' second paragraph stays inside the block (harmless:
   the date sits in the first paragraph). Alternative — parse blockquotes only — rejected: it would
   miss the prose form and force a reformat of `python-rest-api` for no gain.
2. **ISO date regex only.** `\b20\d\d-\d\d-\d\d\b`. A stricter parse (real calendar date, not in the
   future) is out of scope by the item; the KNOWN LIMIT names it.
3. **One sentence, one shape.** `Probed on 2026-08-06 (change <id>, commit <sha>).` appended to the
   first paragraph of each block. The word "recorded" is not needed when the change id and commit
   are in the sentence: a reader can open both. `python-rest-api` gets the same sentence on its
   line.
4. **Waiver, not 14 bumps.** The skill-version gate's own header names this case ("the sweep that
   adds one cross-reference to twelve skills"); a date on a block changes no contract.
5. **Selftest target `fivem-lua`**: its block has exactly one date (`Probed on 2026-09-05`); the
   mutation replaces it with `Probed recently`, leaving the literal `Verified against` in place so
   only the new rule fires.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| A pin carries the date it was probed | `skills-authoring` spec + C5 docstring | already canonical — skills carry the sentence, not the rule |
| Dated claims and the research ladder | `verify-before-claiming` | already canonical — nothing restated |

## Risks / Trade-offs

- [A block that mentions an unrelated date passes] → accepted; the gate proves presence, the
  review judges meaning, as with the versions themselves (KNOWN LIMIT).
- [The backfilled date reads as "probed today"] → the sentence names the change and commit, both
  dated 2026-08-06 in the repository.

## Open Questions

None.
