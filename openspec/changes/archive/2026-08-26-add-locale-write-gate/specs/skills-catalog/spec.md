## ADDED Requirements

### Requirement: The identifier-locale check reads the path it is given

The shipped identifier-locale check SHALL apply its tiers to the **path** of the artifact it scans —
directory names and the file stem — and not only to the artifact's contents, because file, directory
and module names are named by the doctrine as part of the machine layer. A check whose documented
scope names an artifact class it never reads SHALL be treated as a defect in the check, not as a
property of the artifact class.

The path tier SHALL reuse the exclusions the check already applies to identifiers — vendored and
generated trees, the minimum segment length, the kept domain terms and the allowlist file — so that
one rule change cannot make the two halves disagree.

The path measured SHALL be the part the scanned project owns: the path relative to the working
directory when the artifact lies inside it, and the file's own name otherwise. Segments above the
working directory SHALL NOT be scanned, because they name the machine, the user or the mount point
rather than anything the project chose.

In diff mode the path SHALL be checked only for files the diff **adds**. A file that already exists
SHALL NOT be reported on every diff that touches it, because renaming it is the migration policy's
decision and not this check's.

A path finding SHALL name the waiver that silences it. Since a file name carries no inline comment,
that waiver SHALL be the allowlist file the check already reads.

#### Scenario: A Portuguese file name with an English body is reported

- **WHEN** the check scans a file whose body is English but whose path carries Portuguese segments
- **THEN** it reports one finding per offending segment and exits non-zero
- **AND** the finding names the path and the segment, in the same shape an identifier finding uses

#### Scenario: An added path is measured and an existing one is not

- **WHEN** a unified diff adds a file whose path carries a Portuguese segment
- **THEN** the check reports it in diff mode
- **AND** a diff that only modifies an already existing file with the same path reports nothing about
  that path

#### Scenario: The path above the working directory is out of scope

- **WHEN** the artifact scanned lies inside the working directory
- **THEN** only the segments relative to that directory are measured
- **AND** an artifact outside the working directory has only its own file name measured

#### Scenario: A path finding names its waiver

- **WHEN** a path finding is printed
- **THEN** it states the allowlist entry that silences it, because a file name cannot carry the
  inline waiver an identifier uses

#### Scenario: The path tier inherits the identifier exclusions

- **WHEN** the scanned path lies in a vendored or generated tree, or its segments are shorter than
  the minimum length, or they are kept domain terms, or they are listed in the allowlist
- **THEN** the check reports nothing for that path, exactly as it already behaves for identifiers

### Requirement: The code-locale rite is enforced at the moment of the write

The catalog SHALL ship an enforcement artifact that measures the locale rule when a file is written,
not only when a diff is reviewed. Doctrine held in context and a check that must be invoked by hand
SHALL NOT be treated as enforcement: the repository already states, for its other two rites, that
enforcement must not depend on the assistant noticing a rule already in context.

The artifact SHALL run on the harness event that follows a file write, SHALL measure the written
path and the written content with the shipped check, and SHALL return its findings through the field
that harness reads for that event — established against the installed version, never assumed, since
plain standard output is not carried into context for that event.

The artifact SHALL be silent when the write is clean, SHALL NOT block the tool call, and SHALL
persist nothing outside the repository. Where the shipped check is absent, it SHALL exit silently
rather than fail, because a missing gate must not present itself as an error to the user.

#### Scenario: A write that introduces a Portuguese name is reported

- **WHEN** a file is written whose path or added content carries a Portuguese identifier
- **THEN** the findings reach the assistant as context for the next turn, naming the offending
  segments and the waiver that silences them

#### Scenario: A clean write is silent

- **WHEN** the written path and content are English
- **THEN** the artifact produces no output at all, so the reminder never becomes background noise

#### Scenario: The gate informs and never blocks

- **WHEN** the artifact reports findings
- **THEN** the tool call stands, and the decision to keep the name belongs to the user, as it does
  for the catalog's other rites

#### Scenario: A file type without a language profile still has its path measured

- **WHEN** the written file's extension has no language profile in the check
- **THEN** the path is still measured, and the content is reported as skipped rather than as passing

#### Scenario: A payload the artifact cannot read produces no error

- **WHEN** the payload is missing, malformed, or names no written file
- **THEN** the artifact exits silently and successfully, writing no state and requiring no credentials
