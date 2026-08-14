## ADDED Requirements

### Requirement: Code locale has a canonical home

The catalog SHALL contain one skill that governs which natural language each artifact of a change is
written in. It SHALL draw the boundary by what consumes the artifact, not by who wrote it: prose read
by humans — commit subjects and bodies, pull-request and issue text, documentation, code comments,
user-facing strings — follows the repository's working language, while anything a machine parses —
identifiers, file and module names, REST path segments and query parameters, database tables,
columns and indexes, enum values, event and topic names, configuration keys, structured-log field
keys and test names — is English and ASCII.

The doctrine SHALL be stack-agnostic. Skills that state a format-level naming convention for one
stack — a test-method naming pattern, a DTO naming triple, a config-file naming scheme — SHALL keep
that text and link to the canonical skill for the language rule rather than restating it.

#### Scenario: A prose rule and an identifier rule do not collide

- **WHEN** a repository's convention is to write commit subjects, issues and documentation in a
  language other than English
- **THEN** that convention is preserved, and only the machine layer is required to be English
- **AND** the skills carrying the prose rules gain a scope clause and a link, rather than being
  rewritten

#### Scenario: An untranslatable domain term is kept and enumerated

- **WHEN** a domain term has legal or regulatory meaning and no faithful English translation
- **THEN** the term is kept, ASCII-folded, inside English grammar
- **AND** it is legitimate only when the change's glossary lists it or the code carries an inline
  waiver naming the reason, so that "it is a domain term" cannot become an unbounded exception

#### Scenario: A foreign payload is mirrored at the boundary, not carried inward

- **WHEN** an external API's payload field names are in another language
- **THEN** those names are mirrored verbatim only inside the adapter or transport schema, and are
  translated to the English domain model at a single mapping point

#### Scenario: The translation decision is taken before implementation, not during it

- **WHEN** a backlog item written in another language will produce code
- **THEN** the item carries a glossary mapping each domain term to its identifier, with each row
  marked as harvested from the codebase or decided in the item
- **AND** the implementing agent takes names from that glossary instead of improvising a translation,
  and an unlisted term is raised as a question rather than translated on the spot

#### Scenario: Existing names migrate by tier rather than by rename

- **WHEN** a repository already contains identifiers in another language
- **THEN** the doctrine requires English only for new code, permits opportunistic renaming of
  internal names in files already being changed, and forbids renaming a contract-bearing name in
  place — routes, persisted columns, event names and deployed configuration keys change through an
  expand/contract window
- **AND** a whole-repository rename is named as the anti-pattern it is, because names referenced as
  strings fail silently at runtime

### Requirement: A shipped enforcement script declares what escapes it

A catalog skill that ships an executable check SHALL state, inside the check itself, the conditions
under which it does not fire, so that a passing run is not read as full coverage. The script SHALL
carry a self-test that injects one known defect per detection tier and fails when any goes
undetected, and any catalog-side wiring of that script SHALL be exercised by the catalog's own
validator self-test.

#### Scenario: A heuristic check states its blind spots

- **WHEN** a check relies on a curated word list, a morphology rule or a language it can tokenize
- **THEN** the words, patterns and file types that escape it are enumerated in the check
- **AND** the material outside its reach is identified as review-only rather than assumed compliant

#### Scenario: A precision failure is cheap to waive, not a blocked pipeline

- **WHEN** the check reports a finding the author judges correct as written
- **THEN** the finding names the file, the line and the token, and prints the exact waiver line to add
- **AND** the waiver requires a stated reason, so every exception is visible in review

#### Scenario: The shipped script is proven to run by the catalog that ships it

- **WHEN** the catalog documents that target repositories should wire the script into their own CI
- **THEN** the catalog's own CI executes that same script rather than a reimplementation of it, so
  the instruction is backed by a run and not by an assertion
