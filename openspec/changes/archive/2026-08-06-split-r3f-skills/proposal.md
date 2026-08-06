# Change: Split the ten r3f skills into SKILL.md + references/

## Why

Executes solvelab/ai-skills#28. The `r3f-*` family was the only group in the catalog with **no
`references/` directory**: ten skills of 566-1150 lines, 75% fenced code, every topic inline. Asking
about morph targets pulled all 1150 lines of `r3f-animation` — spring physics, skeletal animation and
procedural walk cycles included. Nothing let the model read an index and fetch one section.

#26 deliberately left the structure untouched so its compile numbers stayed attributable. This is that
follow-up.

**A defect from #26 was found while executing this.** #26's task 1.1 claimed the version pin was added
*"under the title"* of all ten skills, and the task was ticked. It was not: the regex that inserted it
matched a `---` **section divider** instead of the frontmatter, landing the pin in the **last three
lines** of every one of the ten files. A pin exists so a reader knows which era the code targets
*before* reading it; 1100 lines below the code it qualifies, it does nothing. The pin is now anchored
directly under the H1, which #28's constraint required anyway.

## What Changes

- Each `r3f-*/SKILL.md` becomes frontmatter + title + version pin + a **Topics index** + *See also* —
  **37-41 lines**, against a catalog median of 117.
- **41 reference files** across the ten skills, 3-6 each. Sections are grouped into coherent buckets of
  ~150-250 lines, never one file per heading — #28's Risks section called out the ~130-file sprawl a
  naive split produces.
- `r3f-assets` is decomposed by its real topics. Its two `##` sections hid 21 `###` subtopics; it now
  has six references (`models-usegltf-drei`, `textures-texture-configuration`, ...) rather than two
  buckets, which #28 made an explicit acceptance criterion.
- Content is **moved verbatim**. No teaching content, heading level or code block was rewritten.
- `scripts/validate-skills.py`: C1 now accepts a path that resolves relative to **either** the file or
  the skill directory. Both conventions are correct — `../SKILL.md` from a reference is file-relative,
  `references/x.md` cited anywhere is skill-relative — and the check previously rejected the first.

## Verification

| Acceptance criterion (#28) | Result |
|---|---|
| Every `r3f-*/SKILL.md` at or below the catalog median | 37-41 lines vs median **117** |
| Every moved topic in `references/`, linked from the index | validator: **0 findings** |
| `r3f-assets` decomposed into real topics | **6** references, not two buckets |
| Compile probe: parse <= 1, unresolved imports = 0, untyped <= 5 | **1 / 0 / 5** |
| 62 excerpt markers still present | **62** |
| `generate.sh` clean, rite gate green, CI green | green |
| Cross-references between r3f skills still resolve | validator C1/C2 clean |

Content preservation was checked line by line against `HEAD` for all ten skills: **0 lines lost**. The
probe reports the same 211 compilable blocks and 52 excerpts as before the split, so nothing was
dropped or double-counted.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-catalog`: MODIFIED **Catalog composition after the quality review** — a skill's topics may
  live in `references/`; the catalog is still the set of `skills/*/SKILL.md`, and a reference file is
  not a catalog entry.

## Impact

- Ten `skills/r3f-*/SKILL.md` rewritten as indexes; 41 new `skills/r3f-*/references/*.md`;
  regenerated wrappers; `scripts/validate-skills.py`.
- Loading any r3f skill now costs ~40 lines instead of 566-1150, with the topic fetched on demand.
- Closes #28.
