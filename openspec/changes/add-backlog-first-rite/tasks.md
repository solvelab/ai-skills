## 1. Global rules

- [x] 1.1 Add the **Development Rite (backlog-first)** section to `claude/global/personal-rules.md`:
      entry point, second step, diagnosis stays free, plan mode is not a bypass, OpenSpec as
      complement, and the out-of-scope list (personal config, scratchpad, one-off ops commands)

## 2. Enforcement artifact

- [x] 2.1 Add `claude/global/hooks/backlog-rite.py` — `UserPromptSubmit` hook reading the JSON
      payload on stdin, printing the rite reminder when the prompt matches code-change signals
- [x] 2.2 Silence list: slash commands already inside the rite (`/backlog`, `/execute-backlog`) and
      explicit waivers produce no output
- [x] 2.3 Verify by running the hook against three payloads: a code-change prompt (prints), a rite
      command (silent), a trivial question (silent)

## 3. Documentation

- [x] 3.1 README *Global Personal Rules*: document the hook, its `settings.json` wiring, and that it
      informs rather than blocks
- [x] 3.2 State that the hook, like `personal-rules.md`, is the maintainer's config and meant to be
      edited rather than adopted blindly

## 4. Skill framing

- [x] 4.1 `skills/backlog/SKILL.md`: description names `execute-backlog` as the next step
- [x] 4.2 `skills/execute-backlog/SKILL.md`: description names `backlog` as the step that produces
      the item (it already excludes creation; make the pairing explicit)
- [x] 4.3 Mirror both into `claude/skills/` via the repo's generator, no hand-editing of mirrors

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [x] Q.2 All touched skill content in English (catalog locale)
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-backlog-first-rite --strict` green
- [x] V.2 Catalog discovery intact: skill count unchanged, no orphan/renamed leftovers, mirrors in
      sync with sources
- [x] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive add-backlog-first-rite --yes` after all groups above are `[x]`
      — pending: this repo archives in a separate PR after the implementation PR merges
      (see `docs(openspec): archive … and sync the spec delta` commits)
