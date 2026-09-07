## ADDED Requirements

### Requirement: Plugin groups are project domains, not skill subjects

A published plugin group SHALL be the **project domain that installs it**, not the subject the skills
share. Two skills SHALL share a group only when a project that wants one wants the other.

The test is about installation, not taxonomy: if repositories commonly install one of two skills and
not the other, they belong to different groups. Grouping by subject is what produces a plugin whose
consumer cannot refuse half of it, because a skill installed through a plugin cannot be disabled
individually — the assistant's per-skill visibility setting does not apply to plugin skills, and
disabling operates on the whole plugin.

The rule SHALL also say when NOT to split: a group is not divided because two skills merely differ in
topic, only because a real project takes one without the other. A catalog of one plugin per skill
publishes the same noise from the other direction.

When a skill serves two domains, it SHALL be placed in the domain whose projects always need it, and
the other domain's skills SHALL link to it rather than a copy being published in both groups.

Renaming, splitting or narrowing a published group is a **breaking change** for every consumer whose
configuration names it. Such a change SHALL declare the migration where a consumer reads it, and the
release SHALL carry the breaking marker rather than shipping the rename as an ordinary update.

#### Scenario: A group that forces an unrelated domain on its consumers is refused

- **WHEN** a plugin group would ship a skill whose domain the installing project does not have —
  a server-operations skill inside the group a web project installs for its cluster manifests
- **THEN** the composition is a defect, because the consumer cannot disable that skill without
  disabling the group
- **AND** the skill moves to the group whose projects actually install it

#### Scenario: A group is not split on topic alone

- **WHEN** two skills in one group differ in topic but no project takes one without the other
- **THEN** they stay in the same group, because the test is installation and not subject

#### Scenario: A renamed or narrowed group declares its migration

- **WHEN** a published group is renamed, split, or loses a skill
- **THEN** the change publishes the old-to-new mapping where a consumer reads it, and the release
  carries the breaking marker
- **AND** no duplicate group is published to keep the old name alive, because two groups shipping
  copies of the same skills contradict the single-canonical-source law the catalog is built on

#### Scenario: The grouping rule is checked against the tree, not against intent

- **WHEN** a change alters which skills a group publishes
- **THEN** the acceptance evidence is the list of skills under each group in the tree, and the
  published description derived from it, rather than a statement that the grouping is now correct
