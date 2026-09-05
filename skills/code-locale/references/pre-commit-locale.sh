#!/usr/bin/env bash
# pre-commit-locale.sh — git pre-commit hook: the lines this commit ADDS carry no non-English
# identifier in the machine layer. Doctrine: the `code-locale` skill (solvelab/ai-skills).
#
# WHAT IT DOES
#   git diff --cached --no-color --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ \
#     | PYTHONIOENCODING=utf-8:surrogateescape python3 check-identifier-locale.py --diff -
#   That is the whole check. The detector is the one the skill ships; this file only finds it,
#   runs it on the staged diff, and explains a refusal. Exit 0 and silent when the diff is clean.
#   The four diff flags pin the diff's SHAPE, so a repository's or a user's git config cannot change
#   what the detector reads (measured 2026-09-05, each one a silent approval or a false refusal):
#     --no-ext-diff    `diff.external` replaces the unified diff with a driver's output — an empty
#                      stream, `findings: 0`, and the commit is approved unmeasured.
#     --no-renames     with rename detection (git's default) `git mv orders.py relatorio.py` is a
#                      `rename to` header with no `--- /dev/null`, and the new name is never measured.
#                      Without it a rename is a delete plus an add: the new PATH is measured, and the
#                      moved content is read as added lines (see DOES NOT COVER).
#     --src/dst-prefix `diff.mnemonicPrefix` writes `+++ i/relatorio.txt`; the detector strips only
#                      `b/`, so a path grandfathered in .identifier-locale-allow stops matching.
#   PYTHONIOENCODING=utf-8:surrogateescape keeps a hunk with non-UTF-8 bytes (a latin-1 legacy file)
#   from aborting the detector: undecodable bytes pass through, and only the names are judged.
#   Exit 1 with the detector's findings when a gating tier (pt-verb, pt-noun, pt-morphology, path)
#   reports — the same exit code the detector itself uses. The `en-unknown` tier stays advisory:
#   it prints, and it never refuses a commit (the detector's --gate-unknown is deliberately not
#   passed here; add it to EXTRA_ARGS below once your repository has measured its own noise).
#
# INSTALL — one of:
#   cp pre-commit-locale.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
#     (per clone; .git/ is never versioned)
#   mkdir -p .githooks && cp pre-commit-locale.sh .githooks/pre-commit && chmod +x .githooks/pre-commit
#   git config core.hooksPath .githooks
#     (versioned hooks; the `git config` line runs once per clone — git never sets hooksPath
#     from a repository file, on purpose)
#   A repository that already has a pre-commit hook chains this one from it: `exec` or call
#   `.githooks/pre-commit-locale.sh` at the end of the existing script and keep its exit code.
#
# WHERE THE DETECTOR COMES FROM — first match wins:
#   1. $LOCALE_CHECK — an explicit path, for a repository that vendored the detector.
#   2. $AI_SKILLS_HOME/skills/code-locale/references/check-identifier-locale.py, then the same path
#      under ~/ai-skills — the clone the catalog's install.sh creates. The word lists sit beside
#      the detector there, so the advisory English tier runs in full.
#   3. Download, pinned: https://raw.githubusercontent.com/solvelab/ai-skills/<TAG>/skills/code-locale/references/check-identifier-locale.py
#      fetched with `curl -fsSL`, its sha256 checked with python3 (hashlib — no sha256sum/shasum
#      dependency), cached under `$(git rev-parse --git-dir)/locale-check/<TAG>/` so it is fetched
#      once per tag and never enters the tree. Only the detector is downloaded: in this mode the
#      English word lists are absent, so the hook passes --no-english and says so on stderr. The
#      gating tiers are identical in every mode; only the advisory tier is off here.
#
# THE PIN — applies to source 3 only. Sources 1 and 2 run whatever file is at that path, with no
# digest check: an explicit LOCALE_CHECK is your vendored copy, and the ~/ai-skills clone is at
# whatever commit its owner last pulled — so a commit accepted locally and the CI step
# (references/ci-step.md, always pinned) can run different detector versions. Bump the two together:
#   LOCALE_CHECK_TAG     a release tag of solvelab/ai-skills (`git tag --list 'v*'` in the catalog,
#                        or the Releases page). Never `master`: a gate on a moving branch fails
#                        your commits on someone else's schedule.
#   LOCALE_CHECK_SHA256  sha256 of the detector AT THAT TAG:
#                        curl -fsSL <raw url at the tag> | sha256sum
#                        or, from a clone: git show <tag>:skills/code-locale/references/check-identifier-locale.py | sha256sum
#   A tag changed without its hash fails loudly — a pin that accepts any content is not a pin.
#   LOCALE_CHECK_SHA256=skip disables the digest check, in writing, for a tag-only pin.
#   Both accept an environment override (`LOCALE_CHECK_TAG=v2.22.0 LOCALE_CHECK_SHA256=... git commit`).
#
# THE EXITS — every finding prints the exact line to add:
#   # locale-ok: <why this term has no faithful English name>   on the offending line or the one
#                                                                above it (the waiver covers its
#                                                                own line and the next, nothing further)
#   .identifier-locale-allow                                     one path or segment per line — the
#                                                                only waiver a FILE NAME can carry
#   git commit --no-verify                                       the deliberate bypass. Named, not
#                                                                hidden: the rite informs, the author
#                                                                decides — and the CI step
#                                                                (references/ci-step.md) is the layer
#                                                                that measures a bypassed commit.
#
# WHAT THIS HOOK DOES NOT COVER — a clean commit is not proof of compliance:
#   - `git commit --no-verify`, and every path that never runs pre-commit: `git merge` with a
#     conflict-free fast-forward, `git rebase`, `git cherry-pick`, `git commit --amend --no-verify`,
#     pushes made by another machine or by a GUI with hooks disabled. The CI step is the layer
#     that measures those.
#   - Content outside the detector's EXT_LANG (.py .lua .js .jsx .mjs .cjs .ts .tsx .cs .sql .yml
#     .yaml .json .sh .bash): the file's PATH is still measured when the diff adds the file, and
#     its content is reported as skipped, never as passing. Markdown fences are not scanned here
#     (that is the detector's --markdown-fences mode, for documentation repositories).
#   - Existing content. Only ADDED lines are read (`--diff`); a legacy name already in the tree is
#     never reported, and renaming it is the skill's migration policy, not this hook's job. Partial
#     staging (`git add -p`) is measured as staged: hunks left out of the commit are not read.
#   - A rename is read as delete + add (--no-renames, above). The new path is measured — that is the
#     point — and every line of the moved file is read as ADDED, so renaming a legacy file whose
#     content still carries Portuguese names meets the gate at that moment: fix the names, waive
#     them, or `--no-verify` and let CI record it. A pure rename of an English-clean file is silent.
#   - A detector exit 1 counts as a refusal only when its output carries the `findings:` line the
#     detector prints after a completed scan. Any other exit 1 — a traceback, a wrong LOCALE_CHECK —
#     is reported as the detector failing, and the commit is still refused: nothing was measured.
#   - The advisory English tier in download mode (see 3 above), and everything the detector's own
#     docstring lists under KNOWN LIMIT — a curated word list is not a language model.
#   - A missing python3 REFUSES the commit (exit 1, naming the bypass) instead of approving it: a
#     gate that cannot measure must not approve. Install python3 (3.9+) or commit with --no-verify.
#
# Dependencies: bash 3.2+ (macOS's stock /bin/bash included — every array expansion here is written
# for `set -u` on bash < 4.4, where `"${empty[@]}"` is an unbound variable), git 2.x, python3 (3.9+).
# curl only for the download fallback.

set -u
set -o pipefail

LOCALE_CHECK_TAG="${LOCALE_CHECK_TAG:-v2.21.0}"
LOCALE_CHECK_SHA256="${LOCALE_CHECK_SHA256:-4e72af47225d6259f6b69db638af6db6c586c7ee6800e401941e08c223413ff2}"
# Extra detector flags for this repository, e.g. EXTRA_ARGS=(--gate-unknown) once measured.
EXTRA_ARGS=()

CHECK_REL="skills/code-locale/references/check-identifier-locale.py"
RAW_URL="https://raw.githubusercontent.com/solvelab/ai-skills/${LOCALE_CHECK_TAG}/${CHECK_REL}"

log() { printf '%s\n' "pre-commit-locale: $*" >&2; }

refuse() {
  log "$*"
  log "bypass, if you mean it: git commit --no-verify"
  exit 1
}

verify_digest() {
  # $1 = file. Compares its sha256 with LOCALE_CHECK_SHA256 unless that is `skip`.
  [ "$LOCALE_CHECK_SHA256" = "skip" ] && return 0
  local actual
  actual="$(python3 -c 'import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$1")" || return 1
  if [ "$actual" != "$LOCALE_CHECK_SHA256" ]; then
    log "digest mismatch for the detector at tag ${LOCALE_CHECK_TAG}"
    log "  expected ${LOCALE_CHECK_SHA256}"
    log "  got      ${actual}"
    log "  bump LOCALE_CHECK_TAG and LOCALE_CHECK_SHA256 together (header: THE PIN), or set LOCALE_CHECK_SHA256=skip in writing"
    return 1
  fi
}

locate_check() {
  # Prints the detector path on stdout; returns 1 when no source works.
  if [ -n "${LOCALE_CHECK:-}" ]; then
    if [ -f "$LOCALE_CHECK" ]; then printf '%s\n' "$LOCALE_CHECK"; return 0; fi
    log "LOCALE_CHECK is set but is not a file: ${LOCALE_CHECK}"
    return 1
  fi
  local candidate
  for candidate in "${AI_SKILLS_HOME:-}/${CHECK_REL}" "${HOME}/ai-skills/${CHECK_REL}"; do
    case "$candidate" in /"${CHECK_REL}") continue ;; esac   # AI_SKILLS_HOME unset
    if [ -f "$candidate" ]; then printf '%s\n' "$candidate"; return 0; fi
  done

  local git_dir cache_dir cached tmp
  git_dir="$(git rev-parse --git-dir)" || return 1
  cache_dir="${git_dir}/locale-check/${LOCALE_CHECK_TAG}"
  cached="${cache_dir}/check-identifier-locale.py"
  if [ -f "$cached" ]; then
    verify_digest "$cached" || return 1
    printf '%s\n' "$cached"; return 0
  fi
  command -v curl >/dev/null 2>&1 || { log "no local detector and no curl to download it (header: WHERE THE DETECTOR COMES FROM)"; return 1; }
  mkdir -p "$cache_dir" || return 1
  tmp="${cached}.part"
  log "downloading the detector once, pinned at ${LOCALE_CHECK_TAG}: ${RAW_URL}"
  if ! curl -fsSL "$RAW_URL" -o "$tmp"; then
    rm -f "$tmp"
    log "download failed (is ${LOCALE_CHECK_TAG} a published tag of solvelab/ai-skills?)"
    return 1
  fi
  verify_digest "$tmp" || { rm -f "$tmp"; return 1; }
  mv "$tmp" "$cached" || return 1
  printf '%s\n' "$cached"
}

command -v git >/dev/null 2>&1 || refuse "git not found on PATH"
command -v python3 >/dev/null 2>&1 || refuse "python3 not found on PATH — the detector needs Python 3.9+, and a gate that cannot measure must not approve"

check_path="$(locate_check)" || refuse "could not locate the identifier-locale detector"

# The English word lists live beside the detector. Absent (download mode, or a vendored copy of
# the single file) every segment would be reported as unknown, so the advisory tier is switched
# off and the switch is announced — the gating tiers do not depend on those lists.
# `${arr[@]+"${arr[@]}"}` is the expansion that survives `set -u` with an empty array on bash 3.2
# and 4.3; the plain `"${arr[@]}"` aborts the hook there (measured on bash:3.2 and bash:4.3).
args=(${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"})
if [ ! -f "$(dirname "$check_path")/english-words.txt.gz" ]; then
  args+=(--no-english)
  log "advisory English tier off: english-words.txt.gz is not beside ${check_path} (gating tiers unaffected)"
fi

output="$(git diff --cached --no-color --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ \
  | PYTHONIOENCODING=utf-8:surrogateescape python3 "$check_path" --diff - ${args[@]+"${args[@]}"} 2>&1)"
rc=$?

# The detector prints `findings: N` only after a completed scan. Exit 1 without that line is a
# crash (an uncaught exception also exits 1), not a measurement — and must not be explained as one.
if [ "$rc" -eq 1 ] && ! printf '%s\n' "$output" | grep -q '^findings: '; then
  rc=70
fi

case "$rc" in
  0)
    # Clean. Advisory lines, when any, still deserve the author's eyes.
    if [ -n "$output" ] && printf '%s\n' "$output" | grep -q 'advisory'; then
      printf '%s\n' "$output" >&2
    fi
    exit 0
    ;;
  1)
    printf '%s\n' "$output" >&2
    log "refused: the staged diff adds a non-English name to the machine layer (code-locale)."
    log "  waive one line:   # locale-ok: <why this term has no faithful English name>   (on the line, or the one above)"
    log "  waive a path:     add it to .identifier-locale-allow (one path or segment per line)"
    log "  bypass:           git commit --no-verify   — the deliberate exit; CI measures it anyway"
    exit 1
    ;;
  *)
    printf '%s\n' "$output" >&2
    refuse "the detector itself failed (exit ${rc}, no findings: line); nothing was measured, so nothing is approved"
    ;;
esac
