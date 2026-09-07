# Change: Prove an acceptance by the absence of a finding, not by the exit code

## Why

`scripts/selftest-validate-agents.py` grew the fragment assertion in issue #232, and it covers only
the cases that must be **rejected**. The six accepting blocks at the bottom of `main()` — the four
limits at their value, the fifty-character name, and the two-agent case — still assert nothing but
`code != 0`.

The baseline block a few lines above them is stricter: it requires `"findings: 0" not in out` as well
as the exit code. So the same file holds two rigours for the same kind of assertion, and the weaker
one is on the blocks that exist precisely to prove the gate stays quiet.

That weaker form has two costs. A validator that exited zero while reporting something would pass,
because nothing reads the output. And when an accepting block does fail, the message is `was
rejected` followed by the whole run — it does not name the check that fired, which is the first thing
a reader wants and exactly what the `OTHER` line of the fragment cases now says.

## What Changes

- One acceptance helper, used by all six blocks, asserting the exit code **and** `findings: 0`.
- On failure it names the check that fired, extracted from the output, before printing the rest; when
  no check id can be found it says that rather than omitting it.
- No case is added and no case is removed: this raises the rigour of what already exists.

## Capabilities

### New Capabilities

### Modified Capabilities

- `agents-catalog`: MODIFIED *A published agent declares its admission and its privilege* — the
  self-test proves an acceptance by the absence of a finding rather than by the exit code alone, and
  a failed acceptance names the check that fired.

## Impact

- `scripts/selftest-validate-agents.py` only. No skill, no agent, no generated tree, so
  `generate.sh` does not run and the skill-version gate reports no skill changed.
