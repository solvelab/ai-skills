## 1. Score the existing checklist

- [x] 1.1 Take the five defects found in the catalog audit and score each against the universal
      checklist as written
- [x] 1.2 Record the verdict per defect (4 clean misses, 1 wrong-scale partial)
- [x] 1.3 Confirm the stack tracks do not close the gap

## 2. Extend the checklist

- [x] 2.1 Add **Shape, not just size**
- [x] 2.2 Add **Fragmented input**
- [x] 2.3 Add **Distinctness** as the stated inverse of idempotency
- [x] 2.4 Add **Observable degradation**
- [x] 2.5 Replace pair-concurrency with **burst**, keeping the pair as the minimum case
- [x] 2.6 Add the provenance table and the standing rule to grow it on the next escape
- [x] 2.7 Raise the concurrency scenario in `track-python-pytest.md` and `track-fivem-lua.md`
- [x] 2.8 Bump `metadata.version` to 2.2.0

## 3. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on `bug-hunter`
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers and the "Do NOT use for … that is api-resilience-testing" boundary unchanged
- [x] Q.4 No duplicated doctrine: fallback behaviour still defined by `backend-resilience`, REST
      surface audit still owned by `api-resilience-testing`
- [x] Q.5 Every added item names the defect that earned it, with its measured number
- [x] Q.6 Description states no policy the body contradicts
- [x] Q.7 No README change — purpose and triggers unchanged

## 4. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate harden-bug-hunter --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `scripts/validate-skills.py` reports 0 findings across 31 skills
- [x] V.5 `scripts/selftest-validate-skills.py` detects 11/11
- [x] V.6 `openspec archive harden-bug-hunter --yes` after review
