## 1. Split

- [x] 1.1 Write a splitter that groups `##` sections into ~150-250 line buckets on section boundaries
- [x] 1.2 Descend into `###` when a `##` exceeds 1.5x the target and has 3+ subsections
- [x] 1.3 Never merge sections from different parent `##` into one reference
- [x] 1.4 Name each reference after its most substantial non-generic section
- [x] 1.5 Rewrite each `SKILL.md` as frontmatter + title + pin + Topics index + See also
- [x] 1.6 Apply to all ten skills — 41 references, 3-6 per skill

## 2. Fix what the run exposed

- [x] 2.1 Re-anchor the version pin under the H1 in all ten skills (#26 left it in the last three
      lines of every file while claiming otherwise)
- [x] 2.2 `scripts/validate-skills.py` C1: accept a path resolving from either the file or the skill
      directory

## 3. Acceptance criteria from #28

- [x] 3.1 Every `r3f-*/SKILL.md` at or below the catalog median — 37-41 vs 117
- [x] 3.2 Every moved topic in `references/`, linked from the index — validator 0 findings
- [x] 3.3 `r3f-assets` decomposed into real topics — 6 references, not two buckets
- [x] 3.4 Compile probe: parse failures 1, unresolved imports 0, untyped 5 — all within limits
- [x] 3.5 62 excerpt markers still present
- [x] 3.6 Cross-references between the r3f skills still resolve
- [x] 3.7 Content preservation verified line by line against HEAD — 0 lines lost in all ten

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on all ten skills; reference files carry none, by design
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Descriptions, triggers and "For X use Y" cross-references unchanged
- [x] Q.4 No duplicated doctrine: content moved, never copied; progressive-disclosure pattern reused
      from `bug-hunter` / `documentation`, not restated
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 No description promises a policy its body contradicts
- [x] Q.7 No README change — the Game section already describes the family and its pin

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate split-r3f-skills --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 `scripts/validate-skills.py` 0 findings across 31 skills
- [x] V.5 `scripts/selftest-validate-skills.py` 11/11
- [x] V.6 `openspec archive split-r3f-skills --yes` after review
