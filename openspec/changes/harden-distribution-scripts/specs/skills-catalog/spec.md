## ADDED Requirements

### Requirement: Distribution scripts refuse what they cannot honor, and CI exercises them

The catalog's distribution scripts — the installer and the updater the README documents — SHALL
refuse, or route around with a stated reason, every state they cannot honor, instead of failing
silently or with the underlying tool's raw error.

The updater SHALL always attempt the fast-forward pull, and SHALL regenerate the tool wrappers only
when the generator's inputs (the version file and the canonical skills tree) are clean in the
index. When they are not, it SHALL print which files are dirty and how to clean them, skip the
regeneration, and still exit success, so that a user who edits the clone the way the README
allows is neither blocked nor pushed toward a hard reset. A failure of the generator SHALL surface
as a non-zero exit with the generator's output, never be swallowed by the shell.

The installer SHALL validate its tool argument before any clone or pull, SHALL reject a missing
value with a usage error that lists the supported tools, and on a re-run over an existing clone
SHALL pull fast-forward only, giving the same message and recovery hint the updater gives when the
clone has diverged.

Neither script SHALL prompt: both are documented as piped into `bash` from `curl`, where standard
input is the script itself. Each script SHALL state, in its own header, what its guard does not
cover.

The catalog's CI SHALL exercise both scripts through their real entry points, in a temporary home
directory, cloning from a local repository rather than the network, covering every behavior this
requirement names, and SHALL print the case matrix as counts.

#### Scenario: A dirty generator input skips regeneration without blocking the update

- **WHEN** the updater runs over a clone whose version file or canonical skills tree carries an
  uncommitted, tracked modification
- **THEN** the pull happens, the regeneration is skipped, the dirty files and the cleaning command
  are printed, the script exits zero, and no generated plugin manifest is modified

#### Scenario: An edit outside the generator's inputs does not skip regeneration

- **WHEN** the updater runs over a clone whose only uncommitted change is outside the version file
  and the canonical skills tree — such as the personal rules file the README tells users to edit
- **THEN** the wrappers are regenerated as usual

#### Scenario: A generator failure is visible

- **WHEN** the generator exits non-zero during an update
- **THEN** the updater exits non-zero and prints the generator's output, instead of reporting the
  wrappers as regenerated

#### Scenario: A diverged clone is refused with the recovery hint, by both scripts

- **WHEN** the clone carries a local commit that the remote branch does not, and either the updater
  without `--force` or the installer on a re-run is executed
- **THEN** the script exits one with its own message naming the divergence and the `--force`
  recovery command, and the tool's own error appears only as an indented detail under that message

#### Scenario: An unsupported or missing tool value fails before any clone

- **WHEN** the installer is invoked with a tool value outside the supported list, or with the tool
  flag and no value at all
- **THEN** it exits one listing the supported tools, and no clone directory is created and no pull
  is attempted

#### Scenario: The scripts are exercised in CI without the network

- **WHEN** the catalog's validation job runs
- **THEN** a smoke test clones from a local repository into a temporary home directory, runs the
  installer and the updater through their documented invocations for every scenario above, prints
  the case matrix as counts, and fails the job when any case regresses

#### Scenario: The guard declares its own blind spot

- **WHEN** the updater decides whether to regenerate by reading the index for a fixed set of paths
- **THEN** its header states that untracked files and edits outside those paths are not seen, so a
  regeneration that ran is not read as proof that the inputs were pristine
