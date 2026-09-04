## MODIFIED Requirements

### Requirement: The repository itself is gated, not only its skills

The catalog SHALL carry a gate whose subject is the whole repository rather than a subtree, wired
into CI, covering at minimum two classes that have escaped every other gate: a compiled artifact
that is tracked, and a published count of the catalog's contents that disagrees with the contents.
Tracked-file discovery SHALL read the index rather than the filesystem, so that an ignored artifact
present in a working directory is not a finding and one forced into the index is.

The gate SHALL carry a self-test that injects one known defect per check and asserts detection, and
each check SHALL state inside itself what it does not cover.

The repository's other whole-repository checks SHALL measure what they claim to measure, and three
classes that were measured escaping them SHALL be covered:

- The check that keeps the generated wrapper trees in sync with `skills/` SHALL fail on a generated
  file that is **untracked** after regeneration, naming the file, and not only on a tracked file
  whose content changed — a diff against the index never sees an untracked file.
- The check that a pull request registers its change SHALL require **relevance**, not existence: the
  diff touches the directory of an active change, or the pull request body names an active change
  on a `Spec-rite: <id>` line, or the diff archives a change, or the body carries the written
  waiver. The mere presence of an unrelated active change SHALL NOT register a diff. The line
  naming a change SHALL be matched as text, anchored to the start of a line, and never executed.
- The frontmatter checks on `skills/*/SKILL.md` SHALL read only the frontmatter block — the text
  between the two `---` delimiters, extracted the same way the wrapper generator extracts it — so a
  field that appears only inside a code block in the body does not satisfy a check on the
  frontmatter.

The job that runs these gates SHALL hold the least privilege the gates need: read-only repository
contents, no credential persisted past the checkout, a declared timeout, and every third-party tool
it runs pinned to a version that was probed, with the bump rule stated beside the pin. A job output
that no consumer reads SHALL be removed or wired to one.

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

#### Scenario: An untracked generated file fails the wrapper-sync check

- **WHEN** a commit adds a file under `skills/<name>/` whose regenerated mirror under `plugins/` is
  not tracked
- **THEN** the wrapper-sync step fails and names the untracked file, instead of passing because the
  diff against the index is empty

#### Scenario: An unrelated active change does not register a diff

- **WHEN** a pull request's diff touches a path outside the workflow's own directory, an active
  change exists whose directory the diff does not touch, and the body names no active change and
  carries no waiver
- **THEN** the spec-rite gate fails, naming the active changes it found and the two ways of linking
  the diff to one of them

#### Scenario: A pull request that touches or names its change passes

- **WHEN** the diff touches `openspec/changes/<id>/` of an active change, or the body carries
  `Spec-rite: <id>` naming an active change
- **THEN** the spec-rite gate passes, so a pull request that only ticks a task list, or a small fix
  opened against a change in progress elsewhere, is not rejected

#### Scenario: An archive-only pull request still passes

- **WHEN** a pull request only moves a change into `openspec/changes/archive/` and syncs the specs
- **THEN** the spec-rite gate passes, whether or not another change is active

#### Scenario: A frontmatter field inside a code block does not count

- **WHEN** a `SKILL.md` carries no `name:` in its frontmatter but a fenced `yaml` block in its body
  contains `name: <dir>`
- **THEN** the frontmatter check fails with `Missing name`, because only the block between the two
  `---` delimiters is read

#### Scenario: The validate job holds no writable token

- **WHEN** the validate job runs on a pull request
- **THEN** its permissions grant read-only repository contents, the checkout does not persist the
  token, the job carries a timeout, and the spec-driven CLI it runs is pinned to a probed version

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

Where a shape rule accepts a box on a proxy — a length threshold standing in for "names something"
— the proxy and what it lets through SHALL be declared in the script's own known limits, and the
self-test SHALL carry an explicit case for it whose expected result is silence, so that the escape
is measured on every run rather than remembered.

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

#### Scenario: A declared escape is measured, not remembered

- **WHEN** a gap box (E.3, E.4 or S.3) is ticked with more than the length threshold of text that
  names no gap and declares none absent
- **THEN** the gate stays silent, the script's known limits name that threshold as the reason, and
  the self-test reports the case under its known escapes with the observed silence

#### Scenario: A group that is reported rather than gated is not implied to be gated

- **WHEN** a mandatory group carries items that are judgments rather than executions
- **THEN** its evidence density is printed as a labelled report that never changes the exit code,
  and the check states that the group is reported and not gated, rather than demanding a command
  where none belongs

#### Scenario: A gate introduced mid-flight does not exempt existing work

- **WHEN** a new mandatory group is added while a change is already open
- **THEN** the open change is backfilled with the group in the same change that introduces the gate,
  rather than being added to an exemption list
