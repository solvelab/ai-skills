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

- [x] 2.1 `skills/bug-hunter/SKILL.md`: new section separating enumerate / generate / score, each
      conditional layer carrying its condition and a `lean:` ceiling with the upgrade trigger
- [x] 2.2 The measured yields written where they motivate the rule — property-based on the catalog's
      own tokenizer, mutation on the catalog's own validator — with the conditions of each
- [x] 2.3 `skills/bug-hunter/references/track-python-pytest.md`: the working command scoped to the
      changed module, and the plausible-but-wrong command named with the failure it produces
- [x] 2.4 `agents/bug-hunter-analyst.md`: the output contract gains candidate invariants without
      touching `ATTACKS`, `TESTS TO WRITE` or `TRIED AND FOUND NOTHING`
- [x] 2.5 `metadata.version` 2.4.0 -> 2.5.0; `./generate.sh` run so the generated trees match

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded. Both artifacts were staged into the live plugin cache
      (`~/.claude/plugins/cache/ai-skills/ai-skills-testing/3.0.1/`) and driven from a fresh
      process, then the cache was restored to its pre-proof state. **Agent** — entry point
      `claude -p` -> `Agent(subagent_type: ai-skills-testing:bug-hunter-analyst)` against
      `scripts/validate-skill-version.py`; observed section headers at lines `1 ATTACKS`,
      `38 TESTS TO WRITE`, `91 INVARIANTS WORTH GENERALIZING`, `114 TRIED AND FOUND NOTHING`, with
      the new section reading `For every frontmatter block ci.yml:109 accepts, version_of() returns
      a string semver_key() parses ... attacks 1, 6 and 7 are all points in that gap`. **Skill** —
      entry point `claude -p` -> `Skill(ai-skills-testing:bug-hunter)`; observed
      `1. Enumerate, generate, score.` and, quoted back verbatim,
      `lean: enumeration only -> add a property when a function has an invariant statable in one
      sentence and an input space too large to enumerate.`
- [x] S.2 Case matrix measured, as counts: contract sections that had to appear and did, 4/4 in the
      fresh-process run; skill questions answered correctly from the loaded body, 4/4; invariants
      returned by the new section, 3, each generalizing 1 to 3 of the attacks the same report had
      listed separately; runs in which the new section appeared, 1/2 — the failing one is the
      in-session dispatch and its cause is named in S.3; mutation survivors independently re-derived
      by the analyst without being told to trust the number, 1/1 (it measured that the suite's only
      body lengths are 17, 85 and 163, so `BODY_MAX` has zero witnesses).
- [x] S.3 What escaped or behaved differently than expected is named here. **One escape, and it is
      about how this catalog is proved, not about the change**: an agent definition edited on disk
      is NOT picked up by the session that is already running — the harness loads agent definitions
      at session start. The first field-proof run therefore executed the OLD contract while reading
      the new file, and looked like the new section simply failing to fire. It was settled by asking
      that agent to quote its own contract: it listed three sections and six `How you work` bullets,
      neither of them the new ones. Every later proof was run from a fresh `claude -p` process, which
      does reload. Nothing else behaved unexpectedly: the property-based probe's own fifth invariant
      failed and the failure was a wrong premise about the contract, recorded in E.4 as a follow-up
      rather than patched here.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md — `python3 scripts/validate-skills.py` ->
      `skills checked: 38   findings: 0`, which is the check that owns every field in this box
- [x] Q.2 All touched skill content in English. The issue and the commit are Portuguese, the skill
      and the agent are English; `git diff origin/master --unified=0 | python3
      skills/code-locale/references/check-identifier-locale.py --diff -` -> `findings: 0`
- [x] Q.3 Triggers unchanged by this change — the `description` frontmatter is byte-identical to
      2.4.0, so the routing surface and the existing "Do NOT use for" boundaries against
      `api-resilience-testing` and `tdd` are untouched
- [x] Q.4 No duplicated doctrine. The new section links `api-resilience-testing` for schema-driven
      generation on a REST surface instead of describing it, and uses `lean-code`'s `lean:` marker
      rather than restating its ladder; the full table is in design.md
- [x] Q.5 The two new code examples in `references/track-python-pytest.md` — the `hypothesis`
      property and the `cosmic-ray` TOML — carry English identifiers, keys and file names only

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate update-bug-hunter-generation-and-scoring --strict` ->
      `Change 'update-bug-hunter-generation-and-scoring' is valid`; `bash scripts/validate-rite.sh`
      -> `rite gate OK`
- [x] V.2 `npx -y skills add . --list` -> 44 skills listed, which is the 38 under `skills/` plus the
      6 under `.claude/skills/`; no skill added, removed or renamed by this change
- [x] V.3 Composition unchanged, so no discovery text moves; the two README rows that describe what
      these artifacts return were corrected — the agent row now names the invariants section, and the
      skill row now reads `enumerate / generate / score`
- [ ] V.4 `openspec archive update-bug-hunter-generation-and-scoring --yes` — deliberately left for
      after the merge, the way this repository has closed its previous rites (issues #192, #211); the
      pull request reports the change as active and names this as what closes it
