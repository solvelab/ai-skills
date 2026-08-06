## MODIFIED Requirements

### Requirement: Shipped scripts state what they persist

A skill that ships an executable which writes state outside the repository SHALL state where that
state lives, what keys it, and how it is bounded. State that grows once per session SHALL be pruned
by the script itself rather than left to accumulate for the life of the machine.

Persisted records SHALL use a field separator that survives an empty field, and a record that does not
parse SHALL be discarded whole rather than partially trusted.

#### Scenario: A shipped script's state is discoverable

- **WHEN** a skill ships a script that persists anything between runs
- **THEN** the skill names the path, the key it is filed under, and the retention, so a user can find
  it, inspect it or delete it without reading the source

#### Scenario: Per-session state does not grow without bound

- **WHEN** a script keeps one state file per session
- **THEN** it prunes stale files on a cheap occasion (such as the first write of a new session),
  instead of relying on the user to clean up

#### Scenario: An empty field does not corrupt the record

- **WHEN** a persisted record contains a field that is empty for a legitimate reason
- **THEN** reading it back yields the same fields in the same positions, and a record that fails to
  parse is discarded rather than read with its values shifted
