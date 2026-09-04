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

The enforcement artifact SHALL carry a self-test, exercised by the repository's own CI, that fixes
the decisions its design already assumes — what fires, what stays silent, and where the spec
sentence is appended — so that an edit to its signal list is measured rather than trusted. A
deliberately accepted false positive SHALL be fixed in that self-test as a case that fires, with the
recorded decision cited beside it, so that a well-meant correction cannot revert it unread. A
payload that is not a JSON object SHALL be ignored: the artifact exits zero with no output and no
traceback, because a hook that crashes on malformed input costs the turn it was meant to inform.

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

#### Scenario: The shipped hook carries a self-test and a malformed payload is ignored

- **WHEN** the hook is run with `--selftest`
- **THEN** it prints one OK/FAILED line per fixed decision plus a summary line and exits non-zero
  when any decision regressed, and the repository's CI runs that mode as a blocking step
- **AND** the case list includes a diagnostic question containing a change word as a case that
  fires, citing the decision that accepted the false positive
- **AND** when the payload on stdin is a JSON array, a JSON string or empty, the hook exits zero
  with no output and no traceback

### Requirement: The grounding rite is carried into context on correction

The catalog SHALL ship an enforcement artifact that re-injects the anti-guessing doctrine when a
prompt indicates a guess was caught or research is being demanded, in both of the catalog's working
languages. The artifact SHALL inform rather than block: it never denies a tool call, it persists
nothing, it needs no credentials, and an explicit waiver silences it.

The artifact SHALL state which moment it does **not** cover, and the documentation SHALL name the
layer that enforces evidence when the artifact is not wired, so that a reader does not mistake a
per-session convenience for a gate.

The artifact SHALL carry a self-test, exercised by the repository's own CI, that fixes the decisions
its design already assumes — a caught guess fires in each working language, a waiver silences, a
correction typed inside a slash command still fires, an implementation request stays silent — so
that an edit to its signal list is measured rather than trusted. A payload that is not a JSON object
SHALL be ignored: the artifact exits zero with no output and no traceback.

#### Scenario: A caught guess carries the doctrine into the turn

- **WHEN** a prompt says the assistant invented something, demands a source, asks where a fact came
  from, states that a flag or option does not exist, or says the work was out of scope
- **THEN** the hook injects the research ladder, the labelling rule, the not-found rule and the scope
  rule into that turn's context

#### Scenario: The reminder is silent when the user waives it

- **WHEN** the prompt explicitly permits an unverified answer
- **THEN** the hook produces no output, because the rite is the user's to waive

#### Scenario: The uncovered moment is declared, not implied

- **WHEN** the artifact is documented
- **THEN** the documentation states that it fires on corrections rather than on the guess itself,
  that no prompt regex can observe the moment a model is about to guess, and that the artifact does
  not run in CI or for a contributor who has not wired it

#### Scenario: The shipped hook carries a self-test and a malformed payload is ignored

- **WHEN** the hook is run with `--selftest`
- **THEN** it prints one OK/FAILED line per fixed decision plus a summary line and exits non-zero
  when any decision regressed, and the repository's CI runs that mode as a blocking step
- **AND** the case list fixes that a correction typed inside a slash command still fires, which is
  the opposite of the backlog hook's rule and is deliberate
- **AND** when the payload on stdin is a JSON array, a JSON string or empty, the hook exits zero
  with no output and no traceback
