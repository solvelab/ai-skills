# Design — an acceptance is silence, not a zero

## Context

Two rigours in one file: the baseline block reads the output, the six accepting blocks read only the
exit code. The fragment work of issue #232 closed the rejecting half of the same gap.

## Goals / Non-Goals

**Goals:**

- One rigour for acceptance in this suite, and it is the stricter one that already exists in it.
- A failing acceptance names the check that fired.

**Non-Goals:**

- Touching `scripts/validate-agents.py`; nothing in it is wrong.
- New cases. This is rigour on what exists, not coverage.
- Re-running the mutation measurement: no mutant depends on this, and measuring for the sake of
  measuring is the waste the skill names beside the technique.

## Decisions

**D1 — Adopt the rigour already in the file.** The baseline block's condition
(`code != 0 or "findings: 0" not in out`) is the shape; a third form invented here would be the
duplication `lean-code` refuses.

**D2 — The helper takes the label and returns a verdict; the blocks keep their own labels.** The
difference between the six blocks is what they plant, not how they judge, so only the judging moves.

**D3 — Name the check on failure by reading it out of the output.** The findings are printed as
`[A3 description] …`, so the first bracketed token is the check. When none is present the message
says so — an acceptance that failed with no check id is a different defect and should not look like
the common one.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Reuse the shape already present instead of inventing a second | `lean-code` | link — D1 applies it |
| What the self-test that gates the agent validator must prove | `agents-catalog` (spec) | already canonical — this change modifies it |
| Assert what was observed, not what was expected | `verify-before-claiming` | link — the failure message reports the finding produced |

## Risks / Trade-offs

- **The stricter rigour could fail a block that passes today.** That is the outcome worth having: it
  would mean a finding nobody was reading, and it goes in the pull request.
- **A helper can hide which block failed.** Each call keeps its own label, and the label is printed.

## Open questions

- None.
