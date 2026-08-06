## ADDED Requirements

### Requirement: No runtime is not an excuse

A skill whose subject cannot be exercised in the working environment SHALL still be audited by
reading its doctrine in full, by applying the adversarial defect classes from `bug-hunter`, and by
probing whatever part of its claims is publicly verifiable. Leaving such a skill at mechanical
validation only SHALL be recorded as a gap, never treated as complete.

#### Scenario: A public claim is probed even when the runtime is absent

- **WHEN** a skill pins a version, names an upstream target framework, or asserts that a type or API
  is present or absent in a runtime
- **THEN** the claim is checked against the public source (release tag, manifest, upstream file)
  before the skill is considered audited

#### Scenario: An internal contradiction is found without running anything

- **WHEN** two statements in the same skill cannot both hold — a prescribed default that violates a
  constraint stated elsewhere in the file
- **THEN** the contradiction is resolved against the probed evidence, and the losing statement is
  corrected rather than left for the runtime to expose

#### Scenario: An unaudited skill is reported, not silently counted as done

- **WHEN** an audit cannot reach a skill's subject at all
- **THEN** the coverage report names the skill and what is missing, instead of reporting a total that
  implies it was covered
