## 1. Evidence & Sources (MANDATORY)

<!-- Always the FIRST group: probe before you write. Record the COMMAND and a fragment of its
     RAW OUTPUT, never a conclusion — a row a reviewer can re-run in two seconds is the only kind
     worth writing. A claim with no evidence is a guess: drop the claim, or go get the evidence.
     Doctrine: the verify-before-claiming skill. -->

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled. Read on
      2026-08-06: `README.md:55`, `:82`, `:662`, `:668-673`; `.claude-plugin/marketplace.json:15`;
      `openspec/specs/skills-authoring/spec.md:24-34`; `.github/workflows/ci.yml:52-56`;
      `scripts/validate-skills.py:1-16` (the docstring that declares the checks).
- [x] E.2 Every number this change writes was re-derived by command, not copied from the report:
      `ls skills | wc -l` -> `33`.
      `grep -nE '^  C[0-9]' scripts/validate-skills.py` -> eight lines, `C1` through `C8`; the README
      sentence named only six of them, omitting `C7 no orphan wrapper skills` and `C8 no meta
      sections in SKILL.md`.
      `sed -n '54p' .github/workflows/ci.yml` ->
      `CATEGORIES="backend testing fivem game devops docs git process nui frontend tooling"` — 11
      values, against the 8 written in `openspec/specs/skills-authoring/spec.md:28`.
      `python3 scripts/selftest-validate-skills.py | tail -1` -> `12/12 defect classes detected`,
      which is why `README.md:688` was checked and left alone: that number is **not** drifted.
- [x] E.3 Anything that could NOT be probed is written down rather than stated as fact. One item:
      whether these counts should be generated instead of written is a design question that cannot
      be settled by a probe; it is recorded as an Open Question in design.md and as a follow-up,
      not decided in passing.
- [x] E.4 Scope check: this change does only what the proposal asked. A near-miss is recorded rather
      than buried — the first sweep used a pattern requiring the word `skills` after the number and
      **missed** `README.md:55` ("all 30." with no noun). The sweep was widened and re-run before any
      edit; that is why design.md records the derivation commands and not only the conclusions.

## 2. Corrections

- [x] 2.1 `.claude-plugin/marketplace.json` — bundle description count 27 -> 33
- [x] 2.2 `README.md:55` and `README.md:82` — 30 -> 33
- [x] 2.3 `README.md` — the validator runs eight checks, with `C7` and `C8` named in the prose that
      previously listed only six
- [x] 2.4 `openspec/specs/skills-authoring/spec.md` — controlled category set matches
      `.github/workflows/ci.yml`, via a `MODIFIED` requirement in this change's spec delta
- [x] 2.5 Each corrected number carries the command that produces it, so the next editor re-derives
      instead of re-copying

## 3. Quality Gates (MANDATORY)

<!-- Adversarial review of the skills touched — not happy-path. Every skill added or edited
     by this change gets checked against the skills-authoring spec. Keep the group number
     as the second-to-last group. -->

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: no `skills/` file is touched by this change,
      so the requirement is vacuously satisfied and `validate-skills.py` still exits 0
- [x] Q.2 All touched content in English (catalog locale)
- [x] Q.3 Description triggers testable: no skill description changes in this change
- [x] Q.4 No duplicated doctrine: no skill file is modified, so no cross-cutting rule moves or is
      restated (see the design.md Canonical Home table)
- [x] Q.5 The corrected category set was checked **against the gate**, not against memory: every one
      of the 11 values comes from `.github/workflows/ci.yml:54`, and every category in use by a
      shipped skill is inside it

## 4. Validation & Closure (MANDATORY)

<!-- Always the last group. "Done" is verifiable, not an opinion. -->

- [x] V.1 `openspec validate fix-catalog-drift --strict` green
- [x] V.2 Catalog discovery intact: 33 skills, every `name` matching its directory, no orphan
      wrappers; `./generate.sh` leaves no diff
- [x] V.3 README / docs updated — that is the entire change
- [x] V.4 `openspec archive fix-catalog-drift --yes` after all groups above are `[x]`
      — per this repo's established sequence this happens in a follow-up PR after the
      implementation PR merges (precedent: PR #61 shipped the active change, PR #62 archived it)
