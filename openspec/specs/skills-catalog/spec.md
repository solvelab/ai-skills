# skills-catalog Specification

## Purpose
TBD - created by archiving change refactor-skills-quality-review. Update Purpose after archive.
## Requirements
### Requirement: Catalog composition after the quality review

The skills catalog SHALL contain 20 skills: the 17 retained/edited skills plus `backend-resilience`,
`openspec`, and `r3f-assets`, with `r3f-loaders` and `r3f-textures` removed (superseded by `r3f-assets`).

#### Scenario: npx discovery lists the full catalog

- **WHEN** `npx skills add <repo> --list` runs against the repository root
- **THEN** exactly 20 skills are discovered, including `backend-resilience`, `openspec` and `r3f-assets`
- **AND** `r3f-loaders` and `r3f-textures` are absent

### Requirement: Generic doctrine is reusable outside FiveM

Dependency-resilience doctrine SHALL live in `backend-resilience` (stack-agnostic principles with Python
examples) and adversarial-testing methodology SHALL live in `bug-hunter`'s stack-agnostic SKILL.md, so
non-FiveM projects can adopt them without pulling FiveM content.

#### Scenario: Python project adopts resilience patterns

- **WHEN** an agent working on a Python REST project needs fallback/negative-cache/retry guidance
- **THEN** `backend-resilience` provides the complete doctrine with no FiveM/Lua prerequisites
- **AND** `fivem-fallback` contains only the FiveM/Lua adaptation and links to `backend-resilience`

#### Scenario: Adversarial testing on a non-DriveZone stack

- **WHEN** an agent runs the bug-hunter rite on a project that is neither pytest nor FiveM
- **THEN** the SKILL.md mindset, universal checklist and output contract apply as-is
- **AND** stack specifics are opt-in reference files (`references/track-python-pytest.md`,
  `references/track-fivem-lua.md`)

### Requirement: r3f asset loading is a single skill

Model loading, texture loading/configuration and Suspense/caching patterns SHALL be covered by one
skill, `r3f-assets`.

#### Scenario: Texture task routes unambiguously

- **WHEN** a task involves loading textures or GLTF models in React Three Fiber
- **THEN** exactly one skill description (`r3f-assets`) claims that territory

### Requirement: Backlog item creation skill

The catalog SHALL provide a `backlog` skill that turns a natural-language idea into a structured
GitHub issue added to a configured GitHub Project v2 with fields filled, using only per-target
config files (repo `.github/backlog.yml` or workspace-root `backlog.yml`) and the user's own `gh`
CLI authentication. The skill SHALL contain no user-, org- or project-specific data.

#### Scenario: Repo mode creation

- **WHEN** `/backlog <idea>` runs inside a git repository containing `.github/backlog.yml`
- **THEN** the skill drafts a structured issue enriched with real repository context, shows a
  preview, and only after approval creates the issue in that repository and adds it to the
  configured Project with mapped fields set

#### Scenario: Workspace mode creation

- **WHEN** `/backlog <idea>` runs in a directory that is not a git repository but contains multiple
  repositories of one org, with `backlog.yml` at its root
- **THEN** the skill analyzes which repositories the idea affects, includes an Affected
  repositories section, and creates the issue in the primary affected repository (or the
  `issues_repo` override), adding it to the org's configured Project

#### Scenario: Missing Project scopes abort cleanly

- **WHEN** the authenticated `gh` token lacks the `project` scope
- **THEN** the skill stops before any write, printing the exact
  `gh auth refresh -s project,read:project` remediation

#### Scenario: First run without config launches the wizard

- **WHEN** `/backlog <idea>` runs where no config file exists
- **THEN** the skill discovers the owner from git remotes, lists that owner's Projects, maps fields
  by name after the user picks one, and writes the config file before proceeding

### Requirement: Backlog execution skill

The catalog SHALL provide an `execute-backlog` skill that takes an existing GitHub issue (number,
URL or search term), validates it is executable, presents an implementation plan for approval
before any code change, implements it on a dedicated branch following the target repo's
conventions, runs the repo's discoverable validations, opens pull request(s) linking the issue,
and updates the configured GitHub Project item — without ever merging, closing the issue directly,
or committing to the default branch.

#### Scenario: Plan approval gates implementation

- **WHEN** `/execute-backlog <n>` runs on a well-formed issue
- **THEN** the skill presents scope, affected files, test strategy and risks derived from the
  current codebase state
- **AND** no file is modified until the user approves the plan

#### Scenario: Incomplete item is not executed

- **WHEN** the referenced issue lacks scope or acceptance criteria, or contradicts the current
  codebase
- **THEN** the skill reports the gaps and asks whether to proceed anyway, refine the item first,
  or abort — it never fills missing scope by guessing

#### Scenario: Execution outcome is linked and tracked

- **WHEN** an approved plan is implemented and validations pass
- **THEN** a pull request referencing the issue (`Closes #n` on the primary repo) is opened from a
  dedicated branch
- **AND** the Project item moves to the configured review column
- **AND** the issue itself is not closed by the skill

#### Scenario: Workspace mode resolves affected repositories

- **WHEN** the issue contains an Affected repositories section and the skill runs in a workspace
- **THEN** work is orchestrated per affected repo (missing local clones offered via
  `gh repo clone`), with one PR per repo that changes

