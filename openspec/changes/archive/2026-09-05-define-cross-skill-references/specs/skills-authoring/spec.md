## ADDED Requirements

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

## MODIFIED Requirements

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
