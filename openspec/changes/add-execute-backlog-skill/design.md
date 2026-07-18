# Design: `execute-backlog` skill

## Context

Companion to `backlog`: consumes the items it creates (or any well-formed issue). Same catalog
constraints: public, generic, English, config-per-target. Runs inside the target repo or
workspace, driven by the user's own `gh` auth.

## Goals / Non-Goals

- **Goals**: issue → approved plan → implementation → validated PR → board updated; completeness
  gate before any work; explicit approval gates; workspace-aware (multi-repo).
- **Non-Goals**: merging PRs, closing issues directly, deploying, editing the backlog item's scope
  silently, executing several items in one run.

## Decisions

1. **Plan-before-code is a hard gate** — the skill always presents scope, files to touch, test
   strategy and risks, and waits for approval. Mirrors the preview gate of `backlog`.
2. **Completeness gate** — if the issue lacks acceptance criteria/scope or contradicts the current
   codebase (drift since creation), the skill reports gaps and asks whether to proceed, refine the
   issue first (pointing to `/backlog`), or abort. It never guesses missing scope.
3. **Branch-per-item** (`backlog/<issue-number>-<slug>`) in each affected repo; commits follow the
   repo's own conventions (`conventional-commit` skill when present). One PR per affected repo,
   each linking the issue; only the primary repo's PR carries `Closes #n`.
4. **Validation discovery, not assumption** — detect the repo's real checks (test runner, linter,
   build, typecheck) from its manifests/docs; run what exists; report what was skipped for not
   existing. Never invent commands.
5. **Board sync via the same runtime-ID resolution** as `backlog` (`references/board-sync.md`):
   move to the configured in-progress column when work starts, review column when the PR opens.
6. **Scope-change protocol** — any deviation from the issue's scope/acceptance criteria is
   surfaced with rationale and requires explicit approval; approved deviations are recorded as an
   issue comment for traceability.

## Risks / Trade-offs

- Issue drift (codebase changed since grooming) → completeness gate re-validates against current
  code before planning.
- Long multi-repo executions → per-repo PRs keep reviews small; the skill reports partial progress
  instead of one opaque mega-change.
- Validation commands can be destructive in odd repos → only run read-only/build/test commands
  discovered from the repo's own docs/manifests; never migrations/deploys without explicit ask.

## Migration

None — additive. Depends on the merged `backlog` config convention.
