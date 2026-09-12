---
name: documentation
description: >-
  Creates and updates project documentation against a fixed map: one canonical name per reader
  need, one owning document per kind of fact, an English source with a mirror in the project's
  language, and requirements, decisions and dated reports each with a home of their own. Use
  whenever the user mentions README, docs, SETUP, ARCHITECTURE, REQUIREMENTS, ADR, CHANGELOG,
  AGENTS.md, "document this", "write the docs", "update the readme", "standardize the docs",
  "explain how this works", or asks to document a codebase for AI tools or new developers.
  Enforces read-the-code-first, machine-checkable claims, migrate-never-duplicate for legacy
  layouts, and docs that change in the same commit as the code. Do NOT use for non-software
  documentation tasks.
metadata:
  author: solvelab
  version: 4.0.0
  category: docs
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

# Documentation

> **Not version-bound**: this skill does not depend on a tool version — it decides which documents
> a project gets, what each is called, what lives inside it, and in which languages, and it
> prescribes no generator, linter or CLI. The `AGENTS.md` convention it names is a specification,
> not a versioned tool. Declared on 2026-09-05, re-declared for 4.0.0 on 2026-09-12.

Write documentation a reader can act on and a script can verify — and put it where the reader of
the *next* repository will look for it. Skeletons and worked examples live in `references/`; read
them when you are about to generate output, not before.

## Contents

- [Analyze before documenting](#analyze-before-documenting)
- [The document map](#the-document-map)
- [One fact, one document](#one-fact-one-document)
- [One purpose per page](#one-purpose-per-page)
- [Two languages, one source](#two-languages-one-source)
- [Organization is checkable too](#organization-is-checkable-too)
- [Every claim must be checkable](#every-claim-must-be-checkable)
- [Keeping it true](#keeping-it-true)
- [AGENTS.md — the repo's instructions for coding agents](#agentsmd--the-repos-instructions-for-coding-agents)
- [README](#readme)
- [Writing style](#writing-style)
- [Updating existing documentation](#updating-existing-documentation)
- [See also](#see-also)

## Analyze before documenting

Never write a line of documentation before reading the code it describes.

1. `find . -type f -not -path "*/.git/*" | head -60` — structure.
2. Read the entry point, the config module, the dependency manifest, and any existing docs.
3. Identify: language, framework, how it is configured, how it is run, what it integrates with.
4. **Extract the facts**, don't invent them: env vars from the config module, endpoints from the
   router, commands from the manifest scripts / Makefile / CI, and — from the deployment manifest
   (compose file, chart, Kubernetes manifest, systemd unit) — the ports, the compute and storage the
   project asks for, the uid/gid it runs as, and the filesystem modes it needs. Prerequisites are
   read from that file, never composed from memory: measured on a production repo, the setup guide
   listed four prerequisites while the manifest two directories away carried the CPU and memory
   requests and limits, the volume size, both node ports, the uid and the read-only root — none of
   which reached the guide.
5. Run the layout audit before writing anything: `references/check-doc-layout.py .` reports which
   slots exist, which legacy names are present and where each one migrates to.

Only document what you read. A fact that matters and could not be verified is written as an admitted
gap ("Deployment target: not documented in this repo"), never guessed — the ladder for finding it and
the report to write when it cannot be found are `verify-before-claiming`.

## The document map

One reader need, one slot. One slot, one canonical name — in English, identical in every repository,
so a reader who learned one project can navigate the next one. The condition decides whether the
slot is **filled**, never what it is called.

| Slot | Canonical | Condition | Absorbs these legacy names |
|---|---|---|---|
| Entry | `README.md` | always | — |
| Index | `## Documentation` in the README | always | `DOCS_INDEX.md` |
| Requirements | `docs/en/REQUIREMENTS.md` | always | — |
| Tutorial | `docs/en/SETUP.md` | setup over ~5 commands, or prerequisites | `COMO-SUBIR.md`, `INSTALL.md` |
| Explanation | `docs/en/ARCHITECTURE.md` | architecture a reader cannot infer from the tree | `docs/TECHNICAL.md`, root `ARCHITECTURE.md`, `docs/DESIGN.md` |
| Decisions | `docs/en/adr/NNNN-<slug>.md` | from the first non-obvious decision | `DESIGN-REVIEW.md`, `DECISIONS.md` |
| API reference | `docs/en/API.md`, or a link to the generated spec | an API with no published spec | `api-contract.md`, `ENDPOINTS.md` |
| Operation | `docs/en/OPERATIONS.md` | more than one environment, or a service someone operates | `DEPLOYMENT.md`, `INFRASTRUCTURE.md`, `RUNBOOK.md`, `DEPLOY.md` |
| Security | `docs/en/SECURITY.md` | auth, secrets, or security-sensitive config | — |
| Dated reports | `docs/reports/YYYY-MM-DD-<slug>.md` | any transient artifact | `*-HOMOLOGATION-*.md`, `DIAGNOSE-*.md`, `PROGRESS.md`, `TODO.md` |
| Agents | `AGENTS.md` | an agent-instruction file exists, or the user asks | — |
| History | `CHANGELOG.md` | releases are tagged | `docs/CHANGELOG.md` |
| Contribution | `CONTRIBUTING.md` | the project accepts outside contributions | — |

Every document under `docs/en/` has a mirror under `docs/pt-BR/` — or under whatever the project's
language is. That rule is [Two languages, one source](#two-languages-one-source). `docs/reports/`,
`AGENTS.md` and `CHANGELOG.md` stay single: a transient record has one known reader, the agent file
is read by tooling, and the changelog is generated.

**A page the map has no slot for is declared, not smuggled.** The map is closed for the concepts it
names, and a project may still owe a page none of them covers — an integration guide written for the
people who call this service is a different reader from the API reference. Such a page lives in the
language trees like any other, carries no fact another slot owns, and appears in the README index by
name. What it may not be is unlisted: that is how the open `docs/<topic>.md` slot produced a
different set of documents in every repository. Measured 2026-09-12: documenting a real service end
to end produced exactly one page outside the map, and the session declared it in the index and said
why.

**A slot the project does not earn is declared, not created.** It appears in the README index as
`not applicable: <reason>` and produces no file. This is the one rule that keeps a fixed map from
regrowing the decorative documents an earlier version of this skill was rebuilt to remove — the
absence is visible and dated, so a reader can tell a decision from an omission, and so can a script.

**Why a map instead of conditions.** Measured on 2026-09-12 across the 39 git repositories of one
maintainer's fleet, documented under the previous version of this skill: 19 `docs/TECHNICAL.md`
against 12 `ARCHITECTURE.md`, with 11 repositories carrying both at once; four different names for
the operation slot across 13 documents; 7 to 25 `##` sections under the same file name; zero
requirements documents; zero ADR directories; 24 transient reports loose beside permanent
documentation, 7 of them inside a repository and 17 in the workspace directories above them. Conditions decide whether a
document is earned and say nothing about what it is called, so two projects earning the same right
spell it differently — and eleven of them spelled it both ways.

**Why `OPERATIONS.md` and not the most common name.** `DEPLOYMENT.md` (6 occurrences) names half the
slot: how it goes out. The other half — what it needs to run, which ports, which outbound
destinations, what to do when it breaks — went to `INFRASTRUCTURE.md` (4) and `RUNBOOK.md` (2)
precisely because it did not fit under a name about deploying. A name that covers half the content is
how the other half grows a second file. Renaming six documents buys a name that stops the split.

## One fact, one document

A name per concept was never enough: nothing said where a fact **lives**, so an environment-variable
table was equally legitimate in three documents, and the three drifted apart in silence.

Each kind of fact has one owning document and one fixed shape there. Everywhere else: a link.

| Fact | Owner | Fixed shape |
|---|---|---|
| What it does and why, one sentence | `README.md` | prose, above everything |
| Quick start | `README.md` | one code block, 3-5 commands |
| Environment variables | `SETUP.md` | table `Variable · Type · Default · Required · Description` |
| Endpoints | `API.md` or the generated spec | table `Method · Path · Auth · Description` |
| Ports, CPU/memory, uid, egress | `OPERATIONS.md` | table `Resource · Value · Source` |
| Requirements, users, glossary | `REQUIREMENTS.md` | numbered `FR-n` / `NFR-n`, plus a glossary table |
| Components, flows, trade-offs | `ARCHITECTURE.md` | text diagram plus prose |
| Decisions | `adr/NNNN-<slug>.md` | MADR: Context · Decision · Consequences |
| Development commands | `README.md` | table `Command · What it does` |
| Troubleshooting | `SETUP.md` | table `Symptom · Cause · Fix` |
| Release history | `CHANGELOG.md` | generated, never hand-written |

The fixed shape is not decoration: it is what makes ownership **detectable**. The checker does not
understand that a table describes environment variables — it recognizes the canonical header row
outside its owning document. Two consequences, both accepted and written down rather than hidden: a
table with improvised columns escapes the check, and inside the owner that header row is the only
legitimate one.

**The single exception is the quick start.** The README may repeat up to 5 commands that also appear
in `SETUP.md`, because that repetition is what the reader wants on the first screen. Any other fact
appearing twice is a defect, not a convenience.

## One purpose per page

Four reader needs, four kinds of page. Mixing them is the most common reason docs go stale and the
most common reason readers can't find anything:

| Need | Page kind | In this map |
|---|---|---|
| "Get me running for the first time" | **Tutorial** — one happy path, no options | `SETUP.md` |
| "How do I do X?" | **How-to** — task-oriented, assumes context | README quick start, `OPERATIONS.md` |
| "What exactly does Y take?" | **Reference** — exhaustive, dry, generated where possible | `API.md`, `REQUIREMENTS.md` |
| "Why is it like this?" | **Explanation** — design rationale, trade-offs | `ARCHITECTURE.md`, `adr/` |

The practical rule: **how-to content changes far faster than why content.** A page that mixes a
command sequence with architectural rationale goes stale at the speed of its fastest-changing half.
Keep them on separate pages, and cross-link.

**Requirements are a slot, not a spec-workflow artifact.** `REQUIREMENTS.md` carries purpose, users,
numbered functional and non-functional requirements, and the glossary every other document draws its
terms from. Where the repository runs a spec-driven workflow, that document **indexes and links** the
capabilities instead of restating them — one table, one row per capability, pointing at each
specification. Copying them creates a second source of truth that drifts; having no cumulative
document at all leaves the reader with per-change deltas and no statement of what the system is for.
The workflow's own lifecycle is `openspec`.

## Two languages, one source

**Documentation is written in two languages by default**: English, and the language the project's
people actually speak. A single-language project is the exception, and the exception is declared in
the README index (`documented in English only`), never decided in silence — the same rule the map
applies to a slot nobody earned.

The pair is a fixed structure, not a habit:

- **English is the source.** Identifiers, routes, config keys and commands are already English
  (`code-locale`), so the English document is the one where nothing has to be translated back. On
  any conflict between the two, English wins.
- **The mirror is written in the same commit as the source.** A mirror added later is a second
  document about the same thing, which means one of them is already wrong.
- `README.md` (English) sits beside `README.pt-BR.md`; `docs/en/X.md` beside `docs/pt-BR/X.md`. Same
  file name, same section numbering, same count of `##`.
- **Code blocks are identical**, byte for byte. Comments inside a code block are part of the block:
  they stay in the source language in both copies, because the reader pastes the block.
- Both READMEs carry the same `## Documentation` index, each linking its own language's tree.

Parity is checked as **structure**: the twin exists, the section count and numbering match, the code
blocks match. Whether the translated prose still says what the source says is **review-only** — the
only mechanical signal available is "the twin changed in the same commit", which the rule above
already covers, and anything beyond it is a judgement about meaning across two languages. This
catalog has twice measured what a gate over meaning costs: 7 of 10 findings wrong for heading nesting
and 3 of 4 for justification prose, both of which is why those rules ship review-only.

The pair is never half-built: one mirror missing is a finding, not a stage. A source tree with no
mirror and no declaration is the same finding — the reader cannot tell "this project decided one
language is enough" from "somebody stopped halfway".

## Organization is checkable too

Two checkers ship beside this skill, and they answer different questions:

| Checker | Question | Rules |
|---|---|---|
| `references/check-doc-structure.py` | Is this **page** navigable? | R1-R7 |
| `references/check-doc-layout.py` | Is this **repository's layout** the map? | L1-L7 |

The full set of both — each rule with its published source, its worked example and the measurement
behind its verdict — is [`references/information-architecture.md`](references/information-architecture.md).

These four page rules hold without exception, so they belong in the body:

- **A document over 100 lines carries an index, and the index links every `##`.** Required by the
  Standard README spec, not recommended by it. This is also the precondition for the rule below —
  a page of per-option sections is only navigable because the index exists.
- **A table cell stops at 120 characters.** Above that the data is not tabular; it is a paragraph
  rendered as one unbroken line, with whatever the reader needed pushed to the far right.
- **Past 25 options, a table becomes an index plus one section per option.** A heading is an anchor:
  `docs/en/API.md#leader_term` can be pasted into an issue or an alert, and it appears in the
  GitHub Outline. A table row can do neither. Below that threshold the table is still the right form.
- **A `###` belongs to the `##` above it.** A heading is a tree, and the Outline reads it as one.

And these three layout rules:

- **Every slot is present or declared.** A missing document with no `not applicable` line in the
  README index is indistinguishable from forgotten work.
- **A legacy name is reported with its destination.** A finding that names the problem and not the
  fix is a finding nobody acts on.
- **A dated report lives in `docs/reports/`.** Transient records mixed into permanent documentation
  are why a reader stops trusting the directory.

Rules ship **review-only** when their measured noise would get the gate switched off in its first
week — that is a legitimate outcome, and the reason it is written down with its count.

## Every claim must be checkable

This is the difference between documentation and decoration. Prefer facts a script can verify against
the repo, and write them so it can:

- **Repo paths are links**, not prose: `[app/main.py](app/main.py)`. A link is checkable; a sentence
  is not.
- **A prerequisite states the value that passes**, not only the command that probes it. `kubectl
  version` printing a JSON blob proves the reader has *a* cluster, and an expected result of "a JSON
  block" is satisfied by every run — a step that cannot fail does not verify, it reassures, and that
  costs the reader attention while returning nothing. Name the minimum, the range, or the exact
  string. Where one command's results mean different failures with opposite fixes, map each result to
  its meaning in a table; a single "expected" line can only describe success.
- **What the software must reach is a prerequisite too.** Inbound ports get written down; outbound
  destinations almost never do — and for anything that notifies, integrates, pulls an image or calls
  an API, blocked egress fails *silently*: the process is healthy, the request never lands, and no
  error surfaces where anyone looks. List the hostnames and ports the software must reach out to, and
  say what the reader sees when it cannot. What the service should *do* while that dependency is
  down is a different subject, and it belongs to `backend-resilience`.
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

- **Docs change in the same commit as the code** — and the mirror changes in that same commit too. A
  PR that adds an env var and does not touch the config table is incomplete; treat it the way you
  would treat a missing test.
- **Every document names an owner** (a person or a team) in its footer or frontmatter. An unowned doc
  is nobody's job.
- **Date the volatile parts.** Version numbers, screenshots, benchmark figures and "current status"
  sections carry the date they were verified.
- **Delete aggressively.** A section describing a removed feature is worse than no section — it
  actively misleads. Prune when you touch a page.

## AGENTS.md — the repo's instructions for coding agents

When AI agents work in the repo, the conventions they need live in `AGENTS.md` at the root — an open
spec (donated to the Linux Foundation's Agentic AI Foundation in December 2025) that most agent tools
now read. The files that count as an agent-instruction file already present in a repo are
`CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md` and `.clinerules`; any one of them is
the signal that this document is owed. Anthropic's `CLAUDE.md` serves the same role for Claude Code;
when both exist, keep one canonical and have the other point at it rather than maintaining two.

Content that measurably helps: **architecture overview, where the important files are, and how to
build/test/run.** Be honest about the ceiling — the published evaluation of repository context files
on SWE-bench found gains modest and inconsistent across models, with setup and build guidance the most
valuable part. Write it for that: concrete commands and locations, not aspirational style rules. It
carries the three essential commands and links the map for everything else; it is not a third copy of
the README.

`AGENTS.md` is about *contributing to this code*. It is not a substitute for the README, and it is a
different thing from `llms.txt`, which maps a documentation *site* for retrieval.

**The trigger has to be something you can see.** "This repo is worked on by agents" is not observable
from a checkout — measured: with that phrasing, no run produced the file. Use the detectable signals
in the map above: an existing tool-specific instruction file, or the user asking for it. When none
is present, do not create `AGENTS.md` silently — say it is missing and what it would carry.

## README

Lead with what the software does and why, in one sentence, above everything else. Then only the
sections this project earns. The full skeleton and a worked example: `references/templates.md` and
`references/examples.md`.

- **A `## Documentation` section is mandatory**, and it lists every slot of the map: the earned ones
  as links, the rest as `not applicable: <reason>`. It is the one place a reader learns what this
  project decided not to write.
- **Quick start is 3-5 commands.** More than that means it is a tutorial — move it to `docs/en/SETUP.md`
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
3. **One term per concept**, taken from the glossary in `REQUIREMENTS.md` and used in every document.
4. **Document the why for non-obvious decisions** — the constraint that forced the choice, not the
   choice alone. A decision worth a paragraph is worth an ADR instead.
5. **Real values, never `foo`/`bar`.** Realistic payloads, actual config values.
6. **Warn about footguns** in bold, at the point of danger, not in a distant section.
7. **Prose follows the language of its tree; the machine layer never moves.** The English tree is
   written in English and its mirror in the project's language, while identifiers, routes, config
   keys and commands are copied from the code verbatim into both, never translated (`code-locale`).
   File and directory names are English in every tree.

## Updating existing documentation

1. **Audit the layout first.** `references/check-doc-layout.py .` names what is canonical, what is
   legacy and where each legacy document belongs. Do this before writing a line.
2. **Migrate, never duplicate.** A legacy name is moved to its canonical path with `git mv`, the
   inbound links are updated, and the mirror is created — all in the same commit. Creating the
   canonical document beside the legacy one produces two documents about the same thing, which is
   the state this map exists to end.
3. **Keep the existing structure of what is already canonical.** Add to the skeleton that is there;
   this rule stops at the canonical layout and is not a reason to preserve a legacy one.
4. **Follow the code change.** New endpoint, new env var, new module → the corresponding rows change
   in the same commit, in both languages.
5. **Re-verify what you touch.** If you edit a section, its links, paths and commands are yours now.
6. **Say what you moved.** A migration is reported to the user as a list of `old → new`, because the
   reader's bookmarks and the team's links are about to break, and a silent rename is indistinguishable
   from a deletion.

## See also

- `code-locale` — prose follows the repository's language and the machine layer stays English; the
  two-tree mirror above is the declared exception, and it is declared there too.
- [`references/information-architecture.md`](references/information-architecture.md) — the page rules
  and the layout rules, their sources, and the measured verdict on which a script can judge.
- [`references/templates.md`](references/templates.md) — skeletons for every canonical document.
- [`references/examples.md`](references/examples.md) — worked examples, including an English/mirror pair.
- `verify-before-claiming` — how to research a fact before documenting it, and the report to write
  when it cannot be found.
- `conventional-commit` — the commit format that drives generated changelogs.
- `openspec` — where design rationale lives when a project runs the spec-driven flow; documentation
  describes what exists, proposals describe what changes.
