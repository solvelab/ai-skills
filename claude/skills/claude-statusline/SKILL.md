---
name: claude-statusline
description: >-
  Configure or customize the Claude Code status line — the shell-script status bar at the bottom of the CLI that shows model, effort tier, context usage, git state, cost (cumulative session + per-turn token cost), rate limits and prompt-cache health. Use when the user wants to set up, change, share, or debug their Claude Code status line / status bar, mentions statusLine in settings.json or a statusline.sh script, wants a context/token/cost/git/effort indicator in the CLI, or shares a status-line gist to install. Ships a ready-made 3-line script (references/statusline.sh) and the full list of available JSON fields (references/fields.md). Do NOT use for shell prompt themes (PS1, starship, powerlevel10k) or non-Claude-Code status bars.
metadata:
  author: solvelab
  version: 1.1.0
  category: tooling
license: MIT
compatibility: Works in Claude Code (CLI, desktop, IDE). Requires `jq` on PATH. Bash script targets macOS/Linux (incl. WSL); Git Bash on Windows.
---

Read and follow all instructions in ~/ai-skills/skills/claude-statusline/SKILL.md

Reference files are in ~/ai-skills/skills/claude-statusline/references/ — read them when the skill instructions point to them.
