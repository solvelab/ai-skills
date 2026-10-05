## MODIFIED Requirements

### Requirement: The development rite is enforced outside the model's discretion

The catalog SHALL state, in its portable global rules, that every code change starts as a backlog
item, and SHALL ship an enforcement artifact that fires without depending on the assistant noticing
the rule. The artifact SHALL inform rather than block: it never denies a tool call, and the user can
always waive the rite explicitly. Diagnosing, reading and answering SHALL remain unrestricted — the
rite applies only when code is going to change.

In a repository that runs a spec-driven workflow, the rite SHALL NOT end at the backlog item. The
spec artifact SHALL be named by the same enforcement artifact that names the backlog step, and the
naming SHALL be conditional on that workflow being present, so that the reminder stays silent where
it does not apply. A repository whose spec policy is unstated SHALL be treated as requiring the
artifact, so that the absence of a decision is not read as permission to skip it.

The workflow SHALL be looked for where the work belongs, not only in the working directory. When the
working directory is inside a repository, at any depth, the artifact SHALL look in the working
directory and in every directory above it up to that repository's root — the root found by walking
up the filesystem to the first repository marker, a directory or a file, so a linked work tree and a
submodule count, without calling the version-control tool — and the nearest directory that carries
the workflow's directory SHALL be the one that counts, which is how the workflow's own command-line
tool resolves its root. A repository whose root runs the workflow is then found from any depth, and
a working directory that carries the workflow below a root that does not keeps the sentence it
carries today. When the working directory is a workspace root — outside any repository, with
repositories as its direct subdirectories — the artifact SHALL look in each of those repositories
and SHALL name, in one sentence, the ones that run the workflow, staying silent about the spec rite
when none does. A directory outside any repository that carries the workflow's directory itself
SHALL keep the sentence, because the workflow does not require version control. The position of the
working directory SHALL NOT hide the workflow of the repository the work belongs to: a gate that
fails closed by doctrine must not fail open on the depth of the working directory.

The decision to ship without a spec artifact SHALL be a written one. A judgment made silently by the
assistant, or by a contributor in conversation, SHALL NOT satisfy the rite: the waiver SHALL exist as
a reviewable line in the pull request, and the gate SHALL be what reads it.

The enforcement artifact SHALL carry a self-test, exercised by the repository's own CI, that fixes
the decisions its design already assumes — what fires, what stays silent, and where the spec
sentence is appended — so that an edit to its signal list is measured rather than trusted. A
deliberately accepted false positive SHALL be fixed in that self-test as a case that fires, with the
recorded decision cited beside it, so that a well-meant correction cannot revert it unread. A
payload that is not a JSON object SHALL be ignored: the artifact exits zero with no output and no
traceback, because a hook that crashes on malformed input costs the turn it was meant to inform.
The self-test's cases SHALL NOT depend on the repository it happens to run in: every fixture that
stands for a repository carries the marker that stops the walk, and a case that needs a directory
outside any repository says so when the temporary directory cannot provide one, instead of passing
or failing on the runner's layout.

#### Scenario: A code-change request carries the rite into context

- **WHEN** a prompt asks for an implementation, fix, refactor or removal
- **THEN** the shipped `UserPromptSubmit` hook injects the rite reminder naming `/backlog` as the
  entry point and `/execute-backlog` as the second step
- **AND** the reminder states that diagnosis is free and that an approved plan is not a waiver

#### Scenario: The reminder names the spec rite only where it exists

- **WHEN** the prompt matches a code-change signal and the working directory, or a directory above it
  up to the root of the repository it is in, carries the spec-driven workflow's directory — whether
  the working directory is that root or a subdirectory at any depth below it
- **THEN** the reminder also names the spec artifact as a step that precedes the first edit outside
  that directory
- **AND** the same prompt in a repository where neither the working directory nor any directory up
  to its root carries that workflow produces the reminder without the spec sentence, so the added
  line never fires where it has no meaning

#### Scenario: The reminder is silent inside its own rite

- **WHEN** the prompt is already a rite command (`/backlog`, `/execute-backlog`), another slash
  command, or contains an explicit waiver
- **THEN** the hook produces no output, so the reminder never fires against the flow it enforces

#### Scenario: Plan approval is not a bypass

- **WHEN** an assistant finishes planning and the plan is approved
- **THEN** the rule as stated in the global rules requires the work to become a backlog item before
  the first edit, because approving a plan approves the plan and not the skipping of the rite

#### Scenario: The enforcement artifact persists nothing

- **WHEN** the shipped hook runs
- **THEN** it reads the prompt payload, matches, prints and exits, writing no state outside the
  repository and requiring no credentials

#### Scenario: The shipped hook carries a self-test and a malformed payload is ignored

- **WHEN** the hook is run with `--selftest`
- **THEN** it prints one OK/FAILED line per fixed decision plus a summary line and exits non-zero
  when any decision regressed, and the repository's CI runs that mode as a blocking step
- **AND** the case list includes a diagnostic question containing a change word as a case that
  fires, citing the decision that accepted the false positive
- **AND** when the payload on stdin is a JSON array, a JSON string or empty, the hook exits zero
  with no output and no traceback
- **AND** the case list includes a subdirectory of a repository whose root runs the workflow, a
  subdirectory that runs it below a root that does not, a workspace root with and without a child
  that runs it, and a repository whose marker is a file

#### Scenario: A workspace root names the repositories that run the spec rite

- **WHEN** the prompt matches a code-change signal and the working directory is outside any
  repository, with repositories as its direct subdirectories, and at least one of them carries the
  spec-driven workflow's directory at its root
- **THEN** the reminder carries one spec sentence naming each such repository and none that lacks the
  workflow
- **AND** the same prompt at a workspace root where no child runs the workflow produces the reminder
  without the spec sentence, as before

#### Scenario: A linked work tree or a submodule is a repository root

- **WHEN** the working directory sits below a directory whose repository marker is a file rather
  than a directory, and that directory carries the spec-driven workflow's directory
- **THEN** the reminder carries the spec sentence, found without calling the version-control tool

#### Scenario: The workflow outside any repository keeps its sentence

- **WHEN** the working directory is outside any repository and carries the spec-driven workflow's
  directory itself
- **THEN** the reminder carries the spec sentence, exactly as it did before the artifact looked for
  repository roots

### Requirement: The backlog skills declare their place in one rite

The `backlog` and `execute-backlog` descriptions SHALL identify each other as the two halves of a
single flow — creation then execution — so that a reader arriving at either one learns where the
work came from and where it goes next. Neither description SHALL restate the other's workflow.

Where the target repository runs a spec-driven workflow, both skills SHALL carry the gate that
workflow imposes between them, and neither SHALL restate its lifecycle: the lifecycle has a canonical
home in the catalog's own spec-driven skill, and the backlog skills SHALL link to it. The creating
skill SHALL record the verdict — the artifact that will exist, or the written waiver — in the item
itself, so the executing skill inherits a decision instead of making a new one. The executing skill
SHALL re-check that verdict against the change it is about to make, SHALL raise it without asking
when the work outgrew the item, and SHALL NOT lower it without the user, because a silent downgrade
is the failure this gate exists to prevent.

The policy SHALL be the repository's to set rather than the skills', because both skills run against
repositories with different rites; a repository that states no policy while carrying the workflow
SHALL be treated as requiring the artifact. In a workspace, the policy of each affected repository
SHALL come from that repository's own configuration first, then from the workspace's, then from that
fail-closed default.

Both skills SHALL detect the workflow, and run its commands, where it lives for the repository the
work targets — in the repository the working directory is in, whatever its depth, the nearest
directory carrying the workflow's directory between the working directory and that repository's
root; from a workspace root, the root of each affected repository — and never in the working
directory alone, because the workflow's command-line tool takes no path and answers that there are
no active changes from a directory that merely sits above a repository. Neither skill SHALL
conclude that a repository runs no workflow because the working directory does not carry one. From
a workspace root, the item SHALL carry one verdict per affected repository that runs the workflow,
so that the executing skill inherits a decision for each repository it will change.

#### Scenario: Entry point is discoverable from the execution skill

- **WHEN** a user reads the `execute-backlog` description
- **THEN** it names `backlog` as the step that produces the item it consumes

#### Scenario: Exit is discoverable from the creation skill

- **WHEN** a user reads the `backlog` description
- **THEN** it names `execute-backlog` as the step that turns the created item into a pull request

#### Scenario: The item carries its spec verdict

- **WHEN** the creating skill drafts an item for a repository that runs the spec-driven workflow
- **THEN** the drafted item declares either the change identifier and the capabilities its delta will
  touch, or the written waiver and its reason
- **AND** the verdict appears in the approval preview alongside the proposed field values

#### Scenario: The executing skill refuses to edit before the artifact exists

- **WHEN** the executing skill is about to change a file outside the spec-driven workflow's own
  directory, in a repository whose policy requires the artifact
- **THEN** it stops until the change exists and its strict validation is green, and the plan it
  presents for approval carries the change identifier, the affected capabilities and the validation
  output

#### Scenario: A verdict is raised silently and lowered only by the user

- **WHEN** re-analysis shows the work touches more than the item's waiver assumed
- **THEN** the executing skill raises the verdict to requiring an artifact without asking
- **AND** the reverse move — dropping a required artifact to a waiver — stops for an explicit user
  decision rather than being taken by the assistant

#### Scenario: Detection does not depend on the working directory's depth

- **WHEN** either skill runs from a subdirectory of a repository whose root carries the spec-driven
  workflow
- **THEN** it detects the workflow at that root, reads that repository's policy, and runs the
  workflow's commands with that root as the working directory

#### Scenario: A workspace item carries one verdict per affected repository

- **WHEN** the creating skill drafts, from a workspace root, an item that affects a child repository
  running the spec-driven workflow
- **THEN** the item's spec section declares that repository's verdict, with the policy read from that
  repository's own configuration, then the workspace's, then the fail-closed default
- **AND** an affected repository that does not run the workflow carries no verdict

#### Scenario: The executing skill does not skip the gate from a workspace root

- **WHEN** the executing skill runs from a workspace root for an item whose affected repository runs
  the spec-driven workflow
- **THEN** its spec step is not a no-op: the change is created and validated strict in that
  repository before any file outside that repository's workflow directory is edited

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

The written path SHALL be measured relative to the root of the repository the written file belongs
to, found by walking up from the file's directory to the first repository marker — a directory or a
file — and the allowlist SHALL be the one found from that root; the working directory in the payload
SHALL serve only as the fallback for a file that belongs to no repository, the rule the prose
declaration already follows. The position of the working directory — a subdirectory, or a
workspace root above the repository — SHALL NOT change which path is measured or which allowlist
speaks for it.

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
  the name or path is listed in the allowlist file found from the root of the repository the
  written file belongs to (from the working directory only when the file belongs to no repository)
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

#### Scenario: A write from a subdirectory measures the path from the repository root

- **WHEN** the working directory is a subdirectory of a repository and the event that precedes a
  write creates a file elsewhere in the same repository whose path carries a Portuguese segment
- **THEN** the artifact denies the write and the reason names the path relative to the repository
  root, exactly as it does when the working directory is that root

#### Scenario: A write from a workspace root answers to the child repository's allowlist

- **WHEN** the working directory is a workspace root and the event that precedes a write creates a
  file inside a child repository whose own allowlist lists the file's Portuguese segment
- **THEN** the artifact produces no output and the write lands
- **AND** without that entry the reason names the path relative to the child repository's root, so
  the allowlist line it implies is the one that silences it there

### Requirement: The code-locale rite closes the turn, not only the write

The catalog SHALL ship an enforcement artifact that measures the locale rule on the **result** of a
turn — the repository's uncommitted diff — and not only on the tool that wrote it. A write that
reaches the disk outside the harness's edit tools (a shell heredoc, `sed`, a script) is never seen by
the write-time artifact, so the rite that covers only the write SHALL NOT be treated as covering the
turn.

The artifact SHALL run on the harness event that ends a turn, SHALL read the working directory from
the payload, and SHALL measure the repositories the work belongs to: the git work tree that directory
is inside, or — when it is outside any work tree and its direct subdirectories are work trees, a
workspace root — each of those children. For each, it SHALL build the uncommitted diff — tracked
files against the current commit, plus every untracked file the repository does not ignore, each as
an added file — and measure it with the shipped identifier-locale check in its diff mode, honouring
that repository's own allowlist and the check's own exclusions. It SHALL measure only what the turn
left uncommitted: history and untouched lines never enter.

At a workspace root, the findings of every child SHALL reach one reason, each path prefixed with the
child's directory, while the line the reason prints as the allowlist exit for a file name SHALL stay
the one that silences it in that child's own allowlist — an exit that does not work when followed
produces the blind second attempt the write-time artifact already guards against. The declared line
cap SHALL be shared by all the children, and the time the artifact spends measuring SHALL have a
bound it declares, below the timeout of the wiring it documents; a child that the cap or the time
bound leaves unmeasured — never reached, or interrupted partway through its diff — SHALL be named as
not measured, with the same semantics as a capped diff. A child whose version-control call fails, or
does not answer within its own per-call timeout while the time bound still runs, SHALL be skipped
without blocking, the rule that already holds for a single repository.

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

The artifact SHALL be silent — no output, exit zero — where the working directory is outside any
git work tree and none of its direct subdirectories is one, on an empty diff, on advisory-only
findings, in the informative mode, and on a payload it cannot read. Where it measures, it SHALL
finish within the time bound it declares rather than within a fixed second, because the cost of one
clean repository depends on the filesystem it sits on: on a 9p-mounted filesystem it was measured
both under and above one second.
It SHALL cap the diff it measures at a declared number of lines and SHALL say so when the cap was
reached, never truncating in silence: in its reason when the measured part has a finding, and as a
block of its own — once, then a message on the Stop that follows — when the measured part is clean,
because an unmeasured tail is not a clean result. It SHALL carry a self-test exercised by the
repository's CI, exercised also under a git configuration that alters the diff's shape, and SHALL
declare what escapes it: a file committed inside the same turn, another repository when the working
directory is already inside one, a repository more than one level below a workspace root, and the
event's different name inside a subagent.

Where the root of a measured work tree carries the prose declaration, the artifact SHALL measure that
work tree's diff with the shipped prose detector as well: a comment or docstring with strong evidence
of the wrong language blocks the end of the turn alongside any identifier finding, in one reason; a
Markdown paragraph in the wrong language reaches the assistant as a message and never blocks; and a
declaration the detector cannot read is named in a message rather than silencing the direction.
Without the declaration the artifact SHALL measure prose nowhere, and a child of a workspace is
judged by its own declaration, never by another child's.

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

- **WHEN** the working directory in the payload is not inside a git repository and none of its
  direct subdirectories is one
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

#### Scenario: A workspace root measures each child repository

- **WHEN** the working directory is a workspace root and a child repository ends the turn with
  `servico_cliente.py` holding `def buscar_cliente(id_usuario)`, untracked
- **THEN** the artifact blocks the end of the turn and the reason names the file as
  `<child>/servico_cliente.py`, with its identifiers and the exits

#### Scenario: The allowlist line a workspace reason prints works when followed

- **WHEN** a child of a workspace root holds an uncommitted file whose only finding is its Portuguese
  name, and the line the reason prints as that name's allowlist exit is added to the child's own
  allowlist
- **THEN** the next Stop at the workspace root produces no output, because the printed line is
  relative to the child's root, where that allowlist is read

#### Scenario: Each child answers to its own allowlist and declaration

- **WHEN** two children of a workspace root end the turn with uncommitted changes, and only one of
  them lists the finding's name in its allowlist or declares its prose language
- **THEN** that allowlist and that declaration apply to that child alone, and the other child's
  findings are exactly what they would be with the working directory inside it

#### Scenario: Children past the shared cap or the time bound are named, never dropped

- **WHEN** the children's uncommitted diffs together exceed the declared line cap, or the time bound
  ends before every child was measured in full — before a child was reached, or partway through its
  untracked files
- **THEN** the artifact says what was not measured — in its reason when the measured part has a
  finding, and as a block of its own when it is clean, then a message on the Stop that follows —
  exactly as it does for one capped diff
