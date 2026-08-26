## ADDED Requirements

### Requirement: The identifier-locale check asks whether the word is English

The shipped identifier-locale check SHALL decide a name by two questions, not one. The first — is
this word in the known foreign lexicon? — SHALL keep gating, because its confidence is high. The
second — is this word English? — SHALL report every segment it does not recognize, so that the
default answer to an unknown word is *surfaced* rather than *approved*.

The second question SHALL be answered from a word list shipped with the check, not from the host's
dictionary, so that the same input produces the same finding on a maintainer's machine, in
continuous integration and inside an editor hook. The list SHALL be public-domain or permissively
licensed, and SHALL record its source, licence and date in the repository. Vocabulary that belongs to
programming rather than to English SHALL live in a separate list from the natural-language one, so
that either can be audited on its own.

A segment that decomposes into two known words SHALL be treated as known, so that ordinary compounds
do not become manual entries and the curated list does not become the same open-vocabulary chase the
foreign lexicon already is.

Findings from the second question SHALL be **advisory**: reported and counted separately, and SHALL
NOT change the exit code unless the caller asks for it. Whole-tree enforcement of a closed-world
question turns a legacy repository red on day one, and a check that fails everything is switched off
within a week — the same reason the check's diff mode exists. A segment already reported by the
first question SHALL NOT be reported again by the second.

#### Scenario: A foreign word outside the lexicon is surfaced

- **WHEN** an identifier or path segment carries a word the foreign lexicon does not know and the
  English list does not contain
- **THEN** the check reports it as an advisory finding naming the segment
- **AND** the exit code is unchanged, unless the caller asked for those findings to gate

#### Scenario: English, programming vocabulary and compounds stay silent

- **WHEN** the segment is an English word, an entry of the programming vocabulary, a kept domain
  term, an allowlisted entry, or a compound of two known words
- **THEN** the check reports nothing for it

#### Scenario: One segment, one finding

- **WHEN** a segment is caught by the foreign-lexicon question
- **THEN** it is not also reported by the English question, so that the higher-confidence tier is the
  one the reader sees

#### Scenario: The word list is deterministic and declared

- **WHEN** the check runs on any machine
- **THEN** it answers from the list shipped beside it rather than from a host dictionary
- **AND** the list's source, licence and date are recorded, and an explicit override names a
  different list, failing loudly when that list cannot be read

#### Scenario: What neither question reaches is declared

- **WHEN** a word exists in both languages, such as a name spelled the same in each
- **THEN** it passes both questions, and the check's own limits state that it does, so a clean run is
  never read as full compliance
