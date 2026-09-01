## ADDED Requirements

### Requirement: A published cost claim carries re-runnable backing

Where the catalog publishes a claim about the cost of a technique — that one approach is cheaper,
that a property triggers layout or paint, that an approach holds a frame budget — that claim SHALL
be backed either by an artifact in this repository that a reader can run, or by a named published
benchmark. A cost claim with neither SHALL be removed rather than softened into a hedge, because a
hedged guess reads as knowledge and is not.

The backing artifact SHALL live outside the directory the catalog publishes to consumers, so that
evidence is versioned and reviewable without being shipped to every project that enables a plugin.

Every recorded measurement SHALL state what was measured, by what method, and in which browser and
version. A number without its method is not re-runnable and therefore is not evidence.

The record SHALL state what it does not cover — the browsers, devices or conditions the measurement
did not reach — so that a passing number is not read as a general guarantee.

#### Scenario: A cost claim without backing does not ship

- **WHEN** a skill would assert that one technique is cheaper than another
- **THEN** the assertion carries a runnable artifact in this repository or a named published
  benchmark, or it does not appear at all

#### Scenario: Evidence does not reach the consumer's project

- **WHEN** a reader enables one of the published plugins
- **THEN** the backing artifacts are not part of what they receive, because they live outside the
  directory the generator publishes from

#### Scenario: A measurement states its method

- **WHEN** a measurement is recorded as evidence
- **THEN** it names what was measured, how, and the browser and version it ran in

#### Scenario: The reach of a measurement is declared

- **WHEN** a measurement covers one browser or one device class
- **THEN** what it did not cover is written beside it, so the number is not read as universal

#### Scenario: A contested fact is measured rather than cited

- **WHEN** the available sources disagree about a technique's cost
- **THEN** the disagreement is resolved by measurement recorded here, or the question is reported
  as open with the attempts that failed to settle it
