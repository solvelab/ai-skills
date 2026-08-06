## Context

The process skills are the ones that *act* — they run `gh`, `git` and `openspec` on the user's behalf.
A wrong flag in a code-heavy reference skill wastes a reader's minute; a wrong flag here fails
mid-operation, sometimes after a write has already landed. They are also the easiest family to verify,
because the tools are installed and self-documenting.

## Goals / Non-Goals

**Goals**
- Every CLI claim these skills make is probed against the installed tool.
- The two defects found by using the skills are fixed at the point of use.
- A negative result is reported as a negative result.

**Non-Goals**
- No new doctrine. The `backlog` recipe was already correct; only its rationale was missing.
- No commit-message linting. The gitmoji↔type mapping is convention; adding a CI check for it is a
  separate proposal, and history is immutable anyway.
- Not probing `claude-statusline`'s JSON field list against a live Claude Code session — that needs a
  running harness, not a CLI, and is out of scope here.

## Decisions

**D1 — Probe by `--help`, not by execution.** Running `gh issue create` to check it exists would file
an issue. Resolving the subcommand and grepping its help output for each flag is non-destructive and
catches exactly the failure that matters: a renamed subcommand or a removed flag.

**D2 — Report the clean result.** 28 of 28 claims held. Writing edits anyway to justify the audit
would be the same dishonesty the catalog's other audits were built to remove.

**D3 — Ground the release table in this repo's history, not the preset docs.** Three commits merged on
2026-08-06 give a direct reading: `fix` released, `ci` and `docs` did not. That is falsifiable by
anyone with `git log`; a citation of the preset's README is not.

**D4 — Tell people to type security fixes as `fix`.** The honest alternative — adding `security` to
`releaseRules` — is a repo-by-repo change this skill cannot make. The rule that works everywhere is to
use a shipping type and carry the emphasis in the scope, body and emoji.

**D5 — Put the lag warning next to the recipe, not in a troubleshooting section.** The failure happens
in the seconds between two commands; the warning is only useful where the id is captured.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Commit and PR message format, type→icon mapping, release impact | `conventional-commit` | already canonical — release impact added |
| `gh` Projects v2 recipes (ids, item-add/edit, org issue fields, recovery) | `backlog/references/gh-projects.md` | already canonical — lag warning added |
| Executing an existing backlog item | `execute-backlog` | unchanged; it links the recipes above |
| OpenSpec lifecycle and `validate --strict` semantics | `openspec` | unchanged; claims probed clean |
| Rite gates and their enforcement layer | `openspec-drivezone` | unchanged; claims probed clean |

## Risks / Trade-offs

- [The release table hardcodes this repo's `releaseRules` as an example] → it is labelled as this
  catalog's config and the rule above it says to read `.releaserc.json` before assuming.
- [Advising `fix` for security changes loses the `security` type's signal] → the emoji, scope and body
  carry it; shipping the fix matters more than the taxonomy.
- [The probe is a point-in-time result] → it names the tool versions it ran against, so a future
  reader can tell whether it still applies.
