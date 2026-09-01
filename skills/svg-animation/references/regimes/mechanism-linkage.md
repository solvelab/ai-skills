# Regime: mechanism and linkage

Anything whose parts are joined by CONSTRAINTS rather than by flesh: a car, a bicycle, a motorcycle,
a train, a crane, a piston engine, a clock, a robot arm, a door.

**This schema is UNEXERCISED.** Every other schema in this directory has a defect column, because
each of its questions came from something measured going wrong in this repository. Nothing has been
built in this regime here, so the questions below come from mechanics rather than from experience,
and the defect column is empty on purpose. The first vehicle built through it fills that column —
and if a question turns out to be wrong, it was wrong in a file that said it was unproven.

## What makes this regime different

In every other regime the parts are free and the physics decides where they go. Here the parts are
BOUND: a wheel cannot spin at a rate unrelated to how fast the vehicle is moving, a piston cannot
be anywhere but where the crank puts it, a steered pair of wheels cannot point the same way. The
questions are therefore about the constraints, and almost every recognisable defect in animated
machinery is a violated constraint rather than a wrong number.

## Must be known before drawing

| # | question | the relation, and why it is the recognisable one |
|---|---|---|
| 1 | **Rolling without slipping.** | `ω = v / r`. A wheel's spin rate is NOT free — it is the travel speed divided by the radius. A wheel spinning while the vehicle is still, or turning at a rate unrelated to its motion, is the most common defect in animated vehicles and the eye catches it instantly even when it cannot say why. |
| 2 | **Does the spoke pattern strobe?** | A spoked wheel is a sampled signal. At frame rate `f` with `n` spokes, the wheel appears stationary when `ω·n/2π` is a multiple of `f`, and appears to run BACKWARDS just below it — the wagon-wheel effect, and it is real on a screen exactly as it is on film. Either blur the spokes, choose a count that does not beat with the frame rate at the speeds shown, or accept it deliberately. |
| 3 | **Steering geometry.** | Ackermann: the inner wheel must turn MORE than the outer, because they travel different radii about a shared centre. `R = L / tan δ` for wheelbase `L`. Parallel front wheels is the tell that the linkage was not thought about. |
| 4 | **Weight transfer.** | `Δload = m·a·h/L` — mass, acceleration, centre-of-gravity height, wheelbase. The nose dips under braking and squats under power, and the BODY pitches while the WHEELS stay on the road. A vehicle that changes speed without pitching reads as a sprite being translated. |
| 5 | **Where the suspension is.** | The body and the wheels are separate bodies joined by a spring and a damper. Drawing them as one rigid object removes every secondary motion a vehicle has: bump absorption, roll in a corner, the rebound after a kerb. |
| 6 | **Lean, if it is a single-track vehicle.** | A bicycle or motorcycle in a turn leans by `tan θ = v²/(gR)`. It cannot turn upright. This is the whole silhouette of a cornering bike. |
| 7 | **Non-sinusoidal linkages.** | A piston's position from crank angle is `x = r·cos θ + sqrt(l² − r²·sin²θ)`, which is NOT a sine — the asymmetry between the strokes is what makes an engine look like an engine. Any four-bar linkage has the same property: the output is not a harmonic of the input. |
| 8 | **Gear and drive ratios.** | Pedal cadence, chain, sprocket, wheel: one chain of ratios, and every rate downstream follows from the one upstream. Same rule as everywhere else in this skill — one root quantity, everything derived. |
| 9 | **Track vehicles: the top run moves at twice the hull speed.** | Relative to the ground the lower run is stationary (it is in contact) and the upper run travels at `2v`. Animating both at hull speed is the classic tank-track error. |
| 10 | **What is rigid and what is not.** | A chassis is rigid, a chain is not, a tyre deforms at its contact patch, a cable sags. Deciding this is the same phase-2 decision as anywhere: loaded members bow. |

## Failure signature

- wheels whose rotation is unrelated to the travel — check `ω = v/r` before anything else
- front wheels parallel in a turn
- a vehicle that accelerates or brakes without pitching
- body and wheels moving as one rigid piece over a bump
- a bike cornering upright
- a piston moving as a pure sine
- both runs of a track at the same speed

## Technology note

A vehicle is usually **tens of parts, transform-only** — the SVG channel, and cheap. It becomes a
different problem the moment it is one of a hundred in traffic, which is a ballistic ensemble of
constrained bodies and belongs on canvas. See `references/technology.md`.
