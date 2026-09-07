## ADDED Requirements

### Requirement: Delegation and the artifact boundary have a canonical home

The catalog SHALL contain one skill that governs two decisions the catalog makes repeatedly and has
never written down: which artifact a cross-cutting rule becomes, and when dispatching a subprocess
pays for itself.

The artifact boundary SHALL be stated as an ordered choice between the artifact kinds this
repository actually ships — a skill that enters the model's context before the task, a hook the
harness fires without the model noticing, a deterministic script the build runs, and an agent that
executes isolated work — and each kind SHALL be anchored to a real artifact of this repository
rather than described in the abstract.

Delegation SHALL be gated on three tests a piece of work must pass before it becomes an agent:
that it is heavy enough in reading for isolation to pay, that its context is separable from the
caller's, and that its output is a narrow contract the caller can check. The skill SHALL name the
anti-patterns it refuses: one agent per skill, an agent standing in for a deterministic validator,
and an agent granted write access to files the calling loop should write.

The skill SHALL state model and effort tiering as a criterion — task difficulty, the subagent's
separate context, and the effect on the calling loop's prompt cache — rather than as a list of
model names, so that the rule outlives the models it was written under. It SHALL require
least-privilege `tools` and a written output contract for every agent defined.

The doctrine SHALL be about which artifact exists and what privilege it holds, and SHALL link to
`lean-code` for how much code a change leaves behind rather than restating that ladder.

#### Scenario: A deterministic check is not delegated to a model

- **WHEN** a rule can be decided by a script that reads the tree and exits non-zero
- **THEN** the doctrine routes it to a CI script, not to an agent
- **AND** an agent is admitted only for the judgement the script cannot make, and is advisory there

#### Scenario: A rule stated only in personal configuration is published

- **WHEN** a cross-cutting rule is stated only in a file the repository publishes as an example of
  personal configuration
- **THEN** the doctrine treats that as no canonical home at all, because a file that tells the
  reader not to adopt its defaults cannot be the contract a consumer installs
- **AND** the rule moves into the catalog and the personal file links to it

#### Scenario: The tiering rule survives a model rename

- **WHEN** the model names current at authoring time are superseded
- **THEN** the published rule still decides, because it is written on difficulty, separate context
  and prompt-cache effect rather than on the names
- **AND** a repository or a maintainer naming specific models does so as a local instance of the
  published criterion

#### Scenario: An agent is refused write access the caller should hold

- **WHEN** delegated work would produce a file — a test, a fix, a document
- **THEN** the doctrine has the agent return what to write and the calling loop write it, unless
  writing inside the agent is itself the isolated work being bought
- **AND** the agent's `tools` are declared at the minimum the contract needs, never omitted
