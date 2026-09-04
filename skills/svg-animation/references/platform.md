# Platform: what SVG, CSS and Canvas actually cost

Every number here was measured with `measure.mjs`, a dependency-free CDP harness kept in the
catalog repository, outside the installed skill
([research/svg-animation](https://github.com/solvelab/ai-skills/tree/master/research/svg-animation)),
against Chrome for Testing 151.0.7922.34, headless, software rasterisation, one machine,
2026-08-30/31. **What transfers is the relative ordering of two techniques measured in the same run**
— absolute frame times on a machine with no GPU are not a desktop and are not a phone.

## The finding that contradicts the advice everywhere else

**In SVG, every animation mechanism pays layout per frame. The mechanism is not the variable — the
element type is.**

Five mechanisms moving the same 300 circles the same distance — a geometry attribute, JS writing
`style.transform`, CSS keyframes, SMIL, the Web Animations API — all report layout every frame.
Byte-identical CSS against HTML `<div>`s reports **layout 0**.

"Animate `transform`, not attributes, because `transform` is GPU-composited" is right about HTML and
imported wholesale into SVG, where the control shows it does not hold.

## The design rule that follows

**Decide the layer boundary by what moves.** Anything that moves as a unit gets its own `<svg>`
element — an `<svg>` is an HTML-level replaced box, so animating it is animating a box.

| | layout/s |
|---|---|
| parallax as `<g>` layers inside one SVG | 37.4 |
| the same layers as sibling `<svg>` elements | **0** |

Promoting the container is not enough. A version that promoted each mark to its own `<svg>` but kept
animating the `<circle>` inside reported 37 layout/s — identical to the naive form.

## Where SVG breaks, with the number

2000 particles, identical simulation, identical result: SVG **466 ms/s** of main thread (~47%
occupied, and the only measurement below 60 composited fps) against canvas **125 ms/s**, 28 DOM
nodes versus 2024. **This is the switch-to-canvas signal.**

## Canvas is not free either, and the cost is not where you think

The ocean scene, same picture three ways:

| | task ms/s |
|---|---|
| one `Path2D` per shade bucket, 26 `fill()` calls | **1023** |
| each quad filled immediately as computed | 673 |
| `fillRect` per quad | **304** |

Every `fill()` rasterises over the path's whole BOUNDING BOX, and each bucket's box was the entire
sea. Cutting the quad count by two thirds recovered only 20%, because the cost was never the
geometry. The same lesson in the sky: 7000 stars via `beginPath/arc/fill` cost 346 ms/s, and most
are one or two pixels across where a square and a circle are the same picture — `fillRect` for
those, a real disc only for the few big ones: 280 ms/s.

## `<use>` does not reduce runtime cost. It increases it.

1500 stars as `<path>`: 1529 DOM nodes, 1513 layout objects. The same 1500 as `<use>` of one symbol:
**4527 nodes, 3012 layout objects**. Each `<use>` instantiates a shadow subtree. Heap goes the other
way (0.7 MB vs 1.1 MB) and file size drops — which is the real reason to use it: authoring and
transfer, not performance.

## Simulating can be cheaper than animating

| tree version | style ms/s | task ms/s |
|---|---|---|
| CSS keyframes on ~250 elements | 87.9 | 284.9 |
| one rAF loop integrating ~250 damped oscillators | **10.5** | **58.8** |

The keyframe machinery is not free. Four times in this work the truer version was also the cheaper
one — often enough that it is worth checking before assuming a trade-off exists.

## Traps that break silently

**`transform-box: fill-box` re-resolves the coordinates inside a `transform` ATTRIBUTE**, so
`rotate(a cx cy)` stops meaning what it says. This has dismembered a figure three separate times in
this work. Anything driven by the transform attribute must pin `transform-box: view-box` and
`transform-origin: 0 0` itself. A global stylesheet rule that changes what an attribute means is a
landmine.

**SVG's initial `transform-origin` is `0 0`, not `50% 50%`.** A `scale()` or `rotate()` on an SVG
child moves it as well as transforming it.

**A canvas needs `object-fit: cover` to match `preserveAspectRatio="xMidYMid slice"`.** Without it
the canvas stretches while an SVG overlay crops, and every marker drifts off the thing it marks.

**Adjacent quads in different `Path2D` objects antialias their shared edge against whatever is
already there**, producing a pale hairline grid. Overlap by a fraction of a pixel.

**`presentedFps` low is not automatically bad.** A lightning scene reports 8.5 because it is dark
between flashes. A static page reports 0.2. The column measures composited frames, which is what it
claims.

## Cost of the finished scenes

| scene | presentedFps | layout/s | style ms/s | task ms/s |
|---|---|---|---|---|
| ocean, dispersive on canvas | 59.9 | 0 | 0 | 339 |
| starfield | 59.9 | 0 | 0 | 280 |
| rain | 59.9 | 0 | 0 | 120 |
| clouds, one `<svg>` per cloud | 56.1 | **0** | 14.0 | 53 |
| tree, simulated | 60.0 | 60.3 | 10.5 | 58.8 |
| solar | 59.8 | 60.3 | 5.6 | 40 |
| walker | 59.9 | 60.3 | 8.3 | 49 |

Re-measure anything older than the browser version it names. A number past its Chrome version is a
hypothesis again.
