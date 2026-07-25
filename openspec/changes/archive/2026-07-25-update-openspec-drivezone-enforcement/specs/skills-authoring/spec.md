## ADDED Requirements

### Requirement: Verified enforcement claims

Any claim a skill makes about external tool behavior (CLI validation, runtime checks, generated
output) SHALL be empirically verified before publication, and every enforcement mechanism the skill
describes SHALL state where enforcement actually happens (tool-level, script, CI, or convention-only).

#### Scenario: Tool-behavior claim is probe-tested

- **WHEN** a skill states that a tool blocks, validates, or refuses an input
- **THEN** the claim is backed by a reproducible probe against the tool version in use, and the skill
  names the enforcing layer explicitly

#### Scenario: Advisory mechanisms are not sold as hard gates

- **WHEN** a mechanism only guides generation or relies on convention (e.g. schema templates feeding
  artifact scaffolding)
- **THEN** the skill labels it advisory and points to the structural gate (script/CI) that makes it
  mandatory, or states that none exists
