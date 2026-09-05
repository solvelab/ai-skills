---
name: backlog
description: >-
  Turn a natural-language idea into a structured GitHub backlog item: analyze the repository (or
  multi-repo workspace) for real context, draft a rich issue (context, problem, scope, acceptance
  criteria, risks, affected files/repos), preview it for approval, then create the issue and add
  it to the configured GitHub Project v2 with fields set (Status/Priority/Size/Estimate) via the
  gh CLI. Use when the user invokes /backlog <idea>, says "create a backlog item", "add this to
  the backlog", "turn this idea into an issue", "groom this idea", or wants an idea registered in
  a GitHub Project. Entry point of the backlog-first rite: execute-backlog turns the item created
  here into a branch and a pull request. In a repository with a spec-driven workflow (an openspec/
  directory) the item also declares its spec verdict: a change id or a written waiver. Do NOT use
  for implementing an existing issue (that is execute-backlog), for creating pull requests, or for
  non-GitHub trackers (Jira, Linear, Trello).
metadata:
  author: solvelab
  version: 1.5.1
  category: process
license: MIT
compatibility: >-
  Requires the gh CLI (>= 2.40) authenticated with project,read:project scopes and write access to
  the target repository. Works in any git repository or multi-repo workspace directory.
---

# Backlog — idea → structured GitHub Project item

Enrich a raw idea with real repository context and publish it as a GitHub issue inside the
configured GitHub Project v2 — never a copy of the user's sentence, always grounded in the actual
codebase. The first run per repo/workspace launches a config wizard that writes
`.github/backlog.yml` (repo mode) or `backlog.yml` (workspace mode). The spec verdict the item
declares is what `execute-backlog` inherits, instead of making a new decision.

- **Issue section template + writing guidance**: `references/issue-template.md`
- **Config schema (both modes, precedence, wizard, `spec_rite`)**: `references/backlog-config.md`
- **gh recipes for Projects v2 (IDs, item-edit, verification, recovery)**: `references/gh-projects.md`

## CRITICAL: Ground rules

1. **Preview gate** — nothing is created on GitHub before the user approves the full preview
   (issue markdown + target repo + proposed field values). Approve / adjust / cancel; adjusting
   loops back to a new preview.
2. **No invention** — never guess org, repo, Project, field names or select options. Everything
   comes from config, `gh` output, or the user. Select values must be options returned by
   `gh project field-list`. A translation is an invention too: an identifier proposed in the Glossary
   is harvested from the codebase or decided with the user, never improvised (`code-locale`). The
   general form — the research ladder and the report to write when nothing is found — is
   `verify-before-claiming`.
3. **Anti-generic gate** — the draft must cite real files, modules or features found in the
   repository. If context collection found nothing relevant, say so instead of padding.
4. **Non-destructive** — never delete/close issues, never edit existing items, never merge. A
   partially failed run reports the exact recovery command instead of rolling back.
5. **IDs are runtime-only** — config stores field *names*; resolve project/field/option/item IDs
   fresh each run (they drift and differ per Project).
6. Ask questions **only** when essential information is missing or ambiguous (max ~3, objective).
   Everything derivable from the repo must be derived, not asked.
7. **Spec-rite gate** — in a repo that runs a spec-driven workflow, the item is not complete until
   it declares its verdict: the change that will register the work, or a waiver written as a line
   with a reason. The default is that the change is required; a repo carrying the workflow with no
   stated policy is treated as requiring it, because an unstated policy is the absence of a
   decision, not permission to skip. Never decide this silently — the verdict is a section of the
   item and appears in the preview. The workflow's own lifecycle is not restated here: it is
   `openspec`, or the project's fork (`openspec-drivezone` is one).

## Workflow

1. **Parse** — the argument is the idea. Empty → ask for it and stop until answered.
2. **Preflight** — `gh auth status` must list the `project` scope; missing → print
   `gh auth refresh -s project,read:project` and stop (zero side effects). Detect mode and load
   config (see `references/backlog-config.md`):
   - cwd inside a git repo → **repo mode**, config `.github/backlog.yml` (walk up to repo root;
     also check for a workspace `backlog.yml` one level above the repo — repo config wins).
   - cwd not a repo but subdirectories are git repos → **workspace mode**, config `backlog.yml`
     in cwd.
   - No config → **setup wizard** (below), then continue.
3. **Context collection** — spawn Explore subagent(s) (cheap model, low effort) over the target
   repo(s): related modules/files, existing similar features, naming and test conventions, docs
   (README/CLAUDE.md), and the **identifier vocabulary already in use** for the concepts the idea
   names. Workspace mode: one subagent per candidate repo in parallel; conclude which repos the idea
   affects and each repo's role.
4. **Duplicate check** — `gh issue list -R <repo> --search "<key terms>" --state open`. Strong
   candidate → show it and ask whether to continue, enrich the existing issue instead, or cancel.
5. **Gap questions** — only for essentials the repo cannot answer (e.g. which provider, which of
   two plausible scopes). Batch them in one round.
6. **Spec-rite triage** — repo with a spec-driven workflow only; skip when there is none:

   ```bash
   [ -d openspec ] && grep -m1 '^schema:' openspec/config.yaml   # which schema this repo runs
   openspec list                                                 # a related change may be open
   ```

   Read `spec_rite.policy` from config (`references/backlog-config.md`); absent with the workflow
   present ⇒ `required`. Then propose the verdict: a verb-led change id (`add-`, `update-`,
   `remove-`, `refactor-`) plus the capabilities its delta will touch, or the waiver line and the
   reason it is legitimate. An existing open change that already covers the idea is named instead
   of a new one.
7. **Draft** — fill the template from `references/issue-template.md`; omit sections that do not
   apply. When the item produces code, fill the **Glossary** from the vocabulary harvested in step 3
   before deciding any new name; a term neither the codebase nor the user resolves becomes a gap
   question in step 5, never a translation invented here (`code-locale`). Workspace mode adds
   *Affected repositories* (role per repo) and elects the **primary affected repo** (issue home,
   unless `issues_repo` is configured). Propose field values (Status default from config;
   Priority/Size/Estimate heuristics) each with a 1-line rationale.
8. **Preview + approval** — show the complete issue markdown, target repo, labels, assignees,
   proposed field values and the spec verdict. Only proceed on explicit approval.
9. **Create** — in order, capturing outputs (exact commands in `references/gh-projects.md`):
   `gh issue create` → `gh project item-add` → `gh project item-edit` per configured field. Repeat
   the add (and the Status default) for every board in `extra_projects`, when configured — an issue
   can live on several Projects at once (see `references/backlog-config.md`).
10. **Report** — issue URL, project item confirmation, fields set, the spec verdict recorded, plus
   any warnings (skipped fields, partial failures + recovery commands).

## Setup wizard (first run, per repo/workspace)

1. Discover candidate owner(s) from git remotes (`git remote get-url origin`; workspace mode:
   remotes of child repos — they normally share one org).
2. `gh project list --owner <owner>` → user picks the Project (auto-pick if exactly one, confirm).
3. `gh project field-list <n> --owner <owner> --format json` → map standard fields by name
   (Status, Priority, Size, Estimate — case-insensitive; report unmapped names).
4. Pick the default Status for new items (suggest "Backlog" if present).
5. Write the config file, show it, suggest committing it so the whole team inherits the setup.

## Failure rules

| Failure | Behavior |
|---|---|
| Missing `project` scope | Stop before any write; print the exact `gh auth refresh` command. |
| Config invalid / Project not found | Report the exact `gh` error; create nothing. |
| Configured field absent in Project | Warn + skip that field; still create the issue. |
| `item-add`/`item-edit` fails after issue creation | Keep the issue; report it + the exact manual recovery command. |
| `extra_projects` board unreachable / field missing there | Warn + skip that board; the primary Project and the issue stand. A mirror is never a reason to fail the run. |
| Select option not found for a proposed value | Show available options; ask instead of guessing. |
| Select field with an empty options array | Likely an org **issue field** mirrored into the board — resolve options via `GET /orgs/<owner>/issue-fields` and set through the issue-field-values endpoint (see `references/gh-projects.md`), not `item-edit`. |

