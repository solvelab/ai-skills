## ADDED Requirements

### Requirement: A shipped script reads the quantity its host publishes

A skill that ships an executable displaying a quantity its host already computes SHALL read the
host's own value. It SHALL NOT reconstruct that quantity by accumulating samples of an observable
the host refreshes on a schedule unrelated to the events being counted.

The rule exists because reconstruction was measured and it does not converge. The status line
accumulated `context_window.current_usage` — the usage of the last API call — at its own ≤1 Hz
refresh, while the host published the authoritative total in the very same payload. Measured on
2026-09-07 against two real sessions: on a single-model session the reconstruction was **+11.5%** on
cache writes, **+2.0%** on cache reads, **−92.7%** on fresh input and **−54.5%** on output; on a
four-model session the total was **−35.4%**. The error had no fixed sign and no stable magnitude,
so no multiplier could correct it.

Where a script displays parts of a whole the host publishes, the parts SHALL be derived as a
share of the host's value rather than computed independently, so that they sum to it by
construction. A rate table embedded in the script MAY decide the proportion between parts; it SHALL
NOT decide the total, because a stale rate then produces a part larger than the whole — the defect
this requirement was written from.

A derived part SHALL be marked as derived wherever it appears next to a host-published value, so a
reader can tell which of two adjacent numbers is authoritative.

#### Scenario: the host publishes the quantity and the script samples instead

- **WHEN** a shipped script displays a running total the host already computes and exposes, whether
  in the payload it is handed or in a file that payload points to
- **THEN** it reads the host's value
- **AND** SHALL NOT bank samples of a per-event observable to approximate it

#### Scenario: the parts of a host-published whole

- **WHEN** a script breaks a host-published total into parts it computes itself
- **THEN** the parts are a share of that total and sum to it exactly
- **AND** SHALL NOT be computed independently of it, which lets a part exceed the whole

#### Scenario: two provenances on the same screen

- **WHEN** a script displays both a host-computed value and a value it derived itself
- **THEN** the derived value is marked as derived, and the skill states why the two can diverge
- **AND** SHALL NOT present them as if both were measured the same way

#### Scenario: the reconstruction is a lower bound

- **WHEN** a script can count only part of what the host counts, and the size of the gap is measured
  but its cause is not
- **THEN** the count is published for what it covers, and the skill records the measured gap
- **AND** SHALL NOT be labelled as the session's total
