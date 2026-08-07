## 1. Evidence & Sources (MANDATORY)

<!-- Always the FIRST group: probe before you write. Record the COMMAND and a fragment of its
     RAW OUTPUT, never a conclusion — a row a reviewer can re-run in two seconds is the only kind
     worth writing. A claim with no evidence is a guess: drop the claim, or go get the evidence.
     Doctrine: the verify-before-claiming skill. -->

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled. Read on
      2026-08-07 at `b9184a4`: `.github/workflows/ci.yml` (the step order the two new steps slot
      into, after the secret scan and before the rite gate), `scripts/validate-skills.py` (the
      `add()`/`findings`/exit-1 shape cloned here), `scripts/selftest-validate-skills.py` (the
      inject-one-defect-per-check pattern), `scripts/scan-secrets.py`, `.gitignore` (the bytecode
      rules H1 mirrors), `README.md:682-690` (the enforcement prose the new paragraph joins).
- [x] E.2 Every claim this change asserts was probed, not assumed:
      `python3 scripts/validate-repo-hygiene.py` on the clean tree -> `repo hygiene: 0 findings`,
      `exit=0`.
      `--selftest` -> `CAUGHT H1 tracked bytecode` / `CAUGHT H2 stale count` / `2/2 defect classes
      detected`.
      H1 probed live on the real tree, not only in the self-test: forcing
      `claude/global/hooks/__pycache__/live.cpython-314.pyc` in with `git add -f` produced
      `H1 tracked bytecode: ... is tracked — untrack it` and `exit=1`; after `git rm --cached` the
      tree returned to `0 findings`.
      H2 probed live: editing `all 33 skills` to `all 41 skills` produced
      `H2 stale count: README.md:82 claims 41, `ls skills | wc -l` says 33` and `exit=1`; after
      `git checkout README.md` the tree returned to `0 findings`.
      `ls skills | wc -l` -> `33`. `python3 --version` -> `Python 3.14.5`.
- [x] E.3 Anything that could NOT be probed is written down rather than stated as fact. Two items,
      both declared inside the checks rather than in prose only: H1 cannot see a blob already
      published in a past release, and cannot see non-Python compiled artifacts; H2 cannot see a
      count phrased outside the literal `all N` shape or living in a third file. Neither limit is
      hypothetical — the second one is the exact miss that happened during the sweep that first
      hunted these counts.
- [x] E.4 Scope check: this change does only what the proposal asked. Noticed and **not** performed:
      broadening H1 to other artifact classes (nothing else has leaked), and templating the README
      counts (rejected under design.md Decisions with a reason, not deferred again).

## 2. The gate

- [x] 2.1 `scripts/validate-repo-hygiene.py` — H1 no tracked compiled artifact, using `git ls-files`
      so a forced-in file fires and an ignored working-directory artifact does not
- [x] 2.2 H2 — every `all N` count in `README.md` and `.claude-plugin/marketplace.json` equals the
      number of directories under `skills/`
- [x] 2.3 Each check carries a `KNOWN LIMIT` paragraph naming what it does not cover
- [x] 2.4 `--selftest` mode injecting one defect per check into a throwaway clone
- [x] 2.5 Standard library only — no new CI dependency

## 3. Wiring

- [x] 3.1 `.github/workflows/ci.yml` — gate step plus self-test step, after the secret scan
- [x] 3.2 `README.md` — the enforcement section describes the gate, why each check exists, and its
      blind spots

## 4. Quality Gates (MANDATORY)

<!-- Adversarial review of the skills touched — not happy-path. Every skill added or edited
     by this change gets checked against the skills-authoring spec. Keep the group number
     as the second-to-last group. -->

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: no `skills/` file is touched, so the
      requirement is vacuously satisfied and `validate-skills.py` still exits 0
- [x] Q.2 All touched content in English (catalog locale)
- [x] Q.3 Description triggers testable: no skill description changes in this change
- [x] Q.4 No duplicated doctrine: no skill file is modified; the checks apply rules whose canonical
      homes are named in the design.md table rather than restating them
- [x] Q.5 The gate was tested **negatively and live**, not only by its own self-test: each defect
      was forced into the real working tree, the failure and its message were recorded, and the tree
      was restored to `0 findings`

## 5. Validation & Closure (MANDATORY)

<!-- Always the last group. "Done" is verifiable, not an opinion. -->

- [x] V.1 `openspec validate add-repo-hygiene-gates --strict` green
- [x] V.2 Catalog discovery intact: 33 skills, every `name` matching its directory, no orphan
      wrappers; `./generate.sh` leaves no diff
- [x] V.3 README / docs updated where the change alters enforcement
- [x] V.4 `openspec archive add-repo-hygiene-gates --yes` after all groups above are `[x]`
      — per this repo's established sequence this happens in a follow-up PR after the
      implementation PR merges (precedent: PR #61 shipped the active change, PR #62 archived it)
