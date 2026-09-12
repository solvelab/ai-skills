## ADDED Requirements

### Requirement: Project documentation layout has a canonical home

The catalog's documentation skill SHALL decide not only **which** documents a project gets, but
what each one is **called**, what **facts live inside it**, and in which **languages** it exists.
The decision SHALL be published as a closed map — one slot per reader need, one canonical name per
slot, written in English — instead of a set of conditions that lets two projects earning the same
right spell it differently.

A slot a project does not earn SHALL NOT become an empty document. It SHALL be declared absent, with
its reason, in the README's documentation index, so a reader can tell a decision from an omission.

Every legacy name the map absorbs SHALL be listed with the canonical name it migrates to, and the
list SHALL be drawn from names measured in real repositories rather than invented for the table.

The skill SHALL publish an ownership rule: each kind of fact — environment variables, endpoints,
operational resources, requirements, decisions, development commands, troubleshooting — has exactly
one owning document and one fixed shape there, and every other document links instead of repeating
it. The fixed shape SHALL be what makes ownership detectable, and the skill SHALL state what that
detection cannot see.

Requirements SHALL have a cumulative home of their own, independent of whether the repository runs a
spec-driven workflow. Where such a workflow exists, that document SHALL index and link its
capabilities rather than restate them.

Where a project documents in two languages, the skill SHALL name one language as the source and the
other as a mirror written in the same commit, with identical code blocks and matching section
numbering. Parity SHALL be checked as structure, never as freshness of translation.

The skill SHALL ship a checker that audits the **repository layout** — canonical slot present or
declared, legacy name with its destination, loose documents at the root, dated reports outside their
directory, file names written in another language, mirror parity, and fact ownership — beside the
existing checker that audits a single page. The layout checker SHALL prove every rule with an
injected defect in its own self-test, SHALL never move a file, and SHALL declare in its own docstring
what it cannot judge.

A layout rule SHALL NOT ship as a gate until its false-positive rate has been measured on real
repositories; a rule whose noise exceeds what the catalog already rejected for a page rule SHALL ship
review-only, with the measurement recorded.

#### Scenario: Two projects earning the same document spell it the same way

- **WHEN** two repositories both earn the architecture document
- **THEN** both write `docs/en/ARCHITECTURE.md`, and a repository carrying the legacy name is
  reported with that canonical name as its destination

#### Scenario: A slot the project does not earn is declared, not created

- **WHEN** a project has a single deploy target and earns no operations document
- **THEN** no such file is created, and the README's documentation index carries the slot with
  `not applicable` and the reason

#### Scenario: A fact lives in exactly one document

- **WHEN** the environment-variable table is written in the setup document
- **THEN** no other document repeats that table, and the checker reports the canonical header row
  found outside the owning document

#### Scenario: The mirror is checked as structure, not as translation

- **WHEN** the English source and its mirror carry the same sections in the same order with the same
  code blocks, while a paragraph of the mirror reads as an older wording
- **THEN** the parity check is silent, and the skill states that freshness of translation is
  review-only with the reason it was not made a gate

#### Scenario: Requirements exist without a spec-driven workflow

- **WHEN** a repository has no `openspec/` directory
- **THEN** the requirements document still exists with purpose, users, numbered functional and
  non-functional requirements and a glossary

#### Scenario: Requirements point at the specs instead of copying them

- **WHEN** a repository runs a spec-driven workflow
- **THEN** the requirements document indexes the capabilities and links each specification, and
  restates none of them

#### Scenario: A layout rule ships only with its measured noise

- **WHEN** a layout rule reproves correct documents on the repositories it was measured against, at
  a rate above the one that already sent a page rule to review-only
- **THEN** the rule ships review-only with the count recorded, rather than as a gate
