#!/bin/bash
# Claude Code status line (3 lines)
# Line 1: 🤖 model | ⚡ effort | 🧠 thinking | ⏱️ duration | 💰 cost              (identity + session)
# Line 2: 🔗 repo | 🌱 branch | git status | 📝 lines +/- | 🎟️ In · cache · Out   (place + tokens)
# Line 3: 📊 ctx | 🚦 5h | 7d                                                  (all progress meters)
input=$(cat)

IFS=$'\t' read -r MODEL DIR COST CTX EFFORT THINKING RL5 RL7 DUR ADDED REMOVED IN_TOK CACHE_W CACHE_R OUT_TOK <<< "$(jq -r '[
  (.model.display_name // "Claude"),
  (.workspace.current_dir // .cwd // "."),
  (.cost.total_cost_usd // 0),
  (.context_window.used_percentage // "-"),
  (.effort.level // "-"),
  (if .thinking.enabled == true then "enabled" elif .thinking.enabled == false then "disabled" else "-" end),
  (.rate_limits.five_hour.used_percentage // "-"),
  (.rate_limits.seven_day.used_percentage // "-"),
  (.cost.total_duration_ms // 0),
  (.cost.total_lines_added // 0),
  (.cost.total_lines_removed // 0),
  (.context_window.current_usage.input_tokens // 0),
  (.context_window.current_usage.cache_creation_input_tokens // 0),
  (.context_window.current_usage.cache_read_input_tokens // 0),
  (.context_window.current_usage.output_tokens // 0)
] | map(tostring) | join("\t")' <<< "$input")"

# ANSI colors
C_MODEL=$'\e[1;36m'; C_TREE=$'\e[32m'; C_COST=$'\e[1;33m'; C_EFFORT=$'\e[35m'
C_DIM=$'\e[2m'; C_RESET=$'\e[0m'; C_GREEN=$'\e[32m'; C_YELLOW=$'\e[33m'; C_RED=$'\e[31m'
C_THINK_ON=$'\e[1;34m'   # bright blue when thinking is enabled
C_THINK_OFF=$'\e[31m'    # red when thinking is disabled
SEP=" ${C_DIM}|${C_RESET} "

join() { local out="" p; for p in "$@"; do out="${out:+$out$SEP}$p"; done; printf '%s\n' "$out"; }

# bar <pct-int> [width] — filled ▓ / empty ░ bar (default width 10)
bar() {
  local pct=$1 width=${2:-10} filled i b=""
  filled=$(( pct * width / 100 ))
  [ "$filled" -gt "$width" ] && filled=$width
  [ "$filled" -lt 0 ] && filled=0
  for ((i = 0; i < width; i++)); do
    if [ "$i" -lt "$filled" ]; then b+="▓"; else b+="░"; fi
  done
  printf '%s' "$b"
}

# human <n> — 1234 -> 1.2k, 1500000 -> 1.5M
human() {
  local n=$1
  if   [ "$n" -ge 1000000 ]; then awk "BEGIN{printf \"%.1fM\", $n/1000000}"
  elif [ "$n" -ge 1000 ];    then awk "BEGIN{printf \"%.0fk\", $n/1000}"
  else printf '%s' "$n"; fi
}

# pct_color <pct-int> — green <50, yellow 50-79, red >=80
pct_color() {
  if   [ "$1" -ge 80 ]; then printf '%s' "$C_RED"
  elif [ "$1" -ge 50 ]; then printf '%s' "$C_YELLOW"
  else printf '%s' "$C_GREEN"; fi
}

# meter <label> <pct> — "label ▓▓▓░░░░░░░ 42%" with a colored bar+percent
meter() {
  local label="$1" p="${2%%.*}" col
  col="$(pct_color "$p")"
  printf '%s %s%s%s %s%s%%%s' "$label" "$col" "$(bar "$p" 8)" "$C_RESET" "$col" "$p" "$C_RESET"
}

cd "$DIR" 2>/dev/null

# ---------- Line 1: identity — model | effort | thinking ----------
line1=()
line1+=("🤖 ${C_MODEL}${MODEL}${C_RESET}")
[ "$EFFORT" != "-" ] && line1+=("⚡ ${C_EFFORT}${EFFORT}${C_RESET}")
case "$THINKING" in
  enabled)  line1+=("🧠 ${C_THINK_ON}thinking enabled${C_RESET}") ;;
  disabled) line1+=("🧠 ${C_THINK_OFF}thinking disabled${C_RESET}") ;;
esac
# ⏱️ session duration (adaptive) + 💰 cost
DUR_MS=${DUR%%.*}
if [ "${DUR_MS:-0}" -gt 0 ] 2>/dev/null; then
  TOT_S=$(( DUR_MS / 1000 ))
  D=$(( TOT_S / 86400 )); H=$(( (TOT_S % 86400) / 3600 ))
  M=$(( (TOT_S % 3600) / 60 )); S=$(( TOT_S % 60 ))
  if   [ "$D" -gt 0 ]; then ELAPSED="${D}d ${H}h"
  elif [ "$H" -gt 0 ]; then ELAPSED="${H}h ${M}m"
  else ELAPSED="${M}m ${S}s"; fi
  line1+=("⏱️  ${C_DIM}${ELAPSED}${C_RESET}")
fi
line1+=("💰 ${C_COST}$(printf '$%.2f' "$COST")${C_RESET}")

# ---------- Line 2: place — repo | branch | git status ----------
line2=()
REMOTE=$(git remote get-url origin 2>/dev/null | sed -e 's#^git@github.com:#https://github.com/#' -e 's#\.git$##')
if [ -n "$REMOTE" ]; then
  REPO=$(basename "$REMOTE")
  case "$REMOTE" in
    https://*) line2+=("🔗 $(printf '\e]8;;%s\a%s\e]8;;\a' "$REMOTE" "$REPO")") ;;
    *)         line2+=("🔗 $REPO") ;;
  esac
fi
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
[ -n "$BRANCH" ] && line2+=("🌱 ${C_TREE}${BRANCH}${C_RESET}")
STATUS=$(git status --porcelain 2>/dev/null)
if [ -n "$STATUS" ]; then
  STAGED=$(grep -c '^[MADRC]' <<< "$STATUS")
  MODIFIED=$(grep -c '^.[MD]' <<< "$STATUS")
  dirty=""
  [ "$STAGED" -gt 0 ]   && dirty="${C_GREEN}● ${STAGED}${C_RESET}"
  [ "$MODIFIED" -gt 0 ] && dirty="${dirty:+$dirty }${C_YELLOW}✚ ${MODIFIED}${C_RESET}"
  [ -n "$dirty" ] && line2+=("$dirty")
fi
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null)
case "$GIT_DIR" in
  */worktrees/*) line2+=("🌿 ${C_TREE}${GIT_DIR##*/}${C_RESET}") ;;
esac

# ---------- Line 2 (cont.): lines +/- | 🎟️ tokens ----------
if [ "${ADDED:-0}" -gt 0 ] 2>/dev/null || [ "${REMOVED:-0}" -gt 0 ] 2>/dev/null; then
  line2+=("📝 ${C_GREEN}+${ADDED}${C_RESET} ${C_RED}-${REMOVED}${C_RESET}")
fi
# 🎟️ last-response tokens — In (total) · cache health % · Out
TOTAL_IN=$(( ${IN_TOK:-0} + ${CACHE_W:-0} + ${CACHE_R:-0} ))
if [ "$TOTAL_IN" -gt 0 ]; then
  CACHE_PCT=$(( CACHE_R * 100 / TOTAL_IN ))
  if   [ "$CACHE_PCT" -ge 80 ]; then CACHE_COL="$C_GREEN"
  elif [ "$CACHE_PCT" -ge 40 ]; then CACHE_COL="$C_YELLOW"
  else CACHE_COL="$C_RED"; fi
  line2+=("🎟️  In $(human "$TOTAL_IN") ${C_DIM}·${C_RESET} ${CACHE_COL}${CACHE_PCT}% cache${C_RESET} ${C_DIM}·${C_RESET} Out $(human "${OUT_TOK:-0}")")
fi

# ---------- Line 3: meters — ctx | 5h | 7d (all bars together) ----------
line3=()
if [ "$CTX" != "-" ]; then
  line3+=("📊 $(meter ctx "$CTX")")
else
  line3+=("📊 ctx ${C_DIM}░░░░░░░░ -%${C_RESET}")
fi
[ "$RL5" != "-" ] && line3+=("🚦 $(meter 5h "$RL5")")
[ "$RL7" != "-" ] && line3+=("$(meter 7d "$RL7")")

join "${line1[@]}"
[ "${#line2[@]}" -gt 0 ] && join "${line2[@]}"
join "${line3[@]}"
exit 0
