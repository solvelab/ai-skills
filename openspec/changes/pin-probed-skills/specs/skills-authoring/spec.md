## MODIFIED Requirements

### Requirement: Authoring rules are machine-enforced

The mechanically checkable authoring rules SHALL be enforced by a script wired into CI, and that
script SHALL carry a self-test that injects one known defect per check and asserts detection. Rules
that cannot be checked mechanically SHALL be identified as review-only rather than left to imply
coverage. A check that covers only **part** of its rule SHALL state the uncovered part in the check
itself, so that a passing run is not read as full coverage.

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

#### Scenario: Partial coverage is declared, not implied

- **WHEN** a check enforces its rule only under some condition (a size threshold, a file type, a
  language it can parse)
- **THEN** the condition and what escapes it are stated in the check, and skills falling outside it
  are reviewed by hand rather than assumed compliant
