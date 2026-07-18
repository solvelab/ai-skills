# Tasks: add-backlog-skill

## 1. Skill authoring

- [x] 1.1 `skills/backlog/SKILL.md` — frontmatter per skills-authoring spec (`category: process`,
      English, `compatibility` requiring `gh` CLI with `project,read:project` scopes); flow: mode
      detection → preflight (scopes, config/wizard) → context collection (Explore subagents) →
      duplicate check → essential-gap questions only → structured draft (anti-generic gate: must
      cite real files/modules) → preview approval → create issue + project item-add + item-edit →
      report with URLs; partial-failure and error rules.
- [x] 1.2 `references/issue-template.md` — canonical section template (Title, Context, Problem,
      Goal, Scope, Out of scope, Functional/Technical requirements, Acceptance criteria,
      Dependencies, Risks, Test strategy, Affected files/components, Affected repositories
      [workspace mode]) + writing guidance (omit non-applicable sections).
- [x] 1.3 `references/backlog-config.md` — schema + commented examples for both modes
      (`.github/backlog.yml`, workspace `backlog.yml`), precedence rule, `issues_repo` override.
- [x] 1.4 `references/gh-projects.md` — `gh` recipes: scope check, project list/field-list JSON,
      option-ID resolution, item-add/item-edit per field type, item-list verification, recovery
      commands for partial failures.

## 2. Wrappers & catalog integrity

- [x] 2.1 Run `./generate.sh`; confirm wrappers for `backlog` appear in claude/codex/cursor/copilot
      and `plugins/workflow/` (category process → workflow group).
- [x] 2.2 Local CI parity: frontmatter check passes (name==dir, semver, controlled category);
      `git diff` clean after regeneration; README catalog table updated if it enumerates skills.

## 3. Tests & validation (controlled, DriveZoneFivem sandbox)

- [x] 3.1 Negative — missing scopes: simulate token without `project` scope → skill aborts with the
      exact `gh auth refresh -s project,read:project` instruction, zero side effects.
- [x] 3.2 Wizard — run in the DriveZoneFivem workspace with no config → generated config points to
      org project #1 (Assetto-Corsa) with correctly mapped Status/Priority/Size/Estimate fields.
- [x] 3.3 Controlled creation — sample idea → preview shown and approved → issue created in primary
      affected repo, item in project #1, fields set; verified via `gh issue view` +
      `gh project item-list --format json`.
- [x] 3.4 Duplicate detection — same idea again → warning before creation.
- [x] 3.5 Invalid config — wrong owner/number → clear error, nothing created.
- [x] 3.6 Partial failure — field configured but absent in Project → warn + skip, issue still
      created, recovery command reported.

## 4. Closure

- [x] 4.1 Document usage/maintenance (skill body serves as doc; README entry present).
- [ ] 4.2 Present validation evidence (URLs, JSON field dump) to the user; await approval before
      starting the `execute-backlog` change.
