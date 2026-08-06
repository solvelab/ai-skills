## ADDED Requirements

### Requirement: Authoring rules are machine-enforced

The mechanically checkable authoring rules SHALL be enforced by a script wired into CI, and that
script SHALL carry a self-test that injects one known defect per check and asserts detection. Rules
that cannot be checked mechanically SHALL be identified as review-only rather than left to imply
coverage.

#### Scenario: A violation fails the build

- **WHEN** a change introduces a broken reference, an unparseable code block, a mistagged fence, or a
  description that contradicts its body
- **THEN** the CI validate job fails and names the skill, the check and the offending content

#### Scenario: A disabled check is caught

- **WHEN** a change to the validator silently stops one of its checks from firing
- **THEN** the self-test fails, because a catalog with zero findings and a check that cannot fire are
  otherwise indistinguishable

#### Scenario: A missing tool is reported, not passed over

- **WHEN** a checker dependency is unavailable in the environment
- **THEN** the affected check is reported as skipped in the output instead of counting as a pass
