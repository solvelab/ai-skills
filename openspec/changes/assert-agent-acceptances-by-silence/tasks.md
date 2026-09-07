## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at. Read at `28d0c80` on 2026-09-07:
      `scripts/selftest-validate-agents.py` — the baseline block
      (`if code != 0 or "findings: 0" not in out`), the six accepting blocks that assert only
      `if code != 0`, and the `OTHER` branch the fragment work of #232 added; and
      `openspec/specs/agents-catalog/spec.md`, the requirement this change modifies, nine scenarios,
      carried whole into the delta.
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded.
      `python3 scripts/selftest-validate-agents.py` on the base -> `55/55 cases passed`. The finding
      format the failure message parses was read from a real run rather than assumed: planting a
      short description gives `   [A3 description] 5 characters — the accepted range is 10-5000`, so
      the check id is the first bracketed token of the line.
- [x] E.3 Anything that could NOT be probed is written down as an open question — never stated as
      fact, never filled with a plausible substitute. There is none: everything this change asserts
      is in one file in this repository and was run.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed: `selftest-validate-skills.py`
      compares its copy against the source after the loop, which the agents suite does not do because
      it rebuilds the tree per case — worth a look only if that ever changes.

## 2. The rigour

- [x] 2.1 One acceptance helper asserting the exit code and `findings: 0`, in the shape the baseline
      block already uses
- [x] 2.2 All six accepting blocks go through it; none keeps the old assertion
- [x] 2.3 A failed acceptance names the check that fired, or says explicitly that none was found
- [x] 2.4 Demonstrated: an input that makes the validator report while exiting zero fails a block
      under the new rigour and passed under the old

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact is a self-test and its entry point is running it.
      `python3 scripts/selftest-validate-agents.py` -> `55/55 cases passed`, with the first line now
      `OK     a conforming agent produces zero findings is accepted`. Then, with the validator
      patched to report a finding **and still exit zero**:
      `FAIL   a conforming agent produces zero findings was not accepted cleanly — A9:`,
      `FAIL   A6  a tab after the heading hashes was not accepted cleanly — A9:`,
      `FAIL   A7  a generated copy with a source is not an orphan was not accepted cleanly — A9:`.
      The same run judged by the OLD rule: `code=0 -> regra antiga (code != 0) julgaria: ACEITA`.
- [x] S.2 Case matrix measured, as counts. Acceptances now judged by the helper, **8** across
      **5 call sites**: the baseline, the four limits at their value, the fifty-character name, the
      tab after the heading hashes, and the generated copy with a source. Acceptances that had to
      stay silent and did, **8/8** (`55/55 cases passed`, unchanged). Acceptances the new rigour had
      to fail under a validator that reports while exiting zero, **3/3 observed**, each naming the
      check. Cases added, **0** — this raises rigour, not coverage.
- [x] S.3 One thing, and it is a correction to the item that asked for this. The issue said "the
      six accepting blocks — the four limits at their value, the fifty-character name and the
      two-agent case". **The two-agent case is not an acceptance**: it asserts that the agent after a
      defective one IS reported, which is a rejection-shaped check and keeps its own assertion. And
      two acceptances the issue did not list were found while doing the work — the tab after the
      heading hashes, and the generated copy with a canonical source — plus the baseline block, whose
      condition is where the helper's rigour came from and which now goes through it too. The count
      is 8 acceptances at 5 call sites, not six blocks; the item's FR3 and its criterion were
      corrected rather than ticked as written. Nothing else behaved unexpectedly.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 No SKILL.md is touched — `validate-skill-version.py` -> `0 skill(s) changed`, and
      `validate-skills.py` -> `skills checked: 38   findings: 0`
- [x] Q.2 The one file edited is a Python self-test, written in English
- [x] Q.3 No `description` and no trigger surface is touched
- [x] Q.4 The opposite of duplication: the file held two rigours for one assertion and now holds
      one, taken from the stricter of the two
- [x] Q.5 No skill example is touched; the helper and its labels are English

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate assert-agent-acceptances-by-silence --strict` ->
      `Change 'assert-agent-acceptances-by-silence' is valid`; `bash scripts/validate-rite.sh` ->
      `rite gate OK`
- [x] V.2 `npx -y skills add . --list` -> 44 skills, the 38 under `skills/` plus the 6 under
      `.claude/skills/`; nothing added, removed or renamed
- [x] V.3 No composition or usage change; `README.md:592` names no counts and stays accurate
- [ ] V.4 `openspec archive assert-agent-acceptances-by-silence --yes` — left for after the merge,
      as in #236, #233 and #224; the pull request reports the change as active
