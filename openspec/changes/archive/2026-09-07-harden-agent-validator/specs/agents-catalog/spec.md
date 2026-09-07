## MODIFIED Requirements

### Requirement: Agents have a single canonical home and no orphans

The repository SHALL publish agents from exactly one canonical location, `agents/<name>.md` at the
repository root, and every copy under `plugins/<group>/agents/` SHALL be generated from it. An agent
present only in a generated tree is not a published agent: it escapes the generator, the validator
and the README, while still installing for users. CI SHALL reject that state, the same way it
rejects an orphan wrapper skill.

The canonical directory SHALL be flat. A subdirectory changes the name under which the agent is
invoked, so grouping by domain would be paid for in the name the user types.

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


### Requirement: A published agent declares its admission and its privilege

Every `agents/<name>.md` SHALL carry the frontmatter its harness requires — an identifier equal to
the file name, a description naming the conditions that route work to it, the model, and the colour —
and SHALL declare `tools` explicitly. Omitting `tools` grants every tool, so the declaration is the
difference between a stated privilege and an unstated one.

A required field declared with no value SHALL be treated as absent. A key present and null satisfies
a membership test while stating nothing, and `tools` declared null is equivalent at run time to
omitting it — the case the privilege rule above exists to refuse.

The gate SHALL NOT end by unhandled exception on malformed input. A directory carrying the file
suffix, a file that cannot be decoded, a dangling symlink, an unencodable character in a field, and
an anchor or alias in the frontmatter SHALL each become a reported finding that names the path, and
the remaining agents SHALL still be checked. A gate that crashes on the first bad input reports
nothing about the inputs after it.

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

#### Scenario: A required field present but null fails the gate

- **WHEN** an agent declares a required field with no value, or an explicit null
- **THEN** the validator reports it as missing, and every check that field feeds still runs

#### Scenario: Malformed input is reported, not fatal

- **WHEN** the canonical directory contains a directory named like an agent file, a file that cannot
  be decoded, or a dangling symlink
- **THEN** each is reported as a finding naming the path, the remaining agents are still checked, and
  the run still exits non-zero

