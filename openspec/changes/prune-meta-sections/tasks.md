## 1. Measure

- [x] 1.1 Find every `How to Use` / `Trigger Test Cases` / `Prompt` / `Usage` section in the catalog
- [x] 1.2 Measure the per-invocation cost of each (85 lines across four skills)
- [x] 1.3 Check every trigger case against its own skill's description before deleting anything

## 2. Preserve what carried information

- [x] 2.1 `helm-migration`: fold the four uncovered anti-triggers into the description as a
      `Do NOT use for …` clause — the skill had no routing guidance of any kind
- [x] 2.2 Confirm `backlog`, `execute-backlog` and `claude-statusline` descriptions already cover
      every case in their blocks

## 3. Remove and enforce

- [x] 3.1 Delete the meta sections from all four skills
- [x] 3.2 Add validator check C8 with its reasoning in the check itself
- [x] 3.3 Extend the self-test to inject a meta section — 12/12 classes detected
- [x] 3.4 Bump versions: helm-migration 2.2.0, backlog 1.1.1, execute-backlog 1.3.1,
      claude-statusline 1.1.1

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on all four skills
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers preserved — moved to the description where they act, never dropped
- [x] Q.4 No duplicated doctrine: the rule lives in `skills-authoring`, enforced by C8, not restated
      in any skill
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 No description promises a policy its body contradicts
- [x] Q.7 No README change — no skill added, removed or repurposed

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate prune-meta-sections --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `scripts/validate-skills.py` 0 findings across 31 skills
- [x] V.5 `scripts/selftest-validate-skills.py` 12/12
- [ ] V.6 `openspec archive prune-meta-sections --yes` after review
