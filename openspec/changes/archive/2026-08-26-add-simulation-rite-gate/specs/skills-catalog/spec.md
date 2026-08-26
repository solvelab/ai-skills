## ADDED Requirements

### Requirement: The rite gates proof that the artifact was exercised

The repository's spec-driven rite SHALL require every active change to record that the artifact it
touches was **run through the path its user takes**, before the change can be closed. Reading,
probing, uniform frontmatter and a green strict validation SHALL NOT be treated as proof of delivery:
each of them can hold while the artifact has never been executed once.

The record SHALL live in its own mandatory task group, positioned before the quality-review group so
that what the simulation finds is available to the review that follows it, and its presence SHALL be
enforced by the same script that enforces the other mandatory groups, because the OpenSpec CLI
validates delta-spec format only.

The group's boxes SHALL be checked in **shape**, per kind rather than uniformly, following the
measurement that already rejected a uniform rule for the evidence group: an entry point together with
an observed output fragment; a case matrix expressed as counts; and what escaped, or an explicit
statement that nothing did. A change that touches no runtime artifact SHALL satisfy the group by
stating that explicitly, so that documentation-only work is never pushed into inventing a simulation.

The gate SHALL declare, in its own header, that it proves the record's shape and never its honesty —
a box filled with invented output passes it, and the reviewer is what judges the content.

#### Scenario: A change that ships a runtime artifact records its exercise

- **WHEN** an active change touches a skill, a hook or a shipped script
- **THEN** its task list carries the simulation group, naming the entry point that was exercised and a
  fragment of the output that was observed
- **AND** the counts of the case matrix are recorded — what had to fire and did, what had to stay
  silent and did, and which known escapes stayed silent

#### Scenario: A documentation-only change closes the group explicitly

- **WHEN** an active change touches no runtime artifact
- **THEN** the group is satisfied by stating that explicitly
- **AND** the change is not required to invent a simulation, because a padded record is worth less
  than an honest absence

#### Scenario: A missing or misplaced group fails the gate

- **WHEN** an active change's task list lacks the simulation group
- **THEN** the rite gate fails with a file-specific error naming the missing group
- **AND** the first-group and last-group rules of the existing mandatory groups are unchanged

#### Scenario: A ticked box that states a conclusion instead of an observation fails

- **WHEN** a box in the simulation group is ticked without naming an entry point and an observed
  output, without counts, or without naming an escape or declaring none
- **THEN** the evidence gate reports a file-specific finding naming the box and what is missing

#### Scenario: The shipped catalog validator is a gate, not a suggestion

- **WHEN** continuous integration validates this repository's plugins and skills with the vendor's
  own validator
- **THEN** the step fails the build on a finding, and pins the validator's version, so that a gate is
  neither silently disabled nor broken by an upstream release
