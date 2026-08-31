# The method

How to take **any** object someone asks for and produce it in SVG — still and moving — so that it
reads as that object and moves the way that object moves.

This file is the point of the whole research. Everything else here is either evidence for it
([`measurements.md`](measurements.md)) or a worked demonstration of it (the scenes and the
bestiary). If you read one file, read this one.

It is a **procedure**, not a gallery. It has five phases, each with an output you can check before
moving on.

**And the procedure has a rule about itself: every change to it is simulated before it is believed.**
Run the changed method from a blank page on an object it has never seen, count the iterations, and
record what the new phase actually removed. A change to a procedure that has not been simulated is
an opinion. Both trials below produced a rule that reasoning alone had not surfaced. Skipping a phase does not save time — every defect recorded in this directory came from
skipping one, and each was found only after the phase it belonged to had been skipped.

---

## Phase 0 — Frame the request

Before any research, settle four things. They change everything downstream, and guessing them is
the cheapest way to waste the other four phases.

| Question | Why it decides things |
|---|---|
| **What is the object, in one sentence?** | "A bird" and "a herring gull in cruising flight" produce different work. Pin the species, model, era or type. |
| **Which VIEW shows the mechanism?** | A shark's whole stroke is lateral: drawn in profile it is invisible. A bird's wing fold is invisible from below. Choose the view where the motion lives, not the view that is prettiest. |
| **At what size will it be read?** | At 40 px only the silhouette and one or two marks survive. At 400 px the joins are visible and must be correct. Decide the target before drawing, because it sets how much geometry is worth building. |
| **What must it NOT be mistaken for?** | Naming the neighbour it has to be distinguished from is what surfaces the diagnostic features. A gull's neighbour is a pigeon; a dolphin's is a shark; a van's is a truck. |

**Output:** four written answers. If the view is wrong, nothing after this matters.

---

## Phase 1 — Research the object

**Do not draw before this exists.** A technique catalogue applied without an observation step
produces animation that is fast, cheap and wrong — measured repeatedly in this research.

Fill this sheet. Each row is a question with a findable answer, and "I do not know" is a legitimate
entry that must be written down rather than guessed.

| Field | What to find | Example, from this directory |
|---|---|---|
| **Mechanism** | What physically produces the motion — joints, pivots, hinges, the driver | A wing is two bones: arm at the shoulder, hand at the elbow |
| **Phases** | The named parts of the cycle, and their **relative durations** | Wingbeat: upstroke, US→DS transition, downstroke, DS→US. The downstroke is shorter and faster |
| **Asymmetries** | What is not a sine — where the cycle is uneven | The power stroke occupies less of the cycle than the recovery |
| **What CHANGES shape** | The part that is not rigid. This is usually the detail whose absence kills it | The wing's span shortens on the upstroke because the elbow folds |
| **Proportions** | Real measures, as **fractions of the whole** | Gull: wingspan 2.30 L, bill 0.090 L, skull 0.10 L, fold at 39% of half-span |
| **Materials and colours** | Named by what the thing IS, not by hue | `sea, reef, sand, grass, trunk, canopy-dark/mid/light, ground-shadow` — never `hsl(88 + rand())` |
| **Recognition marks** | The one to three details the eye uses. Often cheap | A gull's black wingtip with white mirrors: one fill, and it reads at twenty pixels |
| **Scale relations** | Ratios that are observable and free to honour | A smaller bird beats faster; a bigger network is a bigger island |
| **Unknowns** | What could not be established | Written down, not filled with a plausible substitute |

### 1b — The anchor map: WHERE each part sits

The sheet above says what the object does. It does not say **where anything is**, and that omission
produced most of the defects in this directory: wings emerging from a neck, a flipper rooted at
mid-body instead of behind the head, a fin's fold placed at the midpoint instead of at 39%.

For every part, record its anchor as a **fraction of the whole, in both axes**:

| Part | Anchor along | Anchor across | Extent |
|---|---|---|---|
| gull wing | 0.22 L from the bill | at the top of the back | span 1.15 L per side |
| gull wing fold (wrist) | **39% of the half-span** from the shoulder | — | hand ≈ 2× the arm |
| dolphin pectoral | 0.24 L from the snout | on the belly line | 0.14 L |
| humpback pectoral | 0.28 L | on the belly line | **0.30 L** |
| dolphin dorsal | 0.42 L | on the midline | height 0.10 L |

Write it as a table before drawing. Two rules that fall out of it:

- **Anchor to a landmark, not to a number you like.** "Just behind the head", "at the widest point",
  "where the peduncle begins" — then convert to a fraction and record both.
- **State the anchor's axis.** A pectoral is at 0.28 L *along* **and on the ventral surface**. The
  humpback's flipper was drawn above the axis and appeared to sprout from the spine, because only
  the first number had been written down.

### 1c — Kinematics: HOW FAR each joint travels

The last field, and the one whose absence caused the most rework. A cycle written as "the wing goes
up and down" leaves every angle to be guessed, and guessed angles produced an inverted stroke twice,
an amplitude that folded a shark's peduncle into a fork, and a turtle flipper that lay across its
own shell.

These quantities are **measured and published**, and the reason to know their names is that the
names are what make them findable:

| Quantity | What it is | Example found |
|---|---|---|
| **angular amplitude** | angle between the highest and lowest wingtip position, in the stroke plane — **record the axis**, since twist is not stroke | the number that sets your keyframe range |
| **stroke plane angle** | angle of that plane relative to the horizontal | why a downstroke goes down *and forward* |
| **joint range of motion** | per joint, in degrees | gull elbow ≈ **130°** |
| **forward sweep** | travel in the second axis | gull ≈ **15°**; pigeon reaches ≈ 50° |
| **degrees of freedom** | how many axes each joint has | bird forelimb: shoulder 3, elbow 1, wrist 2 |
| **upstroke:downstroke ratio** | the asymmetry, as a number | sets the keyframe *positions*, not just the values |
| **span ratio** | how much the span shortens on recovery | the fold, quantified |

Search these terms with the species name and you get papers with numbers. Search "how a bird flies"
and you get adjectives.

**These numbers also VERIFY, not just build.** Once the object exists, compute the quantity back out
of the geometry and compare it to the published value. The gull here was built by trial before this
phase existed; measured afterwards its most-folded elbow angle is **133.9°** against a published
**130°**. That is a pass — and it is a check that can be run on any joint of any object, in a few
lines, at any time.

One caution, earned: the first attempt at that check computed the angle without normalising and
reported 196°, which would have prompted "fixing" a wing that was already correct. **A verification
step is code too.** Wrong verification is worse than none, because it manufactures confident
changes in the wrong direction.

**Where a number genuinely cannot be found**, write the value you chose and mark it as set by eye —
as the turtle's flipper length is marked here. An estimate labelled as an estimate is honest; an
estimate presented as a measurement is the failure mode this whole method exists to prevent.

### 1d — Depth order: WHAT IS IN FRONT OF WHAT

One line per part, front to back. It is the third input to the join rule in phase 2.3, and writing
it down at research time is what prevents discovering at render time that a tail has been painted
over the body it hangs from.

**Output:** the filled sheet. Every later decision cites a row of it.

**Where to look, cheapest first:** what the project already contains (a codebase that draws this
object has usually already learned the lesson — the maintainer's own `Gulls.tsx` carried thirteen
documented defects and the species measurements that fixed them); then reference and specification
material; then the open web. Prefer a source that gives **numbers or a mechanism** over one that
gives adjectives.

---

## Phase 2 — Geometry: build it still

An object that is wrong when still does not become right by moving. Build and check the static
form first.

### 2.1 Decompose by what moves together

List the parts. A part is anything that moves as a unit, or that is a different material. This
list becomes the drawing hierarchy and, later, the animation hierarchy — they are the same tree.

### 2.2 Choose the construction per part

This is the split that took three failed attempts to learn:

| The part is… | Build it as | Because |
|---|---|---|
| a **mass** with a smooth rule — a body, a hull, a fuselage, a bottle | a **profile table**: stations along an axis, with a thickness at each | many samples, one law; the outline is continuous by construction and every number is a checkable proportion |
| a **feature** with a handful of characteristics — a fin, a wing, a handle, a mirror, a bracket | an **explicit outline**, written directly | six or eight meaningful points; deriving them from parameters means tuning blind |

A profile table looks like this, and its virtue is that each line can be argued about:

```js
{ x: 0.000, back: 0.012, belly: 0.012 },   // snout
{ x: 0.072, back: 0.058, belly: 0.034 },   // THE CREASE — the melon rises abruptly
{ x: 0.340, back: 0.108, belly: 0.100 },   // maximum girth, 34% back — not the middle
```

The same table serves the plan view by reading the column as half-width. Derived shapes — a
countershaded belly, a painted stripe, a shadow — are generated **from the same table**, so they
cannot drift off the form.

### 2.3 Join the parts by the colour rule

Three cases. Picking the wrong one produces a notch, and this defect was found and misdiagnosed
three times before the rule was stated:

| The part is… | How it joins | Why |
|---|---|---|
| **on the midline** (a dorsal fin, a mast, a spine) | draw it **before** the body | the body's own outline becomes the join; nothing is left to blend |
| **the body's colour** (a dolphin's flipper, a same-tone bracket) | draw it after, root buried **inside** | the buried part is invisible, so no edge exists |
| **a different colour** (a humpback's white flipper, a chrome trim) | draw it after, root lying **on** the surface | anything of it inside the body shows as a wedge with a straight edge |

The third case is the one that keeps being got wrong, because burying the root is the instinct from
the second — and burying a white shape in a dark body is exactly what draws the corner.

### 2.4 Two more that generalise past organisms

- **Gradients of value carry volume more cheaply than detail.** Three stacked shapes, each narrower
  and lighter than the one below, give a tree its mass without drawing a leaf. The same trick builds
  a cloud, a rock, a hedge, a crowd.
- **Declare the light direction, once, and obey it everywhere.** Shadows that agree read as solid;
  shadows that disagree read as collage. Write it down so later parts inherit it.
- **Distribute by Poisson-disk, not by `Math.random()`.** Uniform random produces clumps and voids,
  and clumps are precisely what the eye reads as "generated".
- **Fade a field out; do not cut it.** A painted band that stops square reads as a sticker. Taper
  its height to nothing.

### 2.5 Check it before animating

**Render it large, against a grid, and look at it.** Not at thumbnail size, and not in motion.

Every geometric defect in this research was invisible in motion and obvious in a still: a hole
between two outlines, a rectangular step where one path met another, a belly patch floating clear
of the body, wings emerging from a neck, a mixed viewpoint.

---

## Phase 3 — Script the life cycle

**Write the cycle in prose before writing a single keyframe.** This is the phase most often skipped
entirely, and skipping it is what produces motion that is technically smooth and reads as a
metronome.

The script answers:

1. **What are the states?** Not every object only loops. Consider: at rest, entering, cycling,
   acting, degrading, leaving, absent. A watchdog post has *transmitting*, *late*, *lost*, *muted* —
   and the fourth is not a variation of the first three.
2. **What are the phases within the cycle**, named, with relative durations? "Down and up" is not a
   script. "Power stroke, 28% of the cycle, wing extending and moving forward; recovery, 38%, wing
   folding and moving back" is.
3. **What changes besides position?** Shape, span, opacity, colour, count. The detail that kills a
   naive animation is almost always one of these, not the trajectory.
4. **Where is the asymmetry?** Almost nothing in nature or in machines is a sine.
5. **What must NOT repeat?** And, separately: what may repeat, but must not be *seen* to repeat.
6. **What does absence mean?** Sometimes the important state is the one where an expected motion
   stops. That only reads if the expected motion was established first.

**Output:** a written script. It is the specification the keyframes implement, and it is reviewable
by someone who cannot read CSS.

---

## Phase 4 — Assemble and animate

Now, and only now, the animation.

### 4.1 The hierarchy is the part list from 2.1

Each part hangs from the part it is attached to. A wing's hand hangs from its arm; a moon's group
hangs from its planet's. Built this way, derived motion falls out for free: fold the elbow and the
span shortens, because it must.

### 4.2 Lag between parts is what makes a wave

Give each part in a chain a slightly later start than the one before it. That lag is the travelling
wave. Without it a chain flexes as one rigid hinge — a windscreen wiper, not a swimmer.

### 4.3 Choose the channel by cost

Measured, in Chromium (`measurements.md`): **inside an SVG, every animation mechanism pays layout
every frame** — script, CSS, SMIL and the Web Animations API alike. The same declaration on an
HTML-level box pays none.

So: **anything that moves as a unit becomes its own `<svg>` element**, animated as a box. Parts that
move *within* a unit stay inside it and pay layout, which is affordable in the tens and must be
budgeted in the hundreds. Past a few hundred moving things, leave SVG for Canvas.

### 4.4 Decorrelate everything that repeats

- **Stagger instances** with a negative delay proportional to index — a flock that beats in unison
  is the signature of a screensaver.
- **Sum frequencies that share no small common multiple** so a loop never quite lines up.
- **Vary rate with size** where the object's own physics says so.

### 4.5 Reduce motion, do not remove it

`prefers-reduced-motion: reduce` means *remove, reduce, **or replace***. Travel, parallax, rotation
and scaling go; the object keeps breathing. Deleting motion that carried meaning makes the interface
worse, not kinder. And read the preference again when it changes — it can change while the page is
open.

---

## Phase 5 — Verify

**Looking at stills is not enough, and this phase was wrong until that was proved.** Frozen-pose
strips show the *theoretical* state at each percentage — they are rendered by pausing the animation
with a negative delay. They caught inverted signs, opening joints and mixed viewpoints. They cannot
catch anything about the motion, because in a frozen strip there is no motion.

Two instruments close that gap, and both live in this directory:

**`verify-motion.mjs`** samples the REAL animation frame by frame, reads the on-screen position of
points the page marks with `data-track`, and reports trajectories plus checks a picture cannot make:

- does the cycle **close** — does the last frame return to the first (over whole cycles only)
- are two limbs that should be **half a cycle apart** actually so — tested by shifting one series
  and matching, which works for any waveform; a plain correlation only works for sinusoids
- does a point that should be **planted stay planted** — measured *relative to the surface*, since
  a foot correctly locked to a treadmill still travels across the frame
- does anything **never move**, which usually means a selector or an animation that failed silently

**A live strip**: build several independent copies staggered in time and capture them at one
instant. Every copy is running at real speed, so the strip shows the actual animation rather than a
paused idea of it.

**And where the motion is solved rather than authored, verify the solver exactly.** The walking
figure's inverse kinematics had the knee's sign inverted. Five rounds of looking at renders and
adjusting did not find it. Checking the solver against FORWARD kinematics — solve for a target, walk
the chain forward from the result, compare — found it in one run: the foot was landing 28 to 47
units from where it was asked to go, and with the sign corrected the error is **0.00**. Anything
with a closed-form inverse can be checked this way, in a few lines, without looking at anything.

The checks in order:

Four checks, in this order. Each one caught defects the others could not.

1. **The solver, against forward kinematics**, if the motion is solved rather than authored.
2. **Frozen poses, side by side.** Render six to ten frames of the cycle, paused, and look at the
   strip. Joints opening, patches surfacing, mixed viewpoints and hidden phases are all visible here
   and invisible in motion.
3. **Large, against a grid.** As in 2.5, again — the animation may have moved a part into a place
   the static check did not cover.
4. **The live strip and `verify-motion.mjs`.** The animation running, and its trajectories
   measured. This is the check that separates "is it shaped right" from "is it moving right".
5. **Reduced-motion variant.** Look at it. It is a state of the artifact, not a fallback.
6. **Measure the cost.** Layout per second and main-thread milliseconds per second of animation. A
   number, not an impression.

---

## The procedure in one page

```
0  FRAME     object in one sentence · view chosen by mechanism · read size · what it is not
1  RESEARCH  a. mechanism · phases · asymmetries · what changes shape · proportions in units of
                the whole · materials by name · recognition marks · unknowns written down
             b. ANCHOR MAP    where each part sits, as a fraction in BOTH axes, plus its extent
             c. KINEMATICS    per joint, EACH NUMBER TAGGED WITH ITS AXIS: angular amplitude ·
                              stroke plane angle · range of motion ·
                              forward sweep · degrees of freedom · up:down ratio · span ratio
                              — these are published numbers; the terms are what make them findable
                              EVERY RATE PAIRED WITH ITS AMPLITUDE, and the amplitude sourced too:
                              a frequency alone is half a measurement, and it is the invisible
                              half. Where the amplitude has no published value, DERIVE it from
                              what drives the motion — the forcing spectrum, the compliance, the
                              load — and write down which.
             d. DEPTH ORDER   what is in front of what, one line per part
2  GEOMETRY  decompose by what moves together
             mass → profile table · feature → explicit outline
             LOADED MEMBERS BOW: anything carrying weight or force is a cantilever, so it curves,
             and the curve gathers toward the tip. Straight is what weightless looks like.
             TURNABLE SURFACES HAVE TWO FACES: a leaf, a sail, a wing, a hand — if it can present
             its other side it needs that side's colour, or the flip cannot read
             join by the colour rule · declare the light · fade fields out
             CHECK: large, against a grid
3  SCRIPT    states · named phases with durations · what changes besides position ·
             asymmetry · what must not repeat · what absence means
             IS THE DRIVER RANDOM? If what moves the object is turbulence, traffic, a crowd, a
             queue — then a loop cannot represent it at any frequency or amplitude, because a
             randomly driven system has a WANDERING envelope and a loop has a fixed one. Stop
             animating the output and integrate the system: driver -> response.
4  ASSEMBLE  hierarchy = part list · lag makes the wave · own <svg> per moving unit ·
             decorrelate · reduce rather than remove
5  VERIFY    solver vs forward kinematics · frozen poses · large on a grid ·
             AGAINST THE VERSION IT REPLACES, side by side, whenever you are changing something
             that already worked. Verifying only against the physics tells you the new thing is
             true; it cannot tell you the old thing was better.
             LIVE STRIP + verify-motion.mjs (does it MOVE right, not just look right) ·
             PEAK SPEED = 2πfA, held against something physical in the scene — the wind speed,
             the walking speed, a body length per second. This is the check that catches an
             invented amplitude, and it is one line of arithmetic.
             reduced-motion · measured cost
```

---

## Does it work? One measured trial

The method was written after the fact, from defects found the hard way on a gull, a dolphin, a
humpback and a shark. That makes it a description of hindsight, which is not evidence that it helps
anyone going forward. So it was tested on an object nobody here had drawn: a **green sea turtle**,
run from a blank page through all five phases in order.

**Result: two iterations to an acceptable figure, against six for the dolphin.**

What each phase actually contributed, and what it would have cost to skip it:

| Phase | What it produced | What skipping it would have cost |
|---|---|---|
| **1 · Research** | The stroke has **five** stages, not the four a bird has, and includes a *sweep* where the tip travels in toward the shell. Thrust is **almost entirely** on the downstroke — a stronger asymmetry than a bird's. | A symmetric four-phase flap. Plausible, and wrong. |
| **1 · Research** | Carapace width is 76-82% of length; the shell is strongly vaulted; the head is **small**; there is one visible claw per flipper. | Proportions by eye, which is what made the first gull head 50% too large. |
| **1 · Research** | **The shell is rigid.** The body does not undulate at all. | This is the big one. Every previous swimmer here carries a travelling body wave, and reaching for the same spine chain would have been automatic — and would have been the same class of error as giving a shark a cetacean's fluke. |
| **3 · Script** | Named the five stages with durations before any keyframe: downstroke 30% and fast, sweep 15%, upstroke 35% and slow, extension 15%, brief glide. | Two keyframes and an ease, which is how a metronome is built. |
| **2 · Geometry** | Shell from a profile table; flipper as an explicit outline; head and rear flipper drawn before the shell so their roots are covered. | The join notch, three times, as before. |
| **5 · Verify** | The frozen-pose strip caught an inverted stroke sign in one look — at 0%, which the script called the top of the recovery, the flipper was at the bottom — and a swing wide enough to lay the paddle across the shell. | Both are invisible in motion. They would have shipped. |

The honest reading: **the method does not make the first attempt correct.** It made the first
attempt *wrong in ways the verification step catches immediately*, which is a different and more
useful property. The two defects it left were both sign and range errors in phase 4 — cheap, local,
and found by a check that takes one command.

What it removed entirely was the expensive class: the wrong mechanism, the wrong proportions, the
wrong view, and the model-level mistakes that no amount of curve-tuning can fix.

---

## Second trial: simulating a change to the METHOD itself

The turtle validated the method as it stood. Phases 1b, 1c and 1d — the anchor map, the kinematics
sheet and the depth order — were added *after* it, which meant the newest and largest change to the
method had never been tested. A change to a procedure has to be simulated exactly as a change to
code does, or it is an opinion.

So it was run again, on a **walking human**: the hardest available subject, because everyone knows
what walking looks like, and one with an unusually rich published literature.

**Result: two iterations. And, for the first time, no inverted sign.**

| | dolphin (no method) | turtle (method, no 1b/1c/1d) | walker (full method) |
|---|---|---|---|
| iterations to acceptable | 6 | 2 | 2 |
| inverted stroke sign | — | **yes** | **no** |
| proportions wrong on first pass | yes | no | no |
| keyframe values | guessed | guessed | **transcribed from published data** |
| defects remaining | many | 0 declared | **1, declared** |

What 1c bought, specifically: every keyframe stop is a published number placed at its published
percentage — stance 60% / swing 40%, hip 20° extension at terminal stance, knee 40° at pre-swing
and ~60° at mid-swing peak, ankle 20° plantarflexion at toe off. **Nothing was guessed**, and the
sign convention was written down before the first keyframe, which is what stopped the inversion
that caught both the bird and the turtle.

What the two iterations were spent on, and neither was a modelling error:

1. The arms were drawn in the torso's exact colour and disappeared into it — only the hands read.
2. There was no ground line, so the figure floated and the cycle could not be judged at all.

### The defect the second iteration exposed, which is worth more than the figure

Adding the ground revealed something invisible without it: **the planted foot slides**. The chain is
rooted at the hip, so when the pelvis rises the stance foot rises with it.

That is not a bug in this walker. It is a general rule the method was missing:

> **A supported chain should be rooted at its CONTACT POINT, not at its centre of mass.** Drive a
> walker from the hip and the stance foot slips; drive a crane from its cab and the hook drifts;
> drive a leaning ladder from its middle and its feet skate. Wherever a part is in contact and must
> not move, the hierarchy has to be inverted for as long as that contact lasts — which is inverse
> kinematics, not a transform chain.

It is left in place here, with the amplitude held to ~1% of height so the slip is below the noise,
and **declared rather than hidden**, because the point of the trial is what it found.

### What this says about simulating method changes

The turtle trial said the method works. This one says something more specific and more useful: the
part that removed the largest class of error was **1c, the kinematics sheet** — because guessed
angles were the single most frequent defect across every figure in this directory, and transcribed
angles cannot be guessed wrong.

It also produced a new rule that no amount of reasoning about the method would have surfaced. That
is the argument for the practice itself: **every change to the method gets simulated, and the
simulation is where the next rule comes from.**

---

## Third trial: verifying every subject, not just the newest

The walking figure was verified in motion; the five animals built before the tool existed never
were. Running all six through it found real defects in two, and **six false positives in the tool
itself** — every one discovered by using it rather than by reasoning about it.

**Defects found in the work:**

| Subject | Found | Why it mattered |
|---|---|---|
| turtle | fore flippers scored 0.60 on a phase match that should be ~1.0 | a sea turtle beats them TOGETHER; a 10% lag was visually subtle and measurably wrong |
| shark | snout travelled **0%** of the busiest part | a body whose head is nailed in place while the tail works is a toy with a hinge. A real fish yaws its head in counterphase — angular momentum has to go somewhere |

**False positives found in the tool**, each of which would have sent someone "fixing" correct work:

1. Sampling an arbitrary window and calling a periodic animation drifted — needs whole cycles.
2. Measuring foot slip in absolute coordinates — slip is relative to the SURFACE, and a foot locked
   to a treadmill still crosses the frame.
3. Lumping two separate stance phases into one span and counting the reposition between them.
4. Testing antiphase with a plain correlation — that assumes a sinusoid, and a gait has a 60%
   plateau. The shape-independent test is to shift one series by half a cycle and match.
5. Reporting locomotion as drift — a bird flying a path moves a long way per cycle on purpose. The
   distinction is whether the per-cycle displacement is CONSTANT, which needs three cycles to judge,
   not two.
6. Indexing cycles by frame count instead of by timestamp — the rounding error accumulated and made
   a perfectly periodic object look like it drifted a unit or two per cycle.

That ratio — two defects in the work, six in the instrument — is not an argument against the
instrument. It is what an instrument costs, and every one of the six was found in minutes because a
wrong reading is loud. The alternative, judging motion by eye, produced five rounds of failed
guessing on a single inverted sign.

**The rule this adds:** when a check fires, ask whether the SUBJECT or the CHECK is wrong, and
answer it before changing anything. A verification step is code, and code has bugs.

Final state, all six passing:

```
dolphin   PASS      whale     PASS      shark     PASS
turtle    PASS      walker    PASS      gull      PASS
```

---

## Fourth trial: applying the method to work that already existed

The five animals were built before phase 1c existed, so every rate and amplitude in them was
**guessed**. The walking figure was the only one whose keyframes were transcribed. Running 1c over
the other five, and comparing what was there against what is published:

| Subject | Was | Measured | Verdict |
|---|---|---|---|
| dolphin | 1.9 s cycle (0.53 Hz) | **3.1 Hz** in steady swimming | **6× too slow** — it read as a whale |
| humpback | 5.4 s (0.185 Hz) | 0.172 Hz not feeding, 0.23 Hz mean | already in range — **a guess that was right** |
| shark | 1.35 s (0.74 Hz) | **0.51 Hz** cruising, mako | too fast: agitated rather than patrolling |
| turtle | 2.6 s (0.38 Hz) | **0.23 Hz** general swimming | too fast — that is a *descending* turtle's rate |
| gull | ~0.45 s (2.2 Hz) | **2.3 ± 0.3 Hz** normal flight | already correct |

Two of five were right, three were wrong, and one was wrong by a factor of six. **The check is what
tells you which** — the humpback and the gull would have been "corrected" by anyone tuning by feel,
and the dolphin would have stayed wrong forever, because 0.53 Hz looks perfectly plausible on its
own.

Amplitude was checked the same way and gave a different lesson. The dolphin's measured fluke
amplitude is 20% of body length; rather than assume the existing value wrong, the built geometry was
solved — the two tail segments displace `0.095·sin(t1) + 0.215·sin(t1+t2)`, which at 13° gives 23%
peak-to-peak. Close enough that nothing needed changing. **Verify before correcting**, or the fix
becomes the defect.

### The trap this trial found: a measured number on the WRONG AXIS

The source for green turtles gives a flipper excursion of **−73° to +35°, 108° total**. Applied to
the stroke it left the flippers hanging below the shell like two poles. Reading the sentence again:
it describes flipper **TWISTING** — rotation about the flipper's own long axis, which sets angle of
attack. It is not the up-and-down stroke, and in profile it is edge-on and nearly invisible.

> **A measured number applied to the wrong axis is as bad as a guess, and more dangerous, because it
> arrives with a citation.** Record which axis, plane and reference frame each number belongs to at
> the moment it enters the sheet — twist is not stroke, stroke *plane* is not stroke *amplitude*,
> and a body-frame angle is not a world-frame one.

The turtle's twist is now left unmodelled and declared, rather than modelled in the wrong place.

---

## Fifth trial: auditing what the method was actually applied to

Asked whether the method had really been applied to everything, the honest answer was **no** — and
saying so required checking rather than remembering. Each subject's code was scanned for the marks
each phase leaves behind:

```
subject      kind         0    1   1b   1c   1d    2    3    5
starfield    scene        .  yes    .    .    .    .  yes    .
ocean        scene        .    .    .    .    .    .  yes    .
tree         scene        .    .    .    .    .    .  yes    .
rain         scene        .    .    .    .    .    .  yes    .
dolphin      creature   yes  yes  yes  yes    .  yes  yes  yes
walker       creature   yes  yes  yes  yes  yes    .  yes  yes
complete (all 8 markers): NONE
```

**Nothing had the full method.** Seven scenes had received only phase 3. The animals had picked up
1c retroactively and little else. An audit like this takes minutes to write and is worth more than
any assurance, because a claim about process is exactly the kind that memory flatters.

Rebuilding two of the worst from zero shows what the missing phases were worth:

**Tree.** A trunk sways at **0.2-0.33 Hz** while BRANCH modes sit at **2, 7 and 11 Hz** — a spread of
10× to 30×. The old scene used 1.5×, so everything swayed at one rate and the tree moved like
seaweed. Damping also comes from the branches: **10.6% with them, 1.3% stripped bare**, which is why
each order must move out of phase with its parent rather than with it.

**Rain.** Terminal velocity is a FUNCTION OF DIAMETER — `v = 9.65 − 10.3·exp(−0.6·d)`, the Gunn &
Kinzer fit. The old scene drew speed and streak length from **independent** random ranges, so a
small drop could out-fall a large one. And a streak is motion blur, so its length is velocity times
exposure. One roll of the dice — the diameter — now sets size, speed, streak and opacity together,
and they cannot contradict each other.

That second one is the general lesson:

> **Derive every correlated property from one root quantity.** Where two things are related by
> physics, sampling them independently guarantees combinations that cannot exist. The viewer cannot
> name what is wrong, but reads the whole field as false.

---

## Sixth trial: the remaining eight, rebuilt from zero

The audit named seven scenes that had only ever received phase 3. Two were rebuilt in the fifth
trial; this is the rest, plus the walker's missing phase 2. Every one of them had a defect that
phase 1 would have caught before a line was written, and three of those defects were MECHANISMS
RUNNING BACKWARDS — not values slightly off, but the physics pointing the wrong way.

**Ocean.** Waves are DISPERSIVE: c = sqrt(gL/2π), so each wavelength travels at its own speed and
trains drift through one another, building and dissolving the groups that are the sea's signature.
The old scene translated a fixed tile, which can never do that. Two defects fell out of one
missing question. **Parallax inverted** — the nearest band rolled in 35 s and the furthest in 11 s.
**Speed picked independently of wavelength** — periods 11/17/23/29/35 s against fixed harmonics of
3, 7, 13. Celerity FOLLOWS from wavelength.

Then the sea state itself, as one root quantity per train. At U = 9 m/s: Hs = 0.21·U²/g = 1.73 m,
peak wavelength 67.5 m. And the number that changed the design — the four trains carry a slope
variance of 0.0054 against Cox & Munk's measured 0.0491, so **89% of the sea's slope lives in waves
too short to draw.** The glitter therefore cannot be a test on the drawn surface; it is a
probability, Gaussian in the residual slope with σ = 0.209. Modelling what you are NOT drawing is
what made the glitter path appear.

**Night sky.** The old recipe was `scatter + flicker + parallax`. **Parallax on a starfield is
impossible** — stars are at infinity, so there is no depth for motion to reveal. The sky turns
rigidly about the pole at 15°/hour. Everything else follows from the atmosphere: airmass 1.02 at
80° altitude and 5.59 at 10°, extinction 0.28 mag per airmass, scintillation as airmass^1.75 — so
the horizon empties and reddens without anyone drawing an emptiness. And PLANETS DO NOT TWINKLE:
a disc averages the speckle out, so a steady light among trembling ones is what says "atmosphere".

**Cumulus.** Every base is at the same height, because they all condense at the same level:
125 m per °C of dewpoint spread. Bases across a whole sky lie on ONE PLANE. The old blobs sat at
whatever height each landed. Tops are self-similar (measured perimeter dimension ≈ 1.35), and the
flat base is a CUT through the bubbles, not a slab under them — drawn as a slab it protrudes as a
shelf, a shape no cumulus has.

**Solar system.** T = a^1.5, so a 25× span of distance is a 123× span of period. The Sun sits at a
FOCUS, offset by e·a — 20.6% for Mercury — and equal areas make it run (1+e)/(1-e) = 1.52× faster
at perihelion. Jupiter and Saturn are drawn oblate because they spin in under 11 hours. Io, Europa
and Ganymede keep 1:2:4 because their measured days do.

**Lightning.** The old recipe drew the bolt downward with `stroke-dashoffset`. **Wrong twice.** The
visible flash is the RETURN STROKE and it runs UP from the ground at ~c/3 — 30 µs for the channel,
far too fast to read as a draw. What the eye sees is 3-4 strokes down the same channel ~60 ms
apart; THAT is the flicker, and it was never random opacity. Branches point DOWN because the
stepped leader made them going down, and they fade first because no return stroke passes through
them.

**Ferdinand and Feldt.** Both carried the same inverted-parallax sea. Fixed at the root: a tile
carrying n cycles rolls in (n/2)·sqrt(2πL/g) seconds, and a near band carries fewer cycles, so near
is faster by construction rather than by choice.

**Walker, phase 2.** Every limb was a trapezoid. Limb mass is a PROFILE TABLE and the table is
ASYMMETRIC: the shin's front edge is subcutaneous bone and runs almost straight, while the calf
mass sits entirely behind and peaks at 28% down, falling to an ankle less than half its width. A
leg reads as a leg because of that one-sided bulge. Shoulders were 40% too narrow — biacromial
breadth is 0.259 of stature — and a trunk is an hourglass, not a trapezoid.

### What measuring changed, after it all looked right

Every scene above was judged by eye first and passed. Then they were measured, and **the ocean was
spending 1023 ms of main thread per second of animation** — the thread saturated, 23 fps composited.
The fix was not the obvious one. Cutting the quad count by two thirds recovered only 20%, because
the cost was never the geometry:

```
one Path2D per shade, 26 fills      1023 ms/s   every fill rasterises its whole bounding box,
                                                and each bucket's box was the entire sea
immediate per-quad path fill         673 ms/s   thousands of small boxes instead of 26 huge ones
fillRect per quad                    304 ms/s   no path construction, no scan conversion
```

The same lesson in the sky: 7,000 stars drawn with `beginPath/arc/fill` cost 346 ms/s, and most of
them are one or two pixels across, where a square and a circle are the same picture. `fillRect` for
those and a real disc only for the few big ones: 280 ms/s.

> **A picture that looks right can still be wrong, and looking will never tell you.** Phase 5 is
> not finished at "it renders correctly" — an animation that saturates the main thread is broken
> for anyone whose machine has less headroom than yours. And when the number is bad, measure the
> FIX too: the first two attempts here were reasoned from the wrong cause and bought almost nothing.

### What the instrument got wrong this time

`verify-motion.mjs` reported the walker's ankles and hands as "NOT half a cycle apart" — after the
rebuild, on a figure whose strip plainly showed the offset. The cause was mine: `--cycle` is in
milliseconds and I passed `1.1` for a 1.1-second gait. The shift rounded to zero, so the antiphase
test silently became an in-phase test and confidently reported two correct limbs as broken.

> **A tool that answers a malformed question is worse than one that refuses it.** The guard now
> rejects any cycle under 50 ms rather than quietly computing a zero shift.

---

## Seventh trial: the primitives, which were the worst of all

The scenes were the obvious place to apply the method. The primitives were not, and that is exactly
why they were the worst: twelve behaviours, every one of them `ease-in-out infinite alternate` at a
duration picked to look about right.

Phase 1 asked one question and it changed all twelve at once:

> **Almost every primitive in every motion vocabulary is named after a real dynamical system.**
> sway is a pendulum. float is heave. breathe is respiration. pulse is a heart. flicker is a flame.
> ripple is a surface wave. orbit is Kepler. And a real system does not HAVE a duration you choose
> — it has a duration that follows from one measurable quantity.

```
sway     T = 2π·sqrt(2L/3g)          from the rod's LENGTH — and, Galileo, from nothing
                                     else: not the mass, and barely the amplitude
float    T = 2π·sqrt(draft/g)        from how deep it floats
breathe  T = 60/rate, split 1:2      from the breathing RATE; inhale is half the exhale
pulse    T = 60/bpm, systole 0.30 s  from the heart RATE
flicker  f = 1.5/sqrt(D) Hz          from the fire's DIAMETER
ripple   r = c·t, amplitude ∝ 1/√r   from the wave SPEED
orbit    T = a^1.5, centre at a focus  from the semi-major AXIS
wave     T = (n/2)·sqrt(2πL/g)       from the WAVELENGTH
stagger  delay = x/c                 from the SPACING and a propagation speed
```

**So a primitive's parameter is not its duration. It is the physical quantity, and the duration is
an output.** That one inversion is what all twelve were missing, and it is the same rule the rain
and the ocean reached from the other direction.

Four of them were not merely arbitrary but wrong in kind:

- **drift** ran `linear` with `alternate`. A body that reverses at the end of a constant-velocity
  run changes direction in zero time — infinite acceleration. Real drift wraps or it turns.
- **breathe** was symmetric. At rest the inspiration-to-expiration ratio is about 1:2, so a
  symmetric breathe makes the chest fall as fast as it rises, which a body does only when panting.
- **ripple** used `ease-out`, which decelerates the ring. No free wave decelerates. And the opacity
  faded linearly, where energy spreading around a growing circumference falls as 1/√r.
- **draw** advanced at constant speed. A HAND does not: the two-thirds power law (Lacquaniti,
  Terzuolo & Viviani 1983) says tangential speed goes as radius^(1/3), so you slow in tight curves
  and run in the straights — radius 100 is drawn 2.7x faster than radius 5. Constant-speed
  `stroke-dashoffset` is the machine tell, and reparametrising by measured curvature removes it.

### A CSS easing is not a law

`ease-in-out` is a cubic Bézier, and no cubic Bézier is a cosine. Measured against a true harmonic:

```
ease-in-out    (0.42, 0, 0.58, 1)   max error 1.87% of amplitude
easeInOutSine  (0.37, 0, 0.63, 1)   max error 0.20% of amplitude
sampled from cos()                  exact
```

Sampling the law into keyframes costs nothing to author and is exact, so every primitive here whose
motion has a closed form is sampled and its timing function is `linear`. **The curve belongs in the
keyframes, not in the easing** — an easing can only ever approximate, and it hides which law it was
approximating.

### Verified, not asserted

The captions print each duration, so the arithmetic is checkable against the animation. Then the
page was asked what it was actually running:

```
sway     swayPend 2.01s linear      = 2π·sqrt(2·1.5/3g)      ✓
float    heave 1.42s linear         = 2π·sqrt(0.5/g)         ✓
breathe  breathIE 4.29s linear      = 60/14                  ✓
pulse    heart72 0.83s linear       = 60/72                  ✓
flicker  flameFlick 0.163s linear   = sqrt(0.06)/1.5         ✓
wave     roll 6.12s linear          = (3/2)·sqrt(2π·26/g)    ✓
stagger  delays 0.05, 0.25, 0.45 …  = x/60, 0.2 s per 12 units ✓
```

Printing a number in a caption is a claim. Reading it back out of `getComputedStyle` is the check,
and it costs one evaluation.

---

## Eighth trial: a rate without its amplitude

The tree had already been rebuilt once, and the rebuild was the proudest one — it found the
measured branch modes, 2, 7 and 11 Hz against a trunk at 0.30 Hz, and fixed a scene that had been
swaying like seaweed. Shown the result, the reader said the speeds looked wrong.

They were, and the check that proves it is one line:

```
peak angular velocity = 2πfA
  order 0   0.30 Hz x  1.4 deg =    3 deg/s
  order 4  11.00 Hz x 14.0 deg =  968 deg/s     = 16 degrees PER FRAME at 60 fps
```

Measured on the running page rather than computed, tracking the tip of one twig:

```
                        BEFORE              AFTER
twig tip, peak      1283 px/s           106 px/s        12x
twig tip, mean       515 px/s            38 px/s        14x
per frame at 60fps    21.4 px             1.8 px
```

At the scene's own scale — a 9 m tree drawn 392 px tall, so 43.6 px/m — the old twig tip was
averaging **11.8 m/s, more than twice the wind speed that was supposed to be moving it**, forever,
with nothing paying for it.

### Where the method let this through

Phase 1c asks for rates and insists each one carries its axis. It never asks for amplitudes. So the
frequencies were researched and the amplitudes were invented — invented *plausibly*, growing
outward, because obviously a twig moves more than a trunk. Every individual number looked
defensible. Their product was absurd.

> **A rate without its amplitude is half a measurement, and it is the half nobody sees.** What the
> eye reads is displacement and velocity. `2πfA` turns any frequency-amplitude pair into a speed
> you can hold against something physical already in the scene — the wind speed, the walking speed,
> a body length per second. It is one line of arithmetic and it catches an invented amplitude
> instantly.

Both rules are now in the method: **phase 1c pairs every rate with an amplitude and sources it**,
and **phase 5 computes peak speed and compares it to something physical**.

Where the amplitude has no published value, it is derived from what drives the motion. Here that
turned out to split the tree's movement in two, which is also what a tree actually does:

- **SLOW** — the gust deflection. This is the static response, so it grows outward with compliance:
  `[2.0, 2.8, 4.0, 5.6, 7.9, 10.4]` degrees over an 11 s gust. It carries all the large angles.
- **FAST** — each mode's own oscillation, driven by turbulence whose energy falls as `f^(-5/3)`.
  Relative to the trunk band the forcing is 0.206 at 2 Hz, 0.072 at 7 Hz, 0.050 at 11 Hz. Times
  compliance, the amplitudes barely grow at all: `[2.2, 0.64, 0.32, 0.31, 0.43, 0.58]` degrees.

### Weight and colour, which were also missing

The same reader named two more things the method never asked for, and both were absent:

**Loaded members bow.** A branch is a cantilever under its own weight and its leaves', so it curves,
and the curvature gathers toward the tip rather than spreading evenly — a symmetric arc is a rope.
Every branch here was a straight line, and **straight is what weightless looks like**.

**Turnable surfaces have two faces.** A leaf's underside has no palisade layer and often carries wax
or hairs, so it is markedly paler and matte. That is why a crown flashes pale when a gust turns it
over — a real, nameable event. With one colour per leaf it cannot happen at all. The flip also
belongs to the TWIG, not the leaf: the eddies that move leaves are around 10 cm across, so every
leaf on one twig is inside the same one and they turn together, in patches.

And the geometry had an arithmetic error the method should have caught in phase 2. **Leonardo's
rule**: the daughters' cross-sections sum to the parent's, so `r_child = r_parent·n^(-1/2)` —
×0.707 for two daughters, ×0.577 for three. The code used a flat 0.62 for both, so every three-way
fork carried more wood out of the node than came into it.

### And the fix had to be measured too

Correcting the tree took it from 45 animated nodes to about 250, and the first correct version cost
**534 ms/s of main thread at 39 fps**. Composing the two rotations onto one element instead of
nesting a group for each changed nothing at all — 537 ms/s — because the cost was never the groups.
It was 530 separate leaf animations.

The fix came from the physics, not from the profiler: leaves on one twig share an eddy, so they
flutter together. One animation per twig instead of per leaf is both correct and **285 ms/s at 60
fps**. The cheap version and the true version were the same version, which is the second time in
this directory that has happened.

---

## Ninth trial: three passes on one tree, and the third was still wrong

Told the tree's motion still was not natural, I stopped tuning and looked at frames instead of
numbers. Six of them, 200 ms apart: **almost identical**. Having killed the buzz, I had produced a
photograph with twitching leaves.

Three passes, three different kinds of wrong:

```
pass 1   every order at nearly one rate      -> waved like seaweed
pass 2   measured rates, invented amplitudes -> buzzed at 968 deg/s
pass 3   measured rates AND amplitudes       -> dead
```

Pass 3 was built out of correct numbers. Both of its animations were right. It was still wrong,
and no further tuning of a number could have fixed it, because the error was structural:

> **A tree in wind is a randomly driven damped system, and a periodic loop cannot represent one.**
> A randomly driven oscillator has a WANDERING amplitude; a keyframe loop has a fixed one. Every
> branch of an order moving in exact lockstep, forever, at constant amplitude, is the mechanical
> tell — and it survives any amount of correcting the frequency and the amplitude, because those
> were never the thing that was wrong.

So the tree stopped being animated and started being simulated. Each member is a damped oscillator
with its measured frequency and the measured damping (ζ = 0.106), chasing the deflection the
current wind would hold it at:

```
θ̈ = ω²(θ_target − θ) − 2ζω θ̇        θ_target = lean · u(t)^1.5
```

The wind `u(t)` is one shared turbulent signal, and everything follows from it: the amplitude
wanders because the forcing wanders, the tree leans downwind and recoils rather than swinging
through vertical (**air does not blow backwards**), no two branches are in lockstep, and nothing
repeats. The exponent is 1.5, not 2, because **a tree reconfigures**: leaves fold, the crown
streamlines, and drag grows as U^1.3-1.5 instead of U². That is why trees survive storms, and it
changes the shape of every gust response.

Then three more things went wrong, each worth more than the fix itself.

**The spectrum needs a knee.** The first wind used amplitude ∝ f^(-5/6), which is right for the
inertial subrange and has no low-frequency limit, so a single 50-second component carried 79x the
energy of everything else and the tree did nothing for a minute at a time. The von Kármán
spectrum is FLAT below f ≈ U/L and only then rolls off. Across the same band the spread becomes
about 4x, and there is finally real energy at the 0.30 Hz sway mode, where the oscillator amplifies
it by Q = 4.7.

**The wind was wrong, not the response.** At 6 m/s the model was self-consistent, correctly
parameterised, and the tree still looked dead — because 6 m/s does not move a tree much. No amount
of tuning the response would ever have found that; the fault was in a quantity I had not thought
to question. The anchor is the Beaufort scale, whose whole point is that it **defines wind by what
trees do**: force 5 "small trees in leaf begin to sway", force 6 "large branches in motion", force
7 "whole trees in motion". The scene is force 6 and says so.

> When every part of a model is defensible and the result is still wrong, the error is in a
> quantity you did not think to question. Look for the one you inherited without deciding.

**Decide whether the drawn geometry is loaded or unloaded.** Drawing the intended silhouette and
then applying a 27° mean lean gives a tree permanently swept sideways — a real thing on an exposed
coast, but the giveaway that shape and load were authored as if they were independent. The drawn
shape is now the UNLOADED one, pre-tilted upwind, so the mean wind brings it back to the intended
silhouette.

### And it was cheaper

| tree version | presentedFps | style ms/s | task ms/s |
|---|---|---|---|
| CSS keyframes, one flutter per twig | 59.8 | 87.9 | 284.9 |
| simulated: one rAF loop over 250 members | 59.9 | **42.0** | **221.1** |

Integrating 250 damped oscillators and writing 250 transforms per frame costs **less** than running
250 CSS animations, because the keyframe machinery is not free. Third time in this directory that
the truer version has also been the cheaper one — which is beginning to look like a rule rather
than a run of luck.

### The trap that has now bitten three times

The scene stylesheet gives every `<g>` `transform-box: fill-box`, and `fill-box` re-resolves the
coordinates inside a `transform` ATTRIBUTE, so `rotate(a cx cy)` stops meaning what it says. Driving
the tree by attribute made it come apart at every joint. It is recorded in report.md §7b, it
dismembered the walker, and it has now dismembered the tree. **Anything driven by the transform
attribute must pin `transform-box: view-box` and `transform-origin: 0 0` itself** — a global
stylesheet rule that changes what an attribute means is a landmine, and the fix is at the joint.

---

## Tenth trial: three "corrections" that each made it worse

Told the tree was now bad and the very FIRST version had been natural and fluid, I stopped arguing
and rendered them side by side. The reader was right, and it was not close.

v1 was 0.7-5.2 degrees per order, every order between **0.09 and 0.14 Hz** — seven- to
eleven-second cycles, `ease-in-out`, random phase, amplitude growing outward. Slow, smooth,
coupled. What I replaced it with, over three passes, was motion at 2, 7 and 11 Hz, then
per-branch independent forcing at 0.8-3.4 Hz. The eye reads independent fast motion as insect
twitch, not as wood.

**And my own arithmetic had already said so.** The measured branch modes are real, and the wind
does carry energy up there — about 5% of the trunk band, by the spectrum I had computed myself two
passes earlier. Modes carrying 5% of the energy contributed most of the visible motion, because I
rendered them at full amplitude. v1 was, by luck, closer to what a tree actually looks like than
any of my corrections.

> **More physics is not monotonically better.** A detail that carries 5% of the energy and 50% of
> the visual noise is a bad trade, and the number that tells you so may already be sitting in your
> own notes. Fidelity is not the goal; what the object looks like is the goal, and they are not
> the same target.

The geometry went the same way, and worse, because each step was individually defensible: one more
level of recursion, three-way forks more often, self-weight bow, pale undersides on a third of the
leaves. Every one of them is true of a real tree. Together they turned an open, legible crown into
a dense mat with the branch structure buried and the limbs looking wilted. **Density is a
legibility decision, not a fidelity one.**

### The failure was in the verification, not the physics

Phase 5 had grown a lot by this point — forward-kinematics checks, motion tracking, peak-speed
arithmetic, cost measurement. All of it verified the new thing against the LAW. Not one of them
compared the new thing against the old thing. So three regressions passed every gate I owned,
and the only instrument that caught them was a person looking at the screen.

> **When you change something that already worked, put the two side by side before you keep the
> change.** Verifying against the physics tells you the new version is true. It cannot tell you the
> old version was better. This is now in phase 5.

What survived the comparison, and what did not:

```
KEPT   simulation instead of a keyframe loop   the envelope wanders; nothing repeats
KEPT   Davenport coherence as a travelling lag a gust crosses the crown and it ripples
KEPT   two-sided leaves                        but on 20% of twigs, as a rare flash
KEPT   self-weight bow                         at half the sag: weight, not wilt
KEPT   Leonardo's rule                         it was always an arithmetic fix
DROPPED  visible 2/7/11 Hz motion              5% of the energy, most of the noise
DROPPED  per-branch independent fast forcing   reads as twitch, not as wind
DROPPED  a sixth branch order and dense forks  buried the structure
```

The forcing band now stops at 0.55 Hz, and members stiffer than 4 Hz are solved quasi-statically
rather than integrated — which is also the correct approximation, since an 11 Hz oscillator driven
at 0.3 Hz does not ring, it follows. Integrating it at dt = 1/60 gave ω·dt = 1.15, where
semi-implicit Euler is stable but accurate nowhere near, so part of what was being rendered as
motion was the integrator's own noise.

### And the result is a fifth of the cost

| tree version | presentedFps | style ms/s | task ms/s |
|---|---|---|---|
| CSS keyframes, dense crown | 59.8 | 87.9 | 284.9 |
| simulated, dense crown, full band | 59.9 | 42.0 | 221.1 |
| simulated, v1's density, band to 0.55 Hz | 60.0 | **10.5** | **58.8** |

Fourth time in this directory that the truer version has also been the cheaper one. This time it
was the more legible one as well, and legibility was what the reader had been asking for all along.

## What this method costs, and when to skip it

Phases 1 and 3 are perhaps twenty minutes for an object nobody has drawn before, and they are the
two that get skipped. Everything in this directory says that skipping them is what produces the
"almost right but ugly" result that then absorbs hours of tuning — tuning that cannot succeed,
because the defect is in the model rather than in the curve.

Skip the method for a decorative shape with no referent: an abstract loader, a gradient blob, a
pattern. There is no object to be faithful to, so there is nothing to research. **The moment the
thing has a name — a gull, a Corolla, a windmill, a heartbeat — the method applies**, because the
viewer already knows what it should look like and will see it if it is wrong.
