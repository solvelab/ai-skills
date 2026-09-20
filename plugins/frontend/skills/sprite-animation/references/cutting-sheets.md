# Cutting a sheet into strips

Recipes measured on `solvelab/my-company`, 2026-09-20, Python 3 with Pillow and NumPy. The method
is the point; the pixel numbers are the evidence behind it.

## Find the frames by connected component, not by a grid

A sheet is rarely a clean grid. Frames touch, gutters vanish where a hairstyle or an outstretched
arm overlaps the neighbour, and rows are packed tight. Splitting on empty rows and columns fails
exactly where it matters: on the measured sheet, `grep`-style gutter detection found **two blobs
for eight figures**, because the walkers touched.

Label the alpha channel into connected components and keep the large ones.

**The four thresholds below scale with the sheet, so derive them, do not copy them.** The values
in the code are the ones used on the measured sheet — 2172×724 px, figures about 430 px tall,
exported from a vector tool with clean alpha:

| Threshold | What it is | How to derive it |
|---|---|---|
| `alpha > 16` | what counts as opaque | an assumption about the export: clean alpha needs only to exclude near-zero. A sheet with a soft outer glow or a JPEG round-trip needs a higher cut, found by looking at the alpha histogram |
| `area > 3000` | the smallest blob that is a figure | a fraction of the expected figure area. Here the figures are ~430 px tall and 3000 px is under 2% of one — enough to drop motion marks and stray dots. Scale it with the square of the figure height, not with the sheet |
| `0.45` (head band) | how much of the frame is head | a property of the character's proportion, not of the sheet: here the hair reaches about 45% down. Measure it once on one frame |
| `+ 2` (cell padding) | slack so nothing touches the cell edge | two pixels at this resolution; one pixel per side is the minimum that survives rounding when the strip is scaled |

A reader who keeps `area > 3000` on a sheet four times larger silently keeps the motion marks.

```python
from collections import deque
import numpy as np
from PIL import Image

image = Image.open(path).convert('RGBA')
opaque = np.array(image)[:, :, 3] > 16
height, width = opaque.shape
seen = np.zeros_like(opaque)
boxes = []

for y in range(height):
    for x in np.nonzero(opaque[y] & ~seen[y])[0]:
        if seen[y, x]:
            continue
        queue = deque([(y, x)])
        seen[y, x] = True
        y0 = y1 = y
        x0 = x1 = x
        area = 0
        while queue:
            cy, cx = queue.popleft()
            area += 1
            y0, y1 = min(y0, cy), max(y1, cy)
            x0, x1 = min(x0, cx), max(x1, cx)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < height and 0 <= nx < width and opaque[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    queue.append((ny, nx))
        if area > 3000:                       # drop motion marks and stray dots
            boxes.append((x0, x1, y0, y1))

boxes.sort(key=lambda b: b[0])                # left to right within a row
```

When components still merge — figures that genuinely overlap — fall back to **one head per
figure**: mask the hair colour in the upper band, group the columns, and cut midway between
neighbouring head centres. Heads are separated even when bodies are not.

## Always render the cut and look at it

Before any code uses the frames, build a contact sheet with the index under each frame and open
it. This is what catches a group cut in the wrong place, a reaction frame mistaken for a cycle
frame, and — measured, and expensive — a group facing the opposite way from the one assumed.

## Align on the head, pad to one cell

Bottom-align every frame so the feet sit on the cell's bottom edge, and horizontally align on the
**head centre**, not the bounding box centre. Frame widths vary with arm swing and motion marks;
centring on the box makes the head shift sideways from frame to frame.

```python
# head centre: the hair colour, upper 45% of the frame
mask = hair[y0:y1 + 1, x0:x1 + 1].copy()
mask[int(mask.shape[0] * 0.45):, :] = False
xs = np.nonzero(mask)[1]
head_centre = (int(xs.min()) + int(xs.max())) / 2
```

One cell for **every** strip the scene can switch between, sized from all of them at once:

```python
left  = max(centre for _, centre in frames)                   # widest left of the head
right = max(image.width - centre for image, centre in frames) # widest right of the head
cell_width  = int(np.ceil(left + right)) + 2
cell_height = max(image.height for image, _ in frames)
```

Then paste each frame at `n * cell_width + round(left - centre)` and
`cell_height - image.height`.

## Checks that catch a bad cut

Run these before the strip reaches the scene. Each one corresponds to a defect that shipped.

| Check | What passes | Catches |
|---|---|---|
| Frame count | Equals what the artist says the sheet holds | A group merged into its neighbour |
| Baseline inside a group | Every frame's lowest opaque row within **1 px** of the group's median | Frames from two different groups mixed |
| Figure height across sheets | Every sheet's median figure height within **2%** of the others | Groups drawn at different zooms |
| Contact sheet | Every index present and consecutive, and every figure in a group facing the direction its file name claims | Direction, reaction frames, wrong group |
| Strip width | `strip width ÷ cell width` equals the frame count the code declares, exactly | Half a figure on screen, silently |

The 2% on figure height is the tolerance that separates a pose difference from a zoom difference:
on the measured sheets the walking group spanned 426–433 px (1.6%) inside one zoom, while the
groups drawn at different zooms differed by 26% and 60%. Anything past a few percent is a scale
difference, not a stride.

On the measured sheets the baseline check was decisive: the walk group had all eight frames at
`200 px` tall with feet at `y = 395`, and the seated group all five at `288–292 px` with feet at
`y = 996–999`. Consistent inside each group, and that is what makes a strip a strip.

## Delivery size

Export at roughly twice the largest size the sprite will render at. The measured scene renders the
figure at about 60 px and the strips ship at 200 px tall — enough for a high-density display, and
small enough that eight frames stay a couple of hundred kilobytes.

Keep the source sheets **outside** the repository that consumes them. Only the cut strips are
build input; the sheets are working files, and they are large.
