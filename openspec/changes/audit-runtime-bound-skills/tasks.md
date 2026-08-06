## 1. Audit without the runtime

- [x] 1.1 Read all five skills in full
- [x] 1.2 Apply the five `bug-hunter` defect classes (#37) as a lens to each
- [x] 1.3 Probe every publicly verifiable claim

## 2. assettoserver-plugin (1.3.0)

- [x] 2.1 Confirm `System.Threading.Lock` ships in .NET 9
- [x] 2.2 Probe upstream `AssettoServer.csproj` at tag v0.0.54 — targets `net8.0`
- [x] 2.3 Correct the TFM fallback to `net8.0` and record the probed evidence inline
- [x] 2.4 State why a fallback default is a trap here
- [x] 2.5 Version-scope the `System.Threading.Lock` ban and say what to do when the pin moves

## 3. fivem-lua (1.3.0)

- [x] 3.1 Confirm the skill never mentions logging a rejection
- [x] 3.2 Add the rejection counter + log rule at the trust boundary
- [x] 3.3 Syntax-check the added Lua with `luac -p`

## 4. Report what needed nothing

- [x] 4.1 `assettoserver-ops`, `assettoserver-csp-lua`: read in full, lenses applied, no defect found
- [x] 4.2 `openspec-drivezone`: enforcement already corrected by an earlier change
- [x] 4.3 Record all three in the proposal rather than editing to move a number

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on both touched skills
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Triggers and "Do NOT use for" boundaries unchanged
- [x] Q.4 No duplicated doctrine: observability principle links `backend-resilience`; the Cecil gate
      stays in `bug-hunter/references/track-dotnet-plugin.md`
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 No description promises a policy its body contradicts
- [x] Q.7 No README change — no skill added, removed or repurposed

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate audit-runtime-bound-skills --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `scripts/validate-skills.py` 0 findings across 31 skills
- [x] V.5 `scripts/selftest-validate-skills.py` 12/12
- [ ] V.6 `openspec archive audit-runtime-bound-skills --yes` after review
