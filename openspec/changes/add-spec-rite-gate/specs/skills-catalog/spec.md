## MODIFIED Requirements

### Requirement: The development rite is enforced outside the model's discretion

The catalog SHALL state, in its portable global rules, that every code change starts as a backlog
item, and SHALL ship an enforcement artifact that fires without depending on the assistant noticing
the rule. The artifact SHALL inform rather than block: it never denies a tool call, and the user can
always waive the rite explicitly. Diagnosing, reading and answering SHALL remain unrestricted — the
rite applies only when code is going to change.

In a repository that runs a spec-driven workflow, the rite SHALL NOT end at the backlog item. The
spec artifact SHALL be named by the same enforcement artifact that names the backlog step, and the
naming SHALL be conditional on that workflow being present, so that the reminder stays silent where
it does not apply. A repository whose spec policy is unstated SHALL be treated as requiring the
artifact, so that the absence of a decision is not read as permission to skip it.

The decision to ship without a spec artifact SHALL be a written one. A judgment made silently by the
assistant, or by a contributor in conversation, SHALL NOT satisfy the rite: the waiver SHALL exist as
a reviewable line in the pull request, and the gate SHALL be what reads it.

#### Scenario: A code-change request carries the rite into context

- **WHEN** a prompt asks for an implementation, fix, refactor or removal
- **THEN** the shipped `UserPromptSubmit` hook injects the rite reminder naming `/backlog` as the
  entry point and `/execute-backlog` as the second step
- **AND** the reminder states that diagnosis is free and that an approved plan is not a waiver

#### Scenario: The reminder names the spec rite only where it exists

- **WHEN** the prompt matches a code-change signal and the working directory carries the
  spec-driven workflow's directory
- **THEN** the reminder also names the spec artifact as a step that precedes the first edit outside
  that directory
- **AND** the same prompt in a working directory without that workflow produces the reminder without
  the spec sentence, so the added line never fires where it has no meaning

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

Where the target repository runs a spec-driven workflow, both skills SHALL carry the gate that
workflow imposes between them, and neither SHALL restate its lifecycle: the lifecycle has a canonical
home in the catalog's own spec-driven skill, and the backlog skills SHALL link to it. The creating
skill SHALL record the verdict — the artifact that will exist, or the written waiver — in the item
itself, so the executing skill inherits a decision instead of making a new one. The executing skill
SHALL re-check that verdict against the change it is about to make, SHALL raise it without asking
when the work outgrew the item, and SHALL NOT lower it without the user, because a silent downgrade
is the failure this gate exists to prevent.

The policy SHALL be the repository's to set rather than the skills', because both skills run against
repositories with different rites; a repository that states no policy while carrying the workflow
SHALL be treated as requiring the artifact.

#### Scenario: Entry point is discoverable from the execution skill

- **WHEN** a user reads the `execute-backlog` description
- **THEN** it names `backlog` as the step that produces the item it consumes

#### Scenario: Exit is discoverable from the creation skill

- **WHEN** a user reads the `backlog` description
- **THEN** it names `execute-backlog` as the step that turns the created item into a pull request

#### Scenario: The item carries its spec verdict

- **WHEN** the creating skill drafts an item for a repository that runs the spec-driven workflow
- **THEN** the drafted item declares either the change identifier and the capabilities its delta will
  touch, or the written waiver and its reason
- **AND** the verdict appears in the approval preview alongside the proposed field values

#### Scenario: The executing skill refuses to edit before the artifact exists

- **WHEN** the executing skill is about to change a file outside the spec-driven workflow's own
  directory, in a repository whose policy requires the artifact
- **THEN** it stops until the change exists and its strict validation is green, and the plan it
  presents for approval carries the change identifier, the affected capabilities and the validation
  output

#### Scenario: A verdict is raised silently and lowered only by the user

- **WHEN** re-analysis shows the work touches more than the item's waiver assumed
- **THEN** the executing skill raises the verdict to requiring an artifact without asking
- **AND** the reverse move — dropping a required artifact to a waiver — stops for an explicit user
  decision rather than being taken by the assistant

### Requirement: The rite gates evidence before it gates quality

The repository's spec-driven rite SHALL require every active change to open its task list with a
group recording what was probed: local paths opened rather than recalled, external tools, flags,
config keys, API names and versions checked against the installed version, and anything that could
not be probed written down as an open question rather than stated as fact. The group SHALL be the
first task group, and its presence and position SHALL be enforced by the same script that enforces
the other mandatory groups, because the OpenSpec CLI validates delta-spec format only.

Recorded evidence SHALL be a command together with a fragment of its raw output, never a conclusion,
so that a reviewer can re-run it. That rule SHALL be enforced in **shape**: a ticked box in the
evidence group SHALL be checked against the form its kind owes — a path opened together with the
commit or date it was read at; a probe together with a fragment of its output; a gap named or
explicitly declared absent — with a file-specific error naming the box and what is missing. The
rules SHALL be per box kind rather than uniform, because the kinds do not share a shape and a
uniform rule rejects boxes that are correct as written.

The gate SHALL cover the **absence** of a change and not only the shape of one that is present. A
gate whose checks are written as a loop over active changes passes vacuously when there are none,
which reads as approval of a pull request that recorded nothing. Therefore a pull request whose diff
touches paths outside the workflow's own directory SHALL be required to carry one of: an active
change, a change archived within the same diff, or a waiver line in the pull request body naming a
reason. Paths written by the release automation alone SHALL be exempt, and the check SHALL run only
where a base revision to compare against exists.

The waiver SHALL be treated as untrusted input: it is authored by whoever opened the pull request,
including from a fork, and SHALL be matched as text and never executed or interpolated into a
command.

Every enforcing script SHALL state that it verifies presence, position and shape, and **not the
truth of the contents**: a box padded to satisfy the shape passes, and no script can tell an
invented output from a real one. A script that also verifies that a change exists SHALL state that
existence is not honesty — a change scaffolded to satisfy the gate passes it.

The mandatory groups that are **not** gated on shape SHALL have their evidence density reported
without affecting the exit code, so that a group whose boxes carry no probe is visible to a reviewer
without reading the diff.

#### Scenario: A change without recorded evidence fails the build

- **WHEN** an active change's task list lacks the evidence group, or carries it somewhere other than
  the first task group
- **THEN** the rite gate script fails with a file-specific error naming the missing or misplaced
  group, and the build does not pass

#### Scenario: A pull request that records nothing fails the build

- **WHEN** a pull request's diff touches a path outside the workflow's own directory and carries
  neither an active change, nor a change archived in the same diff, nor a waiver line
- **THEN** the rite gate fails, naming the offending path, rather than passing because the loop over
  active changes found nothing to check

#### Scenario: The waiver is a written line, not a judgment

- **WHEN** the same diff is accompanied by a waiver line in the pull request body naming a reason
- **THEN** the gate passes and the reason is visible to the reviewer in the pull request itself
- **AND** the line is matched as text, never executed, because its author is whoever opened the pull
  request

#### Scenario: A ticked box that states a conclusion fails the build

- **WHEN** a ticked box in the evidence group records a conclusion instead of the form its kind owes
- **THEN** the gate fails, naming the box and the missing element
- **AND** the same box rewritten with a command and a fragment of its output passes

#### Scenario: The gate declares what it cannot check

- **WHEN** the gate passes
- **THEN** the enforcing scripts state that shape is not truth — a box padded to satisfy the rule is
  indistinguishable from an earned one — so that a green run is not read as verified evidence
- **AND** they state that the existence of a change is not the honesty of one

#### Scenario: A group that is reported rather than gated is not implied to be gated

- **WHEN** a mandatory group carries items that are judgments rather than executions
- **THEN** its evidence density is printed as a labelled report that never changes the exit code,
  and the check states that the group is reported and not gated, rather than demanding a command
  where none belongs

#### Scenario: A gate introduced mid-flight does not exempt existing work

- **WHEN** a new mandatory group is added while a change is already open
- **THEN** the open change is backfilled with the group in the same change that introduces the gate,
  rather than being added to an exemption list
