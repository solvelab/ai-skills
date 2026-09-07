## ADDED Requirements

### Requirement: A per-render cost is measured before it is cached

A skill that ships an executable the host runs on a timer SHALL measure the cost of each call it
makes before caching any of them, and SHALL cache only the calls the measurement shows to be
expensive. A cache over a call that is already cheap adds state, staleness and a code path while
returning nothing.

Measured on this catalog's status line, four git calls per render in a 1032-file repository:
`git status --porcelain` cost 9 ms while `git remote get-url`, `git symbolic-ref` and
`git rev-parse --git-dir` cost 1 ms each. Caching the three cheap ones would have added three
invalidation rules to save 3 ms.

Where a cached value can go stale, the skill SHALL state how stale it can get, and a value whose
staleness would mislead — the branch a command will act on, an identity, a destination — SHALL NOT
be cached behind a timer.

#### Scenario: choosing what to cache

- **WHEN** a shipped script makes several calls per render and one dominates the cost
- **THEN** the measurement of each call is recorded, and only the dominant one is cached
- **AND** SHALL NOT cache the cheap calls for symmetry

#### Scenario: a cached value that could mislead

- **WHEN** a value identifies what a subsequent action would affect, such as the current branch
- **THEN** it is read fresh on every render
- **AND** SHALL NOT be served from a timed cache, however cheap that would be

#### Scenario: an optimization that trades correctness

- **WHEN** a cheaper path would produce a number that is wrong or incomplete
- **THEN** the slower path is kept and the cost is recorded as a measured, accepted gap
- **AND** SHALL NOT be replaced by an approximation presented as the real figure
