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
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      None left open. The one open point at writing time, how GitHub renders `\|` inside a cell, was
      probed (E.2) and closed. The `plugin validate` step of CI
      (`npx @anthropic-ai/claude-code@2.1.246 plugin validate . --strict`) was not run locally; it
      runs in the pull request, and its result is read there, not assumed.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Noticed and NOT performed:
      - The catalog's own `skills/` tree carries 247 R1/R2 findings under this detector (242 before
        the change). The detector is not run over `skills/` in CI and this change does not start
        that: bringing 148 files under the rules is its own item.
      - The five new findings are `references/` pages of `r3f-assets` and `r3f-postprocessing`,
        made only of `###`: a follow-up for those skills, not for the detector.

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
- [x] 3.4 `bash generate.sh` run after the commit, `git diff --exit-code` clean on the wrappers

      `bash generate.sh` after the fix commit -> 4 wrapper files changed under `claude/` and
      `plugins/docs/`, committed; `bash generate.sh` again -> `git diff --exit-code` exit 0

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

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      The consumer's path: a clone of the repository, the script run on its tree.
      - `python3 check-doc-structure.py --exclude 'docs/spikes/*' --exclude 'openspec/*' --exclude
        'CHANGELOG.md' --exclude 'spike/*' --exclude 'test/*' .` on `solvelab/ferdinand@eea8b20` ->
        `10 [R6]` and nothing else, with the old script and with the new one
      - `python3 check-doc-structure.py skills/documentation` -> `findings: 0 in 4 file(s)`
      - `python3 check-doc-structure.py r1.md` (only `###`, 120+ lines) ->
        `[R1] 126 lines and no index; a reader has no way in`
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      - Had to fire and did: 10/10 injected cases (`--selftest`), of which 3/3 are the field misses.
      - Had to stay silent and did: 1/1 clean selftest document; ferdinand at `eea8b20`: 0/0 R1 and
        R2 before and after; `skills/documentation`: 0/0.
      - Delta over the whole `skills/` tree, old script against new: 5/5 new R1 findings
        hand-confirmed (pages of 105 to 218 lines, only `###`, no index); 1/1 R2 cell remeasured
        from 222 to 264 characters (`verify-before-claiming/references/failure-catalog.md:22`,
        which carries a `\|`); 0 findings from the index-block rule.
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      The index-block rule found nothing new anywhere it ran. It is proven by its injected case only;
      no real document in either sample had an index missing a section the body cites. Nothing else
      behaved differently than expected.

## 5. Quality Gates (MANDATORY)

<!-- Adversarial review of the skills touched — not happy-path. Every skill added or edited
     by this change gets checked against the skills-authoring spec. Keep this group second-to-last. -->

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present

      Only `metadata.version` moved in `skills/documentation/SKILL.md`;
      `python3 scripts/validate-skills.py` -> `skills checked: 40   findings: 0`
- [x] Q.2 All touched skill content in English (catalog locale)

      The two paragraphs added to `information-architecture.md` and the comments in the script are English.
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists

      Description untouched by this change.
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)

      The selftest-in-CI obligation is stated once, in `skills-authoring`; the CI step comment points
      at the item, not at a restated rule.
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown

      New identifiers: `ESCAPED_PIPE_SPLIT`, `index_end`, `level_of_sections`, and the selftest keys
      `R1-h3-only`, `R1-body-link`, `R2-escaped-pipe`, all English.

## 6. Validation & Closure (MANDATORY)

<!-- Always the last group. "Done" is verifiable, not an opinion. -->

- [x] V.1 `openspec validate <id> --strict` green

      `openspec validate update-doc-structure-checker-blind-spots --strict` ->
      `Change 'update-doc-structure-checker-blind-spots' is valid`; `bash scripts/validate-rite.sh`
      -> `rite gate OK`; `python3 scripts/validate-rite-evidence.py` -> `rite evidence gate: 0 findings`
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers

      `npx -y skills add solvelab/ai-skills --list` -> `Found 40 skills`, `documentation` among
      them; `ls skills/ | wc -l` -> `40`. No skill added, renamed or removed.
- [x] V.3 README / docs updated where the change alters catalog composition or usage

      Nothing to update: composition and install forms are unchanged. The rule text changed in the
      same commit as the detector (`information-architecture.md`).
- [x] V.4 `openspec archive <id> --yes` after all groups above are `[x]`

      `openspec archive update-doc-structure-checker-blind-spots --yes` ->
      `skills-authoring: update` / `~ 1 modified` / `Totals: + 0, ~ 1, - 0, → 0` /
      `Change 'update-doc-structure-checker-blind-spots' archived as
      '2026-09-25-update-doc-structure-checker-blind-spots'`
