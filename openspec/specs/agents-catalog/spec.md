# agents-catalog Specification

## Purpose
TBD - created by archiving change add-agents-layer. Update Purpose after archive.
## Requirements
### Requirement: Agents have a single canonical home and no orphans

The repository SHALL publish agents from exactly one canonical location, `agents/<name>.md` at the
repository root, and every copy under `plugins/<group>/agents/` SHALL be generated from it. An agent
present only in a generated tree is not a published agent: it escapes the generator, the validator
and the README, while still installing for users. CI SHALL reject that state, the same way it
rejects an orphan wrapper skill.

The canonical directory SHALL be flat. A subdirectory changes the name under which the agent is
invoked, so grouping by domain would be paid for in the name the user types.

Discovery of both trees SHALL be agnostic to the case of the file suffix and to depth. A file whose
suffix differs only in case escapes every check that follows it, and a generated copy nested below
`plugins/<group>/agents/` escapes the orphan check while still shipping. Discovery is the first gate;
anything it misses is unchecked rather than approved, so its patterns SHALL NOT encode an assumption
that a filesystem is case-sensitive or that a generated tree is flat.

The check SHALL compare the generated copy with its canonical source by **content**, not by name
alone: a copy that has drifted from the source — hand-edited, or left behind by a stale generator run
— is published content with no canonical source, which is the state this requirement exists to
refuse. The check SHALL also run when the canonical directory is absent, because a missing
`agents/` with generated copies still present is itself that state, and a validator that returns
early there cannot see the very regression it owns.

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

#### Scenario: A generated copy that drifted from its source is reported

- **WHEN** a file under `plugins/<group>/agents/` differs in content from `agents/<name>.md`
- **THEN** the validator reports it, naming both paths

#### Scenario: A missing canonical directory does not silence the orphan check

- **WHEN** the canonical directory does not exist and generated copies do
- **THEN** the orphan check still runs and reports every copy as having no source
- **AND** a repository that legitimately publishes no agents still reports zero findings, because the
  check ran and found nothing — not because it was skipped

#### Scenario: A file the discovery pattern would miss is still judged

- **WHEN** a canonical file carries an uppercase suffix, or a generated copy sits in a subdirectory
  below `plugins/<group>/agents/`
- **THEN** it is discovered and judged like any other, rather than passing because nothing looked at it

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

A required field declared with no value SHALL be treated as absent. A key present and null satisfies
a membership test while stating nothing, and `tools` declared null is equivalent at run time to
omitting it — the case the privilege rule above exists to refuse. A declared tool name SHALL carry a
non-blank value for the same reason: a name made only of spaces is a privilege stated in form and
absent in substance.

The gate SHALL NOT end by unhandled exception on malformed input. A directory carrying the file
suffix, a file that cannot be decoded, a dangling symlink, an unencodable character in a field, an
anchor or alias in the frontmatter, **a field whose value is a collection where a scalar is
required, and a payload whose nesting exhausts the parser** SHALL each become a reported finding that
names the path, and the remaining agents SHALL still be checked. A gate that crashes on the first bad
input reports nothing about the inputs after it. Guarding a value SHALL be done by checking its shape
before the test that cannot survive it, never by wrapping that test in a handler that would turn the
crash into a silent pass for the field the check owns.

Where a defect of this kind is fixed in one gate, every sibling gate in the repository that parses
the same input with the same construct SHALL be fixed in the same change. A gate hardened alone
leaves the identical input fatal one file over.

The body SHALL carry a section naming the situations that invoke the agent, and SHALL state the
output contract: the shape the caller receives and what the agent must not return. That section
SHALL be recognised only where a Markdown renderer would render it as a heading: hashes followed on
the same line by the heading text, outside any fenced code block. An agent whose work would produce a
file SHALL return what to write rather than write it, unless writing inside the isolated context is
the work being bought.

Every published agent SHALL carry, in the repository, the written reason it passes the three
admission tests of the delegation doctrine. An agent admitted by symmetry with an existing artifact,
rather than by those tests, is a defect.

The self-test that gates this validator SHALL carry, for every limit the gate enforces, a case on
each side of the limit and one at the value itself. A suite that proves only that a limit fires
leaves the limit's position unmeasured, so moving the constant breaks nothing and the check is
covered on paper and untested in fact.

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

#### Scenario: A required field present but null fails the gate

- **WHEN** an agent declares a required field with no value, or an explicit null
- **THEN** the validator reports it as missing, and every check that field feeds still runs

#### Scenario: Malformed input is reported, not fatal

- **WHEN** the canonical directory contains a directory named like an agent file, a file that cannot
  be decoded, or a dangling symlink
- **THEN** each is reported as a finding naming the path, the remaining agents are still checked, and
  the run still exits non-zero

#### Scenario: A value of the wrong shape does not end the run

- **WHEN** a scalar field is declared as a sequence or a mapping, or a value nests deeply enough to
  exhaust the parser
- **THEN** it is reported as a finding naming the path and the field, and an agent placed after it is
  still checked

#### Scenario: A heading that is not rendered as one does not satisfy the body rule

- **WHEN** the invocation section's hashes stand alone on their line, or the only such heading lies
  inside a fenced code block
- **THEN** the validator reports the section as missing

#### Scenario: A limit is proved at its own value

- **WHEN** the gate enforces a minimum or a maximum
- **THEN** the self-test carries an accepted case at the limit, a rejected case one past it, and an
  accepted case one inside it, so a changed constant fails a test

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

