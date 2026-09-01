# Choosing the technology

**The technology is an OUTPUT of the regime, not an input to it.** By the time the regime schema is
answered you know the three things that decide it — how many elements move, whether their geometry
changes every frame, and whether the scene is flat or spatial — so the choice stops being a
preference and becomes a lookup.

Everything below is either measured in this repository or marked as not measured. A claim about a
library's speed that nobody here ran is a guess wearing a brand name, and this file does not carry
any.

## The three questions that decide it

```
1. How many things move independently?          tens · hundreds · thousands
2. Does their GEOMETRY change every frame,
   or only their position/rotation/opacity?     transform-only · rebuilt
3. Is the scene flat, or does it need depth
   that the viewer can move through?            2D · 3D
```

## The decision

| the object is… | use | why, and how well it is known |
|---|---|---|
| tens to a few hundred parts, transform-only, flat | **SVG in this skill** | measured here: the whole catalogue of scenes runs this way |
| the same, but it must stay crisp at any zoom, be styled by CSS, be reachable by a screen reader, or be inspected in devtools | **SVG**, even where canvas would be cheaper | SVG's elements are DOM: that is the whole advantage and it is not a performance one |
| thousands of independent elements, or geometry rebuilt every frame | **Canvas 2D** | measured here: 2000 particles cost **466 ms/s** in SVG against **125 ms/s** on canvas, 2024 DOM nodes against 28 |
| more than a canvas main thread can carry, or per-pixel effects | **WebGL** | NOT measured here. The principle is that the work moves to the GPU and becomes parallel; where the crossover sits on a given machine is exactly the thing this repository has not run |
| a scene with depth the viewer moves through | **hand off to `r3f-*`** | this catalogue already carries nine three.js skills — `r3f-fundamentals`, `r3f-animation`, `r3f-geometry`, `r3f-shaders` and the rest. Do not reimplement 3D here |

## When the answer is not a rendering channel at all

Three cases where the right move is a tool rather than a technique. **None is measured here**, and
what would decide each is named, so the gap is visible rather than papered over.

| situation | tool | what would have to be true, and what is unknown |
|---|---|---|
| the motion is authored by a designer in After Effects and only needs to play back | **Lottie** | it is a player for exported keyframes, so it wins when a human already authored the motion and loses when the motion has to be *computed* from a driver. Nothing here has measured its runtime cost |
| the motion has STATES the user drives — hover, press, a character reacting to input | **Rive** | a state machine is the thing being bought, not the renderer. Unmeasured here |
| the geometry is yours but the ORCHESTRATION is hard — long timelines, staggered sequences, scroll-linked | **GSAP** | it schedules and interpolates; it does not decide what to draw. Unmeasured here |

The distinction that matters across all three: **do you need to PLAY a motion or COMPUTE one?**
A gull's wingbeat is playback. A tree in wind is computation — it is a randomly driven system, so
there is no keyframe sequence that represents it, and reaching for a playback tool there means
reaching for a tool that cannot express the problem.

## What is measured here, and what it costs

The full table is `references/platform.md`. The three findings that most often change a decision:

**Inside SVG every animation mechanism pays layout per frame — the mechanism is not the variable,
the element type is.** Five mechanisms (geometry attribute, JS transform, CSS keyframes, SMIL, Web
Animations) all report layout every frame on SVG children; byte-identical CSS on HTML `<div>`s
reports zero. The common advice "animate transform, not attributes" is right about HTML and false
inside SVG.

**Anything that moves as a unit should be its own `<svg>` element**, because that is an HTML-level
box: `<g>` layers inside one SVG cost 37 layout/s, sibling `<svg>` elements cost 0.

**Canvas moves the cost, it does not remove it.** The dispersive ocean holds 60 fps with zero layout
and still spends 339 ms/s of main thread. And the cost inside canvas is rarely where you expect: the
same sea went 1023 → 673 → 304 ms/s without any change to the geometry, purely by how the fills
were issued.

## Do not choose by what the object IS

"Animals in SVG, particles in canvas, vehicles in WebGL" is a taxonomy, and taxonomies are what this
skill exists to avoid. A flock of two thousand birds is a ballistic ensemble and belongs on canvas;
one bird is an articulated body and belongs in SVG. Same animal, different regime, different
technology — and the regime is what tells you.
