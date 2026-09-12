---
name: documentation
description: >-
  Creates and updates project documentation against a fixed map: one canonical name per reader
  need, one owning document per kind of fact, an English source with a mirror in the project's
  language, and requirements, decisions and dated reports each with a home of their own. Use
  whenever the user mentions README, docs, SETUP, ARCHITECTURE, REQUIREMENTS, ADR, CHANGELOG,
  AGENTS.md, "document this", "write the docs", "update the readme", "standardize the docs",
  "explain how this works", or asks to document a codebase for AI tools or new developers.
  Enforces read-the-code-first, machine-checkable claims, migrate-never-duplicate for legacy
  layouts, and docs that change in the same commit as the code. Do NOT use for non-software
  documentation tasks.
metadata:
  author: solvelab
  version: 4.0.0
  category: docs
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/documentation/SKILL.md

Reference files are in ~/ai-skills/skills/documentation/references/ — read them when the skill instructions point to them.
