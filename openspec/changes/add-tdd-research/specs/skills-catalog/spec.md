## MODIFIED Requirements

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

Where the claim is about a **behaviour gain** of a skill or rule — that with it a model writes less
code, keeps a guard it would otherwise drop, reuses a helper instead of re-implementing it — the
record SHALL name the model id, the CLI version, the number of repetitions `n` and the arms
compared, and SHALL be measured against a baseline arm that is the same agent without the skill.
The arms SHALL be isolated from the maintainer's own hooks, plugins and skills, and that isolation
SHALL be proven by a probe recorded beside the result, because an upstream benchmark of the same
doctrine published a baseline that was secretly running the skill through a `SessionStart` hook.
A behaviour-gain number measured on another model, another CLI version or another repository is
not the catalog's number: it MAY be cited as the upstream's, with its conditions, and SHALL NOT be
presented as this catalog's measurement.

Where the behaviour gain claimed is an **order of production** — that with the rule the model
writes one kind of artifact before another, such as a test before the implementation it covers —
the record SHALL name the source of the order datum. Order does not survive in the final diff,
which shows state and not sequence, so the datum SHALL come from the session transcript; where the
harness fell back to any other source, such as file modification times, the record SHALL mark that
cell as a fallback and SHALL NOT publish a fallback-backed value as a measurement of order.

Such a record SHALL also declare whether the measured agent was able to execute anything. A rule
whose subject is a red-green cycle, measured in cells where the agent could not run a test, is a
claim about the order in which artifacts were written and about the quality of what remained — not
about the feedback loop — and the record SHALL say so in the words of what it did not cover.

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

#### Scenario: A behaviour-gain claim names its conditions

- **WHEN** a skill or a research record states that a rule reduces the code a model writes, keeps a
  guard, or makes it reuse existing code
- **THEN** the record names the model id, the CLI version, `n` and the arms compared, and the
  baseline arm is the same agent without the rule
- **AND** a record missing any of those is not a measurement and does not appear as one

#### Scenario: Arms are proven isolated before a number is recorded

- **WHEN** a behaviour-gain matrix is about to spend on a model
- **THEN** a probe has already shown, and the record keeps, that each arm loaded its own rules
  file and none of the maintainer's hooks or plugins, and a probe that fails stops the matrix

#### Scenario: An upstream number is cited as the upstream's

- **WHEN** the only available measurement of a rule comes from another model, CLI version or
  repository
- **THEN** the catalog cites it with those conditions and as the upstream's number
- **AND** SHALL NOT present it as a measurement of this catalog's skill

#### Scenario: An order-of-production claim names where the order came from

- **WHEN** a record states that a rule makes the model write a test before the implementation
- **THEN** the order datum comes from the session transcript, and the record says so
- **AND** a cell whose order was inferred from file modification times is marked as a fallback and
  is not published as a measurement of order

#### Scenario: A red-green claim declares whether the agent could run anything

- **WHEN** a record measures a rule whose subject is the red-green cycle
- **THEN** it states whether the measured cells could execute a test at all
- **AND** where they could not, the record presents the result as order of production and quality
  of the artifact that remained, never as a measurement of the feedback loop
