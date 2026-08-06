## Context

A rule accepted for one skill and never applied to the rest is not a rule — it is an exception that
happens to be documented. #24 established that trigger blocks in a skill body cost context and cannot
affect routing. This applies it to the four skills that still carried them, and puts it behind a check
so the next one is caught rather than argued again.

## Goals / Non-Goals

**Goals**
- The rule holds across the whole catalog, not the skill it was written for.
- No routing information is lost — cases the description misses get folded in first.
- The rule is enforced mechanically, like the other authoring rules.

**Non-Goals**
- Not touching doctrine. Only meta sections were removed; every rule, example and reference stays.
- Not rewriting descriptions wholesale. `helm-migration` gains a clause because it had none; the other
  three already routed correctly and were left alone.

## Decisions

**D1 — Check each block against its description before deleting it.** Assuming redundancy would have
thrown away `helm-migration`'s four anti-triggers, which were the only routing guidance that skill had
anywhere. Three of the four skills were pure duplication; one was not, and only checking told them
apart.

**D2 — Anti-triggers belong in the description because that is where they act.** A `Should NOT trigger
on` list inside the body is evaluated after selection already happened. Moving those four cases into
`helm-migration`'s description is the difference between documenting a routing rule and having one.

**D3 — Redirects count as routing guidance.** A first sweep flagged 17 skills for lacking a `Do NOT
use` clause; most of them route via a redirect instead (`for X use r3f-animation`, `see fivem-lua`),
which serves the same purpose. The requirement accepts either form, so the check does not manufacture
17 edits for a phrasing preference.

**D4 — Put the reasoning inside the check.** C8's docstring carries *why* a meta section is a defect,
so a contributor who hits it gets the argument rather than a rule number.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Where triggers and anti-triggers live | `openspec/specs/skills-authoring` | establish here (new requirement) |
| Mechanical enforcement of authoring rules | `scripts/validate-skills.py` | already canonical — gains C8 |
| Helm migration workflow and chart conventions | `helm-migration` | already canonical — description gains routing, body unchanged |
| Grooming and executing backlog items | `backlog`, `execute-backlog` | already canonical — meta blocks removed only |
| Claude Code status line setup | `claude-statusline` | already canonical — meta block removed only |

## Risks / Trade-offs

- [Trigger cases had value as author-facing test material] → the ones carrying information moved into
  the description; the rest were duplicates. Nothing that affected behaviour was lost.
- [C8 fires on a future skill that wants a usage example] → an example belongs in `references/`, where
  it loads on demand; the check names that in its message.
- [Descriptions grow] → `helm-migration`'s grew by one sentence and replaced 38 body lines.
