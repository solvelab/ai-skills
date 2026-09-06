## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at
      Evidence: Opened 2026-09-06 at HEAD c8f55f9: `scripts/validate-skills.py` (module docstring, the C5 region 249-300, the import block, `add()`), `scripts/selftest-validate-skills.py` (24 MUTATIONS entries, the runner's `expect`/`fragment` contract), `README.md:880-881` and `:916`, `openspec/specs/skills-authoring/spec.md` (requirement copied whole into the MODIFIED delta), the 32 `Verified against` blocks (read programmatically), `openspec/changes/archive/2026-09-06-require-probed-on-literal/tasks.md` (the KNOWN LIMIT this change closes).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded
      Evidence: `git log --reverse --format='%cs %h' | head -1` -> `2026-03-13 1e95262` (the P3 floor). `date -u +%F` -> `2026-09-06`. `python3 -c "datetime.date.fromisoformat('2026-13-45')"` -> `ValueError: month must be in 1..12`. Dry run of the three rules over the catalogue before any edit -> `implausible probe dates today: []`, probe dates `['2026-08-06', '2026-08-30', '2026-09-05']`. Capture check -> `svg-animation captures=['2026-08-30'] all_iso=['2026-08-30','2026-08-31','2026-09-05']`, `fivem-lua captures=['2026-09-05'] all_iso=['2026-09-02','2026-08-17','2026-09-05']` (cited commit dates stay outside the rule). `python3 scripts/validate-skills.py` after the edit -> `skills checked: 35   findings: 0`. `git status --porcelain` -> only `README.md`, `scripts/selftest-validate-skills.py`, `scripts/validate-skills.py`; `git diff --stat master -- skills` -> empty.
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
      Evidence: Nothing this change asserts was unprobeable: every rule was exercised through the validator's own entry point and every count comes from a script over this clone. What the gate still cannot tell — a plausible date written for a probe that never ran — is stated in the C5 docstring as the remaining KNOWN LIMIT, not filled in.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed
      Evidence: Follow-ups noticed and NOT performed: (1) an age report per pin (days since the probe) and any expiry policy — excluded by the item on the user's choice; (2) dates the block cites outside the literal are still unvalidated, by design; (3) `REPO_INCEPTION` is a constant, so a rewritten history would need it re-measured — the command is in the comment beside it; (4) the two active changes from another session (`add-lean-code-research`, `update-documentation-prerequisites`) were left untouched.
## 2. Gate

- [x] 2.1 C5 validates every captured probe date: P1 calendar (`date.fromisoformat`), P2 not after
      today in UTC, P3 not before `REPO_INCEPTION`; one finding per rule; cited dates untouched
      Evidence: `scripts/validate-skills.py`: `PROBE_DATE = re.compile(r"[Pp]robed on (20\d\d-\d\d-\d\d)")`, `REPO_INCEPTION = date(2026, 3, 13)` with the re-measure command in the comment, and a loop over `PROBE_DATE.findall(block)` raising one finding per rule under the check name `C5 implausible probe date`: `is not a calendar date` (ValueError from `date.fromisoformat`), `is in the future (checked <today> UTC)`, `predates the repository (first commit 2026-03-13)`. Dates outside the literal are never read.
- [x] 2.2 Docstring: plausibility leaves the KNOWN LIMIT, what remains is written, UTC choice stated
      Evidence: Docstring: the paragraph 'Each captured probe date is also checked for POSSIBILITY (issue #165)…' states the three rules, the UTC + `<=` choice and why (CI is UTC, the maintainer is UTC-3), and that cited dates are left alone; the KNOWN LIMIT now reads 'proves the literals are PRESENT and the probe date is POSSIBLE, not that either is earned… a plausible date for a probe that never happened' passes.
## 3. Selftest and docs

- [x] 3.1 Three mutations on `observability` (month 13, year 2099, year 2020), one per rule
      Evidence: `scripts/selftest-validate-skills.py`: `C5 implausible probe date (not a calendar date)` / `(future)` / `(predates the repository)` on `skills/observability/SKILL.md`, replacing `Probed on 2026-08-06` with `2026-13-45` / `2099-01-01` / `2020-01-01`; run -> all three `CAUGHT`, `26/27 defect classes detected` locally (MISSED only `C3 lua syntax`, luac absent here).
- [x] 3.2 README: C5 sentence says the date is plausible; selftest count 24 → 27
      Evidence: `README.md:880-882` -> `with a \`Probed on <date>\` line whose date could actually be true`; `:916` -> `27/27 defect classes detected`. The module docstring's C5 line also names the possible date.
- [x] 3.3 `./generate.sh`; wrappers in sync (nothing generated changes)
      Evidence: `bash generate.sh` -> `git status --porcelain --untracked-files=all | grep -c '^??'` -> 0, and the working tree still shows only the three edited files: nothing generated changed, because no `skills/` file was touched.
## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
      Evidence: entry point `python3 scripts/validate-skills.py` on the catalogue -> `skills checked: 35   findings: 0`. Four temporary copies, each with observability's probe date replaced, run through the same entry point: `2026-13-45` -> `[C5 implausible probe date] Probed on 2026-13-45 is not a calendar date`; `2099-01-01` -> `… is in the future (checked 2026-09-06 UTC)`; `2020-01-01` -> `… predates the repository (first commit 2026-03-13)`; `2026-09-06` (today in UTC, the P2 boundary) -> `<silent>`. entry point `python3 scripts/selftest-validate-skills.py` -> three `CAUGHT`, `26/27`.
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
      Evidence: 3/3 rules had to fire and did, each with its own message; 1/1 boundary case (a date equal to today in UTC) had to stay silent and did; 35/35 skills silent with no edit; 32/32 probe dates plausible in the dry run; 2/2 blocks carrying cited commit dates (`fivem-lua`, `assettoserver-csp-lua`) silent, so the rule reads only what follows the literal; 1/1 block with two dates after one literal (`svg-animation`) silent; 0 files under `skills/` changed; 1/1 pre-existing local miss unchanged (`C3 lua syntax`, luac absent — CI installs lua5.4).
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did
      Evidence: Nothing escaped or behaved differently than expected. One deliberate design choice worth naming: the three findings are filed under a NEW check label, `C5 implausible probe date`, instead of the existing `C5 no version pin` — the summary groups findings by label, and a run that says 'implausible probe date 1' points at the defect directly. It stays inside C5's family and the README's C1–C13 list is unaffected.
## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
      Evidence: No SKILL.md was touched (`git diff --stat master -- skills` empty); the frontmatter loop was replicated anyway over `skills/*/SKILL.md` -> `frontmatter fail=0`; `agentskills validate` -> `fail=0` over 35; `npx -y @anthropic-ai/claude-code@2.1.246 plugin validate . --strict` -> `✔ Validation passed`.
- [x] Q.2 All touched skill content in English (catalog locale)
      Evidence: All added text is English; `check-identifier-locale.py` over the three changed files -> `findings: 0`.
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
      Evidence: No description changed (no skill file touched), so no trigger moved.
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
      Evidence: The rule lives in the `skills-authoring` requirement and the C5 docstring; no skill restates it (design.md Canonical Home, two rows, `already canonical`).
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown
      Evidence: No code example touched; detector -> `findings: 0`.
## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-probe-date-plausibility --strict` green
      Evidence: `openspec validate add-probe-date-plausibility --strict` -> `Change 'add-probe-date-plausibility' is valid`; `bash scripts/validate-rite.sh` -> `rite gate OK` (evidence gate 0 findings, spec-rite gate 0 findings, 3 active changes — two belong to another session and were not touched).
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
      Evidence: `npx -y skills add solvelab/ai-skills --list | grep -c -E '^│    [a-z0-9-]+$'` -> `35`; nothing added, removed or renamed.
- [x] V.3 README / docs updated where the change alters catalog composition or usage
      Evidence: `README.md` C5 sentence and selftest count updated; catalog composition unchanged.
- [x] V.4 `openspec archive add-probe-date-plausibility --yes` after all groups above are `[x]`
      Evidence: `openspec archive add-probe-date-plausibility --yes` after PR #166 merged -> archived as `2026-09-06-add-probe-date-plausibility`, specs updated. `openspec list` still shows the two changes another session left active (`add-lean-code-research`, `update-documentation-prerequisites`) — untouched by this run.