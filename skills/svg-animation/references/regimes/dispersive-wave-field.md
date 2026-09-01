# Regime: dispersive wave field

Open water, swell, ripples. The defining property: **each wavelength travels at its own speed**, so
trains overtake one another and where they briefly add you get a GROUP that forms, travels and dies.
That is the most recognisable thing the sea does and no translating tile can produce it.

## Must be known before drawing

| # | question | the measured defect that put it here |
|---|---|---|
| 1 | **The dispersion relation.** | `c = sqrt(gL/2π)` in deep water. The old scene chose periods (11/17/23/29/35 s) against fixed harmonics — speed and wavelength picked separately, which the physics forbids. 12x the wavelength is only 3.4x the speed, because celerity goes as the square root. |
| 2 | **Which way is near.** | The nearest band rolled in 35 s and the furthest in 11 s. Near moves faster. Always. |
| 3 | **The sea state, from the wind.** | Fully developed at U: `Hs = 0.21·U²/g`, peak period from `ωp = 0.877g/U`. One root quantity per train — the wavelength — and period, celerity and steepness limit all follow. |
| 4 | **Crest shape.** | NOT a sine. Stokes 2nd order `η = A[cos θ + (Ak/2)cos 2θ]`: peaked crests, broad flat troughs. Breaking at `H/L = 1/7` (Michell), crest angle 120°. |
| 5 | **WHAT YOU ARE NOT DRAWING.** | Four wave trains carry a slope variance of 0.0054 against Cox & Munk's measured 0.0491 — **89% of the sea's slope lives in waves too short to draw**. So sun glitter cannot be a test on the drawn surface; it is a PROBABILITY, Gaussian in the residual slope with σ = 0.209. Modelling the unresolved roughness explicitly is what made the glitter path appear. |
| 6 | **Both axes of the specular condition.** | Along the view the required facet tilt is set by range; ACROSS it, a patch seen off the sun's bearing must tilt sideways by half that bearing. Leaving the second one out put glints over the entire sea, because the roughness is wide enough to satisfy the first everywhere. |
| 7 | **Breaking rate, if foam appears.** | Whitecap coverage `W = 3.84e-6·U^3.41` — 0.69% at 9 m/s. Foam is a fleck on a crest, not a texture. And the drawn trains never reach Michell's limit: the waves that actually break are the short ones you are not resolving. |
| 8 | **Sampling limit.** | A train whose screen wavelength falls below two samples cannot be drawn, and drawing it anyway is moire. Fade it out between four samples and two. |

## Perspective

For a horizontal-looking camera, still water at range D lands at `y = yh + f·h/D` and an elevation
η lifts it by `f·η/D`. **Slope is preserved by this projection**, so the world gradient is the visual
one and shading needs no extra transform.

## Failure signature

- a shape that slides instead of trains that pass through each other → no groups, and the sea reads
  as a moving picture of a sea
- glints scattered at fixed heights → a glint can only be where the geometry allows it
- sine crests → the troughs are as narrow as the crests, which no gravity wave has
