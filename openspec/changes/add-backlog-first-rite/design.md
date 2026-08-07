## Context

The catalog distributes two kinds of artifact today: skills (loaded per task, by description
match) and portable global rules (`claude/global/personal-rules.md`, pulled into
`~/.claude/CLAUDE.md` with the `@` directive). Both depend on the assistant *reading and heeding*
them at the right moment.

The backlog rite has a failure mode that neither covers. A user asks "analyse this error"; the
analysis is legitimate work that needs no issue; the assistant then continues into implementation
without ever crossing a point where the skill descriptions would match. Plan mode makes it worse:
`ExitPlanMode` reads as a green light for code, so an approved plan becomes an unbacklogged change.

Claude Code's `UserPromptSubmit` hook runs on every prompt, outside the model's discretion, and
its stdout becomes turn context. That is the only mechanism available here that does not depend on
the model noticing a rule.

## Goals / Non-Goals

**Goals:**

- The rite is stated once, in the global rules, and carried by an artifact that fires without the
  model's cooperation.
- Diagnosis, reading and answering stay unrestricted — the rite starts when code is going to change.
- The two backlog skills read as one flow.

**Non-Goals:**

- Blocking edits. The hook informs; it never denies a tool call. A `PreToolUse` deny on
  `Edit`/`Write` would fire on scratchpad files, plan files and personal config, and a rite that
  fights the user gets uninstalled.
- Detecting intent perfectly. A false positive costs one line of context; a false negative costs
  traceability. The matcher is deliberately generous.
- Making the hook mandatory for catalog consumers. It is opt-in wiring in `settings.json`, like
  the global rules file itself.

## Decisions

**Hook over skill-description change alone.** Rewriting the `backlog` description to claim "all
code changes" would collide with every implementation-shaped skill in the catalog and still fail
the diagnosis→implementation drift, because no new prompt arrives at the moment the drift happens.
The description change is kept, but as framing, not as the enforcement mechanism.

**`UserPromptSubmit` over `PreToolUse`.** `PreToolUse` fires at the right moment (first edit) but
has no way to tell an in-rite edit from an out-of-rite one without reading conversation state the
hook does not have. `UserPromptSubmit` fires early enough to change the plan, and injecting
context is cheap and reversible.

**Python over shell.** The matcher needs a case-insensitive alternation over accented Portuguese
and English verbs, plus JSON parsing of the hook payload. `python3` is already assumed by
`scripts/validate-skills.py`; no new dependency.

**Silence list is part of the contract.** Prompts starting with `/backlog`, `/execute-backlog` or
other slash commands, and prompts containing an explicit waiver, produce no output. Without this
the reminder fires *during* the rite it is enforcing, training the reader to ignore it.

**No persisted state.** The hook reads stdin, matches, prints, exits. Nothing is written, so
`skills-catalog`'s *Shipped scripts state what they persist* requirement is satisfied by having
nothing to state — recorded here so a future reader does not go looking for a state file.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Backlog item creation (idea → issue → Project fields) | `backlog` | already canonical — the hook and the global rules name the command, they do not restate the workflow |
| Backlog execution (issue → plan → branch → PR → board) | `execute-backlog` | already canonical — same; the rite text points at it for the second half |
| Commit / PR message conventions used by the rite's PRs | `conventional-commit` | already canonical — the rite text does not restate commit formatting |
| Spec-driven flow for capability-level change | `openspec` | already canonical — the rite text states *when* OpenSpec applies (new capability, breaking change, architecture) and links; it does not restate the proposal/validate/archive flow |
| "Every code change starts as a backlog item" (the rite itself) | `claude/global/personal-rules.md` | new canonical home — the hook message and any downstream project `CLAUDE.md` state the trigger and defer here for the full rule |

The rite is a *user-level process rule*, not skill doctrine: it applies across every project and
every skill, so its home is the global rules file rather than any single skill. The two backlog
skills remain the canonical homes of their own mechanics.

## Risks / Trade-offs

- **Reminder fatigue on false positives** → the silence list covers in-rite prompts and explicit
  waivers, and the message is a single short paragraph rather than a block.
- **A generous matcher fires on pure questions containing "erro"/"bug"** → accepted deliberately:
  the injected text says diagnosis is free, so the correct behavior on a false positive is
  visible in the message itself.
- **Hook is opt-in, so a machine without the wiring loses enforcement** → the global rules file
  still carries the rule, and the README documents the wiring next to the rules setup it already
  describes.
- **Consumers who fork the catalog inherit a Portuguese-language matcher** → the message and the
  matcher cover both Portuguese and English verbs; the README states the file is meant to be
  edited like `personal-rules.md` itself.

## Migration Plan

Additive. Existing consumers see no change until they add the hook entry to `settings.json`;
`git pull` alone changes nothing at runtime. Rollback is removing that entry.
