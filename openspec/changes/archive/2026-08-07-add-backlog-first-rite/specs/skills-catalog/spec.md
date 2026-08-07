## ADDED Requirements

### Requirement: The development rite is enforced outside the model's discretion

The catalog SHALL state, in its portable global rules, that every code change starts as a backlog
item, and SHALL ship an enforcement artifact that fires without depending on the assistant noticing
the rule. The artifact SHALL inform rather than block: it never denies a tool call, and the user can
always waive the rite explicitly. Diagnosing, reading and answering SHALL remain unrestricted — the
rite applies only when code is going to change.

#### Scenario: A code-change request carries the rite into context

- **WHEN** a prompt asks for an implementation, fix, refactor or removal
- **THEN** the shipped `UserPromptSubmit` hook injects the rite reminder naming `/backlog` as the
  entry point and `/execute-backlog` as the second step
- **AND** the reminder states that diagnosis is free and that an approved plan is not a waiver

#### Scenario: The reminder is silent inside its own rite

- **WHEN** the prompt is already a rite command (`/backlog`, `/execute-backlog`), another slash
  command, or contains an explicit waiver
- **THEN** the hook produces no output, so the reminder never fires against the flow it enforces

#### Scenario: Plan approval is not a bypass

- **WHEN** an assistant finishes planning and the plan is approved
- **THEN** the rule as stated in the global rules requires the work to become a backlog item before
  the first edit, because approving a plan approves the plan and not the skipping of the rite

#### Scenario: The enforcement artifact persists nothing

- **WHEN** the shipped hook runs
- **THEN** it reads the prompt payload, matches, prints and exits, writing no state outside the
  repository and requiring no credentials

### Requirement: The backlog skills declare their place in one rite

The `backlog` and `execute-backlog` descriptions SHALL identify each other as the two halves of a
single flow — creation then execution — so that a reader arriving at either one learns where the
work came from and where it goes next. Neither description SHALL restate the other's workflow.

#### Scenario: Entry point is discoverable from the execution skill

- **WHEN** a user reads the `execute-backlog` description
- **THEN** it names `backlog` as the step that produces the item it consumes

#### Scenario: Exit is discoverable from the creation skill

- **WHEN** a user reads the `backlog` description
- **THEN** it names `execute-backlog` as the step that turns the created item into a pull request
