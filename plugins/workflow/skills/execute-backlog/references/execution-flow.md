# Execution flow details

## Completeness checklist (gate before planning)

Executable item needs, at minimum:

- [ ] Goal — observable outcome.
- [ ] Scope + Out of scope — boundaries of the work.
- [ ] Acceptance criteria — verifiable statements.
- [ ] Affected repositories (workspace mode) or the issue lives in the repo to change.

Soft signals worth flagging (not blockers): missing test strategy, missing technical requirements,
stale file references (drift). Present gaps as a short list with a recommendation: proceed /
refine via `/backlog` / abort.

## Plan format (presented for approval)

```markdown
## Plan — #<n> <title>

**Interpretation**: 1-2 sentences — what will exist when done.
**Repos/branches**: org/repo → backlog/<n>-<slug> (one line per repo, primary marked)
**Changes**: per repo, file-level bullets (path → what and why)
**Tests**: what will be added/updated, framework, where
**Validations**: the discovered commands that will run
**Risks**: item risks + anything new found in re-analysis
**Out of scope (respected)**: restate the issue's exclusions
```

Approval options: approve / adjust (loop back with changes) / abort. Record substantive
adjustments as an issue comment before starting.

## Scope-change protocol

Deviation discovered mid-implementation (hidden dependency, wrong assumption in the item):

1. Stop at a safe point (no half-applied refactors).
2. Present: what was found, why the planned path is wrong/insufficient, proposed scope change,
   impact on acceptance criteria.
3. On approval: comment on the issue documenting the approved change, then continue.
4. On rejection: revert uncommitted deviation work, continue inside original scope or abort.

## Multi-repo orchestration (workspace mode)

- Source of truth for targets: the issue's *Affected repositories* section; re-validate it against
  the re-analysis (drift may have added/removed repos → surface in the plan).
- Missing local clone → offer `gh repo clone org/repo` into the workspace root; never work on a
  repo the user declined to clone.
- Implement repos in dependency order stated in the plan (e.g. backend before consumer).
- One PR per changed repo. Primary PR: `Closes #n`. Secondary PRs: `Relates to <issue-url>` plus a
  link to the primary PR. Cross-link all PRs in the final issue comment.

## Branch & commit rules

- Branch: `backlog/<issue-number>-<kebab-slug>` from the repo's default branch, freshly pulled.
- Commits: repo's own convention (check its history and skills; `conventional-commit` applies when
  present — no AI attribution).
- Small, reviewable commits; no squashing of unrelated concerns.
