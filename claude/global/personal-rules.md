# Personal Rules (Global)

> **Note:** This file is the **repo maintainer's personal Claude Code config** — collaboration style, commit conventions, etc. It's published here as a working example of the "portable global rules" pattern (see the README section _Global Personal Rules_). If you clone this repo and want your own rules, edit this file (or maintain your own fork) — do not adopt the defaults blindly.

Portable rules for Claude Code. Included from `~/.claude/CLAUDE.md` via the `@` directive on every machine, so a single edit here propagates everywhere.

## Collaboration Style
- Be technically impartial. Do not agree to please me.
- When my request is suboptimal, push back with the better alternative and explain the reasoning briefly, as if to a child (simple, objective).
- If my idea is fine, still pause to consider if a better option exists before agreeing.
- Prefer the best long-term outcome over speed.
- Always stay technical and concrete.

## Commits
- NEVER include the `Co-Authored-By` line in commit messages. Do not add any AI attribution or co-author references to commits under any circumstances.

## Model & Effort Tiering (token economy + quality)
Match effort and model to task **difficulty** — do not max everything (maxing trivial work wastes tokens, the opposite of the goal).
- **Trivial / conversational:** session model, effort `low`/`medium`.
- **Planning / hard reasoning / architecture decisions:** Opus 4.8 (Fable 5 only for the hardest), effort `high`/`xhigh`; `max` only when correctness outweighs cost.
- **Mechanical or parallel subtasks** (search, file reads, trivial edits, lint, broad sweeps): delegate to a subagent on a cheaper model (Haiku 4.5 / Sonnet 4.6) + effort `low`. Subagents have separate context, so a cheaper model there does NOT invalidate the main loop's prompt cache.
- **Reasoning-heavy subtasks:** keep a capable model — a cheaper model that gets it wrong means rework = more tokens + worse result.
- Apply this when spawning Agent/Workflow subagents (`model`/`effort` per call); don't switch the main session model mid-task (cache invalidation) — use a subagent instead.

---

## How to use on a new machine

1. Clone the repo (if not already):
   ```bash
   git clone git@github.com:solvelab/ai-skills.git ~/ai-skills
   ```

2. Reference this file from `~/.claude/CLAUDE.md`:
   ```markdown
   @~/ai-skills/claude/global/personal-rules.md
   ```

   Add other machine-specific blocks (e.g. `@RTK.md`, project paths) below as needed.
