## 1. Skill correction

- [x] 1.1 Fix frontmatter description in `skills/openspec-drivezone/SKILL.md`: replace "mandatory
      gates the `validate --strict` step refuses to skip" with a truthful enforcement statement
- [x] 1.2 Correct Part 1 ("For the AI"): state that the schema scaffolds the gates via `/opsx`
      generation and that the hard gate is the repo's rite-gate script + CI step
- [x] 1.3 Correct Part 2 ("For humans"): rewrite the "gates validate --strict refuses to skip"
      narrative; add a "Hard gate" subsection documenting the pattern (heading grep over active
      changes + `openspec validate --all --strict`, wired in CI) with `scripts/validate-rite.sh`
      (solvelab/ai-skills) linked as the canonical live example
- [x] 1.4 Bump `metadata.version` to 2.1.0
- [x] 1.5 Run `./generate.sh` and confirm wrappers regenerate (claude/, codex/, cursor/, copilot/,
      plugins/)

## 2. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on `skills/openspec-drivezone/SKILL.md`: name == directory, folded
      description, metadata.author solvelab, semver metadata.version, category in the controlled
      set, license MIT, compatibility present
- [x] Q.2 All touched skill content in English (catalog locale)
- [x] Q.3 Description triggers still route correctly (rite/forked schema/DriveZone) and the
      "Do NOT use for" boundary vs `openspec` remains
- [x] Q.4 No duplicated doctrine: hard-gate pattern lives only in `openspec-drivezone`; script not
      inlined verbatim; links per design.md Canonical Home table

## 3. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate update-openspec-drivezone-enforcement --strict` green
- [x] V.2 `scripts/validate-rite.sh` green (rite gate incl. this change's own gate groups)
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `openspec archive update-openspec-drivezone-enforcement --yes` after all groups above
