## ADDED Requirements

### Requirement: A review-only rule records the measurement that made it review-only

A catalog rule that ships without a validator SHALL record the measurement that produced that
verdict: the draft detector's findings, how many survived hand confirmation, how many were false
positives, and the sample the count was taken on. The bare label "review-only" is not sufficient,
because it is indistinguishable from a rule whose detector was never attempted.

The measurement SHALL be taken against a real repository the rule was drawn from, not a fixture. A
fixture proves the regex; only a repository proves the rule.

A rule whose draft detector produces a high false-positive rate SHALL ship review-only rather than
with the detector. A gate that fails without a defect is switched off in its first week, and a rule
enforced by a switched-off gate is worse than a rule with no gate at all, because it reads as
covered.

#### Scenario: A rule shipping without a validator carries its numbers

- **WHEN** a change publishes a doctrine rule and marks it review-only
- **THEN** the rule records the draft detector's findings, the hand-confirmed defects, the false
  positives and the sample, so a later reader can re-run the measurement instead of re-deciding it

#### Scenario: The label alone is treated as missing evidence

- **WHEN** a rule is marked review-only with no measurement beside it
- **THEN** it is treated the same as an unverified claim: either the measurement is taken, or the
  rule states explicitly that no detector was attempted and why

#### Scenario: A high false-positive rate decides against the gate

- **WHEN** a draft detector's findings are mostly false positives on the sample repository
- **THEN** the rule ships review-only and the measurement is recorded, rather than the detector
  shipping and the rule being enforced by a gate that reprove correct documents

#### Scenario: The sample is a repository, not a fixture

- **WHEN** the measurement behind a review-only verdict is recorded
- **THEN** it names the repository and the commit it was taken at, because a fixture built to
  exercise the detector cannot show what the detector does to documents nobody wrote for it
