## ADDED Requirements

### Requirement: The adversarial rite separates enumerating, generating and scoring

The catalog's adversarial-testing rite SHALL distinguish three activities rather than presenting one:
**enumerating** the scenarios an author can list, **generating** inputs from a stated invariant, and
**scoring** whether the resulting suite would notice the defect. Enumeration is the default and
always applies; each of the other two SHALL carry the condition under which it pays and a ceiling
naming the trigger that would raise it, so a small change is not made to carry a technique sized for
a large one.

A technique SHALL NOT be prescribed on a number taken from outside this catalog. Its yield SHALL be
measured against code in this repository before publication, with the conditions of the measurement
stated, and a measurement that came out unfavourable SHALL be published as measured rather than
replaced by a citation.

#### Scenario: A generation technique is prescribed

- **WHEN** the rite prescribes generating inputs instead of listing them
- **THEN** it states the condition that makes the technique pay — a stateable invariant, not a
  category of code — and the ceiling at which enumeration remains sufficient
- **AND** it names what the technique yielded when it was measured here, including "no defects" when
  that is the measured result

#### Scenario: A scoring technique is prescribed

- **WHEN** the rite prescribes scoring an existing suite by breaking the code under it
- **THEN** the scope prescribed is the surface the change touched, not the repository
- **AND** the measurement that motivates the rule names the module, the suite, the tool version and
  the counts, so a reader can reproduce or refute it

#### Scenario: A prescribed technique carries the wrong command too

- **WHEN** the ecosystem's best-known tool for a prescribed technique fails or misleads under this
  catalog's conventions
- **THEN** the stack track names that command as the wrong one, with the failure it produces, beside
  the command that works
