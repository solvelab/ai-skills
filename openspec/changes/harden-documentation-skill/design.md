## Context

`documentation` is the catalog's only `docs`-category skill and one of its most frequently triggered:
its description fires on README, docs, SETUP, TECHNICAL, CHANGELOG and "explain how this works". It is
also the skill whose output is hardest to falsify — a wrong sentence in a README looks exactly like a
right one until someone follows it.

That is why this change was driven by measurement rather than review. Two instruments were built: a
claim checker that extracts every machine-checkable assertion a markdown doc makes about its repo
(links, tree paths, inline paths, env vars in tables) and verifies it, and an A/B trial that ran the
current doctrine and a revised draft over the same real, undocumented codebase and scored the output
against the source.

## Goals / Non-Goals

**Goals**
- One policy, stated once, for which documents exist.
- Rules that produce assertions a script can check, and a way to keep them true over time.
- Cover the reader-need distinction and the agent context-file convention the skill currently omits.

**Non-Goals**
- Not adopting Diátaxis wholesale as a file layout. The four needs are used as a *test* for whether a
  page has one purpose; the repo's README/SETUP/TECHNICAL naming stays.
- No documentation generator, linter, or CI job shipped in this repo. The skill prescribes shipping a
  checker in the documented project; building one here is a separate proposal.
- The `r3f-*` size problem is named in the proposal and left alone.

## Decisions

**D1 — The decision table is the single authority on which files exist.** The
"ALWAYS three tiers" promise loses, because it is the side that contradicts the body twice and because
it measurably over-produces: 5 documents for a 1,432-line service, including one the trial's own
control arm had to justify at length. Owner decision, 2026-08-06.

**D2 — Reader need is a test, not a taxonomy to file under.** Pages keep their existing names; the
tutorial/how-to/reference/explanation split is applied as "does this page have one purpose?". The
operative rule is the rot mechanism — how-to content changes faster than why content, so a page
mixing them decays at the speed of its fastest half.

**D3 — Checkability is the skill's central rule, not a nicety.** The A/B difference was not accuracy
(both arms got 16/16 env vars and 6/6 endpoints) — it was that the revised arm wrote 131 checkable
claims where the control wrote 84, and failed fewer of them. Writing a path as a link instead of prose
converts an unfalsifiable sentence into a testable one at zero cost.

**D4 — Directory trees are demoted, not banned.** They are the highest-rot artifact measured (9 of 10
entries wrong in a production README, from an omitted root plus one genuine rename). They stay
available for genuinely non-obvious layouts, with two hard requirements: show the real root, and cap
at directories that carry meaning.

**D5 — `AGENTS.md` needs a detectable trigger.** The first draft conditioned it on "repo is worked on
by AI coding agents" and **no trial run produced the file** — the condition is not observable from a
checkout. It now keys on an existing tool-specific instruction file or an explicit request, and the
skill is required to *name the gap* rather than create the file silently when neither is present. This
is a negative result from the simulation, folded back in.

**D6 — Claims about `AGENTS.md` value are stated with their ceiling.** The published SWE-bench
evaluation of repository context files reports modest and inconsistent gains, with build/setup
guidance the most useful content. The skill says that, rather than selling the file.

**D7 — Templates leave SKILL.md.** 42% of the file was fenced skeleton. Skeletons are read at
generation time, not at selection time, which is exactly what `references/` is for.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Which documents a project needs; README/SETUP/TECHNICAL structure | `documentation` | already canonical — decision table becomes the sole authority |
| One purpose per page (tutorial/how-to/reference/explanation) | `documentation` | establish here (new) |
| Checkable documentation claims + doc staleness controls | `documentation` | establish here (new) |
| `AGENTS.md` / agent context files | `documentation` | establish here (new) |
| Document skeletons and formatting conventions | `documentation/references/templates.md` | move out of SKILL.md |
| Changelog format and commit types that generate it | `conventional-commit` | link (already canonical) |
| Design rationale for a *change* (vs documentation of what exists) | `openspec` | link (already canonical) |
| Frontmatter/authoring conventions for skills themselves | `openspec/specs/skills-authoring` | spec delta, not skill content |

## Risks / Trade-offs

- [Fewer documents by default may read as a regression to anyone relying on the three-tier promise] →
  the skill must state explicitly when it produced only a README and why; the decision table makes the
  reasoning inspectable rather than implicit.
- [Major version bump invalidates cached copies] → intended; the output set changes.
- [`AGENTS.md` guidance ages fast — the spec is young] → the rule is written against detectable files
  rather than a spec version, and the value claim carries its published ceiling.
- [Moving skeletons to `references/` costs a second file read at generation time] → acceptable: they
  are not needed to decide whether the skill applies, only to produce output.
- [The claim checker used for the measurements lives outside this repo] → the numbers it produced are
  recorded in the proposal with their conditions; the skill prescribes shipping such a checker in the
  documented project, which is where it belongs.
