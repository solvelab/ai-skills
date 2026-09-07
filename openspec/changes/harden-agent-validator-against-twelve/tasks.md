## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at. Read at `501b3cf` on 2026-09-07:
      `scripts/validate-agents.py` (checks A1-A7; `NAME_RE` at :49, `WHEN_TO_INVOKE` at :53, the
      limit constants at :79-80, the parse handler at :130-134, the membership tests at :168 and
      :171, the blank-tool test at :179, the A6 search at :186, the globs at :213, :214 and :242),
      `scripts/selftest-validate-agents.py` (33 cases), `scripts/validate-skills.py` (:408 and :592,
      the same bare `except _yaml.YAMLError` over `safe_load`),
      `openspec/specs/agents-catalog/spec.md` (the two requirements this change modifies) and
      `.github/workflows/ci.yml` (:136 and :142, where both gates run).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded.
      Each finding was reproduced first-hand in a throwaway tree holding only `scripts/` and one
      conforming agent, `python3 scripts/validate-agents.py` after planting one defect at a time:
      `##` alone plus the paragraph -> `agents checked: 1   findings: 0`; the heading only inside a
      fence -> `agents checked: 1   findings: 0`; `model: [inherit]` ->
      `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`;
      `tools: ["Read", "   "]` -> `agents checked: 1   findings: 0`;
      `tools: ` + 500 nested flow sequences -> `RecursionError: maximum recursion depth exceeded`;
      `model: [inherit]` plus a second broken `agents/zz-broken.md` -> `zz-broken` appears 0 times in
      the output; `agents/rogue.MD` holding garbage -> `agents checked: 1   findings: 0`;
      an orphan at `plugins/testing/agents/sub/ghost.md` -> `agents checked: 1   findings: 0`.
      `NAME_RE` measured directly: a 50-character name matches, 51 does not, 2 does not, and a
      50-character name followed by `\n` matches — a 51-character value accepted by a `$` anchor.
- [x] E.3 Anything that could NOT be probed is written down as an open question — never stated as
      fact, never filled with a plausible substitute. There is one, and it came back **refuted**
      rather than unprobed. Finding 10 claimed a duplicate frontmatter key could make the gate judge
      a value the harness does not use. Probed both directions in a scratch project with a
      `dup-probe` agent driven by a fresh `claude -p`: with `tools: ["Read"]` then
      `tools: ["Read", "Bash"]` the agent reported `Read, Bash`; with the order reversed it reported
      `Read`. PyYAML reports the same value in both cases. The harness takes the last key, exactly as
      PyYAML does, so there is no divergence to gate and no code is written for finding 10 — adding a
      check with no defect behind it is what `skills-authoring` forbids.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed: (a) the `split_prose()` contract
      wording in `skills/code-locale/references/check-identifier-locale.py`, where a string literal is
      collapsed to one space while the docstring says "blanked", which reads as positional — no caller
      depends on columns today; (b) whether mutation testing should become a CI gate of this
      repository, which the doctrine deliberately does not decide.

## 2. The two crashes

- [x] 2.1 A scalar field declared as a collection becomes a finding naming the field, checked by
      shape before the membership test, never by wrapping the test in a handler
- [x] 2.2 `RecursionError` is caught beside `yaml.YAMLError` around the parse call in
      `scripts/validate-agents.py`, and in `scripts/validate-skills.py` at `:408` and `:592`
- [x] 2.3 A case with two agents, the first defective, proves the run reaches the second

## 3. The two false GREENs

- [x] 3.1 `WHEN_TO_INVOKE` stops matching a newline between the hashes and the text
- [x] 3.2 Fenced blocks are removed before the A6 search, the way the sibling validator already does

## 4. Discovery and privilege

- [x] 4.1 Canonical and generated files are discovered regardless of the case of their suffix
- [x] 4.2 An orphan is found at any depth below `plugins/<group>/agents/`
- [x] 4.3 A whitespace-only entry in `tools` is reported
- [x] 4.4 `NAME_RE` stops accepting a trailing newline

## 5. Boundary witnesses

- [x] 5.1 `DESCRIPTION_MIN`, `DESCRIPTION_MAX`, `BODY_MIN` and `BODY_MAX` each gain an accepted case
      at the value, a rejected case one past it and an accepted case one inside it
- [x] 5.2 The mutation measurement is re-run under the conditions of the first one and the number is
      recorded beside today's 54, whatever it is

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point — both artifacts are gates, and
      their entry point is being run. `python3 scripts/validate-agents.py` on the real tree ->
      `agents checked: 3   findings: 0`; `python3 scripts/selftest-validate-agents.py` ->
      `53/53 cases passed`; `python3 scripts/selftest-validate-skills.py` ->
      `28/28 defect classes detected`. Each finding was also planted one at a time in a throwaway
      tree and the fixed gate answered, e.g. `##` alone -> `[A6 body] no ## When to invoke section`,
      `model: [inherit]` -> `[A4 model/color] model is a list, not one of ['haiku', 'inherit',
      'opus', 'sonnet']`, nested YAML -> `[A1 frontmatter] YAML nesting exhausts the parser`,
      `agents/rogue.MD` -> `[A1 frontmatter] no YAML frontmatter delimited by ---`, nested orphan ->
      `[A7 layout] plugins/testing/agents/sub/ghost.md has no source`. The `RecursionError` case was
      run against the PRE-fix validator taken from `origin/master`, which answered
      `rc=1 traceback=True`, and against the fixed one, which answered
      `rc=1 traceback=False finding_novo=True` — the case is a real regression gate, not a
      restatement of current behaviour.
- [x] S.2 Case matrix measured, as counts: `selftest-validate-agents` 33 -> **53/53**, of which 14
      new cases had to fire and did and 5 new accepting blocks had to stay silent and did;
      `selftest-validate-skills` 27 -> **28/28**; findings reproduced before the fix and re-run
      after it, **9/9** now reported; the pre-fix regression proof, **1/1**; mutation over
      `scripts/validate-agents.py` under the conditions of the first measurement (`cosmic-ray
      8.7.0`, the self-test as runner, default operators): **205 mutants / 54 survivors** before,
      **229 / 46** after — survivors on the limit constants and on the boundary comparisons
      **20 -> 0**, with 4 survivors remaining on the frontmatter split offsets and 16 on `|` in type
      annotations, which have no runtime effect.
- [x] S.3 What escaped or behaved differently than expected is named here. **Two escapes, both mine,
      both caught by the layers this catalog just published.** (1) The discovery helper
      `agent_files()` filtered on `is_file()`, which is False for a dangling symlink, so it silently
      stopped judging the very input A1 owns; the existing self-test caught it immediately
      (`51/52`, `MISSED A1 a dangling symlink`) and the helper now documents why the filter is not
      there. (2) The self-test helper `sized()` built the body BEFORE `.strip()`, so asking for 19
      characters produced 17 — the suite looked like it had a witness at `BODY_MIN` and did not, and
      the mutant `BODY_MIN = 20 -> 19` survived the second measurement. **The suite did not catch
      that; the mutation score did**, which is the exact claim the `bug-hunter` scoring layer makes,
      landing on the change written immediately after it. Fixed, asserted on the stripped form, and
      the mutant is dead in the third run.

## 7. Quality Gates (MANDATORY)

- [x] Q.1 No SKILL.md is touched by this change — `python3 scripts/validate-skill-version.py` ->
      `0 skill(s) changed, 0 with content changes`, and `python3 scripts/validate-skills.py` ->
      `skills checked: 38   findings: 0` confirms none drifted
- [x] Q.2 Everything this change writes is English: the two gates, both self-tests and the change
      itself. `check-identifier-locale.py --diff -` over the staged diff -> `findings: 0`
- [x] Q.3 No `description` and no trigger surface is touched, so routing is unchanged
- [x] Q.4 No doctrine restated: D2 applies `lean-code`'s root-cause rule by linking it, and the
      adversarial method stays in `bug-hunter`; the table is in design.md
- [x] Q.5 The code this change writes is Python in `scripts/`, not a skill example; identifiers,
      helper names and comments are English

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate harden-agent-validator-against-twelve --strict` ->
      `Change 'harden-agent-validator-against-twelve' is valid`; `bash scripts/validate-rite.sh` ->
      `rite gate OK`
- [x] V.2 `npx -y skills add . --list` -> 44 skills, the 38 under `skills/` plus the 6 under
      `.claude/skills/`; this change adds, removes and renames none
- [x] V.3 No composition or usage change. `README.md:592` describes what the agent gate checks and
      names no count, so it stays accurate as written
- [ ] V.4 `openspec archive harden-agent-validator-against-twelve --yes` — left for after the merge,
      the way #224, #208, #203, #195 and the rest of this repository's rites have closed; the pull
      request reports the change as active and names this as what closes it
