# Change: Rebuild the documentation skill around checkable claims and reader need

## Why

`skills/documentation/SKILL.md` instructs two opposite behaviours in the same file. The frontmatter
description — the part always in context, and what the model reads when selecting the skill — says
"**ALWAYS creates all three documentation tiers** unless the user explicitly says otherwise". The body
says "**Do NOT create documents that don't apply to this project**", and the Troubleshooting section
restates the first claim ("This skill always creates all three tiers"). Three statements, two
incompatible policies.

Measured consequences, from an A/B trial on a real undocumented 1,432-line Python service (same task,
same reference files, output scored against the source code):

| | current skill | revised draft |
|---|---|---|
| documents created | 5 | 4 |
| documentation lines | 873 | 786 |
| env vars documented / in code | 16/16 | 16/16 |
| endpoints documented / in code | 6/6 | 6/6 |
| **machine-checkable claims** | **84** | **131** |
| claims that fail verification | 13 | 11 |
| **failure rate** | **15.5%** | **8.4%** |
| states what it could not verify | no | yes |

The revised text produces 56% more verifiable assertions at roughly half the failure rate, with fewer
files. Both arms read the code correctly — the current skill is sound on accuracy; it is wrong on
*scope* and silent on *durability*.

Documentation rot was measured directly with a claim checker over production repos. A README
directory tree written without its `src/` prefix made every path in the block unresolvable, and one
entry named a file renamed months earlier — 9 of 10 tree entries wrong, in the artifact the skill
mandates most insistently ("Folder structure with annotations", "Always include inline comments").

Gaps the current text has no rule for at all:

- **Staleness.** "Living documentation" is listed as a principle with no mechanism — no
  same-commit rule, no ownership, no verification. Rot is the default outcome of every doc set.
- **`AGENTS.md`.** The skill triggers on "document this for AI tools" and claims to be "vibe coding
  friendly", but never mentions the repository context-file convention that agent tooling actually
  reads (open spec, donated to the Linux Foundation's Agentic AI Foundation in December 2025).
- **Reader need.** The three tiers conflate tutorial, how-to, reference and explanation. Mixing
  fast-changing how-to content with slow-changing rationale on one page is the mechanism by which
  pages go stale.

The file is also 543 lines / ~4.9k tokens — at the ceiling for a SKILL.md — of which 42% is fenced
template content that belongs in `references/`, plus meta sections ("How to Use", "Trigger Test
Cases") that cost context on every invocation and instruct nothing.

## What Changes

- `documentation` → 3.0.0 (major: changes which files the skill produces).
  - Remove the "ALWAYS all three tiers" promise from the description and Troubleshooting. `README.md`
    is the only unconditional document; the decision table governs the rest, and the skill must say
    when it deliberately produced only a README.
  - Add **one purpose per page** (tutorial / how-to / reference / explanation) as the organizing
    principle behind the tiers, with the fast-how / slow-why rot mechanism stated.
  - Add **every claim must be checkable**: repo paths as links, directory trees rooted correctly and
    demoted to "only when the layout is non-obvious", never hand-copy generated sources, env tables
    sourced from the config module, commands actually run, and ship the checker.
  - Add **keeping it true**: docs change in the same commit as the code, every document names an
    owner, volatile facts carry a verification date, delete aggressively.
  - Add **`AGENTS.md`** with a *detectable* trigger (an existing `CLAUDE.md` / `.cursorrules` /
    `.github/copilot-instructions.md` / `.clinerules`, or the user asking), and the honest ceiling from
    the published SWE-bench evaluation of repository context files — gains modest and inconsistent,
    with build/setup guidance the most valuable part.
  - Replace the badge/logo material (14 mentions of "badge", 5 of `logo.png`) with a single
    signal-only rule: a badge that cannot fail carries no information.
  - Move the README / SETUP / TECHNICAL skeletons and formatting conventions to
    `references/templates.md`; drop the "How to Use" and "Trigger Test Cases" meta sections.
- New file `skills/documentation/references/templates.md`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — a skill's frontmatter description SHALL NOT state a policy
  its body contradicts, since the description is what drives selection and is always in context.

## Impact

- `skills/documentation/SKILL.md` (rewritten), `skills/documentation/references/templates.md` (new),
  and every regenerated wrapper tree (`claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`).
- README skill-table row for `documentation`.
- Consumers: projects documented with this skill will get fewer files by default and an `AGENTS.md`
  where a tool-specific instruction file already exists.
- Out of scope, noted for a follow-up: the `r3f-*` skills run 732-1,145 lines with 78-86% fenced
  content and no `references/` at all — the same size problem, larger.
