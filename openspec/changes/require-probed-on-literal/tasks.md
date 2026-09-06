## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at
      Evidence: Opened 2026-09-06 at HEAD f1e4b02: `scripts/validate-skills.py:244-296` (C5 block, `ISO_DATE`, `check_pin`), `scripts/selftest-validate-skills.py:30-55`, `README.md:875-913`, `openspec/specs/skills-authoring/spec.md` (requirement copied whole into the MODIFIED delta), the 32 `Verified against` blocks (measured programmatically), `skills/api-resilience-testing/SKILL.md:23-30`, `skills/svg-animation/SKILL.md:25-31`, `openspec/changes/archive/2026-09-06-add-pin-date-gate/tasks.md` (S.3, the fivem-lua escape).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded
      Evidence: Normalised measurement script (`block = text[m.start():].split('\n\n',1)[0]; norm = ' '.join(re.sub(r'^> ?','',l) for l in block.splitlines())`) -> `blocks: 32 with literal: 30 declarations: 3`, `missing literal: [('api-resilience-testing', ['2026-09-05']), ('svg-animation', ['2026-08-30','2026-08-31','2026-09-05'])]`; raw-vs-normalised on the wrap cases -> `assettoserver-csp-lua raw=False normalised=True`, `react-api-client raw=False normalised=True`, `k8s-tune-resources raw=True normalised=True paragraphs=2`. After the rewrites -> `missing literal: []`. `python3 scripts/validate-skills.py` -> `skills checked: 35   findings: 0`.
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
      Evidence: Nothing this change asserts was unprobeable: every count comes from the measurement script over this clone and every finding text from a run of the validator. What the gate still cannot tell — a `Probed on <date>` written for a run nobody made, or an implausible date — stays in the C5 docstring as the remaining KNOWN LIMIT.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed
      Evidence: Follow-ups noticed and NOT performed: (1) date plausibility (future or decades-old dates pass); (2) the declaration form carries a date by convention only; (3) README:468 still says `C1–C9` in the tree listing (noted three times now); (4) `verify-before-claiming` writes the literal in lower case inside running prose — accepted by design, not reworded.
## 2. Gate

- [x] 2.1 C5 normalises the block and requires `[Pp]robed on YYYY-MM-DD`; "carries no date" kept for
      blocks with no date; docstring names the normalisation and the wrap it exists for
      Evidence: `scripts/validate-skills.py`: `PROBED_ON = re.compile(r"\b[Pp]robed on 20\d\d-\d\d-\d\d\b")`; `block = " ".join(re.sub(r"^> ?", "", line) for line in block.splitlines())` before both rules; new finding `'Verified against' block names no \`Probed on <date>\` — a date of a commit or release the block cites does not stand in for the date the probe ran`; docstring names the normalisation and the two wrap cases.
- [x] 2.2 Selftest mutation `C5 no version pin (date but no Probed on)` on `observability`
      Evidence: `scripts/selftest-validate-skills.py`: mutation `C5 no version pin (date but no Probed on)` on `skills/observability/SKILL.md` (`Probed on 2026-08-06` -> `Dated 2026-08-06`, fragment `names no`) -> `CAUGHT`; run -> `23/24 defect classes detected` locally (MISSED only `C3 lua syntax`, luac absent).
## 3. Blocks and docs

- [x] 3.1 `api-resilience-testing` and `svg-animation` blocks reworded to carry the literal, facts kept;
      patch bumps
      Evidence: `api-resilience-testing` 1.3.2 -> 1.3.3: `… \`uvicorn 0.52.4\`. Probed on 2026-09-05, re-measuring the nine baseline rows with a stock two-route service …`; `svg-animation` 1.1.3 -> 1.1.4: `… WSL2). Probed on 2026-08-30 and 2026-08-31, driven over CDP by measure.mjs — …`, `Not re-run on 2026-09-05` kept. Rewrite script asserted the old sentence present before replacing.
- [x] 3.2 README C5 sentence and selftest count (23 → 24)
      Evidence: `README.md:878-879` -> `with a \`Probed on <date>\` line`; `:913` -> `24/24 defect classes detected`.
- [x] 3.3 `./generate.sh`; wrappers in sync
      Evidence: `bash generate.sh` -> `git status --porcelain --untracked-files=all | grep -c '^??'` -> 0; 11 paths changed before commit.
## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
      Evidence: entry point `python3 scripts/validate-skills.py` -> `skills checked: 35   findings: 0`; on a copy with observability's `Probed on` -> `Dated` -> `[C5 no version pin] 'Verified against' block names no \`Probed on <date>\` — a date of a commit or release the block cites does not stand in for the date the probe ran`; the same copy restored -> `assettoserver-csp-lua`, `react-api-client`, `k8s-tune-resources` absent from the findings (wrap-split and two-paragraph blocks silent); entry point `python3 scripts/selftest-validate-skills.py` -> `CAUGHT  C5 no version pin (date but no Probed on)`.
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
      Evidence: 1/1 dated-but-unnamed block had to fire and did; 35/35 skills silent after the two rewrites; 2/2 wrap-split blocks silent without edits; 1/1 two-paragraph block silent; 2/2 reworded blocks keep their facts; 1/1 lower-case `probed on` block (verify-before-claiming) silent by design; 1/1 pre-existing local miss unchanged (`C3 lua syntax`).
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did
      Evidence: Nothing escaped or behaved differently than expected: the raw-vs-normalised measurement predicted exactly the two rewrites and the two wrap cases, and the validator confirmed both.
## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
      Evidence: Frontmatter loop replicated over `skills/*/SKILL.md` -> `frontmatter fail=0`; `agentskills validate` -> `fail=0` over 35; `npx -y @anthropic-ai/claude-code@2.1.246 plugin validate . --strict` -> `✔ Validation passed`.
- [x] Q.2 All touched skill content in English (catalog locale)
      Evidence: All added text is English; `check-identifier-locale.py` over the changed `skills/`, `scripts/` and `README.md` -> `findings: 0`.
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
      Evidence: `git diff master -- skills/ | grep -c -E '^[-+]\s*description'` -> `0`; no trigger moved.
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
      Evidence: The rule lives in the `skills-authoring` requirement and the C5 docstring; the two blocks carry the sentence only (design.md Canonical Home, two rows, `already canonical`).
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown
      Evidence: No code example touched; detector -> `findings: 0`.
## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate require-probed-on-literal --strict` green
      Evidence: `openspec validate require-probed-on-literal --strict` -> `Change 'require-probed-on-literal' is valid`; `bash scripts/validate-rite.sh` -> `rite gate OK` (evidence gate 0, spec-rite gate 0).
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
      Evidence: `npx -y skills add solvelab/ai-skills --list | grep -c -E '^│    [a-z0-9-]+$'` -> `35`; nothing added, removed or renamed.
- [x] V.3 README / docs updated where the change alters catalog composition or usage
      Evidence: `README.md` C5 sentence and selftest count updated; catalog composition unchanged.
- [ ] V.4 `openspec archive require-probed-on-literal --yes` after all groups above are `[x]`
