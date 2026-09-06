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
shipped detector rather than reimplement any of its tiers, and SHALL measure only the lines the
change adds. Whenever either artifact downloads the detector it SHALL do so from a tagged release of
the catalog — never from its default branch — and SHALL verify the file's digest before running it,
with the pin and its bump rule stated beside it; the hook MAY instead run a detector the machine
already holds (an explicit path, or the catalog's local clone) and SHALL state in its header that
those sources carry no pin. Both SHALL fix the shape of the diff they read so that a repository's or
a user's git configuration cannot empty it or alter its paths, and neither SHALL approve when it
could not measure — a diff command that fails, or a detector that exits without completing its scan,
fails the commit or the step. Each SHALL declare, in its own header, what it does not cover, and
SHALL name the exits the doctrine already defines — the inline waiver, the allowlist file, and the
deliberate bypass — so that a refused commit or a failed pull request tells its author what to do
next. The skill SHALL state which layer catches what: a session hook measures
the assistant's write, the pre-commit hook measures the human's commit, and the CI step measures the
pull request regardless of how it was produced.

The prose half of the rule SHALL be measurable too, where a repository asks for it: a declaration
file at the repository root (`.code-locale`, one `key: value` per line) names the working language
of its prose, and the canonical skill SHALL ship a second detector that reads comments, docstrings
and Markdown paragraphs through the same language tables as the identifier detector — imported,
never duplicated — and classifies each fragment by closed lists of function words for the two
languages it knows, lists that share no word and ship beside it with their provenance. Without the
declaration the prose direction SHALL be silent at every layer — detector, session hooks,
pre-commit hook, CI step — and SHALL say so when asked; a declaration with a value the detector
does not know SHALL be an error naming the file and the accepted values, never a silent pass. The
prose detector SHALL count what it skips (short, code-like, quoted, unknown) and report those
counts, so that zero findings is never read as full compliance; it SHALL gate only a comment or
docstring with strong evidence of the wrong language, keep Markdown and weak evidence advisory,
honour the same inline waiver and the same allowlist file the identifier detector honours, and
declare in its own header what it does not measure — user-facing strings and log messages, languages
other than the two it knows, text inside code fences. The pre-commit hook and the CI step SHALL run
it on the added lines only where the declaration exists. The catalog itself SHALL NOT declare a
prose language, and the skill SHALL say why: its README is English and its change records are
Portuguese.

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

#### Scenario: A gate that cannot measure does not approve

- **WHEN** the CI step's base revision is absent from the clone, or the hook's detector exits without
  printing its findings line, or a git configuration would replace or empty the diff the detector reads
- **THEN** the step or the commit fails, naming the cause, instead of reporting zero findings
- **AND** a commit whose staged diff renames a file to a name in another language is refused on the
  new path, and a staged hunk carrying non-UTF-8 bytes is measured rather than aborting the detector

#### Scenario: A declared repository measures the prose direction

- **WHEN** a repository carries `.code-locale` with `prose: pt-BR` and a Python file adds a comment
  of four or more words whose function words are English and none are Portuguese
- **THEN** the prose detector reports it as a gating finding naming the path, the line, the kind of
  fragment, the language it reads as and the declared one, and names the exits: the inline waiver on
  the line or the line above, and the path in the allowlist file
- **AND** a comment of four or more Portuguese words, a comment under four words, a fragment that
  is mostly identifiers, quoted spans and paths, and a Markdown paragraph in English produce no
  gating finding — the first passes, the next two are counted as skipped, the last is advisory

#### Scenario: Without the declaration the prose direction is silent

- **WHEN** no `.code-locale` is found walking up from the scanned root to the repository boundary
- **THEN** the prose detector, the session hooks, the pre-commit hook and the CI step report no
  prose finding and exit zero, the identifier direction is measured exactly as before, and the
  detector's explain mode states that the prose direction is off and how to declare it

#### Scenario: A declaration the detector cannot read is an error, not a pass

- **WHEN** `.code-locale` carries `prose:` with a value outside the accepted set
- **THEN** the detector exits with the usage code, naming the file and the accepted values, and the
  pre-commit hook refuses the commit for the same reason instead of approving an unmeasured diff

#### Scenario: The function-word lists are disjoint by construction

- **WHEN** the prose detector loads its two word lists, or its self-test runs
- **THEN** a word present in both lists fails the load and the self-test, so that a word both
  languages share can never count as evidence for either

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

Where the repository declares its prose language, the same artifact SHALL measure the written text
with the shipped prose detector as well, locating the declaration by walking up from the written
file. On the event that **precedes** the write, a comment or docstring with strong evidence of the
wrong language SHALL deny the tool call with the same three exits in the reason; a Markdown
paragraph or weak evidence SHALL NOT deny and reaches the assistant as advisory on the event that
**follows** the write. Without the declaration the artifact SHALL measure prose nowhere and behave
exactly as before.

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

#### Scenario: A comment in the wrong language is denied where the repository declares its prose

- **WHEN** the repository the written file belongs to carries `.code-locale` with `prose: pt-BR`
  and the event that precedes a write carries a Python comment of four or more English words
- **THEN** the artifact denies the write, and the reason names the line, the fragment, the
  language it reads as, the declared language and the three exits
- **AND** the same write with the comment in Portuguese lands in silence, and the same write with
  the inline waiver on the line above the comment lands in silence

#### Scenario: A Markdown paragraph in the wrong language only informs

- **WHEN** the same repository receives a write of a `.md` file whose paragraph reads as English
- **THEN** the event that precedes the write denies nothing, and the event that follows it reports
  the paragraph as advisory context

#### Scenario: Without a declaration no prose is measured at the write

- **WHEN** no `.code-locale` is found walking up from the written file's directory to the
  repository boundary
- **THEN** the artifact reports no prose finding on either event, whatever language the comment is
  in, and the identifier findings are exactly what they were before

### Requirement: The code-locale rite closes the turn, not only the write

The catalog SHALL ship an enforcement artifact that measures the locale rule on the **result** of a
turn — the repository's uncommitted diff — and not only on the tool that wrote it. A write that
reaches the disk outside the harness's edit tools (a shell heredoc, `sed`, a script) is never seen by
the write-time artifact, so the rite that covers only the write SHALL NOT be treated as covering the
turn.

The artifact SHALL run on the harness event that ends a turn, SHALL read the working directory from
the payload, and, when that directory is inside a git work tree, SHALL build the uncommitted diff —
tracked files against the current commit, plus every untracked file the repository does not ignore,
each as an added file — and measure it with the shipped identifier-locale check in its diff mode,
honouring the repository's allowlist and the check's own exclusions. It SHALL measure only what the
turn left uncommitted: history and untouched lines never enter.

When the diff carries a gating finding and the payload does not mark the block as already in
progress, the artifact SHALL prevent the turn from ending, through the field the installed harness
reads for that event — established against the installed version, never assumed — and its reason
SHALL list every finding and the legitimate exits (an inline waiver with a reason, the repository
allowlist, the session-wide informative mode). When the payload marks the block as already in
progress, the artifact SHALL NOT block again: it SHALL report what remains as a message and let the
turn end, because the second turn is the last chance and never a loop.

The artifact SHALL build the diff in a shape that does not depend on the user's git configuration:
no external diff driver or text conversion, unquoted non-ASCII paths, fixed `a/` and `b/` prefixes,
no colour — so that a setting in `~/.gitconfig` can neither silence the gate nor make it report a
path that does not exist. Untracked files the check itself calls vendored, and empty or binary
files, SHALL be skipped before git is asked, so they consume neither the measuring budget nor a
process each.

The artifact SHALL be silent — no output, exit zero, under one second — outside a git work tree, on
an empty diff, on advisory-only findings, in the informative mode, and on a payload it cannot read.
It SHALL cap the diff it measures at a declared number of lines and SHALL say so when the cap was
reached, never truncating in silence: in its reason when the measured part has a finding, and as a
block of its own — once, then a message on the Stop that follows — when the measured part is clean,
because an unmeasured tail is not a clean result. It SHALL carry a self-test exercised by the
repository's CI, exercised also under a git configuration that alters the diff's shape, and SHALL
declare what escapes it: a file committed inside the same turn, a repository outside the working
directory, and the event's different name inside a subagent.

Where the work tree root carries the prose declaration, the artifact SHALL measure the same diff
with the shipped prose detector as well: a comment or docstring with strong evidence of the wrong
language blocks the end of the turn alongside any identifier finding, in one reason; a Markdown
paragraph in the wrong language reaches the assistant as a message and never blocks; and a
declaration the detector cannot read is named in a message rather than silencing the direction.
Without the declaration the artifact SHALL measure prose nowhere.

#### Scenario: A heredoc-written Portuguese file blocks the end of the turn

- **WHEN** a turn wrote `servico_cliente.py` with `def buscar_cliente(id_usuario)` through a shell
  heredoc, so no write-time hook ran, and the turn ends with the file uncommitted
- **THEN** the artifact answers with the block decision the installed harness reads for that event,
  and the reason names the path, the identifiers, and the three exits

#### Scenario: Once renamed, the turn ends

- **WHEN** the same file has been renamed and its identifiers translated (or waived with a stated
  reason) and the turn ends again
- **THEN** the artifact produces no output and the turn ends

#### Scenario: An active block is not repeated

- **WHEN** the payload carries `stop_hook_active: true` and the diff still has a gating finding
- **THEN** the artifact does not block; it emits a message listing what remains and exits zero

#### Scenario: Outside a git work tree the artifact is silent

- **WHEN** the working directory in the payload is not inside a git repository
- **THEN** the artifact produces no output and exits zero

#### Scenario: The informative mode silences the gate

- **WHEN** the session runs with the informative mode set and the diff has a gating finding
- **THEN** the artifact produces no output and exits zero, because the mode is the user's to set

#### Scenario: A diff over the declared cap says so

- **WHEN** the uncommitted diff has more lines than the declared cap and a gating finding within it
- **THEN** the reason states that the diff was truncated at the cap and that the rest was not
  measured, so the truncation is never silent

#### Scenario: A clean measured part over the cap is not a clean result

- **WHEN** the uncommitted diff has more lines than the declared cap and the part within the cap has
  no gating finding — clean or generated content that sorts ahead of a Portuguese file, for instance
- **THEN** the artifact still blocks the end of the turn once, its reason says the tail was not
  measured and how to measure it, and on the Stop that follows it reports as a message and lets the
  turn end

#### Scenario: The user's git configuration does not change what is measured

- **WHEN** `~/.gitconfig` sets an external diff driver, mnemonic prefixes or the default path quoting,
  and the turn edited a tracked file or wrote an untracked file whose name carries a non-ASCII letter
- **THEN** the artifact blocks as it would under a blank configuration, and the reason names the
  repository-relative path exactly as it is on disk

#### Scenario: A heredoc-written English comment blocks the turn in a repository declaring Portuguese prose

- **WHEN** the work tree root carries `.code-locale` with `prose: pt-BR`, a turn wrote a Python file
  whose comment reads as English through a shell heredoc, and the turn ends with the file
  uncommitted
- **THEN** the artifact blocks the end of the turn and the reason names the path, the line, the
  fragment and the exits; with the same comment in Portuguese, or waived on the line above, the
  turn ends in silence

#### Scenario: A Markdown paragraph in the wrong language is a message, not a block

- **WHEN** the same repository has an uncommitted `.md` file whose paragraph reads as English and
  no gating finding
- **THEN** the artifact emits a message naming the paragraph as advisory, does not block, and the
  turn ends

#### Scenario: Without a declaration the Stop gate measures no prose

- **WHEN** the work tree root carries no `.code-locale` and the uncommitted diff adds an English
  comment
- **THEN** the artifact produces no prose finding and decides exactly as it did before
