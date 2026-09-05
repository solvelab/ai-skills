## ADDED Requirements

### Requirement: Version-scoped rules move with the pin

A rule in a skill that holds only for a range of versions of the tool or runtime the skill targets
SHALL state that range next to the rule, and SHALL be lifted or re-scoped in the same change that
moves the skill's `Verified against` pin out of that range. A rule written as timeless whose premise
is a version fact is a defect once the pin moves.

#### Scenario: A ban that depends on the runtime names the runtime

- **WHEN** a skill forbids a construct because the pinned runtime lacks a type, API or behaviour
- **THEN** the rule names the runtime range in which that premise holds, rather than presenting the
  ban as unconditional

#### Scenario: Moving the pin re-derives the scoped rules

- **WHEN** a change moves a skill's `Verified against` pin to a version where a scoped rule's premise
  no longer holds
- **THEN** that change lifts or re-scopes the rule and records the probe that decided it, instead of
  carrying the rule forward unchanged

#### Scenario: A replicated rule moves everywhere it lives

- **WHEN** the scoped rule is also cited as an example in another skill (a bug-hunter track, a
  checklist)
- **THEN** the same change scopes the example there, so the two skills do not disagree about the
  same runtime
