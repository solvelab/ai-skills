## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at
      Evidence: Opened 2026-09-05 at HEAD 85c453d: `scripts/validate-skills.py` (C5 block, `check_pin`), `scripts/selftest-validate-skills.py:30-46`, `README.md:875-913`, `openspec/specs/skills-authoring/spec.md:250-300` (the requirement, copied whole into the MODIFIED delta), the 14 `skills/<name>/SKILL.md` blocks (`r3f-*:18-22`, `observability:22-25`, `k8s-tune-resources:23-28`, `fivem-nui-react:105-108`, `python-rest-api:183`), and the archived changes `2026-08-06-{harden-r3f-skills,pin-probed-skills,onboard-k8s-tune-resources,add-observability-skill,add-async-lane-rule}`.
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded
      Evidence: `for f in skills/*/SKILL.md; do awk '/Verified against/{p=1} p&&/^$/{exit} p' $f | grep -q -E '20[0-9]{2}-[0-9]{2}-[0-9]{2}' || grep -q 'does not depend on a tool version' $f || echo $f; done` -> 14 files before, nothing after. `git log --format='%h %cs %s' a18758c 9afef67 d1e22a4 60eb0be c27ca79` -> all `2026-08-06`: `🐛 fix(r3f): make the code blocks compile, and pin what they compile against (#26)`, `🐛 fix(skills): pin what was probed, and fix the pin detector (#39)`, `✨ feat(k8s-tune-resources): bring the orphan skill into the catalog (#33)`, `✨ feat(observability): add the skill that makes the family's failures visible (#53)`, `✨ feat(python-rest-api): state the async/sync lane rule for DB access (#51)`. `grep -l 'Verified against' openspec/changes/archive/2026-08-06-*/{tasks,proposal,design}.md` -> `harden-r3f-skills/tasks.md`, `pin-probed-skills/design.md`, `onboard-k8s-tune-resources/proposal.md`, `add-async-lane-rule/proposal.md` (+ observability's own change). `python3 scripts/validate-skills.py` -> `skills checked: 35   findings: 0`. `git diff -- skills | grep -c -E '^[-+]\s+version:'` -> `0`.
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
      Evidence: Nothing this change asserts was unprobeable: the dates come from `git log` on this clone, the block shapes from reading the 14 files. What the gate cannot tell — whether a date is the probe's or an unrelated one, and whether it is plausible — is written into the C5 docstring as the remaining KNOWN LIMIT and into design.md, not filled in.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed
      Evidence: Follow-ups noticed and NOT performed: (1) `fivem-lua`'s block dates the citizenfx commits it names, so it carries three ISO dates — a stricter rule ("a `Probed on` date") would need a literal for the probe date itself, out of scope; (2) date plausibility (future, decades old) is not checked; (3) the declaration form (`helm-migration`, `bug-hunter`, `documentation`) carries a date by convention only; (4) README:468 still says `C1–C9` in the tree listing (stale before this change, noted twice now).
## 2. Gate

- [x] 2.1 C5 isolates the block and requires `\b20\d\d-\d\d-\d\d\b` inside it; declaration form exempt;
      docstring updated (date KNOWN LIMIT removed, plausibility named as the remaining one)
      Evidence: `scripts/validate-skills.py`: `ISO_DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")`; `block = text[pinned.start():].split("\n\n", 1)[0]`; finding `'Verified against' block carries no date (YYYY-MM-DD) — a pin with no date does not say when it stopped being trustworthy`; docstring names the remaining limits (shape only, plausibility unchecked, deferral phrase).
- [x] 2.2 Selftest mutation `C5 no version pin (undated block)` on `fivem-lua`; old mutations untouched
      Evidence: `scripts/selftest-validate-skills.py`: mutation `C5 no version pin (undated block)` on `skills/observability/SKILL.md` (`2026-08-06` -> `the day the skill landed`; the file carries exactly one ISO date) -> `CAUGHT`; the first target (`fivem-lua`) stayed silent because its block also dates the citizenfx commits — recorded in the mutation's comment. Run -> `22/23 defect classes detected` locally (MISSED only `C3 lua syntax`, luac absent here).
## 3. Backfill

- [x] 3.1 The 14 blocks gain `Probed on 2026-08-06 (change <id>, commit <sha>).` with the id/sha the
      history gives for each; no pinned version changes
      Evidence: 14 blocks end with `Probed on 2026-08-06 (change \`<id>\`, commit \`<sha>\`).` — `harden-r3f-skills`/`a18758c` ×10, `pin-probed-skills`/`9afef67`, `onboard-k8s-tune-resources`/`d1e22a4`, `add-observability-skill`/`60eb0be`, `add-async-lane-rule`/`c27ca79`; the backfill script asserted the set of pinned `tool version` tokens unchanged per file; `git diff -- skills` touches no `version:` line.
- [x] 3.2 README validator paragraph and selftest count (22 → 23)
      Evidence: `README.md:878-879` -> `every skill states what it was verified against — with the date it was probed — or that it does not depend on a tool version (C5)`; `:913` -> `23/23 defect classes detected`.
- [x] 3.3 `./generate.sh`; wrappers in sync
      Evidence: `bash generate.sh` -> `git status --porcelain --untracked-files=all | grep -c '^??'` -> 0; 45 paths changed before commit (3 scripts/README + 14 skills + wrappers).
## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
      Evidence: entry point `python3 scripts/validate-skills.py` on the backfilled catalog -> `skills checked: 35   findings: 0`; on a copy with observability's date removed -> `[C5 no version pin] 'Verified against' block carries no date (YYYY-MM-DD) — a pin with no date does not say when it stopped being trustworthy`; entry point `python3 scripts/selftest-validate-skills.py` -> `CAUGHT  C5 no version pin (undated block)`, `22/23`.
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
      Evidence: 1/1 undated block had to fire and did (observability, date removed); 35/35 skills had to stay silent after the backfill and did; 14/14 blocks gained a date; 0/14 pinned versions changed; 3/3 declaration-form skills stayed silent with no date rule applied to them; 1/1 pre-existing local miss unchanged (`C3 lua syntax`).
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did
      Evidence: One thing behaved differently than expected: the first selftest target, `fivem-lua`, stayed silent with `Probed on 2026-09-05` replaced because its block also carries `(2026-09-02)` and `(2026-08-17)` for the citizenfx commits — the rule asks for any ISO date in the block, as designed, so the mutation moved to `observability`, whose file carries exactly one. Also: the first S.1 probe edited a string that the 97-column wrap had split across two lines and therefore changed nothing; the probe was redone on the bare date token.
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
      Evidence: The sentence added to each block states a date and two identifiers; the rule lives in the `skills-authoring` requirement and the C5 docstring (design.md Canonical Home, two rows, `already canonical`).
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown
      Evidence: No code example touched; detector -> `findings: 0`.
## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-pin-date-gate --strict` green
      Evidence: `openspec validate add-pin-date-gate --strict` -> `Change 'add-pin-date-gate' is valid`; `bash scripts/validate-rite.sh` -> `rite gate OK` (evidence gate 0 findings, spec-rite gate 0 findings).
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
      Evidence: `npx -y skills add solvelab/ai-skills --list | grep -c -E '^│    [a-z0-9-]+$'` -> `35`; `ls skills | wc -l` -> 35; nothing added, removed or renamed.
- [x] V.3 README / docs updated where the change alters catalog composition or usage
      Evidence: `README.md` validator paragraph and selftest count updated; catalog composition unchanged.
- [x] V.4 `openspec archive add-pin-date-gate --yes` after all groups above are `[x]`
      Evidence: `openspec archive add-pin-date-gate --yes` after PR #155 merged -> archived as `2026-09-06-add-pin-date-gate` (the CLI stamps the local date, which had rolled past midnight), specs updated; `openspec list` -> `No active changes found`.