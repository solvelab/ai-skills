## MODIFIED Requirements

### Requirement: Single canonical home per rule

Every cross-cutting rule SHALL be defined in exactly one skill and referenced by link (with at most a
one-line summary) everywhere else. Canonical map: trust boundary → `fivem-lua`;
fallback/negative-cache/clamping → `backend-resilience`; REST negative-testing checklist →
`api-resilience-testing`; adversarial methodology → `bug-hunter`; OpenSpec lifecycle → `openspec`;
claim verification, the research ladder, not-found reporting and the off-script scope guard →
`verify-before-claiming`; the identifier/prose language boundary, the untranslatable-domain-term
exception and the identifier migration policy → `code-locale`.

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

### Requirement: English as catalog locale

All skill content SHALL be written in English. This requirement governs the **documentation prose of
this catalog** — the text of `SKILL.md` and `references/` files. The natural language of the code a
skill teaches, shows in an example, or produces in a target repository is governed separately by the
identifier/prose language boundary whose canonical home is `code-locale`, and the two SHALL NOT be
conflated: a catalog written in English can still teach an agent to emit identifiers in another
language, which is the defect that separating them prevents.

#### Scenario: Project-specific skill is still English

- **WHEN** a skill documents a project-specific workflow (e.g. `openspec-drivezone`)
- **THEN** its content is in English regardless of the project's working language

#### Scenario: Catalog locale is not read as a rule about produced code

- **WHEN** an author asks whether this requirement already covers the identifiers, route segments or
  schema names appearing in a skill's code examples
- **THEN** the requirement states that it does not, and names `code-locale` as the rule that does,
  so the absence of an identifier rule cannot be mistaken for coverage
