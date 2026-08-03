## ADDED Requirements

### Requirement: Prescribed numbers carry the rule that produces them

A skill that prescribes numeric configuration SHALL publish the rule, formula or computation the
target system uses, so an adopter can derive and audit the values instead of copying them. A
configuration snapshot taken from a running deployment SHALL NOT be presented as a validated
baseline unless it has been re-derived from that rule; "it works in production" is not derivation,
because a defect that only manifests beyond the conditions reached in production looks identical to
a correct value.

Where the target system can compute the value itself, the skill SHALL say so and SHALL prefer that
over hardcoded constants.

A prescribed block SHALL NOT mix settings from different domains under one heading when the system's
own schema groups them together; a setting whose effect lies outside the section's subject SHALL be
called out separately, with the effect named.

#### Scenario: Baseline copied from a deployment

- **WHEN** a skill documents configuration values observed on a working production system
- **THEN** each value is either derived from the published rule or marked as an unverified
  observation, and values that only hold for that deployment's scale are labelled with the
  conditions they were verified under

#### Scenario: The system can derive the value itself

- **WHEN** the target system computes a sane default when a setting is left empty or zero
- **THEN** the skill recommends that default and shows the computation, rather than prescribing a
  constant that silently diverges as the surrounding configuration changes

#### Scenario: A setting is filed under a misleading heading

- **WHEN** the system's schema groups a setting with unrelated ones (for example, an access limit
  nested under a performance-tuning block)
- **THEN** the skill documents its real effect separately from the block, so a reader tuning that
  block does not carry the setting along by copy-paste
