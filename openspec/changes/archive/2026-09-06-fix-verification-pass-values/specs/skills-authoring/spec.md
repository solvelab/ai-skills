## MODIFIED Requirements

### Requirement: A prescribed verification states what passes

A skill that tells the reader to verify a step SHALL state the value that passes, not only the
command and the output it prints. A verification whose expected result is satisfied by any run of the
command does not verify; it reassures, which is worse than no verification because it consumes the
reader's attention and returns nothing.

Where one command's output distinguishes failures that need opposite remedies, the skill SHALL
prescribe a table mapping each observable result to its meaning, rather than a single "expected"
line that can only describe the success case.

This applies to a skill's **examples** as much as to its instructions: an example is what a reader
copies, so an expected-output line written there is a prescription. A stated result that describes an
**absence** — "without errors", "no failures", "cleanly" — is not a passing value, because nothing
observable distinguishes it from a run that failed in a way the reader did not think to look for.

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

#### Scenario: An example carries the same obligation as an instruction

- **WHEN** a skill's reference examples show a command followed by an expected-output line
- **THEN** that line names an observable value, because a reader imitates the example rather than
  re-deriving the rule from the skill body

#### Scenario: An absence is not a passing value

- **WHEN** a prescribed result is stated as the absence of a problem — "without errors", "no
  failures", "disappears cleanly"
- **THEN** it is rewritten to name what the reader sees when the step succeeded: the lines that
  appear, the segments that are gone, the exact string printed
