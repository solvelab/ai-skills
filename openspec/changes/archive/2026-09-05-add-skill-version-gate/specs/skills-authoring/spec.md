## ADDED Requirements

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
