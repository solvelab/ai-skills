---
name: r3f-animation
description: >-
  React Three Fiber animation — time-based useFrame motion, GLTF clips via useAnimations,
  react-spring physics, morph targets, skeletal animation, zustand-driven animation state, and
  tuned procedural walk/jump cycles. Use when animating objects or characters. useFrame basics
  live in r3f-fundamentals; drag gestures in r3f-interaction. Do NOT use for 2D, SVG or CSS
  animation (that is `svg-animation`).
metadata:
  author: solvelab
  version: 1.2.1
  category: game
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---


# React Three Fiber Animation
> **Verified against**: `three@0.185` · `@react-three/fiber@9.7` · `@react-three/drei@10.7` ·
> `react@19.2`. Code blocks tagged `tsx` are complete modules and typecheck against that stack;
> blocks marked `// excerpt` are illustrative fragments. R3F v10 (alpha) renames `state.gl` to
> `state.renderer` and moves to `THREE.Timer` — check the migration guide before adopting it.

## Topics

Each topic is a reference file — read the one the task needs, not the whole set.

| Reference | Covers |
|---|---|
| [GLTF Animations with useAnimations](references/gltf-animations-with-useanimations.md) | useFrame Basics, GLTF Animations with useAnimations |
| [Spring Animation (@react-spring/three)](references/spring-animation-react-springthree.md) | Spring Animation (@react-spring/three), Morph Targets |
| [Procedural Animation Patterns](references/procedural-animation-patterns.md) | Skeletal Animation, Procedural Animation Patterns, Drei Animation Helpers |
| [State Management Performance](references/state-management-performance.md) | Animation with Zustand State, State Management Performance |
| [Procedural Walk Cycle (Bipedal Character)](references/procedural-walk-cycle-bipedal-character.md) | Performance Tips, Procedural Walk Cycle (Bipedal Character), Procedural Jump Animation (Point-to-Point) |

## See Also

- `r3f-assets` - Loading animated GLTF models
- `r3f-fundamentals` - useFrame and animation loop
- `r3f-shaders` - Vertex animation in shaders

