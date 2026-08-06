## 1. Measure the actual exposure

- [x] 1.1 Scan every blob in the full history (1879) for credential classes
- [x] 1.2 Record the result: no keys, tokens, private keys, JWTs or public addresses
- [x] 1.3 Measure the rewrite's cost: 2 commits carry the values, 0 forks, 0 stars, 40 published tags
- [x] 1.4 Establish that a force-push does not remove published objects from GitHub

## 2. Scanner

- [x] 2.1 Working-tree mode that gates CI on credential classes
- [x] 2.2 `--history` mode that reports without gating
- [x] 2.3 Report private addresses as operational detail, never as a failure
- [x] 2.4 Wire the gate into the CI validate job

## 3. Clean the tree

- [x] 3.1 Replace the example connection string with an unmistakable placeholder
- [x] 3.2 Regenerate wrappers so the plugin copies carry the fix
- [x] 3.3 Working-tree scan reports no credentials
- [x] 3.4 `documentation` bumped to 3.0.1

## 4. Record the decision

- [x] 4.1 Proposal states the rewrite was declined, with cost and why it would not achieve the goal
- [x] 4.2 Proposal names the owner's half of the job if they still want the purge

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on the touched skill
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers unchanged
- [x] Q.4 No duplicated doctrine: the no-run-values rule stays in `k8s-tune-resources`
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 No description promises a policy its body contradicts
- [x] Q.7 README documents both scanner modes and why they differ

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate close-secret-scanning --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync
- [x] V.4 `scripts/validate-skills.py` 0 findings across 32 skills
- [x] V.5 `scripts/selftest-validate-skills.py` 12/12
- [x] V.6 `scripts/scan-secrets.py` reports no credentials in the working tree
- [x] V.7 `openspec archive close-secret-scanning --yes` after review
