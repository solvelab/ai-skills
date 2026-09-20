# Playing a strip in DOM/CSS

Measured on `solvelab/my-company`, 2026-09-20, Chromium driven over CDP by `playwright-core`,
device pixel ratio 2 and 4. The CSS semantics below are specification-level and carry no version;
the pixel numbers are from that scene and are shown as evidence, not as values to copy.

## The element is a background, not an `<img>`

A strip has to advance frame by frame. With `<img>` that means swapping `src` on a timer: one
frame per framework render, each able to arrive late, and the timer competing with everything
else on the main thread. With a background, the browser advances the strip itself through
`steps()`, on the compositor, and the framework does not take part.

```css
.sprite {
  --sprite-height: 60px;
  /* the cell's aspect ratio: cell width ÷ cell height */
  --frame-width: calc(var(--sprite-height) * 0.615);

  display: block;
  height: var(--sprite-height);
  width: var(--frame-width);
  background-repeat: no-repeat;
  background-size: auto 100%;
  background-position: 0 0;
  /* background-image and --sprite-frames are set per pose */
}

@keyframes sprite-cycle {
  to {
    background-position-x: calc(var(--sprite-frames) * var(--frame-width) * -1);
  }
}

.sprite--walk {
  animation: sprite-cycle 0.5333s steps(8) infinite;   /* 8 frames at 15 fps */
}
```

`background-size: auto 100%` scales the whole strip to the element's height, so **one frame is
exactly `--frame-width` wide**. Advancing the strip is then adding that width, which is what the
keyframe does in absolute units.

Measured, walking: `background-position-x` took the values
`0 / −36.3782 / −72.7564 / −109.135 / −181.891 / −218.269 / −254.647 px`. The frame width was
`36.3782 px`. Every value is an exact integer multiple — the strip lands on frame boundaries.

## The technique that does not work

The approach copied most often is `background-size: N00%` with `background-position` in
percentages. It is wrong, and it is wrong in a way that looks almost right: the frames drift
rather than jumping, so it reads as a bad sprite sheet rather than as a bug.

Percentage positions do not measure the image. Per
[MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/background-position), the offset is:

```
offset = (container width − image width) × p
```

With `background-size: N00%` the image is `N` container widths, so
`container − image = −(N−1) × W`. And
[`steps(N)`](https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/steps) with the
default `end` term produces `p = k/N` for `k = 0..N−1`. The offset is therefore:

```
−(N−1) · W · k/N          instead of the −k · W that frame k needs
```

For `N = 8`, frame 1 lands at `−0.875 W` instead of `−1 W`: one eighth of a frame off, growing
with `k`. Nothing errors. Nothing fails. Part of the neighbouring frame is on screen the whole
time.

## The frame rate

Restricted to divisors of 60, and derived from the travel speed rather than chosen. Both rules,
with their reasons and sources, are in this skill's `SKILL.md`; they are not repeated here so the
two cannot drift apart.

## A static pose is the same strip, paused

When a pose has no dedicated frame — an idle that was never drawn — do not import one from another
sheet, because it brings that sheet's scale with it. Freeze the cycle instead:

```css
.sprite--resting { animation-play-state: paused; }
```

This shows frame 0 of the strip already in use. It costs no asset and cannot introduce a scale
mismatch.

## Reduced motion

`prefers-reduced-motion: reduce` must stop the cycles, and with the animation off the element
shows frame 0 — so frame 0 should be a pose that is legible on its own.

```css
@media (prefers-reduced-motion: reduce) {
  .sprite { animation: none; }
}
```

Verify both branches deliberately, and know what passing looks like in each:

| Branch | What passes |
|---|---|
| `emulateMedia({ reducedMotion: 'no-preference' })` | sampling `background-position-x` over a cycle returns several **distinct** values, every one an integer multiple of the frame width |
| `emulateMedia({ reducedMotion: 'reduce' })` | `background-position-x` stays at `0px` across every sample, and the pose on screen is frame 0 |

The trap this catches: headless Chromium reports `reduce` by default, so a measurement taken
without setting the media explicitly is measuring the reduced path while appearing to measure the
normal one — and the normal path's check above would return a single repeated value, which is
exactly what the reduced branch is supposed to return. Without the two rows, one observation
satisfies both.

## Smooth art is not pixel art

`image-rendering: pixelated` is correct for pixel art and wrong for vector-style art, which it
serrates when scaled down. Set it **per element**, not globally, when a scene mixes both — a
character in one style over furniture in another is a normal state during an art migration.

## The ceiling, and why this document does not give you a number

Each animated figure is one element whose animation runs on the compositor, so the cost that
grows with the count is the layout and paint of the elements, not the animation. There is
therefore a figure count past which a canvas with one draw call per frame is cheaper.

**That crossover was not measured.** The scene these rules come from animates one figure at a
time, so no count here would be anything but a guess wearing a number. Measure it on your own
scene — frame time against figure count, at the device pixel ratio you ship — and only then write
the ceiling down, with the conditions it was taken under. The marker for writing it down belongs
to the `lean-code` skill:

```
lean: DOM/CSS up to <N> simultaneous figures on <conditions> -> move to canvas past that
```
