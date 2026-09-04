## MODIFIED Requirements

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
