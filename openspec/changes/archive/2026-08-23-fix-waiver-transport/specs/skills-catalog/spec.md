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

The gate SHALL cover the **absence** of a change and not only the shape of one that is present. A
gate whose checks are written as a loop over active changes passes vacuously when there are none,
which reads as approval of a pull request that recorded nothing. Therefore a pull request whose diff
touches paths outside the workflow's own directory SHALL be required to carry one of: an active
change, a change archived within the same diff, or a waiver line in the pull request body naming a
reason. Paths written by the release automation alone SHALL be exempt, and the check SHALL run only
where a base revision to compare against exists. Where it runs in continuous integration and no base
revision can be resolved, it SHALL fail rather than skip, because a gate that cannot measure must not
approve — an unresolvable base there is a misconfigured checkout, not an exemption.

The waiver SHALL be treated as untrusted input: it is authored by whoever opened the pull request,
including from a fork, and SHALL be matched as text and never executed or interpolated into a
command.

The same care SHALL apply to what the gate makes appear. A gate SHALL NOT publish the content it
reads into a channel whose audience differs from that content's own: it reads the pull request body
from the payload the runner already writes, rather than having it handed over through a mechanism the
continuous-integration system echoes into the build log. Where the gate is nonetheless given the
content explicitly — for local runs, or as a fallback — that path SHALL be the deliberate override
and not the default. Failure to read the payload SHALL degrade to an empty body rather than an
error, so that the decision stays with the rules that already exist instead of the build failing for
a reason unrelated to the rite.

Every enforcing script SHALL state that it verifies presence, position and shape, and **not the
truth of the contents**: a box padded to satisfy the shape passes, and no script can tell an
invented output from a real one. A script that also verifies that a change exists SHALL state that
existence is not honesty — a change scaffolded to satisfy the gate passes it.

The mandatory groups that are **not** gated on shape SHALL have their evidence density reported
without affecting the exit code, so that a group whose boxes carry no probe is visible to a reviewer
without reading the diff.

#### Scenario: A change without recorded evidence fails the build

- **WHEN** an active change's task list lacks the evidence group, or carries it somewhere other than
  the first task group
- **THEN** the rite gate script fails with a file-specific error naming the missing or misplaced
  group, and the build does not pass

#### Scenario: A pull request that records nothing fails the build

- **WHEN** a pull request's diff touches a path outside the workflow's own directory and carries
  neither an active change, nor a change archived in the same diff, nor a waiver line
- **THEN** the rite gate fails, naming the offending path, rather than passing because the loop over
  active changes found nothing to check

#### Scenario: A gate that cannot measure does not approve

- **WHEN** the check runs in continuous integration and no base revision can be resolved
- **THEN** it fails naming the missing fetch depth, rather than passing because it had nothing to
  compare against

#### Scenario: The waiver is a written line, not a judgment

- **WHEN** the same diff is accompanied by a waiver line in the pull request body naming a reason
- **THEN** the gate passes and the reason is visible to the reviewer in the pull request itself
- **AND** the line is matched as text, never executed, because its author is whoever opened the pull
  request

#### Scenario: The gate does not publish what it reads

- **WHEN** the gate needs the pull request body to look for a waiver
- **THEN** it reads it from the event payload the runner already wrote, so no step hands the body
  over through a mechanism that prints it into the build log
- **AND** an explicit hand-over remains available as an override for running the gate outside
  continuous integration, taking precedence when it is set
- **AND** a payload that is missing, unreadable or without the key yields an empty body, leaving the
  existing rules to decide, rather than failing the build

#### Scenario: A ticked box that states a conclusion fails the build

- **WHEN** a ticked box in the evidence group records a conclusion instead of the form its kind owes
- **THEN** the gate fails, naming the box and the missing element
- **AND** the same box rewritten with a command and a fragment of its output passes

#### Scenario: The gate declares what it cannot check

- **WHEN** the gate passes
- **THEN** the enforcing scripts state that shape is not truth — a box padded to satisfy the rule is
  indistinguishable from an earned one — so that a green run is not read as verified evidence
- **AND** they state that the existence of a change is not the honesty of one

#### Scenario: A group that is reported rather than gated is not implied to be gated

- **WHEN** a mandatory group carries items that are judgments rather than executions
- **THEN** its evidence density is printed as a labelled report that never changes the exit code,
  and the check states that the group is reported and not gated, rather than demanding a command
  where none belongs

#### Scenario: A gate introduced mid-flight does not exempt existing work

- **WHEN** a new mandatory group is added while a change is already open
- **THEN** the open change is backfilled with the group in the same change that introduces the gate,
  rather than being added to an exemption list
