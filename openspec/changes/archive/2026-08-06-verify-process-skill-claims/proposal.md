# Change: Probe the process skills' CLI claims, and document what release types actually ship

## Why

Six skills (`openspec`, `openspec-drivezone`, `backlog`, `execute-backlog`, `conventional-commit`,
`claude-statusline`) instruct the agent to run external CLIs. `skills-authoring` requires those claims
to be verified, and they never had been.

Every command and flag was extracted from their code blocks and inline code and probed against the
installed tools — **28 distinct claims against `gh 2.92.0` and `openspec 1.6.0`: all subcommands exist
and every flag appears in its help output. Zero problems.** That is a negative result and it is
reported as one; no edits were manufactured from it.

Two real defects surfaced from actually *using* these skills, not from reading them:

**1. `conventional-commit` lists twelve types and never says which ones ship.** Under the
`conventionalcommits` preset only `feat`, `fix` and `perf` cut a release. The table's `security` row
is the trap: it is not a preset type, so `🔒 security(auth): rotate leaked token` produces **no
release and no changelog entry** — a security fix sits unreleased on the default branch while the
author believes it shipped.

Verified against this repo's own history rather than the preset docs:

| commit | release |
|---|---|
| `🐛 fix(r3f): make the code blocks compile…` (#26) | v2.0.1 |
| `✅ ci(skills): enforce the authoring rules…` (#29) | none |
| `📝 docs(openspec): archive…` (#27, #30) | none |

The skill also omits the repo's own `releaseRules` overrides — `refactor` → patch and a catalog-
specific `skill` type → minor — so a contributor following the skill cannot predict the outcome.

**2. `backlog` has the right recipe but not the reason.** Its `gh-projects.md` already says to capture
the item id from `item-add --format json --jq .id`. It does not say what happens if you look it up
again instead: a freshly added item is **not yet visible to `gh project item-list`**, so the follow-up
`item-edit` fails with `Could not resolve to a node with the global id of ''`. The identical id
resolves fine once the board catches up. Hit live while filing #28.

## What Changes

- `conventional-commit` → 1.3.0:
  - Type table gains a **release impact** column, with `!`/`BREAKING CHANGE` called out as major.
  - New section on the two traps: `security` ships nothing (type a shippable security fix as `fix`),
    and `ci`/`test`/`build`/`style`/`revert` ship nothing either.
  - New section on repo-specific `releaseRules` overrides, with this catalog's as the worked example
    (`refactor` → patch, `skill` → minor, `docs`/`chore` → none).
  - Notes that the release tooling treats the gitmoji as optional (`headerPattern` skips a leading
    non-word prefix) while this convention still requires it — the emoji never replaces the type.
- `backlog` → 1.0.1: `references/gh-projects.md` states the propagation lag and the exact error it
  produces, next to the recipe that avoids it.
- `openspec` → 1.1.0: states that every change needs a delta, that a correction should be expressed as
  `## MODIFIED Requirements` rather than a near-duplicate `## ADDED` one, and that the `skip_specs`
  escape hatch the CLI advertises does not work on 1.6.0.

**3. `openspec` repeats a CLI escape hatch that the CLI does not honour.** A change with no spec
delta fails validation. The validator's own error message suggests setting `skip_specs: true` in the
change's `.openspec.yaml`; probed on CLI 1.6.0, **neither `skip_specs` nor `skipSpecs` has any
effect**. Hit while writing this very change.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: MODIFIED **Versioned external APIs are pinned** — extended to command-line
  tools, requiring prescribed subcommands and flags to be probed against the installed tool and the
  probed version recorded, and requiring tool guidance contradicted by the tool itself to be corrected
  rather than repeated.

## Impact

- `skills/conventional-commit/SKILL.md`, `skills/backlog/references/gh-projects.md`, regenerated
  wrappers.
- Anyone typing a security fix as `security` in a semantic-release repo now learns it will not ship.
- No change to the other three probed skills (`openspec-drivezone`, `execute-backlog`,
  `claude-statusline`): their CLI claims verified clean.
