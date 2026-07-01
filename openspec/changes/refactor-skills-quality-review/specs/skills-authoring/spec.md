## ADDED Requirements

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
