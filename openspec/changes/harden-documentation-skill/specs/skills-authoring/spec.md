## ADDED Requirements

### Requirement: Description agrees with body

A skill's frontmatter `description` SHALL NOT state a policy that its body contradicts. The
description is loaded into every session and drives skill selection, so a conflict there is resolved
by the model, not by the author.

#### Scenario: Conflicting policy is caught before publication

- **WHEN** a skill's description asserts a behaviour ("always creates X", "never does Y") that a rule
  in the body qualifies or reverses
- **THEN** the conflict is resolved to a single policy and stated once, in the body, with the
  description summarizing it rather than restating a stronger claim

#### Scenario: Behavioural promises are attributed to the governing rule

- **WHEN** a skill's output set depends on a condition (a decision table, a detected file, a user
  request)
- **THEN** the description names the condition rather than promising an unconditional result
