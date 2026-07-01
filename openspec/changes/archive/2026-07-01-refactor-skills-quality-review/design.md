## Context

19 skills serve 4+ project families (DriveZone FiveM + Python backend, fabcost3d FastAPI, omnivoice-tts
Python REST, vibetalker React/TS). Audit evidence: generic resilience principles embedded in
`fivem-fallback`; `bug-hunter` Track A assumes pytest/TestClient/Postgres silently; overlap matrix shows
anti-forge stated in 4 files, atomicity in 3, negative-cache in 3; `openspec-drivezone` restates sibling
content instead of linking and its footer links point to nonexistent `content.md` files; r3f cluster has
2–4-way content duplication and no frontmatter metadata.

## Goals / Non-Goals

- Goals: maximize reuse across project families; one canonical home per rule; uniform metadata; keep
  everything that already works (api-resilience-testing untouched in substance; fivem-lua kept);
  preserve trigger quality; ship via automated release.
- Non-Goals: authoring `python-rest-api`, `docker-conventions`, `pr-review` skills (backlog — must be
  distilled from real project code, not invented); re-nesting skills into subdirectories (breaks Claude
  plugin + npx discovery, which scan one level); rewriting r3f reference content wholesale.

## Decisions

1. **Generic + adaptation pattern** (not one mega-skill): `backend-resilience` holds doctrine with
   Python examples; `fivem-fallback` holds only Lua mechanics and links up. Rationale: triggers stay
   precise per stack; content is never duplicated; other backends can adopt the generic skill alone.
2. **Tracks as references/** for `bug-hunter`: SKILL.md stays small and stack-agnostic (progressive
   disclosure — agents read the track file only when the stack matches). Alternative rejected: three
   separate skills (adversarial-testing, pytest-testing, fivem-testing) would fragment one rite and
   triple trigger surface.
3. **Merge only loaders+textures** in r3f: the sole pair whose *content* (not just theme) overlaps
   heavily. Other pairs (materials/shaders, interaction/postprocessing, fundamentals/animation) keep
   distinct value and get pointers instead.
4. **Canonical-rule map**: trust boundary → `fivem-lua`; fallback/negative-cache/clamp → `backend-resilience`;
   REST negative-testing checklist → `api-resilience-testing`; adversarial methodology → `bug-hunter`;
   OpenSpec lifecycle → `openspec`. Cross-references are one-line links, never restated lists.
5. **Controlled category vocabulary**: `backend | testing | fivem | game | devops | docs | git | process`.
   Enforced by CI (frontmatter check in `.github/workflows/ci.yml` validate job).
6. **English as repo locale** (public repo, npx-distributed); `openspec-drivezone` translated.
7. **Version semantics**: every edited skill bumps `metadata.version` minor; new skills start at 1.0.0;
   repo release handled by semantic-release from commit types (`skill:` → minor).

## Risks / Trade-offs

- Removing skill names (`r3f-loaders`, `r3f-textures`) breaks nothing at install level (symlinks/npx
  re-resolve; plugin updates atomically) but stale local copies may linger → release notes call it out.
- De-duplication relies on agents following links; mitigated by keeping a one-line summary next to each
  link (enough context to decide whether to open the reference).
- Description rewrites risk trigger regressions → each rewritten description keeps all previous
  trigger keywords unless a collision was documented in the audit.

## Migration

Single PR-equivalent series of commits on master; wrappers regenerated in the same commits; semantic-release
cuts one minor release. No consumer action required beyond normal update.
