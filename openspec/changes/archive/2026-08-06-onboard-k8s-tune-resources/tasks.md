## 1. Promote the orphan

- [x] 1.1 Create `skills/k8s-tune-resources/SKILL.md` from the orphan wrapper
- [x] 1.2 Catalog-conformant frontmatter: folded description, `solvelab`, semver, `devops`, MIT,
      `compatibility`
- [x] 1.3 Delete `claude/skills/k8s-tune-resources/` so `generate.sh` owns every tree
- [x] 1.4 Run `./generate.sh`; confirm the claude/codex/cursor/copilot/plugins variants appear

## 2. Make the operation survivable

- [x] 2.1 Wire `DRY_RUN` into the Step 2 loop, defaulting to `1`, reporting `WOULD_CHANGE` + diffstat
- [x] 2.2 Verify the loop with `bash -n` after substituting the placeholders
- [x] 2.3 Document the per-repo rollback and forbid fleet-wide force-push
- [x] 2.4 State the blast radius (51 repos from one label) and the two commands that size a run
- [x] 2.5 Add the dry-run banner to the header

## 3. Remove published operational detail

- [x] 3.1 Delete the cluster node addresses, customer org slug and app-name prefixes
- [x] 3.2 Genericise the remaining examples in *Required inputs*
- [x] 3.3 Add the standing rule that run values are inputs, not doctrine
- [x] 3.4 Grep every tree to confirm none of the removed values survive

## 4. Prevent recurrence

- [x] 4.1 Add validator check C7: every directory under `claude/skills/` and `codex/skills/` has a
      canonical `skills/<name>/SKILL.md`
- [x] 4.2 Extend the self-test to inject an orphan wrapper; 11/11 classes detected
- [x] 4.3 Probe and pin the tools the skill prescribes (`kubectl v1.36.1`, `git 2.47.3`)

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on the new skill
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Description carries its triggers and a "Do NOT use for" boundary
- [x] Q.4 No duplicated doctrine: no overlap with `helm-migration`; commit format links
      `conventional-commit`
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 Description states no policy the body contradicts
- [x] Q.7 README gains the `k8s-tune-resources` row in the devops section

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate onboard-k8s-tune-resources --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `scripts/validate-skills.py` reports 0 findings across 31 skills
- [x] V.5 `scripts/selftest-validate-skills.py` detects 11/11 injected defect classes
- [x] V.6 `openspec archive onboard-k8s-tune-resources --yes` after review
