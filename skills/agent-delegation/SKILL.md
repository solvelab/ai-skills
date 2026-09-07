---
name: agent-delegation
description: >-
  Answers two questions kept apart: where a cross-cutting rule lives — a deterministic CI script, a
  hook the harness fires, or a skill loaded into context — and, separately, whether one piece of
  work runs in the calling loop or is dispatched to a subagent, which holds no rule, only runs
  under one. Use when a new rule needs a home, when about to spawn a subagent or define an agent, when choosing an agent's tools, model or effort, when a validator and an agent both
  seem to fit, and when the user says "should this be a skill or a hook", "write an agent for
  this", "delegate this", "spawn a subagent", "which model for this", "isso vira skill ou hook",
  "cria um agente pra isso", "delega isso", "qual modelo uso aqui". Do NOT use to decide how much
  code a change leaves behind (that is lean-code), to establish whether a fact is true before
  asserting it (that is verify-before-claiming), to break code already written (that is
  bug-hunter), or to write the prose of a documentation page (that is documentation).
metadata:
  author: solvelab
  version: 1.1.0
  category: process
license: MIT
compatibility: >-
  Doctrine only; no runtime, no CLI, no flag. The artifact kinds it names are the ones an
  assistant harness provides — a context-loaded instruction file, an event hook, a build script and
  a dispatched subagent. Where a harness lacks one of them, the row is unavailable, not wrong.
---

# Agent delegation — where a rule lives, and where the work runs

> **Not version-bound**: this skill does not depend on a tool version — it is a decision order,
> three admission tests and a privilege rule. The file format of an agent definition belongs to the
> harness that loads it and is deliberately not described here, so this doctrine does not have to
> change when that format does. Declared on 2026-09-07.

Two questions, and they are about different things. The first asks **where a rule lives**; the
second asks **where a piece of work runs**. An agent is never an answer to the first: it holds no
doctrine, it executes work under doctrine that lives somewhere else. Collapsing the two is how a
catalog grows a subagent for every rule a script already enforces.

## Question 1 — where the rule lives

Walk the rows top to bottom and stop at the first one that holds. The order is not taste: each row
costs more than the one above it, in tokens, in latency and in the number of ways it can be wrong.

| Where the rule lives | Take this row when | Real instance in this repository |
|---|---|---|
| **A deterministic script** | The rule can be decided by reading the tree and exiting non-zero. No judgement is involved — only a pattern, a count, a path that does or does not exist. | `scripts/validate-skills.py`, thirteen checks over the catalog, none of which asks anyone's opinion |
| **A hook** | The rule must fire whether or not the model notices it, at a moment the harness owns: a prompt arriving, a write about to land, a turn ending. | The locale write-gate, [`claude/global/hooks/locale-rite.py`](https://github.com/solvelab/ai-skills/blob/master/claude/global/hooks/locale-rite.py), which denies a write instead of hoping a rule in context was read |
| **A skill** | The rule needs to be in the model's context *before* the task, and the decision it governs is a judgement the model makes. | This file, and every other `skills/<name>/SKILL.md` in the catalog |

Two rules bind the table:

- **A row never replaces the row above it.** Where a script can decide, the script is the authority.
  A judgement layer above it — skill or agent — covers only what the script cannot decide, and
  covers it advisorily.
- **Advisory and blocking are different artifacts.** A mechanism that reports is not sold as a gate,
  and a gate that blocks says in its own text what escapes it. A rule enforced by judgement is
  advisory by construction, because the judgement can be wrong.

## Question 2 — where the work runs

Question 1 settled where the rule is written. This one is asked about a **task**: one application of
some rule, to some input, now. Its answers are only two — the calling loop does it, or an agent does.

The test that separates them is not "is this important" or "does this deserve a specialist". It is
the three admission tests below, and the giveaway that you are looking at agent-shaped work rather
than a rule is grammatical: a rule is a sentence in the present tense that is always true; a task
has an input, a start and an end.

- *"Everything a machine parses is English"* — a rule. It lives in a skill, and in a script for the
  half that is mechanical.
- *"Survey this repository and list every identifier that is not"* — a task under that rule. It has
  an input, it reads far more than it reports, and it ends. That is what Question 2 is for.

Write the rule once, then decide the task separately — and decide it again next time, because the
same rule produces tasks that pay and tasks that do not. A task that fails the tests below is not a
smaller agent; it is work the calling loop does itself.

### The three admission tests

Three tests. **All three must hold.** Two out of three means do the work inline and keep the result.

1. **Reading weight.** The work reads far more than it reports. A sweep over forty files that ends
   in a twenty-line table pays; a lookup in a file you already have open does not. Delegation buys
   context back, so there has to be context worth buying.
2. **Separable context.** The work needs the task statement and the tree — not the conversation
   that led here. If the answer depends on what the user said three turns ago, the subagent will
   either be told all of it (and the isolation was a lie) or miss it (and the answer is wrong).
3. **Checkable output contract.** The result can be trusted without redoing the work: a table of
   `path:line`, a verdict with its evidence, a list of cases. If the caller has to re-read
   everything to know whether the answer is right, nothing was saved.

### Three anti-patterns

Each passes a superficial reading of the tests and fails a real one:

- **One agent per skill.** A skill is already knowledge delivered into the context that needs it.
  Wrapping each one in a subagent adds a dispatch, a prompt and a summarisation step to work that
  was already in the right place. Agents are admitted one at a time, on the three tests, never by
  symmetry with an existing catalog.
- **An agent in place of a validator.** A model asked to check a mechanical property gives a
  different answer on a different day. If the property is mechanical, the script is cheaper, faster
  and reproducible — and the agent's real value, judgement about prose and intent, is exactly what
  the script cannot do. Put the agent where the script stops, not where it already works.
- **An agent holding a write the caller should hold.** Delegated work that produces a file — a test,
  a fix, a document — usually wants to return *what to write*, and let the calling loop write it.
  Authorship, review and the undo all live in the caller. Grant the write only when writing inside
  the isolated context is itself the thing being bought.

## Model and effort tiering

Match model and effort to the **difficulty of the work**, not to its importance. Maxing trivial work
burns the budget the hard step will need, which is the opposite of the goal.

- **Trivial or conversational** — the session's model, low to medium effort.
- **Planning, architecture, a decision that is expensive to reverse** — the most capable model
  available, high effort. The top of the range is for the case where being wrong costs more than
  the run.
- **Mechanical or parallel subtasks** — search, bulk reads, a lint sweep, a broad rename survey —
  a cheap model at low effort, inside a subagent. This is safe *because* the subagent holds its own
  context: a cheaper model there does not invalidate the calling loop's prompt cache, which is what
  makes the saving real rather than a tax paid twice.
- **Reasoning-heavy subtasks** keep a capable model. A cheap model that gets it wrong costs the run,
  the re-run and a worse answer.

Never swap the calling loop's model mid-task to save tokens — that invalidates its cache and pays
for the whole conversation again. Move the cheap work into a subagent instead; that is the same
saving without the cache loss.

Write the criterion, not the model names: the names current when a rule is written are superseded in
weeks, while difficulty, separate context and cache behaviour are not. A project or a maintainer
naming specific models does so as a local instance of this criterion, in its own configuration.

## Least privilege and the output contract

An agent definition declares two things the caller depends on and cannot see from outside.

**Tools, at the minimum the contract needs.** Omitting the declaration grants everything, so it is
always written out. Read-only work gets read-only tools; an agent that must not edit is made unable
to edit rather than asked not to. This is not distrust of the model — it is the same reason a
migration script does not run with a superuser role.

**An output contract, written in the definition itself.** State the shape the caller will receive,
and state what the agent must *not* return — the refusal is the half that keeps a locator from
drifting into a reviewer. An agent that reports a fact also reports how far it got: which sources
answered, which were unreachable, and what remains unknown. The general form of that report, and the
ladder behind it, is `verify-before-claiming`; do not restate it inside the agent.

## See also

- `lean-code` — how much code a change leaves behind. That skill asks whether this should be written
  at all; this one asks, once something must exist, which kind of thing it is. A rule that needs no
  new artifact at all is `lean-code`'s answer, and it outranks both questions here.
- `verify-before-claiming` — the research ladder, claim labelling and the not-found report that a
  research agent's output contract points at instead of reproducing.
- `bug-hunter` — the adversarial methodology itself. Deciding to delegate the analysis is this
  skill; performing it is that one.
