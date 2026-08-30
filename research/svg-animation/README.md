# research/svg-animation

Backing evidence for issue #107: what is true about animating SVG, what it costs, and where that
knowledge should live in this catalog.

This directory sits **outside `skills/`** on purpose. `generate.sh` publishes only `skills/`, so
everything here is versioned and reviewable without being shipped to any project that enables a
plugin.

## Read in this order

| File | What it is |
|---|---|
| [`report.md`](report.md) | The research. Every claim labelled measured / source / unknown. |
| [`measurements.md`](measurements.md) | Every number, its method, and what it does not cover. |
| [`primitives.md`](primitives.md) | The reusable behaviours and how scenes compose from them. |
| [`decision.md`](decision.md) | Where this should live: a new `svg-animation` skill, and why. |

## Live showcase

<https://claude.ai/code/artifact/f92ae439-2e51-4977-8f6f-acb481a0c031>

Nine scenes and twelve primitives running, each naming the technique and the measured cost behind
it, plus a switch that demonstrates the reduced-motion variant without changing your OS setting.

The ninth scene is taken from `ferdinand`, a real out-of-band Kubernetes node watchdog, and animates
its dead man's switch: the alert is the post that stops transmitting. It is there because a
vocabulary that only produces weather has not been shown to carry meaning.

The page is **generated** from `scenes/scenes.js` by `build-showcase.mjs` — it is a view of this
directory, never a second implementation. If the two disagree, this directory is right and the page
was not rebuilt.

## Running things

Everything here runs by opening a file. No build step, no server, no `npm install`.

```bash
# See the model scenes
xdg-open scenes/index.html

# See one comparison prototype
xdg-open prototypes/13-particles-svg.html

# Re-measure everything (needs a Chrome; set CHROME_PATH if it is not in the usual places)
node measure.mjs --all --ms 5000

# Structural gauges instead of per-frame counters
GAUGES=1 node measure.mjs prototypes/09-nodes-duplicated.html prototypes/10-nodes-use.html

# Rebuild the showcase after changing a scene
node build-showcase.mjs
```

`measure.mjs` has no dependencies: it drives Chrome over the DevTools Protocol using the `WebSocket`
that Node 22+ provides as a global.

## The prototypes

Numbered in pairs. Each pair holds everything constant except the one thing under test.

| Pair | Question |
|---|---|
| 00 | baseline — the floor for every other number |
| 01–06 | five animation mechanisms on SVG, plus the HTML control that isolates the cause |
| 07 / 08 | parallax as `<g>` layers vs sibling `<svg>` elements |
| 09 / 10 | duplicated path nodes vs `<use>` of one symbol |
| 11 / 12 | animated `feTurbulence` vs generated-once-and-translated |
| 13 / 14 | 2000 particles in SVG vs on a canvas |
| 15 / 16 | morphing by JS vs by CSS `d: path()` |
| 17 / 18 | waves rebuilt per frame vs a seamless translated tile |

## Status

Evidence, not a maintained test suite. Measured 2026-08-30 against Chrome for Testing
151.0.7922.34, headless, software rasterisation, one machine. A number older than the browser
version it names is a hypothesis again.
