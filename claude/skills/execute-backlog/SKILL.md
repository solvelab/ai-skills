---
name: execute-backlog
description: >-
  Execute an existing GitHub backlog item end-to-end: locate the issue (number, URL or search),
  validate it is complete enough, re-analyze the repo/workspace, present an implementation plan
  for approval BEFORE touching code, implement on a dedicated branch with tests, run the repo's
  discoverable validations, tick the acceptance criteria proven by evidence, open pull request(s)
  with Closes #n, and move the GitHub Project item to the review column. Use when the user invokes
  /execute-backlog <n>, says "implement issue #N", "execute this backlog item", "pick up this
  ticket", or wants an existing issue turned into a PR. Second half of the backlog-first rite:
  consumes the item the backlog skill produced. In a repository with a spec-driven workflow (an
  openspec/ directory) it re-checks the item's spec verdict and validates the change strict before
  the plan goes to approval. Do NOT use for creating backlog items (that is backlog), for merging
  PRs, for deploying, or for non-GitHub trackers.
metadata:
  author: solvelab
  version: 1.8.3
  category: process
license: MIT
compatibility: >-
  Requires the gh CLI (>= 2.40) authenticated with project,read:project scopes, write access to
  the affected repositories, and a local clone (repo mode) or workspace with clones (workspace
  mode). Reuses the backlog skill's config files.
---

Read and follow all instructions in ~/ai-skills/skills/execute-backlog/SKILL.md

Reference files are in ~/ai-skills/skills/execute-backlog/references/ — read them when the skill instructions point to them.
