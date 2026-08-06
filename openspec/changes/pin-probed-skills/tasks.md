## 1. Probe

- [x] 1.1 Build a minimal Vite project with the four rules `fivem-nui-react` prescribes and check each
      output (`vite 8.2.0`, `terser 5.49.2`)
- [x] 1.2 Extract and syntax-check the `ts` blocks in `react-api-client/references/api-client.md`
- [x] 1.3 Record the earlier `gh 2.92.0` probe as the pin for the two backlog skills

## 2. Fix the detector

- [x] 2.1 Widen the PIN regex to recognise `Probed on` and `runtime|tag|CLI|preset <version>`
- [x] 2.2 Confirm `assettoserver-plugin` and `openspec` are no longer reported as unpinned
- [x] 2.3 Document C5's 40-fenced-line limit in the check's docstring

## 3. Pin and mark

- [x] 3.1 `fivem-nui-react` 1.0.1 — pin with what each build rule produced
- [x] 3.2 `backlog` 1.0.2 and `execute-backlog` 1.2.1 — pin `gh 2.92.0`
- [x] 3.3 `react-api-client` 1.1.1 — mark the non-parsing `ts` block as an excerpt
- [x] 3.4 Record the four skills left unpinned and why

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched skill
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers and "Do NOT use for" boundaries unchanged
- [x] Q.4 No duplicated doctrine: excerpt convention reused from `r3f-*`, not restated
- [x] Q.5 Every pin names what was probed and what it produced
- [x] Q.6 No description promises a policy its body contradicts
- [x] Q.7 No README change — no skill added, removed or repurposed

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate pin-probed-skills --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `scripts/validate-skills.py` reports 0 findings across 31 skills
- [x] V.5 `scripts/selftest-validate-skills.py` detects 11/11
- [ ] V.6 `openspec archive pin-probed-skills --yes` after review
