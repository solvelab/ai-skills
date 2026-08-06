# Change: Remove the meta sections the catalog kept after ruling against them

## Why

#24 removed `How to Use` and `Trigger Test Cases` from `documentation`, arguing they are read only
*after* the skill has already been selected — so they cannot influence routing, and they cost context
on every invocation. The argument was accepted and the sections were deleted.

**It was applied to exactly one skill.** Four others kept theirs:

| skill | meta lines | % of file | sections |
|---|---|---|---|
| `helm-migration` | 38 | 11% | How to Use, Trigger Test Cases |
| `backlog` | 16 | 14% | Trigger Test Cases |
| `execute-backlog` | 16 | 15% | Trigger Test Cases |
| `claude-statusline` | 15 | 8% | Trigger Test Cases |

**85 lines loaded on every invocation that instruct nothing about the task.**

Before deleting, each block was checked against its own description rather than assumed redundant:

- `backlog`, `execute-backlog`, `claude-statusline` — every case already covered. `claude-statusline`'s
  "tmux status bar" is its description's "non-Claude-Code status bars"; `execute-backlog`'s
  "Merge PR #12" is its "Do NOT use … for merging PRs".
- `helm-migration` — **four cases were not covered**, all anti-triggers (README, a Python bug, a
  docker-compose file, project documentation), because its description carries **no routing guidance at
  all**: no `Do NOT use` clause and no redirect to a sibling skill. Those four are the reason it needed
  one.

`helm-migration`'s `How to Use` was separately redundant: 24 lines telling the user which prompt to
type — read after they typed — listing three inputs its own workflow step 1 already asks for.

## What Changes

- `helm-migration` → 2.2.0: description gains a `Do NOT use for …` clause built from the four real
  anti-triggers; `How to Use` and `Trigger Test Cases` removed (−38 lines).
- `backlog` → 1.1.1, `execute-backlog` → 1.3.1, `claude-statusline` → 1.1.1: `Trigger Test Cases`
  removed (−47 lines), descriptions already carrying every case.
- New validator check **C8 — no meta sections in SKILL.md**, with the reasoning in the check itself.
  Self-test extended to **12/12** defect classes.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — triggers live in the description, not the body; a case the
  description does not cover is folded in rather than filed away, and every skill states where it does
  not apply.

## Impact

- `skills/{helm-migration,backlog,execute-backlog,claude-statusline}/SKILL.md`;
  `scripts/validate-skills.py` (+C8); `scripts/selftest-validate-skills.py` (12 classes); regenerated
  wrappers.
- 85 fewer lines of per-invocation context across four skills, and `helm-migration` gains routing
  guidance it never had.
