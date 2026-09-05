---
name: documentation
description: >-
  Creates and updates project documentation sized to what the project actually is — README.md plus
  only the deeper docs the code warrants, organized by reader need (tutorial / how-to / reference /
  explanation). Use whenever the user mentions README, docs, SETUP, TECHNICAL, CHANGELOG, AGENTS.md,
  "document this", "write the docs", "update the readme", "explain how this works", "help someone
  understand this project", or asks to document a codebase for AI tools or new developers. Enforces
  read-the-code-first, machine-checkable claims, one purpose per page, and docs that change in the
  same commit as the code. Do NOT use for non-software documentation tasks.
metadata:
  author: solvelab
  version: 3.0.3
  category: docs
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

# Documentation

> **Not version-bound**: this skill does not depend on a tool version — it decides which documents
> a project gets and how a claim inside them is made checkable, and it prescribes no generator,
> linter or CLI. The `AGENTS.md` convention it names is a specification, not a versioned tool.
> Declared on 2026-09-05.

Write documentation a reader can act on and a script can verify. Templates and full worked examples
live in `references/` — read them when you are about to generate output, not before.

## Analyze before documenting

Never write a line of documentation before reading the code it describes.

1. `find . -type f -not -path "*/.git/*" | head -60` — structure.
2. Read the entry point, the config module, the dependency manifest, and any existing docs.
3. Identify: language, framework, how it is configured, how it is run, what it integrates with.
4. **Extract the facts**, don't invent them: env vars from the config module, endpoints from the
   router, commands from the manifest scripts / Makefile / CI, ports from the compose file.

Only document what you read. A fact that matters and could not be verified is written as an admitted
gap ("Deployment target: not documented in this repo"), never guessed — the ladder for finding it and
the report to write when it cannot be found are `verify-before-claiming`.

## Decide which documents exist

`README.md` is the only unconditional document. Everything else is earned:

| Condition | Document |
|---|---|
| Any project | `README.md` |
| A `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md` or `.clinerules` exists, **or** the user asked to document the repo for AI tools | `AGENTS.md` |
| Setup takes more than ~5 commands, or has environment prerequisites | `docs/SETUP.md` |
| Architecture a reader cannot infer from the tree (services, flows, integrations) | `docs/TECHNICAL.md` |
| REST/GraphQL API with no generated spec published | `docs/API.md` |
| Project accepts outside contributions | `CONTRIBUTING.md` |
| More than one deploy environment | `docs/DEPLOYMENT.md` |
| Releases are tagged | `CHANGELOG.md` (generated, not hand-written) |
| Background workers, webhooks, ML pipelines, CLI, SDK, security-sensitive config | the matching `docs/<topic>.md` |

**Do not create a document to satisfy the table.** A 200-line project with a 3-command setup needs a
README and nothing else; splitting it into three tiers produces three files that rot instead of one
that doesn't. If you create only a README, say so and why.

## One purpose per page

Four reader needs, four kinds of page. Mixing them is the most common reason docs go stale and the
most common reason readers can't find anything:

| Need | Page kind | In this model |
|---|---|---|
| "Get me running for the first time" | **Tutorial** — one happy path, no options | `docs/SETUP.md` |
| "How do I do X?" | **How-to** — task-oriented, assumes context | `README.md` quick start, `docs/<topic>.md` |
| "What exactly does Y take?" | **Reference** — exhaustive, dry, generated where possible | config tables, `docs/API.md` |
| "Why is it like this?" | **Explanation** — design rationale, trade-offs | `docs/TECHNICAL.md`, ADRs |

The practical rule: **how-to content changes far faster than why content.** A page that mixes a
command sequence with architectural rationale goes stale at the speed of its fastest-changing half.
Keep them on separate pages, and cross-link.

## Every claim must be checkable

This is the difference between documentation and decoration. Prefer facts a script can verify against
the repo, and write them so it can:

- **Repo paths are links**, not prose: `[app/main.py](app/main.py)`. A link is checkable; a sentence
  is not.
- **Directory trees show the real root.** Measured on a production repo: a README tree written without
  its `src/` prefix made every path in it unresolvable, and one entry had been renamed months earlier
  — 9 of 10 entries wrong in a block the reader trusts most.
- **Directory trees are the highest-rot artifact you can write.** They duplicate the filesystem and
  break on every refactor. Include one only when the layout is genuinely non-obvious, cap it at the
  directories that carry meaning (not every file), and annotate each with its purpose. Never paste a
  full `tree` dump.
- **Never hand-copy what a tool generates.** Endpoint tables duplicating an OpenAPI spec, flag tables
  duplicating `--help`, changelogs duplicating the release tool — link or generate them. Hand copies
  drift silently and there is no signal when they do.
- **Env var tables come from the config module**, and every row must name a variable that exists in
  the code. A documented variable the code never reads is a bug report waiting to happen.
- **Commands are copy-paste runnable.** Run them, or state that you did not. Show expected output for
  anything whose success is not obvious.
- Ship the checker. A ~50-line script that resolves every link, every tree path, and every documented
  env var, wired into CI, turns "the docs are stale" from a discovery into a build failure.

## Keeping it true

Documentation rot is the default outcome; the only reliable fix is process, not diligence:

- **Docs change in the same commit as the code.** A PR that adds an env var and does not touch the
  config table is incomplete — treat it the way you would treat a missing test.
- **Every document names an owner** (a person or a team) in its footer or frontmatter. An unowned doc
  is nobody's job.
- **Date the volatile parts.** Version numbers, screenshots, benchmark figures and "current status"
  sections carry the date they were verified.
- **Delete aggressively.** A section describing a removed feature is worse than no section — it
  actively misleads. Prune when you touch a page.

## AGENTS.md — the repo's instructions for coding agents

When AI agents work in the repo, the conventions they need live in `AGENTS.md` at the root — an open
spec (donated to the Linux Foundation's Agentic AI Foundation in December 2025) that most agent tools
now read. Anthropic's `CLAUDE.md` serves the same role for Claude Code; when both exist, keep one
canonical and have the other point at it rather than maintaining two.

Content that measurably helps: **architecture overview, where the important files are, and how to
build/test/run.** Be honest about the ceiling — the published evaluation of repository context files
on SWE-bench found gains modest and inconsistent across models, with setup and build guidance the most
valuable part. Write it for that: concrete commands and locations, not aspirational style rules.

`AGENTS.md` is about *contributing to this code*. It is not a substitute for the README, and it is a
different thing from `llms.txt`, which maps a documentation *site* for retrieval.

**The trigger has to be something you can see.** "This repo is worked on by agents" is not observable
from a checkout — measured: with that phrasing, no run produced the file. Use the detectable signals
in the table above: an existing tool-specific instruction file, or the user asking for it. When none
is present, do not create `AGENTS.md` silently — say it is missing and what it would carry.

## README

Lead with what the software does and why, in one sentence, above everything else. Then only the
sections this project earns. The full skeleton and a worked example: `references/templates.md` and
`references/examples.md`.

- **Quick start is 3-5 commands.** More than that means it is a tutorial — move it to `docs/SETUP.md`
  and link.
- **Tables for structured data** (env vars, endpoints, commands, tech stack); prose only for context.
- **Text diagrams over images** — greppable, diff-able, readable by agents.
- **Badges: signal only.** A badge that cannot fail carries no information — a hardcoded
  `python-3.12-blue` shield is decoration. Live badges (CI status, coverage, published version) are
  worth their space; static ones are not. For internal services and private tools a plain H1 plus a
  one-line description is the correct header. Each badge is also a third-party request served to every
  reader, so keep the set small.
- **Include a logo** in a centered header block only if one already exists in the repo.

## Writing style

1. **Imperative for instructions.** "Run the migration", not "you may wish to run".
2. **Show, don't explain.** A code block beats a paragraph.
3. **One term per concept**, used consistently across every document.
4. **Document the why for non-obvious decisions** — the constraint that forced the choice, not the
   choice alone.
5. **Real values, never `foo`/`bar`.** Realistic payloads, actual config values.
6. **Warn about footguns** in bold, at the point of danger, not in a distant section.
7. **Match the project's existing language and voice.** Portuguese docs stay Portuguese — but an
   identifier, route or config key quoted in the docs is copied from the code verbatim, never
   translated (`code-locale`).

## Updating existing documentation

1. **Keep the existing structure** unless asked to reorganize. Add to the skeleton that is there.
2. **Update in place; never fork a parallel doc.** Two documents describing the same thing means one
   of them is already wrong.
3. **Follow the code change.** New endpoint, new env var, new module → the corresponding rows change
   in the same commit.
4. **Re-verify what you touch.** If you edit a section, its links, paths and commands are yours now.

## See also

- `code-locale` — an identifier, route or config key quoted in the docs is copied from the code,
  never translated; docs prose keeps the project's language.
- `references/templates.md` — README / SETUP / TECHNICAL skeletons.
- `references/examples.md` — worked examples of good output per tier.
- `verify-before-claiming` — how to research a fact before documenting it, and the report to write
  when it cannot be found.
- `conventional-commit` — the commit format that drives generated changelogs.
- `openspec` — where design rationale lives when a project runs the spec-driven flow; documentation
  describes what exists, proposals describe what changes.
