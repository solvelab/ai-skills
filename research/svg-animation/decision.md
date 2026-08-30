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

**Scope, corrected.** The skill is not only about animation. The method's phases 0-2 build the
object **still** — framing, research and geometry — and an object that is wrong at rest does not
become right by moving. The name stays `svg-animation` because it is what a user types, but the
description must say that it covers building the object as well as moving it, or the skill will not
be reached for when someone needs a correct static figure.

**Category.** `frontend` — from the controlled set the CI enforces
(`.github/workflows/ci.yml`). Ships in `plugins/frontend/`, bringing that plugin from 1 skill to 2.

**Boundary — "Do NOT use for".** three.js/R3F (`r3f-*`), the FiveM NUI bridge (`fivem-nui-react`),
and charting, which is a different discipline.

## Outline for the follow-up item

Following the repository's `SKILL.md` + `references/` shape, which the r3f split established as the
catalog's pattern (issue #28).

**`SKILL.md` is the METHOD** — the five-phase procedure in [`method.md`](method.md), which is what
makes this skill generic. An agent asked for a windmill, a Corolla, a heartbeat or a gull runs the
same five phases; only the research sheet's contents differ.

This is the correction that matters most in this whole item. The research spent a long stretch
refining one dolphin, one whale and one shark, fin by fin — and the maintainer's verdict was that
the skill was getting *worse*, because per-object craft is not what a skill carries. It was right.
A skill that ships a catalogue of shapes someone else drew helps with those shapes. A skill that
ships a procedure helps with every object nobody has drawn yet.

So the worked animals move to `references/` as demonstrations, and the operational core is:

0. **Frame the request** — object in one sentence, the view chosen by the mechanism, the read size,
   and what it must not be mistaken for.
1. **Research the object** — a sheet with nine fields, filled before anything is drawn.
2. **Geometry** — decompose by what moves together; mass from a profile table, features as explicit
   outlines; join by the colour rule; check it large against a grid.
3. **Script the life cycle** — states and named phases in prose, before a keyframe exists.
4. **Assemble and animate** — hierarchy from the part list, lag makes the wave, channel by measured
   cost, decorrelate, reduce rather than remove.
5. **Verify** — frozen poses, large on a grid, the reduced-motion variant, measured cost.

The old outline, which put the cost model first, is kept below only to record what it got wrong:

0. **The observation step, first.** Research the subject before animating it: mechanism, phases,
   geometry, materials, scale relations. This was missing from the first draft of the research and
   its absence produced a bird made of two rotating arcs — every performance rule obeyed, and the
   result worthless. A skill that opens with the cost model teaches an agent to make fast, cheap,
   wrong animation. `report.md` §0 and §0b.
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
| `object-research.md` | the phase-1 sheet in full, with worked examples of each field |
| `geometry.md` | profile tables, explicit outlines, the three-case join rule, light direction, distribution |
| `life-cycle-script.md` | how to write a cycle in prose: states, named phases, asymmetry, what absence means |
| `worked-examples.md` | the gull, the dolphin, the humpback and the shark — each one the method run end to end, including the failed attempts and why they failed |
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

## The doctrine was tested against code that was already right

The `ferdinand` scene above shows the vocabulary carrying a domain. The `feldt` scene tests something
harder: what the doctrine says to a screen that is **already correct**.

`feldt` is the central dead man's switch those posts report to. Its `/world` screen draws an
archipelago — one island per network, shape derived from a seeded hash of the network id — on a
**canvas**, with a camera, level-of-detail and a baked stage. Read in the source at
`src/http/scene.ts`: 49 canvas references, zero SVG, and **zero `requestAnimationFrame`** — the
island is static, and the only rAF in that screen is the camera flight.

Three things follow, and the first is the one that matters:

1. **The doctrine says keep the canvas.** A world with pan, zoom and many islands is precisely the
   case where retained-mode SVG loses — measured at 2000 elements, 466 ms/s against 125. A skill
   whose answer to every screen is "use SVG" would be wrong here, and would be wrong loudly.
2. **What is missing is ambient motion, and it belongs above the canvas.** Adding it inside the
   canvas would mean redrawing per frame and invalidating the bake the camera depends on. In layers
   above it, the canvas is never touched.
3. **The obvious way to write those layers costs 37 layout/s; the correct way costs 0.** Measured as
   prototypes 19, 20 and 21. The intermediate attempt is the instructive one: promoting each mark to
   its own `<svg>` while still animating the `<circle>` inside it changed nothing. The transform has
   to land on the HTML-level box.

That third point is the strongest argument for the skill existing at all. The rule is short enough
to state in a sentence, it is not in the literature, and getting it half-right produces exactly the
same cost as not knowing it.

The follow-up skill should carry this pair — a screen before and after — because "add motion here"
is advice anyone can give, and "on this channel, in this shape, at this measured cost" is not.

## Consequences

- `skills/` gains one directory; `README.md` and `.claude-plugin/marketplace.json` counts move from
  34 to 35, which `scripts/validate-repo-hygiene.py` will require.
- `plugins/frontend/` goes from 1 skill to 2.
- Nothing existing is edited or renamed.
- This directory stays as the backing evidence, outside `skills/` and therefore outside what
  consumers receive.
