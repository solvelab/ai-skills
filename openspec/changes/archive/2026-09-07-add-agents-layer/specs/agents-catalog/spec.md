## ADDED Requirements

### Requirement: Agents have a single canonical home and no orphans

The repository SHALL publish agents from exactly one canonical location, `agents/<name>.md` at the
repository root, and every copy under `plugins/<group>/agents/` SHALL be generated from it. An agent
present only in a generated tree is not a published agent: it escapes the generator, the validator
and the README, while still installing for users. CI SHALL reject that state, the same way it
rejects an orphan wrapper skill.

The canonical directory SHALL be flat. A subdirectory changes the name under which the agent is
invoked, so grouping by domain would be paid for in the name the user types.

#### Scenario: An agent in a generated tree without a source is rejected

- **WHEN** a file exists under `plugins/<group>/agents/` with no matching `agents/<name>.md`
- **THEN** the agent validator reports it as an orphan and CI fails

#### Scenario: The generator refuses an agent it cannot place

- **WHEN** an agent exists in the canonical directory with no plugin group mapped to it
- **THEN** the generator fails before writing any file and before removing the generated plugin
  tree, so the working tree is left exactly as it was
- **AND** the error names the agent and where the mapping is declared

#### Scenario: Adding an agent goes through the canonical tree

- **WHEN** a new agent is added
- **THEN** it is written to `agents/<name>.md`, its plugin copies are produced by the generator, and
  it gains a README row — never hand-written into a generated tree

### Requirement: The agent layer declares that it is not portable

Agents SHALL be published only for the assistant that defines them, and the repository SHALL say so
where it publishes its portability claim. The catalog's other artifact — the skill — is generated
into a wrapper for every supported tool; an agent has no equivalent in tools that do not implement
dispatched subagents, and inventing one would publish behaviour that does not exist.

#### Scenario: The multi-tool table states the limit rather than omitting it

- **WHEN** the repository documents which tool consumes which artifact
- **THEN** it states that agents are published for one assistant only and produce no wrapper in the
  other generated trees
- **AND** the reduction is written where the portability claim is made, not left to be discovered

#### Scenario: No agent wrapper is generated for a tool that lacks the concept

- **WHEN** the generator runs
- **THEN** it writes agent copies only into the plugin trees, and none into the wrapper trees of
  tools that have no subagent concept

### Requirement: A published agent declares its admission and its privilege

Every `agents/<name>.md` SHALL carry the frontmatter its harness requires — an identifier equal to
the file name, a description naming the conditions that route work to it, the model, and the colour —
and SHALL declare `tools` explicitly. Omitting `tools` grants every tool, so the declaration is the
difference between a stated privilege and an unstated one.

The body SHALL carry a section naming the situations that invoke the agent, and SHALL state the
output contract: the shape the caller receives and what the agent must not return. An agent whose
work would produce a file SHALL return what to write rather than write it, unless writing inside the
isolated context is the work being bought.

Every published agent SHALL carry, in the repository, the written reason it passes the three
admission tests of the delegation doctrine. An agent admitted by symmetry with an existing artifact,
rather than by those tests, is a defect.

#### Scenario: An agent without a declared tool set fails the gate

- **WHEN** an agent omits `tools`, or names a write tool while its contract says it returns what to
  write
- **THEN** the validator fails naming the agent and the field

#### Scenario: An agent that does not say when to invoke it fails the gate

- **WHEN** the body carries no section naming the situations that invoke the agent
- **THEN** the validator fails, because a description alone routes without telling the agent what
  the caller expected

#### Scenario: The validator is itself gated

- **WHEN** the agent validator ships
- **THEN** a self-test proves each of its rules fails a violating agent and passes a conforming one,
  so the gate is not trusted on its own word

### Requirement: A published agent count names its members

A plugin description that publishes how many agents it ships SHALL name them, in a parenthetical
separate from the one that names its skills, and the repository hygiene check SHALL compare that
list with the tree. A count with no member list is unverifiable and is refused by shape; omitting
the agents entirely is refused too, because it makes a published artifact invisible where the
plugin is browsed.

#### Scenario: A stale agent list fails the hygiene check

- **WHEN** a plugin description names agents that its tree does not contain, or omits one it does
- **THEN** the hygiene check fails naming the group, the names in excess and the names missing

#### Scenario: The skills list is not disturbed by the agents list

- **WHEN** a group publishes both skills and agents
- **THEN** each list has its own parenthetical, so the check that reads the skills list matches
  exactly the skills and never absorbs the agent names
