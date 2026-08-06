## MODIFIED Requirements

### Requirement: Simulated failure behaviour

Any claim a skill makes about how prescribed code behaves under failure (timeout, dependency down,
partial payload, concurrency, replay, hostile input) SHALL be backed by a reproducible run of that
code against that failure before publication, and the skill SHALL state the measured outcome where it
motivates a rule.

A claim about a **performance or concurrency property** — blocking, serialization, throughput — SHALL
likewise be measured rather than asserted, and the measurement's conditions stated, so a reader can
reproduce or refute it.

#### Scenario: Prescribed snippet is exercised against the failure it claims to handle

- **WHEN** a skill ships a code snippet as the recommended handling for a failure mode
- **THEN** the snippet is run against that failure mode and the observed result is recorded
- **AND** if the result contradicts the surrounding doctrine, the snippet is corrected before the
  skill is published

#### Scenario: A quantified claim carries its measurement

- **WHEN** a rule is justified by a cost, a count, or a latency (e.g. "N callers each pay the full
  timeout", "worst case is X seconds")
- **THEN** the skill states the measured number and the conditions it was measured under, rather than
  an unquantified assertion

#### Scenario: A concurrency claim is demonstrated, not asserted

- **WHEN** a rule rests on a property like "this blocks the event loop" or "these serialize"
- **THEN** the property is demonstrated with a runnable measurement and the skill records the numbers
  and the conditions, instead of relying on the reader trusting the mechanism
