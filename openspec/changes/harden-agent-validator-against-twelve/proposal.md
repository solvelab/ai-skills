# Change: Harden the agent validator against the twelve field-proof findings

## Why

`openspec/specs/agents-catalog/spec.md:74` already requires it: *"The gate SHALL NOT end by unhandled
exception on malformed input ... and the remaining agents SHALL still be checked. A gate that crashes
on the first bad input reports nothing about the inputs after it."* Two inputs break that today, and
were reproduced first-hand on `e56579a`: a `model` declared as a list raises `TypeError: cannot use
'list' as a set element`, and a `tools` value of 500 nested flow sequences raises `RecursionError`,
which is not a `yaml.YAMLError` and so escapes the handler. With the first planted, a second broken
agent placed after it alphabetically is never reported.

Two more inputs produce a false GREEN on A6: a body whose `##` sits alone on its line with
`When to invoke` on the next passes, because the check's `\s+` matches a newline; and a body whose
only `## When to invoke` lives inside a fenced code block passes, because the search runs over the
raw body. Both were planted and both returned `agents checked: 1   findings: 0`.

The remaining findings come from the same field proof (PR #223, issue #222), where a mutation run
left 54 of 205 mutants alive with the suite green — 20 of them on the limit constants and the
boundary comparisons, which have no witness in the 33 cases.

## What Changes

- `scripts/validate-agents.py`: malformed values become findings instead of tracebacks; A6 recognises
  a heading a Markdown renderer would render, and only outside fenced blocks; canonical and generated
  files are discovered regardless of the case of their suffix and of their depth; a whitespace-only
  entry in `tools` stops counting as a declared privilege; `NAME_RE` stops accepting a trailing
  newline.
- `scripts/validate-skills.py`: the same `RecursionError` escape at `:408` and `:592`. It is the same
  defect in a sibling that parses the same input with the same construct; fixing only the caller the
  report named is the symptom patch `lean-code` exists to refuse.
- `scripts/selftest-validate-agents.py` and `scripts/selftest-validate-skills.py`: a case per finding,
  both sides of every limit constant and the value itself, and a case with two agents where the first
  is defective.
- The mutation measurement is re-run under the same conditions and the new number is published beside
  today's 54, whatever it turns out to be.

## Capabilities

### New Capabilities

### Modified Capabilities

- `agents-catalog`: MODIFIED *Agents have a single canonical home and no orphans* — discovery of
  canonical files and of orphans is agnostic to the case of the suffix and to depth, because a file
  that escapes discovery escapes every check that follows.
- `agents-catalog`: MODIFIED *A published agent declares its admission and its privilege* — the
  malformed-input classes the gate must survive are named to include a value of the wrong shape and a
  payload whose nesting exhausts the parser; a declared privilege must be a non-blank name; the
  self-test must carry a witness on each side of every limit the gate enforces and one at the value;
  and a defect fixed in one gate must be fixed in every sibling gate that carries the same construct.

## Impact

- `scripts/validate-agents.py`, `scripts/validate-skills.py` and both self-tests. No skill, no agent
  and no generated tree changes, so `generate.sh` does not run and the skill-version gate reports no
  skill touched.
- Every pull request inherits a stricter A6 and a stricter A5: a body that passed by accident will
  now be reported. No published agent in the repository relies on either escape — verified before
  the change and re-verified after.
