## MODIFIED Requirements

### Requirement: Checklists are scored against field defects

A skill that prescribes a checklist or a rite SHALL be scored against defects actually found in the
field, and every class the checklist would have missed SHALL be added together with the defect that
earned it. A checklist item without a traceable origin SHALL NOT be added.

A skill that prescribes a **step** SHALL also give the command that performs it whenever a plausible
wrong command exists, and SHALL name the wrong one. A step stated without a method is executed by
whatever command looks obvious, which is how a wrong one becomes the de facto instruction.

#### Scenario: A missed class is added with its provenance

- **WHEN** a defect is found by some means other than the checklist that claims to cover its area
- **THEN** the class it belongs to is added to the checklist, recorded with the defect that earned it
- **AND** an item that cannot name the defect behind it is removed rather than kept

#### Scenario: The scoring is stated, not implied

- **WHEN** a checklist is revised after an audit
- **THEN** the change records which defects were scored against it and which of them it would have
  caught as previously written

#### Scenario: A prescribed step carries its command

- **WHEN** a step instructs the agent to check, resolve or look something up, and more than one
  command could plausibly do it
- **THEN** the correct command is given, and any plausible-but-wrong alternative is named as forbidden
  with the failure it produces
