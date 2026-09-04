---
name: verify-before-claiming
description: >-
  Anti-guessing rite: research before asserting, label every claim with its source, and report
  what could not be found instead of producing a plausible substitute. Use when about to state or
  use an API, CLI flag, config key, env var, path, version or behavior not read in this session;
  when a fact depends on a library version; when the answer cannot be found and the gap has to be
  reported; or when the user says "you invented that", "don't guess", "achismo", "não inventa",
  "chutou", "pesquisa antes", "de onde tirou", "where did you see that", "cite the source", "that
  flag does not exist", "out of scope", "não foi isso que eu pedi". Covers the research ladder,
  claim labelling, the not-found report and the scope-restatement guard. Do NOT use for
  adversarially testing code already written (that is bug-hunter), for designing an API test suite
  (that is api-resilience-testing), for writing documentation pages (that is documentation), or
  for the plan-approval gate of a backlog item (that is execute-backlog).
metadata:
  author: solvelab
  version: 1.1.0
  category: process
license: MIT
compatibility: >-
  Works in any environment with filesystem access. Ladder rungs 4-5 need a web-fetch and a web-search
  tool (WebFetch/WebSearch in Claude Code); without them the ladder ends at rung 3 and the run reports
  the gap instead of guessing.
---

# Verify before claiming

A **claim** is anything you assert **or act on** as if it were true. A sentence in an answer is a
claim. So is `client.get(url, timeout=5)` — it claims that parameter exists. So is building a second
endpoint nobody asked for — it claims the user wanted it.

Every claim is one of three things: **verified** against a source you opened in this session,
**inferred** and labelled as such, or **unknown** and reported. There is no fourth option. A
plausible sentence with no source is the defect this skill exists to prevent. The research
ladder is cheapest-first: session context, this repo, the installed dependency, the tool itself,
version-pinned docs, web search, the user.

- **Per-ecosystem commands for each rung, offline degradation**: `references/research-ladder.md`
- **Claim labels, the not-found report, scope blocks**: `references/report-templates.md`
- **Anti-pattern catalog with the defect that earned each row**: `references/failure-catalog.md`

## CRITICAL: Ground rules

1. **No invention** — never state or use an API, flag, config key, path, version, field name or
   behavior you have not read in a source **this session**. `backlog` states this for GitHub
   metadata; this is the general form.
2. **Research before answering, not after being corrected** — the ladder runs before the first line
   of the answer and before the first edit. "The user will tell me if I am wrong" is not a
   verification strategy.
3. **Not found is a deliverable** — when the ladder ends without the fact, produce the not-found
   report. Never substitute a plausible answer, never let a guess wear the grammar of a fact.
4. **Your memory is a hypothesis** — what you remember about a library is dated at your training
   cutoff. The lockfile decides the version; the installed source decides the API. When they
   disagree with your memory, you are the stale one.
5. **Scope is the user's, not yours** — restate what you are about to do before doing it, and treat
   everything you added on your own as an unverified claim about intent.
6. **Every load-bearing claim carries its source** — `file:line`, the command and the output line,
   or the URL plus the version it documents. Not the adverb "probably".
7. **Cite only what you opened** — a URL you did not fetch and a line number you reconstructed from
   memory are fabrications, and a fabricated citation is worse than none because it makes a wrong
   answer authoritative. If you cannot quote a line from it, you did not read it.
8. **Probes are read-only** — `--help`, `--version`, `--dry-run`, a throwaway script in a scratch
   directory. A probe that changes state is not a probe; it is an unapproved edit.

## The research ladder

Ordered by cost, cheapest first. Commands per ecosystem: `references/research-ladder.md`.

| Rung | Source | Authoritative for |
|---|---|---|
| 0 | This session's context — files already read, tool output already returned | anything already established; cite it, do not re-read it |
| 1 | This repo — the symbol, the call site, the test, the schema, the history | everything the project owns: paths, config keys, conventions, why it is like this |
| 2 | The installed dependency — the lockfile for the version, then that version's source | the API this project actually calls; it is the code that will run |
| 3 | The tool itself — `--help`, `--version`, a `--dry-run` probe, a one-line REPL | what the installed binary does, as opposed to what its docs say it does |
| 4 | Official docs, fetched at the version from rung 2 | intent, semantics, and guarantees absent from the source (limits, ordering, retries) |
| 5 | Web search | current state only: deprecations, known bugs, what changed after your cutoff |
| 6 | The user | intent, business rules, priorities, credentials, anything in a system you cannot read |

Rules bolted to the ladder — without these it is ceremony:

- **Stop at the first rung that answers.** Climbing for confirmation you already have is cost
  without information.
- **Never skip downward.** Searching the web for something the repo answers is slower *and* wrong
  more often, because the web does not know *this* project.
- **Rungs 4-5 depend on rung 2.** Fetch documentation for the pinned version, never for `latest`.
  Latest docs read against a pinned older dependency is the highest-yield way to produce a
  confident wrong answer.
- **A search result is a lead, not a fact.** It becomes a fact when you fetch the primary source it
  points at — the upstream repository, the release notes, the vendor's own page.
- **Rung 6 is not a shortcut past 1-3.** Everything derivable from the repo is derived, not asked.
- **No network is not permission to guess.** Rungs 0-3 always exist. If the fact needs 4-5 and the
  tools are absent, name the unavailable rungs and go to rung 6.

## When the ladder does not run

This section is what keeps the doctrine affordable. Without it, every one-line edit costs a research
session and the rule gets abandoned wholesale.

| Situation | Ladder |
|---|---|
| Already established in this session's context | none — cite it |
| A language or stdlib construct you would write identically from memory **and** the compiler, type checker or an existing test rejects it in seconds | none |
| Anything this repo owns — a path, a symbol, a config key, a script name, a schema field | rung 1, always, never from memory |
| Third-party API surface: name, signature, flag, config key, error type | rungs 2-3 minimum; rung 4 when the source is unreadable (minified, native, closed) |
| "Is this still true, was it deprecated, did it change" | 2, then 4, then 5 |
| Intent, priority, business rule, which of two plausible scopes | rung 6 immediately — no other rung can answer it |

Research is bounded by **the cost of being wrong × the cost of checking**. A misspelled identifier
the test suite rejects in three seconds does not earn a documentation fetch. A misspelled config key
that is silently ignored earns the whole ladder, because that failure has no symptom. The cheapest
check that would catch the error wins: if running the test proves the signature, run the test
instead of reading the docs.

**Do not perform research; do research.** A web search whose results you do not read, or a `--help`
you run and do not quote, is cost without evidence — and it is worse than skipping it, because it
buys the appearance of rigor.

## Labelling claims

Templates and worked examples: `references/report-templates.md`.

- **Verified** — the source travels inline, at the point of the claim, not in a footnote.
- **Inferred** — a conclusion drawn from verified facts, marked as one, naming what it came from.
- **Unknown** — goes to the not-found report; it never appears as a hedged sentence.

Two rules carry the weight:

**Confidence adverbs are not labels.** "Probably", "should", "typically", "in most versions" read as
hedged facts and are remembered as facts. Use the label.

**In code, the label is a comment where the decision is, not a note in the chat.** Chat scrolls away;
the code ships. Write the marker at the line that depends on the unverified fact, naming what was
checked and what would confirm it.

Threshold: label **load-bearing** claims — anything the user will act on or that code will depend
on. Labelling ordinary prose makes answers unreadable and trains the reader to skip citations, which
is this rule defeating itself.

## The not-found protocol

Full template: `references/report-templates.md`.

When the ladder ends without the fact, the report is the deliverable. It states the question, then
logs **commands** per rung — "I looked around" is not a search log — then the rungs that were not
searched and why, then what remains unknown, then options.

- **The absolute ban:** never close the gap by producing the most plausible-looking answer, and
  never invent a name because it "would make sense". If you catch yourself typing a symbol you did
  not read, stop mid-sentence and switch to this report.
- Include at least one option that moves the work forward without the missing fact, when one exists.
  A not-found that only says "I do not know" is half a deliverable.
- A confident wrong sentence costs more than an admitted gap.

## Your memory is dated

Every API you remember was true for *some* version at *some* date. You do not know which version
this project uses until you read the lockfile.

Highest-risk shapes, in order: a parameter added or removed between minors; a renamed export; a
changed default; a config key that moved; an ecosystem-wide rename.

**Post-cutoff releases you do not know at all — including whether they exist.** A package you
"remember" that has no entry in the lockfile and no page upstream may be a hallucination. "I
remember this library" is rung-0 evidence, which is none.

The build-time form of this rule already has a home: `assettoserver-plugin` — compile against the
upstream source checkout at the exact tag matching the runtime, because a fallback default is used
exactly when detection failed, which is when you can least afford a guess.

## Off-script guard

Delivering work nobody asked for is the same defect: an unverified claim about intent.

- **Before acting, restate.** One block, three parts — Doing / Not doing / Assumptions. Anything
  under *Assumptions* that changes the shape of the work needs a yes before you start.
- **A request has an explicit half and a half you filled in.** Only the first was agreed. The extra
  endpoint, the rename, the refactor, the new dependency, the "while I was there" fix — each is a
  claim about what the user wanted, and gets the same treatment as an unverified API.
- **Drive-by fixes are off-script even when they are correct.** Unrelated defects found during the
  work are reported, not fixed, unless the user says otherwise.
- **Deliverable shape is part of the scope.** Asked for an analysis, do not deliver code. Asked
  about one file, do not touch five. Delivering more than was asked buries the answer.
- **When implementation proves the scope wrong**, stop at a safe point — never a half-applied
  refactor — and report what was agreed, what was found, why the agreed path fails, and the options.
  Never silently re-scope. Recording an approved deviation on the issue and the board belongs to
  `execute-backlog`; this rule governs only the stopping and the reporting.

## Anti-patterns

Full table with provenance: `references/failure-catalog.md`. Every row there names the defect that
earned it — a row that cannot name one is removed rather than kept.

| Anti-pattern | What it looks like |
|---|---|
| **Assumed enforcement** | trusting that a tool checks what its name implies, without probing it |
| **Negative claim from an unread source** | "that API does not exist", asserted without opening the SDK |
| **Layout written from memory** | a directory tree in a README that no `ls` produced |
| **Assumed framework default** | a limit or status code stated without measuring the stock behavior |
| **Guessed default masking a detection failure** | a fallback constant used exactly when detection failed |
| **Hand-copied fact that drifted** | a count in the docs that no longer matches the tree it describes |

When a guess ships and someone catches it, add the row **and** the incident that earned it.

## See also

- `bug-hunter` — the adversarial rite that runs *after* a change; this skill runs before it, because
  a test written against a guessed contract passes for the wrong reason.
- `documentation` — the same read-first discipline applied to what goes on a page.
- `execute-backlog` — the backlog-rite bookkeeping for an approved scope deviation.
- `backlog` — the GitHub-metadata instance of *No invention*.
- `openspec` — where a claim about *what will be built* is recorded and gated.

> **Verified against**: ripgrep 14.1.1, git 2.47.3, Python 3.14.5, gh 2.92.0, openspec 1.6.0,
> Node.js v26.0.0 — every command this skill and its references prescribe was probed on 2026-08-06.
> Rung 4-5 tool names (WebFetch, WebSearch) are Claude Code's; on another harness, substitute the
> equivalent and keep the ordering.
