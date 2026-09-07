## ADDED Requirements

### Requirement: An agent that applies a skill stays in step with it

When a published agent exists to apply a catalog skill's methodology, and that methodology gains a
layer, the agent's output contract SHALL carry the layer or the change SHALL state why it does not.
An agent whose contract silently lags the skill it names teaches the older methodology to every
caller that reads its output, which is worse than having no agent: the caller believes the rite ran.

The agent SHALL keep returning what it could not establish. A layer added to the contract SHALL NOT
displace the section that reports the lines of attack that produced nothing.

#### Scenario: The skill gains a layer the agent could carry

- **WHEN** a change adds an activity to a skill's methodology and a published agent applies that
  methodology
- **THEN** the agent's output contract gains the corresponding section in the same change, or the
  change records why the layer belongs only to the skill

#### Scenario: The contract grows without losing its negative half

- **WHEN** a section is added to an agent's output contract
- **THEN** the section that reports what was tried and found nothing remains mandatory and unchanged
