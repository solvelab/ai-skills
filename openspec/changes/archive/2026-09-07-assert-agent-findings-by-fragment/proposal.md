# Change: Let the agent self-test assert which finding fired, not only which check

## Why

`scripts/selftest-validate-agents.py` asserts the **check id** and nothing more: a case declares
`[A1` and any A1 finding satisfies it. Its sibling `scripts/selftest-validate-skills.py` already goes
one step further — an entry may carry `(check, fragment)` and the fragment must appear in the finding
— which is how a case like `C12 out-of-skill path (nested reference)` proves *which* path was
reported rather than that some path was.

The measurement in PR #229 made the cost visible. After the hardening, mutation over
`scripts/validate-agents.py` left 45 of 229 mutants alive, and four of them sit on the frontmatter
split offsets: `text.find("\n---\n", 4)` mutated to 3 and to 5, and `text[4:end], text[end + 5:]`
mutated to `+4` and `+6`. On the degenerate document whose delimiters are present with nothing
between them, the mutated path and the original **both** answer with an A1 finding — one calling it
absent, the other calling it not a mapping — so a suite that asserts `[A1` cannot tell them apart.
That case was added in #229 anyway, because it is a legitimate malformed input, and the fact that it
kills nothing was written into *Known gaps* rather than papered over.

The gap is not those four mutants. It is that a check owning more than one message cannot be proved
by message at all, which is exactly the reason the skills suite grew the fragment.

## What Changes

- `scripts/selftest-validate-agents.py`: a case may carry an optional fragment as a fourth element,
  in the shape the skills suite already uses. A case without one behaves exactly as today, so the
  54 existing cases are untouched.
- Fragments added where a check owns more than one message, starting with the two frontmatter paths.
- A case for the document whose frontmatter opens with an empty line, which is what separates the
  offset `4` from the offset `5`.
- The mutation measurement re-run under the conditions of #229 and reported as measured.

## Capabilities

### New Capabilities

### Modified Capabilities

- `agents-catalog`: MODIFIED *A published agent declares its admission and its privilege* — the
  self-test SHALL be able to assert which message a check produced, and SHALL use that wherever a
  check owns more than one, so two paths through the same check are distinguishable.

## Impact

- `scripts/selftest-validate-agents.py` only. `scripts/validate-agents.py` is not touched: its
  behaviour is correct, and what was missing is assertion power in the suite.
- No skill, no agent, no generated tree, so `generate.sh` does not run and the skill-version gate
  reports no skill changed.
