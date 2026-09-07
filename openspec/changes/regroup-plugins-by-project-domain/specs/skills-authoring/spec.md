## MODIFIED Requirements

### Requirement: Uniform frontmatter metadata

Every `skills/<name>/SKILL.md` SHALL carry: `name` (== directory), `description` (folded block scalar),
`metadata.author: solvelab`, `metadata.version` (semver), `metadata.category` from the controlled set
{backend, testing, fivem, game, assettoserver, devops, docs, git, process, nui, frontend,
tooling}, `license: MIT`,
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
