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

- [ ] 2.1 A scalar field declared as a collection becomes a finding naming the field, checked by
      shape before the membership test, never by wrapping the test in a handler
- [ ] 2.2 `RecursionError` is caught beside `yaml.YAMLError` around the parse call in
      `scripts/validate-agents.py`, and in `scripts/validate-skills.py` at `:408` and `:592`
- [ ] 2.3 A case with two agents, the first defective, proves the run reaches the second

## 3. The two false GREENs

- [ ] 3.1 `WHEN_TO_INVOKE` stops matching a newline between the hashes and the text
- [ ] 3.2 Fenced blocks are removed before the A6 search, the way the sibling validator already does

## 4. Discovery and privilege

- [ ] 4.1 Canonical and generated files are discovered regardless of the case of their suffix
- [ ] 4.2 An orphan is found at any depth below `plugins/<group>/agents/`
- [ ] 4.3 A whitespace-only entry in `tools` is reported
- [ ] 4.4 `NAME_RE` stops accepting a trailing newline

## 5. Boundary witnesses

- [ ] 5.1 `DESCRIPTION_MIN`, `DESCRIPTION_MAX`, `BODY_MIN` and `BODY_MAX` each gain an accepted case
      at the value, a rejected case one past it and an accepted case one inside it
- [ ] 5.2 The mutation measurement is re-run under the conditions of the first one and the number is
      recorded beside today's 54, whatever it is

## 6. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 7. Quality Gates (MANDATORY)

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

## 8. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate <id> --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive <id> --yes` after all groups above are `[x]`
