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

- [x] 2.1 `skills/documentation/references/information-architecture.md` created, carrying the seven
      rules — each with its statement, its published source as a link, an example of the defect and
      an example of the correct form
- [x] 2.2 Every rule carries the anatomy of the reference page it governs where it applies: the
      fixed field order, and what a consumer repo writes when a field does not apply
- [x] 2.3 The threshold rules carry their cut as a number, not as a preference: 100 lines for the
      index, 120 characters for a table cell, 25 rows for a table of options
- [x] 2.4 The reference links to `verify-before-claiming` and `code-locale` instead of restating
      them, per the Canonical Home table in `design.md`

## 3. The detector, measured

- [x] 3.1 `skills/documentation/references/check-doc-structure.py` drafted, stdlib only, with the
      CLI contract of the `code-locale` detectors
- [x] 3.2 The draft ran against `ferdinand@66346d4`; findings per rule recorded as counts
- [x] 3.3 Every finding hand-confirmed; true positives and false positives counted per rule
- [x] 3.4 Each rule marked **with validator** or **review-only** in the reference, and no
      `review-only` mark stands without its measurement beside it
- [x] 3.5 The detector proved by inversion: a document carrying the defect fails, a correct document
      passes — one inversion per shipped check
- [x] 3.6 `--selftest` implemented, injecting one known defect per shipped check and asserting
      detection; it is the only gate over this script, since `scripts/validate-skills.py` never
      opens a `.py` under `references/`
- [x] 3.7 The four measured ferdinand defects are each either caught by the detector or explicitly
      assigned to a review-only rule, with no defect left unassigned

## 4. The skill body and the catalog

- [x] 4.1 `skills/documentation/SKILL.md` links `references/information-architecture.md` and carries
      in its body only the rules that hold without exception. The link is a gate, not a courtesy:
      C11 of `scripts/validate-skills.py` fails an orphan `*.md` under `references/`, and the
      Cursor wrapper's specific blob link depends on the same edge
- [x] 4.2 `metadata.version` bumped
- [x] 4.3 `bash generate.sh` run after the commit, `git diff --exit-code` clean on the wrappers
- [x] 4.4 The reference states how a consumer runs the detector from a clone and that the existing
      `pre-commit-locale.sh` does NOT pick it up — that hook hardcodes two filenames

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      Ran in `solvelab/ferdinand` at commit `66346d4`:

      `python3 …/check-doc-structure.py --exclude 'spikes/*' README.md docs/` ->
      `docs/REFERENCE.md: [R3] 115 options in tables across this document and not one section
      heading, so none has an anchor; above 25 the catalog is navigated, not scanned` /
      `findings: 31 in 8 file(s); rules run: R1,R2,R3,R4,R6,R7`, exit `1`

      `python3 …/check-doc-structure.py --selftest` ->
      `selftest: 7/7 injected defects detected; clean document silent`, exit `0`

      `python3 …/check-doc-structure.py --list` ->
      `R1  implemented  a document over 100 lines carries an index covering every '##'` (six rows)
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      Injected defects that had to fire and did: **7/7**.
      Clean document that had to stay silent and did: **1/1**.
      Rules shipping with a validator: **5/7** (R1, R2, R3, R4, R7); review-only: **2/7** (R5, R6).

      Findings on the sample, each confirmed by hand:

      | rule | findings | confirmed | false positives |
      |---|---|---|---|
      | R1 index | 10 | 7 | 3 — all spike notes, a scope question, resolved by `--exclude` |
      | R2 cell length | 15 | 15 | 0 |
      | R3 option catalog | 1 | 1 | 0 |
      | R6 heading tree | 10 | 3 | 7 |
      | R4 anatomy | 0 | — | — (the repository has no option sections yet) |
      | R7 alert type | 0 | — | — (the repository uses no alerts yet) |

      With `--exclude 'spikes/*'`: `findings: 31 in 8 file(s)`, R1 at 7/7.
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 6. Quality Gates (MANDATORY)


      Three things behaved differently than expected, all recorded rather than smoothed over:

      1. **R6 reproved itself.** Seven of ten reports were correctly-nested sections that are merely
         long — `## Memória` with four memory signals, `## CPU` with five CPU signals,
         `## 4. Decisões de arquitetura` with four decisions, `## 1. Variáveis do agente` with
         fourteen variable groups. R6 ships review-only because of this count, not despite it.
      2. **Two defects in my own detector**, both found by hand confirmation and both fixed:
         `## Índice` was read as absent because the match was not accent-folded, reproving a correct
         document; and a table cell was reported at line 220 when it sat at 219, because the divider
         row leaves the list and keeps its line.
      3. **R4 and R7 have no field evidence.** Zero findings on the sample is correct — there are no
         option sections and no alerts in that repository yet — but it means both are proved only by
         their injected defect, never against prose somebody wrote. Written here rather than counted
         as a clean run.

      Limit of the measurement: one repository, one writing style. A second sample is a follow-up.
- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present

      `python3 scripts/validate-skills.py` -> `skills checked: 36   findings: 0` (C10 measures the
      parsed `description` and `compatibility` limits). Only `documentation` was touched; its
      `metadata.version` moved `3.1.1` -> `3.2.0`.
- [x] Q.2 All touched skill content in English (catalog locale)

      Both new files are English throughout. `python3 scripts/validate-skills.py` -> `findings: 0`,
      which includes C9 running `check-identifier-locale.py --markdown-fences skills/`.
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists

      The `description` was not touched: this change adds doctrine inside the skill, not a new
      reason to route to it. Its existing "Do NOT use for non-software documentation tasks" boundary
      stands, and no sibling gained a colliding trigger.
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)

      `information-architecture.md` links `verify-before-claiming` and `code-locale` instead of
      restating either, and the review-only obligation is stated once in the `skills-authoring`
      spec delta with the skill pointing at it. Checked by reading the file, and by C11 —
      `validate-skills.py` -> `findings: 0` — which also proves the new `.md` is not an orphan.
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-information-architecture-rules --strict` green

      `openspec validate add-information-architecture-rules --strict` ->
      `Change 'add-information-architecture-rules' is valid`; `bash scripts/validate-rite.sh` ->
      `rite gate OK`; `python3 scripts/selftest-validate-skills.py` ->
      `27/27 defect classes detected`
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers

      `npx -y skills add solvelab/ai-skills --list` -> 36 skill names listed, `documentation` among
      them. The command reads the published catalog, and this change adds, renames and removes no
      skill, so the count is the invariant: `ls skills/ | wc -l` -> `36` and
      `python3 scripts/validate-skills.py` -> `skills checked: 36   findings: 0`
- [x] V.3 README / docs updated where the change alters catalog composition or usage

      Nothing to update: catalog composition is unchanged and no install form changed. The skill's
      own body and `See also` were updated in the same commit as the reference it points at.
- [ ] V.4 `openspec archive add-information-architecture-rules --yes` after all groups above are `[x]`

      **Left unticked on purpose.** This repository archives in its own pull request — the precedent
      is commit `0959ccc`, `docs(openspec): arquiva a change add-prose-locale-gate (#181)`, which
      moved a finished change and nothing else. Archiving here would move the published specs before
      a human approved the code they describe.
