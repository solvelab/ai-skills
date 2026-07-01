# Tasks — refactor-skills-quality-review

## 1. Generalization (backend/FiveM cluster)

- [x] 1.1 Create `skills/backend-resilience/SKILL.md` — principles (safe default, shared helper,
      response-shape validation, clamp, bounded retries, negative cache w/ 404 exception, in-flight
      dedupe) + Python examples; category `backend`
- [x] 1.2 Rewrite `skills/fivem-fallback/SKILL.md` as thin FiveM adaptation (Lua mechanics only;
      links to backend-resilience at top)
- [x] 1.3 Restructure `skills/bug-hunter/`: stack-agnostic SKILL.md + `references/track-python-pytest.md`
      + `references/track-fivem-lua.md`; replace restated rules with links; de-collide description
- [x] 1.4 Adjust `skills/api-resilience-testing/SKILL.md`: soften "bug hunting" terminology line
      (acknowledge bug-hunter rite); add See-also (bug-hunter, backend-resilience)
- [x] 1.5 Update `skills/fivem-lua/SKILL.md` See-also graph (bidirectional links across the cluster)

## 2. OpenSpec skills

- [x] 2.1 Create `skills/openspec/SKILL.md` — vanilla lifecycle (explore→propose→validate→apply→archive),
      proposal/delta/tasks format, trigger guidance; based on vibetalker `openspec/AGENTS.md` + the
      vanilla paragraph of openspec-drivezone
- [x] 2.2 Rework `skills/openspec-drivezone/SKILL.md`: translate to English; fix broken
      `../*/content.md` links → `SKILL.md`; replace restated gate tables with links + 1-line summaries;
      link `openspec` as the base workflow

## 3. r3f cluster (11 → 10)

- [x] 3.1 Create `skills/r3f-assets/SKILL.md` (curated merge of loaders+textures; env-map deep-dive
      stays in r3f-lighting, linked); delete `skills/r3f-loaders/`, `skills/r3f-textures/`
- [x] 3.2 De-dup `r3f-animation` (drop basic useFrame → pointer to fundamentals; drop
      MeshWobble/Distort → pointer to materials; keep procedural cycles + zustand perf)
- [x] 3.3 De-dup `r3f-materials` (drop full shaderMaterial example → pointer to r3f-shaders; drop
      env-maps section → pointer to r3f-assets/lighting)
- [x] 3.4 De-dup `r3f-interaction` (drop outline/multi-select → pointer to postprocessing; keep drag
      canonical here, animation links back)
- [x] 3.5 Fix TypeScript declarations to v9 `ThreeElements` pattern in `r3f-fundamentals` and
      `r3f-shaders`
- [x] 3.6 Rewrite the 10 r3f descriptions with explicit boundaries (environment/HDR, useFrame, shader,
      drag collisions resolved)

## 4. Metadata & policy standardization

- [x] 4.1 Standard frontmatter on ALL skills: `metadata.author: solvelab`, `metadata.version`,
      `metadata.category` ∈ {backend, testing, fivem, game, devops, docs, git, process}, `license: MIT`,
      `compatibility`; add full blocks to the 10 r3f skills; bump minor on every edited skill
- [x] 4.2 Extend CI frontmatter check (`.github/workflows/ci.yml` validate job): require
      metadata.version, license, category-in-enum
- [x] 4.3 Soften `skills/documentation/SKILL.md` style mandates into audience-conditional defaults
- [x] 4.4 Make `skills/helm-migration/SKILL.md` coupling explicit (solvelab chart template required);
      prose "your-org-specific fields" → "template-specific fields"
- [x] 4.5 Align `skills/conventional-commit/SKILL.md` with personal-rules.md wording (skill is
      canonical; complete frontmatter)

## 5. Docs & regeneration

- [x] 5.1 Regenerate README Skills Available table (20 skills grouped by category; coupling notes)
- [x] 5.2 Run `generate.sh`; remove orphaned loaders/textures wrappers from all four wrapper trees

## 6. Validação & Fechamento

- [x] 6.1 `bash generate.sh && git status` clean of unexpected drift; orphaned wrappers gone
- [x] 6.2 `npx skills add ./ --list` → Found 20 skills (no YAML-silent drops)
- [x] 6.3 Frontmatter lint 20/20 (CI loop run locally)
- [x] 6.4 Consistency grep: no `r3f-loaders`/`r3f-textures`/`content.md` references left in skills/ or
      README; canonical rules defined once, linked elsewhere
- [x] 6.5 Cross-read: openspec-drivezone contains links, not restated mechanism lists
- [ ] 6.6 Commit series pushed; CI green; semantic-release minor with new skills in notes;
      `openspec archive refactor-skills-quality-review`
