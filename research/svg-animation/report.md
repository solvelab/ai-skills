# SVG animation — research report

Scope: what is true about animating SVG on the web in August 2026, what it costs, and which widely
repeated advice does not survive measurement.

Live showcase, with every scene running and the reduced-motion variant on a switch:
<https://claude.ai/code/artifact/f92ae439-2e51-4977-8f6f-acb481a0c031>

Companion files: [`measurements.md`](measurements.md) (every number, its method and its blind
spots), [`primitives.md`](primitives.md) (the reusable behaviours), [`decision.md`](decision.md)
(where this knowledge should live).

Claims are labelled: **[measured]** here, **[source]** read in a primary document, **[unknown]**
not established.

---

## 0. Before any of this: research the object, or the cost model is worthless

This section exists because the rest of this report was written without it, and the omission
produced exactly the failure it describes.

Everything below §1 is about **cost and channel** — what is cheap to animate, where the layer
boundary goes, when to leave SVG. All of it is true and none of it makes an animation good. The
first version of the birds plate in the showcase obeyed every rule here — `follow-path`,
`offset-rotate`, a wing oscillation, per-bird stagger — and was two mirrored arcs rotating on one
sine at constant span. It was a *symbol* of a bird. The maintainer's verdict on it was that it had
nothing to do with anything, and that was correct.

**A technique catalogue without an observation step produces cheap, fast, wrong animation.**

### The rule

Before drawing or animating a subject, research the subject: how it actually moves, what it is
built out of, what its geometry is, what colours it really carries, and which details a viewer uses
to recognise it. Then animate the mechanism you found, not the impression you remember.

### What that produced for one bird

Reading about wing mechanics before redrawing changed every part of the result:

| What the research said | What the first version did | What it forced |
|---|---|---|
| The cycle has **four phases** — upstroke, US→DS transition, downstroke, DS→US transition | one sine, two phases | four keyframe stops |
| The **downstroke** is the power stroke: down **and forward**, fully extended, elbow straight | a symmetric swing | a forward translation that peaks with the stroke |
| The **upstroke** recovers: up and back, and the wing **partially folds** | constant span | the wing rebuilt as two hinged bones, so folding shortens the span as a *consequence* |
| The halves are **asymmetric in time** — the downstroke is faster | 50/50 | 20/48/64 stops, downstroke shorter |
| Cruising flight has a **shallow** beat | full swing | reduced amplitude at the top |

The span change is the detail that carries the whole thing. Without it an animated bird reads as a
paper cutout no matter how good the easing is — and no easing curve substitutes for it, because it
is a fact about anatomy, not about timing.

The structural lesson generalises past birds: **build the object out of the parts it actually has,
and let the derived motion fall out.** A wing modelled as arm-plus-hand folds correctly for free. A
wing modelled as one rotating shape needs a second fake tween to imitate folding, and the fake is
what reads as wrong.

### What to research, per subject

- **Mechanism** — what physically produces the motion. Joints, hinges, pivots, the thing that
  drives it. Animate that, not the silhouette's path through space.
- **Phases** — almost nothing in nature is a sine. Cycles have named parts with different
  durations, and the asymmetry is usually visible.
- **Geometry** — the real proportions and the shape of each part. Where a wing joins a body is a
  fact; the first version put it at the neck.
- **Colour** — the actual materials, not a hue ramp. See §0b.
- **Scale relations** — a smaller bird beats faster; a bigger island holds more. These ratios are
  observable and free to honour.
- **What the viewer recognises it by** — often one or two details doing all the work. A gull is
  read from its swept hand and its deep chest long before any colour is resolved.

### The view is part of the research

A dolphin and a shark both "swim with the tail", and their mechanics are opposites. Cetaceans
descend from land mammals whose spines flex up and down, so their flukes are **horizontal** and they
oscillate dorsoventrally **[source]**. Sharks descend from fish whose spines flex side to side, so
the caudal fin is **vertical** and they undulate laterally.

Draw both in profile and one of them is a lie: the shark's entire stroke happens in the plane the
viewer cannot see. So in the bestiary the cetaceans are drawn in profile and the shark from above.

**Choose the view in which the mechanism is visible.** It is a research decision, not a styling one,
and getting it wrong cannot be recovered by any amount of drawing skill.

Two more findings from the same pass, both of which contradict the obvious guess:

- The fold in a gull's wing sits at **39% of the half-span, close to the body** — the hand is nearly
  twice the arm. Putting the fold at the midpoint is the classic error and it is what produces the
  wrong wing.
- **Fast lamniform sharks — the great white, the mako — have a near-symmetrical tail**, not the
  upper-lobe-dominant tail of most sharks. The exception is the one everybody draws as the rule.

### How to check it

Render the key poses side by side, frozen, and look at them — the way an animator checks a cycle
before it moves. Every defect in the bird above was invisible in motion and obvious in a strip of
six frozen frames: the wings emerging from the neck, the mixed viewpoint, the joint gap opening as
the elbow rotated, the whole downstroke hidden behind the body.

That check is now the first thing to do, not the last. It caught, in order: wings emerging from the
neck; a mixed viewpoint (mirrored wings, which is the view from below, on a body drawn from the
side); the joint gap opening as the elbow rotated; a patch added to close that gap surfacing as a
lump on the bird's back; and a wedge of background between a dolphin's melon and its trunk. Every
one of them was invisible in motion.

The joint is worth one more line, because the fix that worked is structural rather than cosmetic.
Two rigid shapes meeting along an edge **always** reopen somewhere once their rotations diverge, and
no tuning of the two outlines closes it. A patch that rotates with the far shape eventually escapes
from under the near one. What works is geometry: extend the parent shape **past the pivot**, so that
because it does not rotate with the child, it covers the child's root at every angle.

### Draw a body from a thickness table, not from guessed curve handles

The bestiary's first draft was written the way most SVG illustration is written: by typing Bézier
control points and adjusting them until the shape looked acceptable at thumbnail size. Rendered
large against a grid it was indefensible — a hole between the melon and the rostrum, a rectangular
step where one hand-written path met the next, a belly patch floating clear of the body, a rostrum
that had become a bird's bill.

None of those are drawing mistakes. They are the predictable output of the method. Independent
paths tuned by eye do not meet, and cannot be checked against anything.

**A fusiform body is not a set of curves. It is a thickness function.** At each station along the
axis there is a distance up to the back and a distance down to the belly. Write the table, walk the
stations, and emit one closed outline through them:

```js
const body = [
  { x: 0.000, back: 0.012, belly: 0.012 },   // tip of the rostrum
  { x: 0.058, back: 0.032, belly: 0.030 },   // rostrum, near-cylindrical
  { x: 0.072, back: 0.058, belly: 0.034 },   // THE CREASE — the melon rises abruptly
  { x: 0.140, back: 0.094, belly: 0.060 },   // crown of the melon
  { x: 0.340, back: 0.108, belly: 0.100 },   // maximum girth, 34% back — not the middle
  ...
]
```

Three things follow, and each one removes a class of defect outright:

- **The silhouette is continuous by construction.** There is one path, so there is nothing to
  misalign. The hole and the step cannot occur.
- **Every number is a proportion that can be checked against the animal.** "Maximum girth at 34%"
  is verifiable; a curve handle at `C -3.4 -8.6` is not. Fractions of body length also make the
  final scale a single multiplier.
- **Derived shapes inherit the table.** The dolphin's countershaded belly is the same table with the
  lower half scaled, so it cannot drift off the body — which is exactly what it did when it was a
  separate hand-written path.

The same table drives the plan view by reading the column as half-width instead of back and belly,
which is how the shark is built.

What still has to be tuned by hand is what attaches to the body — fins, flippers, the wing of a
bird. For those the rule from §0 applies: root the attachment INSIDE the outline, and where a part
rotates, extend its parent past the pivot.

### A rotating part goes UNDER the part it hinges from

The dolphin and the whale both showed a step cut across the back, the belly and the countershading,
right where the tail met the trunk. It was not a curve that needed adjusting: the tail segment was
being drawn **after** the body, so its own outline sat on top and its edge became a seam.

Reversing the order — build the tail first, paint the trunk over its root — removed the defect from
both animals at once and needed no change to either shape.

The general form, which also fixed the gull's wing:

> **Draw the rotating child first, then the parent over its root. Where that is impossible, extend
> the parent past the pivot.** A join between a moving part and a still one is only invisible while
> one of them covers the other's edge; two outlines that merely meet will separate at some angle of
> the rotation, and no tuning of either outline prevents it.

### An appendage is species-specific. Do not reuse it.

The sharpest correction in this whole exercise: the dolphin and the humpback were given the *same*
pectoral geometry at different scales, and the maintainer's response was that the flipper made no
sense because **the geometry of each animal is different**. It was right, and the error is worth
naming because it is the natural one to make once a body-building method exists.

They are not the same organ at two sizes:

| | dolphin | humpback |
|---|---|---|
| length | ~0.14 L | **~0.30 L** — a third of the animal, hence *Megaptera*, "big wing" |
| shape | short, broad-rooted paddle, slightly falcate | long, narrow, gently arced |
| leading edge | smooth | **rounded tubercles** |
| tip | tapered | **rounded** |
| colour | body colour | pale below — it is the light shape on a dark animal |

Getting this wrong is not a rendering flaw, it is a claim about the animal. And the fix is not
finer tuning of one flipper: it is refusing to share the shape at all.

Two attempts failed before the third worked, and the failures are instructive. Generating the
flipper from an axis plus a chord function produced a **saw blade** (straight axis, uniform teeth),
then a **ribbon** (curved axis, but no control over width or tip). Written as an explicit outline —
where each pair of curves is one tubercle and the tip is an arc — it came out right first time.

**Procedural generation is right for the body and wrong for the appendages.** The body has many
stations and a smooth rule, so a table wins. A flipper has perhaps eight meaningful features, and
writing them down directly beats deriving them from parameters that then have to be tuned blind.

### Proportions belong in units of the whole

Also taken from the maintainer's `Gulls.tsx`, which had already learned this: express every measure
as a fraction of total length, so the final scale is a single multiplier. For *Larus argentatus* —
wingspan 2.30 L, bill 0.090 L, tail 0.279 L, skull 0.10 L. Checked against those, the first head
here was 0.15 L and the bill 0.13 L, both far too large, which is why it read as a cartoon. The
numbers are free to look up and they remove an entire class of "something is off but I cannot say
what".

## 0b. Colour comes from materials, not from a hue ramp

Taken from `feldt`, a project in the same workspace whose archipelago is markedly better drawn than
the first draft of this research, and worth studying for why.

Its palette does not have "green" and "blue". It has **twenty-one named materials**, in two complete
themes:

```
mar, recife, areia, grama, mata, mataCerrada, lago, pantano, rocha, cume,
tronco, copaEscura, copaMedia, copaClara, sombraChao, onda,
raso, abissal, vulto, dorsal, esteira
```

Sea, reef, sand, grass, woodland, dense woodland, lake, marsh, rock, summit, trunk, three canopy
depths, ground shadow, wave — and then, for the sea's life, shallows, abyss, shape, dorsal, wake.
Each name is a thing that exists, and each colour was chosen for that thing.

The scenes in this research used `hsl(88 + rand() * 34, 42%, ...)` — a hue ramp with noise, which is
what "make it look natural" produces when nobody looked at anything. The difference is visible
immediately and it is not subtle.

Three more techniques worth stealing outright from that code, each cheap and each worth more than a
performance trick:

- **Volume from stacked layers, not from detail.** Its tree is three ellipses, each narrower and
  lighter than the one below, over a trunk — with the comment *"it is what gives volume without
  drawing a single leaf"*. No gradient, no texture, no per-leaf geometry.
- **A declared light direction.** Ground shadows are short *because the light comes from above*, and
  that is written down. A scene where every shadow agrees reads as solid; one where they disagree
  reads as collage.
- **Distribution by Poisson disk, not by `Math.random()`.** Bridson sampling with a minimum spacing
  gives scatter that looks natural because it has no clumps and no voids. Uniform random has both,
  and clumps are exactly what the eye reads as "generated".

And one rule about restraint that belongs in any skill for on-call screens, quoted from that code:
fish are drawn on the map but never on the board, because on the board they would be *"movement
where the screen asks for reading"*. Motion is not free of meaning. Adding it where nothing changed
is a lie about the state of the system.

## 1. The five mechanisms, and why the choice matters less than people think

SVG can be animated five ways. The SVG 2 specification lists them itself and declines to require
any of them: *"SVG does not mandate support for any of these animation methods"* **[source:
w3.org/TR/SVG2/animate.html]**.

| Mechanism | Timeline owner | Runs without script | Portable |
|---|---|---|---|
| SMIL (`<animate>`, `<animateTransform>`, `<animateMotion>`) | browser | yes, even inside `<img>` | all current engines; **not in SVG 2** |
| CSS animations / transitions | browser | yes | universal |
| Web Animations API | browser | no (script builds it) | universal |
| Script writing attributes | you | no | universal |
| Script writing `style.transform` | you | no | universal |

**SMIL's status is genuinely confusing and worth stating precisely.** Chrome announced an intent to
deprecate it in 2015 and withdrew after developer pushback — path morphing and animation inside
`<img>`-referenced SVG had no replacement **[source: blink-dev intent-to-deprecate thread]**. It
still ships in every current engine. It is not part of SVG 2. So: safe to use today, with no
standards track behind it. The one thing it does that nothing else does is animate an SVG that is
loaded as an image, where CSS and script never run.

**[measured]** The mechanism you pick barely changes the cost. Prototypes 01–06 animate the same
300 circles the same distance through all five, and every one of them does layout every frame.
The mechanism is not the variable.

## 2. The finding that matters most: it is the element type, not the property

The advice you will find everywhere is: *animate `transform` and `opacity`, because those are
GPU-composited; never animate geometry attributes*. For HTML, that is correct and well sourced —
Chrome documents `opacity`, `filter` and `transform` as the hardware-accelerated set **[source:
developer.chrome.com/blog/hardware-accelerated-animations]**.

Imported into SVG, it does not hold.

**[measured]** Same scene, same motion, five mechanisms, plus one control:

| what animates | layout/s |
|---|---|
| `cx` attribute, by JS | 60.2 |
| `transform`, by JS | 60.2 |
| `transform`, by CSS keyframes, on `<circle>` | 37.0 |
| `transform`, by SMIL | 60.2 |
| `transform`, by Web Animations API | 37.0 |
| **`transform`, by the same CSS keyframes, on `<div>`** | **0** |

Moving an SVG child by `transform` costs layout every frame. Moving an HTML box by the identical
declaration costs none. The literature's rule survives; its scope does not.

Stated carefully, because the distinction matters: this measures **layout**, not compositing. It
does not prove SVG children are never composited. It proves the main thread does layout work every
frame for them and none for an HTML box doing the same thing. Whether the paint that follows is
composited was **[unknown]** at the end of this work — see §8.

### The rule that follows

**Decide your layer boundary by what moves.** Anything that moves as a unit should be its own
`<svg>` element, positioned and animated by CSS as an HTML box. Anything that does not move can sit
inside as ordinary SVG children.

**[measured]** The same parallax starfield — 600 stars, 5 depths, identical drift — built both
ways: `<g>` layers inside one SVG cost **37.4 layout/s**; sibling `<svg>` elements cost **0**.

This one rule is worth more than every other performance tip in this report combined, because it
turns the expensive channel into the free one without changing the picture.

## 3. Node count: `<use>` is not a performance technique

The standard advice is to declare a shape once in `<defs>` and stamp it with `<use>` to keep the
DOM small.

**[measured]** 1500 stars, drawn both ways:

| | DOM nodes | layout objects | JS heap |
|---|---|---|---|
| 1500 full `<path>` | 1529 | 1513 | 1.1 MB |
| 1500 `<use>` of one symbol | **4527** | **3012** | 0.7 MB |

`<use>` roughly **tripled** node count and **doubled** layout objects. Each `<use>` instantiates a
shadow subtree; the renderer does not share it the way the author imagines.

`<use>` is still worth using — for file size, for authoring, for keeping one definition of a shape.
It is not a runtime-cost technique, and recommending it as one is unsupported.

## 4. When to leave SVG

**[measured]** 2000 particles, identical simulation and identical visuals:

| | main-thread ms per second | layout/s | style ms/s | DOM nodes | composited fps |
|---|---|---|---|---|---|
| SVG circles | **466.4** | 60.0 | 122.6 | 2024 | **56.7** |
| Canvas 2D | **124.8** | 0 | 0 | 28 | 59.9 |

3.7× on main-thread time. The SVG version is the only prototype in the whole set that failed to
hold 60 composited fps, on a machine with headroom.

### The decision rule

- **SVG** — when the graphic has *identity*: things that need to be styled by CSS, hit-tested,
  linked, read by assistive technology, or authored in a vector tool and handed over. Tens to low
  hundreds of animated elements.
- **Canvas 2D** — when the graphic is a *field*: many small things that are not individually
  meaningful. Particles, rain, snow, embers, dust, sparks. The crossover in this measurement is in
  the hundreds, not the thousands.
- **WebGL** — when the per-particle work is itself the cost: tens of thousands of elements, or
  per-pixel effects (real fluid, volumetric light, heavy blur fields). Also when the effect is
  fundamentally a shader — plasma, refraction, displacement — where doing it on the CPU is the
  wrong shape regardless of count.

A scene may use all three in layers: SVG for the shapes with meaning, Canvas for the field, and the
composition handled by ordinary CSS stacking.

## 5. Filters

**[measured]** Animating `feTurbulence`'s `baseFrequency` — regenerating a 4-octave fractal noise
field over 1200×640 every frame — held **59.9 composited fps** and cost **8.12 ms/s** of main
thread. Generating the field once and translating the result cost **7.44 ms/s**.

At this scale, on this machine, animated turbulence was not the catastrophe it is usually called.

**[unknown]** Where it breaks. The breaking point was not searched for: a larger surface, more
octaves, or a device without headroom may well fall over, and nothing here says where. Treat
animated turbulence as "measure it in your scene", not as "free" and not as "forbidden".

What *is* safe to say: generating noise once and moving it is never more expensive, and it is the
pattern that scales, because translation is the free channel (§2).

## 6. Morphing

**[measured]** Rewriting `d` from JS (26.12 ms/s) and declaring the interpolation in CSS with
`d: path()` (26.08 ms/s) cost the same. CSS moves the work from script to style and gives up
portability — `d` as an animatable CSS property is Chromium-only. Verified in this build rather
than assumed: `CSS.supports('d', 'path("M0 0")')` returned `true`, and the computed value
mid-animation was a genuine interpolated path.

The real constraint on morphing is not cost, it is geometry. **Interpolation is pairwise over
numbers, so both paths must have the same command sequence** — same count, same types, same order
**[source: consistent across every morphing library's documentation]**. A star with 10 points cannot
become a circle with 4 curves without something resampling one of them first.

Three ways out, in order of preference:

1. **Author both shapes with the same command count.** Free, exact, no library. This is what
   prototype 15 does — both blobs are 8 cubic segments by construction. If you control the artwork,
   this is the answer.
2. **Resample at build time.** Convert both paths to a common sample count once, ship the result.
   Cost moves out of the runtime entirely.
3. **Resample at runtime** with a library — GSAP's MorphSVG or Flubber. Correct for arbitrary
   shapes, and the only option when the shapes are not known in advance.

## 7. Accessibility: `prefers-reduced-motion` is not an off switch

The most common implementation error is treating `reduce` as "disable all animation". The
specification is explicit that it means the user *"prefers an interface that removes, **reduces, or
replaces** motion-based animations"* **[source: MDN]**.

The distinction is not pedantry. Vestibular triggers are large-area movement, parallax, scaling and
panning — not change as such. A fade, a colour shift, or a slowed-down version is usually the right
answer, and killing an animation that communicated state leaves the interface *less* usable.

```css
/* Default: the full motion. */
.cloud { animation: drift 40s linear infinite; }

/* Reduced: replace the motion, keep the life. */
@media (prefers-reduced-motion: reduce) {
  .cloud { animation: breathe 12s ease-in-out infinite; }  /* opacity only, no travel */
}
@keyframes breathe { 0%, 100% { opacity: .75 } 50% { opacity: .95 } }
```

```js
const calm = matchMedia('(prefers-reduced-motion: reduce)')
if (calm.matches) { /* fewer particles, no parallax, shorter travel */ }
calm.addEventListener('change', rebuild)   // the setting can change while the page is open
```

Two rules that follow:

- **Never gate the whole scene behind a single `if`.** Reduce the motion budget: fewer particles,
  no parallax, no scaling, shorter travel — the scene still lives.
- **Listen for changes.** The preference can flip while the page is open; a page that only reads it
  at startup is wrong for the rest of the session.

## 7b. Two transform traps that cost real time

Both were found by rendering the scenes and looking at the result, not by reading. Both are
SVG-specific and neither appears in the performance advice that dominates search results.

**`transform-origin` starts at `0 0` in SVG, not at the centre.** For an HTML box the initial value
is `50% 50%`; for an SVG element it is the user-space origin. So `transform: scale(1.07)` on a
`<circle>` does not swell it in place — it moves it as well. In the first render of the solar-system
scene the sun's halo drifted visibly off the sun for exactly this reason.

The fix is `transform-box: fill-box`, which makes percentage origins resolve against the element's
own bounding box and restores the behaviour every author already expects:

```css
svg circle, svg ellipse, svg path, svg rect, svg g {
  transform-box: fill-box;
  transform-origin: center;
}
```

**But `transform-box: fill-box` re-resolves the coordinates inside a `transform` attribute.** A
`transform="rotate(30 400 250)"` written in user space is re-interpreted against the element's own
box once fill-box is in effect — in the tree scene, every leaf was flung out of the canopy the
moment the rule above was added.

So the two rules interact, and the resolution is a choice per element:

- Rotating or scaling an element **about itself** → `fill-box`, and write `rotate(deg)` with no
  centre.
- Rotating about a **point in user space** — a branch about its joint, a planet about its star →
  `transform-box: view-box` and an explicit `transform-origin`, opting out of the blanket rule.

The tree and the solar system in the model scenes each carry one of these, with the reason inline.

## 8. What this work did not settle

Stated plainly, per `verify-before-claiming`, instead of filled with a plausible answer.

**Whether SVG children are composited in current Chromium.** Three readings disagree: the Chrome
blog says hardware acceleration was enabled by default for SVG animations as of Chromium 89
**[source]**; the Blink `core/animation/README.md` at tag 85 said Chromium does not support
compositor-thread animation of elements with SVG transforms **[source]**; and the same file on
`main` today does not mention SVG at all — which is not evidence that the limitation was removed.

What was tried: reading all three; then measuring. The measurement settles the *layout* question
decisively (§2) and cannot settle the compositing question, because the `Performance` domain
exposes no paint or raster counter — checked against this build, the metric list has `LayoutCount`
and `RecalcStyleCount` and nothing for paint. Resolving it properly needs trace-level capture,
which was out of scope here.

The practical consequence is nil: the layout finding already dictates the design rule in §2. But
the compositing question is open, and this report does not pretend otherwise.

**Also not established:** where animated filters break (§5); anything at all about Firefox or
Safari; anything about phones. Every number here is one engine on one machine.

## 9. Libraries

The landscape changed materially in 2025 and any older advice about it is stale.

- **GSAP** became free in its entirety on 2025-04-30 under Webflow, including the plugins that were
  paid — MorphSVG, DrawSVG, SplitText, ScrollTrigger, Inertia **[source: Webflow blog, GSAP standard
  licence]**. Core is roughly 25 kB. The licence carries one restriction: it may not be used to
  build a no-code visual animation tool that competes with Webflow. For SVG specifically, MorphSVG
  is the mature answer to arbitrary-shape morphing.
- **Anime.js v4** — roughly 17 kB minified and gzipped, ES modules, explicit SVG support
  **[source: project README / npm]**. The lighter choice when the motion is a handful of tweens.
- **Web Animations API** — no bundle at all, universal, and the right default for anything a
  keyframe can express. **[measured]** it costs the same as the alternatives on SVG (§2), so the
  reason to reach past it is expressiveness, not speed.

**The default should be no library.** Everything in the prototypes here — parallax, waves, morphing,
particles, seamless loops — is plain CSS and a few lines of script. Reach for a library when you
need arbitrary-shape morphing, scroll orchestration, or timeline sequencing with many interacting
parts; those are real problems that are tedious to solve by hand.

## 10. Techniques not recommended, with the reason

- **Animating `transform` on SVG children and believing it is free.** **[measured]** It costs layout
  every frame (§2). Use it — but for correctness of the picture, not as a performance measure.
- **`<use>` to make a scene faster.** **[measured]** It makes the node graph bigger (§3).
- **`will-change: transform` on many elements.** Each promotion is a compositor layer with memory
  behind it; applying it broadly trades one cost for a worse one **[source: Chrome documentation]**.
  Put it on the handful of layers that actually move — which, if §2 is followed, is a handful.
- **One SVG containing the whole animated scene.** It forces every moving thing into the expensive
  channel. Split by what moves.
- **Thousands of SVG nodes for a particle field.** **[measured]** §4.
- **`prefers-reduced-motion` as an off switch.** §7 — the specification says reduce or replace, and
  removing state-communicating animation makes the interface worse.
- **Animating an impression of a subject instead of its mechanism.** §0 — the catalogue of
  primitives is a set of tools, not a substitute for looking at the thing.
- **Reusing one appendage shape across species.** §0 — a dolphin's flipper and a humpback's are
  different organs, not one shape at two scales.
- **Drawing an organic body by typing Bézier handles and adjusting by eye.** §0 — it produces
  outlines that do not meet and numbers nobody can check. Use a thickness table.
- **Colour from a hue ramp with noise.** §0b — it is the visual signature of work where nobody
  observed the subject.
- **Assuming SVG `transform-origin` behaves like HTML's.** §7b — it starts at `0 0`, and a `scale`
  or `rotate` silently translates the element.
- **Rebuilding geometry every frame when a seamless tile would do.** **[measured]** 17.85 ms/s and
  60.2 layout/s versus 7.12 ms/s and 0 (§ prototypes 17/18). Pay it only when you genuinely need
  non-repeating motion, and know that you are buying the absence of a period.

---

## Sources

Primary documents read for this report:

- [SVG 2 — Animation](https://www.w3.org/TR/SVG2/animate.html) — W3C
- [Updates in hardware-accelerated animation capabilities](https://developer.chrome.com/blog/hardware-accelerated-animations) — Chrome for Developers
- [`blink/renderer/core/animation/README.md`](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/third_party/blink/renderer/core/animation/README.md) — Chromium source, `main`
- [Intent to deprecate: SMIL](https://groups.google.com/a/chromium.org/g/blink-dev/c/5o0yiO440LM/m/YGEJBsjUAwAJ) — blink-dev
- [`prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion) — MDN
- [The Web Animation Performance Tier List](https://motion.dev/magazine/web-animation-performance-tier-list) — Motion
- [GSAP is now completely free](https://webflow.com/blog/gsap-becomes-free) — Webflow · [Standard licence](https://gsap.com/community/standard-license/)
- [anime.js](https://github.com/juliangarnier/anime) — project repository

Not used as backing for any claim: several high-ranking results (`svgai.org`, `zigpoll`, `boundev`)
carry the marks of generated content at scale — confident performance numbers with no method, no
browser and no reproduction. Their absence here is deliberate.
