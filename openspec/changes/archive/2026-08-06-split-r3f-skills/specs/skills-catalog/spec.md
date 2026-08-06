## MODIFIED Requirements

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
