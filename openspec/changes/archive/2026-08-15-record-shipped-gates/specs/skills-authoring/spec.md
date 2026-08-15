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
