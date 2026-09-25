## 1. Evidence & Sources (MANDATORY)

<!-- Always the FIRST group: probe before you write. Record the COMMAND and a fragment of its
     RAW OUTPUT, never a conclusion — a row a reviewer can re-run in two seconds is the only kind
     worth writing. A claim with no evidence is a guess: drop the claim, or go get the evidence.
     Doctrine: the verify-before-claiming skill.

     Shape each box owes, gated by scripts/validate-rite-evidence.py once ticked:
       E.1  a repo-relative path AND the commit sha or date it was read at
       E.2  at least one `command` -> a fragment of its output
       E.3  names the gap, or states explicitly that there is none
       E.4  lists a follow-up, or states explicitly that there is none
     The gate cannot tell a real output from an invented one — that is still the reviewer's job. -->

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Read on 2026-09-24 in `solvelab/ai-skills` at commit `1abce62`:
      - `skills/documentation/references/check-doc-structure.py` — 515 lines; `check_index`,
        `tables()`, `anchor_of`, `SELFTEST_CASES`, `SELFTEST_CLEAN`
      - `skills/documentation/references/information-architecture.md` — 536 lines; R1 and R2 text
      - `skills/documentation/SKILL.md` — 385 lines, `metadata.version: 4.0.0`
      - `openspec/specs/skills-authoring/spec.md` — 904 lines, 20 requirements; *Authoring rules are
        machine-enforced*
      - `.github/workflows/ci.yml` — the self-test steps for the `code-locale` detectors
      - `openspec/changes/archive/2026-09-06-add-information-architecture-rules/` — the change that
        shipped the detector

      Read on 2026-09-24 in `solvelab/ferdinand` at commit `eea8b20`:
      - `test/unit/docs-structure.test.ts` — the guard that found the three shapes
      - `docs/SIGNALS.md`, `docs/DEPLOYMENT.md` — the two field cases
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      - `openspec --version` -> `1.6.0`
      - `openspec new change update-doc-structure-checker-blind-spots --schema skills-rite` -> `Schema: skills-rite`
      - `python3 check-doc-structure.py --selftest` at `1abce62` ->
        `selftest: 7/7 injected defects detected; clean document silent`
      - `python3 check-doc-structure.py r1.md` (only `###`, 120+ lines) -> `findings: 0 in 1 file(s)`
      - `python3 check-doc-structure.py r2.md` (cell of 70 + ` \| ` + 70 chars) -> `findings: 0 in 1 file(s)`
      - `python3 check-doc-structure.py r1b.md` (`## B` linked only from the body) -> `findings: 0 in 1 file(s)`
      - `grep -n check-doc-structure .github/workflows/ci.yml` -> no output
      - `gh api -X POST markdown -f mode=gfm` over `| x | p \| q |` -> `<td>p | q</td>`, one cell
- [ ] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
- [ ] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

## 2. The detector

- [x] 2.1 Three injected cases added to `SELFTEST_CASES` first, and `--selftest` fails on them
      before the fix

      `python3 check-doc-structure.py --selftest` before the fix ->
      `selftest: 7/10 injected defects detected; clean document silent`, exit 1, naming
      `R1-h3-only`, `R1-body-link` and `R2-escaped-pipe`
- [x] 2.2 R1 falls back to `###` when the document has no `##`
- [x] 2.3 R1 counts only links inside the index block, from the index heading to the next heading
- [x] 2.4 R2 treats `\|` as cell text
- [x] 2.5 `--selftest` detects every injected defect and `SELFTEST_CLEAN` stays silent

      `python3 check-doc-structure.py --selftest` after the fix ->
      `selftest: 10/10 injected defects detected; clean document silent`, exit 0

## 3. The rule text, the gate and the catalog

- [x] 3.1 `information-architecture.md` R1 states the `###` fallback and that only the index block
      counts; R2 states that an escaped pipe is cell text
- [x] 3.2 `.github/workflows/ci.yml` runs `check-doc-structure.py --selftest`
- [x] 3.3 `metadata.version` of `documentation` bumped: `4.0.0` -> `4.1.0`, minor because R1 now
      reproves a shape it accepted
- [ ] 3.4 `bash generate.sh` run after the commit, `git diff --exit-code` clean on the wrappers

## 4. Simulation & Field Proof (MANDATORY)

<!-- Second-to-last but one: proof that the artifact was RUN, before the quality review discusses it.
     Reading, probing, uniform frontmatter and a green strict validation can all hold while the
     artifact was never executed once — measured on 2026-08-26 (issue #95), where a green selftest
     and a green CI still shipped two defects that only an end-to-end run surfaced.

     Exercise the artifact through the path its USER takes — the hook fired by the harness, the CLI
     invoked as documented, the skill loaded in a session — and record what you OBSERVED, never what
     you expected. Breaking it on purpose afterwards is a different job: the bug-hunter skill.
     The doctrine behind "observed, not recalled" is verify-before-claiming.

     Shape each box owes, gated by scripts/validate-rite-evidence.py once ticked:
       S.1  an `entry point` -> a fragment of the OBSERVED output; or an explicit statement that the
            change touches no runtime artifact
       S.2  the case matrix as counts (n/n): what had to fire and did, what had to stay silent and
            did, which known escapes stayed silent
       S.3  names what escaped or misbehaved, or states explicitly that nothing did
     The gate cannot tell a real observation from an invented one — that is still the reviewer's job. -->

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 5. Quality Gates (MANDATORY)

<!-- Adversarial review of the skills touched — not happy-path. Every skill added or edited
     by this change gets checked against the skills-authoring spec. Keep this group second-to-last. -->

- [ ] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [ ] Q.2 All touched skill content in English (catalog locale)
- [ ] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [ ] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [ ] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown

## 6. Validation & Closure (MANDATORY)

<!-- Always the last group. "Done" is verifiable, not an opinion. -->

- [ ] V.1 `openspec validate <id> --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive <id> --yes` after all groups above are `[x]`
