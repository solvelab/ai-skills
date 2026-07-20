# Acceptance tracking — tick what is proven, never what is hoped

Runs after validations, before the PR. Every checkbox in the item ends with an explicit verdict:
ticked with evidence, or left unticked and reported. Silence is not an option — an unticked box in
a closed issue is indistinguishable from forgotten work.

## Which checkboxes

Every checkbox list in the executed item's body that states a deliverable:

- Acceptance criteria — always.
- Rite checklists the repo's process adds to the body (test/bug-hunter groups, validation/closure
  sections, task mirrors of an OpenSpec `tasks.md`).

Headings may be in the repo's working language (`Critérios de aceite`, `Testes & Bug-Hunter`) —
match by position and meaning, never by an English literal.

Never touch checkboxes outside the executed item: a parent issue, a sibling sub-issue, or a linked
tracking issue is edited by whoever executes it.

## Verdicts

| Verdict | Action |
|---|---|
| Met — proven by a command, test, or artifact | tick, record evidence |
| Not met — out of what was implemented | leave unticked, list in the gate below |
| Unverifiable here — needs runtime, staging, human eyes, third party | leave unticked, report as `manual` with the exact steps to verify |

Evidence is a test name, a command output line, a migration result, a diff path. "Looks right",
"should work", or "code implements it" is not evidence — if nothing executed it, it is `manual`.

A `manual` criterion the user confirms in the session may be ticked; record who confirmed it and
when in the evidence row.

## Editing the body

There is no per-checkbox API. It is a read-modify-write of the whole body, so it must be surgical:

```bash
gh issue view <n> --repo ORG/REPO --json body --jq .body > acceptance-<n>.md
# flip only the proven lines
gh issue edit <n> --repo ORG/REPO --body-file acceptance-<n>.md
```

Rules:

1. **Re-fetch immediately before editing.** The body read back in the *Read fully* step is stale —
   a human may have amended scope since. Body changed → re-read it, re-map the criteria, and say so
   in the report.
2. **Only `- [ ]` → `- [x]`, on the exact matched lines.** No rewrapping, no reordering, no
   heading/spacing/markdown normalization, no trailing-newline changes.
3. **Diff before writing.** `diff` the fetched body against the edited file; every hunk must be a
   checkbox flip. Any other hunk → abort the edit and report it.
4. Never untick a box someone else ticked; a box already `[x]` that the run disproved → leave it,
   report the contradiction, ask.

## Evidence table

Same table in the PR body and in the final issue comment:

| # | Criterion (short) | Verdict | Evidence |
|---|---|---|---|
| 1 | migrations up/down clean | met | `alembic upgrade head` + `downgrade -1` green |
| 2 | invalid handle → 400 | met | `test_handle_rejects_reserved` (tests/api/test_profile.py) |
| 3 | docs/API.md updated | met | `docs/API.md:212` |
| 4 | zero-downtime on staging | manual | deploy to staging, check `/healthz` during rollout |

## Gate before the PR

Any criterion not met or `manual` → stop, present the list, ask:

- implement the remainder (loop back to implementation), or
- open the PR with the gap documented — a **Known gaps** section in the PR body listing each
  unticked criterion and why, plus the same list as an issue comment, or
- abort.

Never open a PR that implies completeness it cannot prove. The primary PR carries `Closes #n`, so a
human merge auto-closes the issue with those boxes still empty — the gap has to be visible before
the merge, not discovered after it.

## Recovery

| Failure | Recovery |
|---|---|
| `gh issue edit` fails | report the exact command and the body-file path; the execution result stands, the ticks are pending |
| body changed between fetch and edit | discard the edit, re-fetch, re-map, redo the flip |
| criterion text no longer matches (item was rewritten mid-run) | do not guess a mapping; report the mismatch and ask |
