---
name: tdd
description: >-
  Decides WHEN a test is written relative to the code it covers: for a change with behaviour worth
  naming, the first artifact is a test that fails for the right reason, and only then the code that
  makes it pass. Use when starting a change whose request names a behaviour or a boundary — an
  empty input, an exclusive edge, a rejected value, a bug report — when a repo or team runs the
  red-green cycle, or the user says "TDD", "test-driven", "red-green", "write the test
  first", "failing test first", "teste primeiro", "escreve o teste antes", "ciclo vermelho-verde".
  Carries the cycle, what makes the first test legitimate, the boundaries a request earns, and when
  the cycle does NOT apply. Opt-in: the catalog's flow implements first and tests after, and this
  skill does not invert it. Do NOT use to break code already written or hunt edge cases after the
  fact (that is bug-hunter), to design a REST negative/fuzz suite (that is
  api-resilience-testing), or to decide how much test a change owes (that floor is lean-code).
metadata:
  author: solvelab
  version: 1.0.0
  category: testing
license: MIT
compatibility: >-
  Doctrine only; no runtime. The stack track assumes Python with pytest. The catalog's own
  measurement of this doctrine is research/tdd/results.md, whose verdict is NO-CLAIM — no figure
  from it appears here.
---

Read and follow all instructions in ~/ai-skills/skills/tdd/SKILL.md

Reference files are in ~/ai-skills/skills/tdd/references/ — read them when the skill instructions point to them.
