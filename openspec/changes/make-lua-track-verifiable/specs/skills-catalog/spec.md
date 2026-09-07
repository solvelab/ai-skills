## MODIFIED Requirements

### Requirement: The adversarial rite separates enumerating, generating and scoring

The catalog's adversarial-testing rite SHALL distinguish three activities rather than presenting one:
**enumerating** the scenarios an author can list, **generating** inputs from a stated invariant, and
**scoring** whether the resulting suite would notice the defect. Enumeration is the default and
always applies; each of the other two SHALL carry the condition under which it pays and a ceiling
naming the trigger that would raise it, so a small change is not made to carry a technique sized for
a large one.

A technique SHALL NOT be prescribed on a number taken from outside this catalog. Its yield SHALL be
measured against code in this repository before publication, with the conditions of the measurement
stated, and a measurement that came out unfavourable SHALL be published as measured rather than
replaced by a citation.

Every stack track SHALL answer both conditional layers rather than omitting them. Where the track's
ecosystem offers a usable tool, the track SHALL carry the probed command; where it offers none, the
track SHALL carry the probe that establishes the absence — the command and its output — and what the
rite does in its place. Silence in a track reads as "the layer does not exist here", which is a
claim, and an unprobed one.

A tool a track names without having run it SHALL be marked as unprobed at the point it is named. A
pointer stated as a prescription is the failure this requirement exists to prevent.


A track that records the **absence** of a tool SHALL also carry how the absence is re-established, so
a dated claim can be re-measured rather than trusted. A method a track publishes in place of a
missing tool SHALL be executable from the published text itself, and the check that executes it SHALL
read it from there rather than from a copy, so example and execution cannot drift apart while both
keep passing.

A check that cannot run SHALL report that it did not run. A script that exits successfully having
done nothing is a stronger false signal than no script at all.
#### Scenario: A generation technique is prescribed

- **WHEN** the rite prescribes generating inputs instead of listing them
- **THEN** it states the condition that makes the technique pay — a stateable invariant, not a
  category of code — and the ceiling at which enumeration remains sufficient
- **AND** it names what the technique yielded when it was measured here, including "no defects" when
  that is the measured result

#### Scenario: A scoring technique is prescribed

- **WHEN** the rite prescribes scoring an existing suite by breaking the code under it
- **THEN** the scope prescribed is the surface the change touched, not the repository
- **AND** the measurement that motivates the rule names the module, the suite, the tool version and
  the counts, so a reader can reproduce or refute it

#### Scenario: A prescribed technique carries the wrong command too

- **WHEN** the ecosystem's best-known tool for a prescribed technique fails or misleads under this
  catalog's conventions
- **THEN** the stack track names that command as the wrong one, with the failure it produces, beside
  the command that works

#### Scenario: A track whose ecosystem has no tool for a layer

- **WHEN** a stack track's ecosystem offers no usable tool for generating or for scoring
- **THEN** the track records the probe that establishes it — the command run and what it answered —
  and states what the rite does instead there
- **AND** the track does not leave the layer unmentioned, because silence claims the layer does not
  apply

#### Scenario: A tool named but not run

- **WHEN** a track points a reader at a tool this catalog has not executed
- **THEN** the tool is marked as unprobed where it is named, rather than presented as prescribed

#### Scenario: A declared absence carries its re-measurement

- **WHEN** a track records that its ecosystem offers no tool for a layer
- **THEN** the repository carries a command that re-runs the probes behind that record and fails
  naming whichever claim stopped holding

#### Scenario: A published method is executable from the text

- **WHEN** a track publishes a worked example as the method it prescribes in place of a missing tool
- **THEN** the check that exercises it reads the example out of the published track, not out of a
  copy
- **AND** the check proves the example witnesses the defect it claims to, by breaking the code under
  it and requiring the example to fail

#### Scenario: A check that cannot run says so

- **WHEN** the tooling a check needs is absent from the environment
- **THEN** the check reports a skip and a non-success result, never a pass
