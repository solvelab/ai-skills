## MODIFIED Requirements

### Requirement: The rite gates evidence before it gates quality

The repository's spec-driven rite SHALL require every active change to open its task list with a
group recording what was probed: local paths opened rather than recalled, external tools, flags,
config keys, API names and versions checked against the installed version, and anything that could
not be probed written down as an open question rather than stated as fact. The group SHALL be the
first task group, and its presence and position SHALL be enforced by the same script that enforces
the other mandatory groups, because the OpenSpec CLI validates delta-spec format only.

Recorded evidence SHALL be a command together with a fragment of its raw output, never a conclusion,
so that a reviewer can re-run it. That rule SHALL be enforced in **shape**: a ticked box in the
evidence group SHALL be checked against the form its kind owes — a path opened together with the
commit or date it was read at; a probe together with a fragment of its output; a gap named or
explicitly declared absent — with a file-specific error naming the box and what is missing. The
rules SHALL be per box kind rather than uniform, because the kinds do not share a shape and a
uniform rule rejects boxes that are correct as written.

Every enforcing script SHALL state that it verifies presence, position and shape, and **not the
truth of the contents**: a box padded to satisfy the shape passes, and no script can tell an
invented output from a real one.

The mandatory groups that are **not** gated on shape SHALL have their evidence density reported
without affecting the exit code, so that a group whose boxes carry no probe is visible to a reviewer
without reading the diff.

#### Scenario: A change without recorded evidence fails the build

- **WHEN** an active change's task list lacks the evidence group, or carries it somewhere other than
  the first task group
- **THEN** the rite gate script fails with a file-specific error naming the missing or misplaced
  group, and the build does not pass

#### Scenario: A ticked box that states a conclusion fails the build

- **WHEN** a ticked box in the evidence group records a conclusion instead of the form its kind owes
- **THEN** the gate fails, naming the box and the missing element
- **AND** the same box rewritten with a command and a fragment of its output passes

#### Scenario: The gate declares what it cannot check

- **WHEN** the gate passes
- **THEN** the enforcing scripts state that shape is not truth — a box padded to satisfy the rule is
  indistinguishable from an earned one — so that a green run is not read as verified evidence

#### Scenario: A group that is reported rather than gated is not implied to be gated

- **WHEN** a mandatory group carries items that are judgments rather than executions
- **THEN** its evidence density is printed as a labelled report that never changes the exit code,
  and the check states that the group is reported and not gated, rather than demanding a command
  where none belongs

#### Scenario: A gate introduced mid-flight does not exempt existing work

- **WHEN** a new mandatory group is added while a change is already open
- **THEN** the open change is backfilled with the group in the same change that introduces the gate,
  rather than being added to an exemption list
