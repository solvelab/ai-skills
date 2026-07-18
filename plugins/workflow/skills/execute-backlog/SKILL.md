---
name: execute-backlog
description: >-
  Execute an existing GitHub backlog item end-to-end: locate the issue (number, URL or search),
  validate it is complete enough to execute, re-analyze the current repo/workspace state, present
  an implementation plan for approval BEFORE touching code, implement on a dedicated branch
  following the repo's conventions, add/update tests, run the repo's discoverable validations
  (tests/lint/build/typecheck), open pull request(s) linking the issue (Closes #n), and move the
  GitHub Project item to the review column. Use when the user invokes /execute-backlog <n>, says
  "implement issue #N", "execute this backlog item", "pick up this ticket", or wants an existing
  issue turned into a PR. Uses the backlog skill's config (.github/backlog.yml or workspace
  backlog.yml). Do NOT use for creating backlog items (that is backlog), for merging PRs, for
  deploying, or for non-GitHub trackers.
metadata:
  author: solvelab
  version: 1.1.0
  category: process
license: MIT
compatibility: >-
  Requires the gh CLI (>= 2.40) authenticated with project,read:project scopes, write access to
  the affected repositories, and a local clone (repo mode) or workspace with clones (workspace
  mode). Reuses the backlog skill's config files.
---

# Execute-backlog — backlog item → implemented, validated PR

Drive an existing issue to a reviewable pull request while keeping the board in sync. Companion
to the `backlog` skill; consumes the same config.

- **Gates, plan format, scope-change protocol, multi-repo orchestration**: `references/execution-flow.md`
- **Discovering and running each repo's validations**: `references/validation-matrix.md`
- **Board transitions + PR↔issue linking + recovery**: `references/board-sync.md`

## CRITICAL: Safety rails

1. **Plan-before-code is a hard gate** — never modify a file before the user approves the plan.
2. **Never merge. Never close the issue directly** — only the `Closes #n` reference on the primary
   PR closes it, and only when a human merges.
3. **Never commit to the default branch** — all work on `backlog/<issue-number>-<slug>`.
4. **Scope is law** — the issue's Scope/Out of scope/Acceptance criteria bound the work. Any
   deviation: stop, explain why, get explicit approval, record the approved deviation as an issue
   comment (`references/execution-flow.md`).
5. **Run only discovered commands** — validations come from the repo's own manifests/docs; never
   invent commands, never run migrations/deploys/destructive steps without an explicit ask.
6. **Faithful reporting** — failing checks are reported with their output; skipped validations are
   listed as skipped, never implied as passed.
7. **The project's rite wins** — at every stage the card advances, discover and follow the target
   repo's own established process for that stage (spec/proposal rites, implementation and test
   rites, review templates). The generic workflow here is the fallback, never an override
   (`references/execution-flow.md`, *Per-stage rite discovery*).

## Workflow

1. **Locate** — argument may be a number, URL or search term. Resolve config (same
   discovery/precedence as `backlog`). Number/search → `gh issue view` in the primary repo (or
   search across workspace repos). Not found → clear error, stop.
2. **Read fully** — body, comments (later comments may amend scope), linked PRs, labels, board
   status. Existing open PR for the item → report and ask before duplicating work.
3. **Completeness gate** — the item must have enough to execute: goal, scope, acceptance
   criteria. Also re-check against the *current* codebase (drift since grooming: files renamed,
   feature landed meanwhile). Gaps/contradictions → report and ask: proceed as-is (user accepts
   risk), refine first (point to `/backlog`), or abort. Never guess missing scope. Gate passed →
   move the board item to the ready column (step-by-step Kanban flow, `references/board-sync.md`).
4. **Context re-analysis** — Explore subagent(s) over the affected repo(s) (issue's Affected
   repositories section in workspace mode; verify local clones, offer `gh repo clone` for missing
   ones). Collect: current state of cited files, conventions, test setup, related recent changes.
5. **Implementation plan** — present: interpretation of the item, files to change per repo, test
   strategy, validations to run, risks, estimated blast radius. **Wait for approval.**
6. **Implement** — branch `backlog/<n>-<slug>` per affected repo; follow repo conventions and
   project skills (e.g. `conventional-commit`, project-specific rites like OpenSpec when the repo
   uses them). Move the board item to the configured in-progress column when work starts.
7. **Tests** — add/update tests per the issue's test strategy and the repo's framework.
8. **Validate** — discover and run the repo's checks (`references/validation-matrix.md`); fix
   findings; re-run until green or report honest blockers.
9. **PR(s)** — one per changed repo; primary repo's PR body carries `Closes #n`, others reference
   `Relates to <issue-url>`. No auto-merge. Follow `conventional-commit` PR rules when present.
10. **Sync & report** — move the board item to the review column; comment on the issue with links
    to the PR(s); present summary: what changed, validation evidence, deviations (if any,
    pre-approved), next human step (review/merge).

## Trigger Test Cases

Should trigger on:
- "/execute-backlog 123"
- "Implement issue #42"
- "Pick up the backlog item about push notifications"
- "Execute https://github.com/org/repo/issues/7"

Should NOT trigger on:
- "Create a backlog item for X" (backlog)
- "Merge PR #12"
- "Deploy the fix"
- "Close issue #9"
