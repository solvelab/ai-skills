## ADDED Requirements

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
