## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Read on 2026-09-06 in `solvelab/ai-skills` at commit `0959ccc`:
      - `skills/documentation/SKILL.md` — 203 lines, `metadata.version: 3.1.1`, two references
      - `skills/documentation/references/` — `examples.md`, `templates.md`; no third file
      - `skills/code-locale/references/check-identifier-locale.py` — the shipped-detector precedent
      - `openspec/specs/skills-authoring/spec.md` — 794 lines, 18 requirements
      - `openspec/schemas/skills-rite/{schema.yaml,templates/tasks.md,templates/design.md}`

      Read on 2026-09-06 in `solvelab/ferdinand` at commit `66346d4`:
      - `README.md` — 1006 lines
      - `docs/REFERENCE.md` — 318 lines
      - `test/unit/reference.test.ts` — the completeness guard shipped by ferdinand#439

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      - `openspec --version` -> `1.6.0`
      - `openspec new change add-information-architecture-rules --schema skills-rite` ->
        `Created change 'add-information-architecture-rules' at openspec/changes/…` / `Schema: skills-rite`
      - `openspec validate add-information-architecture-rules --strict` ->
        `Change 'add-information-architecture-rules' is valid`
      - `grep -m1 '^schema:' openspec/config.yaml` -> `schema: skills-rite`
      - `wc -l skills/code-locale/references/check-identifier-locale.py` -> `981`
      - `wc -l README.md` in ferdinand -> `1006 README.md`
      - largest table cell in `docs/REFERENCE.md`, via awk over `^|` rows ->
        `max=205  linha=144`
      - cells over 120 chars in the same file -> `células=115  média=71 chars  acima de 120 chars=15`
      - `grep -niE '^\s*(## )?(índice|sumário|table of contents)' README.md docs/*.md` ->
        `docs/SETUP.md:10:## Índice` (README returns nothing)
      - fence-aware heading map of ferdinand `README.md` -> `127  ##  ## O modo sem cluster`
        followed by eight `###` entries

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Open question recorded in `design.md`: whether GitHub keeps the code-span text in the anchor it
      generates for a heading like `#### \`LEADER_TERM\``. It does in `solvelab/feldt`, measured there
      against returned HTML, and it has NOT been probed for this catalog. It is written as an open
      question, not asserted, and `ferdinand#441` carries it as a technical requirement to confirm
      against returned HTML before writing 101 links.

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Noticed and NOT performed:
      - `ferdinand`'s `docs/REFERENCE.md` and `README.md` — the two items blocked on this one
        (`ferdinand#441`, `ferdinand#442`)
      - a second sample repository for the false-positive measurement; recorded in `design.md` as a
        limit of the measurement
      - `templates.md` and `examples.md` of the `documentation` skill carry no index of their own;
        left alone beyond the cross-link

## 2. The seven rules

- [ ] 2.1 `skills/documentation/references/information-architecture.md` created, carrying the seven
      rules — each with its statement, its published source as a link, an example of the defect and
      an example of the correct form
- [ ] 2.2 Every rule carries the anatomy of the reference page it governs where it applies: the
      fixed field order, and what a consumer repo writes when a field does not apply
- [ ] 2.3 The threshold rules carry their cut as a number, not as a preference: 100 lines for the
      index, 120 characters for a table cell, 25 rows for a table of options
- [ ] 2.4 The reference links to `verify-before-claiming` and `code-locale` instead of restating
      them, per the Canonical Home table in `design.md`

## 3. The detector, measured

- [ ] 3.1 `skills/documentation/references/check-doc-structure.py` drafted, stdlib only, with the
      CLI contract of the `code-locale` detectors
- [ ] 3.2 The draft ran against `ferdinand@66346d4`; findings per rule recorded as counts
- [ ] 3.3 Every finding hand-confirmed; true positives and false positives counted per rule
- [ ] 3.4 Each rule marked **with validator** or **review-only** in the reference, and no
      `review-only` mark stands without its measurement beside it
- [ ] 3.5 The detector proved by inversion: a document carrying the defect fails, a correct document
      passes — one inversion per shipped check
- [ ] 3.6 `--selftest` implemented, injecting one known defect per shipped check and asserting
      detection; it is the only gate over this script, since `scripts/validate-skills.py` never
      opens a `.py` under `references/`
- [ ] 3.7 The four measured ferdinand defects are each either caught by the detector or explicitly
      assigned to a review-only rule, with no defect left unassigned

## 4. The skill body and the catalog

- [ ] 4.1 `skills/documentation/SKILL.md` links `references/information-architecture.md` and carries
      in its body only the rules that hold without exception. The link is a gate, not a courtesy:
      C11 of `scripts/validate-skills.py` fails an orphan `*.md` under `references/`, and the
      Cursor wrapper's specific blob link depends on the same edge
- [ ] 4.2 `metadata.version` bumped
- [ ] 4.3 `bash generate.sh` run after the commit, `git diff --exit-code` clean on the wrappers
- [ ] 4.4 The reference states how a consumer runs the detector from a clone and that the existing
      `pre-commit-locale.sh` does NOT pick it up — that hook hardcodes two filenames

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [ ] Q.2 All touched skill content in English (catalog locale)
- [ ] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [ ] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [ ] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-information-architecture-rules --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive add-information-architecture-rules --yes` after all groups above are `[x]`
