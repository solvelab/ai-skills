## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at. Read at `4a865a2` on 2026-09-07:
      `scripts/selftest-validate-agents.py` (the `(label, check, plant)` tuple and the loop that
      asserts `f"[{check}" in out`), `scripts/selftest-validate-skills.py` (the shape being adopted —
      `expect, fragment = (entry[2] if len(entry) > 2 else (check, ""))` and
      `caught = expect.split()[0] in out and expect in out and fragment in out`),
      `scripts/validate-agents.py` (the `split()` helper whose offsets the four survivors sit on, and
      the two A1 messages those paths produce), and
      `openspec/specs/agents-catalog/spec.md` (the requirement this change modifies).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded.
      `python3 scripts/selftest-validate-agents.py` on the base -> `54/54 cases passed`. Both A1
      messages were read straight out of the validator, run against each document in a throwaway
      tree with the offset patched by hand. Document `---\n---\n`: offset 4 ->
      `[A1 frontmatter] no YAML frontmatter delimited by --- at the top of the file`, offset 3 ->
      `[A1 frontmatter] frontmatter is not a mapping`. Document `---\n\n---\n`, whose closing
      delimiter sits at index 4 exactly (`t.find("\n---\n", 4)` -> `4`, `... , 5)` -> `-1`):
      offset 4 -> `frontmatter is not a mapping`, offset 5 -> `no YAML frontmatter`. The first
      document does NOT separate 4 from 5 — from both it misses — which is why there are two.
      `cosmic-ray 8.7.0` is the tool the re-measurement uses, the same as #229.
- [x] E.3 Anything that could NOT be probed is written down as an open question — never stated as
      fact, never filled with a plausible substitute. One, and it is a property rather than a gap:
      `text[4:end]` mutated to `text[3:end]` prepends the newline at index 3 to the frontmatter, and
      YAML parses a document with a leading blank line identically, so no input separates the two.
      That is an equivalent mutant, stated as one rather than chased with a contrived case.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed: the same optional-fragment shape
      would let the accepting blocks at the bottom of `main()` assert what they accept rather than
      only that the run exited zero — a separate item, because it touches cases this change has no
      defect against.

## 2. The mechanism

- [x] 2.1 A case may carry an optional fourth element, the fragment, read the way the skills suite
      reads its optional third; a case without one behaves exactly as today
- [x] 2.2 The fragment is asserted **in addition** to the check id, never instead of it
- [x] 2.3 A missing fragment reports the finding that was actually produced, so the failure is
      readable without re-running by hand

## 3. The cases that need it

- [x] 3.1 The degenerate document — delimiters present, nothing between them — asserts the "no YAML
      frontmatter" message, which separates the offset `4` from the offset `3`
- [x] 3.2 A document whose frontmatter opens with an empty line asserts its message, which separates
      the offset `4` from the offset `5`
- [ ] 3.3 Mutation re-run under the conditions of #229 and the number recorded beside the 45

## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact is a gate's self-test and its entry point is being run.
      `python3 scripts/selftest-validate-agents.py` -> `55/55 cases passed`, and
      `python3 scripts/validate-agents.py` on the real tree -> `agents checked: 3   findings: 0`.
      The mechanism was then exercised against the defects it exists to catch, by patching the
      offset by hand and re-running: offset `4 -> 3` ->
      `OTHER  A1  frontmatter delimiters with nothing between them — expected the finding to carry
      'no YAML frontmatter'`, `54/55 cases passed`; offset `4 -> 5` ->
      `OTHER  A1  frontmatter that opens with an empty line — expected the finding to carry
      'not a mapping'`, `54/55 cases passed`. Both were green before this change.
- [x] S.2 Case matrix measured, as counts: suite 54 -> **55/55**; new cases that had to fire and
      did, **2/2**; offset mutants the fragment had to kill and did, **2/2** (`find(..., 3)` and
      `find(..., 5)`); existing cases that had to keep passing and did, **54/54**; mutation over
      `scripts/validate-agents.py` under the conditions of #229 (`cosmic-ray 8.7.0`, the self-test
      as runner, default operators): **229 mutants / 45 survivors / 80.3%** before,
      **229 / 37 / 83.8%** after. Survivors on the frontmatter split offsets: **4 -> 2**, plus one
      the previous run had miscounted (below).
- [x] S.3 Two things, and the first is a correction to what #229 published. **(1) One of the four
      offset survivors was miscounted there.** `text[end | 5:]` is a `BitOr` mutation, and the
      classifier that grouped survivors put every `BitOr` in the "type annotation, no runtime effect"
      bucket before looking at the line — so #229's four were `find(..., 3)`, `find(..., 5)`,
      `text[3:end]` and `text[end + 4:]`, and `end | 5` was hidden in the wrong bucket. It is a real
      survivor and it is named here. **(2) The two that remain are equivalent mutants, and this was
      proved rather than assumed.** `text[3:end]` prepends the newline at index 3 to the frontmatter,
      which YAML parses identically; `text[end + 4:]` prepends it to the body, where `.strip()`
      removes it for the length check and `re.M` makes the heading regex indifferent. Both were run
      against the real tree and produced output byte-identical to the original, with `55/55` on the
      suite. Nothing can kill them, and a case that tried would be asserting an implementation detail
      no behaviour depends on. `end | 5` is distinguishable in principle — on two of the three
      published agents `end | 5 != end + 5` — but nothing notices, because the body it produces still
      clears the length limits and still carries the heading; killing it needs a document whose
      frontmatter length has a chosen bit pattern, which is a test written to the mutation operator
      rather than to a defect. That is the anti-pattern `bug-hunter` names beside the technique, and
      it is declined here on purpose.

## 5. Quality Gates (MANDATORY)

- [x] Q.1 No SKILL.md is touched — `validate-skill-version.py` -> `0 skill(s) changed`, and
      `validate-skills.py` -> `skills checked: 38   findings: 0`
- [x] Q.2 The one file this change edits is a Python self-test, written in English
- [x] Q.3 No `description` and no trigger surface is touched
- [x] Q.4 No doctrine restated; the equivalent-mutant rule stays in `bug-hunter` and is applied,
      not copied
- [x] Q.5 No skill example is touched; the new case labels and comments are English

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate assert-agent-findings-by-fragment --strict` ->
      `Change 'assert-agent-findings-by-fragment' is valid`; `bash scripts/validate-rite.sh` ->
      `rite gate OK`
- [x] V.2 `npx -y skills add . --list` -> 44 skills, the 38 under `skills/` plus the 6 under
      `.claude/skills/`; nothing added, removed or renamed
- [x] V.3 No composition or usage change; `README.md:592` describes the gate and names no count
- [ ] V.4 `openspec archive assert-agent-findings-by-fragment --yes` — left for after the merge,
      as in #233, #224 and #208; the pull request reports the change as active and names this as what
      closes it
