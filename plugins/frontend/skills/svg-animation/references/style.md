# Visual register, and what it changes

Style is not decoration applied at the end. It decides **which facts must be drawn**, and the same
object researched to the same depth needs different things depending on the register it is drawn in.

## Ask, do not assume

The register is one of the four things worth asking about when the request does not say (the others
are viewpoint, reading size, and what the object is doing). Ask when the answer would change the
geometry, not merely the palette — and it usually would.

## The registers, and what each one demands

| register | what carries the recognition | what it forgives | what it will not forgive |
|---|---|---|---|
| **flat vector** (this catalogue's default) | silhouette and one or two colour marks | absent texture, absent shading, absent small detail | a wrong silhouette, or a missing recognition mark — a gull without black wingtips is a white blob |
| **line art** | contour and line weight | all colour | inconsistent line weight, and any contour that is not a real edge of the object |
| **painterly / soft** | value and edge quality | imprecise contours | flat lighting, and a light direction that is not declared |
| **isometric / technical** | correct projection and consistent axes | absent perspective | a single element in a different projection — the same two-viewpoint error as a gull drawn from two angles |
| **silhouette only** | outline, and nothing else | everything else | a pose that reads ambiguously; every recognition mark has to migrate into the outline |
| **pixel / low-res** | the pose at the actual pixel count | detail below the grid | anything that relies on a mark smaller than a pixel |

## The rule that generalises

**Lower the register and the recognition marks must get LOUDER, not fewer.** A flat-vector gull
needs its black wingtips more than a painterly one does, because it has nothing else to be
recognised by. The instinct to simplify a mark along with everything else is what turns a stylised
animal into an anonymous shape.

Measured example, from this repository: the gulls were rebuilt with correct two-bone wing anatomy,
correct proportions in units of body length, and a documented profile viewpoint — and still read as
dark blobs, because they were drawn in one uniform slate. *Larus argentatus* is a WHITE bird with a
pale grey mantle, black outer primaries carrying white mirrors, and a yellow bill with a red gonys
spot. Adding that plumage changed no geometry at all and turned them into gulls. **In a flat
register, colour was carrying the entire recognition and had never been researched.**

## Register interacts with density

`growth-structure` records that density is a legibility decision rather than a fidelity one. The
register is what sets the budget: a painterly crown can absorb detail that a flat-vector crown
cannot, because flat shapes accumulate into a mat while soft ones accumulate into a mass. Four
individually-true additions to a tree — another level of recursion, more three-way forks,
self-weight bow, pale leaf undersides — together buried the branch structure. **In a flat register,
every added detail competes with the silhouette for the same attention.**

## What style never excuses

The physics. A stylised tree still sways at the frequency a tree sways at, a stylised wheel still
turns at `v/r`, a stylised gull still beats its wings the way a gull does. Register changes what is
DRAWN; it does not change what is TRUE about how the thing moves, and a stylised object with
invented motion reads as broken rather than as stylised.
