---
name: execute-backlog
description: >-
  Execute an existing GitHub backlog item end-to-end: locate the issue (number, URL or search),
  validate it is complete enough to execute, re-analyze the current repo/workspace state, present
  an implementation plan for approval BEFORE touching code, implement on a dedicated branch
  following the repo's conventions, add/update tests, run the repo's discoverable validations
  (tests/lint/build/typecheck), open pull request(s) linking the issue (Closes #n), and move the
  GitHub Project item to the review column. Use when the user invokes /execute-backlog <n>, says
  "implement issue #N", "execute this backlog item", "pick up this ticket", or wants an existing
  issue turned into a PR. Uses the backlog skill's config (.github/backlog.yml or workspace
  backlog.yml). Do NOT use for creating backlog items (that is backlog), for merging PRs, for
  deploying, or for non-GitHub trackers.
metadata:
  author: solvelab
  version: 1.0.0
  category: process
license: MIT
compatibility: >-
  Requires the gh CLI (>= 2.40) authenticated with project,read:project scopes, write access to
  the affected repositories, and a local clone (repo mode) or workspace with clones (workspace
  mode). Reuses the backlog skill's config files.
---

Read and follow all instructions in ~/ai-skills/skills/execute-backlog/SKILL.md

Reference files are in ~/ai-skills/skills/execute-backlog/references/ — read them when the skill instructions point to them.
