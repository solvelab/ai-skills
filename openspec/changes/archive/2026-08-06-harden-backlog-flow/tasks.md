## 1. Run the flow for real

- [x] 1.1 Execute `execute-backlog` steps 1-3 against issue #28, groomed by `backlog` the same day
- [x] 1.2 Record each friction point with the command that produced it
- [x] 1.3 Verify the drift check: the issue's ten line-count claims still hold (0/10 divergent)
- [x] 1.4 Check the suspicion that the board columns are undefined — found specified in
      `board-sync.md`; record as unfounded

## 2. execute-backlog (1.3.0)

- [x] 2.1 Step 2 resolves linked PRs from the issue's link graph and points at the recipe
- [x] 2.2 Add *Finding the item's PRs* to `references/board-sync.md` with both queries
- [x] 2.3 Forbid `gh pr list --search "<n> in:body"`, with the measured 3-false-positives result and
      the miss direction
- [x] 2.4 Bump `metadata.version` to 1.3.0

## 3. backlog (1.1.0)

- [x] 3.1 Document the duplicate-check punctuation trap with the measured four-way comparison
- [x] 3.2 Document the optional `columns:` block in `references/backlog-config.md`, cross-referencing
      `board-sync.md` as canonical
- [x] 3.3 Bump `metadata.version` to 1.1.0

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on both skills
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers and the mutual "Do NOT use for … that is the other skill" boundaries unchanged
- [x] Q.4 No duplicated doctrine: `columns:` cross-referenced, not restated; PR-link recipe lives only
      in `board-sync.md`
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 No description promises a policy its body contradicts
- [x] Q.7 No README change — no skill added, removed or repurposed

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate harden-backlog-flow --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `scripts/validate-skills.py` reports 0 findings across 31 skills
- [x] V.5 `scripts/selftest-validate-skills.py` detects 11/11
- [x] V.6 The corrected PR-link recipe returns the right answer for issue #28 (0 linked PRs)
- [x] V.7 `openspec archive harden-backlog-flow --yes` after review
