# Design — hardening the agent validator against twelve findings

## Context

`scripts/validate-agents.py` and its 33-case self-test were hardened once already, under issue #205,
against six findings from the same analyst. The twelve findings here came from a second pass run
during the field proof of issue #222, and from a mutation measurement that used the self-test itself
as the runner: 205 mutants, 151 killed, 54 survived, with 20 survivors sitting on the limit constants
and the boundary comparisons.

The two crashes are the important ones. They are not new requirements — the published requirement
already forbids them, in the sentence *"A gate that crashes on the first bad input reports nothing
about the inputs after it."* What this change adds to the spec is the two input classes that reach
that state, so the next reader does not have to rediscover them.

## Goals / Non-Goals

**Goals:**

- No frontmatter value ends the process by traceback; every one becomes a finding carrying the id of
  the check that owns it.
- A6 accepts only a heading a Markdown renderer would render as one, and only outside fenced blocks.
- Every limit the gate enforces has a witness on each side and one at the value, so moving the
  constant kills a test.
- The mutation number is re-measured under the conditions of the first measurement, so the two are
  comparable, and published as measured.

**Non-Goals:**

- Making mutation testing a CI gate of this repository. The doctrine shipped by #222 is scoped to a
  change; turning it into a pipeline is a decision of its own.
- Touching any published skill or agent, or the generated trees.
- Rewriting A7's drift check, which is correct and tested.

## Decisions

**D1 — The type guard goes before the membership test, not around it.** `model not in MODELS` raises
only because an unhashable value reaches it. Wrapping the expression in `try` would convert the crash
into a silent pass for the very field the check owns. The value is checked for being a string first,
and a non-string is the finding.

**D2 — `RecursionError` is caught beside `yaml.YAMLError`, in both gates.** It is raised by the parser
on input the parser cannot handle, which is exactly what the existing handler is for; it is simply not
a subclass of `YAMLError`. `scripts/validate-skills.py:408` and `:592` carry the same bare
`except _yaml.YAMLError` over the same `safe_load`, so they are fixed in this change. Fixing only
`validate-agents.py` would leave the sibling gate crashing on the same 1 KB payload.

**D3 — A6 stops using `\s+`.** The intent was "the heading text follows the hashes on the same line";
`\s` includes `\n`, so an empty heading followed by a paragraph satisfies it. The fix is `[ \t]+`.
Separately, fenced blocks are removed before the search, the way the sibling validator already does
for its own citation check — the same construct, so the same treatment.

**D4 — Finding 10 is researched before it is coded.** A duplicate frontmatter key (`tools: ~` then
`tools: ["Read"]`) currently yields no finding: PyYAML keeps the last value silently, so the gate
judges a value the harness's own reader may not pick. Which key the harness takes is a fact about the
harness, not a guess to encode — it is probed by planting an agent with duplicate keys in a scratch
project and asking a fresh session what privilege it holds. If the probe cannot settle it, the finding
is recorded as a written gap in the Evidence group and no code is written for it, because a test built
on the wrong assumption locks the wrong behaviour in.

**D5 — Boundary witnesses live in the self-test, not in the gate.** Findings 5, 6, 7 and 12 name no
defect in the validator's behaviour; they name the absence of evidence that the behaviour is what the
gate claims. The fix is cases, on both sides and at the value, plus the two-agent case whose absence
is what let the crash stay invisible.

**D6 — The re-measurement is reported as it comes out.** If survivors on the limit constants do not
fall to zero, the number is published with the condition rather than adjusted. A measurement that
disagrees with the change is information about the change.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Fix the root cause, grep every caller, never patch only the named path | `lean-code` | link — D2 applies it and points there |
| Adversarial defect classes and the enumerate/generate/score layers | `bug-hunter` | already canonical — this change is an application of it, not an edit to it |
| Measure a claim before publishing it; report what could not be probed | `verify-before-claiming` | link — D4 and D6 apply it |
| What a published agent must declare and what its gate must survive | `agents-catalog` (spec) | already canonical — this change modifies it |

## Risks / Trade-offs

- **A stricter A6 and A5 could reject a published agent.** Checked before writing the change: the
  three published agents pass today and must still pass; the self-test carries the accepting cases.
- **Removing fenced blocks before the A6 search could hide a legitimate heading** that a reader
  intended inside a fence. That is the correct outcome: a heading inside a fence is not rendered as a
  heading, so it does not satisfy the requirement either.
- **The `RecursionError` guard could mask a real stack overflow in our own code.** It is caught only
  around the parse call, never around the checks.

## Open questions

- Finding 10, until D4's probe settles it.
