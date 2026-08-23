# Execution flow details

## Completeness checklist (gate before planning)

Executable item needs, at minimum:

- [ ] Goal — observable outcome.
- [ ] Scope + Out of scope — boundaries of the work.
- [ ] Acceptance criteria — verifiable statements.
- [ ] Affected repositories (workspace mode) or the issue lives in the repo to change.

Soft signals worth flagging (not blockers): missing test strategy, missing technical requirements,
stale file references (drift), and a code-producing item with no Glossary — derive the rows during
re-analysis rather than blocking (`code-locale`). Present gaps as a short list with a
recommendation: proceed / refine via `/backlog` / abort.

## Plan format (presented for approval)

```markdown
## Plan — #<n> <title>

**Interpretation**: 1-2 sentences — what will exist when done.
**Spec rite**: change id + capabilities the delta touches + the strict-validation output line, or
the written waiver and its reason (omit the whole line in a repo with no spec rite)
**Repos/branches**: org/repo → backlog/<n>-<slug> (one line per repo, primary marked)
**Changes**: per repo, file-level bullets (path → what and why)
**Glossary**: term → identifier (from the item; rows derived here are marked NEW)
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

## Per-stage rite discovery (respect the project's own process)

Each project may have its own rite for each Kanban stage. Before acting in a stage, discover how
the target repo runs that stage and follow it — the generic flow in SKILL.md is the fallback,
never an override. When a rite exists, its artifacts (proposal, tasks file, checklists) become
part of the deliverable and must appear in the plan.

| Stage | What to look for | Examples |
|---|---|---|
| Ready (grooming gate) | Does the project require a formal proposal/spec before code? | A spec-driven workflow is not an example here — it is a hard gate with its own protocol: `references/spec-rite.md`. Other shapes: RFC/ADR templates in `docs/` |
| In progress (implementation) | Implementation and test rites, commit conventions | The spec rite's task list ticked task by task; adversarial-test rites (e.g. bug-hunter); `conventional-commit` |
| In review (PR) | Review rites: PR templates, required checklists, CI gates | `.github/PULL_REQUEST_TEMPLATE*`, CONTRIBUTING review rules, project code-review skills |

Discovery sources, in order:

1. Project skills active in the session (they encode the rite explicitly).
2. Repo docs: `CLAUDE.md`, `CONTRIBUTING.md`, `README`, `docs/`.
3. Structural markers: `openspec/` dir, PR/issue templates, CI required checks.

Conflict between the generic flow and a project rite → the project rite wins; state in the plan
which rite is being followed per stage so the user sees it before approving.

Discovery is a judgment, and a judgment is exactly what fails silently. Where the rite is
spec-driven, do not rely on this table: rail 10 and `references/spec-rite.md` make it a gate with a
default that fails closed.

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
- A spec rite's artifacts are committed **before** the first commit that changes anything else, so
  the history shows the registration preceding the work rather than trailing it.
- Small, reviewable commits; no squashing of unrelated concerns.
