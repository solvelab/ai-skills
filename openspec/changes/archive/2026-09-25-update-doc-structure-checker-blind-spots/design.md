## Context

The detector shipped in `add-information-architecture-rules` (archived 2026-09-06) with a self-test
of seven injected defects. `solvelab/ferdinand#583` then wrote its own guard for the same rules in
TypeScript, and that guard found three shapes the Python detector could not see. The rule texts in
`information-architecture.md` were right about two of them. The third, a document with only `###`,
is a gap in the rule itself.

## Goals / Non-Goals

**Goals:**

- The three shapes fail, each proven by an injected case in `--selftest`.
- The self-test runs in CI, like every other detector this repository ships.
- No new finding on a document that was correct: measured on ferdinand at `eea8b20`.

**Non-Goals:**

- R5 and R6 stay review-only. Their measurement is recorded and this change does not reopen it.
- The thresholds (100 lines, 120 characters, 25 rows) do not move.

## Decisions

### R1 reads the index block, not the whole document

The rule says "the index links every `##`". Counting a link anywhere made the check accept a
document whose index is incomplete as long as the body cites the missing section, and that is the
defect a reader hits: they open the index and the section is not there. The block runs from the
index heading to the next heading of any level, which is the same boundary ferdinand's guard uses.

### With no `##`, the index owes every `###`

A catalog written only in `###` is navigated through `###`. Returning early made the check silent on
the longest document of that shape in the sample repository. The alternative, requiring a `##`, would
reprove the heading tree itself. That is R6's subject, and R6 is review-only.

### `\|` is text

GitHub renders `\|` inside a table cell as a literal pipe. The split now ignores a pipe preceded by
a backslash. Pipes inside code spans without escape still split, as they do on GitHub.

### A field miss becomes a self-test case first

Each of the three shapes enters `SELFTEST_CASES` before the fix, so the self-test fails first and
then passes. The requirement added to `skills-authoring` makes this the rule for every detector the
catalog ships: a defect found in the field and missed by the detector is turned into an injected
case.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Document organization: index, cell length | `documentation` | already canonical — this change corrects its detector and states two limits in the rule text |
| A detector's self-test runs in CI; a field miss becomes an injected case | `skills-authoring` (spec) | already canonical — the existing requirement is extended to detectors shipped under `references/` |
| Break the artifact on purpose after it works | `bug-hunter` | link — the injected cases are the detector's own regression net, not a restatement of the rite |

## Risks / Trade-offs

- **Stricter R1 can fail documents that passed.** A document that orients readers through a list of
  links outside a heading called "Index" now fails. Mitigation: measure on ferdinand at `eea8b20`
  and on this skill's own references before closing. A finding there is either fixed or recorded.
- **The `###` fallback is a rule change, not only a fix.** It is written into R1's text so the check
  and the rule do not diverge again.

## Open Questions

None at writing time. The GitHub rendering of `\|` inside a cell is checked against GitHub's own
renderer during the change and recorded in `tasks.md` E.2.
