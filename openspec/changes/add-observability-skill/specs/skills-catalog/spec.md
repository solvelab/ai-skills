## ADDED Requirements

### Requirement: Observability has a canonical home

The catalog SHALL contain one skill that defines how a backend service is observed — request
correlation, metrics and their labels, and the reporting of degraded operation. Skills that
*prescribe* an observable action (incrementing a counter, emitting a correlated log line) SHALL link
to it for the definition rather than restating the mechanism.

#### Scenario: A prescribed metric has a defined home

- **WHEN** a skill instructs code to increment a counter or emit a correlated log line
- **THEN** the counter's registry, name and permitted labels are defined in `observability`, and the
  prescribing skill links to it instead of describing them

#### Scenario: Degraded operation is reportable

- **WHEN** a service is serving requests entirely from fallbacks
- **THEN** the doctrine provides a way to report it — a detailed-health field and a metric — so that
  liveness and readiness both passing does not read as healthy
