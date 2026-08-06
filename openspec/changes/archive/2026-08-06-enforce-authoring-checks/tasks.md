## 1. Validator

- [x] 1.1 Implement C1-C6 over every `skills/*/SKILL.md` and its `references/*.md`
- [x] 1.2 Handle fences nested in list items (dedent by the fence's own indentation)
- [x] 1.3 Ignore paths inside fenced blocks and links inside inline-code spans
- [x] 1.4 Resolve `references/…` from the skill directory, not the citing file's directory
- [x] 1.5 Narrow C4 (absolute promise carrying its own condition is fine) and C5 (a stated stack is a
      pin; a skill deferring to a local source of truth is exempt)
- [x] 1.6 Report checks skipped for want of `luac` or PyYAML; support `luac5.4` naming

## 2. Self-test

- [x] 2.1 Inject one known defect per check into a throwaway copy and assert detection
- [x] 2.2 All ten defect classes detected

## 3. Catalog corrections found by the validator

- [x] 3.1 Qualify 7 cross-skill reference paths with the owning skill
- [x] 3.2 helm-migration: description names the env.yaml condition; chart template declared the source
      of truth
- [x] 3.3 Retag 5 comment-annotated multi-payload blocks `json` -> `jsonc`
- [x] 3.4 Mark the `lua` and `python` fragments as excerpts

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched skill
- [x] Q.2 All touched content in English (catalog locale)
- [x] Q.3 Triggers and "Do NOT use for" boundaries unchanged on every touched skill
- [x] Q.4 No duplicated doctrine: the validator enforces `skills-authoring`, it does not restate it
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 No description promises a policy its body contradicts (verified by the validator itself)
- [x] Q.7 README documents the new scripts

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate enforce-authoring-checks --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 CI frontmatter check passes locally
- [x] V.5 `scripts/validate-skills.py` reports 0 findings across all 30 skills
- [x] V.6 `scripts/selftest-validate-skills.py` detects 10/10 injected defect classes
- [x] V.7 `openspec archive enforce-authoring-checks --yes` after review
