## MODIFIED Requirements

### Requirement: Single canonical home per rule

Every cross-cutting rule SHALL be defined in exactly one skill and referenced by link (with at most a
one-line summary) everywhere else. Canonical map: trust boundary → `fivem-lua`;
fallback/negative-cache/clamping → `backend-resilience`; REST negative-testing checklist →
`api-resilience-testing`; adversarial methodology → `bug-hunter`; OpenSpec lifecycle → `openspec`;
claim verification, the research ladder, not-found reporting and the off-script scope guard →
`verify-before-claiming`.

#### Scenario: Orchestrator skill references instead of restating

- **WHEN** `openspec-drivezone` describes its Fallback and Bug-Hunter gates
- **THEN** each gate row links to the canonical skill with a one-line summary
- **AND** no mechanism list from a sibling skill is reproduced inline

#### Scenario: A stack-specific instance links to the general rule

- **WHEN** a skill states a domain instance of a rule that has a canonical home elsewhere — reading
  the CSP EmmyLua stub before calling an API, or reading the chart template before emitting a field
- **THEN** the instance keeps its stack-specific text and gains one sentence linking to the canonical
  skill for the general form, rather than reproducing the general rule inline

#### Scenario: Doctrine that acquires a canonical home stops being restated

- **WHEN** a rule previously stated in full inside one skill is given a canonical home
- **THEN** the original statement is reduced to a link with at most a one-line summary, so the
  catalog carries the doctrine exactly once
