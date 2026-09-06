## MODIFIED Requirements

### Requirement: Single canonical home per rule

Every cross-cutting rule SHALL be defined in exactly one skill and referenced by link (with at most a
one-line summary) everywhere else. Canonical map: trust boundary → `fivem-lua`;
fallback/negative-cache/clamping → `backend-resilience`; REST negative-testing checklist →
`api-resilience-testing`; adversarial methodology → `bug-hunter`; OpenSpec lifecycle → `openspec`;
claim verification, the research ladder, not-found reporting and the off-script scope guard →
`verify-before-claiming`; the identifier/prose language boundary, the untranslatable-domain-term
exception and the identifier migration policy → `code-locale`; code volume — the reuse-before-writing
ladder, the root-cause rule for bug fixes, the never-simplified-away carve-outs, the `lean:` marker
with its ledger, and the over-engineering review lens → `lean-code`.

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

#### Scenario: A prose-language rule keeps its text and gains a scope clause

- **WHEN** a skill instructs the agent to match the repository's working language — issue text, docs
  prose, commit subjects, issue headings
- **THEN** the instruction is preserved unchanged and gains one clause stating that it governs prose
  only, plus a link to the canonical skill for the machine layer
- **AND** the machine-layer rule is not reproduced inline in that skill

#### Scenario: A dependency-restraint instance links to the general rung

- **WHEN** a skill states a stack-specific instance of "no new dependency for what a few lines do" —
  a stdlib-only rule for a bare container, a no-new-supply-chain rule for a sidecar
- **THEN** the instance keeps its text and gains one line linking to `lean-code` for the general
  rung of the ladder, rather than reproducing the ladder inline
