# Regime: driven oscillator

A structure that bends under a driver it does not control: a tree in wind, a flag, a wheat field, a
hanging sign, a cable, a mast. Four different subjects, one list of questions.

This schema is the one that cost the most to learn. The tree failed **four times running** while
every domain fact about trees was already in hand.

## Must be known before drawing

| # | question | the measured defect that put it here |
|---|---|---|
| 1 | **Natural frequencies of each member.** | A tree's trunk sits at 0.2-0.33 Hz while BRANCH modes are at 2, 7 and 11 Hz — a spread of 10x to 30x. The first version used 1.5x, so everything swayed at one rate and the tree moved like seaweed. |
| 2 | **Damping ratio.** | 10.6% with branches attached, 1.3% stripped bare. The branches ARE the damper. Without this the structure rings forever. |
| 3 | **THE AMPLITUDE OF EACH RATE, and where it comes from.** | Measured frequencies were written beside INVENTED amplitudes, growing outward because a twig obviously moves more than a trunk. 11 Hz at 14 degrees is 968 deg/s — 16 degrees per frame, a twig tip averaging 11.8 m/s in a 5 m/s wind. Every number was plausible; the product was absurd. |
| 4 | **The forcing spectrum, WITH ITS KNEE.** | Amplitude ∝ f^(-5/6) is right in the inertial subrange and has no low-frequency limit, so one 50-second component carried 79x the energy of everything else and the structure did nothing for a minute at a time. The von Kármán form is FLAT below f ≈ U/L and only then rolls off. |
| 5 | **Is the driver stochastic?** | If yes, a keyframe loop cannot represent it. A randomly driven oscillator has a WANDERING envelope; a loop has a fixed one. Correct frequencies and correct amplitudes in a periodic loop produced a scene that read as dead, and no further tuning of a number could have fixed it. |
| 6 | **Spatial coherence of the driver.** | Turbulence is not either coherent or independent: coherence decays as `exp(-C·f·d/U)`, C ≈ 10. At 0.3 Hz across 5 m that is 0.29. So a crown ripples — but at LOW frequency, as one gust crossing it. Giving each member its own fast forcing instead produced independent twitching that reads as an insect. |
| 7 | **Mean deflection vs fluctuation.** | The driver does not reverse. Wind is a fluctuation about a POSITIVE mean, so the structure leans downwind and recoils; it does not swing symmetrically through vertical. |
| 8 | **Does the object reconfigure under load?** | A tree streamlines: leaves fold, drag grows as U^1.3-1.5 instead of U². That is why trees survive storms, and it changes the shape of every gust response. |
| 9 | **How strong is the driver, anchored on an observable?** | At 6 m/s the model was self-consistent, correctly parameterised, and the tree looked dead — because 6 m/s does not move a tree. The Beaufort scale exists precisely because it **defines wind by what trees do**: force 5 "small trees in leaf begin to sway", 6 "large branches in motion", 7 "whole trees in motion". |

> When every part of a model is defensible and the result is still wrong, the error is in a quantity
> you did not think to question. Look for the one you inherited without deciding.

## The model

```
θ̈ = ω²(θ_target − θ) − 2ζω θ̇        θ_target = lean · u(t)^vogel
```

`u(t)` is one shared driver signal built by spectral synthesis: components log-spaced across the
band, amplitudes from the spectrum's own form, random phases — incommensurate, so it never repeats.
Each member sees it with a phase LAG proportional to `f·d/U`, which is Davenport coherence and which
is what makes the structure ripple instead of moving as a slab.

**Solve stiff members quasi-statically.** A member whose natural frequency is far above the forcing
band does not ring, it follows. Integrating it anyway is not more physical, it is less: at 11 Hz and
dt = 1/60, `ω·dt = 1.15`, where semi-implicit Euler is stable but accurate nowhere near — what gets
rendered is the integrator's own noise. Above ~4 Hz, set θ = target.

## Failure signature

- everything at one rate → seaweed
- fast members at large amplitude → buzz; check `2πfA` against the driver's own speed
- correct numbers in a periodic loop → dead, and no number will fix it
- per-member independent fast forcing → insect twitch, not wind
- rendering modes that carry ~5% of the driver's energy at full amplitude → nervous AND illegible
