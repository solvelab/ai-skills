## ADDED Requirements

### Requirement: A prescribed verification states what passes

A skill that tells the reader to verify a step SHALL state the value that passes, not only the
command and the output it prints. A verification whose expected result is satisfied by any run of the
command does not verify; it reassures, which is worse than no verification because it consumes the
reader's attention and returns nothing.

Where one command's output distinguishes failures that need opposite remedies, the skill SHALL
prescribe a table mapping each observable result to its meaning, rather than a single "expected"
line that can only describe the success case.

#### Scenario: A version probe names the version that passes

- **WHEN** a skill prescribes a command whose purpose is to establish that a dependency is present at
  a supported version
- **THEN** the prescribed step states the minimum or the range that passes, so that a reader running
  it against an unsupported version fails the step instead of continuing

#### Scenario: An expected output that any run satisfies is a defect

- **WHEN** the expected result of a prescribed verification is a shape the command prints regardless
  of whether the underlying condition holds
- **THEN** it is treated as a missing criterion and rewritten to name the passing value, because the
  step as written cannot fail

#### Scenario: Opposite remedies get a table, not a line

- **WHEN** one prescribed command has results that mean different failures and call for different
  fixes
- **THEN** the skill maps each result to its meaning and its remedy in a table, instead of naming
  only the success case and leaving the reader to guess which failure they hit

#### Scenario: The criterion is reviewed by hand, and that is declared

- **WHEN** a skill adds or edits a prescribed verification
- **THEN** the criterion is reviewed by a human, and the skill's change records that no validator
  covers this rule, because distinguishing a criterion from a shape description in prose is a
  judgement a checker would get wrong in both directions
