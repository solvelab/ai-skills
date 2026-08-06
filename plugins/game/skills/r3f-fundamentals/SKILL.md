---
name: r3f-fundamentals
description: >-
  React Three Fiber fundamentals — Canvas setup, the useFrame/useThree hooks, JSX scene elements,
  pointer events, refs, extend, and Leva debug UI. Use for scene setup, render-loop basics, or any
  R3F question that no more specific r3f skill covers. For animation techniques beyond basic
  useFrame use r3f-animation.
metadata:
  author: solvelab
  version: 1.2.0
  category: game
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---


# React Three Fiber Fundamentals
> **Verified against**: `three@0.185` · `@react-three/fiber@9.7` · `@react-three/drei@10.7` ·
> `react@19.2`. Code blocks tagged `tsx` are complete modules and typecheck against that stack;
> blocks marked `// excerpt` are illustrative fragments. R3F v10 (alpha) renames `state.gl` to
> `state.renderer` and moves to `THREE.Timer` — check the migration guide before adopting it.

## Topics

Each topic is a reference file — read the one the task needs, not the whole set.

| Reference | Covers |
|---|---|
| [useFrame Hook](references/useframe-hook.md) | Quick Start, Canvas Component, useFrame Hook |
| [JSX Elements](references/jsx-elements.md) | useThree Hook, JSX Elements |
| [Event Handling](references/event-handling.md) | Event Handling, primitive Element, extend Function, Refs and Imperative Access, Performance Patterns |
| [Debugging with Leva](references/debugging-with-leva.md) | Common Patterns, Debugging with Leva |

## See Also

- `r3f-geometry` - Geometry creation
- `r3f-materials` - Material configuration
- `r3f-lighting` - Lights and shadows
- `r3f-interaction` - Controls and user input

