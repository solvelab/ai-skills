## Context

The repo's enforcement is layered and the layers are honest about themselves. `README.md` has a
*Where enforcement actually happens* section; `scripts/validate-rite.sh` opens by explaining that
the OpenSpec CLI does not check custom template sections; `scripts/validate-skills.py` carries
`KNOWN LIMIT` docstrings on the checks that cover only part of their rule. Any new enforcement has
to meet that standard or it lowers it.

What is missing is a layer that binds **evidence**. Today a change is gated on having a canonical-home
table, a quality-gates group and a closure group — all structural, none about whether the facts in
the change were probed.

## Goals / Non-Goals

**Goals:**

- Make evidence a required, reviewable artifact of every change, positioned where it is produced
  (first) rather than where it is remembered (last).
- Re-inject the doctrine at the moment a guess is caught, without waiting for the model to route to
  a skill.
- State plainly, in the artifacts themselves, what each layer cannot do.

**Non-Goals:**

- Detecting an un-researched claim mechanically. Nothing here does that, and nothing claims to.
- Blocking a tool call. `openspec/specs/skills-catalog` requires the enforcement artifact to inform
  rather than block, and the user can always waive.
- Per-skill provenance ledgers with CI checks — designed and rejected in the sibling change.

## Decisions

**The gate lives in `tasks.md` as the FIRST group, not in `design.md` and not in `proposal.md`.**
`scripts/validate-rite.sh:34` guards the design file with `if [ -f "$design" ]`, so a change without
a design doc silently escapes any gate placed there — evidence must not be skippable, which is the
entire point. `tasks.md` always exists: the schema declares `apply.tracks: tasks.md`. Splitting
evidence across proposal and tasks would create two places to drift and no single place to check.
First position is not decoration: it is the mirror of the proven last-group constraint on
`Validation & Closure`, and it encodes *probe before you write*.

**Evidence is a command plus a fragment of its raw output, never a conclusion.** "Verified against
kubectl 1.36.1" is unfalsifiable prose; `kubectl version --client -o json` → `"gitVersion":
"v1.36.1"` can be re-run by a reviewer in two seconds. This single format rule does more real work
than the grep does, and it is stated in three places — the template comment, the schema instruction,
and the hook reminder — because none of the three is machine-enforced.

**The hook is correction-triggered, not preventive.** A preventive `UserPromptSubmit` matcher was
designed and rejected: every plausible signal list (library, API, flag, version, "how do I")
matches most technical prompts, and a reminder that fires on every prompt stops being read — which
would also degrade the `backlog-rite.py` reminder sitting next to it in the same hook array.
Corrections are rare and unambiguous, so the hook fires when it is most likely to be read. Preventive
coverage goes to `personal-rules.md`, which costs once per session instead of once per turn.

**A `PreToolUse` variant on `Edit`/`Write` was rejected on evidence grounds.** It could parse
`transcript_path` and flag "about to write having read nothing this turn", but that is a proxy: it
false-positives on legitimate new-file creation, false-negatives on "read one file, then invent a
flag", and couples the hook to an undocumented JSONL layout. Shipping it as a detector would be
selling an advisory mechanism as a hard gate, which `skills-authoring` forbids. It is documented in
the hook's docstring as a rejected option, with its failure modes named.

**The in-flight change is backfilled rather than exempted.** Introducing a gate breaks work already
open. An allowlist would decay into a permanent exemption; backfilling the one active change costs
four lines and keeps the gate absolute from its first run.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Research ladder, claim labelling, not-found reporting, off-script scope guard | `verify-before-claiming` | already canonical — the hook reminder, the `personal-rules.md` block and the tasks template each carry a compressed operational form and name the skill; no mechanism list is reproduced |
| Backlog-first rite (issue → branch → PR) | `backlog` + `execute-backlog` | already canonical — the second hook sits beside `backlog-rite.py` and does not restate the backlog rite |
| OpenSpec lifecycle | `openspec` | already canonical — untouched; this change alters this repo's *forked* schema, not the vanilla lifecycle doctrine |
| "Advisory mechanisms are not sold as hard gates" | `openspec/specs/skills-authoring` (spec, not skill) | already canonical — applied here by giving `validate-rite.sh` a `KNOWN LIMIT` header and by stating in the README what the hook cannot enforce |

No skill file gains duplicated doctrine in this change. The compressed forms in the hook and in
`personal-rules.md` are deliberate: those two artifacts are read when the skill is *not* loaded, so
a pointer alone would carry nothing. Both name `verify-before-claiming` as the full doctrine.

## Risks / Trade-offs

- **The gate becomes a formality** — four boxes ticked without a probe behind them → the template,
  the schema instruction and the hook all demand the command and its raw output rather than a
  conclusion, and `validate-rite.sh` states in its own header that it checks presence and position,
  not truth. The review judges the evidence; the gate only guarantees it is there to judge.
- **Two hooks firing on one prompt** → the trigger sets do not overlap (change verbs versus
  correction phrases), the new reminder is shorter, and corrections are rare. Worst case is one
  prompt like "implementa o endpoint que você inventou" receiving both, which is arguably correct.
- **The gate breaks in-flight branches** → real and accepted; the one active change is backfilled in
  this change, and the breakage is declared in the proposal's Impact.
- **The README overstates what the hook enforces** → mitigated by an explicit paragraph naming the
  layer that survives an unwired contributor, verified against `.claude/settings.local.json`, whose
  only top-level key is `permissions` — this repo ships hooks for consumers and does not self-apply
  them.

## Migration Plan

The gate is additive to the template and the schema, so newly generated changes carry it
automatically. The single active change at the time of this proposal
(`add-verify-before-claiming`) is backfilled in the same commit. Rollback is a `git revert`: the
gate is four lines in one script plus template and prose edits, and no generated tree depends on it.

## Open Questions

None. The two candidate designs that would have been open questions — a preventive per-turn hook and
a `PreToolUse` transcript-based detector — were both designed far enough to be rejected on stated
grounds rather than left undecided.
