---
name: claude-statusline
description: >-
  Configure or customize the Claude Code status line — the shell-script status bar at the bottom of the CLI that shows model, context usage, git state, cost, rate limits and prompt-cache health. Use when the user wants to set up, change, share, or debug their Claude Code status line / status bar, mentions statusLine in settings.json or a statusline.sh script, wants a context/token/cost/git indicator in the CLI, or shares a status-line gist to install. Ships a ready-made 4-line script (references/statusline.sh) and the full list of available JSON fields (references/fields.md). Do NOT use for shell prompt themes (PS1, starship, powerlevel10k) or non-Claude-Code status bars.
metadata:
  author: solvelab
  version: 1.0.0
  category: tooling
license: MIT
compatibility: Works in Claude Code (CLI, desktop, IDE). Requires `jq` on PATH. Bash script targets macOS/Linux (incl. WSL); Git Bash on Windows.
---

# Claude Code Status Line

The status line is a customizable bar at the bottom of Claude Code. Claude Code runs a
shell command, pipes JSON session data to it on **stdin**, and renders whatever the
command prints to **stdout**. It runs locally and costs no API tokens.

Use this skill to install the ready-made script, build a custom one, debug a broken
status line, or package one to share.

- **Field reference** (all JSON fields, settings block, null/absent rules): `references/fields.md`
- **Ready-made script** (4 lines, colored, safe): `references/statusline.sh`

---

## CRITICAL: Workflow

1. **Ask what they want** if unclear: install the ready-made script as-is, or a custom
   layout (which segments, one line vs. multi-line). Default to offering the ready-made
   script first — it covers the common case.
2. **Confirm `jq` is installed** (`command -v jq`). The scripts here depend on it. If
   missing, tell the user to install it (`brew install jq` / `apt install jq`).
3. **Write the script** to `~/.claude/statusline.sh` and `chmod +x` it. When adapting a
   script the user found online (a gist, a blog), **read it fully and write the reviewed
   content yourself** — never pipe-execute a downloaded script (`curl … | bash`).
4. **Register it** in `~/.claude/settings.json` under `statusLine` (see below). Preserve
   existing keys — edit, don't overwrite the file.
5. **Test with mock input** before declaring done (see Verify).
6. Tell the user it applies **on their next interaction** with Claude Code (settings
   reload automatically; the row won't change until the next update event).

---

## Install the ready-made script

`references/statusline.sh` renders four lines and degrades gracefully (git line hidden
outside a repo, token line hidden before the first API response, rate-limit segments
hidden on non-subscription accounts):

```
🤖 Opus 4.8 | ⚡ medium | 🧠 thinking enabled | 📊 ctx ▓▓▓▓▓▓░░░░ 63%
🔗 my-project | 🌱 master | ● 2 ✚ 1
🚦 5h ▓▓▓▓▓░░░░░ 58% | 7d ▓▓▓▓▓▓▓▓░░ 84% | 📝 +1347 -156 | ⏱️ 1h 26m | 💰 $2.47
🎟️ In 135k · 95% cache · Out 2k
```

- **Line 1** — model · effort · thinking on/off · context-window bar (green <50, yellow
  50–79, red ≥80).
- **Line 2** — clickable GitHub repo link (OSC 8) · branch (short SHA when detached) ·
  `●` staged / `✚` modified counts · worktree name when in one.
- **Line 3** — rate-limit bars (5h/7d, Pro/Max only) · lines added/removed · session
  duration (adaptive `Dd Hh` / `Hh Mm` / `Mm Ss`) · cost (always last).
- **Line 4** — last-response tokens: total input · **cache health %** (green ≥80, yellow
  40–79, red <40 = cache was invalidated → next turn costs more) · output. Numbers are
  humanized (`k`/`M`).

Steps:

1. Copy `references/statusline.sh` to `~/.claude/statusline.sh`.
2. `chmod +x ~/.claude/statusline.sh`.
3. Add to `~/.claude/settings.json` (merge with existing keys):
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "~/.claude/statusline.sh",
       "padding": 2
     }
   }
   ```

---

## Build a custom status line

Read `references/fields.md` for every available field and its null/absent behavior, then
follow these rules — they are what keep a status line from breaking or lagging:

- **Always provide fallbacks.** `// 0` for numbers that may be null (`used_percentage`,
  `current_usage`), `// empty` for fields that may be absent (`rate_limits`, `effort`,
  `pr`, `worktree`). Check for empty strings before using a value in bash arithmetic.
- **Hide empty segments** instead of printing `0`/`-`. A new session has no tokens, cost,
  or rate limits yet — a segment that would read `In 0 · 0%` should not appear.
- **Keep it fast.** The script runs on every update. In large repos, `git status` can lag;
  cache git output to a temp file keyed by `session_id` (never `$$`/pid — those change
  each run and defeat the cache) and refresh every few seconds.
- **Keep output short.** The bar has limited width and shares its row with system
  notifications on the right. Read `COLUMNS` for the real width (v2.1.153+).
- **Match the context formula.** `used_percentage` is input-only
  (`input + cache_creation + cache_read`), excluding output. Use the same if you compute
  it by hand.
- **Multi-line + escape codes** are more prone to render glitches than plain text. If the
  output garbles, simplify. Use `printf '%b'` (not `echo -e`) for OSC 8 links.

Extend the ready-made script rather than starting from scratch when the user wants "the
same plus X" — its `jq` extraction, `bar()`, `human()`, and `pct_color()` helpers are
reusable.

---

## Verify

Run the script against mock JSON before finishing. Strip ANSI to read it plainly:

```bash
echo '{"model":{"display_name":"Opus 4.8"},"workspace":{"current_dir":"/tmp"},"context_window":{"used_percentage":63,"current_usage":{"input_tokens":4820,"cache_creation_input_tokens":1210,"cache_read_input_tokens":128900,"output_tokens":1834}},"cost":{"total_cost_usd":2.47,"total_duration_ms":5187000,"total_lines_added":1347,"total_lines_removed":156},"effort":{"level":"medium"},"thinking":{"enabled":true},"rate_limits":{"five_hour":{"used_percentage":57.8},"seven_day":{"used_percentage":84.2}}}' \
  | ~/.claude/statusline.sh | sed 's/\x1b\[[0-9;]*m//g'
```

Also test the empty case (`"current_usage": null`, no git repo) to confirm optional
segments disappear cleanly. To exercise the git line, run it from inside a repo with
staged and modified files.

---

## Share a status line

To hand a script to someone else, publish it as a GitHub gist:

```bash
gh gist create ~/.claude/statusline.sh --public \
  --desc "Claude Code status line: model/context/git/cost/cache"
```

The recipient saves it to `~/.claude/statusline.sh`, `chmod +x`, adds the `statusLine`
block to their settings, and installs `jq`. Prefer `--public` for open sharing or omit it
for a secret (unlisted-but-linkable) gist. Manage with `gh gist edit|view|delete <id>`.

---

## Troubleshooting

- **Status line not appearing** — script must be executable (`chmod +x`), must print to
  stdout (not stderr), and the workspace-trust dialog must have been accepted (the command
  runs a shell, like a hook). `disableAllHooks: true` also disables it. Run
  `claude --debug` to see the exit code and stderr of the first invocation.
- **Shows `--` or empty values** — fields are `null` before the first API response. Add
  `// 0` fallbacks. Restart if values stay empty after several messages.
- **Duration looks huge** (e.g. `1428m`) — convert to `Hh Mm`/`Dd Hh` above the hour; the
  ready-made script already does this.
- **OSC 8 link prints as literal `\e]8;;`** — use `printf '%b'`, and confirm the terminal
  supports hyperlinks (`FORCE_HYPERLINK=1 claude` to override detection).
- **Lag / stale output** — a slow script blocks updates; a new update cancels an in-flight
  run. Cache slow git calls (keyed by `session_id`).
- **Windows** — write the `command` path with forward slashes; Git Bash eats backslashes.

---

## Trigger Test Cases

Should trigger on:
- "Configure my Claude Code status line"
- "Add context / cost / git to my statusline"
- "My statusline.sh isn't showing up"
- "Make the status bar show cache usage"
- "My friend sent me this statusline gist, install it"
- "Share my status line with someone"

Should NOT trigger on:
- "Customize my shell prompt / PS1 / starship / powerlevel10k"
- "Set up a tmux status bar"
- "Change the VS Code status bar"
- "Write documentation for this project"
