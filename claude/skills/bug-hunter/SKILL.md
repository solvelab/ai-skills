---
name: bug-hunter
description: Adversarial testing rite — after implementing a change, actively try to break it instead of only confirming the happy path. Use when writing/reviewing tests for a change, when a tasks.md has a "Testes & Bug-Hunter" group, or when the user says bug hunt, adversarial test, edge cases, atomicity, anti-forge, race condition, fuzz. Has two tracks: Backend (Python/pytest — anti-forge, clamps, atomicity, dependency-down, concurrency) and FiveM/Lua (pure modules, event injection, NUI payload, disconnect cleanup, StateBag races, fallback under failure).
metadata:
  author: your-org
  version: 1.0.0
  category: testing
license: MIT
compatibility: Works in any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/shared/skills/bug-hunter/content.md
