## ADDED Requirements

### Requirement: The rite gates evidence before it gates quality

The repository's spec-driven rite SHALL require every active change to open its task list with a
group recording what was probed: local paths opened rather than recalled, external tools, flags,
config keys, API names and versions checked against the installed version, and anything that could
not be probed written down as an open question rather than stated as fact. The group SHALL be the
first task group, and its presence and position SHALL be enforced by the same script that enforces
the other mandatory groups, because the OpenSpec CLI validates delta-spec format only.

Recorded evidence SHALL be a command together with a fragment of its raw output, never a conclusion,
so that a reviewer can re-run it. The enforcing script SHALL state that it verifies the presence and
position of the group and not the truth of its contents.

#### Scenario: A change without recorded evidence fails the build

- **WHEN** an active change's task list lacks the evidence group, or carries it somewhere other than
  the first task group
- **THEN** the rite gate script fails with a file-specific error naming the missing or misplaced
  group, and the build does not pass

#### Scenario: The gate declares what it cannot check

- **WHEN** the gate passes
- **THEN** the script's own header states that a ticked box with no probe behind it is
  indistinguishable from one with, so that a green run is not read as verified evidence

#### Scenario: A gate introduced mid-flight does not exempt existing work

- **WHEN** a new mandatory group is added while a change is already open
- **THEN** the open change is backfilled with the group in the same change that introduces the gate,
  rather than being added to an exemption list

### Requirement: The grounding rite is carried into context on correction

The catalog SHALL ship an enforcement artifact that re-injects the anti-guessing doctrine when a
prompt indicates a guess was caught or research is being demanded, in both of the catalog's working
languages. The artifact SHALL inform rather than block: it never denies a tool call, it persists
nothing, it needs no credentials, and an explicit waiver silences it.

The artifact SHALL state which moment it does **not** cover, and the documentation SHALL name the
layer that enforces evidence when the artifact is not wired, so that a reader does not mistake a
per-session convenience for a gate.

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
