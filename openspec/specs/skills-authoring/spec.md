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
`verify-before-claiming`; the identifier/prose language boundary, the untranslatable-domain-term
exception and the identifier migration policy → `code-locale`.

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

#### Scenario: A prose-language rule keeps its text and gains a scope clause

- **WHEN** a skill instructs the agent to match the repository's working language — issue text, docs
  prose, commit subjects, issue headings
- **THEN** the instruction is preserved unchanged and gains one clause stating that it governs prose
  only, plus a link to the canonical skill for the machine layer
- **AND** the machine-layer rule is not reproduced inline in that skill

### Requirement: Uniform frontmatter metadata

Every `skills/<name>/SKILL.md` SHALL carry: `name` (== directory), `description` (folded block scalar),
`metadata.author: solvelab`, `metadata.version` (semver), `metadata.category` from the controlled set
{backend, testing, fivem, game, devops, docs, git, process, nui, frontend, tooling}, `license: MIT`,
and `compatibility`.

The controlled set is the one the CI frontmatter check enforces. When the two disagree, the gate is
authoritative and this document is corrected, because a contributor who follows a document that is
behind its gate writes a change the build rejects.

All seven SHALL be enforced by that check, each with a file-specific error naming the field. Where a
value is fixed by this requirement — `metadata.author: solvelab`, `license: MIT`, and the folded
`description` — the check SHALL assert the **value**, not merely the presence of the key, because a
key present with the wrong value satisfies a presence check while violating the requirement.

The catalog declares itself an implementation of the open Agent Skills standard
(agentskills.io/specification), so the size limits that standard fixes SHALL hold for every skill:
`description` is at most 1024 characters and `compatibility` at most 500. Both limits are measured
on the **YAML-parsed value** — the string a consumer receives after the folded scalar is unfolded —
counted in characters (code points), never on the raw frontmatter block and never in bytes. The raw
block carries the indentation and line breaks of the folded scalar and measures more than the
value — 6–26 characters more across this catalog, 1024 raw against 998 parsed on one skill — so a
gate on the raw block would reject a skill the standard accepts.

#### Scenario: CI rejects incomplete frontmatter

- **WHEN** a skill is added or edited without `name` matching its directory, without `description`,
  `metadata.author`, `metadata.version`, `license` or `compatibility`, with a category outside the
  controlled set, with `metadata.author` or `license` set to anything other than the value fixed
  above, or with a `description` that is not a folded block scalar
- **THEN** the CI validate job fails with a file-specific error naming the field

#### Scenario: The documented set matches the enforced set

- **WHEN** a category is added to the CI frontmatter check
- **THEN** this requirement is updated in the same change, so no contributor reads a controlled set
  that is narrower than the one the build accepts

#### Scenario: A field the document mandates is not left to review alone

- **WHEN** this requirement names a field that the frontmatter check does not verify
- **THEN** either the check is extended to cover it, or the field is identified as review-only, so
  that the gap between the document and the gate is never silent

#### Scenario: A description over the limit fails the build with its measured size

- **WHEN** a skill's parsed `description` exceeds 1024 characters, or its parsed `compatibility`
  exceeds 500
- **THEN** the catalog validator fails naming the skill, the check and the measured size next to the
  limit, so the author knows how much has to move out of the frontmatter

#### Scenario: The limit is measured the way the standard measures it

- **WHEN** a `description` measures 1024 characters on the raw frontmatter block and 998 once parsed
- **THEN** the skill passes, because the limit applies to the parsed value — the same value the
  standard's reference validator measures — and not to the block as written in the file

### Requirement: English as catalog locale

All skill content SHALL be written in English. This requirement governs the **documentation prose of
this catalog** — the text of `SKILL.md` and `references/` files. The natural language of the code a
skill teaches, shows in an example, or produces in a target repository is governed separately by the
identifier/prose language boundary whose canonical home is `code-locale`, and the two SHALL NOT be
conflated: a catalog written in English can still teach an agent to emit identifiers in another
language, which is the defect that separating them prevents.

#### Scenario: Project-specific skill is still English

- **WHEN** a skill documents a project-specific workflow (e.g. `openspec-drivezone`)
- **THEN** its content is in English regardless of the project's working language

#### Scenario: Catalog locale is not read as a rule about produced code

- **WHEN** an author asks whether this requirement already covers the identifiers, route segments or
  schema names appearing in a skill's code examples
- **THEN** the requirement states that it does not, and names `code-locale` as the rule that does,
  so the absence of an identifier rule cannot be mistaken for coverage

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

Conformance with an external standard the catalog claims SHALL be measured by two independent
paths: the catalog's own check, which the self-test can break on purpose, and the standard's
reference validator, pinned to an exact version and run over every skill in CI. The pin SHALL carry
the reason it exists next to it, because a blocking gate on an unpinned upstream fails the build on
someone else's release schedule.

The cross-reference rules — every reference file reachable from `SKILL.md`, no path that resolves
only in a full checkout, every description carrying a boundary clause — SHALL be among the checks
the script enforces, each with its own injected defect in the self-test and its uncovered part
declared in the check.

#### Scenario: A violation fails the build

- **WHEN** a change introduces a broken reference, an unparseable code block, a mistagged fence, a
  description that contradicts its body, or a `description` or `compatibility` longer than the
  standard allows
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

#### Scenario: The frontmatter-limits check is itself gated

- **WHEN** the self-test injects a `description` of more than 1024 parsed characters into a copy of
  the catalog
- **THEN** the validator reports the frontmatter-limits check for that skill, and a validator that
  stays silent fails the self-test

#### Scenario: The reference validator runs pinned, over every skill

- **WHEN** the CI validate job runs
- **THEN** the standard's reference validator, installed at an exact pinned version, is executed
  once per `skills/<name>/` directory and any finding fails the job, and the step states what the
  reference validator covers and what it leaves to the catalog's own checks

#### Scenario: The cross-reference checks are themselves gated

- **WHEN** the self-test injects, into a copy of the catalog, a `*.md` under `references/` that no
  file links, a `<other-skill>/references/<file>` path without the `skills/` prefix, and a
  description with neither a "Do NOT use" clause nor a redirect naming a sibling skill
- **THEN** the validator reports the orphan-reference (C11), out-of-skill-path (C12) and
  anti-trigger-clause (C13) checks respectively, each check states in its own text the exact phrase
  list or path forms it judges and what it leaves to review, and a validator silent on any of the
  three fails the self-test

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

A skill SHALL NOT carry a `How to Use`, `When to use this skill`, `Trigger Test Cases`, `Prompt` or
`Usage` section in its `SKILL.md`. Such a section is read only after the skill has already been
selected, so it cannot influence routing, and it costs context on every invocation. Trigger and
anti-trigger information SHALL live in the frontmatter `description`, which is what the model reads
when choosing a skill.

Folding a trigger into the description SHALL respect the size limit fixed by *Uniform frontmatter
metadata*. When the description cannot hold everything, what stays is what routes: the quoted
phrases a user would say, the "Use when" conditions and the "Do NOT use for" boundary. What moves
out first is what does not route: sentences describing what the skill covers, file paths,
configuration detail and enumerations that the body or a reference already carries. The overflow
goes to the first paragraph of the body or to a file under `references/`, never to a body section
that restates triggers.

#### Scenario: A trigger case not present in the description is folded in, not filed away

- **WHEN** a skill's body lists a trigger or anti-trigger case that its description does not cover
- **THEN** the case is added to the description, where it can affect selection
- **AND** the body section is removed rather than kept as a duplicate

#### Scenario: Every skill states where it does not apply

- **WHEN** another skill in the catalog covers an adjacent area
- **THEN** the description names it, either as an explicit "Do NOT use for … (that is `<skill>`)"
  clause or as a redirect ("for X use `<skill>`"), so the two do not compete for the same prompt

#### Scenario: The fold does not push the description over the limit

- **WHEN** adding a trigger to a description would take it past 1024 parsed characters
- **THEN** non-routing content is moved out of the description first — to the body's first
  paragraph or to `references/` — and every quoted trigger phrase present before the edit is still
  present after it, recorded as a before/after table in the change that made the edit

#### Scenario: A body section that duplicates the description is removed, not folded

- **WHEN** a skill carries a body section whose trigger content already appears in its description
- **THEN** the section is removed and nothing is added to the description, because the fold exists
  to carry information into the description, not to repeat it

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

The scanner SHALL carry a self-test, wired into CI beside the scan, that injects one credential per
pattern it claims to detect and asserts each class is reported, including a credential preceded by a
word the placeholder filter recognises and one wrapped in angle brackets, because the filter that
silences documentation placeholders SHALL apply to the matched token only and never to the text
around it. The self-test SHALL build its samples at run time rather than carry them as literals, so
the scanner's own source does not fail the scan. The pattern set SHALL cover fine-grained GitHub
tokens (`github_pat_`) and `sk-`-prefixed API keys in addition to the classic classes.

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

#### Scenario: A credential after a placeholder word is still a credential

- **WHEN** a real-shaped token is written after the word `test` (`test_token = ghp_…`) or between
  angle brackets (`<ghp_…>`)
- **THEN** the scanner reports it, because the placeholder filter is applied to the token and not to
  the forty characters before it

#### Scenario: A scanner pattern that cannot fire is caught

- **WHEN** a change to the scanner silently stops one of its patterns from matching its sample
- **THEN** `--selftest` fails naming the pattern, because a clean tree and a pattern that cannot fire
  are otherwise indistinguishable

### Requirement: A skill's version moves with its content

A pull request that changes any path under `skills/<name>/` — the `SKILL.md` body, a file under
`references/`, anything the skill owns — SHALL raise that skill's `metadata.version` above the value
on the base revision, or SHALL carry one pull-request-wide line `Skill-version: none — <reason>` in
its body, with a reason at least as long as the spec-rite waiver requires. The rule SHALL be measured
by a script wired into CI that diffs the branch against its base, so that the promise `README.md`
makes to contributors — "bump it when that skill's behavior changes" — is enforced and not merely
stated.

The gate SHALL read the diff, not the working tree: a skill whose only change is the `  version:`
line itself is not a content change; a skill with no `SKILL.md` on the base is new and has nothing to
move from; a diff confined to the generated trees (`claude/`, `codex/`, `cursor/`, `copilot/`,
`plugins/`) is not a skill edit. A version that moves **backwards** SHALL be a finding regardless of
any waiver, because no reason makes a lower number correct.

The waiver is authored by whoever opened the pull request and SHALL be matched as text at the start
of a line, never executed or interpolated, and read from the event payload the runner writes rather
than through a step's environment, the same way the spec-rite waiver is read.

The gate SHALL carry a self-test that injects one defect per rule and asserts detection, and SHALL
state in its own header what it does not cover: it proves the number moved, not that the movement
was the right magnitude or that the waiver's reason is honest.

#### Scenario: An edited skill without a bump fails

- **WHEN** a pull request changes `skills/backlog/SKILL.md` and `metadata.version` reads `1.5.0` on
  both the base and the head, and the body carries no `Skill-version:` line
- **THEN** the CI validate job fails naming the skill, the base version, the head version, and the
  two exits — bump the version above `1.5.0`, or add `Skill-version: none — <reason>` to the body

#### Scenario: A pull-request-wide waiver covers every edited skill

- **WHEN** a pull request edits twelve skills without moving any `metadata.version` and its body
  carries one line `Skill-version: none — cross-reference line added to each skill, no rule changed`
- **THEN** the gate stays silent for all twelve, because the waiver is read once for the whole diff

#### Scenario: A waiver without a usable reason fails

- **WHEN** the body carries `Skill-version: none` alone, or with a reason shorter than the shared
  minimum
- **THEN** the gate fails naming the missing reason, not the missing bump

#### Scenario: A new skill passes

- **WHEN** a pull request adds `skills/new-skill/SKILL.md` and no `SKILL.md` exists for it on the base
- **THEN** the gate stays silent for that skill, because there is no previous version to move from

#### Scenario: A wrapper-only diff passes

- **WHEN** a pull request changes only files under `claude/skills/<name>/` or
  `plugins/<group>/skills/<name>/` and nothing under `skills/<name>/`
- **THEN** the gate stays silent, because generated trees are never counted as skill edits

#### Scenario: A version that moves backwards fails even with a waiver

- **WHEN** a pull request changes `skills/x/SKILL.md` and `metadata.version` goes from `1.8.0` to
  `1.7.0`, with or without a `Skill-version: none — <reason>` line in the body
- **THEN** the gate fails naming the regression

#### Scenario: The gate skips on push events and says so

- **WHEN** the CI job runs on an event that is not `pull_request` (a push to `master`)
- **THEN** the gate prints that it skipped and why, and exits successfully, because there is no
  pull request body to read and no base to diff against

### Requirement: Cross-skill references resolve in every install form

A skill SHALL be written so that every path it cites resolves, or is recognisable as belonging to
another skill, in every form the catalog is installed in: a full clone with symlinks, `npx skills
add` (which copies one `skills/<name>/` directory), a category plugin group (which copies the skills
of one group), and the Cursor and Copilot wrappers the README instructs users to copy alone.

- A reference to another skill SHALL name that skill in prose and, when it points at a file, SHALL
  use the repository-root form `skills/<skill>/references/<file>` and say that the file lives in that
  skill. The form `<skill>/references/<file>` with no `skills/` prefix SHALL NOT be used: it
  resolves in no install form, the clone included.
- A path outside `skills/` — `research/`, `claude/global/hooks/`, any entry only a clone carries —
  SHALL be written as the repository URL.
- Every `*.md` under a skill's `references/` directory, recursively, SHALL be reachable from that
  skill's `SKILL.md`: linked directly, or linked from a reference file that is itself reachable. A
  `README.md` inside a `references/` subdirectory counts as an index once it is linked.
- The generated Cursor and Copilot wrappers SHALL point at `references/` through the repository URL,
  never through a path relative to the catalog tree.

#### Scenario: Clone or symlink install

- **WHEN** a skill installed from a clone (directly or through `~/.claude/skills/<name>` symlinks)
  cites `skills/<other>/references/<file>`
- **THEN** the path resolves from the repository root, because the symlink target lives inside the
  clone, and the validator's path check (C1) verifies the file exists

#### Scenario: npx skills install

- **WHEN** `npx skills add` has copied only `skills/<name>/` and the skill cites a file of another
  skill
- **THEN** every path under the skill's own directory resolves, and the cross-skill path is
  recognisable by its `skills/<other>/` prefix and by the sentence naming `<other>`, so the reader
  installs that skill instead of following a dead relative path

#### Scenario: Plugin group install

- **WHEN** a skill in one plugin group cites a reference file of a skill that lives in another group
- **THEN** the sentence names the skill to install and the path is written in the canonical form;
  the path is not read as a promise that the file is present in this group

#### Scenario: Cursor or Copilot copy

- **WHEN** a `cursor/rules/<name>.mdc` or `copilot/instructions/<name>.instructions.md` is copied
  alone into a project, as the README instructs
- **THEN** every `references/` link inside it is a repository URL that resolves without the catalog
  tree, and `generate.sh` produces that URL from the canonical `references/` link

#### Scenario: A path only a clone carries is written as a URL

- **WHEN** a skill needs to point at something outside `skills/` — a research directory, a hook
  shipped under `claude/global/`
- **THEN** it writes the repository URL, and the validator reports a bare `research/…` or
  `claude/…` path as an out-of-skill path (C12)

#### Scenario: A reference file nobody links is caught

- **WHEN** a `*.md` is added under `references/` and neither `SKILL.md` nor any reachable reference
  links it
- **THEN** the validator reports it as an orphan reference (C11), because a file nobody points at is
  a file nobody loads

