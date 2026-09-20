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

## The frame rate divides 60

Browsers composite at 60 Hz. A rate that does not divide 60 gives one frame two compositor
updates and the next three. Use 10, 15, 20 or 30. The conventional rate for an 8-frame walk cycle
is 10 fps (<https://novasprite.tech/blog/how-many-frames-sprite-animation>,
<https://www.spritesheets.ai/blog/how-to-create-a-walk-cycle-spritesheet>); the rate that matches
a given travel speed comes from the computation in the skill body, and the two have to agree.

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

Verify this path deliberately: headless Chromium reports `reduce` by default, so a measurement
taken without `emulateMedia({ reducedMotion: 'no-preference' })` is measuring the reduced path
while appearing to measure the normal one.

## Smooth art is not pixel art

`image-rendering: pixelated` is correct for pixel art and wrong for vector-style art, which it
serrates when scaled down. Set it **per element**, not globally, when a scene mixes both — a
character in one style over furniture in another is a normal state during an art migration.

## The ceiling

DOM/CSS carries this cheaply while the scene has tens of animated figures: each is one element
whose animation runs on the compositor. Past that, the cost is layout and paint of the elements
themselves, not the animation, and a canvas with one draw call per frame takes over. Declare the
ceiling where the code lives rather than discovering it (the marker is the `lean-code`
skill's):

```
lean: DOM/CSS up to ~60 simultaneous figures -> move to canvas past that
```
