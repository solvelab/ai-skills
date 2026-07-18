---
name: backlog
description: >-
  Turn a natural-language idea into a structured GitHub backlog item: analyze the current
  repository (or multi-repo workspace) for real context, draft a rich issue (context, problem,
  scope, acceptance criteria, risks, affected files/repos), preview it for approval, then create
  the GitHub issue and add it to the configured GitHub Project v2 with fields set
  (Status/Priority/Size/Estimate) via the gh CLI. Use when the user invokes /backlog <idea>, says
  "create a backlog item", "add this to the backlog", "turn this idea into an issue", "groom this
  idea", or wants an idea registered in a GitHub Project. First run per repo/workspace launches a
  config wizard that writes .github/backlog.yml (repo mode) or backlog.yml (workspace mode). Do NOT
  use for implementing an existing issue (that is execute-backlog), for creating pull requests, or
  for non-GitHub trackers (Jira, Linear, Trello).
metadata:
  author: solvelab
  version: 1.0.0
  category: process
license: MIT
compatibility: >-
  Requires the gh CLI (>= 2.40) authenticated with project,read:project scopes and write access to
  the target repository. Works in any git repository or multi-repo workspace directory.
---

Read and follow all instructions in ~/ai-skills/skills/backlog/SKILL.md

Reference files are in ~/ai-skills/skills/backlog/references/ — read them when the skill instructions point to them.
