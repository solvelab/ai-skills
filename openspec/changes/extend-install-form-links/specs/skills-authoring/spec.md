## MODIFIED Requirements

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
  never through a path relative to the catalog tree; a wrapper that links its own `SKILL.md`
  instead of inlining it (the Copilot wrapper) SHALL point at that file through the repository
  URL as well, for the same reason.

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

#### Scenario: A wrapper copied alone links its own SKILL.md by repository URL

- **WHEN** a `copilot/instructions/<name>.instructions.md` is copied alone into a project's
  `.github/instructions/`, as the README instructs, and the assistant follows its link to the
  canonical `SKILL.md`
- **THEN** that link is `https://github.com/solvelab/ai-skills/blob/master/skills/<name>/SKILL.md`,
  which resolves without the catalog tree, and no generated Copilot wrapper carries a
  `../../skills/` path

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
