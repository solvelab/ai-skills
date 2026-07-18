# Issue template

Title: short, imperative, outcome-focused (max ~70 chars). Prefix nothing — labels/fields carry
type and priority.

Omit any section that does not apply — an empty heading is worse than no heading. Every claim about
the codebase must come from the context-collection step (real paths, real modules). Write the issue
in the repository's working language (default: the language of its README).

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

## Technical requirements

- TR1 … (constraints: stack, patterns to follow — cite existing conventions/files)

## Acceptance criteria

- [ ] Verifiable statements, testable one by one.

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

Field proposal guidance (shown in the preview with a 1-line rationale each):

- **Status**: config default (usually Backlog).
- **Priority**: infer from user wording and blast radius; when in doubt propose the middle option.
- **Size/Estimate**: from the number of affected files/repos and requirement count; never present
  as certainty — it is a triage hint, not a commitment.
- **Labels**: only labels that already exist in the repo (`gh label list`); map via config
  `labels:` when present.
