#!/usr/bin/env bash
# smoke-install-scripts.sh — end-to-end smoke test for install.sh and update.sh.
#
# The two distribution scripts had no gate: nothing in CI ever ran them, so the behaviors the
# README promises (fast-forward sync, wrapper regeneration, --tool validation) were assertions.
# Measured on 2026-09-04 (issue #113): an uncommitted line in VERSION did not stop update.sh, and
# generate.sh wrote that line into ten tracked plugin.json files; a failing generate.sh exited 0;
# `install.sh --tool` died with `$2: unbound variable`; `--tool bogus` cloned before failing.
#
# How it runs — the same way a user runs them, minus the network:
#   - a bare repository is built from this checkout's HEAD (`git push <bare> HEAD:refs/heads/master`,
#     which works on a branch and on the detached HEAD actions/checkout produces for a pull request);
#   - install.sh clones from it through AI_SKILLS_REPO_URL, never from the GitHub URL, and the
#     https/ssh transports are disabled for every invocation, so a script that ignores the override
#     fails instead of reaching the network;
#   - every invocation gets HOME=<temp dir>, so ~/.claude and ~/.codex are never touched;
#   - "upstream" commits are pushed from a second clone, "local" commits are made in the install.
#
# Output: one PASS/FAIL line per case and a final matrix as counts — refusals that had to fire,
# paths that had to succeed. Exit 1 when any case fails.
#
# WHAT THIS DOES NOT COVER: the real clone URL (network is never used); `curl | bash` as a
# transport; macOS/BSD userland (this runs on GNU tools); a --legacy install on a HOME that has no
# CLAUDE.md yet is covered, but a pre-existing CLAUDE.md with a foreign `## Skills` block is not;
# the guard's own declared blind spots — untracked files under skills/ and edits outside
# VERSION/skills/ — are exercised only in the direction the scripts promise (regeneration runs),
# not judged. The "update clean" case also requires the committed wrappers to match generate.sh's
# output, which the "Wrappers in sync" CI step guarantees for the same HEAD.
#
# Usage: bash scripts/smoke-install-scripts.sh   (from anywhere; CI runs it on every PR)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/ai-skills-smoke.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
# A fixture step that fails (a clone that never happened, a push that was refused) aborts the run
# under set -e before the matrix is printed; name the line so the abort is diagnosable from CI.
trap 'echo "::error::smoke aborted at line $LINENO: $BASH_COMMAND" >&2' ERR

ORIGIN="$WORK/origin.git"
AUTHOR="$WORK/author"
GIT_ID=(-c user.name=smoke -c user.email=smoke@example.invalid)

# ── bookkeeping ───────────────────────────────────────────────────────────
refused=0; refused_total=0
accepted=0; accepted_total=0
failures=()
CASE_ERRORS=()
OUT=""; RC=0

# run <home> <cmd...>: run one script invocation under a fake HOME, capture output and exit code.
# The network transports are switched off for the invocation (protocol.<name>.allow=never): a script
# that reaches for the GitHub URL fails at once with `fatal: transport 'https' not allowed` instead
# of downloading the catalog, and the local-path transport is unaffected. Probed on git 2.47.3.
run() {
    local home="$1"; shift
    mkdir -p "$home"
    set +e
    OUT="$(HOME="$home" AI_SKILLS_REPO_URL="$ORIGIN" \
           GIT_CONFIG_COUNT=2 \
           GIT_CONFIG_KEY_0=protocol.https.allow GIT_CONFIG_VALUE_0=never \
           GIT_CONFIG_KEY_1=protocol.ssh.allow   GIT_CONFIG_VALUE_1=never \
           "$@" 2>&1)"
    RC=$?
    set -e
}

want_rc()      { [ "$RC" -eq "$1" ] || CASE_ERRORS+=("expected exit $1, got $RC"); }
want_rc_not()  { [ "$RC" -ne "$1" ] || CASE_ERRORS+=("expected exit != $1, got $RC"); }
want_out()     { grep -qF -- "$1" <<<"$OUT" || CASE_ERRORS+=("output lacks: $1"); }
want_no_out()  { ! grep -qF -- "$1" <<<"$OUT" || CASE_ERRORS+=("output must not contain: $1"); }
want()         { local desc="$1"; shift; "$@" || CASE_ERRORS+=("$desc"); }

# finish <refuse|accept> <name>: record the case, print its verdict, reset the error list.
finish() {
    local kind="$1" name="$2"
    if [ "$kind" = refuse ]; then refused_total=$((refused_total + 1)); else accepted_total=$((accepted_total + 1)); fi
    if [ "${#CASE_ERRORS[@]}" -eq 0 ]; then
        if [ "$kind" = refuse ]; then refused=$((refused + 1)); else accepted=$((accepted + 1)); fi
        printf 'PASS  [%s] %s\n' "$kind" "$name"
    else
        printf 'FAIL  [%s] %s\n' "$kind" "$name"
        local e; for e in "${CASE_ERRORS[@]}"; do printf '        - %s\n' "$e"; done
        printf '        --- output ---\n%s\n        --------------\n' "$(sed 's/^/        | /' <<<"$OUT")"
        failures+=("$name")
    fi
    CASE_ERRORS=()
}

# upstream_commit <name>: push one new commit to the bare origin from the author clone.
upstream_commit() {
    echo "$1" > "$AUTHOR/smoke-upstream-$1.txt"
    git -C "$AUTHOR" add "smoke-upstream-$1.txt"
    git -C "$AUTHOR" "${GIT_ID[@]}" commit -q -m "smoke: upstream $1"
    git -C "$AUTHOR" push -q origin HEAD:master
}

head_of() { git -C "$1" rev-parse HEAD; }

# ── fixture: a local origin built from this checkout's HEAD ───────────────
git init -q --bare "$ORIGIN"
git -C "$ORIGIN" symbolic-ref HEAD refs/heads/master
git -C "$ROOT" push -q "$ORIGIN" HEAD:refs/heads/master
git clone -q "$ORIGIN" "$AUTHOR"
SKILL_COUNT="$(find "$AUTHOR/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
echo "smoke: origin=$ORIGIN head=$(head_of "$AUTHOR" | cut -c1-7) skills=$SKILL_COUNT"

H1="$WORK/home-main"
INSTALL="$H1/ai-skills"

# ── 1. default install into an empty HOME ─────────────────────────────────
run "$H1" bash "$ROOT/install.sh"
want_rc 0
want_out "Cloning ai-skills into ~/ai-skills"
want_out "$SKILL_COUNT skill(s) symlinked into ~/.claude/skills/ (0 already up to date)"
want "origin is the local bare, not the network" \
    test "$(git -C "$INSTALL" remote get-url origin)" = "$ORIGIN"
want "one symlink per skill" \
    test "$(find "$H1/.claude/skills" -mindepth 1 -maxdepth 1 -type l | wc -l | tr -d ' ')" = "$SKILL_COUNT"
want "symlinks point into the clone" \
    test "$(readlink "$H1/.claude/skills/backlog")" = "$INSTALL/skills/backlog"
finish accept "install: default (claude symlinks)"

# ── 2. idempotent re-run ──────────────────────────────────────────────────
run "$H1" bash "$ROOT/install.sh"
want_rc 0
want_out "already exists. Pulling latest changes"
want_out "0 skill(s) symlinked into ~/.claude/skills/ ($SKILL_COUNT already up to date)"
finish accept "install: idempotent re-run (0 linked / $SKILL_COUNT up to date)"

# ── 3. --legacy ───────────────────────────────────────────────────────────
run "$H1" bash "$ROOT/install.sh" --legacy
want_rc 0
want_out "Adding Skills section to ~/.claude/CLAUDE.md"
want "CLAUDE.md carries the Skills block" grep -q "## Skills" "$H1/.claude/CLAUDE.md"
finish accept "install: --legacy"

# ── 4. --tool codex ───────────────────────────────────────────────────────
run "$H1" bash "$ROOT/install.sh" --tool codex
want_rc 0
want_out "Adding Skills section to ~/.codex/AGENTS.md"
want "AGENTS.md carries the block" grep -q "# AI Skills" "$H1/.codex/AGENTS.md"
finish accept "install: --tool codex"

# ── 5. --tool all ─────────────────────────────────────────────────────────
run "$H1" bash "$ROOT/install.sh" --tool all
want_rc 0
want_out "0 skill(s) symlinked into ~/.claude/skills/ ($SKILL_COUNT already up to date)"
want_out "Codex: Skills section already exists"
want_out "Cursor: rules are in"
want_out "Copilot: instructions are in"
want_out "installed successfully for all"
finish accept "install: --tool all"

# ── 6. --tool bogus: refused before any clone ─────────────────────────────
H2="$WORK/home-bogus"
run "$H2" bash "$ROOT/install.sh" --tool bogus
want_rc 1
want_out "Unknown tool: bogus"
want_out "Supported: claude, codex, cursor, copilot, all"
want_no_out "Cloning"
want "no clone directory was created" test ! -e "$H2/ai-skills"
finish refuse "install: --tool bogus (exit 1, nothing cloned)"

# ── 7. --tool with no value: usage error, not `unbound variable` ──────────
H3="$WORK/home-novalue"
run "$H3" bash "$ROOT/install.sh" --tool
want_rc 1
want_out "--tool requires a value"
want_out "Supported: claude, codex, cursor, copilot, all"
want_no_out "unbound variable"
want_no_out "Cloning"
want "no clone directory was created" test ! -e "$H3/ai-skills"
finish refuse "install: --tool without a value (exit 1, nothing cloned)"

# ── 8. --tool bogus over an existing clone: no pull either ────────────────
upstream_commit 1
BEFORE="$(head_of "$INSTALL")"
run "$H1" bash "$ROOT/install.sh" --tool bogus
want_rc 1
want_no_out "Pulling"
want "HEAD unchanged (no pull ran)" test "$(head_of "$INSTALL")" = "$BEFORE"
finish refuse "install: --tool bogus over an existing clone (no pull)"

# ── 9. update over a clean clone with origin ahead ────────────────────────
run "$H1" bash "$ROOT/update.sh"
want_rc 0
want_out "Regenerating tool wrappers"
want_out "Wrappers regenerated"
want_out "Updated to v"
want_out "smoke: upstream 1"
want "HEAD moved to origin/master" test "$(head_of "$INSTALL")" = "$(head_of "$AUTHOR")"
want "tree clean after regeneration" test -z "$(git -C "$INSTALL" status --porcelain)"
finish accept "update: clean clone, origin ahead (pull + regenerate)"

# ── 10. update with a dirty VERSION: pull yes, regeneration no ────────────
echo "dirtychange" >> "$INSTALL/VERSION"
upstream_commit 2
run "$H1" bash "$ROOT/update.sh"
want_rc 0
want_out "Skipping wrapper regeneration"
want_out " M VERSION"
want_out "checkout -- VERSION skills/"
want_no_out "Wrappers regenerated"
want_out "smoke: upstream 2"
want "HEAD moved to origin/master (pull still ran)" test "$(head_of "$INSTALL")" = "$(head_of "$AUTHOR")"
want "no plugin.json modified" test -z "$(git -C "$INSTALL" status --porcelain | grep -F plugin.json || true)"
want "no plugin.json carries the dirty version" test -z "$(grep -rl dirtychange "$INSTALL"/plugins/*/.claude-plugin/plugin.json 2>/dev/null || true)"
want "only VERSION is dirty" test "$(git -C "$INSTALL" status --porcelain)" = " M VERSION"
finish accept "update: dirty VERSION (pull, skip regeneration, exit 0)"
git -C "$INSTALL" checkout -q -- VERSION

# ── 11. update with an edit outside the generator's inputs: regenerates ───
echo "# local customization" >> "$INSTALL/claude/global/personal-rules.md"
run "$H1" bash "$ROOT/update.sh"
want_rc 0
want_out "Wrappers regenerated"
want_out "Already up to date"
want_no_out "Skipping wrapper regeneration"
want "the personal edit survived" test "$(git -C "$INSTALL" status --porcelain)" = " M claude/global/personal-rules.md"
finish accept "update: edit outside VERSION/skills/ still regenerates"
git -C "$INSTALL" checkout -q -- claude/global/personal-rules.md

# ── 12. update with a failing generate.sh: the failure is visible ─────────
printf '#!/usr/bin/env bash\necho "generate boom"\nexit 7\n' > "$INSTALL/generate.sh"
run "$H1" bash "$ROOT/update.sh"
want_rc 7
want_out "generate boom"
want_out "generate.sh failed (exit 7)"
want_no_out "Wrappers regenerated"
finish refuse "update: failing generate.sh (exit 7 with its output)"
git -C "$INSTALL" checkout -q -- generate.sh

# ── 13. divergence: local commit + upstream commit, update without --force ─
echo "mine" > "$INSTALL/smoke-local-note.txt"
git -C "$INSTALL" add smoke-local-note.txt
git -C "$INSTALL" "${GIT_ID[@]}" commit -q -m "smoke: local commit"
LOCAL="$(head_of "$INSTALL")"
upstream_commit 3
run "$H1" bash "$ROOT/update.sh"
want_rc 1
want_out "Fast-forward failed"
want_out "./update.sh --force"
want_out "git: fatal: Not possible to fast-forward"
want_no_out "hint:"
want "own message precedes git's fatal line" \
    test "$(grep -nF 'Fast-forward failed' <<<"$OUT" | head -1 | cut -d: -f1)" -lt "$(grep -nF 'fatal:' <<<"$OUT" | head -1 | cut -d: -f1)"
want "HEAD unchanged" test "$(head_of "$INSTALL")" = "$LOCAL"
finish refuse "update: diverged, no --force (exit 1 with hint)"

# ── 14. divergence: install.sh re-run gives the same refusal ──────────────
run "$H1" bash "$ROOT/install.sh"
want_rc 1
want_out "Fast-forward failed"
want_out "./update.sh --force"
want_no_out "Need to specify how to reconcile"
want_no_out "hint:"
want_no_out "Configuring for"
want "HEAD unchanged" test "$(head_of "$INSTALL")" = "$LOCAL"
finish refuse "install: re-run over a diverged clone (exit 1 with hint)"

# ── 15. divergence: update --force resets to origin ───────────────────────
run "$H1" bash "$ROOT/update.sh" --force
want_rc 0
want_out "--force: discarding local changes"
want_out "Wrappers regenerated"
want "HEAD is origin/master" test "$(head_of "$INSTALL")" = "$(head_of "$AUTHOR")"
want "local commit's file is gone" test ! -e "$INSTALL/smoke-local-note.txt"
finish accept "update: diverged, --force (reset to origin)"

# ── matrix ────────────────────────────────────────────────────────────────
total=$((refused_total + accepted_total))
passed=$((refused + accepted))
echo ""
echo "smoke: $passed/$total cases passed — refusals that had to fire: $refused/$refused_total, paths that had to succeed: $accepted/$accepted_total"
if [ "${#failures[@]}" -gt 0 ]; then
    for f in "${failures[@]}"; do echo "::error::smoke case failed: $f"; done
    exit 1
fi
