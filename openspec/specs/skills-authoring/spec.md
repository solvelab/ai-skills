# skills-authoring Specification

## Purpose

Conventions governing how every skill in this catalog is written, for human contributors and AI
agents alike: uniform frontmatter metadata, English as the catalog locale, a single canonical home
for each cross-cutting rule (siblings link instead of restating), and empirically verified claims
about external tool behavior. CI and the skills-rite Quality Gates enforce these requirements on
every change that touches `skills/`.
## Requirements
### Requirement: Single canonical home per rule

Every cross-cutting rule SHALL be defined in exactly one skill and referenced by link (with at most a
one-line summary) everywhere else. Canonical map: trust boundary → `fivem-lua`;
fallback/negative-cache/clamping → `backend-resilience`; REST negative-testing checklist →
`api-resilience-testing`; adversarial methodology → `bug-hunter`; OpenSpec lifecycle → `openspec`;
claim verification, the research ladder, not-found reporting and the off-script scope guard →
`verify-before-claiming`.

#### Scenario: Orchestrator skill references instead of restating

- **WHEN** `openspec-drivezone` describes its Fallback and Bug-Hunter gates
- **THEN** each gate row links to the canonical skill with a one-line summary
- **AND** no mechanism list from a sibling skill is reproduced inline

#### Scenario: A stack-specific instance links to the general rule

- **WHEN** a skill states a domain instance of a rule that has a canonical home elsewhere — reading
  the CSP EmmyLua stub before calling an API, or reading the chart template before emitting a field
- **THEN** the instance keeps its stack-specific text and gains one sentence linking to the canonical
  skill for the general form, rather than reproducing the general rule inline

#### Scenario: Doctrine that acquires a canonical home stops being restated

- **WHEN** a rule previously stated in full inside one skill is given a canonical home
- **THEN** the original statement is reduced to a link with at most a one-line summary, so the
  catalog carries the doctrine exactly once

### Requirement: Uniform frontmatter metadata

Every `skills/<name>/SKILL.md` SHALL carry: `name` (== directory), `description` (folded block scalar),
`metadata.author: solvelab`, `metadata.version` (semver), `metadata.category` from the controlled set
{backend, testing, fivem, game, devops, docs, git, process, nui, frontend, tooling}, `license: MIT`,
and `compatibility`.

The controlled set is the one the CI frontmatter check enforces. When the two disagree, the gate is
authoritative and this document is corrected, because a contributor who follows a document that is
behind its gate writes a change the build rejects.

#### Scenario: CI rejects incomplete frontmatter

- **WHEN** a skill is added or edited without `metadata.version`, `license`, or with a category outside
  the controlled set
- **THEN** the CI validate job fails with a file-specific error

#### Scenario: The documented set matches the enforced set

- **WHEN** a category is added to the CI frontmatter check
- **THEN** this requirement is updated in the same change, so no contributor reads a controlled set
  that is narrower than the one the build accepts

### Requirement: English as catalog locale

All skill content SHALL be written in English.

#### Scenario: Project-specific skill is still English

- **WHEN** a skill documents a project-specific workflow (e.g. `openspec-drivezone`)
- **THEN** its content is in English regardless of the project's working language

### Requirement: Verified enforcement claims

Any claim a skill makes about external tool behavior (CLI validation, runtime checks, generated
output) SHALL be empirically verified before publication, and every enforcement mechanism the skill
describes SHALL state where enforcement actually happens (tool-level, script, CI, or convention-only).

#### Scenario: Tool-behavior claim is probe-tested

- **WHEN** a skill states that a tool blocks, validates, or refuses an input
- **THEN** the claim is backed by a reproducible probe against the tool version in use, and the skill
  names the enforcing layer explicitly

#### Scenario: Advisory mechanisms are not sold as hard gates

- **WHEN** a mechanism only guides generation or relies on convention (e.g. schema templates feeding
  artifact scaffolding)
- **THEN** the skill labels it advisory and points to the structural gate (script/CI) that makes it
  mandatory, or states that none exists

### Requirement: Prescribed numbers carry the rule that produces them

A skill that prescribes numeric configuration SHALL publish the rule, formula or computation the
target system uses, so an adopter can derive and audit the values instead of copying them. A
configuration snapshot taken from a running deployment SHALL NOT be presented as a validated
baseline unless it has been re-derived from that rule; "it works in production" is not derivation,
because a defect that only manifests beyond the conditions reached in production looks identical to
a correct value.

Where the target system can compute the value itself, the skill SHALL say so and SHALL prefer that
over hardcoded constants.

A prescribed block SHALL NOT mix settings from different domains under one heading when the system's
own schema groups them together; a setting whose effect lies outside the section's subject SHALL be
called out separately, with the effect named.

#### Scenario: Baseline copied from a deployment

- **WHEN** a skill documents configuration values observed on a working production system
- **THEN** each value is either derived from the published rule or marked as an unverified
  observation, and values that only hold for that deployment's scale are labelled with the
  conditions they were verified under

#### Scenario: The system can derive the value itself

- **WHEN** the target system computes a sane default when a setting is left empty or zero
- **THEN** the skill recommends that default and shows the computation, rather than prescribing a
  constant that silently diverges as the surrounding configuration changes

#### Scenario: A setting is filed under a misleading heading

- **WHEN** the system's schema groups a setting with unrelated ones (for example, an access limit
  nested under a performance-tuning block)
- **THEN** the skill documents its real effect separately from the block, so a reader tuning that
  block does not carry the setting along by copy-paste

### Requirement: Simulated failure behaviour

Any claim a skill makes about how prescribed code behaves under failure (timeout, dependency down,
partial payload, concurrency, replay, hostile input) SHALL be backed by a reproducible run of that
code against that failure before publication, and the skill SHALL state the measured outcome where it
motivates a rule.

A claim about a **performance or concurrency property** — blocking, serialization, throughput — SHALL
likewise be measured rather than asserted, and the measurement's conditions stated, so a reader can
reproduce or refute it.

#### Scenario: Prescribed snippet is exercised against the failure it claims to handle

- **WHEN** a skill ships a code snippet as the recommended handling for a failure mode
- **THEN** the snippet is run against that failure mode and the observed result is recorded
- **AND** if the result contradicts the surrounding doctrine, the snippet is corrected before the
  skill is published

#### Scenario: A quantified claim carries its measurement

- **WHEN** a rule is justified by a cost, a count, or a latency (e.g. "N callers each pay the full
  timeout", "worst case is X seconds")
- **THEN** the skill states the measured number and the conditions it was measured under, rather than
  an unquantified assertion

#### Scenario: A concurrency claim is demonstrated, not asserted

- **WHEN** a rule rests on a property like "this blocks the event loop" or "these serialize"
- **THEN** the property is demonstrated with a runnable measurement and the skill records the numbers
  and the conditions, instead of relying on the reader trusting the mechanism

### Requirement: Description agrees with body

A skill's frontmatter `description` SHALL NOT state a policy that its body contradicts. The
description is loaded into every session and drives skill selection, so a conflict there is resolved
by the model, not by the author.

#### Scenario: Conflicting policy is caught before publication

- **WHEN** a skill's description asserts a behaviour ("always creates X", "never does Y") that a rule
  in the body qualifies or reverses
- **THEN** the conflict is resolved to a single policy and stated once, in the body, with the
  description summarizing it rather than restating a stronger claim

#### Scenario: Behavioural promises are attributed to the governing rule

- **WHEN** a skill's output set depends on a condition (a decision table, a detected file, a user
  request)
- **THEN** the description names the condition rather than promising an unconditional result

### Requirement: Code blocks compile or are marked

A fenced code block tagged with a compiled or type-checked language SHALL either be a complete module
that compiles against the skill's stated stack, or carry an explicit marker identifying it as an
illustrative excerpt. A block SHALL be tagged with the language it actually contains.

#### Scenario: Excerpt is distinguishable from broken code

- **WHEN** a skill shows a fragment that is not a complete module (a bare JSX element, a partial
  function body)
- **THEN** the block carries an excerpt marker, so a reader and a compile check can both tell it apart
  from a block that is simply wrong

#### Scenario: Compilable block is verified by compiling it

- **WHEN** a skill ships a block presented as usable code in a compiled language
- **THEN** it is extracted and compiled against the declared dependency versions before publication,
  and unresolved imports or type errors are fixed rather than shipped

### Requirement: Versioned external APIs are pinned

A skill whose content targets an external API **or command-line tool** with breaking releases SHALL
state the exact versions it was verified against, and SHALL name any known upcoming rename or removal
that will invalidate it. For a skill that instructs the agent to run a CLI, the commands and flags it
prescribes SHALL be probed against that tool before publication.

#### Scenario: Reader can tell which era the code targets

- **WHEN** a skill documents a library API
- **THEN** the skill names the library versions its examples were verified against, rather than
  leaving the reader to infer it

#### Scenario: A known breaking change is disclosed, not silently absorbed

- **WHEN** the upstream has announced a rename or removal affecting the skill's examples
- **THEN** the skill names it and where it applies, instead of presenting the current form as timeless

#### Scenario: Prescribed CLI commands are probed, not assumed

- **WHEN** a skill instructs the agent to run a command with specific subcommands and flags
- **THEN** each subcommand and flag is checked against the installed tool before publication, and the
  tool version the check ran against is recorded

#### Scenario: Tool guidance contradicted by the tool is corrected, not repeated

- **WHEN** a tool's own output advertises behaviour its implementation does not deliver
- **THEN** the skill states the probed behaviour and the version it holds for, rather than repeating
  the tool's claim

### Requirement: Authoring rules are machine-enforced

The mechanically checkable authoring rules SHALL be enforced by a script wired into CI, and that
script SHALL carry a self-test that injects one known defect per check and asserts detection. Rules
that cannot be checked mechanically SHALL be identified as review-only rather than left to imply
coverage. A check that covers only **part** of its rule SHALL state the uncovered part in the check
itself, so that a passing run is not read as full coverage.

#### Scenario: A violation fails the build

- **WHEN** a change introduces a broken reference, an unparseable code block, a mistagged fence, or a
  description that contradicts its body
- **THEN** the CI validate job fails and names the skill, the check and the offending content

#### Scenario: A disabled check is caught

- **WHEN** a change to the validator silently stops one of its checks from firing
- **THEN** the self-test fails, because a catalog with zero findings and a check that cannot fire are
  otherwise indistinguishable

#### Scenario: A missing tool is reported, not passed over

- **WHEN** a checker dependency is unavailable in the environment
- **THEN** the affected check is reported as skipped in the output instead of counting as a pass

#### Scenario: Partial coverage is declared, not implied

- **WHEN** a check enforces its rule only under some condition (a size threshold, a file type, a
  language it can parse)
- **THEN** the condition and what escapes it are stated in the check, and skills falling outside it
  are reviewed by hand rather than assumed compliant

### Requirement: Checklists are scored against field defects

A skill that prescribes a checklist or a rite SHALL be scored against defects actually found in the
field, and every class the checklist would have missed SHALL be added together with the defect that
earned it. A checklist item without a traceable origin SHALL NOT be added.

A skill that prescribes a **step** SHALL also give the command that performs it whenever a plausible
wrong command exists, and SHALL name the wrong one. A step stated without a method is executed by
whatever command looks obvious, which is how a wrong one becomes the de facto instruction.

#### Scenario: A missed class is added with its provenance

- **WHEN** a defect is found by some means other than the checklist that claims to cover its area
- **THEN** the class it belongs to is added to the checklist, recorded with the defect that earned it
- **AND** an item that cannot name the defect behind it is removed rather than kept

#### Scenario: The scoring is stated, not implied

- **WHEN** a checklist is revised after an audit
- **THEN** the change records which defects were scored against it and which of them it would have
  caught as previously written

#### Scenario: A prescribed step carries its command

- **WHEN** a step instructs the agent to check, resolve or look something up, and more than one
  command could plausibly do it
- **THEN** the correct command is given, and any plausible-but-wrong alternative is named as forbidden
  with the failure it produces

### Requirement: Triggers live in the description, not the body

A skill SHALL NOT carry a `How to Use`, `Trigger Test Cases`, `Prompt` or `Usage` section in its
`SKILL.md`. Such a section is read only after the skill has already been selected, so it cannot
influence routing, and it costs context on every invocation. Trigger and anti-trigger information
SHALL live in the frontmatter `description`, which is what the model reads when choosing a skill.

#### Scenario: A trigger case not present in the description is folded in, not filed away

- **WHEN** a skill's body lists a trigger or anti-trigger case that its description does not cover
- **THEN** the case is added to the description, where it can affect selection
- **AND** the body section is removed rather than kept as a duplicate

#### Scenario: Every skill states where it does not apply

- **WHEN** another skill in the catalog covers an adjacent area
- **THEN** the description names it, either as an explicit "Do NOT use for … (that is `<skill>`)"
  clause or as a redirect ("for X use `<skill>`"), so the two do not compete for the same prompt

### Requirement: No runtime is not an excuse

A skill whose subject cannot be exercised in the working environment SHALL still be audited by
reading its doctrine in full, by applying the adversarial defect classes from `bug-hunter`, and by
probing whatever part of its claims is publicly verifiable. Leaving such a skill at mechanical
validation only SHALL be recorded as a gap, never treated as complete.

#### Scenario: A public claim is probed even when the runtime is absent

- **WHEN** a skill pins a version, names an upstream target framework, or asserts that a type or API
  is present or absent in a runtime
- **THEN** the claim is checked against the public source (release tag, manifest, upstream file)
  before the skill is considered audited

#### Scenario: An internal contradiction is found without running anything

- **WHEN** two statements in the same skill cannot both hold — a prescribed default that violates a
  constraint stated elsewhere in the file
- **THEN** the contradiction is resolved against the probed evidence, and the losing statement is
  corrected rather than left for the runtime to expose

#### Scenario: An unaudited skill is reported, not silently counted as done

- **WHEN** an audit cannot reach a skill's subject at all
- **THEN** the coverage report names the skill and what is missing, instead of reporting a total that
  implies it was covered

### Requirement: The catalog carries no credentials

The repository SHALL be scanned for credentials by a script wired into CI. The gate SHALL run against
the **working tree**, which can be kept clean; a separate on-demand mode SHALL report findings in the
full git history without gating, because a secret already published cannot be removed by a later
commit and a gate that can never pass is one contributors learn to ignore.

Findings that are operational detail rather than credentials — private (RFC1918) addresses, internal
hostnames — SHALL be reported distinctly and SHALL NOT fail the build.

#### Scenario: A credential added to the tree fails the build

- **WHEN** a change introduces an API key, token, private key, JWT or a connection string carrying a
  password into any tracked text file
- **THEN** the CI secret scan fails and names the file and the matched class

#### Scenario: An example credential is written so it cannot be mistaken for one

- **WHEN** documentation needs to show a connection string or a secret-shaped value
- **THEN** it uses an unmistakable placeholder, so the scanner does not have to guess and a reader
  cannot copy something that looks real

#### Scenario: History is reported, not gated

- **WHEN** the history contains a finding that a later commit already removed from the tree
- **THEN** the audit mode reports it with its class, and the build is not failed by it

