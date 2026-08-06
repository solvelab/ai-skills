## 1. Resolve the scope contradiction

- [x] 1.1 Rewrite the frontmatter `description`: remove "ALWAYS creates all three documentation
      tiers", name the decision table as the governing condition, add the AGENTS.md trigger
- [x] 1.2 Rewrite the decision table: `README.md` unconditional, every other document earned; add the
      "do not create a document to satisfy the table" rule and the requirement to state when only a
      README was produced
- [x] 1.3 Delete the Troubleshooting entry that restates "This skill always creates all three tiers"

## 2. New doctrine

- [x] 2.1 Add "One purpose per page" — tutorial / how-to / reference / explanation mapped to the
      existing file names, with the fast-how / slow-why rot mechanism
- [x] 2.2 Add "Every claim must be checkable" — repo paths as links, trees rooted correctly and
      demoted, never hand-copy generated sources, env tables from the config module, commands run or
      declared unrun, ship the checker; include the measured 9-of-10 tree result
- [x] 2.3 Add "Keeping it true" — same-commit rule, named owner per document, dated volatile facts,
      delete aggressively
- [x] 2.4 Add "AGENTS.md" with the detectable trigger and the published SWE-bench ceiling; state that
      a missing trigger means naming the gap, not creating the file
- [x] 2.5 Add the "state what you could not verify" rule to the analysis section

## 3. Removals and size

- [x] 3.1 Move README / SETUP / TECHNICAL skeletons + formatting conventions + changelog format to
      `skills/documentation/references/templates.md`
- [x] 3.2 Delete the "How to Use" and "Trigger Test Cases" meta sections
- [x] 3.3 Collapse the badge/logo material into one signal-only rule
- [x] 3.4 SKILL.md ends materially shorter than 543 lines with template content in `references/`
- [x] 3.5 Bump `metadata.version` to 3.0.0

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform: name == directory, folded description, metadata.author solvelab,
      semver metadata.version, category `docs`, license MIT, compatibility present
- [x] Q.2 All skill content in English (catalog locale)
- [x] Q.3 Description triggers still route correctly (README, docs, SETUP, TECHNICAL, CHANGELOG,
      AGENTS.md, "document this") and the "Do NOT use for non-software documentation" boundary survives
- [x] Q.4 No duplicated doctrine: skeletons only in `references/templates.md`; changelog format links
      `conventional-commit`; per the design.md Canonical Home table
- [x] Q.5 Every quantified claim carries its measured number and conditions (skills-authoring:
      Simulated failure behaviour)
- [x] Q.6 Description states no policy the body contradicts (skills-authoring: Description agrees with
      body) — re-read both after the rewrite
- [x] Q.7 README skill-table row updated for `documentation`

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate harden-documentation-skill --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 CI frontmatter check passes locally on every `skills/*/SKILL.md`
- [x] V.5 AGENTS.md trigger re-tested: a run against a checkout containing a `CLAUDE.md` produces or
      updates `AGENTS.md` (the first draft's unobservable condition produced it in zero runs)
- [ ] V.6 `openspec archive harden-documentation-skill --yes` after review
