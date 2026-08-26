---
name: execute-backlog
description: >-
  Execute an existing GitHub backlog item end-to-end: locate the issue (number, URL or search),
  validate it is complete enough to execute, re-analyze the current repo/workspace state, present
  an implementation plan for approval BEFORE touching code, implement on a dedicated branch
  following the repo's conventions, add/update tests, run the repo's discoverable validations
  (tests/lint/build/typecheck), tick the issue's acceptance-criteria checkboxes that are proven by
  evidence, open pull request(s) linking the issue (Closes #n), and move the GitHub Project item to
  the review column. Use when the user invokes /execute-backlog <n>, says
  "implement issue #N", "execute this backlog item", "pick up this ticket", or wants an existing
  issue turned into a PR. Second half of the backlog-first rite: the item it consumes is produced
  by the backlog skill, and this skill carries it to a reviewable PR. In a repository that runs a
  spec-driven workflow (an openspec/ directory), it gates on that workflow before touching code:
  the item's spec verdict is re-checked, the change is created and validated strict, and only then
  does the plan go to approval. Uses the backlog skill's
  config (.github/backlog.yml or workspace backlog.yml). Do NOT use for creating backlog items
  (that is backlog), for merging PRs, for deploying, or for non-GitHub trackers.
metadata:
  author: solvelab
  version: 1.7.0
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
- **Spec-driven gate: detection, verdict, upgrade/downgrade, archive timing**: `references/spec-rite.md`
- **Discovering and running each repo's validations**: `references/validation-matrix.md`
- **Ticking the item's checkboxes + evidence table + completeness gate**: `references/acceptance-tracking.md`
- **Board transitions + PR↔issue linking + recovery**: `references/board-sync.md`

## CRITICAL: Safety rails

1. **Plan-before-code is a hard gate** — never modify a file before the user approves the plan.
2. **Never merge. Never close the issue directly** — only the `Closes #n` reference on the primary
   PR closes it, and only when a human merges.
3. **Never commit to the default branch** — all work on `backlog/<issue-number>-<slug>`.
4. **Scope is law** — the issue's Scope/Out of scope/Acceptance criteria bound the work. Any
   deviation: stop, explain why, get explicit approval, record the approved deviation as an issue
   comment (`references/execution-flow.md`). The restate-before-acting block and the generic
   off-script guard are `verify-before-claiming`.
5. **Run only discovered commands** — validations come from the repo's own manifests/docs; never
   invent commands, never run migrations/deploys/destructive steps without an explicit ask. When
   discovery finds no command, report the gap instead of inventing one (`verify-before-claiming`).
6. **Faithful reporting** — failing checks are reported with their output; skipped validations are
   listed as skipped, never implied as passed.
7. **Every checkbox gets a verdict** — before the PR, each acceptance criterion (and each rite
   checklist item in the body) is either ticked because evidence proves it, or left unticked and
   reported as a gap. Never bulk-tick, never tick from intent instead of proof, never leave a box
   silently empty (`references/acceptance-tracking.md`).
8. **Code speaks English** — identifiers, file and module names, REST path segments and query
   params, DB tables and columns, enum values, event and topic names, config keys and log field keys
   are English even when the issue, the commits and the comments are not. Names come from the item's
   Glossary; a domain term with no faithful translation is kept only when that Glossary lists it. An
   unlisted term is a stop-and-ask under rail 4, never an improvised translation (`code-locale`).
9. **The project's rite wins** — at every stage the card advances, discover and follow the target
   repo's own established process for that stage (spec/proposal rites, implementation and test
   rites, review templates). The generic workflow here is the fallback, never an override
   (`references/execution-flow.md`, *Per-stage rite discovery*).
10. **Spec-before-code is a hard gate too** — in a repo that runs a spec-driven workflow, no file
   **outside that workflow's own directory** is edited before the change exists and its strict
   validation is green. The policy belongs to the repo (`spec_rite.policy` in the backlog config);
   a repo that carries the workflow and states no policy is treated as requiring the change. The
   verdict the item carries is re-checked, never re-decided: raise it without asking, lower it only
   with the user. The workflow's own lifecycle is not restated here — it is `openspec` (or the
   project's fork, e.g. `openspec-drivezone`). Protocol: `references/spec-rite.md`.

## Workflow

1. **Locate** — argument may be a number, URL or search term. Resolve config (same
   discovery/precedence as `backlog`). Number/search → `gh issue view` in the primary repo (or
   search across workspace repos). Not found → clear error, stop.
2. **Read fully** — body, comments (later comments may amend scope), linked PRs, labels, board
   status. Existing open PR for the item → report and ask before duplicating work. Resolve linked
   PRs from the issue's own link graph, never from a text search — recipe and the measured failure
   of the search approach: `references/board-sync.md` (*Finding the item's PRs*).
3. **Completeness gate** — the item must have enough to execute: goal, scope, acceptance
   criteria. Also re-check against the *current* codebase (drift since grooming: files renamed,
   feature landed meanwhile). Gaps/contradictions → report and ask: proceed as-is (user accepts
   risk), refine first (point to `/backlog`), or abort. Never guess missing scope. A code-producing
   item with no Glossary is a soft signal, not a blocker — flag it and derive the rows in step 4.
   Gate passed →
   move the board item to the ready column (step-by-step Kanban flow, `references/board-sync.md`).
4. **Context re-analysis** — Explore subagent(s) over the affected repo(s) (issue's Affected
   repositories section in workspace mode; verify local clones, offer `gh repo clone` for missing
   ones). Collect: current state of cited files, conventions, test setup, related recent changes,
   and the identifier vocabulary the repo already uses for the item's concepts (`code-locale`).
5. **Spec rite** — repo with a spec-driven workflow only; skip when there is none. Detect it and
   the schema it runs, re-check the item's verdict against the surface the re-analysis just
   measured, and — when the verdict requires it — create the change and validate it strict before
   step 6. Raising a verdict needs no permission; lowering one does. Full protocol, detection
   commands and archive timing: `references/spec-rite.md`.
6. **Implementation plan** — present: interpretation of the item, files to change per repo, the
   Glossary, test strategy, validations to run, risks, estimated blast radius. When the item ships a
   runtime artifact — a skill, a hook, a script someone runs — the plan also names **how it will be
   exercised end to end**, through the path its user takes, because that is what the sweep will ask
   for later. In a repo with a spec rite, also the change id, the capabilities its delta touches and
   the strict-validation output line. **Wait for approval.**
7. **Implement** — branch `backlog/<n>-<slug>` per affected repo; follow repo conventions and
   project skills (e.g. `conventional-commit`, and the repo's spec rite when it has one). Names for
   anything new come from the approved Glossary (rail 8). A spec rite's task list is ticked task by
   task as each one lands and is validated, never in a batch at the end. Move the board item
   to the configured in-progress column when work starts.
8. **Tests** — add/update tests per the issue's test strategy and the repo's framework. A test suite
   the artifact passes is not proof it runs: **exercise it once through its real entry point** and
   record what you observed, with the case matrix as counts. A green selftest and a green pipeline
   shipped two defects that only an end-to-end run surfaced (measured 2026-08-26, issue #95). Where
   the repo's spec rite carries a simulation group, this is what fills it; breaking the artifact on
   purpose afterwards is `bug-hunter`, a different job.
9. **Validate** — discover and run the repo's checks (`references/validation-matrix.md`); fix
   findings; re-run until green or report honest blockers. A repo that wires an identifier-locale
   check is running one of its own discovered commands — never invent one where none exists.
10. **Acceptance sweep** — walk the item's checkboxes one by one, assign each a verdict backed by
    the validation evidence, tick the proven ones in the issue body (surgical read-modify-write),
    and gate on the rest: unmet or manual-only criteria stop the run for a decision before any PR
    is opened (`references/acceptance-tracking.md`). A spec rite's mandatory closure group is part
    of the sweep, not a separate afterthought.
11. **PR(s)** — one per changed repo; primary repo's PR body carries `Closes #n`, others reference
    `Relates to <issue-url>`, plus the evidence table, the simulation's measured counts when the item
    shipped a runtime artifact, and a **Known gaps** section when the sweep left anything unticked. Where the repo gates on a spec rite, the body also carries the line that
    gate reads — the change id, or the written waiver and its reason (`references/spec-rite.md`).
    No auto-merge. Follow `conventional-commit` PR rules when present.
12. **Sync & report** — move the board item to the review column; comment on the issue with links
    to the PR(s); present summary: what changed, validation evidence, the criteria table with
    every verdict, deviations (if any, pre-approved), next human step (review/merge). A change left
    active on purpose is reported as pending, naming what closes it.
