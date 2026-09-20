---
name: sprite-animation
description: >-
  Replay ready-made frame-sheet art — a character walking, sitting, working, idling — when the
  frames already exist and the job is to show them without lying about them. Use when cutting a
  sprite sheet into strips, when poses must share one scale, when a figure changes size or jumps
  as it switches pose, when a walk cycle's feet slide or moonwalk, when choosing a frame rate,
  and when an animated figure looks wrong but every test passes. Carries the four defects measured
  on a real scene, each with the rule that prevents it, the formula that binds frame rate to travel
  speed, and the CSS technique that lands on frame boundaries plus the widely-copied one that does
  not. For understanding an object before drawing it, or choosing a technology when no art exists,
  use svg-animation; for 3D, r3f-animation.
metadata:
  author: solvelab
  version: 1.0.0
  category: frontend
license: MIT
compatibility: >-
  Any environment with filesystem access. The cutting recipes use Python with Pillow; the CSS
  technique targets any browser with CSS animations. Verifying the result needs a browser that can
  be driven and measured.
---

# sprite-animation — the sheet is data, not a drawing

> **Not version-bound**: this skill does not depend on a tool version. Its CSS rules are
> specification-level — how `background-position` resolves a percentage and how `steps()` divides
> an animation — and its geometry rules are properties of the art, not of any renderer. The pixel
> numbers quoted as evidence come from one measured scene
> ([`solvelab/my-company`](https://github.com/solvelab/my-company), 2026-09-20, Chromium driven
> over CDP by `playwright-core`, device pixel ratio 2 and 4) and are shown to support the rules,
> never to be copied: stride, travel distance and figure height differ per project, which is why
> every number here is published as the formula that derives it.

The failure this skill exists to prevent is not ugly output. It is output that **passes every
gate**. A sliding foot, a figure that grows when it sits, a character walking backwards: unit
tests pass, the typecheck passes, the linter passes, the screenshot looks like a person. The
defect is found by a human looking at the screen, which is the most expensive reviewer there is.

Four defects, all committed in one session on one scene
([`solvelab/my-company`](https://github.com/solvelab/my-company), 2026-09-20, the manager figure),
each now a rule:

| Defect | What it looked like | Rule |
|---|---|---|
| Direction inferred from the drawing | The figure crossed the room with its back to the viewer | [One sheet per direction](#one-sheet-per-direction) |
| Scale matched by a single feature | Hair width said 1.60, face width said something else, both wrong | [No proxy across views](#scale-is-not-measured-by-proxy) |
| One cell per pose | The figure changed size when it sat down | [One cell for every pose](#one-cell-for-every-pose) |
| Duration chosen instead of rate | Feet slid 2.64× — the body crossed 3.39 figure heights while the legs walked 1.28 | [Bind the rate to the travel](#the-rate-and-the-travel-are-one-number) |

A fifth was avoided only because the technique was measured before being trusted: the
widely-copied `background-size: N00%` approach does **not** land on frame boundaries. See
[`references/css-technique.md`](references/css-technique.md).

## One sheet per direction

Ask for **one sheet per direction, with the direction in the file name** —
`walking-to-the-right.png`, `walking-to-the-left.png`, `seated.png`. Never decide which way a
figure faces by looking at the frames.

This is not "look more carefully". A combined sheet with a left-facing group and a right-facing
group is two groups of nearly identical silhouettes, and the reader who is wrong is wrong
silently until someone watches the animation. Removing the judgement removes the defect class.

When the art arrives as one combined sheet anyway, cut it, render each group large, and have the
**person who drew it** name the directions before writing any code.

## Scale is not measured by proxy

Pose groups on one sheet are often drawn at different zooms. Mixing them without normalising makes
the figure change size between poses.

**There is no single feature that measures scale across different viewing angles.** Hair width,
face width, head width, shoulder width — each changes with the angle, so a profile measured
against a front view produces a number that is precise and meaningless. Measured: the same two
groups gave 1.60 by hair and a different factor by face, and neither survived being looked at.

What works: render the same figure from each group **side by side at candidate scales, aligned at
the feet**, and choose by eye. One comparison image settles it. This is the one place in this
skill where the instrument is a person.

Better still, and the reason it is worth asking for: **art delivered as one sheet per pose is
usually already at one scale**, and then there is nothing to normalise. Verify it rather than
assume it — compare figure heights across sheets before cutting.

## One cell for every pose

Every strip a scene can switch between SHALL share **one cell size**, with the figure's head at
the same x and the feet on the cell's bottom edge.

The reason is how the strips are rendered: a scene sizes the sprite by height, so two strips with
different cell heights are forced to the same rendered height and the figures come out at
different scales. Different head offsets make the head jump sideways on a pose change.

Recipe — cut, align, pad — in [`references/cutting-sheets.md`](references/cutting-sheets.md).

## The rate and the travel are one number

A walking figure that moves across the scene has two speeds: how fast the legs cycle and how fast
the body travels. **Pick one and derive the other.** Choosing both independently is how feet slide,
and nothing in the build fails when they do.

```
advance per cycle = 2 × stride            # stride and advance in figure heights
speed             = advance × fps ÷ frames_per_cycle
duration          = distance ÷ speed
```

- `stride` — horizontal distance between the two feet at maximum extension, divided by the figure
  height. Measure it on the art, from the alpha channel; do not estimate it.
- `2 ×` — one full cycle is two steps. Count the passing poses on the sheet to confirm: a cycle
  with two passing positions is two steps.
- `distance` — how far the figure travels, in figure heights, measured on the rendered scene, not
  assumed from the layout.

Worked, with the numbers from the measured scene:

```
stride    = 148 px on a 433 px figure      = 0.342 heights
advance   = 2 × 0.342                      = 0.684 heights per cycle
speed     = 0.684 × 15 ÷ 8                 = 1.283 heights per second
distance  = 3.39 heights                   (measured in the browser)
duration  = 3.39 ÷ 1.283                   = 2.64 s
```

Before the fix: an 0.8 s cycle over a 1.5 s crossing ran 1.88 cycles — the legs walked 1.28
heights while the body moved 3.39. **Slide factor 2.64.**

Publish the formula next to the constants in the code, and put the whole computation in a test.
The test is cheap and it is the only thing that fails when someone later changes one side:

```ts
const advancePerCycle = 2 * STRIDE;
const heightsPerSecond = (advancePerCycle * WALK_FPS) / WALK_FRAMES;
expect(WALK_MS).toBeCloseTo((CROSSING / heightsPerSecond) * 1000, -2);
```

### The frame rate divides 60

Browsers composite at 60 Hz. A rate that does not divide 60 makes one frame last two compositor
updates and the next last three, and the judder is visible. Use **10, 15, 20 or 30**.

Sanity check on the result, not a rule: a real person walks about 0.8 figure heights per second
(1.4 m/s at 1.75 m). The measured art at 10 fps gives 0.855 — so an 8-frame cycle at the
conventional 10 fps lands on a realistic walking speed. A speed far above that is a run being
played with a walk cycle, and it will read as one.

### When the scene is editable, derive the duration at runtime

A fixed duration is correct only for the layout it was computed against. If the scene can be
rearranged — a level editor, a user-placed desk — the travel distance changes and the slide comes
back silently. Prefer computing the duration from the measured distance at runtime, and mark the
fixed version with the ceiling and the trigger that retires it (`lean-code`).

## Where this skill ends

| Request | Skill |
|---|---|
| The art exists as numbered frames; replay it | **this one** |
| No art yet; understand the object, then draw and animate it | the `svg-animation` skill, `skills/svg-animation/SKILL.md` |
| 3D | the `r3f-animation` skill, `skills/r3f-animation/SKILL.md` |
| Claiming a number without measuring it | the `verify-before-claiming` skill |
| The `lean:` ceiling marker used above | the `lean-code` skill |

All four defects in this skill are instances of one thing: acting on a belief that was never
measured. `verify-before-claiming` is the general rule; this skill is what it looks like when the
subject is a sheet of frames.

## References

- [`references/css-technique.md`](references/css-technique.md) — playing a strip in DOM/CSS: the
  technique that lands on frame boundaries, the widely-copied one that does not and why, reduced
  motion, and the ceiling at which canvas takes over.
- [`references/cutting-sheets.md`](references/cutting-sheets.md) — cutting a sheet into frames by
  connected component, aligning on the head, padding to one cell, and the checks that catch a bad
  cut before it reaches the scene.
