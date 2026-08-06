# Change: Fix what running the backlog → execute-backlog flow for real exposed

## Why

`backlog` and `execute-backlog` are about to be used as a rite — groom an item, then execute it. Of
the two, `backlog` had received exactly one improvement (a propagation-lag note found by using it) and
`execute-backlog` had received **no doctrine review at all**: only a cross-skill path correction and a
version pin. Neither had been exercised end-to-end.

So the flow was run against a real item — issue #28, groomed by `backlog` earlier the same day —
following `execute-backlog`'s own steps up to its plan-approval gate. Three defects surfaced, and one
suspicion turned out to be unfounded.

**1. The existing-PR check has no recipe, and the obvious one is wrong in both directions.**
Step 2 says *"Existing open PR for the item → report and ask before duplicating work."* No reference
gives a method, so the natural move is a text search. Measured on issue #28, which has **zero** linked
PRs:

```
gh pr list --search "28 in:body"  →  #31, #39, #5   (three, none related)
gh issue view 28 --json closedByPullRequestsReferences  →  0   (correct)
```

The search matches the bare number anywhere in any PR body — a version string, a line count, an
unrelated issue number. It also **misses** a real link whose reference lives only in a commit message.
Following the step literally halts a legitimate run on a false positive.

**2. The duplicate check fails on a verbatim title.** `backlog` step 4 searches for duplicates. Issue
#28 is titled `refactor(r3f): split the 10 r3f skills into SKILL.md + references/`. Searching its own
title's leading token returns nothing:

| search | found |
|---|---|
| `split r3f skills` | 1 |
| `r3f references split` | 1 |
| `r3f` | 1 |
| **`refactor(r3f)`** | **0** |

GitHub's search drops punctuation-bearing tokens, so a verbatim conventional-commit title reports
"no duplicate" for an issue that exists.

**3. The `columns:` config extension is undocumented where the config is defined.**
`execute-backlog/references/board-sync.md` reads `columns.ready`, `columns.in_progress` and
`columns.review` from the config. `backlog/references/backlog-config.md` — the canonical schema —
mentions `columns` **zero** times. Someone configuring from the `backlog` skill cannot know the key
exists.

**Unfounded suspicion, recorded:** the three board columns first looked undefined, since the config
file carries only `defaults.status`. `board-sync.md` in fact specifies all three, with name heuristics
as fallback and a warn-and-continue path when a name is not among the board's Status options. The
defect was only that the schema doc never mentioned them — a documentation gap, not a missing
mechanism.

## What Changes

- `execute-backlog` → 1.3.0:
  - Step 2 now resolves linked PRs from the issue's **link graph** and points at the recipe.
  - New *Finding the item's PRs* section in `references/board-sync.md` with both queries
    (`closedByPullRequestsReferences` for closing PRs, the timeline's `cross-referenced` events for
    the rest), and an explicit prohibition on `gh pr list --search "<n> in:body"` carrying the
    measured failure.
- `backlog` → 1.1.0:
  - `references/gh-projects.md`: the duplicate check now says to search key terms, never the
    candidate title verbatim, with the measured four-way comparison.
  - `references/backlog-config.md`: the optional `columns:` block documented, marked optional, with
    the fallback behaviour and a pointer to its canonical definition.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: MODIFIED **Checklists are scored against field defects** — a skill that
  prescribes a step SHALL also give the command that performs it when a plausible wrong command
  exists, and SHALL name the wrong one.

## Impact

- `skills/execute-backlog/SKILL.md` + `references/board-sync.md`;
  `skills/backlog/references/{gh-projects,backlog-config}.md`; regenerated wrappers.
- The flow is now safe to run as a rite: the existing-PR gate no longer halts on unrelated PRs, and a
  verbatim-title duplicate search no longer reports a clean board.
