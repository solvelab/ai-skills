# skills-catalog Specification

## Purpose

The composition of the published catalog and its discovery contract: which skills exist, which are
superseded or removed, and the guarantee that `npx skills add <repo> --list` finds every skill at
the expected count with no orphans or renamed leftovers. Changes that add, remove, or supersede
skills are validated against this spec by the skills-rite Validation & Closure gate.
## Requirements
### Requirement: Catalog composition after the quality review

The catalog SHALL be exactly the set of `skills/<name>/SKILL.md` files. A skill present only in a
generated tree (`claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`) is not a catalog skill: it
escapes `generate.sh`, the CI frontmatter check, the content validator and the README index, while
still installing for users. CI SHALL reject that state.

A skill's topics MAY live in `skills/<name>/references/*.md`, reached from an index in its `SKILL.md`.
A reference file is part of its skill, never a catalog entry of its own, and never carries frontmatter.

The composition is not a frozen count. It changes by proposal, and the README index is the
human-readable view of it.

#### Scenario: npx discovery lists the full catalog

- **WHEN** `npx skills add <repo> --list` runs against the repository root
- **THEN** every `skills/<name>/SKILL.md` is discovered
- **AND** the set matches the README skill index
- **AND** no `references/*.md` file appears as a skill

#### Scenario: A skill in a generated tree without a source is rejected

- **WHEN** a directory exists under `claude/skills/` or `codex/skills/` with no matching
  `skills/<name>/SKILL.md`
- **THEN** `scripts/validate-skills.py` reports it as an orphan wrapper and CI fails

#### Scenario: Adding a skill goes through the canonical tree

- **WHEN** a new skill is added
- **THEN** it is written to `skills/<name>/SKILL.md`, its wrappers are produced by `./generate.sh`,
  and it gains a README row — never hand-written into a generated tree

### Requirement: Generic doctrine is reusable outside FiveM

Dependency-resilience doctrine SHALL live in `backend-resilience` (stack-agnostic principles with Python
examples) and adversarial-testing methodology SHALL live in `bug-hunter`'s stack-agnostic SKILL.md, so
non-FiveM projects can adopt them without pulling FiveM content.

#### Scenario: Python project adopts resilience patterns

- **WHEN** an agent working on a Python REST project needs fallback/negative-cache/retry guidance
- **THEN** `backend-resilience` provides the complete doctrine with no FiveM/Lua prerequisites
- **AND** `fivem-fallback` contains only the FiveM/Lua adaptation and links to `backend-resilience`

#### Scenario: Adversarial testing on a non-DriveZone stack

- **WHEN** an agent runs the bug-hunter rite on a project that is neither pytest nor FiveM
- **THEN** the SKILL.md mindset, universal checklist and output contract apply as-is
- **AND** stack specifics are opt-in reference files (`references/track-python-pytest.md`,
  `references/track-fivem-lua.md`)

### Requirement: r3f asset loading is a single skill

Model loading, texture loading/configuration and Suspense/caching patterns SHALL be covered by one
skill, `r3f-assets`.

#### Scenario: Texture task routes unambiguously

- **WHEN** a task involves loading textures or GLTF models in React Three Fiber
- **THEN** exactly one skill description (`r3f-assets`) claims that territory

### Requirement: Backlog item creation skill

The catalog SHALL provide a `backlog` skill that turns a natural-language idea into a structured
GitHub issue added to a configured GitHub Project v2 with fields filled, using only per-target
config files (repo `.github/backlog.yml` or workspace-root `backlog.yml`) and the user's own `gh`
CLI authentication. The skill SHALL contain no user-, org- or project-specific data.

#### Scenario: Repo mode creation

- **WHEN** `/backlog <idea>` runs inside a git repository containing `.github/backlog.yml`
- **THEN** the skill drafts a structured issue enriched with real repository context, shows a
  preview, and only after approval creates the issue in that repository and adds it to the
  configured Project with mapped fields set

#### Scenario: Workspace mode creation

- **WHEN** `/backlog <idea>` runs in a directory that is not a git repository but contains multiple
  repositories of one org, with `backlog.yml` at its root
- **THEN** the skill analyzes which repositories the idea affects, includes an Affected
  repositories section, and creates the issue in the primary affected repository (or the
  `issues_repo` override), adding it to the org's configured Project

#### Scenario: Missing Project scopes abort cleanly

- **WHEN** the authenticated `gh` token lacks the `project` scope
- **THEN** the skill stops before any write, printing the exact
  `gh auth refresh -s project,read:project` remediation

#### Scenario: First run without config launches the wizard

- **WHEN** `/backlog <idea>` runs where no config file exists
- **THEN** the skill discovers the owner from git remotes, lists that owner's Projects, maps fields
  by name after the user picks one, and writes the config file before proceeding

### Requirement: Backlog execution skill

The catalog SHALL provide an `execute-backlog` skill that takes an existing GitHub issue (number,
URL or search term), validates it is executable, presents an implementation plan for approval
before any code change, implements it on a dedicated branch following the target repo's
conventions, runs the repo's discoverable validations, opens pull request(s) linking the issue,
and updates the configured GitHub Project item — without ever merging, closing the issue directly,
or committing to the default branch.

#### Scenario: Plan approval gates implementation

- **WHEN** `/execute-backlog <n>` runs on a well-formed issue
- **THEN** the skill presents scope, affected files, test strategy and risks derived from the
  current codebase state
- **AND** no file is modified until the user approves the plan

#### Scenario: Incomplete item is not executed

- **WHEN** the referenced issue lacks scope or acceptance criteria, or contradicts the current
  codebase
- **THEN** the skill reports the gaps and asks whether to proceed anyway, refine the item first,
  or abort — it never fills missing scope by guessing

#### Scenario: Execution outcome is linked and tracked

- **WHEN** an approved plan is implemented and validations pass
- **THEN** a pull request referencing the issue (`Closes #n` on the primary repo) is opened from a
  dedicated branch
- **AND** the Project item moves to the configured review column
- **AND** the issue itself is not closed by the skill

#### Scenario: Workspace mode resolves affected repositories

- **WHEN** the issue contains an Affected repositories section and the skill runs in a workspace
- **THEN** work is orchestrated per affected repo (missing local clones offered via
  `gh repo clone`), with one PR per repo that changes

### Requirement: Observability has a canonical home

The catalog SHALL contain one skill that defines how a backend service is observed — request
correlation, metrics and their labels, and the reporting of degraded operation. Skills that
*prescribe* an observable action (incrementing a counter, emitting a correlated log line) SHALL link
to it for the definition rather than restating the mechanism.

#### Scenario: A prescribed metric has a defined home

- **WHEN** a skill instructs code to increment a counter or emit a correlated log line
- **THEN** the counter's registry, name and permitted labels are defined in `observability`, and the
  prescribing skill links to it instead of describing them

#### Scenario: Degraded operation is reportable

- **WHEN** a service is serving requests entirely from fallbacks
- **THEN** the doctrine provides a way to report it — a detailed-health field and a metric — so that
  liveness and readiness both passing does not read as healthy

### Requirement: Shipped scripts state what they persist

A skill that ships an executable which writes state outside the repository SHALL state where that
state lives, what keys it, and how it is bounded. State that grows once per session SHALL be pruned
by the script itself rather than left to accumulate for the life of the machine.

Persisted records SHALL use a field separator that survives an empty field, and a record that does not
parse SHALL be discarded whole rather than partially trusted.

#### Scenario: A shipped script's state is discoverable

- **WHEN** a skill ships a script that persists anything between runs
- **THEN** the skill names the path, the key it is filed under, and the retention, so a user can find
  it, inspect it or delete it without reading the source

#### Scenario: Per-session state does not grow without bound

- **WHEN** a script keeps one state file per session
- **THEN** it prunes stale files on a cheap occasion (such as the first write of a new session),
  instead of relying on the user to clean up

#### Scenario: An empty field does not corrupt the record

- **WHEN** a persisted record contains a field that is empty for a legitimate reason
- **THEN** reading it back yields the same fields in the same positions, and a record that fails to
  parse is discarded rather than read with its values shifted

### Requirement: The development rite is enforced outside the model's discretion

The catalog SHALL state, in its portable global rules, that every code change starts as a backlog
item, and SHALL ship an enforcement artifact that fires without depending on the assistant noticing
the rule. The artifact SHALL inform rather than block: it never denies a tool call, and the user can
always waive the rite explicitly. Diagnosing, reading and answering SHALL remain unrestricted — the
rite applies only when code is going to change.

In a repository that runs a spec-driven workflow, the rite SHALL NOT end at the backlog item. The
spec artifact SHALL be named by the same enforcement artifact that names the backlog step, and the
naming SHALL be conditional on that workflow being present, so that the reminder stays silent where
it does not apply. A repository whose spec policy is unstated SHALL be treated as requiring the
artifact, so that the absence of a decision is not read as permission to skip it.

The decision to ship without a spec artifact SHALL be a written one. A judgment made silently by the
assistant, or by a contributor in conversation, SHALL NOT satisfy the rite: the waiver SHALL exist as
a reviewable line in the pull request, and the gate SHALL be what reads it.

The enforcement artifact SHALL carry a self-test, exercised by the repository's own CI, that fixes
the decisions its design already assumes — what fires, what stays silent, and where the spec
sentence is appended — so that an edit to its signal list is measured rather than trusted. A
deliberately accepted false positive SHALL be fixed in that self-test as a case that fires, with the
recorded decision cited beside it, so that a well-meant correction cannot revert it unread. A
payload that is not a JSON object SHALL be ignored: the artifact exits zero with no output and no
traceback, because a hook that crashes on malformed input costs the turn it was meant to inform.

#### Scenario: A code-change request carries the rite into context

- **WHEN** a prompt asks for an implementation, fix, refactor or removal
- **THEN** the shipped `UserPromptSubmit` hook injects the rite reminder naming `/backlog` as the
  entry point and `/execute-backlog` as the second step
- **AND** the reminder states that diagnosis is free and that an approved plan is not a waiver

#### Scenario: The reminder names the spec rite only where it exists

- **WHEN** the prompt matches a code-change signal and the working directory carries the
  spec-driven workflow's directory
- **THEN** the reminder also names the spec artifact as a step that precedes the first edit outside
  that directory
- **AND** the same prompt in a working directory without that workflow produces the reminder without
  the spec sentence, so the added line never fires where it has no meaning

#### Scenario: The reminder is silent inside its own rite

- **WHEN** the prompt is already a rite command (`/backlog`, `/execute-backlog`), another slash
  command, or contains an explicit waiver
- **THEN** the hook produces no output, so the reminder never fires against the flow it enforces

#### Scenario: Plan approval is not a bypass

- **WHEN** an assistant finishes planning and the plan is approved
- **THEN** the rule as stated in the global rules requires the work to become a backlog item before
  the first edit, because approving a plan approves the plan and not the skipping of the rite

#### Scenario: The enforcement artifact persists nothing

- **WHEN** the shipped hook runs
- **THEN** it reads the prompt payload, matches, prints and exits, writing no state outside the
  repository and requiring no credentials

#### Scenario: The shipped hook carries a self-test and a malformed payload is ignored

- **WHEN** the hook is run with `--selftest`
- **THEN** it prints one OK/FAILED line per fixed decision plus a summary line and exits non-zero
  when any decision regressed, and the repository's CI runs that mode as a blocking step
- **AND** the case list includes a diagnostic question containing a change word as a case that
  fires, citing the decision that accepted the false positive
- **AND** when the payload on stdin is a JSON array, a JSON string or empty, the hook exits zero
  with no output and no traceback

### Requirement: The backlog skills declare their place in one rite

The `backlog` and `execute-backlog` descriptions SHALL identify each other as the two halves of a
single flow — creation then execution — so that a reader arriving at either one learns where the
work came from and where it goes next. Neither description SHALL restate the other's workflow.

Where the target repository runs a spec-driven workflow, both skills SHALL carry the gate that
workflow imposes between them, and neither SHALL restate its lifecycle: the lifecycle has a canonical
home in the catalog's own spec-driven skill, and the backlog skills SHALL link to it. The creating
skill SHALL record the verdict — the artifact that will exist, or the written waiver — in the item
itself, so the executing skill inherits a decision instead of making a new one. The executing skill
SHALL re-check that verdict against the change it is about to make, SHALL raise it without asking
when the work outgrew the item, and SHALL NOT lower it without the user, because a silent downgrade
is the failure this gate exists to prevent.

The policy SHALL be the repository's to set rather than the skills', because both skills run against
repositories with different rites; a repository that states no policy while carrying the workflow
SHALL be treated as requiring the artifact.

#### Scenario: Entry point is discoverable from the execution skill

- **WHEN** a user reads the `execute-backlog` description
- **THEN** it names `backlog` as the step that produces the item it consumes

#### Scenario: Exit is discoverable from the creation skill

- **WHEN** a user reads the `backlog` description
- **THEN** it names `execute-backlog` as the step that turns the created item into a pull request

#### Scenario: The item carries its spec verdict

- **WHEN** the creating skill drafts an item for a repository that runs the spec-driven workflow
- **THEN** the drafted item declares either the change identifier and the capabilities its delta will
  touch, or the written waiver and its reason
- **AND** the verdict appears in the approval preview alongside the proposed field values

#### Scenario: The executing skill refuses to edit before the artifact exists

- **WHEN** the executing skill is about to change a file outside the spec-driven workflow's own
  directory, in a repository whose policy requires the artifact
- **THEN** it stops until the change exists and its strict validation is green, and the plan it
  presents for approval carries the change identifier, the affected capabilities and the validation
  output

#### Scenario: A verdict is raised silently and lowered only by the user

- **WHEN** re-analysis shows the work touches more than the item's waiver assumed
- **THEN** the executing skill raises the verdict to requiring an artifact without asking
- **AND** the reverse move — dropping a required artifact to a waiver — stops for an explicit user
  decision rather than being taken by the assistant

### Requirement: Claim verification has a canonical home

The catalog SHALL contain one skill that governs how an agent establishes a fact before asserting or
acting on it: an ordered research ladder that starts with the cheapest source and ends by asking the
user, labels for what is verified, inferred and unknown, and a report for the case where the fact
cannot be found. The skill SHALL define a claim to include anything acted on as if true, not only
anything stated, so that delivering work the user did not ask for falls under the same rule as
inventing an API.

The doctrine SHALL be stack-agnostic. Skills that state a domain instance of it — reading a shipped
SDK stub, reading a chart template, refusing to guess a Project field — SHALL link to it rather than
restate the general rule.

#### Scenario: A fact that cannot be found is reported, not substituted

- **WHEN** the ladder is exhausted without establishing the fact
- **THEN** the agent produces a report naming the question, the commands run at each rung, the rungs
  that were unavailable and why, and what remains unknown
- **AND** no plausible substitute is emitted in place of the missing fact

#### Scenario: The doctrine degrades instead of failing when rungs are unavailable

- **WHEN** the environment provides no web-fetch or web-search tool
- **THEN** the ladder still runs over session context, the repository, the installed dependency and
  the tool itself, and the unavailable rungs are named in the report
- **AND** the absence of a rung is never treated as evidence that the unverified answer is probably
  correct

#### Scenario: The ladder declares when not to run

- **WHEN** a claim is already established in this session, or is a construct the surrounding
  toolchain would reject within seconds
- **THEN** the doctrine states that no research is owed, so that the rule is affordable on ordinary
  work rather than skipped wholesale as ceremony

#### Scenario: Unrequested work is treated as an unverified claim

- **WHEN** an agent adds a change the request did not ask for — an extra endpoint, a rename, an
  unrelated fix found along the way
- **THEN** the doctrine classifies it as an unverified claim about the user's intent, to be proposed
  rather than performed

### Requirement: A shipped checklist names the defect behind each row

A catalog skill that ships a catalog of failure modes SHALL record, for every row, the defect that
earned it, citable in this repository or in a named incident. A row whose origin cannot be named
SHALL be removed rather than kept.

#### Scenario: A row without provenance is not shipped

- **WHEN** a plausible-sounding failure mode is proposed for the catalog
- **THEN** it is added only if the defect that produced it can be cited, and is otherwise left out
- **AND** the growth rule states that a row whose origin column is empty is removed, not kept

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

### Requirement: The grounding rite is carried into context on correction

The catalog SHALL ship an enforcement artifact that re-injects the anti-guessing doctrine when a
prompt indicates a guess was caught or research is being demanded, in both of the catalog's working
languages. The artifact SHALL inform rather than block: it never denies a tool call, it persists
nothing, it needs no credentials, and an explicit waiver silences it.

The artifact SHALL state which moment it does **not** cover, and the documentation SHALL name the
layer that enforces evidence when the artifact is not wired, so that a reader does not mistake a
per-session convenience for a gate.

The artifact SHALL carry a self-test, exercised by the repository's own CI, that fixes the decisions
its design already assumes — a caught guess fires in each working language, a waiver silences, a
correction typed inside a slash command still fires, an implementation request stays silent — so
that an edit to its signal list is measured rather than trusted. A payload that is not a JSON object
SHALL be ignored: the artifact exits zero with no output and no traceback.

#### Scenario: A caught guess carries the doctrine into the turn

- **WHEN** a prompt says the assistant invented something, demands a source, asks where a fact came
  from, states that a flag or option does not exist, or says the work was out of scope
- **THEN** the hook injects the research ladder, the labelling rule, the not-found rule and the scope
  rule into that turn's context

#### Scenario: The reminder is silent when the user waives it

- **WHEN** the prompt explicitly permits an unverified answer
- **THEN** the hook produces no output, because the rite is the user's to waive

#### Scenario: The uncovered moment is declared, not implied

- **WHEN** the artifact is documented
- **THEN** the documentation states that it fires on corrections rather than on the guess itself,
  that no prompt regex can observe the moment a model is about to guess, and that the artifact does
  not run in CI or for a contributor who has not wired it

#### Scenario: The shipped hook carries a self-test and a malformed payload is ignored

- **WHEN** the hook is run with `--selftest`
- **THEN** it prints one OK/FAILED line per fixed decision plus a summary line and exits non-zero
  when any decision regressed, and the repository's CI runs that mode as a blocking step
- **AND** the case list fixes that a correction typed inside a slash command still fires, which is
  the opposite of the backlog hook's rule and is deliberate
- **AND** when the payload on stdin is a JSON array, a JSON string or empty, the hook exits zero
  with no output and no traceback

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

### Requirement: Code locale has a canonical home

The catalog SHALL contain one skill that governs which natural language each artifact of a change is
written in. It SHALL draw the boundary by what consumes the artifact, not by who wrote it: prose read
by humans — commit subjects and bodies, pull-request and issue text, documentation, code comments,
user-facing strings — follows the repository's working language, while anything a machine parses —
identifiers, file and module names, REST path segments and query parameters, database tables,
columns and indexes, enum values, event and topic names, configuration keys, structured-log field
keys and test names — is English and ASCII.

The doctrine SHALL be stack-agnostic. Skills that state a format-level naming convention for one
stack — a test-method naming pattern, a DTO naming triple, a config-file naming scheme — SHALL keep
that text and link to the canonical skill for the language rule rather than restating it.

The canonical skill SHALL ship the means of adopting the rule **per repository**, not only the
detector: a git pre-commit hook and a continuous-integration step, each copyable into a target
repository without cloning the catalog and without an assistant in the loop. Both SHALL invoke the
shipped detector rather than reimplement any of its tiers, and SHALL measure only the lines the
change adds. Whenever either artifact downloads the detector it SHALL do so from a tagged release of
the catalog — never from its default branch — and SHALL verify the file's digest before running it,
with the pin and its bump rule stated beside it; the hook MAY instead run a detector the machine
already holds (an explicit path, or the catalog's local clone) and SHALL state in its header that
those sources carry no pin. Both SHALL fix the shape of the diff they read so that a repository's or
a user's git configuration cannot empty it or alter its paths, and neither SHALL approve when it
could not measure — a diff command that fails, or a detector that exits without completing its scan,
fails the commit or the step. Each SHALL declare, in its own header, what it does not cover, and
SHALL name the exits the doctrine already defines — the inline waiver, the allowlist file, and the
deliberate bypass — so that a refused commit or a failed pull request tells its author what to do
next. The skill SHALL state which layer catches what: a session hook measures
the assistant's write, the pre-commit hook measures the human's commit, and the CI step measures the
pull request regardless of how it was produced.

#### Scenario: A prose rule and an identifier rule do not collide

- **WHEN** a repository's convention is to write commit subjects, issues and documentation in a
  language other than English
- **THEN** that convention is preserved, and only the machine layer is required to be English
- **AND** the skills carrying the prose rules gain a scope clause and a link, rather than being
  rewritten

#### Scenario: An untranslatable domain term is kept and enumerated

- **WHEN** a domain term has legal or regulatory meaning and no faithful English translation
- **THEN** the term is kept, ASCII-folded, inside English grammar
- **AND** it is legitimate only when the change's glossary lists it or the code carries an inline
  waiver naming the reason, so that "it is a domain term" cannot become an unbounded exception

#### Scenario: A foreign payload is mirrored at the boundary, not carried inward

- **WHEN** an external API's payload field names are in another language
- **THEN** those names are mirrored verbatim only inside the adapter or transport schema, and are
  translated to the English domain model at a single mapping point

#### Scenario: The translation decision is taken before implementation, not during it

- **WHEN** a backlog item written in another language will produce code
- **THEN** the item carries a glossary mapping each domain term to its identifier, with each row
  marked as harvested from the codebase or decided in the item
- **AND** the implementing agent takes names from that glossary instead of improvising a translation,
  and an unlisted term is raised as a question rather than translated on the spot

#### Scenario: Existing names migrate by tier rather than by rename

- **WHEN** a repository already contains identifiers in another language
- **THEN** the doctrine requires English only for new code, permits opportunistic renaming of
  internal names in files already being changed, and forbids renaming a contract-bearing name in
  place — routes, persisted columns, event names and deployed configuration keys change through an
  expand/contract window
- **AND** a whole-repository rename is named as the anti-pattern it is, because names referenced as
  strings fail silently at runtime

#### Scenario: A repository adopts the gate without the assistant

- **WHEN** the shipped pre-commit hook is installed in a repository and a commit is attempted whose
  staged diff adds an identifier in another language
- **THEN** the commit is refused with the detector's finding, and the message names the inline
  waiver, the allowlist file and the deliberate bypass
- **AND** the same commit with the inline waiver on the offending line is accepted
- **AND** the shipped CI step, pasted into that repository's workflow, fails a pull request whose
  added lines carry such an identifier and passes one whose added lines are English, downloading the
  detector from a tagged release and verifying its digest before running it

#### Scenario: A gate that cannot measure does not approve

- **WHEN** the CI step's base revision is absent from the clone, or the hook's detector exits without
  printing its findings line, or a git configuration would replace or empty the diff the detector reads
- **THEN** the step or the commit fails, naming the cause, instead of reporting zero findings
- **AND** a commit whose staged diff renames a file to a name in another language is refused on the
  new path, and a staged hunk carrying non-UTF-8 bytes is measured rather than aborting the detector

### Requirement: A shipped enforcement script declares what escapes it

A catalog skill that ships an executable check SHALL state, inside the check itself, the conditions
under which it does not fire, so that a passing run is not read as full coverage. The script SHALL
carry a self-test that injects one known defect per detection tier and fails when any goes
undetected, and any catalog-side wiring of that script SHALL be exercised by the catalog's own
validator self-test.

#### Scenario: A heuristic check states its blind spots

- **WHEN** a check relies on a curated word list, a morphology rule or a language it can tokenize
- **THEN** the words, patterns and file types that escape it are enumerated in the check
- **AND** the material outside its reach is identified as review-only rather than assumed compliant

#### Scenario: A precision failure is cheap to waive, not a blocked pipeline

- **WHEN** the check reports a finding the author judges correct as written
- **THEN** the finding names the file, the line and the token, and prints the exact waiver line to add
- **AND** the waiver requires a stated reason, so every exception is visible in review

#### Scenario: The shipped script is proven to run by the catalog that ships it

- **WHEN** the catalog documents that target repositories should wire the script into their own CI
- **THEN** the catalog's own CI executes that same script rather than a reimplementation of it, so
  the instruction is backed by a run and not by an assertion

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

### Requirement: The code-locale rite is enforced at the moment of the write

The catalog SHALL ship an enforcement artifact that measures the locale rule when a file is written,
not only when a diff is reviewed. Doctrine held in context and a check that must be invoked by hand
SHALL NOT be treated as enforcement: the repository already states, for its other two rites, that
enforcement must not depend on the assistant noticing a rule already in context.

The artifact SHALL run on the harness events that surround a file write, SHALL measure the written
path and the written content with the shipped check, and SHALL return its findings through the field
that harness reads for each event — established against the installed version, never assumed, since
plain standard output is not carried into context for those events and an envelope naming the wrong
event is dropped by the harness.

On the event that **precedes** the write, a gating finding — a Portuguese identifier in the added
content, or a Portuguese path segment in a path the write **creates** — SHALL deny the tool call, so
that the name never reaches the disk. A Portuguese segment in the path of a file that already exists
SHALL NOT deny on that event: the name is already on disk, existing names change through a
deprecation window and not through a blocked edit, and a denial that names a file the model did not
name has no exit but the allowlist. That path is still reported on the event that follows the write.
The denial reason SHALL list each finding and SHALL end with the three legitimate exits: the inline
waiver with a stated reason, the allowlist file, and an explicit informative mode for the whole
session. The reason SHALL fit the caps the installed harness applies to that field, in characters
and in lines, so that the exits are never the part that is cut. The same event SHALL NOT deny on an
advisory finding alone, because a word the English list does not know is a question and not a
verdict.

The inline waiver SHALL be honoured wherever the check itself honours it — on the line above the
name — whether that line is part of the added content or already sits in the file immediately above
the fragment the edit replaces. A denial whose first exit cannot be satisfied by following it
produces the blind second attempt the item lists as a risk.

On the event that **follows** the write, the artifact SHALL keep its informative behaviour: findings,
gating and advisory, reach the assistant as context and the tool call stands. The informative mode
SHALL restore that behaviour for both events: with it set, nothing is denied and the advisory arrives
as before.

The artifact SHALL be silent when the write is clean and SHALL persist nothing outside the
repository. Where the shipped check is absent, it SHALL exit silently rather than fail, because a
missing gate must not present itself as an error to the user. The artifact SHALL state which writes
it does not see — those made through a shell command rather than a write tool — so that a denied
write is not read as proof that no Portuguese name can land.

#### Scenario: A write that introduces a Portuguese name is denied before it lands

- **WHEN** the event that precedes a write carries a path or added content with a Portuguese
  identifier or path segment
- **THEN** the artifact answers with the permission decision the harness reads for that event, set to
  deny, and the file is not written
- **AND** the reason names each offending segment once, and ends with the inline waiver, the
  allowlist file and the informative mode as the three exits

#### Scenario: The same write with a stated waiver or an allowlisted name lands

- **WHEN** the added content carries the inline waiver with a reason on the line above the name, or
  the name or path is listed in the allowlist file found from the working directory
- **THEN** the artifact produces no output on either event, and the write lands in silence

#### Scenario: An edit to a file that already carries a Portuguese name is not denied for the name

- **WHEN** the event that precedes an edit names a file that already exists and whose path carries a
  Portuguese segment, and the added content is English
- **THEN** the artifact produces no output on that event and the edit lands
- **AND** the event that follows the write still reports the path, so the legacy name stays visible
  without blocking its maintenance

#### Scenario: A waiver already on the line above the edited fragment is honoured

- **WHEN** the event that precedes an edit carries added content with a Portuguese identifier on its
  first line, and the file line immediately above the fragment being replaced carries the inline
  waiver with a reason
- **THEN** the artifact denies nothing, exactly as it would had the waiver been part of the added
  content

#### Scenario: The informative mode restores the advisory

- **WHEN** the informative mode is set for the session and a write carries a gating finding
- **THEN** the event that precedes the write denies nothing, and the event that follows it reports
  the findings as context exactly as it does without the mode

#### Scenario: An unrecognised word alone never denies

- **WHEN** the only findings on a write are words the English list does not know
- **THEN** the event that precedes the write denies nothing, and the event that follows it reports
  them as advisory, so the write is never blocked on a question the check cannot answer

#### Scenario: A write that introduces a Portuguese name is reported

- **WHEN** a file is written whose path or added content carries a Portuguese identifier and the
  event that follows the write fires
- **THEN** the findings reach the assistant as context for the next turn, naming the offending
  segments and the waiver that silences them

#### Scenario: The gate informs and never blocks

- **WHEN** the artifact reports findings on the event that follows the write
- **THEN** the tool call stands and the findings reach the assistant as context, as before: the
  denial belongs to the event that precedes the write, and the informative mode restores this
  behaviour for both events

#### Scenario: A clean write is silent

- **WHEN** the written path and content are English
- **THEN** the artifact produces no output at all on either event, so the reminder never becomes
  background noise

#### Scenario: A file type without a language profile still has its path measured

- **WHEN** the written file's extension has no language profile in the check
- **THEN** the path is still measured, and the content is reported as skipped rather than as passing

#### Scenario: A payload the artifact cannot read produces no error

- **WHEN** the payload is missing, malformed, names no written file, or names no event
- **THEN** the artifact exits silently and successfully, writing no state and requiring no
  credentials, and a payload that names no event is treated as the informative one, because in doubt
  the artifact informs and never denies

### Requirement: The rite gates proof that the artifact was exercised

The repository's spec-driven rite SHALL require every active change to record that the artifact it
touches was **run through the path its user takes**, before the change can be closed. Reading,
probing, uniform frontmatter and a green strict validation SHALL NOT be treated as proof of delivery:
each of them can hold while the artifact has never been executed once.

The record SHALL live in its own mandatory task group, positioned before the quality-review group so
that what the simulation finds is available to the review that follows it, and its presence SHALL be
enforced by the same script that enforces the other mandatory groups, because the OpenSpec CLI
validates delta-spec format only.

The group's boxes SHALL be checked in **shape**, per kind rather than uniformly, following the
measurement that already rejected a uniform rule for the evidence group: an entry point together with
an observed output fragment; a case matrix expressed as counts; and what escaped, or an explicit
statement that nothing did. A change that touches no runtime artifact SHALL satisfy the group by
stating that explicitly, so that documentation-only work is never pushed into inventing a simulation.

The gate SHALL declare, in its own header, that it proves the record's shape and never its honesty —
a box filled with invented output passes it, and the reviewer is what judges the content.

#### Scenario: A change that ships a runtime artifact records its exercise

- **WHEN** an active change touches a skill, a hook or a shipped script
- **THEN** its task list carries the simulation group, naming the entry point that was exercised and a
  fragment of the output that was observed
- **AND** the counts of the case matrix are recorded — what had to fire and did, what had to stay
  silent and did, and which known escapes stayed silent

#### Scenario: A documentation-only change closes the group explicitly

- **WHEN** an active change touches no runtime artifact
- **THEN** the group is satisfied by stating that explicitly
- **AND** the change is not required to invent a simulation, because a padded record is worth less
  than an honest absence

#### Scenario: A missing or misplaced group fails the gate

- **WHEN** an active change's task list lacks the simulation group
- **THEN** the rite gate fails with a file-specific error naming the missing group
- **AND** the first-group and last-group rules of the existing mandatory groups are unchanged

#### Scenario: A ticked box that states a conclusion instead of an observation fails

- **WHEN** a box in the simulation group is ticked without naming an entry point and an observed
  output, without counts, or without naming an escape or declaring none
- **THEN** the evidence gate reports a file-specific finding naming the box and what is missing

#### Scenario: The shipped catalog validator is a gate, not a suggestion

- **WHEN** continuous integration validates this repository's plugins and skills with the vendor's
  own validator
- **THEN** the step fails the build on a finding, and pins the validator's version, so that a gate is
  neither silently disabled nor broken by an upstream release

### Requirement: The identifier-locale check asks whether the word is English

The shipped identifier-locale check SHALL decide a name by two questions, not one. The first — is
this word in the known foreign lexicon? — SHALL keep gating, because its confidence is high. The
second — is this word English? — SHALL report every segment it does not recognize, so that the
default answer to an unknown word is *surfaced* rather than *approved*.

The second question SHALL be answered from a word list shipped with the check, not from the host's
dictionary, so that the same input produces the same finding on a maintainer's machine, in
continuous integration and inside an editor hook. The list SHALL be public-domain or permissively
licensed, and SHALL record its source, licence and date in the repository. Vocabulary that belongs to
programming rather than to English SHALL live in a separate list from the natural-language one, so
that either can be audited on its own.

A segment that decomposes into two known words SHALL be treated as known, so that ordinary compounds
do not become manual entries and the curated list does not become the same open-vocabulary chase the
foreign lexicon already is.

Findings from the second question SHALL be **advisory**: reported and counted separately, and SHALL
NOT change the exit code unless the caller asks for it. Whole-tree enforcement of a closed-world
question turns a legacy repository red on day one, and a check that fails everything is switched off
within a week — the same reason the check's diff mode exists. A segment already reported by the
first question SHALL NOT be reported again by the second.

#### Scenario: A foreign word outside the lexicon is surfaced

- **WHEN** an identifier or path segment carries a word the foreign lexicon does not know and the
  English list does not contain
- **THEN** the check reports it as an advisory finding naming the segment
- **AND** the exit code is unchanged, unless the caller asked for those findings to gate

#### Scenario: English, programming vocabulary and compounds stay silent

- **WHEN** the segment is an English word, an entry of the programming vocabulary, a kept domain
  term, an allowlisted entry, or a compound of two known words
- **THEN** the check reports nothing for it

#### Scenario: One segment, one finding

- **WHEN** a segment is caught by the foreign-lexicon question
- **THEN** it is not also reported by the English question, so that the higher-confidence tier is the
  one the reader sees

#### Scenario: The word list is deterministic and declared

- **WHEN** the check runs on any machine
- **THEN** it answers from the list shipped beside it rather than from a host dictionary
- **AND** the list's source, licence and date are recorded, and an explicit override names a
  different list, failing loudly when that list cannot be read

#### Scenario: What neither question reaches is declared

- **WHEN** a word exists in both languages, such as a name spelled the same in each
- **THEN** it passes both questions, and the check's own limits state that it does, so a clean run is
  never read as full compliance

### Requirement: Publication does not depend on the interval between merges

The catalog's release automation SHALL evaluate the tip of the release branch, not the commit that
triggered the run. A run whose triggering commit has been superseded by a later merge SHALL still
publish whatever is due, so that a release is never lost or silently deferred because two pull
requests landed close together.

Where the automation refuses to publish because its checkout is behind the remote branch, the run
SHALL fail rather than report success. That refusal is indistinguishable, from the outside, from the
legitimate outcome of having nothing to publish: both leave no new tag and both exit zero. The
distinction SHALL be made by the pipeline, not left to whoever reads the run list.

A push that legitimately produces no release SHALL remain green, so that the guard does not turn
every documentation merge red.

The guard SHALL state, inside itself, what it does not cover — the same rule this capability already
imposes on the repository's other checks.

#### Scenario: A superseded commit still gets its release

- **WHEN** a commit that warrants a release is merged into the release branch and a second merge
  lands before that commit's release job runs
- **THEN** the release job publishes the version due, because it evaluates the branch tip rather
  than the commit that triggered it

#### Scenario: A refusal to publish is visible

- **WHEN** the release tool reports that the checked-out branch is behind the remote one and
  therefore publishes nothing
- **THEN** the job fails and names the log line that proves it, instead of exiting success with no
  new tag

#### Scenario: Nothing to publish stays green

- **WHEN** a push to the release branch carries only commit types that produce no version bump
- **THEN** the job succeeds with no release, and the guard does not fire

#### Scenario: The guard declares its own blind spot

- **WHEN** the guard recognises the refusal by matching text emitted by a third-party tool
- **THEN** the step states that an upstream wording change would silence it, so a passing run is not
  read as proof that the condition cannot occur

### Requirement: A published cost claim carries re-runnable backing

Where the catalog publishes a claim about the cost of a technique — that one approach is cheaper,
that a property triggers layout or paint, that an approach holds a frame budget — that claim SHALL
be backed either by an artifact in this repository that a reader can run, or by a named published
benchmark. A cost claim with neither SHALL be removed rather than softened into a hedge, because a
hedged guess reads as knowledge and is not.

The backing artifact SHALL live outside the directory the catalog publishes to consumers, so that
evidence is versioned and reviewable without being shipped to every project that enables a plugin.

Every recorded measurement SHALL state what was measured, by what method, and in which browser and
version. A number without its method is not re-runnable and therefore is not evidence.

The record SHALL state what it does not cover — the browsers, devices or conditions the measurement
did not reach — so that a passing number is not read as a general guarantee.

#### Scenario: A cost claim without backing does not ship

- **WHEN** a skill would assert that one technique is cheaper than another
- **THEN** the assertion carries a runnable artifact in this repository or a named published
  benchmark, or it does not appear at all

#### Scenario: Evidence does not reach the consumer's project

- **WHEN** a reader enables one of the published plugins
- **THEN** the backing artifacts are not part of what they receive, because they live outside the
  directory the generator publishes from

#### Scenario: A measurement states its method

- **WHEN** a measurement is recorded as evidence
- **THEN** it names what was measured, how, and the browser and version it ran in

#### Scenario: The reach of a measurement is declared

- **WHEN** a measurement covers one browser or one device class
- **THEN** what it did not cover is written beside it, so the number is not read as universal

#### Scenario: A contested fact is measured rather than cited

- **WHEN** the available sources disagree about a technique's cost
- **THEN** the disagreement is resolved by measurement recorded here, or the question is reported
  as open with the attempts that failed to settle it

### Requirement: A skill que representa objetos declara o regime antes de desenhar

Uma skill do catálogo que produza representação visual de um objeto SHALL classificar o pedido em
um ou mais REGIMES antes de qualquer geometria, e SHALL carregar o esquema de cada regime
classificado. Um regime é um tipo de sistema — corpo articulado, estrutura oscilante forçada,
campo de ondas dispersivo, ensemble balístico — e não um domínio temático. A classificação por
domínio SHALL NOT substituir a classificação por regime, porque a evidência medida em
`research/svg-animation/method.md` mostra que cerca de três quartos dos defeitos registrados não
eram falta de conhecimento de domínio.

#### Scenario: pedido que combina dois regimes

- **WHEN** o pedido é uma árvore ao vento
- **THEN** a skill classifica em `growth-structure` para a geometria e em `driven-oscillator` para
  o movimento, e carrega os dois esquemas
- **AND** nenhum dos dois esquemas é um esquema de "vegetação"

#### Scenario: regime sem esquema publicado

- **WHEN** o pedido cai num regime para o qual não existe esquema em `references/regimes/`
- **THEN** a skill diz qual regime faltou e o que não pode garantir sem ele
- **AND** SHALL NOT prosseguir apresentando o resultado como se o regime tivesse sido coberto

### Requirement: Toda grandeza usada carrega procedência

Uma skill que use números para construir ou animar SHALL marcar cada grandeza como `measured`,
`derived from <X>` ou `assumed`, e uma grandeza `assumed` SHALL aparecer na entrega. A regra existe
porque o defeito mais caro registrado foi amplitude inventada escrita ao lado de frequência medida,
sem nada distinguindo as duas: 11 Hz com 14 graus dá 968 graus por segundo, uma ponta de galho a
27% da velocidade do vento, sustentada.

#### Scenario: número sem fonte

- **WHEN** uma grandeza necessária não tem valor publicado nem derivação
- **THEN** ela é marcada `assumed` e aparece na entrega com o valor adotado
- **AND** SHALL NOT ser apresentada junto das medidas sem distinção

### Requirement: Perspectiva é portão, não observação

Uma skill que represente um objeto SHALL fixar a vista antes da geometria e SHALL expressar cada
número cinemático nos eixos dessa vista. Quando o eixo principal do mecanismo não for visível na
vista escolhida, quando o objeto tiver mais de uma vista canônica, ou quando o tamanho de leitura
mudar o que precisa existir, a skill SHALL perguntar em vez de escolher.

#### Scenario: eixo do mecanismo invisível na vista

- **WHEN** o pedido é um golfinho visto de cima, e a remada do golfinho é vertical
- **THEN** a skill aponta que o movimento característico não aparece nessa vista e pergunta
- **AND** SHALL NOT desenhar a remada como se fosse lateral

### Requirement: Mudança em algo que já funcionava passa por comparação lado a lado

Quando uma skill alterar um artefato que já funcionava, SHALL produzir uma comparação lado a lado
entre a versão nova e a que ela substitui antes de manter a mudança. Verificar contra a lei diz que
a versão nova é verdadeira; não diz que a velha era melhor. Três versões sucessivas da árvore
passaram por todos os portões existentes — cinemática direta, rastreio de movimento, velocidade de
pico e custo — e cada uma era pior que a anterior.

#### Scenario: correção que regride

- **WHEN** uma alteração é verificada contra a física e passa
- **THEN** a comparação lado a lado com a versão anterior é apresentada antes de manter
- **AND** se a anterior for melhor, a alteração é revertida ou reduzida

### Requirement: A skill que representa objetos escolhe a tecnologia a partir do regime

Uma skill que produza representação visual SHALL derivar a tecnologia de renderização das respostas
do esquema de regime — quantos elementos se movem, se a geometria é reconstruída a cada quadro, e se
a cena é plana — e SHALL NOT escolhê-la pelo tipo do objeto. Uma alegação de custo sobre uma
tecnologia SHALL vir de medição neste repositório ou ser marcada como não medida, com o que decidiria
a questão. Quando a resposta for tridimensional, a skill SHALL repassar às skills que o catálogo já
carrega para 3D em vez de reimplementá-lo.

#### Scenario: mesmo animal, regimes diferentes

- **WHEN** o pedido é um bando de dois mil pássaros
- **THEN** a skill classifica em `ballistic-ensemble` e escolhe canvas, citando a medição de 466 ms/s
  contra 125 ms/s
- **AND** para um único pássaro classifica em `articulated-body` e escolhe SVG
- **AND** SHALL NOT justificar nenhuma das duas escolhas por se tratar de "um animal"

#### Scenario: tecnologia sem medição no repositório

- **WHEN** a escolha aponta para uma ferramenta que este repositório nunca mediu
- **THEN** a recomendação diz explicitamente que não foi medida e o que decidiria
- **AND** SHALL NOT apresentar número de desempenho que ninguém aqui rodou

### Requirement: O gatilho para perguntar é derivável, não uma impressão

Uma skill que represente objetos SHALL perguntar sobre ponto de vista, registro visual, tamanho de
leitura ou o que o objeto está fazendo quando a ausência dessa informação mudaria a GEOMETRIA, e
SHALL NOT tratar a decisão de perguntar como uma questão de confiança do modelo.

#### Scenario: registro visual muda a geometria

- **WHEN** o pedido não diz o registro e o objeto tem marcas de reconhecimento que só existem em
  alguns registros
- **THEN** a skill pergunta antes de desenhar
- **AND** se prosseguir sem resposta, marca o registro adotado como `assumed` na entrega

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

### Requirement: The code-locale rite closes the turn, not only the write

The catalog SHALL ship an enforcement artifact that measures the locale rule on the **result** of a
turn — the repository's uncommitted diff — and not only on the tool that wrote it. A write that
reaches the disk outside the harness's edit tools (a shell heredoc, `sed`, a script) is never seen by
the write-time artifact, so the rite that covers only the write SHALL NOT be treated as covering the
turn.

The artifact SHALL run on the harness event that ends a turn, SHALL read the working directory from
the payload, and, when that directory is inside a git work tree, SHALL build the uncommitted diff —
tracked files against the current commit, plus every untracked file the repository does not ignore,
each as an added file — and measure it with the shipped identifier-locale check in its diff mode,
honouring the repository's allowlist and the check's own exclusions. It SHALL measure only what the
turn left uncommitted: history and untouched lines never enter.

When the diff carries a gating finding and the payload does not mark the block as already in
progress, the artifact SHALL prevent the turn from ending, through the field the installed harness
reads for that event — established against the installed version, never assumed — and its reason
SHALL list every finding and the legitimate exits (an inline waiver with a reason, the repository
allowlist, the session-wide informative mode). When the payload marks the block as already in
progress, the artifact SHALL NOT block again: it SHALL report what remains as a message and let the
turn end, because the second turn is the last chance and never a loop.

The artifact SHALL build the diff in a shape that does not depend on the user's git configuration:
no external diff driver or text conversion, unquoted non-ASCII paths, fixed `a/` and `b/` prefixes,
no colour — so that a setting in `~/.gitconfig` can neither silence the gate nor make it report a
path that does not exist. Untracked files the check itself calls vendored, and empty or binary
files, SHALL be skipped before git is asked, so they consume neither the measuring budget nor a
process each.

The artifact SHALL be silent — no output, exit zero, under one second — outside a git work tree, on
an empty diff, on advisory-only findings, in the informative mode, and on a payload it cannot read.
It SHALL cap the diff it measures at a declared number of lines and SHALL say so when the cap was
reached, never truncating in silence: in its reason when the measured part has a finding, and as a
block of its own — once, then a message on the Stop that follows — when the measured part is clean,
because an unmeasured tail is not a clean result. It SHALL carry a self-test exercised by the
repository's CI, exercised also under a git configuration that alters the diff's shape, and SHALL
declare what escapes it: a file committed inside the same turn, a repository outside the working
directory, and the event's different name inside a subagent.

#### Scenario: A heredoc-written Portuguese file blocks the end of the turn

- **WHEN** a turn wrote `servico_cliente.py` with `def buscar_cliente(id_usuario)` through a shell
  heredoc, so no write-time hook ran, and the turn ends with the file uncommitted
- **THEN** the artifact answers with the block decision the installed harness reads for that event,
  and the reason names the path, the identifiers, and the three exits

#### Scenario: Once renamed, the turn ends

- **WHEN** the same file has been renamed and its identifiers translated (or waived with a stated
  reason) and the turn ends again
- **THEN** the artifact produces no output and the turn ends

#### Scenario: An active block is not repeated

- **WHEN** the payload carries `stop_hook_active: true` and the diff still has a gating finding
- **THEN** the artifact does not block; it emits a message listing what remains and exits zero

#### Scenario: Outside a git work tree the artifact is silent

- **WHEN** the working directory in the payload is not inside a git repository
- **THEN** the artifact produces no output and exits zero

#### Scenario: The informative mode silences the gate

- **WHEN** the session runs with the informative mode set and the diff has a gating finding
- **THEN** the artifact produces no output and exits zero, because the mode is the user's to set

#### Scenario: A diff over the declared cap says so

- **WHEN** the uncommitted diff has more lines than the declared cap and a gating finding within it
- **THEN** the reason states that the diff was truncated at the cap and that the rest was not
  measured, so the truncation is never silent

#### Scenario: A clean measured part over the cap is not a clean result

- **WHEN** the uncommitted diff has more lines than the declared cap and the part within the cap has
  no gating finding — clean or generated content that sorts ahead of a Portuguese file, for instance
- **THEN** the artifact still blocks the end of the turn once, its reason says the tail was not
  measured and how to measure it, and on the Stop that follows it reports as a message and lets the
  turn end

#### Scenario: The user's git configuration does not change what is measured

- **WHEN** `~/.gitconfig` sets an external diff driver, mnemonic prefixes or the default path quoting,
  and the turn edited a tracked file or wrote an untracked file whose name carries a non-ASCII letter
- **THEN** the artifact blocks as it would under a blank configuration, and the reason names the
  repository-relative path exactly as it is on disk

