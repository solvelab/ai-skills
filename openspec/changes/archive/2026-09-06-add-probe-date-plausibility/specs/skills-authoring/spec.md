## MODIFIED Requirements

### Requirement: Versioned external APIs are pinned

A skill whose content targets an external API **or command-line tool** with breaking releases SHALL
state the exact versions it was verified against, and SHALL name any known upcoming rename or removal
that will invalidate it. For a skill that instructs the agent to run a CLI, the commands and flags it
prescribes SHALL be probed against that tool before publication.

Every `SKILL.md` SHALL carry exactly one of two literal declarations, placed where a reader meets it
before the first rule: a `Verified against` block naming each tool and the version it was probed
against, what was run, and the probe date written as the literal `Probed on YYYY-MM-DD`, which
SHALL be a real calendar date that is neither in the future nor earlier than the repository's first
commit; or the sentence `does not depend on a tool
version` followed by the reason. The date MAY be the recorded probe's when the block names the change
or commit that recorded it. A `Verified against` block SHALL name only versions the claims were actually probed
against, and SHALL name the part of the skill that was not probed rather than cover it by implication.
A version written for a run nobody made is a defect, not a pin. The declaration is an exit for
process skills: a skill carrying 40 or more fenced lines against a versioned API SHALL carry the
block unless it defers to a local source of truth it instructs the reader to open first.

#### Scenario: Reader can tell which era the code targets

- **WHEN** a skill documents a library API
- **THEN** the skill names the library versions its examples were verified against, rather than
  leaving the reader to infer it

#### Scenario: A known breaking change is disclosed, not silently absorbed

- **WHEN** the upstream has announced a rename or removal affecting the skill's examples
- **THEN** the skill names it and where it applies, instead of presenting the current form as timeless

#### Scenario: Prescribed CLI commands are probed, not assumed

- **WHEN** a skill instructs the agent to run a command with specific subcommands and flags
- **THEN** each subcommand and flag is checked against the installed tool before publication, and the
  tool version the check ran against is recorded

#### Scenario: Tool guidance contradicted by the tool is corrected, not repeated

- **WHEN** a tool's own output advertises behaviour its implementation does not deliver
- **THEN** the skill states the probed behaviour and the version it holds for, rather than repeating
  the tool's claim

#### Scenario: Every skill declares its relationship to versions

- **WHEN** a `SKILL.md` carries neither the literal `Verified against` nor the literal
  `does not depend on a tool version`
- **THEN** the validator reports it under C5, whatever amount of fenced code the skill carries

#### Scenario: A loose version mention is not a pin

- **WHEN** a skill names a version only in passing (`Probed on CLI 1.6.0`, `targets v0.0.54`,
  `needs CSP >= 0.1.78`) and carries no literal `Verified against`
- **THEN** the validator reports it under C5, because a reader cannot tell a pin from a mention

#### Scenario: A code-heavy skill does not exit by declaration

- **WHEN** a skill carries 40 or more fenced lines, names a versioned API, declares that it does not
  depend on a tool version, and does not defer to a local source of truth
- **THEN** the validator reports the declaration as contradicted by the skill's own code

#### Scenario: A partial probe names its boundary

- **WHEN** only part of a skill's surface could be probed — public API stubs or source, but not the
  runtime that executes them
- **THEN** the `Verified against` block names what was probed, against which artifact and version,
  and states what was not probed, instead of letting the pin cover the whole skill

#### Scenario: A pin carries the date it was probed

- **WHEN** a `Verified against` block — the text from that line to the next blank line — carries no
  ISO date (`YYYY-MM-DD`)
- **THEN** the validator reports it under C5, because a pin with no date does not say when it
  stopped being trustworthy

#### Scenario: The probe date is named as such

- **WHEN** a `Verified against` block — normalised by stripping the blockquote prefix and joining
  its lines — carries ISO dates but no `Probed on YYYY-MM-DD` (or `probed on YYYY-MM-DD`)
- **THEN** the validator reports it under C5, because a date of a commit or a release the block
  cites does not stand in for the date the probe ran

#### Scenario: A line wrap does not fail a correct block

- **WHEN** the wrap leaves `Probed on` at the end of one blockquote line and the date at the start of
  the next
- **THEN** the validator, matching on the normalised block, stays silent

#### Scenario: An impossible probe date is a defect

- **WHEN** the date following `Probed on` is not a calendar date, is later than the day of the check
  (UTC), or is earlier than the repository's first commit
- **THEN** the validator reports it under C5 naming the rule it broke, because a date that cannot be
  true tells the reader nothing about how old the pin is

#### Scenario: Dates the block merely cites are not probe dates

- **WHEN** the block names the date of a commit, release or measurement run it cites, outside the
  `Probed on` literal
- **THEN** the validator leaves that date alone, judging only what the block claims as its probe date
