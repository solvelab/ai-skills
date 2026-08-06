## Context

The `r3f-*` family carried 8,454 lines across ten skills, 75% of it fenced code, with no progressive
disclosure anywhere. #26 compile-checked every block and deliberately changed no structure, so its
numbers stayed attributable to the code fixes alone. #28 groomed the structural follow-up; this change
executes it.

## Goals / Non-Goals

**Goals**
- Reading one r3f topic costs one topic, not the whole skill.
- Content moves verbatim, verified line by line.
- The compile state established by #26 survives the move, proven by re-running the same probe.

**Non-Goals**
- No teaching content changed. Not a heading level, not a code block, not a sentence.
- No R3F v10 / drei 11 migration. Both are alpha; the pin names the coming rename.
- No one-file-per-heading split. #28's Risks section named the ~130-file sprawl as the failure mode.

## Decisions

**D1 — Group by size, never by heading count.** Buckets target ~150-250 lines and break on a section
boundary, producing 3-6 references per skill (41 total). One file per `##` would have produced ~130
files and traded one navigation problem for another.

**D2 — Descend into `###` only when a `##` is oversized.** `r3f-assets` had two top-level sections
hiding 21 subtopics. A splitter that only sees `##` produces the two buckets #28 explicitly forbids, so
a section past 1.5x the target with three or more `###` is split at those instead.

**D3 — Never merge across parent sections.** An early run produced a bucket straddling *Models:
Performance Tips* and *Textures: Quick Start*. A reference has to be about one thing, so a bucket
closes when the parent changes regardless of size.

**D4 — Name the reference after its most substantial non-generic section.** Naming by the first
section produced `quick-start.md` for a bucket whose real subject was material types. Ranking by size
and skipping generic titles (*Quick Start*, *Overview*, *Performance Tips*) gives a name that says what
is inside.

**D5 — Verbatim move, verified against `HEAD`.** No heading promotion, no rewrapping. Every non-trivial
line of each original was checked to still exist in the new `SKILL.md` or one of its references:
0 lost across all ten. The compile probe returning the same 211/52 counts is the second, independent
check.

**D6 — Fix the pin placement found in flight.** #26 claimed the pin sat under the title and it sat in
the last three lines of all ten files. It is re-anchored here rather than deferred, because #28's
constraint requires it and because the splitter had to touch that region anyway.

**D7 — Teach the validator that both path conventions are correct.** The split introduced
`../SKILL.md` links from reference files, which C1 rejected: it resolved every path from the skill
directory after an earlier fix for skill-relative citations. A path is now a defect only when it
resolves from neither the file nor the skill directory.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| R3F topic doctrine (scene, assets, lighting, physics, shaders, …) | each `r3f-*` skill | already canonical — relocated into its own `references/`, unchanged |
| Version pin and code-block conventions for the family | each `r3f-*/SKILL.md` | already canonical — pin re-anchored under the title |
| What the catalog is, and where a skill's topics may live | `openspec/specs/skills-catalog` | spec delta |
| Mechanical enforcement of authoring rules | `scripts/validate-skills.py` | already canonical — C1 path resolution corrected |
| Progressive-disclosure precedent (SKILL.md + references) | `bug-hunter`, `documentation`, `python-rest-api` | pattern reused, not restated |

## Risks / Trade-offs

- [41 new files is a wide diff] → every one is a verbatim move, and preservation was verified
  line-by-line against `HEAD` plus a re-run of the compile probe.
- [An index adds one hop before the content] → that is the point; the hop costs ~40 lines instead of
  up to 1150.
- [Bucket names are derived, not authored] → they are section titles, so they match what the reader
  saw before; a better name is a one-line rename with no content risk.
- [Reference files carry no frontmatter] → intended, and now stated in the spec so a future check does
  not flag them as malformed skills.
