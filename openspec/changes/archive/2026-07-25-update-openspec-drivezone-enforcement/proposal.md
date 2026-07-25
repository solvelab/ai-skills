# Change: Correct enforcement claim in openspec-drivezone and document the hard rite-gate pattern

## Why

`skills/openspec-drivezone/SKILL.md` states the forked schema turns three disciplines into "mandatory
gates the `validate --strict` step refuses to skip" — empirically false on OpenSpec CLI 1.6.0: a probe
change with tasks.md missing every gate group passed strict validation (2026-07-25, this repo). The
skill promises a guarantee the CLI does not deliver, misleading every adopter of the rite.

## What Changes

- Correct the enforcement claim in `skills/openspec-drivezone/SKILL.md` (frontmatter description,
  Part 1 and Part 2): forked-schema gates are advisory at the CLI level — they flow into `/opsx`
  artifact generation via `openspec instructions`, but `validate --strict` checks delta-spec format
  only.
- Document the hard-gate pattern that actually enforces the rite: a repo-local validation script
  (canonical example: `scripts/validate-rite.sh` in solvelab/ai-skills) wired as a CI step, greping
  the mandatory headings in every active change and running `openspec validate --all --strict`.
- Bump `metadata.version` 2.0.0 → 2.1.0 and regenerate all tool wrappers via `./generate.sh`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — claims a skill makes about external tool behavior SHALL be
  empirically verified, and enforcement mechanisms SHALL state where they are actually enforced.

## Impact

- `skills/openspec-drivezone/SKILL.md` + regenerated wrappers (`claude/`, `codex/`, `cursor/`,
  `copilot/`, `plugins/`).
- Affected skill consumers: DriveZone repos adopting the rite (deploying the script there is out of
  scope — org DriveZoneFivem board).
- Resolves solvelab/ai-skills#15.
