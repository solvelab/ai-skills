## ADDED Requirements

### Requirement: A published checkable rule holds on the skill that publishes it

Where the catalog publishes an organization rule together with a script that measures it, the skill
that publishes both SHALL pass that script. A rule its own author does not follow is a preference
with a citation attached, and a reference file that violates it teaches the violation: the file the
model imitates is the file the model reproduces.

Where a document legitimately cannot satisfy such a rule, the exemption SHALL be written down — in
the document, in the detector's own exclusion argument, or in the rule's stated limits — never left
as a silent finding that readers learn to scroll past.

A rule SHALL NOT be relaxed in order to make the publishing skill pass. The rule and its detector
are measured artifacts; the skill is the consumer that has to meet them.

#### Scenario: The skill that ships a detector is measured by it

- **WHEN** a skill publishes an organization rule and the script that checks it
- **THEN** running that script over the skill's own directory reports no finding
- **AND** a finding there is fixed in the skill, not by loosening the rule

#### Scenario: A reference file teaches by its own shape

- **WHEN** a reference file exists to be imitated — a template, a skeleton, a worked example
- **THEN** it satisfies the rules the same skill publishes, because a consumer copies the shape
  before reading the rule

#### Scenario: A document that cannot satisfy the rule says so

- **WHEN** a document genuinely cannot meet a published rule — a one-shot record that owes no index,
  a table whose cells are irreducible
- **THEN** the exemption is written where a reader meets it, and the reason is stated
- **AND** it is not left as an unexplained finding in the detector's output
