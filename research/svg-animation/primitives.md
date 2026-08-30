# Primitives and composition

A scene is not written as a scene. It is written as a handful of behaviours, composed. This file is
the vocabulary: what each behaviour is, what channel it uses, what it costs, and what it composes
with.

Cost column uses the channels measured in [`measurements.md`](measurements.md):

- **free** — animates an `<svg>`/HTML box transform or opacity: 0 layout per frame.
- **layout** — animates something inside SVG: layout every frame. Fine in the tens, budget it in
  the hundreds.
- **script** — recomputes geometry per frame: layout, plus script time proportional to sample count.
- **raster** — filter or large-area repaint; cost lives off the main thread and shows up as
  dropped composited frames.

---

## The primitives

### Motion in place

| Primitive | What it is | Channel | Cost |
|---|---|---|---|
| `oscillate` | value swings between two bounds on a sine | transform | free–layout |
| `sway` | oscillate around an anchored base, rotation not translation | `transform-origin` + rotate | layout |
| `float` | slow vertical oscillate, usually paired with slight scale | transform | free |
| `breathe` | slow scale or opacity swell, 4–12 s period | transform/opacity | free |
| `pulse` | fast, sharp scale or opacity beat, under 1 s | opacity | free |
| `flicker` | irregular opacity steps, not a smooth curve | opacity | free |
| `rotate` | constant angular velocity | transform | free–layout |

Before any of these: **set `transform-box` deliberately.** SVG's initial `transform-origin` is
`0 0`, so `scale` and `rotate` translate the element unless you say otherwise. Use
`transform-box: fill-box` for anything that turns about itself, and `view-box` with an explicit
origin for anything that turns about a point in the scene. Both traps, and the two scenes that hit
them, are in `report.md` §7b.

`sway` is the one people get wrong: a tree branch bending is a **rotation about its base**, not a
translation. Set `transform-origin` to the joint and rotate a few degrees. Translating a branch
makes it look like it detached.

`flicker` must be irregular to read as fire or a failing bulb. A sine looks mechanical; step
between random values held for random short durations, and clamp the range so it never fully
disappears.

### Motion through space

| Primitive | What it is | Channel | Cost |
|---|---|---|---|
| `drift` | constant linear travel, usually looping | transform | free |
| `orbit` | circular or elliptical path around a point | transform | free–layout |
| `follow-path` | position driven by an arbitrary path | `offset-path`, or SMIL `animateMotion` | layout |
| `parallax` | layers travelling at rates proportional to depth | transform per layer | free |
| `scatter` | one-off distribution of many instances | none (setup) | — |
| `swarm` | many instances with individual, weakly-correlated motion | varies | layout–script |

`orbit` composes as *rotate a group whose child is offset from the origin* — cheaper and more stable
than recomputing `cx`/`cy` from trigonometry every frame, and it gives you the moon-around-planet
case for free by nesting.

`follow-path` in CSS is `offset-path: path(...)` with `offset-distance` animated, and
`offset-rotate: auto` turns the element to face its direction of travel — which is what makes a bird
or a car read as travelling rather than sliding.

`parallax` is the highest-value primitive in the set, because depth is what turns a flat drawing
into a scene, and **[measured]** it is free when each layer is its own `<svg>` element (0 layout/s
against 37.4 for `<g>` layers).

### Shape and surface

| Primitive | What it is | Channel | Cost |
|---|---|---|---|
| `morph` | interpolate one path into another | `d` | layout + script |
| `wave` | travelling periodic displacement of an outline | transform (tile) or `d` (rebuild) | free or script |
| `ripple` | expanding ring, fading as it grows | transform + opacity | free |
| `turbulence` | procedural noise field | `feTurbulence` | raster |
| `draw` | line revealing itself along its length | `stroke-dashoffset` | layout |

`draw` is the `stroke-dasharray`/`stroke-dashoffset` technique: set both to the path length
(`path.getTotalLength()`), then animate the offset to 0. It is the single most useful SVG-specific
effect — handwriting, route tracing, lightning, growing vines — and it has no HTML equivalent.

`wave` has two implementations with a real trade-off, both measured: rebuild the path each frame
and never repeat (17.85 ms/s, 60.2 layout/s), or translate a seamless double-width tile and accept
a period (7.12 ms/s, 0 layout/s). Prefer the tile; reach for the rebuild only when a viewer will
watch long enough to find the loop.

### Timing and feel

| Primitive | What it is | Where it lives |
|---|---|---|
| `easing` | non-linear progress through a tween | `animation-timing-function`, `keySplines` |
| `stagger` | same animation, offset start per instance | negative `animation-delay` |
| `spring` | overshoot and settle | easing approximation, or a physics library |
| `inertia` | velocity carried past the input that caused it | script |
| `noise-motion` | position or rotation driven by smooth noise rather than a sine | script |

**`stagger` is what separates a scene from a screensaver**, and it is nearly free: give each
instance a *negative* `animation-delay` proportional to its index, and the whole set starts already
distributed through the cycle rather than snapping into phase together.

```js
el.style.animationDelay = `${-(i / count) * durationSeconds}s`
```

`noise-motion` is the antidote to the mechanical look. A sine is exactly periodic and the eye finds
it; summing two or three sines whose frequencies are not simple multiples of each other produces
motion that never quite repeats. Prototype 17 does this with periods of 190, 71 and 37 — chosen so
no small integer relates them.

---

## Composition

The scenes below are combinations. Nothing here is a new technique; each is a recipe over the
vocabulary above.

| Scene | Composition |
|---|---|
| **starfield** | `scatter` + `flicker` (staggered, irregular) + `parallax` over 3–5 depths |
| **ocean** | `wave` (tiled) × 4 depths + `parallax` + gradient for depth + `ripple` for highlights |
| **tree in wind** | `sway` about each joint + `stagger` down the branch hierarchy + `noise-motion` on the amplitude so gusts are uneven |
| **clouds** | `turbulence` generated once + `drift` at two rates + opacity by depth |
| **rain / snow** | `swarm` on Canvas past a few hundred; `drift` + slight `oscillate` for snow, straight `drift` and motion-blurred strokes for rain |
| **fire / smoke** | `flicker` on the core + `float` + `morph` on the outline + `turbulence` displacement for smoke |
| **solar system** | nested `orbit` (moon inside planet's group) + `rotate` on each body + scale for depth |
| **meteor / comet** | `follow-path` + `draw` for the tail + `pulse` on the head |
| **birds** | `follow-path` with `offset-rotate: auto` + a fast `oscillate` on the wing group + per-bird `stagger` so the flock is not synchronised |
| **walking figure** | `oscillate` on each limb about its joint, phase-offset by π between left and right + a small vertical `float` on the hips at twice the step frequency |
| **traffic** | `drift` at per-vehicle rates + `parallax` between lanes + `scatter` on start offsets |
| **aurora** | `wave` (tiled, very slow) + `breathe` on opacity + additive-looking gradient stacking |
| **lightning** | `draw` on a branching path, very short duration + `flicker` on a full-scene overlay |
| **watch network** | `wave` (tiled sea) + `parallax` by depth + `ripple` per node, staggered, as its report + `flicker` for a degraded node + **the absence of ripple** for a dead one |
| **waterfall** | `drift` on a tiled vertical texture + `ripple` at the base + `turbulence` for spray |

The last row is the one worth studying, and it comes from a real project rather than from weather.
`Ferdinand` is an out-of-band Kubernetes node watchdog named after the South Pacific Coastwatchers —
posts scattered across islands, each seeing only its own patch of sea. Its most important mechanism
is a dead man's switch: `src/deadman/heartbeat.ts` states it as *"the operator is warned by its
silence"*.

So the scene's alert is not a node lighting up. It is a node that **stops** pulsing, with a ring
closing on the gap. That inverts a habit worth naming:

> **An absence can be the animation.** Every primitive here describes something moving; a state that
> matters is sometimes the one where a motion the viewer had learned to expect is missing. That only
> reads if the expected motion was established first — which is why the other four posts must be
> pulsing, staggered, before the silent one means anything.

Two composition rules that generalise:

1. **Depth comes from rate, not from drawing.** Three layers of the same thing moving at different
   speeds read as distance more convincingly than careful shading of a single layer does.
2. **Life comes from decorrelation.** Anything that happens to many instances at once should be
   staggered, and anything periodic should be summed from frequencies that do not share a small
   common multiple. The mechanical look is almost always synchronisation.

---

## The scene-building procedure

1. **List what moves independently.** Each of those is a layer, and each layer is its own `<svg>`
   element — that is what keeps the motion on the free channel.
2. **Assign each layer a depth**, and derive its rate from that depth rather than choosing rates by
   eye.
3. **Pick the primitive per layer** from the table above, preferring the transform channel.
4. **Stagger everything with more than one instance.**
5. **Decorrelate the periods** so no two loops line up.
6. **Write the reduced-motion variant** — fewer instances, no parallax, no scaling, replacement
   rather than removal.
7. **Measure before adding the next layer**, not after adding all of them.
