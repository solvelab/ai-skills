---
name: r3f-lighting
description: >-
  React Three Fiber lighting — light types and cost, shadows, and the canonical home for
  Environment/IBL/HDR setup (Environment, Lightformer, Sky, Stars, Stage, ContactShadows,
  AccumulativeShadows) plus three-point/outdoor/studio recipes. Use for any lighting, shadow or
  environment-lighting task. Loading HDR/texture files is covered in r3f-assets.
metadata:
  author: solvelab
  version: 1.2.0
  category: game
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---


# React Three Fiber Lighting
> **Verified against**: `three@0.185` · `@react-three/fiber@9.7` · `@react-three/drei@10.7` ·
> `react@19.2`. Code blocks tagged `tsx` are complete modules and typecheck against that stack;
> blocks marked `// excerpt` are illustrative fragments. R3F v10 (alpha) renames `state.gl` to
> `state.renderer` and moves to `THREE.Timer` — check the migration guide before adopting it.

## Topics

Each topic is a reference file — read the one the task needs, not the whole set.

| Reference | Covers |
|---|---|
| [directionalLight](references/directionallight.md) | Quick Start, Light Types Overview, ambientLight, hemisphereLight, directionalLight, pointLight, spotLight, rectAreaLight |
| [Drei Lighting Helpers](references/drei-lighting-helpers.md) | Shadow Setup, Drei Lighting Helpers |
| [Common Lighting Setups](references/common-lighting-setups.md) | Common Lighting Setups, Animated Lighting, Light Helpers, Performance Tips |

## See Also

- `r3f-materials` - Material light response
- `r3f-assets` - Environment maps
- `r3f-postprocessing` - Bloom and light effects

