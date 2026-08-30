# Decision — where this knowledge should live

Verdict, stated first: **a new skill, `svg-animation`, `metadata.category: frontend`, shipped in
the `ai-skills-frontend` plugin.**

This file records why, what was rejected, and the outline the follow-up item inherits so it does not
have to re-decide any of it.

## What the catalog has today

Measured on `master` at `a8405ae`:

- **34 skills. Zero SVG coverage.** `grep -rniE '\bsvg\b'` across every `SKILL.md` and every
  `references/*.md` returns two lines, both badge URLs in
  `skills/documentation/references/templates.md:26-27`.
- **No 2D animation skill, no Canvas skill, no motion-design skill.**
- The nearest neighbours, and why none of them is a home:

| Skill | Category | Why not |
|---|---|---|
| `r3f-animation` | `game` | three.js/R3F. Its `procedural-animation-patterns.md` is skeletal bone manipulation; its walk-cycle reference is 3D and pinned to `three@0.185`. A consumer enabling `ai-skills-game` wants a 3D engine, not an SVG scene. |
| `react-api-client` | `frontend` | Data fetching. Sole occupant of the `frontend` plugin. |
| `fivem-nui-react` | `nui` | The Lua↔React bridge for CEF. Carries `tokens.css` design-system rules, but its subject is the bridge. |

## The decision

### Rejected: fold it into `r3f-animation`

The overlap is thematic, not technical. Nothing in this research transfers to three.js: the finding
that drives the whole design — SVG children pay layout per frame, HTML boxes do not — has no
meaning in a WebGL scene graph. Merging would also put SVG behind the `game` plugin, where the
audience that needs it is not looking, and would break the `skills-catalog` requirement that a
task route to exactly one skill.

### Rejected: split across several skills

Considered as `svg-animation` + `canvas-animation` + `motion-primitives`. Rejected because the
primitives are worthless without the cost model, and the Canvas material exists only as the answer
to *when do I leave SVG* — **[measured]** at 2000 particles, 466 ms/s against 125 ms/s. Splitting
would put the question in one skill and its answer in another, and the catalog already has a
requirement against restating doctrine across skills.

### Rejected: extend `fivem-nui-react`

FiveM-specific. The `skills-catalog` requirement *Generic doctrine is reusable outside FiveM* says
generic doctrine goes in the generic skill; this is the same shape as `backend-resilience` versus
`fivem-fallback`.

### Chosen: one new skill, `svg-animation`

**Name.** `svg-animation` over the other candidates in the item:

- `svg-motion` — vaguer, and "motion" collides with the Motion library.
- `procedural-svg-animation` — too narrow. Morphing and `draw` are not procedural, and they are
  half the value.
- `svg-animation-design` — reads as visual design; the content is engineering.

`svg-animation` is also what a user actually types. The description's triggers should match the way
the request is phrased in practice: *animate this SVG*, *SVG animation performance*, *animated
background*, *parallax scene*, *particles*, *path morphing*, *animated icon*, *make this loop*.

**Category.** `frontend` — from the controlled set the CI enforces
(`.github/workflows/ci.yml`). Ships in `plugins/frontend/`, bringing that plugin from 1 skill to 2.

**Boundary — "Do NOT use for".** three.js/R3F (`r3f-*`), the FiveM NUI bridge (`fivem-nui-react`),
and charting, which is a different discipline.

## Outline for the follow-up item

Following the repository's `SKILL.md` + `references/` shape, which the r3f split established as the
catalog's pattern (issue #28).

**`SKILL.md`** — the operational core, everything a decision depends on:

1. The cost model. The measured table, and the one rule that follows: *decide the layer boundary by
   what moves; anything that moves as a unit is its own `<svg>` element.*
2. Choosing the mechanism — SMIL / CSS / WAAPI / script — and why the choice barely affects cost.
3. Choosing the technology — SVG / Canvas / WebGL — with the measured crossover.
4. The scene-building procedure, seven steps.
5. Accessibility: reduce and replace, never remove; re-read on change.
6. Anti-patterns, each with the measurement that condemns it.
7. Quality and performance checklists.

**`references/`**:

| File | Contents |
|---|---|
| `primitives.md` | the 22 behaviours: channel, cost, composition notes |
| `scene-recipes.md` | the composition table, with 6–8 scenes developed in full |
| `performance-measurement.md` | how to measure — the harness, what it cannot see, how to read it |
| `morphing.md` | the same-command-count constraint and the three ways out |
| `accessibility.md` | reduced motion done properly, plus semantics of decorative vs meaningful SVG |

The material for all of these exists in this directory. The follow-up item is largely promotion and
compression, not new research — with one exception noted below.

## What the follow-up item must not inherit uncritically

- **The compositing question is open** (`report.md` §8). The skill must carry it as open, not
  resolve it by picking whichever source reads best.
- **Every number is one engine on one machine**, headless, software rasterisation. The skill states
  the scope beside the numbers, or it teaches a falsehood.
- **The measurements are dated**, not maintained. They were taken 2026-08-30 against Chrome
  151.0.7922.34. A skill that quotes them must name that version, per the `skills-authoring`
  requirement *Versioned external APIs are pinned*.
- **Where filters break was not found** (`report.md` §5). The skill says "measure it", not "it is
  fine".

## Seen, not just measured

The eight model scenes run at
<https://claude.ai/code/artifact/f92ae439-2e51-4977-8f6f-acb481a0c031>, generated from
`scenes/scenes.js` by `build-showcase.mjs`. Two defects in this research were found by looking at
that render rather than by reading anything — both `transform-box` traps in `report.md` §7b — which
is the argument for the follow-up skill carrying a "look at it" step and not only a checklist.

## The vocabulary was tested against a real domain, not only against weather

Eight of the model scenes are natural phenomena, which is a fair test of the primitives and a weak
test of whether they say anything. The ninth is taken from `ferdinand`, a production out-of-band
Kubernetes node watchdog in this maintainer's own workspace, named after the South Pacific
Coastwatchers.

It matters because it forced a composition the weather scenes never would have: the project's
central mechanism is a dead man's switch — `src/deadman/heartbeat.ts` says *"the operator is warned
by its silence"* — so the scene's alert had to be a post that **stops** transmitting. Animating an
absence is not in any primitive's definition, and it only reads because the other four posts are
pulsing, staggered, first.

That produced a composition rule the natural scenes did not surface, now recorded in
`primitives.md`. The follow-up skill should carry at least one domain scene for the same reason:
a vocabulary that only produces pretty weather has not been shown to carry meaning.

## Consequences

- `skills/` gains one directory; `README.md` and `.claude-plugin/marketplace.json` counts move from
  34 to 35, which `scripts/validate-repo-hygiene.py` will require.
- `plugins/frontend/` goes from 1 skill to 2.
- Nothing existing is edited or renamed.
- This directory stays as the backing evidence, outside `skills/` and therefore outside what
  consumers receive.
