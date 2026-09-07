---
name: lean-code
description: >-
  Governs how much code a change leaves behind: reuse before writing (this codebase, the stdlib,
  the platform, an installed dependency), root-cause fixes over symptom patches, no speculative
  abstraction, and a review lens for over-engineering. Use when implementing a feature,
  refactoring, fixing a bug, adding a dependency or a cache, or reviewing a diff for bloat; and
  when the user says "simplest solution", "YAGNI", "over-engineered", "what can we delete", "less
  code", "do we need this", "add a cache", "faz o mais simples", "não precisa disso", "menos
  código", "o que dá pra apagar", "tá over". Never trims validation at a trust boundary, error handling that prevents
  data loss, or the one runnable check behind non-trivial logic. Do NOT use to decide whether a
  fact or a scope is true (that is verify-before-claiming), to break code already written (that is
  bug-hunter), to trim docs prose (that is documentation), or in place of the built-in /simplify,
  which cleans a finished diff — this lens runs before it.
metadata:
  author: solvelab
  version: 1.1.0
  category: process
license: MIT
compatibility: >-
  Doctrine only; no runtime. The ledger needs grep. Upstream effect measured on Claude Code
  2.1.177/Haiku 4.5; the catalog's own measurement is in research/lean-code/results.md.
---

Read and follow all instructions in ~/ai-skills/skills/lean-code/SKILL.md

Reference files are in ~/ai-skills/skills/lean-code/references/ — read them when the skill instructions point to them.
