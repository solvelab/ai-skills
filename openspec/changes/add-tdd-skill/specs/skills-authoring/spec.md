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
with its ledger, and the over-engineering review lens → `lean-code`; test order — writing the failing
test before the code it covers, what makes such a test legitimate, and when the cycle does not apply
→ `tdd`.

#### Scenario: Orchestrator skill references instead of restating

- **WHEN** a workflow skill needs a cross-cutting rule to be followed at one of its steps
- **THEN** it links the canonical skill and summarises in at most one line, rather than copying the
  rule

#### Scenario: A stack-specific instance links to the general rule

- **WHEN** a stack skill carries an instance of a rule whose canonical home is elsewhere
- **THEN** the instance names the concrete mechanism for that stack and links the general rule,
  without restating it

#### Scenario: Doctrine that acquires a canonical home stops being restated

- **WHEN** a rule that several skills stated inline acquires a canonical skill
- **THEN** those skills are edited to link it, and the canonical map records where it now lives

#### Scenario: Two skills that touch the same subject at different times

- **WHEN** one skill governs what is written before a change and another governs what is done to it
  afterwards
- **THEN** each names the other and the boundary between them, so neither restates the other's rule
- **AND** the canonical map carries one entry per rule, not one per subject
