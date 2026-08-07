## Why

The catalog ships `backlog` and `execute-backlog`, but nothing makes the rite they encode
*happen*. Both skills describe themselves as invoked on request ("use when the user invokes
`/backlog`"), so an assistant that diagnoses a bug and then implements the fix never routes
through them — the work lands with no issue, no board item and no traceable PR. That is not a
hypothetical: it is how a real session on a downstream project produced nine changed files with
no backlog item behind them.

A rule the model may or may not notice is not a rite. The catalog already distributes portable
global rules; it should also distribute the enforcement that does not depend on the model
noticing.

## What Changes

- Add a **Development Rite** section to `claude/global/personal-rules.md`: every code change
  starts as a backlog item; diagnosing and answering stay free; plan mode is explicitly *not* a
  bypass; OpenSpec is a complement (new capability / breaking change / architecture) rather than
  a parallel path.
- Ship `claude/global/hooks/backlog-rite.py`, a `UserPromptSubmit` hook that inspects the prompt
  and injects the rite reminder when the request looks like a code change. Silent for diagnosis,
  for prompts already inside the rite (`/backlog`, `/execute-backlog`) and for explicit waivers.
- Document both in the README's *Global Personal Rules* section, including the `settings.json`
  wiring for the hook.
- Make `backlog` and `execute-backlog` state their place in the rite: each description gains the
  entry-point/second-step framing so the pair reads as one flow, not two unrelated commands.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skills-catalog`: the catalog gains a distributed enforcement artifact (a hook) alongside the
  portable global rules, and the two backlog skills are declared as the two halves of one rite
  rather than independent commands.

## Impact

- `claude/global/personal-rules.md` — new Development Rite section.
- `claude/global/hooks/backlog-rite.py` — new shipped script (no persisted state, no credentials).
- `README.md` — Global Personal Rules section documents the hook and its wiring.
- `skills/backlog/SKILL.md`, `skills/execute-backlog/SKILL.md` and their `claude/skills/` mirrors —
  description framing only; no workflow, gate or command changes.
- Consumers who wire the hook see one extra context line on prompts that look like code changes.
  Nothing is blocked: the hook informs, the user can always waive.
