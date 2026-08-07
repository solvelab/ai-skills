## ADDED Requirements

### Requirement: The repository itself is gated, not only its skills

The catalog SHALL carry a gate whose subject is the whole repository rather than a subtree, wired
into CI, covering at minimum two classes that have escaped every other gate: a compiled artifact
that is tracked, and a published count of the catalog's contents that disagrees with the contents.
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

#### Scenario: A check that cannot fire is caught

- **WHEN** a change to the gate silently stops one of its checks from detecting its defect class
- **THEN** the self-test fails, because a clean repository and a check that cannot fire are otherwise
  indistinguishable

#### Scenario: The uncovered part is declared, not implied

- **WHEN** a check enforces its rule only over a named pattern or a named file list
- **THEN** the pattern, the file list and what escapes them are stated in the check itself, so a
  passing run is not read as full coverage
