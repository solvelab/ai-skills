# Measurements

Every number in this directory comes from this table. Nothing here is quoted from an article.

## Method

```
node measure.mjs --all --ms 5000
```

- **Browser**: Google Chrome for Testing 151.0.7922.34, headless (`--headless=new`), window
  1280×720, device scale factor 1.
- **Host**: WSL2 on Linux 6.18, no GPU — rasterisation is software.
- **Harness**: `measure.mjs`, no dependencies. It speaks CDP over Node's global `WebSocket`.
- **Window**: 5000 ms of sampling per prototype, after a 600 ms settle so first-paint cost is not
  counted. First rAF delta discarded.
- **Counters**: `Performance.getMetrics` deltas across the window, normalised per second of
  animation. `presentedFps` counts `Page.screencastFrame` events, which fire once per composited
  frame.

## What these numbers do not cover

Read this before quoting any row.

- **Absolute frame times do not transfer.** Software rasterisation on a machine with no GPU is not
  a desktop and is not a phone. What transfers is the *relative ordering* of two techniques
  measured in the same run on the same machine — which is what every conclusion below rests on.
- **`fps` (the rAF column) is an artifact here, not a quality signal.** The static baseline reports
  37.3 while busy pages report 60: headless Chrome throttles the rAF callback when nothing is
  scheduling work, so a *lower* rAF number can mean *less* work rather than worse animation. Use
  `presentedFps` — composited frames actually produced — as the throughput signal. The baseline's
  `presentedFps` of **0.2** is the proof that column measures what it claims: a page where nothing
  moves composites almost nothing.
- **No paint or raster counter exists.** Checked against this build: the `Performance` domain
  exposes `LayoutCount` and `RecalcStyleCount` and nothing for paint. Raster cost is visible here
  only indirectly, through `presentedFps` dropping.
- **One engine, one device class.** Nothing here says anything about Firefox, Safari, or any
  phone. Every claim below is scoped to Chromium.
- **The prototypes are evidence, not a test suite.** They were measured on 2026-08-30 and nothing
  re-runs them. Treat a number older than the Chrome version it names as a hypothesis again.

## Results

`layout/s` and `style ms/s` are per second of animation. Lower is better everywhere except
`presentedFps`.

| # | prototype | presentedFps | layout/s | style ms/s | task ms/s |
|---|---|---|---|---|---|
| 00 | baseline-static | 0.2 | 0 | 0 | 4.02 |
| 01 | attribute-cx | 59.9 | 60.2 | 22.29 | 74.72 |
| 02 | transform-javascript | 59.9 | 60.2 | 23.64 | 84.38 |
| 03 | transform-css-svg | 59.9 | 37.0 | 27.16 | 60.07 |
| 04 | transform-css-html *(control)* | 59.9 | **0** | 34.34 | 65.15 |
| 05 | transform-smil | 60.0 | 60.2 | 18.69 | 62.30 |
| 06 | transform-web-animations | 60.0 | 37.0 | 21.94 | 49.68 |
| 07 | layers-group-transform | 59.9 | 37.4 | 1.74 | 10.97 |
| 08 | layers-svg-element-transform | 60.0 | **0** | 1.93 | 8.91 |
| 09 | nodes-duplicated | 59.8 | 0 | 1.14 | 7.77 |
| 10 | nodes-use | 60.0 | 0 | 1.07 | 8.85 |
| 11 | filter-turbulence-animated | 59.9 | 0 | 0 | 8.12 |
| 12 | filter-turbulence-static | 59.9 | 0 | 1.45 | 7.44 |
| 13 | particles-svg | **56.7** | 60.0 | 122.64 | **466.40** |
| 14 | particles-canvas | 59.9 | **0** | 0 | 124.83 |
| 15 | morph-javascript | 59.9 | 60.2 | 2.78 | 26.12 |
| 16 | morph-css-path | 60.0 | 60.2 | 11.72 | 26.08 |
| 17 | wave-path-rebuild | 59.9 | 60.2 | 1.04 | 17.85 |
| 18 | wave-transform-tiles | 59.9 | **0** | 1.55 | 7.12 |
| 19 | feldt-canvas-only *(the screen today)* | 0.2 | 0 | 0 | 3.09 |
| 20 | feldt-canvas-plus-layers *(naive)* | 59.8 | **37** | 4.01 | 13.51 |
| 21 | feldt-marks-promoted *(correct)* | 59.8 | **0** | 4.44 | 13.02 |

Structural gauges, read once (`GAUGES=1 node measure.mjs ...`):

| prototype | DOM nodes | layout objects | JS heap |
|---|---|---|---|
| 09-nodes-duplicated (1500 `<path>`) | 1529 | 1513 | 1.1 MB |
| 10-nodes-use (1500 `<use>`) | **4527** | **3012** | 0.7 MB |
| 13-particles-svg (2000 circles) | 2024 | 2009 | 1.7 MB |
| 14-particles-canvas (2000 particles) | **28** | **12** | 1.6 MB |

## What the table says

**1. In SVG, every animation mechanism pays layout per frame. The mechanism is not the variable —
the element type is.**

Rows 01–06 animate the same 300 circles the same distance through five different mechanisms:
a geometry attribute, JS writing `style.transform`, CSS keyframes, SMIL, and the Web Animations
API. All five report layout every frame. Row 04 runs *byte-identical CSS* against HTML `<div>`s and
reports **layout 0**.

This is the single most useful thing in the table, and it contradicts the advice repeated across
the secondary literature — "animate `transform`, not attributes, because `transform` is
GPU-composited". Measured here, moving an SVG child by `transform` costs layout every frame just as
animating `cx` does. The advice is right about HTML and imported wholesale into SVG, where the
control shows it does not hold.

To be precise about what was and was not shown: this measures *layout*, not compositing. It does
not prove SVG children are never composited. It proves the main thread does layout work every frame
for them, and does not for an HTML box running the same animation.

**2. Promote a moving layer to its own `<svg>` element and the per-frame layout goes to zero.**

Rows 07 and 08 build the same parallax starfield — same 600 stars, same drift rates, same node
count. 07 uses `<g>` layers inside one SVG: **37.4 layout/s**. 08 makes each depth a sibling `<svg>`
element positioned by CSS: **0**. An `<svg>` element is an HTML-level replaced box, so animating it
is animating a box, not SVG geometry.

This is a design rule, not a micro-optimisation: *decide the layer boundary by what moves*.
Anything that moves as a unit should be its own `<svg>`.

**3. `<use>` does not reduce runtime cost. It increases it.**

1500 stars as full `<path>` nodes: 1529 DOM nodes, 1513 layout objects. The same 1500 stars as
`<use>` of one `<defs>` symbol: **4527 nodes, 3012 layout objects** — roughly 3× and 2×. Each
`<use>` instantiates a shadow subtree; the renderer does not get to share it.

JS heap moves the other way (0.7 MB vs 1.1 MB) because the path data is stored once, and file size
drops, which is the real reason to use `<use>`: authoring and transfer. Recommending it as a
*performance* technique is unsupported by this measurement.

**4. Animated `feTurbulence` held 60 composited fps at this scale.**

Row 11 animates `baseFrequency` — regenerating a 4-octave fractal noise field over 1200×640 every
frame — and still composited at 59.9. The static-and-translate version (12) is cheaper on the main
thread (7.44 vs 8.12 ms/s) but the gap is small at this size.

The honest reading is narrow: at this resolution and octave count, on this machine, animated
turbulence was not the disaster it is usually described as. The breaking point was **not** searched
for. A larger area or more octaves may well fall over, and this table does not say where.

**5. Particles are where SVG actually breaks, and the number is large.**

2000 particles, identical simulation, identical visual result. SVG: **466 ms of main-thread work
per second of animation** — the main thread is ~47% occupied — and the only `presentedFps` in the
table below 60. Canvas: **125 ms/s**, layout 0, style 0, and 28 DOM nodes against 2024.

3.7× on main-thread time, and the SVG version is already dropping composited frames on a machine
with headroom. This is the clearest switch-to-Canvas signal in the set.

**6. Between morph mechanisms the cost is a wash; the constraint is elsewhere.**

JS rewriting `d` (15) and CSS `d: path()` (16) land at 26.12 and 26.08 ms/s. CSS shifts the work
from script to style (11.72 vs 2.78 ms/s style) and gives up portability: `d` as an animatable CSS
property is Chromium-only. Verified in this build rather than assumed —
`CSS.supports('d', 'path("M0 0")')` returned `true` and the computed `d` was a genuine interpolated
value mid-animation (`M 154.745 ...`).

Neither mechanism escapes the real constraint, which is not cost but geometry: interpolation is
pairwise over numbers, so both paths need the same command sequence. That is a modelling
requirement, not a performance one.

**7. Promoting the container is not enough — the animation has to land on the box.**

Rows 19–21 start from a real screen instead of a fixture: `feldt`'s world map, an archipelago drawn
on a canvas with a camera. Row 19 is that screen as it stands — one baked canvas, no ambient motion,
and a `presentedFps` of **0.2**, the signature of a static picture.

Rows 20 and 21 add identical motion — swell, sked rings, state lamps, the silent-post mark — and
differ only in shape. Row 20 puts the rings inside one shared `<svg>`, which is how anyone writes it
first: **37 layout/s**. Row 21 gives each moving mark its own `<svg>` element and animates *that
element*: **0**.

The intermediate step is worth recording because it was measured and it failed. A first version of
21 promoted each mark to its own `<svg>` but kept animating the `<circle>` inside it, and reported
37 layout/s — identical to the naive form. Promoting the container while still animating a child
buys nothing; the transform has to be on the HTML-level box.

The cost of adding motion at all, on the correct shape: **3.09 → 13.02 ms/s** of main thread, with
layout still at zero.

**8. A seamless tile beats rebuilding geometry, at the price of a period.**

Rebuilding four wave paths from summed sines every frame (17): 17.85 ms/s, layout 60.2/s. The same
four layers as a double-width seamless tile translated by 50% (18): **7.12 ms/s, layout 0** —
2.5× cheaper and off the layout path entirely.

The trade is real and should be stated whenever this pattern is recommended: 17 never repeats,
because its three frequencies are incommensurable. 18 repeats every cycle, and only hides it
because layers roll at rates that are not simple multiples of one another.
