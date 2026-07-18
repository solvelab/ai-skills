# Design: `backlog` skill

## Context

Users work across multiple GitHub orgs and multi-repo workspaces (N repos of one org sharing a
single Project v2). The catalog is public, so the skill must be 100% generic: all org/project data
lives in per-target config files, never in the skill.

## Goals / Non-Goals

- **Goals**: generic skill; config-per-target; issue enriched with real repo context; preview gate
  before any creation; workspace mode with affected-repo analysis; runtime ID resolution.
- **Non-Goals**: executing backlog items (future `execute-backlog`); GitHub Apps/Actions/MCP
  servers; draft-only Project items; auto-merge or auto-close of anything.

## Decisions

1. **Skill, not slash-command/agent/workflow** — needs rich instructions + references, user
   interaction mid-flow (questions, preview approval), and distribution through this catalog's
   existing pipeline. Subagents (Explore) are used internally for context collection only.
2. **Issue + project item-add** (not draft items) — issues have numbers/URLs, labels, assignees,
   and close via PR (`Closes #n`), which the future `execute-backlog` requires. Draft items are
   GraphQL-node-only and fragile.
3. **Config stores field *names*, never IDs** — IDs (field/option/item) drift and differ per
   Project; resolved each run via `gh project field-list --format json`.
4. **Workspace mode issue home = primary affected repo** (user decision), confirmed in the preview;
   `issues_repo:` config override supports centralized-planning setups.
5. **`gh` CLI is the only integration surface** — already authenticated per user, no token handling
   in the skill, works for every org the user can access. Missing scopes → print
   `gh auth refresh -s project,read:project` and stop with zero side effects.

## Risks / Trade-offs

- Projects v2 field editing needs option IDs → mitigated by recipes in `references/gh-projects.md`.
- LLM-proposed priority/size are heuristics → always surfaced in the preview with 1-line rationale;
  nothing is created without approval.
- Partial failure (issue created, project add fails) → never delete the issue; report the exact
  manual recovery command.
- Config drift (renamed Project fields) → warn + skip missing fields instead of failing the run.

## Migration

None — additive change. Existing skills untouched.
