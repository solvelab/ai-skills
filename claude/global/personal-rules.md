# Personal Rules (Global)

> **Note:** This file is the **repo maintainer's personal Claude Code config** — collaboration style, commit conventions, etc. It's published here as a working example of the "portable global rules" pattern (see the README section _Global Personal Rules_). If you clone this repo and want your own rules, edit this file (or maintain your own fork) — do not adopt the defaults blindly.

Portable rules for Claude Code. Included from `~/.claude/CLAUDE.md` via the `@` directive on every machine, so a single edit here propagates everywhere.

## Collaboration Style
- Be technically impartial. Do not agree to please me.
- When my request is suboptimal, push back with the better alternative and explain the reasoning briefly, as if to a child (simple, objective).
- If my idea is fine, still pause to consider if a better option exists before agreeing.
- Prefer the best long-term outcome over speed.
- Always stay technical and concrete.

## Development Rite (backlog-first)
Every code change starts as a backlog item. No exception for "small fixes" — small fixes are exactly what escapes traceability.
1. Idea or bug → `/backlog <idea>` → issue in the GitHub Project.
2. Issue → `/execute-backlog <n>` → branch, implementation, tests, PR with `Closes #n`.
- **Diagnosing, reading, explaining and answering are free.** The rite starts when code is going to change.
- **Plan mode is not a bypass.** An approved plan still becomes an issue before the first edit — `ExitPlanMode` approves the *plan*, it does not waive the rite.
- If I ask for code without an issue, say so and offer to run `/backlog` first. I can waive it explicitly; without an explicit waiver, do not start editing.
- Out of scope for the rite: personal config (`~/.claude`), scratchpad files, one-off ops commands.
- OpenSpec is a complement, not a parallel path — and in a repo that carries `openspec/`, the default is **fail-closed**: the backlog item also becomes an OpenSpec change, validated with `openspec validate <id> --strict` before the first edit outside `openspec/`. The exit is a written waiver, never a silent judgement: a line `Spec-rite: none — <reason>` in the PR body, which CI reads. A repo that carries the workflow and states no policy is treated as requiring the change; the policy itself lives in the repo's `spec_rite` config, not in my head. Classifying a change as "just an adjustment" is exactly how two blocking CI gates shipped unregistered and had to be backfilled — the classification now has to be written down to count.

## Grounding (no achismo)
Never guess. A claim is anything you assert **or act on** as if it were true — a sentence, a flag
written into a command, and a feature you decided to build on your own are all claims.
- Research before answering, in cheapest-first order: this session's context → this repo → the
  installed dependency source (the lockfile decides the version) → the tool itself (`--help`,
  `--version`, `--dry-run`) → docs pinned to that version → web search → ask me. Stop at the first
  rung that answers; never skip downward, because the web does not know *this* project.
- Could not find it? **Say so**, listing the commands you ran and the rungs you could not reach.
  Never substitute a plausible answer. A confident wrong sentence costs more than an admitted gap.
- Your memory of a library API is a hypothesis dated at your training cutoff; the lockfile wins.
- Cite only what you opened. If you cannot quote a line from it, you did not read it.
- Before acting, restate scope as **Doing / Not doing / Assumptions**. Anything I did not ask for is
  a guess about my intent — propose it, do not perform it.
- Full doctrine, templates and the anti-pattern catalog: the `verify-before-claiming` skill.

## Code Locale (prose is Portuguese, the machine layer is English)
Commit subjects, PR bodies, issue text, docs and code comments follow the repo's working language.
Everything a machine parses is English and ASCII: identifiers, function/class/file names, REST path
segments and query params, DB tables and columns, enum values, event/topic names, config keys, log
field keys.
- Portuguese belongs in the **values**, never in the keys: `{"status": "pending", "label": "Pendente"}`.
- A domain term with no faithful translation or with legal meaning (CPF, CNPJ, Nota Fiscal, PIX,
  boleto) keeps its name, deaccented, inside English grammar: `validateCpf`, `nota_fiscal_number`.
  It is legitimate only when the backlog item's Glossary lists it or the code carries an inline
  `locale-ok: <reason>`. An unlisted Portuguese noun is a defect, not a domain term.
- A foreign API that speaks Portuguese is mirrored only in its adapter/DTO (alias the wire name);
  past that boundary the domain model is English.
- Never improvise a translation — take the name from the codebase or the item's Glossary, and ask if
  it is in neither. An invented translation is an unverified claim (see Grounding).
- Existing code is not renamed for its own sake: new code is English, and a contract-bearing name
  (route, persisted column, event name, deployed config key) changes only through a deprecation window.
- This is enforced, not only remembered: the `locale-rite.py` hook **denies** a Write/Edit whose
  new content, or whose path when the write creates it, carries a Portuguese identifier
  (PreToolUse), and only informs after the write for words it is unsure about. A file that already
  carries a Portuguese name is edited freely and its name is only reported afterwards — the previous
  bullet applies. The exits are named in the denial itself — `# locale-ok: <reason>` on the line
  above (already in the file counts), the name or path in `.identifier-locale-allow`, or
  `LOCALE_RITE_MODE=inform` for the session. Files written through Bash are caught at the end of the turn by `locale-stop-gate.py`, which blocks the stop until the uncommitted diff is clean or waived.
- Full doctrine, exception protocol, migration policy and the detector: the `code-locale` skill.

## Commits & Pull Requests
- NEVER include the `Co-Authored-By` line in commit messages. Do not add any AI attribution or co-author references to commits under any circumstances.
- The same rule applies to **Pull Requests**: no AI attribution in the PR title, body, or description. Never add `🤖 Generated with Claude Code`, "Generated with", "Created by Claude", "Made with AI", or any line stating the commit/PR was produced by Claude, Anthropic, or any other AI. If a default PR-body template appends such a line (e.g. via `gh pr create`), strip it before submitting.
- Rationale: this is a human–AI interaction where I am the author and idealizer; the AI is a tool. Git artifacts must not attribute authorship to the AI.

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
