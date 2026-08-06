## ADDED Requirements

### Requirement: Triggers live in the description, not the body

A skill SHALL NOT carry a `How to Use`, `Trigger Test Cases`, `Prompt` or `Usage` section in its
`SKILL.md`. Such a section is read only after the skill has already been selected, so it cannot
influence routing, and it costs context on every invocation. Trigger and anti-trigger information
SHALL live in the frontmatter `description`, which is what the model reads when choosing a skill.

#### Scenario: A trigger case not present in the description is folded in, not filed away

- **WHEN** a skill's body lists a trigger or anti-trigger case that its description does not cover
- **THEN** the case is added to the description, where it can affect selection
- **AND** the body section is removed rather than kept as a duplicate

#### Scenario: Every skill states where it does not apply

- **WHEN** another skill in the catalog covers an adjacent area
- **THEN** the description names it, either as an explicit "Do NOT use for … (that is `<skill>`)"
  clause or as a redirect ("for X use `<skill>`"), so the two do not compete for the same prompt
