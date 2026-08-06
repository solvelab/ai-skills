## Context

#57 was tested — six synthetic turns, re-renders, model switch, corrupt state, missing ids — and still
shipped a defect that reset the very total it added. The tests missed it because they were generated
from one template that always supplied both ids, so the empty-field case the bug needs never occurred.
The failure was reported from real use within hours.

## Goals / Non-Goals

**Goals**
- Make the accumulator survive an empty field, which is the actual defect.
- Leave no path where a partially-read record is trusted.
- Record the trap where the next person will hit it.

**Non-Goals**
- Not recovering the accumulation lost to the bug. The values were shifted, not merely hidden; there
  is nothing to reconstruct, and `cost.total_cost_usd` was never affected.
- Not changing what the segment displays. #57's design stands; only its serialization was wrong.

## Decisions

**D1 — `\x1f`, not tab, and not "avoid empty fields".** Keeping tab and promising never to write an
empty field would work until the next field that can legitimately be empty. A non-whitespace separator
removes the class instead of the instance.

**D2 — Rewrite the block, do not keep patching it.** Three targeted edits left the payload read, the
state read and a guard on three different separators, and one of them silently did not apply because
its assertion was missing — accumulation broke entirely and only a regression run caught it. Replacing
the block as a unit made the invariant ("one separator, defined once") visible in the code.

**D3 — Assert every replacement.** The failed patch printed a success message because the message was
unconditional. That is the same defect class as a checker that cannot fail, which this repository
already has a rule against; it applied to the patch script and was not honoured.

**D4 — Discard an unparseable record whole.** Half-reading is worse than not reading: a shifted record
produces plausible numbers. The tail field is checked for being numeric, and anything else resets the
accumulator to zero — including every state file written by #57.

**D5 — Do not migrate #57's state files.** They may already hold shifted values; carrying them forward
would preserve a corrupted total under a fixed script. Restarting is honest and costs one session.

**D6 — Document the trap in `fields.md`, next to the accumulation note.** Anyone writing a status line
that persists anything meets this, and the payload itself contains fields documented as sometimes
absent — so the trap is reachable from the reference that describes them.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Status line script and its segments | `claude-statusline` | already canonical — serialization fixed |
| Harness JSON fields, their absence, and how to accumulate a session total | `claude-statusline/references/fields.md` | already canonical — separator trap recorded |
| Shipped-script state: location, key, bound, and now parse integrity | `openspec/specs/skills-catalog` | spec delta |
| Bounded state for a long-lived process | `log-event-collector` | link in spirit, unchanged |

## Risks / Trade-offs

- [Existing #57 state files lose their accumulation] → accepted and stated; they may hold shifted
  values, and the authoritative session cost was never in them.
- [`\x1f` is invisible in a terminal] → intended for a machine-read record; `cat -v` shows it as `^_`
  and the format is documented.
- [A future field could still be empty at the end of the record] → the tail check covers exactly that
  case by discarding rather than trusting.
