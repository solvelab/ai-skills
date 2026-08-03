# skills-authoring Specification

## Purpose

Conventions governing how every skill in this catalog is written, for human contributors and AI
agents alike: uniform frontmatter metadata, English as the catalog locale, a single canonical home
for each cross-cutting rule (siblings link instead of restating), and empirically verified claims
about external tool behavior. CI and the skills-rite Quality Gates enforce these requirements on
every change that touches `skills/`.
## Requirements
### Requirement: Single canonical home per rule

Every cross-cutting rule SHALL be defined in exactly one skill and referenced by link (with at most a
one-line summary) everywhere else. Canonical map: trust boundary → `fivem-lua`;
fallback/negative-cache/clamping → `backend-resilience`; REST negative-testing checklist →
`api-resilience-testing`; adversarial methodology → `bug-hunter`; OpenSpec lifecycle → `openspec`.

#### Scenario: Orchestrator skill references instead of restating

- **WHEN** `openspec-drivezone` describes its Fallback and Bug-Hunter gates
- **THEN** each gate row links to the canonical skill with a one-line summary
- **AND** no mechanism list from a sibling skill is reproduced inline

### Requirement: Uniform frontmatter metadata

Every `skills/<name>/SKILL.md` SHALL carry: `name` (== directory), `description` (folded block scalar),
`metadata.author: solvelab`, `metadata.version` (semver), `metadata.category` from the controlled set
{backend, testing, fivem, game, devops, docs, git, process}, `license: MIT`, and `compatibility`.

#### Scenario: CI rejects incomplete frontmatter

- **WHEN** a skill is added or edited without `metadata.version`, `license`, or with a category outside
  the controlled set
- **THEN** the CI validate job fails with a file-specific error

### Requirement: English as catalog locale

All skill content SHALL be written in English.

#### Scenario: Project-specific skill is still English

- **WHEN** a skill documents a project-specific workflow (e.g. `openspec-drivezone`)
- **THEN** its content is in English regardless of the project's working language

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

### Requirement: Prescribed numbers carry the rule that produces them

A skill that prescribes numeric configuration SHALL publish the rule, formula or computation the
target system uses, so an adopter can derive and audit the values instead of copying them. A
configuration snapshot taken from a running deployment SHALL NOT be presented as a validated
baseline unless it has been re-derived from that rule; "it works in production" is not derivation,
because a defect that only manifests beyond the conditions reached in production looks identical to
a correct value.

Where the target system can compute the value itself, the skill SHALL say so and SHALL prefer that
over hardcoded constants.

A prescribed block SHALL NOT mix settings from different domains under one heading when the system's
own schema groups them together; a setting whose effect lies outside the section's subject SHALL be
called out separately, with the effect named.

#### Scenario: Baseline copied from a deployment

- **WHEN** a skill documents configuration values observed on a working production system
- **THEN** each value is either derived from the published rule or marked as an unverified
  observation, and values that only hold for that deployment's scale are labelled with the
  conditions they were verified under

#### Scenario: The system can derive the value itself

- **WHEN** the target system computes a sane default when a setting is left empty or zero
- **THEN** the skill recommends that default and shows the computation, rather than prescribing a
  constant that silently diverges as the surrounding configuration changes

#### Scenario: A setting is filed under a misleading heading

- **WHEN** the system's schema groups a setting with unrelated ones (for example, an access limit
  nested under a performance-tuning block)
- **THEN** the skill documents its real effect separately from the block, so a reader tuning that
  block does not carry the setting along by copy-paste

