# Change: Add `backlog` skill (idea → structured GitHub backlog item)

## Why

Turning a raw idea into a well-structured backlog item (issue + GitHub Project v2 placement with
fields) is a repetitive, error-prone manual flow. A catalog skill can do it with real repository
context — generic, so any user/org can adopt it without embedding personal project data in this
public repo.

## What Changes

- **New skill `skills/backlog/`** — invoked as `/backlog <idea>`. Enriches the idea with actual
  repository context, drafts a structured issue (template sections), previews it for approval, then
  creates the GitHub issue and inserts it into the configured Project v2 with fields
  (Status/Priority/Size/Estimate) via `gh` CLI.
- **Two operation modes** detected from the current directory: *repo mode* (config at
  `.github/backlog.yml`) and *workspace mode* (directory containing N repos of one org; config at
  `backlog.yml` in the workspace root; skill analyzes which repos the idea affects and creates the
  issue in the primary affected repo).
- **First-run setup wizard** — discovers owner from git remotes, lists Projects, maps fields by
  name, writes the config file. Field/option/item IDs are resolved at runtime, never persisted.
- **References**: `references/issue-template.md` (canonical section template),
  `references/backlog-config.md` (config schema), `references/gh-projects.md` (Projects v2 `gh`
  recipes, including single-select option-ID resolution).
- Regenerated wrappers (`generate.sh`) for claude/codex/cursor/copilot/plugins.

Out of scope (separate future change): `execute-backlog` skill that implements an existing item.

## Impact

- Affected specs: `skills-catalog` (new skill added).
- Affected code: `skills/backlog/**` (new), generated wrapper outputs, README catalog table.
- No behavior change to existing skills. Requires `gh` CLI with `project,read:project` scopes at
  usage time; degrades to a clean actionable error without them.
