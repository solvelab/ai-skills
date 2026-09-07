## ADDED Requirements

### Requirement: Test order has a canonical home

The catalog SHALL contain one skill that governs **when** a test is written relative to the code it
covers: that for a change with behaviour worth naming, the first artifact written is a test that
fails for the right reason, and only then the implementation that makes it pass. The skill SHALL
state what makes such a test legitimate — that a test which passes before the implementation exists
tests nothing — and SHALL state the boundaries a stated requirement earns their own cases: the
empty input, the inclusive or exclusive edge, the zero, the value that cannot be parsed.

The skill SHALL state when the cycle does **not** apply, so that it does not read as a mandate to
grow a suite: a trivial one-liner, a change with no behaviour to name, and any work the floor of
one runnable check already covers. It SHALL link that floor to its canonical skill rather than
restating it, and SHALL link the adversarial rite that runs after the change to its own.

The skill SHALL be opt-in. The catalog's execution flow states an implement-then-test order, and
this skill SHALL NOT silently invert it: the flow links here for the case where a repository or a
maintainer runs the cycle, and the default stays where it is until a separate decision moves it.

The skill SHALL carry no number about its own effect. The only measurement that exists for it
(`research/tdd/`) returned a verdict of NO-CLAIM under its own pre-registered protocol, and that
protocol's NO-CLAIM row forbids a number in any README or SKILL.md. The skill MAY name the
directory where the measurement lives, together with what it did and did not establish.

#### Scenario: A behaviour with a stated boundary gets its test first

- **WHEN** a change is asked for whose request names a boundary — an empty input, an exclusive end,
  a rejected value
- **THEN** the skill has the test for that boundary written before the implementation, and the test
  fails against the code as it stands
- **AND** a test that would pass before the implementation exists is named as testing nothing

#### Scenario: A trivial change does not acquire a cycle

- **WHEN** the change is a one-liner with no behaviour to name
- **THEN** the skill states that the cycle does not apply, and the floor of one runnable check is
  linked to its canonical skill rather than restated

#### Scenario: The default execution order is not silently inverted

- **WHEN** a reader follows the catalog's backlog execution flow
- **THEN** that flow still states implement-then-test as its default and links to this skill for the
  case where the cycle is being run
- **AND** the skill does not claim to have changed the default

#### Scenario: A skill with a NO-CLAIM measurement carries no number

- **WHEN** the only measurement of a skill's effect returned NO-CLAIM under its own protocol
- **THEN** neither the skill nor the README carries a figure from that measurement
- **AND** the skill names the directory where the measurement and its verdict can be read
