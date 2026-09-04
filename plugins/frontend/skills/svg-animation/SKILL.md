---
name: svg-animation
description: >-
  Create or animate a visual object by understanding it before drawing it. Use whenever someone asks
  for a thing to be drawn or moved — "a toucan flying", "a tree in a light breeze", "a car driving",
  "waves", "rain", "a walking figure", a specific animal or plant or vehicle or weather — whether or
  not they name a technology, and also when an existing animation reads as mechanical, dead or
  wrong. Classifies the request into physical REGIMES (articulated body, driven oscillator,
  dispersive wave field, ballistic ensemble, growth structure, advected field, threshold discharge,
  orbital bodies, radiant point set, mechanism and linkage), loads each regime's schema of what must
  be known before drawing, then CHOOSES THE TECHNOLOGY from what the regime implies — SVG, Canvas,
  WebGL, a playback or orchestration tool, or a hand-off to the r3f-* skills for 3D — and only then
  fixes viewpoint, geometry, appearance and motion. Carries measured costs for SVG/CSS/Canvas and
  the traps that break silently.
metadata:
  author: solvelab
  version: 1.1.1
  category: frontend
license: MIT
compatibility: Works in any environment with filesystem access; verification steps need a Chrome binary.
---

# svg-animation — understand the object, then represent it

The failure this skill exists to prevent is not ugly output. It is **plausible** output: an animation
whose every part is defensible and whose whole is wrong. Measured on 22 objects and 12 primitives
([research/svg-animation in the catalog repository](https://github.com/solvelab/ai-skills/tree/master/research/svg-animation),
ten recorded trials — the research directory is not part of the installed skill), the defects
classified by what was actually missing:

```
viewpoint / axis                    4
coupling between quantities         3
wrong class of system               3
platform / rendering                3
process with no stopping condition  2
geometry method                     2
composition / legibility            1
tooling                             1
DOMAIN KNOWLEDGE                    6   — about one in four
```

Three quarters of it was not domain knowledge. The tree is the proof: holding every domain fact
(0.30 Hz trunk, branch modes at 2, 7 and 11 Hz, damping 10.6%) it still failed four times running —
invented amplitude, wrong class of model, and detail that buried the shape.

So the axis of specialisation here is **the regime**, not the object. A tree in wind, a flag, a
wheat field and a hanging sign are four different subjects and one list of questions.

## CRITICAL: the three gates

1. **Viewpoint before geometry.** No shape is drawn until the view is fixed and every kinematic
   number is expressed in THAT view's axes. Ask rather than choose when the mechanism's principal
   axis is not visible in the requested view, when the object has more than one canonical view, or
   when the reading size changes what must exist.
2. **Provenance on every quantity.** Each number is `measured`, `derived from <X>`, or `assumed`.
   An `assumed` appears in the delivery. The costliest defect on record was an invented amplitude
   written beside a measured frequency with nothing distinguishing them.
3. **Side by side when replacing something that worked.** Verifying against the law tells you the
   new version is true. It cannot tell you the old one was better. Three successive tree versions
   passed every other gate and each was worse than the one before.

## Workflow

### −1 · Recognise what is being asked

Before anything else, notice that this IS an object-creation request. It usually arrives without a
technology named and often without the word "animate":

> "faça um tucano voando" · "uma árvore com brisa leve" · "um carro andando" · "ondas do mar" ·
> "quero uma tartaruga nadando devagar" · "isso aqui ficou mecânico, arruma"

Three things separate this from a chart, an icon, or a UI illustration, and any one of them is
enough: **the subject is a thing in the world** (an animal, a plant, weather, water, a vehicle, a
figure), **it has behaviour** that a viewer would recognise or miss, or **an existing version reads
as wrong** and nobody can say why.

Then say back, in one line, what you understood — object, what it is doing, and what you are about
to decide. A misread here is the cheapest possible thing to fix and the most expensive to discover
after the geometry is written.

### 0 · Frame

Object in one sentence · what it is NOT · reading size · **the view** (gate 1).

**Four things are worth asking about when the request does not say them.** Not "ask when unsure" —
these are derivable triggers, and each one changes the work rather than the taste:

| ask about | when |
|---|---|
| **viewpoint** | the mechanism's principal axis is not visible in the requested view (a dolphin's stroke is vertical: from above it does not exist), or the object has more than one canonical view |
| **visual register** | the answer would change the geometry, not just the palette — which it usually does. See `references/style.md` |
| **reading size** | the object will be small enough that some parts stop existing, or large enough that absent detail becomes a hole |
| **what it is doing** | the behaviour is the subject and more than one is plausible: swimming, resting, hunting, fleeing are different animals |

### 1 · Route to regimes

Classify the request. Most objects need MORE THAN ONE regime, usually one for geometry and one for
motion. Load only the schemas named.

| the object is… | regime | schema |
|---|---|---|
| a limbed animal, a person, anything with joints | articulated body | `references/regimes/articulated-body.md` |
| a structure bending under wind or a rough driver | driven oscillator | `references/regimes/driven-oscillator.md` |
| a branching thing: tree, veins, rivers, roots, lightning's shape | growth structure | `references/regimes/growth-structure.md` |
| open water, swell, ripples | dispersive wave field | `references/regimes/dispersive-wave-field.md` |
| rain, snow, sparks, dust, spray | ballistic ensemble | `references/regimes/ballistic-ensemble.md` |
| cloud, smoke, steam, fire plume | advected field | `references/regimes/advected-field.md` |
| lightning, a crack, a spark, a failure event | threshold discharge | `references/regimes/threshold-discharge.md` |
| planets, moons, anything falling around something | orbital bodies | `references/regimes/orbital-bodies.md` |
| stars, distant lights, a field of point sources | radiant point set | `references/regimes/radiant-point-set.md` |
| a vehicle, a machine, anything whose parts are joined by constraints | mechanism and linkage | `references/regimes/mechanism-linkage.md` |

A tree in wind is `growth-structure` (geometry) + `driven-oscillator` (motion). A gull is
`articulated-body` (wings) + its own trajectory. Neither is "vegetation" or "animals".

Once the regimes are named, check `references/objects/` for a dossier of the object (format and
the existing set: `references/objects/README.md`) — the facts a regime schema asks for, each with
its source; write one when the object is first built, never in advance.

**If the request falls in a regime with no schema here, say which regime is missing and what you
cannot vouch for without it.** Do not present the result as if that regime had been covered.

`mechanism-linkage` is present but **UNEXERCISED**: its questions come from mechanics rather than
from defects measured here, and it says so at the top. Use it, and say that it is unproven.

### 1b · Choose the technology

**The technology is an OUTPUT of the regime, not an input.** Once the schema is answered you know
how many things move, whether their geometry is rebuilt each frame, and whether the scene is flat —
which is the whole decision. `references/technology.md` carries it, along with what is measured here
and what is not.

The short form: tens to hundreds of parts moving by transform, flat → SVG. Thousands, or geometry
rebuilt per frame → Canvas. Depth the viewer moves through → hand off to the `r3f-*` skills, which
this catalogue already carries; do not reimplement 3D here. And the question that decides whether a
tool replaces the technique at all: **do you need to PLAY a motion, or COMPUTE one?** A wingbeat is
playback. A tree in wind is computation — no keyframe sequence represents a randomly driven system.

Never choose by what the object IS. A flock of two thousand birds is a ballistic ensemble and
belongs on canvas; one bird is an articulated body and belongs in SVG. Same animal, different
regime, different technology.

### 2 · Answer the regime's questions

Each schema is a list of things that must be known before drawing, and each entry names the
measured defect that put it there. Answer every one, with provenance (gate 2). An unanswered
question is a stated gap, never a plausible filler.

**Every question gets a written verdict, including `n/a because <reason>`.** A question passed over
in silence is the original defect returning: the process had no stopping condition, so it stopped
wherever the ideas ran out. This rule came from simulating this skill on a flag — six of the nine
questions were recorded and three were silently skipped, and only counting them caught it.

**Two rules that cut across every regime:**

- **Derive correlated properties from ONE root quantity.** Where physics links two things, sampling
  them independently guarantees combinations that cannot exist. Rain: diameter sets speed, streak
  and opacity. Waves: wavelength sets celerity and period. Orbits: the semi-major axis sets the
  period. The viewer cannot name what is wrong and reads the whole field as false.
- **Every rate carries an amplitude, and the amplitude has its own source.** A frequency alone is
  half a measurement and it is the invisible half. Check with `peak = 2πfA` against something
  physical in the scene.

### 3 · Geometry

Decompose by what moves together. Mass becomes a **profile table** — a list of half-widths at
stations along the part, taken from real measurements and divided by the part's own length, so one
table serves any size. Profile tables are usually **asymmetric**: a shin's front edge is bare bone
and runs straight while the whole calf sits behind it. A trapezoid cannot carry that, and a limb
built from trapezoids reads as furniture.

**Loaded members bow.** Anything carrying weight or force is a cantilever: it curves, and the
curvature gathers toward the tip. Straight is what weightless looks like.

**Decide whether the drawn shape is the loaded or the unloaded one**, and say which. Drawing the
intended silhouette and then applying a mean load gives an object permanently swept sideways.

Check large, against a grid.

### 4 · Appearance

Colour from materials by name, not by taste, and **at the register the work is in** — see
`references/style.md`. Lower the register and the recognition marks must get LOUDER, not fewer: the
gulls here had correct anatomy, correct proportions and a documented viewpoint, and still read as
dark blobs until they were given a herring gull's actual plumage. No geometry changed. In a flat
register colour was carrying the entire recognition, and it had never been researched. **Turnable surfaces have two faces** — a leaf, a sail,
a hand — and without the second face the flip cannot read at all.

**Density is a legibility decision, not a fidelity one.** A detail that carries 5% of the energy
and 50% of the visual noise is a bad trade. This is the most recent lesson here and the hardest:
four additions, each individually true of a real tree, together buried the crown.

### 5 · Motion

The regime schema decides the model. The one question that decides the most:

> **Is the driver deterministic or stochastic?** If what moves the object is turbulence, traffic,
> a crowd, a queue — a keyframe loop cannot represent it at any frequency or amplitude, because a
> randomly driven system has a wandering envelope and a loop has a fixed one. Stop animating the
> output and integrate the system: driver → response.

Hierarchy is the part list. Lag makes the wave. Give each unit that moves as a whole its own
`<svg>` element (`references/platform.md`).

### 6 · Verify

- forward kinematics against any solver
- frozen poses, large, on a grid
- a live strip: several frames, side by side, at the real rate
- `peak = 2πfA` held against something physical
- **against the version it replaces** (gate 3)
- reduced motion — remove, reduce, *or replace*
- measured cost (`references/platform.md`)

The tooling used to produce this skill's evidence lives in the catalog repository, outside the
installed skill:
[research/svg-animation](https://github.com/solvelab/ai-skills/tree/master/research/svg-animation) —
`measure.mjs` (CDP cost harness) and `verify-motion.mjs` (does it MOVE right, not just look right).

## What no gate here can catch

Three of five tree versions passed every check in this file and each was worse than the last. The
person looking at the screen is the instrument for whether motion reads as alive, and there is no
substitute. **Design for that: put a six-frame contact sheet in front of them early and cheaply,
before investing in detail — not at the end.**
