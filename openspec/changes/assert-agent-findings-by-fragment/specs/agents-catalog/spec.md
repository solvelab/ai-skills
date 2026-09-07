## MODIFIED Requirements

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

The self-test SHALL be able to assert **which finding** a case produced, not only which check owns
it, and SHALL do so wherever a check can produce more than one message. A check with several
messages that is proved only by its id cannot distinguish two paths through it, and a defect that
moves a case from one message to the other passes unnoticed.


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


#### Scenario: Two paths through one check are told apart

- **WHEN** a check can report more than one message and a case exists for each path
- **THEN** the self-test asserts the message the case expects, in addition to the check id, so a
  defect that swaps one path for the other fails a case
