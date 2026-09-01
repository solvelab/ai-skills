# Regime: ballistic ensemble

Many small bodies falling or flying under drag: rain, snow, sparks, spray, dust, leaves in air.

This regime taught the rule that then appeared in every other one.

## Must be known before drawing

| # | question | the measured defect that put it here |
|---|---|---|
| 1 | **The ONE root quantity, and everything derived from it.** | Rain drew speed and streak length from INDEPENDENT random ranges, so a small drop could out-fall a large one. Terminal velocity is a function of diameter — `v = 9.65 − 10.3·exp(−0.6d)`, the Gunn & Kinzer fit — and a streak is motion blur, so its length is velocity times exposure. One roll of the dice now sets size, speed, streak and opacity together, and they cannot contradict each other. |
| 2 | **The size distribution.** | Marshall-Palmer: small drops vastly outnumber large ones. Sampling diameter uniformly gives a shower of implausibly fat drops. |
| 3 | **The drag regime.** | Whether the terminal velocity law is Stokes, intermediate or Newton decides whether speed goes as d², d^½ or saturates. Quote the fit and its range. |
| 4 | **What the streak actually is.** | Motion blur: length = velocity × exposure. It is not a style parameter; naming the shutter time makes it checkable. |
| 5 | **Shared vs individual forcing.** | Wind shear applies to every member equally; turbulence does not. |

> **Derive every correlated property from one root quantity.** Where two things are related by
> physics, sampling them independently guarantees combinations that cannot exist. The viewer cannot
> name what is wrong, but reads the whole field as false.

## Channel

Measured: 2000 particles in SVG cost **466 ms/s** of main thread and drop composited frames; the
same simulation on canvas costs **125 ms/s** with 28 DOM nodes against 2024. This regime goes to
canvas. See `references/platform.md`.

## Failure signature

- big slow members beside small fast ones → the coupling was not derived
- uniform sizes → the distribution was not sampled
- streaks the same length regardless of speed → blur was treated as decoration
