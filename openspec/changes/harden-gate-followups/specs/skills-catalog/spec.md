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
- The checks that read a pull request's diff SHALL read its paths NUL-separated (`git diff
  --name-only -z`) rather than line by line, so that a path git would quote and octal-escape in
  line mode — one carrying a non-ASCII, control or quote character — is matched verbatim by the
  workflow-directory exemption and by the change directory it belongs to. Every reader of the
  diff in the repository SHALL read it the same way, and each SHALL prove it in its own self-test
  against a repository that quotes paths.

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

#### Scenario: A quoted path still registers its change

- **WHEN** a pull request's diff touches `openspec/changes/<id>/` of an active change only through
  a path git would quote in line mode — a file named `café.md`, say — and the checkout quotes
  paths
- **THEN** the spec-rite gate reads the path verbatim, counts the diff as touching that change,
  and passes, instead of reporting the quoted path as an unregistered file outside the workflow's
  directory

### Requirement: The identifier-locale check reads the path it is given

The shipped identifier-locale check SHALL apply its tiers to the **path** of the artifact it scans —
directory names and the file stem — and not only to the artifact's contents, because file, directory
and module names are named by the doctrine as part of the machine layer. A check whose documented
scope names an artifact class it never reads SHALL be treated as a defect in the check, not as a
property of the artifact class.

The path tier SHALL reuse the exclusions the check already applies to identifiers — vendored and
generated trees, the minimum segment length, the kept domain terms and the allowlist file — so that
one rule change cannot make the two halves disagree.

The path measured SHALL be the part the scanned project owns: the path relative to the working
directory when the artifact lies inside it, and the file's own name otherwise. Segments above the
working directory SHALL NOT be scanned, because they name the machine, the user or the mount point
rather than anything the project chose.

In diff mode the path SHALL be checked only for files the diff **adds**. A file that already exists
SHALL NOT be reported on every diff that touches it, because renaming it is the migration policy's
decision and not this check's.

In diff mode the vendored and generated exclusion SHALL apply to the whole file the `+++` header
names — its path and its added lines alike — and that file SHALL be counted as skipped, never as
passing, exactly as file mode counts it. The exclusion is decided on the path, because a diff
carries no file body for the minified test to read.

A path finding SHALL name the waiver that silences it. Since a file name carries no inline comment,
that waiver SHALL be the allowlist file the check already reads.

#### Scenario: A Portuguese file name with an English body is reported

- **WHEN** the check scans a file whose body is English but whose path carries Portuguese segments
- **THEN** it reports one finding per offending segment and exits non-zero
- **AND** the finding names the path and the segment, in the same shape an identifier finding uses

#### Scenario: An added path is measured and an existing one is not

- **WHEN** a unified diff adds a file whose path carries a Portuguese segment
- **THEN** the check reports it in diff mode
- **AND** a diff that only modifies an already existing file with the same path reports nothing about
  that path

#### Scenario: The path above the working directory is out of scope

- **WHEN** the artifact scanned lies inside the working directory
- **THEN** only the segments relative to that directory are measured
- **AND** an artifact outside the working directory has only its own file name measured

#### Scenario: A path finding names its waiver

- **WHEN** a path finding is printed
- **THEN** it states the allowlist entry that silences it, because a file name cannot carry the
  inline waiver an identifier uses

#### Scenario: The path tier inherits the identifier exclusions

- **WHEN** the scanned path lies in a vendored or generated tree, or its segments are shorter than
  the minimum length, or they are kept domain terms, or they are listed in the allowlist
- **THEN** the check reports nothing for that path, exactly as it already behaves for identifiers

#### Scenario: A vendored path in a diff is skipped, not measured

- **WHEN** a unified diff adds or modifies a file under a vendored or generated tree, such as
  `node_modules/`, whose added lines carry Portuguese identifiers
- **THEN** the check reports nothing for that file in diff mode, counts it in the skipped
  vendored report, and exits zero, exactly as it already does when the same file is scanned by
  path
