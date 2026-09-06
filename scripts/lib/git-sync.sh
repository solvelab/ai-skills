#!/usr/bin/env bash
# git-sync.sh — the fast-forward pull install.sh and update.sh share. Sourced, never executed.
#
# Both scripts used to carry this block verbatim, and a fix in one did not reach the other: issue
# #113 found install.sh dying on git's raw `fatal: Need to specify how to reconcile divergent
# branches` while update.sh already explained the divergence and how to recover. One function, one
# message (issue #173). scripts/smoke-install-scripts.sh asserts the two scripts print it
# byte-identically.
#
# WHERE IT IS READ FROM: both scripts are documented as `curl … | bash`, where there is no script
# directory to source a sibling from — but the pull only ever runs over an existing clone in
# ~/ai-skills, and that clone carries this file. So each script sources
# `$INSTALL_DIR/scripts/lib/git-sync.sh`, the clone it is about to sync. A clone that predates this
# file is refused by the caller with the hint to run the update.sh that clone carries, once.
#
# WHAT IT DOES NOT COVER: the working tree. A fast-forward that touches a locally modified file fails
# on git's side, and that failure is reported under the divergence message like any other pull
# failure — including a network failure, whose `fatal:` line is the only useful detail and is why
# git's output is kept.

# pull_ff_only <dir>: fast-forward <dir> to its upstream. Returns 1 after printing the divergence
# message when git refuses. advice.diverging=false drops git's nine `hint:` lines; the `fatal:` line
# is kept as an indented detail.
pull_ff_only() {
    local dir="$1" pull_err
    if ! pull_err="$(git -C "$dir" -c advice.diverging=false pull --ff-only --quiet 2>&1)"; then
        echo "  ❌ Fast-forward failed — local changes diverge from origin."
        echo "     Re-run with --force to discard them: cd ~/ai-skills && ./update.sh --force"
        [ -z "$pull_err" ] || printf '     git: %s\n' "$pull_err"
        return 1
    fi
}
