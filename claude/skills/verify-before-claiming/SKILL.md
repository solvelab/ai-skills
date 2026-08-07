---
name: verify-before-claiming
description: >-
  Anti-guessing rite: research before asserting, label every claim with its source, and report what
  could not be found instead of producing a plausible substitute. Use when about to state or use an
  API, CLI flag, config key, env var, path, version or behavior not read in this session; when a fact
  depends on a library version; when the answer cannot be found and the gap has to be reported; or
  when the user says "you invented that", "don't guess", "achismo", "não inventa", "chutou",
  "pesquisa antes", "de onde tirou", "where did you see that", "cite the source", "that flag does not
  exist", "out of scope", "não foi isso que eu pedi". Covers the cheapest-first research ladder
  (session context, this repo, the installed dependency, the tool itself, version-pinned docs, web
  search, the user), verified/inferred/unknown claim labelling, the not-found report, and the
  scope-restatement guard against delivering work nobody asked for. Do NOT use for adversarially
  testing code already written (that is bug-hunter), for designing an API test suite (that is
  api-resilience-testing), for writing a project's documentation pages (that is documentation), or
  for the plan-approval gate of a backlog item (that is execute-backlog).
metadata:
  author: solvelab
  version: 1.0.0
  category: process
license: MIT
compatibility: >-
  Works in any environment with filesystem access. Ladder rungs 4-5 need a web-fetch and a web-search
  tool (WebFetch/WebSearch in Claude Code); without them the ladder ends at rung 3 and the run reports
  the gap instead of guessing.
---

Read and follow all instructions in ~/ai-skills/skills/verify-before-claiming/SKILL.md

Reference files are in ~/ai-skills/skills/verify-before-claiming/references/ — read them when the skill instructions point to them.
