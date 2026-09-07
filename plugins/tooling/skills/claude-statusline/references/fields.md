# Claude Code status line — JSON fields reference

Claude Code pipes a JSON object to the status line command via **stdin** on every
update (after each assistant message, after `/compact`, on permission-mode or vim-mode
change; debounced 300ms). The script prints text to **stdout**; each `echo`/`print` is
one row. It runs locally and consumes no API tokens.

Parse with `jq`. Always use fallbacks — many fields are `null` early in a session or
absent entirely.

## Fields

| Field | Notes |
|---|---|
| `model.id`, `model.display_name` | Model identifier and human name. |
| `cwd`, `workspace.current_dir` | Current directory (same value; prefer `workspace.current_dir`). |
| `workspace.project_dir` | Launch directory (may differ from cwd). |
| `workspace.added_dirs` | Extra dirs from `/add-dir`. Empty array if none. |
| `workspace.git_worktree` | Worktree name when inside a linked git worktree. Absent otherwise. |
| `workspace.repo.host/owner/name` | Parsed from `origin`. Absent outside a repo or without an `origin` remote. |
| `cost.total_cost_usd` | Estimated session cost (client-side; may differ from bill). |
| `cost.total_duration_ms` | Wall-clock since session start. |
| `cost.total_api_duration_ms` | Time waiting on the API. |
| `cost.total_lines_added` / `cost.total_lines_removed` | Lines the assistant changed this session. |
| `context_window.total_input_tokens` / `total_output_tokens` | Tokens currently in context (not cumulative, since v2.1.132). |
| — | **There is no cumulative token field, and do not build one by sampling.** `cost.total_cost_usd` is the only running total the payload carries. `current_usage` is the usage of the *last API call*, not of the turn, and the status line re-renders at most 1×/s — a cadence unrelated to when calls happen — so accumulating it samples a stream the script does not control. Measured 2026-09-07 against the host's own ledger: **cache writes +11.5%, cache reads +2.0%, fresh input −92.7%, output −54.5%** on a single-model session; the total **−35.4%** on a four-model one. No fixed sign, no stable magnitude — nothing a multiplier corrects. Read `transcript_path` instead (row below). **Never split state — or the payload — on `\t`**: tab is an IFS *whitespace* character, so bash collapses runs of it and drops empty fields, shifting every later field left. Use `\x1f`. |
| `context_window.context_window_size` | Max context (200000, or 1000000 for extended). |
| `context_window.used_percentage` / `remaining_percentage` | Pre-computed context %; may be `null` early. |
| `context_window.current_usage` | `{input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}`. `null` before first API call and right after `/compact`. |
| `exceeds_200k_tokens` | Boolean, fixed 200k threshold regardless of window size. |
| `effort.level` | `low`/`medium`/`high`/`xhigh`/`max`. Absent when the model has no effort param. Ultracode reports as `xhigh`. |
| `thinking.enabled` | Boolean. |
| `rate_limits.five_hour.used_percentage` / `.resets_at` | 5h window, 0–100 and unix epoch reset. Pro/Max only, after first response. |
| `rate_limits.seven_day.used_percentage` / `.resets_at` | 7d window. Each window may be absent independently. |
| `session_id` | Stable per session — use it for cache filenames, never `$$`/pid. |
| `session_name` | From `--name`/`/rename`. Absent if unset. |
| `prompt_id` | UUID of the prompt being processed. Absent until first input (v2.1.196+). |
| `transcript_path` | Path to the conversation transcript (JSONL). **Observed in a live payload** on 2026-09-07 (Claude Code 2.1.263), pointing at the running session's own file. **This is where session token counts come from.** One `type:"assistant"` row per content block, each with the full `message.usage` — including the `cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens` split the payload does not expose — and a `requestId`. Deduplicate by `requestId` for one record per API call (measured: 1513 rows → 901 calls). Read it incrementally by byte offset: a full re-read cost **96 ms** on a 14 MB transcript, the cursor path **39 ms** for the whole script. Consume a chunk only when the file ends with a newline, or a torn final line is lost. Two things it does **not** carry: the cost — `modelUsage` / `costUSD` live in `type:"cost-state"` rows written at session end, and a live transcript has none (measured: 0 occurrences in a 368-line live session) — and the host's full token count: the transcript's own sums ran **13.5%–93.7% below** what the host billed on the measured session, and why was not determined. Treat the counts as what the transcript records, and `cost.total_cost_usd` as the only live authoritative money. |
| `prompt_cache` | Cache health as the **host** measures it: `warm`, `caching_observed`, `ttl` (`5m`/`1h`), `expires_at`, `requests`, `misses`, `hit_ratio`, `cache_write_tokens`, `last_miss_cause`, `miss_causes`. Note `hit_ratio` is per **request** (127 requests, 0 misses → 0.989 in the observed payload), not per token — the `♻️` segment in `statusline.sh` measures a different thing, the share of *input tokens* served from cache. Do not substitute one for the other. |
| `fast_mode` | Boolean. Fast mode reprices Opus 5 at $10/$50 per MTok instead of $5/$25 — the same 1:5 ratio, so it does not change an input/output cost **split**, only an absolute price. |
| `scratchpad_dir` | Session scratchpad directory. |
| `version` | Claude Code version. |
| `output_style.name` | Active output style. |
| `vim.mode` | `NORMAL`/`INSERT`/`VISUAL`/`VISUAL LINE`. Only when vim mode is on. |
| `agent.name` | Set with `--agent` or agent settings. |
| `pr.number` / `pr.url` / `pr.review_state` | Open PR for the branch. `review_state`: `approved`/`pending`/`changes_requested`/`draft`. Absent until found / after merge. |
| `worktree.name/path/branch/original_cwd/original_branch` | Only during `--worktree` sessions. |

## Fields that are absent (not just null)

`session_name`, `prompt_id`, `workspace.git_worktree`, `workspace.repo`, `effort`, `vim`,
`agent`, `pr`, `worktree`, `rate_limits` (and each window individually). Guard with
`// empty` in jq and check for empty strings in bash.

## Fields that may be `null`

`context_window.current_usage` (before first API call and after `/compact`),
`context_window.used_percentage` / `remaining_percentage` (early in the session).
Guard with `// 0`.

## Context percentage formula

`used_percentage` is **input-only**:
`(input_tokens + cache_creation_input_tokens + cache_read_input_tokens) / context_window_size`.
It does **not** include `output_tokens`. Match this formula if you compute it manually.

## settings.json block

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 2,
    "refreshInterval": 5
  }
}
```

- `padding` (optional, default 0): extra horizontal spacing in characters.
- `refreshInterval` (optional, min 1): re-run every N seconds on top of event updates.
  Set it only for time-based segments (a clock) or when background subagents change git
  state while the session is idle. Leave unset otherwise.
- `hideVimModeIndicator` (optional): set `true` if the script renders `vim.mode` itself.

## Output capabilities

- **Multiple lines**: one `echo`/`print` per row.
- **Colors**: ANSI escapes (`\033[32m` green, `\033[0m` reset).
- **Links**: OSC 8 (`\e]8;;URL\a TEXT \e]8;;\a`). Use `printf '%b'` for reliability.
  Needs a terminal with hyperlink support (iTerm2, Kitty, WezTerm, Windows Terminal).
- **Width**: read `COLUMNS`/`LINES` env vars (set by Claude Code); `tput cols` does not
  work because output is captured, not attached to the tty (v2.1.153+).

## Test with mock input

```bash
echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"/home/user/project"},"context_window":{"used_percentage":25},"session_id":"test"}' | ./statusline.sh
```
