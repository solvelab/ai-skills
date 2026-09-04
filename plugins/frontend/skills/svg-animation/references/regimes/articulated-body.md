# Regime: articulated body

Anything with joints: a walking person, a bird, a fish, a turtle, an insect, a hand. The parts are
rigid; the motion is in the angles.

## Must be known before drawing

| # | question | the measured defect that put it here |
|---|---|---|
| 1 | **THE VIEW, and every kinematic number expressed in its axes.** | A gull was drawn with mirrored wings — the view from below — on a body in pure profile. Two viewpoints in one animal, and three fixes failed before the cause was named rather than patched. |
| 2 | **Which axis each measured angle belongs to.** | A turtle's measured −73°/+35° is flipper TWIST, not stroke. Applied as stroke it hung the flippers below the shell. A number without its axis is not a measurement. |
| 3 | **Segment lengths as fractions of the whole.** | Fractions of stature or body length transfer; absolute sizes do not. Human: hip 0.530 of stature, knee 0.285, ankle 0.039, shoulder 0.818, head height 0.130. |
| 4 | **Breadths, also as fractions.** | Biacromial 0.259 of stature, hip breadth 0.191, waist 0.174. The walker's shoulders ran 0.15-0.17 — **40% too narrow** — which is why the figure read as a stick rather than a person. |
| 5 | **Profile tables, and their ASYMMETRY.** | Every limb was a trapezoid. Half-breadths come from circumferences (`C/2π`) divided by the segment's own length, so one table serves any size. And they are one-sided: the shin's front edge is subcutaneous bone and runs almost straight while the whole calf mass sits behind it, peaking at 28% down and falling to an ankle less than half its width. A leg reads as a leg because of that bulge; a symmetric taper reads as a table leg. |
| 6 | **The cycle: named phases with durations.** | Human gait: stance 60% / swing 40%, with named sub-phases. A cycle without named phases cannot be checked against anything. |
| 7 | **Contact constraints.** | A planted foot does not slide. This forces inverse kinematics for the limb in contact; forward kinematics is correct and cheap only for a limb in the air. |
| 8 | **Sign convention, written BEFORE the first keyframe.** | Inverted phase sign happened on the bird and on the turtle. The walker had no written convention and produced five separate solver bugs, including a knee sign that only a forward-kinematics check caught — error 28-47 units, dropping to 0.00 once fixed. |
| 9 | **Species-specific organs.** | A pectoral fin was reused across species. Each species' organ has its own geometry, and the reuse is visible immediately to anyone who knows the animal. |

## Verification specific to this regime

Solve, then **check by forward kinematics**: rotate the joints by the solution and confirm the
extremity lands on the target. Normalise angles before comparing — an unnormalised elbow angle read
196° and nearly "fixed" a wing that was correct.

`verify-motion.mjs` — in the catalog repository, outside the installed skill
([research/svg-animation](https://github.com/solvelab/ai-skills/tree/master/research/svg-animation)) —
checks cycle closure, phase pairs (`-near`/`-far` for
alternating limbs, `-sync-near`/`-sync-far` for limbs that beat together), contact slip measured
relative to the surface, and anchor stillness. Its `--cycle` argument is in MILLISECONDS: passing
seconds made the half-cycle shift round to zero, so the antiphase test silently became an in-phase
test and reported two correct limbs as broken.

## Failure signature

- two viewpoints in one animal
- a joint that opens a gap when it bends → extend the parent shape PAST the pivot; overlap and
  coverts were both tried first and both failed
- a foot that slides during stance
- limbs that look like furniture → the profile table is missing
