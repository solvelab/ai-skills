## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at. Read at `8582522` on 2026-09-07:
      `skills/bug-hunter/SKILL.md` (2.4.0, 11 checklist classes),
      `skills/bug-hunter/references/track-python-pytest.md`,
      `skills/bug-hunter/references/track-fivem-lua.md`,
      `skills/bug-hunter/references/track-dotnet-plugin.md`,
      `agents/bug-hunter-analyst.md`, `openspec/specs/skills-catalog/spec.md` (line 57 fixes the
      methodology's home), `openspec/specs/skills-authoring/spec.md` (the measured-claim and
      command-with-its-step requirements), `scripts/validate-agents.py`,
      `scripts/selftest-validate-agents.py`, `skills/code-locale/references/check-identifier-locale.py`.
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded.
      `uv run --with cosmic-ray cosmic-ray --version` -> `cosmic-ray, version 8.7.0`.
      `uv run --with hypothesis python -c "import hypothesis; print(hypothesis.__version__)"` ->
      `6.167.1`. `uv run --with mutmut mutmut --help` -> `FileNotFoundError: Could not figure out
      where the code to mutate is. Please specify it by adding "source_paths=code_dir" in setup.cfg`
      — which is why the track names mutmut's default as the wrong command for this repository.
      `cosmic-ray init cr.toml session.sqlite` over `validate-agents.py` with
      `test-command = "python3 selftest-validate-agents.py"` -> 205 mutants; `cosmic-ray exec` ->
      `KILLED 151, SURVIVED 54` (mutation score 73.7%) while the suite reported `33/33 cases passed`.
      Hand-check of one survivor: `DESCRIPTION_MAX = 5000` -> `5001`, rerun -> `33/33 cases passed`.
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute.
      Not probed: metamorphic testing and fault injection, neither exercised during this change and
      therefore prescribed nowhere; mutation and property tooling for Lua and for .NET, which is why
      `track-fivem-lua.md` and `track-dotnet-plugin.md` are left untouched; and whether the mutation
      score of 73.7% generalises past this one module — it is published with its conditions, not as
      a catalog-wide figure. Recorded in `design.md` under *Open questions*.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed. Two follow-ups, neither done here:
      (a) `skills/code-locale/references/check-identifier-locale.py` — `split_prose()` collapses a
      string literal to a single space rather than blanking it in place, so `code` is not positional;
      the docstring's word "blanked" reads as positional and no caller depends on columns today, so
      this is a contract wording gap, not a defect; (b) `scripts/selftest-validate-agents.py` does
      not pin the values of `DESCRIPTION_MAX` / `BODY_MAX` or the boundary comparisons, which is what
      20 of the 54 surviving mutants sit on. Both belong to their own backlog items.

## 2. Doctrine

- [ ] 2.1 `skills/bug-hunter/SKILL.md`: new section separating enumerate / generate / score, each
      conditional layer carrying its condition and a `lean:` ceiling with the upgrade trigger
- [ ] 2.2 The measured yields written where they motivate the rule — property-based on the catalog's
      own tokenizer, mutation on the catalog's own validator — with the conditions of each
- [ ] 2.3 `skills/bug-hunter/references/track-python-pytest.md`: the working command scoped to the
      changed module, and the plausible-but-wrong command named with the failure it produces
- [ ] 2.4 `agents/bug-hunter-analyst.md`: the output contract gains candidate invariants without
      touching `ATTACKS`, `TESTS TO WRITE` or `TRIED AND FOUND NOTHING`
- [ ] 2.5 `metadata.version` 2.4.0 -> 2.5.0; `./generate.sh` run so the generated trees match

## 3. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 4. Quality Gates (MANDATORY)

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

## 5. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate <id> --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive <id> --yes` after all groups above are `[x]`
