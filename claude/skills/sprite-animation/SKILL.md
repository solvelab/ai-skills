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

Read and follow all instructions in ~/ai-skills/skills/sprite-animation/SKILL.md

Reference files are in ~/ai-skills/skills/sprite-animation/references/ — read them when the skill instructions point to them.
