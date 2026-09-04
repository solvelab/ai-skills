## ADDED Requirements

### Requirement: Published plugin descriptions are derived from the tree

The description a plugin publishes — in its own manifest and in the marketplace entry that points
at it — SHALL be produced by the generator from the skills present under that plugin's tree at
generation time. The only hand-written part SHALL be a one-line theme per group; the count of skills
and their names SHALL be read from the tree, so that a skill entering or leaving a group changes
every published description on the next generation without a manual edit.

The generator SHALL refuse to run for a group that has no theme, and SHALL refuse a version string
that is not of the shape `MAJOR.MINOR.PATCH` with an optional pre-release suffix, in both cases
before writing any file. A placeholder description or a malformed version reaching a published
manifest is the silent defect this requirement exists to remove.

Regeneration SHALL be idempotent: a second run over an unchanged tree SHALL write nothing new. The
generator SHALL leave the version fields of the marketplace and the root manifest to the release
script, which remains their only writer.

#### Scenario: A skill that changes category moves in every published description

- **WHEN** a skill's category changes and the generator runs
- **THEN** the plugin manifest of the group it left, the manifest of the group it joined, and both
  marketplace entries name the new membership with the right count, and no file was edited by hand

#### Scenario: A group without a theme stops the generator

- **WHEN** the tree yields a plugin group for which no theme is declared
- **THEN** the generator exits non-zero naming the group and the skill that yielded it, before any
  wrapper or plugin manifest is written, instead of publishing a placeholder

#### Scenario: A malformed version stops the generator before it writes

- **WHEN** the version file carries a value such as `1.2.3garbage`
- **THEN** the generator exits non-zero before any wrapper or plugin manifest is written, and the
  release script refuses the same value with the same rule

#### Scenario: A second generation is a no-op

- **WHEN** the generator runs twice over an unchanged tree
- **THEN** the second run leaves the working tree without a diff

## MODIFIED Requirements

### Requirement: The repository itself is gated, not only its skills

The catalog SHALL carry a gate whose subject is the whole repository rather than a subtree, wired
into CI, covering at minimum three classes that have escaped every other gate: a compiled artifact
that is tracked, a published count of the catalog's contents that disagrees with the contents, and
a published plugin description whose membership disagrees with the plugin's tree.
Tracked-file discovery SHALL read the index rather than the filesystem, so that an ignored artifact
present in a working directory is not a finding and one forced into the index is.

The gate SHALL carry a self-test that injects one known defect per check and asserts detection, and
each check SHALL state inside itself what it does not cover.

#### Scenario: A compiled artifact forced into the index fails the build

- **WHEN** a file matching the repository's bytecode ignore rules is nonetheless tracked
- **THEN** the hygiene gate fails and names the file and the command that untracks it

#### Scenario: An ignored artifact in the working directory is not a finding

- **WHEN** a developer runs a Python file and leaves a `__pycache__` beside it
- **THEN** the gate is silent, because the artifact is not in the index

#### Scenario: A published count that disagrees with the tree fails the build

- **WHEN** a document publishes a count of the catalog's skills that differs from the number of skill
  directories
- **THEN** the gate fails and names the file, the line, the claimed number and the real one

#### Scenario: A published description that disagrees with the tree fails the build

- **WHEN** a plugin manifest or its marketplace entry names a skill that is not under the plugin's
  tree, omits one that is, or publishes a count that does not match the names it lists
- **THEN** the gate fails and names the file, the group, the names in excess and the names missing

#### Scenario: A bare count with no membership is refused

- **WHEN** a published document carries a parenthetical count of topics or skills that names no
  members, outside a code block
- **THEN** the gate fails and names the file and the line, because a count that says which set it
  counts is the only kind the tree can check

#### Scenario: A check that cannot fire is caught

- **WHEN** a change to the gate silently stops one of its checks from detecting its defect class
- **THEN** the self-test fails, because a clean repository and a check that cannot fire are otherwise
  indistinguishable

#### Scenario: The uncovered part is declared, not implied

- **WHEN** a check enforces its rule only over a named pattern or a named file list
- **THEN** the pattern, the file list and what escapes them are stated in the check itself, so a
  passing run is not read as full coverage
