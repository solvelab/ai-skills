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

### Requirement: The grounding rite is carried into context on correction

The catalog SHALL ship an enforcement artifact that re-injects the anti-guessing doctrine when a
prompt indicates a guess was caught or research is being demanded, in both of the catalog's working
languages. The artifact SHALL inform rather than block: it never denies a tool call, it persists
nothing, it needs no credentials, and an explicit waiver silences it.

The artifact SHALL state which moment it does **not** cover, and the documentation SHALL name the
layer that enforces evidence when the artifact is not wired, so that a reader does not mistake a
per-session convenience for a gate.

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

The artifact SHALL run on the harness event that follows a file write, SHALL measure the written
path and the written content with the shipped check, and SHALL return its findings through the field
that harness reads for that event — established against the installed version, never assumed, since
plain standard output is not carried into context for that event.

The artifact SHALL be silent when the write is clean, SHALL NOT block the tool call, and SHALL
persist nothing outside the repository. Where the shipped check is absent, it SHALL exit silently
rather than fail, because a missing gate must not present itself as an error to the user.

#### Scenario: A write that introduces a Portuguese name is reported

- **WHEN** a file is written whose path or added content carries a Portuguese identifier
- **THEN** the findings reach the assistant as context for the next turn, naming the offending
  segments and the waiver that silences them

#### Scenario: A clean write is silent

- **WHEN** the written path and content are English
- **THEN** the artifact produces no output at all, so the reminder never becomes background noise

#### Scenario: The gate informs and never blocks

- **WHEN** the artifact reports findings
- **THEN** the tool call stands, and the decision to keep the name belongs to the user, as it does
  for the catalog's other rites

#### Scenario: A file type without a language profile still has its path measured

- **WHEN** the written file's extension has no language profile in the check
- **THEN** the path is still measured, and the content is reported as skipped rather than as passing

#### Scenario: A payload the artifact cannot read produces no error

- **WHEN** the payload is missing, malformed, or names no written file
- **THEN** the artifact exits silently and successfully, writing no state and requiring no credentials

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

