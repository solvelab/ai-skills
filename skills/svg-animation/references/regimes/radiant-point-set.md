# Regime: radiant point set

Many point sources seen through a medium: a starfield, distant city lights, plankton, embers at a
distance.

The regime that exists because of a **category error**, not a missing number.

## Must be known before drawing

| # | question | the measured defect that put it here |
|---|---|---|
| 1 | **THE DISTANCE REGIME.** | The old recipe was `scatter + flicker + PARALLAX`. Parallax on a starfield is meaningless: stars are effectively at infinity, so there is no depth for the viewer's motion to reveal. Layers drifting at different speeds is a physical impossibility dressed as a depth cue. Ask first whether the set HAS depth. |
| 2 | **What actually moves, if anything.** | The sky turns RIGIDLY about the celestial pole at 15.041 deg/hour. One transform on one layer — which is also the cheapest thing in the measurement table. |
| 3 | **The brightness distribution.** | Each magnitude is 2.512x, and counts rise as `10^0.6m`: ~4 stars brighter than m=1, ~1100 brighter than m=5, ~8700 to the naked-eye limit. Invert that rather than sampling magnitude uniformly. |
| 4 | **What the medium does, as a function of path length.** | Kasten & Young airmass: 1.02 at 80° altitude, 5.59 at 10°. Extinction 0.28 mag per airmass; scintillation grows as airmass^1.75. The horizon empties and reddens without anyone drawing an emptiness. |
| 5 | **What does NOT twinkle, and why.** | A planet shows a disc a few arcseconds across, so the speckle averages out. A steady light among trembling ones is the clearest way to say "atmosphere", and twinkling everything cannot say it. |
| 6 | **The display's dynamic range.** | Naked-eye magnitudes span 3000:1 in light and a screen has 256 levels, so a flux-proportional alpha renders everything past m=5 as nothing. The eye's own response is logarithmic: MAGNITUDE maps to alpha. And a screen pixel is the smallest thing there is — below it a faint source stops being faint and starts being absent. |
| 7 | **Timescale of the variation.** | Turbulent cells cross the line of sight in 5-50 ms: tens of Hz, not the ~1 Hz a "twinkle" animation usually gets. |

## Failure signature

- parallax layers on objects at infinity
- everything twinkling at the same rate
- the field vanishing when alpha was made proportional to flux
