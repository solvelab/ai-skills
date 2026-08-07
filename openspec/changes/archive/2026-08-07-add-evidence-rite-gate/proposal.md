## Why

`verify-before-claiming` gives the catalog a doctrine against guessing. A doctrine can be ignored:
the agent has to notice it and route to it, and the complaint that produced it is precisely that the
agent does not notice.

This repo already established the two mechanisms that do not depend on noticing, and neither carries
the anti-guessing rule today:

- `scripts/validate-rite.sh` — a CI-wired hard gate that greps every active change for three literal
  strings and fails the build when one is missing. Its own header records why it exists: *"`openspec
  validate --strict` (v1.6.0) checks delta-spec format but NOT custom template sections, so the
  schema's mandatory groups would be advisory only."*
- `claude/global/hooks/backlog-rite.py` — a `UserPromptSubmit` hook whose docstring records the same
  reasoning: *"the harness runs this on every prompt, so enforcement does not depend on the
  assistant noticing a rule already in context."*

Both are about *when work is registered*. Neither is about *whether the facts behind the work were
probed*. A change can pass every gate in this repository today while every claim in it was recalled
rather than checked.

## What Changes

- Add a **fourth mandatory rite gate**: `## 1. Evidence & Sources (MANDATORY)`, the **first** group
  of every `tasks.md`. Position encodes the rule — probe before you write — and mirrors the existing
  last-group constraint on `Validation & Closure`.
- `scripts/validate-rite.sh` gains the grep and the first-group position check, in the idiom already
  used for the other three gates. It also gains a `KNOWN LIMIT` header stating what it cannot check.
- The gate lives in `tasks.md`, not `design.md`: `validate-rite.sh` guards the design file with
  `[ -f "$design" ]`, so a change without one would silently escape any gate placed there.
- `openspec/schemas/skills-rite/templates/tasks.md` prepends the group and renumbers; the schema's
  `description` and its `MANDATORY GATES` prose move from three gates to four; `openspec/config.yaml`
  does the same and gains a `rules.tasks` line.
- Ship `claude/global/hooks/verify-rite.py`, a correction-triggered `UserPromptSubmit` hook.
- Add a `## Grounding (no achismo)` block to `claude/global/personal-rules.md`, which is where the
  *preventive* coverage lives because it loads once per session rather than once per turn.
- Document both in the README, including what the hook cannot enforce.
- Backfill the new group into the one active change that predates the gate, so the gate does not
  break work already in flight.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skills-catalog`: the catalog gains a second distributed enforcement artifact alongside
  `backlog-rite.py`, and its own spec-driven rite gains a gate that makes evidence a required,
  reviewable artifact rather than an assumed one.

## Impact

- `scripts/validate-rite.sh` — one new grep, one new position check, a `KNOWN LIMIT` header.
- `openspec/schemas/skills-rite/templates/tasks.md`, `openspec/schemas/skills-rite/schema.yaml`,
  `openspec/config.yaml` — the gate is described where changes are generated from.
- `claude/global/hooks/verify-rite.py` — new shipped script; persists nothing, needs no credentials.
- `claude/global/personal-rules.md`, `README.md`.
- `openspec/changes/add-verify-before-claiming/tasks.md` — backfilled with the new group; without
  this the gate would fail an in-flight change on its first run.
- **Every future change in this repository** must open its `tasks.md` with the new group. That is the
  point, and it is a breaking change for any in-flight branch that already has a `tasks.md`.
- `generate.sh` does not touch `claude/global/` (0 references), so no wrapper regeneration is needed
  for the hook — only the README edit.
