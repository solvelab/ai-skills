## ADDED Requirements

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
