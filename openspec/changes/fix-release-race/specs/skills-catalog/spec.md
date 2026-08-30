## ADDED Requirements

### Requirement: Publication does not depend on the interval between merges

The catalog's release automation SHALL evaluate the tip of the release branch, not the commit that
triggered the run. A run whose triggering commit has been superseded by a later merge SHALL still
publish whatever is due, so that a release is never lost or silently deferred because two pull
requests landed close together.

Where the automation refuses to publish because its checkout is behind the remote branch, the run
SHALL fail rather than report success. That refusal is indistinguishable, from the outside, from the
legitimate outcome of having nothing to publish: both leave no new tag and both exit zero. The
distinction SHALL be made by the pipeline, not left to whoever reads the run list.

A push that legitimately produces no release SHALL remain green, so that the guard does not turn
every documentation merge red.

The guard SHALL state, inside itself, what it does not cover — the same rule this capability already
imposes on the repository's other checks.

#### Scenario: A superseded commit still gets its release

- **WHEN** a commit that warrants a release is merged into the release branch and a second merge
  lands before that commit's release job runs
- **THEN** the release job publishes the version due, because it evaluates the branch tip rather
  than the commit that triggered it

#### Scenario: A refusal to publish is visible

- **WHEN** the release tool reports that the checked-out branch is behind the remote one and
  therefore publishes nothing
- **THEN** the job fails and names the log line that proves it, instead of exiting success with no
  new tag

#### Scenario: Nothing to publish stays green

- **WHEN** a push to the release branch carries only commit types that produce no version bump
- **THEN** the job succeeds with no release, and the guard does not fire

#### Scenario: The guard declares its own blind spot

- **WHEN** the guard recognises the refusal by matching text emitted by a third-party tool
- **THEN** the step states that an upstream wording change would silence it, so a passing run is not
  read as proof that the condition cannot occur
