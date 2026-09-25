## MODIFIED Requirements

### Requirement: Authoring rules are machine-enforced

The mechanically checkable authoring rules SHALL be enforced by a script wired into CI, and that
script SHALL carry a self-test that injects one known defect per check and asserts detection. Rules
that cannot be checked mechanically SHALL be identified as review-only rather than left to imply
coverage. A check that covers only **part** of its rule SHALL state the uncovered part in the check
itself, so that a passing run is not read as full coverage.

Conformance with an external standard the catalog claims SHALL be measured by two independent
paths: the catalog's own check, which the self-test can break on purpose, and the standard's
reference validator, pinned to an exact version and run over every skill in CI. The pin SHALL carry
the reason it exists next to it, because a blocking gate on an unpinned upstream fails the build on
someone else's release schedule.

The cross-reference rules — every reference file reachable from `SKILL.md`, no path that resolves
only in a full checkout, every description carrying a boundary clause — SHALL be among the checks
the script enforces, each with its own injected defect in the self-test and its uncovered part
declared in the check.

A detector a skill ships under its own `references/` for consumers to run SHALL be held to the same
rules as the catalog's validators: its self-test SHALL run in CI. A defect found in the field that
such a detector did not report SHALL enter its self-test as an injected case before the fix is made,
so the self-test fails first and a later regression of the fix is caught by it.

#### Scenario: A violation fails the build

- **WHEN** a change introduces a broken reference, an unparseable code block, a mistagged fence, a
  description that contradicts its body, or a `description` or `compatibility` longer than the
  standard allows
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

#### Scenario: The frontmatter-limits check is itself gated

- **WHEN** the self-test injects a `description` of more than 1024 parsed characters into a copy of
  the catalog
- **THEN** the validator reports the frontmatter-limits check for that skill, and a validator that
  stays silent fails the self-test

#### Scenario: The reference validator runs pinned, over every skill

- **WHEN** the CI validate job runs
- **THEN** the standard's reference validator, installed at an exact pinned version, is executed
  once per `skills/<name>/` directory and any finding fails the job, and the step states what the
  reference validator covers and what it leaves to the catalog's own checks

#### Scenario: The cross-reference checks are themselves gated

- **WHEN** the self-test injects, into a copy of the catalog, a `*.md` under `references/` that no
  file links, a `<other-skill>/references/<file>` path without the `skills/` prefix, and a
  description with neither a "Do NOT use" clause nor a redirect naming a sibling skill
- **THEN** the validator reports the orphan-reference (C11), out-of-skill-path (C12) and
  anti-trigger-clause (C13) checks respectively, each check states in its own text the exact phrase
  list or path forms it judges and what it leaves to review, and a validator silent on any of the
  three fails the self-test

#### Scenario: A detector shipped inside a skill is gated in CI

- **WHEN** a skill ships a detector with `--selftest` under `references/`
- **THEN** the CI validate job runs that self-test, and a self-test that no job runs counts as a
  missing gate rather than as coverage

#### Scenario: A field miss becomes an injected case

- **WHEN** a consumer repository finds a defect a shipped detector should have reported and did not
- **THEN** the defect enters the detector's self-test as an injected case that fails before the fix
  and passes after it, and the rule text states any limit the fix leaves in place
