## ADDED Requirements

### Requirement: Terse response has a canonical home

The catalog SHALL contain one skill that governs the **shape of the assistant's chat response**
when a maintainer asks for it terse: what is dropped (articles, filler, pleasantries, hedging,
narration of tool calls, decorative tables and emoji, long raw error dumps), what is never dropped
(negations and qualifiers that flip meaning, numbers and units, exact technical terms, code blocks,
error strings, the user's language), and what compression is not (invented abbreviations, arrows,
words added to sound terse, grammar mangled where the plain form costs the same).

The skill SHALL state when the terse register yields: security warnings, confirmations of an
irreversible action, multi-step sequences whose order would be misread, compression that creates
technical ambiguity, and a request to clarify. It SHALL state where it does not apply at all —
code, comments, commits, pull requests, issues, documentation, memory files and any message to a
third party are written in normal prose — and the phrase that turns it off for the session.

The skill SHALL carry a single register. Intensity levels, alternative scripts and any mechanism
that needs a hook, a flag file or a per-prompt tracker SHALL NOT be part of it: the always-on path
is the maintainer's own rules file, which links here.

The skill SHALL cite the upstream it was harvested from with a pin (commit, content hash, licence)
and SHALL carry no number about its own effect. The only measurement that exists for response
shape on the maintainer's model (`research/i-have-adhd/`) returned NO-CLAIM, and the skill's own
gate is non-regression against what it replaces, recorded in that directory, not a claim.

#### Scenario: A terse answer keeps what carries meaning

- **WHEN** the terse register is on and the answer contains a negation, a number, a code block or
  an error string
- **THEN** those survive verbatim while articles, filler and pleasantries are dropped

#### Scenario: A security warning is written plainly

- **WHEN** the response warns about a destructive or irreversible action
- **THEN** the warning is written in full, clear prose, and the terse register resumes only after it

#### Scenario: Persisted artifacts are never terse

- **WHEN** the assistant writes code, a commit message, a pull request, an issue, documentation or
  a memory file while the terse register is on
- **THEN** that artifact is written in normal prose, unchanged by the register

#### Scenario: The register turns off by phrase

- **WHEN** the user says the stop phrase
- **THEN** the assistant confirms in one line and answers in its default style for the rest of
  the session, with no flag file or hook involved

#### Scenario: The skill carries no effect number

- **WHEN** the skill or the catalog README describes what the terse register saves
- **THEN** no percentage or token figure appears, and the reader is pointed to the measurement
  directory and its verdict instead
