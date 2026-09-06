## ADDED Requirements

### Requirement: Code volume has a canonical home

The catalog SHALL contain one skill that governs how much code a change leaves behind: an ordered
ladder that asks, before any line is written, whether the need exists at all, whether the codebase,
the standard library, the platform or an already-installed dependency already covers it, and whether
one line does the job — and only then allows the minimum code that works. The ladder SHALL be stated
as running after the problem is understood, never instead of understanding it.

The skill SHALL state that a bug report names a symptom, that the fix goes where every caller routes
through, and that patching only the path the report names leaves the sibling callers broken. It
SHALL carry the carve-outs that are never simplified away — validation at a trust boundary, error
handling that prevents data loss, security measures, accessibility basics, anything explicitly
requested, the calibration knob of a constant that models the physical world, and one runnable check
behind non-trivial logic — as a top-level section that links to the canonical skills for the trust
boundary and for adversarial testing beyond that one check. It SHALL define a marker for a
deliberate simplification that names the ceiling and the trigger to revisit, and a ledger procedure
that harvests every marker and tags the ones with no trigger. It SHALL carry the review lens for
over-engineering — one line per finding, a fixed set of tags, a closing net line — and SHALL state
that correctness, security and performance are another review's job and that a single smoke test
or assert-based self-check is never flagged for deletion.

The skill SHALL NOT restate the scope guard: questioning whether a requested piece needs to exist is
a line in the *Assumptions* block that `verify-before-claiming` owns, never a silent omission. The
skill SHALL carry no number about its own effect that was not measured on this catalog's harness,
and SHALL name the file where that measurement lives.

#### Scenario: A native platform feature replaces a custom build

- **WHEN** an agent is about to write a component, a helper or a dependency for something the
  platform already ships — a date input, a database constraint, a standard-library function
- **THEN** the ladder stops at the rung that already holds, the native feature is used, and the
  skipped custom build is named in the delivery's trailer rather than silently dropped

#### Scenario: A report naming one caller fixes the shared function

- **WHEN** a bug report names one code path and the function it exercises is shared by others
- **THEN** the agent greps every caller before editing and places one guard in the shared function,
  so that the sibling callers the report did not name are fixed by the same diff
- **AND** a fix confined to the named caller is recorded as the defect the rule exists to prevent

#### Scenario: A trust-boundary guard survives simplification

- **WHEN** the ladder or the review lens is applied to code that validates input at a trust boundary,
  prevents data loss, or implements a security measure
- **THEN** that code is kept, the carve-out section is what decides it, and the lens never tags it
  for deletion
- **AND** the section links to the canonical skills for the boundary rule rather than restating them

#### Scenario: A simplification leaves a marker the ledger finds and one without a trigger is tagged

- **WHEN** a deliberate simplification cuts a real corner with a known ceiling
- **THEN** the code carries one marker naming the ceiling and the upgrade trigger, the ledger grep
  lists it as one row, and a marker that names no trigger is tagged so it cannot silently rot

#### Scenario: Questioning the need is a proposal, not an omission

- **WHEN** the first rung of the ladder says a requested piece may not need to exist
- **THEN** the doubt is written as a line in the *Assumptions* block of the scope restatement and
  the requested piece is built when the user confirms it, never dropped without a word
- **AND** the skill links to the canonical scope guard instead of restating it

#### Scenario: Review output is one line per finding and ends with the net

- **WHEN** the review lens runs on a diff or a tree
- **THEN** every finding is one line carrying a location, one of the fixed tags, what to cut and
  what replaces it, and the output ends with the net number of lines the diff could lose — or with
  the sentence that there is nothing to cut
