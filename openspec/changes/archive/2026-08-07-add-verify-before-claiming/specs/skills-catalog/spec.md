## ADDED Requirements

### Requirement: Claim verification has a canonical home

The catalog SHALL contain one skill that governs how an agent establishes a fact before asserting or
acting on it: an ordered research ladder that starts with the cheapest source and ends by asking the
user, labels for what is verified, inferred and unknown, and a report for the case where the fact
cannot be found. The skill SHALL define a claim to include anything acted on as if true, not only
anything stated, so that delivering work the user did not ask for falls under the same rule as
inventing an API.

The doctrine SHALL be stack-agnostic. Skills that state a domain instance of it — reading a shipped
SDK stub, reading a chart template, refusing to guess a Project field — SHALL link to it rather than
restate the general rule.

#### Scenario: A fact that cannot be found is reported, not substituted

- **WHEN** the ladder is exhausted without establishing the fact
- **THEN** the agent produces a report naming the question, the commands run at each rung, the rungs
  that were unavailable and why, and what remains unknown
- **AND** no plausible substitute is emitted in place of the missing fact

#### Scenario: The doctrine degrades instead of failing when rungs are unavailable

- **WHEN** the environment provides no web-fetch or web-search tool
- **THEN** the ladder still runs over session context, the repository, the installed dependency and
  the tool itself, and the unavailable rungs are named in the report
- **AND** the absence of a rung is never treated as evidence that the unverified answer is probably
  correct

#### Scenario: The ladder declares when not to run

- **WHEN** a claim is already established in this session, or is a construct the surrounding
  toolchain would reject within seconds
- **THEN** the doctrine states that no research is owed, so that the rule is affordable on ordinary
  work rather than skipped wholesale as ceremony

#### Scenario: Unrequested work is treated as an unverified claim

- **WHEN** an agent adds a change the request did not ask for — an extra endpoint, a rename, an
  unrelated fix found along the way
- **THEN** the doctrine classifies it as an unverified claim about the user's intent, to be proposed
  rather than performed

### Requirement: A shipped checklist names the defect behind each row

A catalog skill that ships a catalog of failure modes SHALL record, for every row, the defect that
earned it, citable in this repository or in a named incident. A row whose origin cannot be named
SHALL be removed rather than kept.

#### Scenario: A row without provenance is not shipped

- **WHEN** a plausible-sounding failure mode is proposed for the catalog
- **THEN** it is added only if the defect that produced it can be cited, and is otherwise left out
- **AND** the growth rule states that a row whose origin column is empty is removed, not kept
