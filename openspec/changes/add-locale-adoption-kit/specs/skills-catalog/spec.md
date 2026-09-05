## MODIFIED Requirements

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

The canonical skill SHALL ship the means of adopting the rule **per repository**, not only the
detector: a git pre-commit hook and a continuous-integration step, each copyable into a target
repository without cloning the catalog and without an assistant in the loop. Both SHALL invoke the
shipped detector rather than reimplement any of its tiers, SHALL measure only the lines the change
adds, and SHALL obtain the detector from a tagged release of the catalog — never from its default
branch — with the pin and its bump rule stated beside it. Each SHALL declare, in its own header, what
it does not cover, and SHALL name the exits the doctrine already defines — the inline waiver, the
allowlist file, and the deliberate bypass — so that a refused commit or a failed pull request tells
its author what to do next. The skill SHALL state which layer catches what: a session hook measures
the assistant's write, the pre-commit hook measures the human's commit, and the CI step measures the
pull request regardless of how it was produced.

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

#### Scenario: A repository adopts the gate without the assistant

- **WHEN** the shipped pre-commit hook is installed in a repository and a commit is attempted whose
  staged diff adds an identifier in another language
- **THEN** the commit is refused with the detector's finding, and the message names the inline
  waiver, the allowlist file and the deliberate bypass
- **AND** the same commit with the inline waiver on the offending line is accepted
- **AND** the shipped CI step, pasted into that repository's workflow, fails a pull request whose
  added lines carry such an identifier and passes one whose added lines are English, downloading the
  detector from a tagged release and verifying its digest before running it
