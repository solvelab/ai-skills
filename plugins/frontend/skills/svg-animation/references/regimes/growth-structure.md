# Regime: growth structure

Anything that branches: a tree, veins, river networks, roots, a lightning channel's shape, coral,
lungs. The geometry regime that usually pairs with a motion regime.

## Must be known before drawing

| # | question | the measured defect that put it here |
|---|---|---|
| 1 | **The branching rule for radius.** | Leonardo's rule: the daughters' cross-sections sum to the parent's, so `r_child = r_parent·n^(-1/2)` — ×0.707 for two daughters, ×0.577 for three. A flat constant was used for both, so every three-way fork carried more material out of the node than came in. |
| 2 | **Length and angle ratios, WITH VARIATION.** | Equal daughters at equal angles build a flat fan. Real crowns are domed because no two limbs get the same share. |
| 3 | **How many levels are LEGIBLE, which is not how many are real.** | One more level of recursion and more three-way forks is more like a real tree and buried the branch structure under a mat of leaves. **Density is a legibility decision, not a fidelity one.** |
| 4 | **Self-weight bow.** | Every member is a cantilever under its own load: it curves, and the curvature gathers toward the tip rather than spreading evenly — a symmetric arc is a rope. Straight is what weightless looks like. |
| 5 | **Whether the drawn shape is loaded or unloaded.** | Drawing the intended silhouette and then applying a mean load gave a tree permanently swept sideways. Decide which shape the geometry is, and say so. |
| 6 | **Terminal elements: how they group.** | Leaves belong to their TWIG, not to themselves — the eddies that move them are ~10 cm across, so every leaf on one twig is inside the same one. Animating each separately was expensive AND wrong: 530 separate animations, 534 ms/s of main thread, and each leaf getting its own weather. |
| 7 | **Two-sided surfaces.** | A leaf's underside has no palisade layer and often carries wax or hairs, so it is markedly paler and matte. That is why a crown flashes pale when a gust turns it over — a real, nameable event that one colour per leaf cannot show. |

## Failure signature

- uniform fan-shaped crown → no variation in length and angle
- structure invisible under its own terminal elements → too many levels
- straight members → weight was left out
- a fork that gets thicker outward → the radius rule was not applied per child count
