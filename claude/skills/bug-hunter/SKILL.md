---
name: bug-hunter
description: >-
  Adversarial testing rite — after implementing a change, actively try to break it instead of only
  confirming the happy path. Use when writing or reviewing tests for a just-implemented change, when a
  tasks.md has a "Testes & Bug-Hunter" group, or when the user says bug hunt, adversarial test, break
  it, anti-forge, or asks to test edge cases/atomicity/races of a specific change. Stack-agnostic
  methodology with opt-in stack tracks in references/ (Python/pytest, FiveM/Lua, .NET plugin loaded
  by a host runtime). Do NOT use for designing a full API test suite from scratch — that is
  api-resilience-testing.
metadata:
  author: solvelab
  version: 2.1.0
  category: testing
license: MIT
compatibility: Works in any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/bug-hunter/SKILL.md

Reference files are in ~/ai-skills/skills/bug-hunter/references/ — read them when the skill instructions point to them.
