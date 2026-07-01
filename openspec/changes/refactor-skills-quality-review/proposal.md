# Change: Deep quality review of the skills catalog (generalize, de-duplicate, standardize)

## Why

The 19 skills were authored per-project and organically. A three-way audit found: generic backend
doctrine (resilience, adversarial testing) trapped inside FiveM-named skills and therefore unusable by
the other Python/REST projects (fabcost3d, omnivoice-tts, filial); the same rule independently stated
in up to 4 files (anti-forge in 4, atomicity in 3, negative-cache in 3) guaranteeing drift; heavy
copy-paste inside the r3f cluster (loaders≈textures, useFrame/shaderMaterial/outline/environment
duplicated); chaotic frontmatter metadata (three author values, 11 r3f skills with no metadata at all);
broken `content.md` links left over from the layout migration; and a terminology contradiction between
api-resilience-testing and bug-hunter.

## What Changes

- **New skill `backend-resilience`** — generic dependency-resilience doctrine (safe defaults, negative
  cache, bounded retries, clamping, in-flight dedupe) extracted from `fivem-fallback`, with Python
  examples; `fivem-fallback` becomes the thin FiveM/Lua adaptation linking to it.
- **`bug-hunter` restructured** — SKILL.md keeps the stack-agnostic methodology (mindset, universal
  checklist, output contract); stack tracks move to `references/track-python-pytest.md` and
  `references/track-fivem-lua.md`; restated rules replaced with links to canonical skills.
- **New skill `openspec`** — generic OpenSpec workflow skill (vanilla lifecycle); `openspec-drivezone`
  becomes the documented forked variant, translated to English, with broken links fixed and restated
  gate tables replaced by links.
- **r3f cluster 11 → 10** — merge `r3f-loaders` + `r3f-textures` into `r3f-assets`; remove duplicated
  blocks in animation/materials/interaction in favor of cross-references; fix v8/v9 TypeScript
  declaration inconsistency; rewrite the 10 descriptions with explicit boundaries.
- **Single source of truth per rule** — trust boundary lives in `fivem-lua`; fallback/negative-cache in
  `backend-resilience`; REST checklist in `api-resilience-testing`; adversarial methodology in
  `bug-hunter`; every other mention becomes a link.
- **Frontmatter standardization** — all skills get `metadata.author: solvelab`, `metadata.version`,
  `metadata.category` (controlled vocabulary), `license: MIT`, `compatibility`; CI check extended to
  enforce it.
- **`documentation` softened** — hard style rules (badge header) become audience-conditional defaults.
- **`helm-migration` coupling made explicit** — description states it requires the solvelab chart
  template repository.
- README catalog regenerated (20 skills, grouped by category); wrappers regenerated; orphaned
  loaders/textures wrappers removed.

**BREAKING** (catalog-level, not install-level): `r3f-loaders` and `r3f-textures` skill names disappear
(superseded by `r3f-assets`). npx/plugin/symlink installs re-resolve on next update.

## Impact

- Affected specs: `skills-catalog` (new), `skills-authoring` (new).
- Affected code: `skills/**` (17 edited, 3 added, 2 removed), `claude|codex|cursor|copilot` wrappers
  (regenerated), `.github/workflows/ci.yml` (frontmatter check), `README.md`, `generate.sh` output.
- Release: minor via semantic-release (`skill:`/`refactor:` commits); no install-path breakage.
