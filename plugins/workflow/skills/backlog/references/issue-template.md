# Issue template

Title: short, imperative, outcome-focused (max ~70 chars). Prefix nothing — labels/fields carry
type and priority.

Omit any section that does not apply — an empty heading is worse than no heading. Every claim about
the codebase must come from the context-collection step (real paths, real modules). Write the issue
in the repository's working language (default: the language of its README). That governs the
issue's **prose only** — the code the item produces is English regardless (`code-locale`), so fill
the Glossary section below and leave no name to be improvised at implementation time.

```markdown
## Context

What exists today, in this repo, that this idea touches. Cite real files/modules
(`path/to/module.py`) and current behavior.

## Problem

The gap or pain. Why the current state is insufficient.

## Goal

The outcome once done — observable, one paragraph.

## Scope

- Bullet list of what IS included.

## Out of scope

- Explicitly excluded work (prevents scope creep in execution).

## Functional requirements

- FR1 …
- FR2 …

## Glossary (domain term → identifier)   <!-- required when the item produces code -->

| Termo (PT) | Identifier (EN) | Origin |
|---|---|---|
| pedido | `order` | already used in `app/models/order.py` |
| entrega | `delivery` | new — decided here |
| nota fiscal | `nota_fiscal` | keep-as-is: legal document, no faithful translation |

Harvest before deciding: every row is either taken from what the codebase already calls the concept,
or marked `new — decided here`. A term neither the codebase nor the user resolves is a gap question,
never a translation invented in the draft. Protocol: `code-locale`.

## Spec rite   <!-- required when the target repo runs a spec-driven workflow -->

- Workflow / schema: `openspec`, schema `<name>` (from `openspec/config.yaml`; absent → vanilla)
- Policy: `required` (from `spec_rite.policy`, or the fail-closed default)
- Verdict: **change required** — id `<verb-led-change-id>`
- Capabilities the delta touches: `<capability>` (ADDED / MODIFIED / REMOVED)

<!-- or, when the work genuinely registers no requirement change: -->

- Verdict: `Spec-rite: none — <the reason, one line>`

The verdict is a decision recorded here, not one made at implementation time. `execute-backlog`
re-checks it against the real change surface, raises it on its own when the work outgrew the item,
and stops for the user before ever lowering it. Protocol:
`execute-backlog/references/spec-rite.md`.

## Technical requirements

- TR1 … (constraints: stack, patterns to follow — cite existing conventions/files)

## Acceptance criteria

- [ ] Verifiable statements, testable one by one.
- [ ] When the item produces code: new identifiers, routes, keys and event names follow the Glossary
      and `code-locale`.

## Dependencies

- Other issues, services, credentials, decisions this blocks on.

## Risks

- Risk → mitigation, one line each.

## Test strategy

How this will be validated (unit/integration/manual), following the repo's existing test
conventions (cite the test dir/framework found).

## Affected files/components

- `path/…` — why it changes.

## Affected repositories   <!-- workspace mode only -->

- `org/repo-a` — role in the implementation (primary).
- `org/repo-b` — role.
```

Omit the *Spec rite* section entirely in a repository with no such workflow — an empty heading is
worse than no heading, and the gate is a no-op there.

Field proposal guidance (shown in the preview with a 1-line rationale each):

- **Status**: config default (usually Backlog).
- **Priority**: infer from user wording and blast radius; when in doubt propose the middle option.
- **Size/Estimate**: from the number of affected files/repos and requirement count; never present
  as certainty — it is a triage hint, not a commitment.
- **Labels**: only labels that already exist in the repo (`gh label list`); map via config
  `labels:` when present.
