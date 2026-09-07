#!/bin/bash
# Claude Code status line (3 lines)
# Line 1: 🤖 model | ⚡ effort | 🧠 thinking | ⏱️ duration | 💰 cost              (identity + session)
# Line 2: 🔗 repo | 🌱 branch | git status | 📝 lines +/- | 🎟️ In · cache · Out   (place + tokens)
# Line 3: 📊 ctx | 🚦 5h | 7d                                                  (all progress meters)
input=$(cat)


# NOTE: the separator is \x1f, not \t. Tab is an IFS *whitespace* character, so bash
# collapses runs of it and drops empty fields — one absent value would shift every
# later field left. \x1f is non-whitespace, so empty fields are preserved.
IFS=$'\x1f' read -r MODEL DIR COST CTX EFFORT THINKING RL5 RL7 DUR ADDED REMOVED SESSION_ID TRANSCRIPT API_DUR <<< "$(jq -r '[
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
  (.session_id // ""),
  (.transcript_path // ""),
  (.cost.total_api_duration_ms // 0)
] | map(tostring) | join("\u001f")' <<< "$input")"

# ANSI colors
C_MODEL=$'\e[1;36m'; C_TREE=$'\e[32m'; C_COST=$'\e[1;33m'; C_EFFORT=$'\e[35m'
C_DIM=$'\e[2m'; C_RESET=$'\e[0m'; C_GREEN=$'\e[32m'; C_YELLOW=$'\e[33m'; C_RED=$'\e[31m'
C_THINK_ON=$'\e[1;34m'   # bright blue when thinking is enabled
C_THINK_OFF=$'\e[31m'    # red when thinking is disabled
# effort-tier palette — escalating intensity (low → max)
C_EFF_LOW=$'\e[2;37m'; C_EFF_MED=$'\e[36m'; C_EFF_HIGH=$'\e[1;33m'
C_EFF_XHIGH=$'\e[1;38;5;208m'; C_EFF_MAX=$'\e[1;38;5;196m'
C_HI=$'\e[1;97m'        # bright-white highlight for the max shimmer sweep
C_IN=$'\e[36m'; C_OUT=$'\e[35m'   # token in (cyan) / out (magenta) labels
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
# The k branch TRUNCATES rather than rounds. %.0f would round 999500..999999 up to "1000k", a label
# this function's own thresholds exclude — 1000k is where the M branch starts. The M branch keeps
# %.1f because its ceiling is open, so rounding can never carry it out of its own band.
human() {
  local n=$1
  if   [ "$n" -ge 1000000 ]; then awk "BEGIN{printf \"%.1fM\", $n/1000000}"
  elif [ "$n" -ge 1000 ];    then awk "BEGIN{printf \"%dk\", int($n/1000)}"
  else printf '%s' "$n"; fi
}

# price_rates <model-name> — echoes "IN_RATE OUT_RATE CACHE_READ_MULT" ($/1M, multiplier), or ""
# when the model is unknown. These decide the PROPORTION between the input and output segments and
# nothing else: the absolute figure is the host's `cost.total_cost_usd` (see the token block below),
# so a stale rate mis-splits by a few points and can never print a part larger than the whole.
# Canonical home for these numbers is the bundled `claude-api` skill (model table +
# shared/prompt-caching.md); they are mirrored here only because the split has to be computed
# locally. Cache writes are priced from the TTL the transcript reports, 1.25x (5m) / 2x (1h).
price_rates() {
  case "$1" in
    *Fable*|*Mythos*) echo "10 50 0.025" ;;   # cache reads are 0.025x on Fable 5.1, not 0.1x
    *Opus*)           echo "5 25 0.1" ;;
    *"Sonnet 5"*)     echo "2 10 0.1" ;;
    *Sonnet*)         echo "3 15 0.1" ;;      # Sonnet 4.6 and earlier
    *Haiku*)          echo "1 5 0.1" ;;
    *)                echo "" ;;
  esac
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

# effort_render <level> <session-duration-ms> — icon + escalating color per effort tier.
# NOTE: "ultracode" is not a distinct level — it reports as `xhigh` (same as /effort xhigh),
# so 🚀 xhigh is how an ultracode turn shows up here.
effort_render() {
  case "$1" in
    low)    printf '🐢 %slow%s'    "$C_EFF_LOW"   "$C_RESET" ;;
    medium) printf '⚡ %smedium%s' "$C_EFF_MED"   "$C_RESET" ;;
    high)   printf '🔥 %shigh%s'   "$C_EFF_HIGH"  "$C_RESET" ;;
    xhigh)  printf '🚀 %sxhigh%s'  "$C_EFF_XHIGH" "$C_RESET" ;;
    max)
      # ultracode-style shimmer: a bright point sweeps across the label, one step per second.
      # The status line refreshes at most 1×/s (refreshInterval), so this is a 1-fps pulse, not a
      # smooth sub-second gradient. The frame comes from cost.total_duration_ms — the session clock
      # the HOST advances on every render — and never from date(1): a render must be a function of
      # its payload, or the cheapest check that exists for this script (feed a known payload, diff
      # the output) reports differences that mean nothing.
      local lbl="max" i ch col out="" frame secs="${2%%.*}"
      case "${secs:-}" in ''|*[!0-9]*) secs=0 ;; esac
      frame=$(( (secs / 1000) % ${#lbl} ))
      for ((i = 0; i < ${#lbl}; i++)); do
        ch="${lbl:i:1}"
        if [ "$i" -eq "$frame" ]; then col="$C_HI"; else col="$C_EFF_MAX"; fi
        out+="${col}${ch}${C_RESET}"
      done
      printf '💥 %s' "$out" ;;
    *)      printf '⚡ %s%s%s'     "$C_EFFORT" "$1" "$C_RESET" ;;
  esac
}

cd "$DIR" 2>/dev/null

# ---------- Line 1: identity — model | effort | thinking ----------
line1=()
line1+=("🤖 ${C_MODEL}${MODEL}${C_RESET}")
[ "$EFFORT" != "-" ] && line1+=("$(effort_render "$EFFORT" "$DUR")")
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
# tokens — ↑ In (session) · ♻️ cache health % · ↓ Out (session)
#
# SOURCE: the session transcript, NOT the payload's context_window.current_usage.
#
# WHY NOT THE PAYLOAD. current_usage is the usage of the LAST API CALL, and the status line
# re-renders at most 1x/s (refreshInterval) — a cadence unrelated to when calls happen. Accumulating
# it therefore samples a stream it does not control: a render landing mid-stream banks the same
# input tuple twice, and a call that starts and finishes between two renders is never seen at all.
# Measured 2026-09-07 against the host's own ledger, on a single-model session: cache writes +11.5%,
# cache reads +2.0%, fresh input -92.7%, output -54.5%; on a four-model session the total was -35.4%.
# No fixed sign, no stable magnitude — nothing a multiplier could correct.
#
# WHAT THE TRANSCRIPT GIVES. It writes one `type:"assistant"` row per content block, each carrying
# the full message.usage (including the cache_creation TTL split the payload does not expose) and a
# requestId. Deduplicating by requestId yields exactly one record per API call — measured, 1513 rows
# -> 901 calls. No sampling is involved.
#
# WHAT THIS IS NOT: the session's billed total. The transcript counts less than the host bills
# (-13.5% to -93.7% on the measured session) and WHY was not determined, so these are counts of what
# the transcript records, not of what was charged. 💰 on line 1 is `cost.total_cost_usd`, the only
# live authoritative figure, and it is left exactly as the host reports it.
#
# COSTS ARE A SHARE OF THAT TOTAL, never an independent product. price_rates() decides only the
# input/output proportion, so `~In + ~Out` equals 💰 by construction — the defect this replaced was
# a locally computed part that could exceed the whole. The parts print with a leading ~ to say they
# are derived. A session that used several models is split at the CURRENT model's ratio; that is an
# approximation of the ratio only, never of the total.
#
# STATE. `~/.claude/statusline-usage/<session_id>` holds a resumable read cursor for an append-only
# file: byte offset, running sums, the last requestId seen and the transcript's inode. Re-reading it
# is idempotent and it can be rebuilt by deleting the file — unlike the accumulator it replaced,
# whose state was a sum that could not be re-derived. Files older than 30 days are pruned on the
# first write of a new session. A record that does not parse is discarded whole.
SESS_IN=0; SESS_CW5=0; SESS_CW1H=0; SESS_CR=0; SESS_OUT=0

if [ -z "$TRANSCRIPT" ] || [ ! -r "$TRANSCRIPT" ]; then
  # fields.md documents transcript_path, but fall back to the session id rather than trust it:
  # the transcript is filed as ~/.claude/projects/<slug>/<session_id>.jsonl.
  TRANSCRIPT=""
  [ -n "${SESSION_ID:-}" ] && TRANSCRIPT=$(find "$HOME/.claude/projects" -maxdepth 2 \
    -name "${SESSION_ID}.jsonl" 2>/dev/null | head -1)
fi

if [ -n "$TRANSCRIPT" ] && [ -r "$TRANSCRIPT" ]; then
  usage_state="${HOME}/.claude/statusline-usage/${SESSION_ID:-nosession}"
  # Separator is \x1f, never \t: tab is IFS-whitespace, so bash collapses runs of it and drops
  # empty fields, shifting every later field left and corrupting the record.
  US=$'\x1f'
  OFF=0; LAST_RID=""; INODE=""
  if [ -r "$usage_state" ]; then
    IFS="$US" read -r OFF SESS_IN SESS_CW5 SESS_CW1H SESS_CR SESS_OUT LAST_RID INODE \
      < "$usage_state" 2>/dev/null || true
    case "${OFF}${SESS_IN}${SESS_CW5}${SESS_CW1H}${SESS_CR}${SESS_OUT}" in
      ''|*[!0-9]*) OFF=0; SESS_IN=0; SESS_CW5=0; SESS_CW1H=0; SESS_CR=0; SESS_OUT=0
                   LAST_RID=""; INODE="" ;;
    esac
  fi

  NOW_INODE=$(stat -c %i "$TRANSCRIPT" 2>/dev/null || echo "")
  NOW_SIZE=$(stat -c %s "$TRANSCRIPT" 2>/dev/null || echo 0)
  # a replaced or truncated transcript invalidates the cursor; rebuild from zero
  if [ "$NOW_INODE" != "$INODE" ] || [ "$NOW_SIZE" -lt "$OFF" ]; then
    OFF=0; SESS_IN=0; SESS_CW5=0; SESS_CW1H=0; SESS_CR=0; SESS_OUT=0; LAST_RID=""
  fi

  # Only consume the chunk when the file ends with a newline: a torn final line would be dropped by
  # jq, and advancing past it would lose that call's tokens permanently. Waiting one render costs
  # nothing, since another render always follows.
  if [ "$NOW_SIZE" -gt "$OFF" ] && [ "$(tail -c 1 "$TRANSCRIPT" | od -An -c | tr -d ' ')" = "\n" ]; then
    delta=$(tail -c "+$((OFF + 1))" "$TRANSCRIPT" 2>/dev/null \
      | jq -r 'select(.message.usage) | [
            .requestId // "",
            (.message.usage.input_tokens // 0),
            (.message.usage.cache_creation.ephemeral_5m_input_tokens
              // .message.usage.cache_creation_input_tokens // 0),
            (.message.usage.cache_creation.ephemeral_1h_input_tokens // 0),
            (.message.usage.cache_read_input_tokens // 0),
            (.message.usage.output_tokens // 0)
          ] | @tsv' 2>/dev/null \
      | LC_ALL=C awk -F'\t' -v prev="$LAST_RID" '
          BEGIN { seen[prev] = 1 }
          !seen[$1]++ { i += $2; w5 += $3; w1 += $4; r += $5; o += $6 }
          { last = $1 }
          END { printf "%d %d %d %d %d %s", i, w5, w1, r, o, last }')
    if [ -n "$delta" ]; then
      read -r D_IN D_CW5 D_CW1H D_CR D_OUT D_RID <<< "$delta"
      SESS_IN=$((SESS_IN + D_IN)); SESS_CW5=$((SESS_CW5 + D_CW5))
      SESS_CW1H=$((SESS_CW1H + D_CW1H)); SESS_CR=$((SESS_CR + D_CR))
      SESS_OUT=$((SESS_OUT + D_OUT))
      [ -n "$D_RID" ] && LAST_RID="$D_RID"
    fi
    OFF="$NOW_SIZE"
  fi

  # Two renders can overlap (refreshInterval plus a manual repaint). Both read the same cursor and
  # write the same record, which is harmless — but a slow one finishing last would move the cursor
  # BACKWARDS, and the range between the two offsets would then be counted twice. Re-read the stored
  # offset and refuse to regress: double counting is the defect this whole block exists to remove.
  if [ -n "${SESSION_ID:-}" ]; then
    STORED_OFF=0
    [ -r "$usage_state" ] && IFS="$US" read -r STORED_OFF _ < "$usage_state" 2>/dev/null || true
    case "${STORED_OFF:-}" in ''|*[!0-9]*) STORED_OFF=0 ;; esac
  fi
  if [ -n "${SESSION_ID:-}" ] && [ "$OFF" -ge "$STORED_OFF" ]; then
    if [ ! -e "$usage_state" ]; then
      mkdir -p "${usage_state%/*}" 2>/dev/null
      find "${usage_state%/*}" -maxdepth 1 -type f -mtime +30 -delete 2>/dev/null || true
    fi
    mkdir -p "${usage_state%/*}" 2>/dev/null
    { printf '%s' "$OFF"
      for v in "$SESS_IN" "$SESS_CW5" "$SESS_CW1H" "$SESS_CR" "$SESS_OUT" \
               "$LAST_RID" "$NOW_INODE"; do printf '%s%s' "$US" "$v"; done
      printf '\n'
    } > "$usage_state" 2>/dev/null || true
  fi
fi

SESS_CW=$((SESS_CW5 + SESS_CW1H))
TOTAL_IN=$((SESS_IN + SESS_CW + SESS_CR))
if [ "$TOTAL_IN" -gt 0 ]; then
  CACHE_PCT=$((SESS_CR * 100 / TOTAL_IN))
  if   [ "$CACHE_PCT" -ge 80 ]; then CACHE_COL="$C_GREEN"
  elif [ "$CACHE_PCT" -ge 40 ]; then CACHE_COL="$C_YELLOW"
  else CACHE_COL="$C_RED"; fi
  seg_in="${C_IN}↑ In${C_RESET} $(human "$TOTAL_IN")"
  seg_out="${C_OUT}↓ Out${C_RESET} $(human "$SESS_OUT")"
  RATES=$(price_rates "$MODEL")
  if [ -n "$RATES" ]; then
    read -r IN_RATE OUT_RATE CR_MULT <<< "$RATES"
    # Split 💰 by the weight each side carries, then take the output side as the remainder so the
    # two printed figures sum to the printed total exactly, whatever the rounding does.
    split=$(awk "BEGIN{
      wi = ($SESS_IN + $SESS_CW5*1.25 + $SESS_CW1H*2 + $SESS_CR*$CR_MULT) * $IN_RATE;
      wo = $SESS_OUT * $OUT_RATE;
      t  = wi + wo;
      if (t <= 0) { print \"\"; exit }
      total = $COST + 0;
      ic = int(total * (wi / t) * 100 + 0.5) / 100;
      oc = int(total * 100 + 0.5) / 100 - ic;
      printf \"%.2f %.2f\", ic, oc
    }")
    if [ -n "$split" ]; then
      read -r IN_COST OUT_COST <<< "$split"
      seg_in="$seg_in ${C_COST}~\$${IN_COST}${C_RESET}"
      seg_out="$seg_out ${C_COST}~\$${OUT_COST}${C_RESET}"
    fi
  fi
  line2+=("$seg_in ${C_DIM}·${C_RESET} ♻️ ${CACHE_COL}${CACHE_PCT}%${C_RESET} ${C_DIM}·${C_RESET} $seg_out")
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
# 🌐 api — share of the session clock spent waiting on the model. Both numbers are the host's
# (cost.total_api_duration_ms over cost.total_duration_ms), so this reports rather than estimates.
# It lives on line 3 and not beside ⏱️ because line 1 is full: measured at 79 columns before this
# change, so any segment added there overflows an 80-column terminal. Here the four meters come to
# 80 exactly at typical values.
API_MS=${API_DUR%%.*}
if [ "${API_MS:-0}" -gt 0 ] 2>/dev/null && [ "${DUR_MS:-0}" -gt 0 ] 2>/dev/null; then
  API_PCT=$(( API_MS * 100 / DUR_MS ))
  [ "$API_PCT" -gt 100 ] && API_PCT=100
  line3+=("🌐 $(meter api "$API_PCT")")
fi

join "${line1[@]}"
[ "${#line2[@]}" -gt 0 ] && join "${line2[@]}"
join "${line3[@]}"
exit 0
