## MODIFIED Requirements

### Requirement: The code-locale rite is enforced at the moment of the write

The catalog SHALL ship an enforcement artifact that measures the locale rule when a file is written,
not only when a diff is reviewed. Doctrine held in context and a check that must be invoked by hand
SHALL NOT be treated as enforcement: the repository already states, for its other two rites, that
enforcement must not depend on the assistant noticing a rule already in context.

The artifact SHALL run on the harness events that surround a file write, SHALL measure the written
path and the written content with the shipped check, and SHALL return its findings through the field
that harness reads for each event — established against the installed version, never assumed, since
plain standard output is not carried into context for those events and an envelope naming the wrong
event is dropped by the harness.

On the event that **precedes** the write, a gating finding — a Portuguese identifier in the added
content, or a Portuguese path segment in a path the write **creates** — SHALL deny the tool call, so
that the name never reaches the disk. A Portuguese segment in the path of a file that already exists
SHALL NOT deny on that event: the name is already on disk, existing names change through a
deprecation window and not through a blocked edit, and a denial that names a file the model did not
name has no exit but the allowlist. That path is still reported on the event that follows the write.
The denial reason SHALL list each finding and SHALL end with the three legitimate exits: the inline
waiver with a stated reason, the allowlist file, and an explicit informative mode for the whole
session. The reason SHALL fit the caps the installed harness applies to that field, in characters
and in lines, so that the exits are never the part that is cut. The same event SHALL NOT deny on an
advisory finding alone, because a word the English list does not know is a question and not a
verdict.

The inline waiver SHALL be honoured wherever the check itself honours it — on the line above the
name — whether that line is part of the added content or already sits in the file immediately above
the fragment the edit replaces. A denial whose first exit cannot be satisfied by following it
produces the blind second attempt the item lists as a risk.

On the event that **follows** the write, the artifact SHALL keep its informative behaviour: findings,
gating and advisory, reach the assistant as context and the tool call stands. The informative mode
SHALL restore that behaviour for both events: with it set, nothing is denied and the advisory arrives
as before.

The artifact SHALL be silent when the write is clean and SHALL persist nothing outside the
repository. Where the shipped check is absent, it SHALL exit silently rather than fail, because a
missing gate must not present itself as an error to the user. The artifact SHALL state which writes
it does not see — those made through a shell command rather than a write tool — so that a denied
write is not read as proof that no Portuguese name can land.

#### Scenario: A write that introduces a Portuguese name is denied before it lands

- **WHEN** the event that precedes a write carries a path or added content with a Portuguese
  identifier or path segment
- **THEN** the artifact answers with the permission decision the harness reads for that event, set to
  deny, and the file is not written
- **AND** the reason names each offending segment once, and ends with the inline waiver, the
  allowlist file and the informative mode as the three exits

#### Scenario: The same write with a stated waiver or an allowlisted name lands

- **WHEN** the added content carries the inline waiver with a reason on the line above the name, or
  the name or path is listed in the allowlist file found from the working directory
- **THEN** the artifact produces no output on either event, and the write lands in silence

#### Scenario: An edit to a file that already carries a Portuguese name is not denied for the name

- **WHEN** the event that precedes an edit names a file that already exists and whose path carries a
  Portuguese segment, and the added content is English
- **THEN** the artifact produces no output on that event and the edit lands
- **AND** the event that follows the write still reports the path, so the legacy name stays visible
  without blocking its maintenance

#### Scenario: A waiver already on the line above the edited fragment is honoured

- **WHEN** the event that precedes an edit carries added content with a Portuguese identifier on its
  first line, and the file line immediately above the fragment being replaced carries the inline
  waiver with a reason
- **THEN** the artifact denies nothing, exactly as it would had the waiver been part of the added
  content

#### Scenario: The informative mode restores the advisory

- **WHEN** the informative mode is set for the session and a write carries a gating finding
- **THEN** the event that precedes the write denies nothing, and the event that follows it reports
  the findings as context exactly as it does without the mode

#### Scenario: An unrecognised word alone never denies

- **WHEN** the only findings on a write are words the English list does not know
- **THEN** the event that precedes the write denies nothing, and the event that follows it reports
  them as advisory, so the write is never blocked on a question the check cannot answer

#### Scenario: A write that introduces a Portuguese name is reported

- **WHEN** a file is written whose path or added content carries a Portuguese identifier and the
  event that follows the write fires
- **THEN** the findings reach the assistant as context for the next turn, naming the offending
  segments and the waiver that silences them

#### Scenario: The gate informs and never blocks

- **WHEN** the artifact reports findings on the event that follows the write
- **THEN** the tool call stands and the findings reach the assistant as context, as before: the
  denial belongs to the event that precedes the write, and the informative mode restores this
  behaviour for both events

#### Scenario: A clean write is silent

- **WHEN** the written path and content are English
- **THEN** the artifact produces no output at all on either event, so the reminder never becomes
  background noise

#### Scenario: A file type without a language profile still has its path measured

- **WHEN** the written file's extension has no language profile in the check
- **THEN** the path is still measured, and the content is reported as skipped rather than as passing

#### Scenario: A payload the artifact cannot read produces no error

- **WHEN** the payload is missing, malformed, names no written file, or names no event
- **THEN** the artifact exits silently and successfully, writing no state and requiring no
  credentials, and a payload that names no event is treated as the informative one, because in doubt
  the artifact informs and never denies
