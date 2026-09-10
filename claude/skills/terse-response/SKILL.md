---
name: terse-response
description: >-
  Governs the shape of the assistant's chat reply when the maintainer wants it terse: drop
  articles, filler, pleasantries, hedging and tool-call narration; keep every negation, number,
  technical term, code block and error string verbatim; never invent abbreviations or arrows;
  answer in the user's language. Yields to full prose for security warnings, irreversible actions,
  sequences whose order could be misread, and a request to clarify. Chat only: code, commits, pull
  requests, issues, docs, memory files and messages to third parties stay in normal prose. Use
  when the user says "terse mode", "be brief", "less tokens", "caveman mode", "modo terso", "fala
  menos", "resposta curta", or when the maintainer's rules file turns it on; "stop terse", "stop
  caveman" or "normal mode" turns it off. Do NOT use for the wording of persisted artifacts (that
  is documentation and conventional-commit), for how much code a change leaves behind (that is
  lean-code), or for structuring a multi-step answer (no catalog skill does).
metadata:
  author: solvelab
  version: 1.0.0
  category: process
license: MIT
compatibility: >-
  Doctrine only; no runtime, no hook, no flag file. Works in any assistant that loads a rules file
  or a skill into the session context. Harvested from JuliusBrussee/caveman (MIT), pinned in
  references/upstream.md.
---

Read and follow all instructions in ~/ai-skills/skills/terse-response/SKILL.md

Reference files are in ~/ai-skills/skills/terse-response/references/ — read them when the skill instructions point to them.
