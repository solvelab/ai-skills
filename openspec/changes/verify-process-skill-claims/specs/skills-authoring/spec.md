## MODIFIED Requirements

### Requirement: Versioned external APIs are pinned

A skill whose content targets an external API **or command-line tool** with breaking releases SHALL
state the exact versions it was verified against, and SHALL name any known upcoming rename or removal
that will invalidate it. For a skill that instructs the agent to run a CLI, the commands and flags it
prescribes SHALL be probed against that tool before publication.

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
