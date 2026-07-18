## ADDED Requirements

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
