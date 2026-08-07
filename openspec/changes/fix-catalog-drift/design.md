## Context

Two of these five defects were found only because the search was widened after a first, narrower
search had already reported "found everything". The first sweep used a pattern requiring the word
`skills` after the number; `README.md:55` says "all 30." with no noun, and was missed. That near-miss
is the reason this change records its own derivation commands rather than only its conclusions.

## Goals / Non-Goals

**Goals:**

- Every published number agrees with the artifact it describes, at the moment of the PR.
- The next editor can re-derive each number instead of copying it, because the command that produces
  it is written next to it.

**Non-Goals:**

- Automating the counts. A generator or a CI assertion is a real option and a real cost; proposing
  one here would be the unrequested scope this repository's own doctrine forbids. It is recorded as
  a follow-up.
- Touching any skill, script or generated tree. Nothing here changes behaviour.

## Decisions

**The counts are re-derived at PR time, not copied from the issue that reported them.** The issue
was written when the catalog held 32 skills; it holds 33 now, because a sibling change added one.
Copying 32 out of the report would have reproduced the exact defect being fixed, one generation
later.

**The validator description names its checks instead of counting them.** "Runs six checks" drifted
because a bare number carries no signal when it goes stale. The corrected sentence lists what each
check does, so an added check makes the omission visible in review rather than silently wrong.

**The category set is fixed in the spec, not in CI.** CI enforces 11 categories and the catalog
already uses all of them — `nui`, `frontend` and `tooling` are live in shipped skills. The gate is
right and the document is behind, so the document moves.

**No automatic count synchronisation is built.** It would be the correct long-term fix and it is
explicitly out of scope: a half-built generator is worse than an accurate sentence, and the decision
belongs to the maintainer rather than to this change.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| "Never hand-copy what a tool generates; link or generate it" | `documentation` | already canonical — this change is an instance of that rule being enforced on the repo's own docs, and restates nothing |
| Re-derive rather than recall; a hand-copied fact that drifted | `verify-before-claiming` | already canonical — the drift fixed here is the provenance of that skill's *Hand-copied fact that drifted* row; no doctrine is duplicated |
| Controlled `metadata.category` set | `openspec/specs/skills-authoring` (spec, not skill) | already canonical — corrected in place so it matches `.github/workflows/ci.yml` |

No skill file is modified by this change, so no cross-cutting rule moves home.

## Risks / Trade-offs

- **The counts drift again on the next skill added** → accepted and mitigated only partially: each
  corrected sentence names the command that produces its number, so a reviewer can check it in
  seconds. A structural fix (generate the count) is recorded as a follow-up rather than half-built.
- **A count could be wrong at merge time if a sibling change lands first** → the PR records the
  command and the value it produced, so a reviewer re-running it sees any divergence immediately.

## Migration Plan

Pure documentation correction. No script, skill or generated tree changes; `./generate.sh` output is
unaffected. Rollback is a `git revert`.

## Open Questions

- Should the skill count be generated rather than written? Out of scope here by decision, recorded as
  a follow-up so it is not silently forgotten.
