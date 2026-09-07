---
name: agent-delegation
description: >-
  Answers two questions kept apart: where a cross-cutting rule lives — a deterministic CI script, a
  hook the harness fires, or a skill loaded into context — and, separately, whether one piece of
  work runs in the calling loop or is dispatched to a subagent, which holds no rule, only runs
  under one. Use when a new rule needs a home, when about to spawn a subagent or define an agent, when choosing an agent's tools, model or effort, when a validator and an agent both
  seem to fit, and when the user says "should this be a skill or a hook", "write an agent for
  this", "delegate this", "spawn a subagent", "which model for this", "isso vira skill ou hook",
  "cria um agente pra isso", "delega isso", "qual modelo uso aqui". Do NOT use to decide how much
  code a change leaves behind (that is lean-code), to establish whether a fact is true before
  asserting it (that is verify-before-claiming), to break code already written (that is
  bug-hunter), or to write the prose of a documentation page (that is documentation).
metadata:
  author: solvelab
  version: 1.1.0
  category: process
license: MIT
compatibility: >-
  Doctrine only; no runtime, no CLI, no flag. The artifact kinds it names are the ones an
  assistant harness provides — a context-loaded instruction file, an event hook, a build script and
  a dispatched subagent. Where a harness lacks one of them, the row is unavailable, not wrong.
---

Read and follow all instructions in ~/ai-skills/skills/agent-delegation/SKILL.md
