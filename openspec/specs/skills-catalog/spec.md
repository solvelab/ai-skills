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

#### Scenario: A code-change request carries the rite into context

- **WHEN** a prompt asks for an implementation, fix, refactor or removal
- **THEN** the shipped `UserPromptSubmit` hook injects the rite reminder naming `/backlog` as the
  entry point and `/execute-backlog` as the second step
- **AND** the reminder states that diagnosis is free and that an approved plan is not a waiver

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

#### Scenario: Entry point is discoverable from the execution skill

- **WHEN** a user reads the `execute-backlog` description
- **THEN** it names `backlog` as the step that produces the item it consumes

#### Scenario: Exit is discoverable from the creation skill

- **WHEN** a user reads the `backlog` description
- **THEN** it names `execute-backlog` as the step that turns the created item into a pull request

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
so that a reviewer can re-run it. The enforcing script SHALL state that it verifies the presence and
position of the group and not the truth of its contents.

#### Scenario: A change without recorded evidence fails the build

- **WHEN** an active change's task list lacks the evidence group, or carries it somewhere other than
  the first task group
- **THEN** the rite gate script fails with a file-specific error naming the missing or misplaced
  group, and the build does not pass

#### Scenario: The gate declares what it cannot check

- **WHEN** the gate passes
- **THEN** the script's own header states that a ticked box with no probe behind it is
  indistinguishable from one with, so that a green run is not read as verified evidence

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

