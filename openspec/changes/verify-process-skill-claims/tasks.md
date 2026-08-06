## 1. Probe

- [x] 1.1 Extract every `gh`/`openspec` command and flag from the six process skills' code blocks and
      inline code
- [x] 1.2 Probe each subcommand and flag against the installed tool via `--help` (non-destructive)
- [x] 1.3 Record the result: 28/28 claims clean against gh 2.92.0 and openspec 1.6.0

## 2. conventional-commit (1.3.0)

- [x] 2.1 Add a release-impact column to the type table; call out `!`/`BREAKING CHANGE` as major
- [x] 2.2 Document the `security` trap and the non-shipping types, with the repo-history evidence
- [x] 2.3 Document repo-specific `releaseRules` overrides using this catalog's config as the example
- [x] 2.4 Note that the release tooling treats the gitmoji as optional while this convention does not
- [x] 2.5 Bump `metadata.version` to 1.3.0

## 3. backlog (1.0.1)

- [x] 3.1 State the item-add propagation lag and its exact error next to the id-capture recipe
- [x] 3.2 Bump `metadata.version` to 1.0.1

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on both touched skills
- [x] Q.2 All touched content in English (catalog locale)
- [x] Q.3 Triggers and "Do NOT use for" boundaries unchanged
- [x] Q.4 No duplicated doctrine: release impact lives only in `conventional-commit`; Projects v2
      recipes only in `backlog/references/gh-projects.md`
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 No description promises a policy its body contradicts
- [x] Q.7 No README change needed — no skill added, removed or repurposed

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate verify-process-skill-claims --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `scripts/validate-skills.py` reports 0 findings
- [x] V.5 `scripts/selftest-validate-skills.py` detects 10/10
- [ ] V.6 `openspec archive verify-process-skill-claims --yes` after review
