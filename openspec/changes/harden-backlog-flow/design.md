## Context

`backlog` and `execute-backlog` are the catalog's only pair meant to be run in sequence as a rite:
groom an item, then execute it. They are also the pair with the most external surface — a GitHub
Project board, the issue graph, the PR graph — and therefore the most places where a plausible command
is subtly the wrong one.

Neither had been exercised. The audit that covered them earlier only probed that their commands
*exist* (28 subcommand/flag claims against `gh 2.92.0`, all clean). Existing is not the same as
correct-for-the-purpose, which is what running the flow measures.

## Goals / Non-Goals

**Goals**
- Run the flow against a real item and fix what the run exposes.
- Give every step that can be done wrongly the command that does it rightly.
- Record the suspicion that turned out unfounded, so it is not re-raised.

**Non-Goals**
- Not executing issue #28's actual work. The run stopped at `execute-backlog`'s own plan-approval
  gate, which is where the skill says to stop — exercising the skill, not bypassing it.
- Not redesigning the board-sync model. It was checked and found complete; only its documentation
  location was wrong.
- Not adding workspace-mode coverage. Testing multi-repo mode needs a workspace, which this
  environment does not have; it stays unexercised and is not claimed otherwise.

## Decisions

**D1 — A step without a command is a defect, not a style choice.** *"Existing open PR for the item →
report and ask"* reads complete, and produced a wrong result the first time it was run, because the
obvious implementation is a text search. The generalised rule goes into `skills-authoring`: when a
plausible wrong command exists, name it.

**D2 — Name the forbidden command, not just the correct one.** `gh pr list --search "<n> in:body"`
will keep looking reasonable to the next reader. Recording that it returned three unrelated PRs for an
issue with zero linked PRs is what stops it being re-derived.

**D3 — Both failure directions are worth stating.** The text search over-matches (bare number anywhere
in a body) *and* under-matches (a link that lives only in a commit message). A reader who only knows
about false positives will still trust a zero result.

**D4 — The duplicate-check trap belongs next to the command.** GitHub dropping punctuation-bearing
tokens is invisible until it costs a duplicate issue. The measured four-way comparison sits directly
above the query so it cannot be read without it.

**D5 — Config keys are documented where the config is defined.** `columns:` is read by
`execute-backlog` and specified in its `board-sync.md`; the schema doc in `backlog` is where someone
writing `.github/backlog.yml` actually looks. It is cross-referenced rather than duplicated, so
`board-sync.md` stays canonical.

**D6 — Record the unfounded suspicion.** The three board columns looked undefined because the config
file carries only `defaults.status`. They are fully specified in `board-sync.md`, with heuristics and
a warn-and-continue path. Writing that down costs a paragraph and prevents the next reader from
"fixing" a mechanism that already works.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Grooming an idea into a Project item; duplicate check | `backlog` | already canonical — search trap documented |
| Config schema for `.github/backlog.yml` / workspace `backlog.yml` | `backlog/references/backlog-config.md` | already canonical — `columns:` cross-referenced |
| Board transitions and column resolution | `execute-backlog/references/board-sync.md` | already canonical — gains the PR-link recipe |
| Executing an item to a reviewable PR | `execute-backlog` | already canonical — step 2 given its method |
| Acceptance criteria verdicts and evidence | `execute-backlog/references/acceptance-tracking.md` | unchanged — reviewed and found sound |
| Commit/PR message format for the work these skills produce | `conventional-commit` | link (already canonical) |

## Risks / Trade-offs

- [The `closedByPullRequestsReferences` field is a GitHub API surface that can change] → it is pinned
  to `gh 2.92.0` alongside the rest of the skill's recipes, and the timeline query is given as the
  second source.
- [Naming a forbidden command dates the doc if `gh` later fixes the search] → the failure is inherent
  to matching a bare number in free text, not a `gh` bug.
- [Workspace mode stays unexercised] → stated in Non-Goals rather than implied by the rest passing.
