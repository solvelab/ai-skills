# Change: Add `execute-backlog` skill (backlog item → implemented PR)

## Why

The `backlog` skill creates rich, actionable items; executing them is still a manual,
inconsistent flow. A companion skill can take an existing item and drive it to an approved,
tested pull request while keeping the board in sync — with the same generic, config-driven
design (public catalog, zero user/org data).

## What Changes

- **New skill `skills/execute-backlog/`** — invoked as `/execute-backlog <issue number|url|search>`.
  Reads the issue fully, re-analyzes the current repo/workspace state, verifies the item is
  executable (completeness gate), builds an implementation plan, **presents the plan for approval
  before touching code**, implements following repo conventions, adds/updates tests, runs available
  validations (tests/lint/build/typecheck), fixes findings, then opens a PR linked with
  `Closes #n` and moves the Project item to the review column.
- **Reuses the `backlog` config** (`.github/backlog.yml` / workspace `backlog.yml`) for
  org/Project/fields; reads the issue's *Affected repositories* section in workspace mode and
  checks the needed local clones (offers `gh repo clone` into the workspace when missing).
- **Safety rails**: no auto-merge, never closes the issue directly (only `Closes #n` on the PR),
  scope changes require explicit user approval, board Status transitions restricted to
  configured columns, work happens on a new branch — never on the default branch.
- **References**: `references/execution-flow.md` (gates, plan format, scope-change protocol),
  `references/validation-matrix.md` (how to discover and run each repo's checks),
  `references/board-sync.md` (status transitions + PR↔issue linking recipes).
- Regenerated wrappers (`generate.sh`).

## Impact

- Affected specs: `skills-catalog` (new skill).
- Affected code: `skills/execute-backlog/**` (new), generated wrappers, README catalog table.
- Depends on the `backlog` skill's config convention (already merged); no changes to it.
