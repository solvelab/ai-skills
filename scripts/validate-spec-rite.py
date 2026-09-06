#!/usr/bin/env python3
"""Spec-rite gate — a pull request that changes the repository must register the change.

The sibling gates each answer a different question about an OpenSpec change:

  validate-rite.sh            do the mandatory task groups exist, in the right positions?
  validate-rite-evidence.py   does a ticked evidence box say what it ran?
  validate-spec-rite.py       does a change exist at all?

The third question had no gate, and its absence was not neutral: validate-rite.sh loops over
`openspec/changes/*/`, skips `archive`, and with no active change the loop body never runs, so
`fail` stays 0 and the script prints `rite gate OK`. A pull request that recorded nothing read as
approved. PR #80 and PR #84 both shipped new blocking CI gates that way and had to be registered
retroactively by PR #88.

  S1 a diff outside openspec/ carries a change, an archive, or a written waiver
  S2 the waiver names a reason
  S3 the change it carries is ITS change: the diff touches openspec/changes/<id>/ of an active
     change, or the pull request body names one on a `Spec-rite: <id>` line. Until issue #117
     (2026-09-04) the mere existence of any active change registered any diff, and the selftest
     pinned that as a silent case.

KNOWN LIMIT: this proves that a change EXISTS and is LINKED to the diff — by path or by name, never
by content — not that it is honest. A change scaffolded to satisfy the gate passes it, exactly as a
padded evidence box passes the shape gate, and a single tick in the tasks.md of any active change
links any diff to it. Existence and relevance are required, reviewable artifacts; the review is what
judges them. The selftest exercises the decision rules against synthetic inputs, not the git
plumbing that feeds them: a misconfigured checkout is caught by the CI-only base-resolution failure
below, not by the selftest. The one plumbing probe it does run is the path reader, below.

Paths are read with `git diff --name-only -z` and split on NUL, the way validate-skill-version.py
reads them (issue #132). Without `-z`, git wraps any path that carries a non-ASCII, control or quote
character in double quotes with octal escapes (core.quotePath, default true on a fresh checkout and
on the ubuntu runners): `"openspec/changes/<id>/specs/caf\303\251.md"` starts with a quote, not with
`openspec/`, so it stopped being exempt AND stopped touching its own change — the gate reported S3
against a pull request that touched the change it belonged to (measured on issue #172, 2026-09-06).
The selftest commits such a path inside an active change of a throwaway repository and asserts the
diff registers, so the flag cannot be dropped silently.

The waiver is read from the event payload the runner already writes (GITHUB_EVENT_PATH), not from
an environment variable handed to the step: GitHub Actions prints a step's `env:` block into the
build log, so passing the pull request body that way published the whole body on every run —
measured on run 32648727841. A gate must not become a disclosure channel for what it reads. PR_BODY
survives as the deliberate override for running this outside CI.

Exit 1 on any finding. Run from the repo root.
Modes: (default) check this diff   |   --selftest inject one defect per rule and assert detection.
"""
from __future__ import annotations

import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGES = "openspec/changes"

# Everything the spec-driven workflow owns. A diff confined to it needs no separate registration:
# it IS the registration.
EXEMPT_PREFIX = "openspec/"

# Paths the release automation writes on its own (semantic-release). A version bump is not a change
# to the catalog and must not demand a proposal.
EXEMPT_PATHS = {
    "VERSION",
    "CHANGELOG.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
}

# The waiver is authored by whoever opened the pull request, including from a fork. It is matched as
# text and never executed, never interpolated into a command. Anchored to the start of a line so a
# mention of the syntax inside a sentence does not silently waive the gate.
WAIVER = re.compile(
    r"^[ \t>*-]*Spec-rite:[ \t]*none[ \t]*(?:—|--|–|-)[ \t]*(?P<reason>.*\S)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
# A bare `Spec-rite: none` with no reason at all — caught separately so the failure names the real
# problem instead of reporting the whole line as missing.
WAIVER_NO_REASON = re.compile(
    r"^[ \t>*-]*Spec-rite:[ \t]*none[ \t]*(?:(?:—|--|–|-)[ \t]*)?$",
    re.IGNORECASE | re.MULTILINE,
)
MIN_REASON = 8

# The line that names the change a pull request belongs to — the form execute-backlog writes into
# the body (skills/execute-backlog/references/spec-rite.md). Same treatment as the waiver: anchored
# to the start of a line, matched as text, never executed. `none` is the waiver, not a change id,
# and is filtered out after the match rather than excluded in the pattern so the two regexes stay
# readable side by side.
NAMED_CHANGE = re.compile(
    r"^[ \t>*-]*Spec-rite:[ \t]*(?P<id>[A-Za-z0-9][A-Za-z0-9._-]*)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)

findings: list[str] = []

# GitHub turns `::error` into a red annotation on the pull request. During --selftest the findings
# are injected on purpose, so annotating them would put bogus failures on a PR whose job passed —
# the same defect the sibling evidence gate hit on run 31790712710.
annotate = True


def add(check: str, detail: str) -> None:
    findings.append(f"{check}: {detail}")
    if annotate:
        print(f"::error::{check} — {detail}")
    else:
        print(f"    injected: {check} — {detail}")


# ── inputs ────────────────────────────────────────────────────────────────
def active_changes(root: Path) -> list[str]:
    base = root / CHANGES
    if not base.is_dir():
        return []
    return sorted(
        d.name for d in base.iterdir()
        if d.is_dir() and d.name != "archive" and (d / "tasks.md").is_file()
    )


def resolve_base(root: Path) -> str | None:
    """The revision this branch is measured against, or None when there is nothing to compare to."""
    candidates = []
    for env in ("SPEC_RITE_BASE", "GITHUB_BASE_REF"):
        ref = os.environ.get(env, "").strip()
        if ref:
            candidates += [f"origin/{ref}", ref]
    candidates += ["origin/master", "origin/main"]
    for ref in candidates:
        probe = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"],
                               capture_output=True, text=True)
        if probe.returncode == 0:
            return ref
    return None


def read_pr_body() -> str:
    """The pull request body, without routing it through anything that echoes it.

    Precedence, and the reason for it:
      1. PR_BODY, when set — the only reason to set it explicitly is to want that exact value
         (local runs, and the end-to-end probes of this gate).
      2. pull_request.body from the file at GITHUB_EVENT_PATH — the payload the runner wrote for
         itself. Nothing hands it over, so nothing prints it.
      3. empty.

    A payload that is missing, unreadable or without the key degrades to an empty body rather than
    an error: the decision then falls to the rules that already exist, instead of the build failing
    for a reason unrelated to the rite.
    """
    override = os.environ.get("PR_BODY")
    if override is not None:
        return override

    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path:
        return ""
    try:
        with open(event_path, encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"  spec-rite gate: event payload unreadable ({exc.__class__.__name__}) — "
              "continuing with an empty body")
        return ""
    body = (payload.get("pull_request") or {}).get("body")
    return body if isinstance(body, str) else ""


def split_nul_paths(out: str) -> list[str]:
    """`git diff --name-only -z` output -> paths, verbatim. NUL is the one byte a path cannot contain,
    so nothing here is quoted, escaped or split on a newline inside a name.

    Duplicated from validate-skill-version.py rather than imported: that script loads THIS one at
    import time (for MIN_REASON), so importing back would close a cycle, and a third module for two
    lines is more surface than the duplicate. Each script pins its own copy with a real-repository
    probe in --selftest, which is what keeps the two from drifting apart."""
    return [p for p in out.split("\0") if p]


def changed_paths(root: Path, base: str, head: str = "HEAD") -> list[str]:
    # -z: raw names separated by NUL. The default line mode quotes and octal-escapes any name with a
    # non-ASCII, control or quote character, which the prefix rules below would then fail to match.
    out = subprocess.run(["git", "-C", str(root), "diff", "--name-only", "-z", f"{base}...{head}"],
                         capture_output=True, text=True, check=True).stdout
    return split_nul_paths(out)


# ── rules ─────────────────────────────────────────────────────────────────
def requires_registration(paths: list[str]) -> list[str]:
    return [p for p in paths if not p.startswith(EXEMPT_PREFIX) and p not in EXEMPT_PATHS]


def archived_in_diff(paths: list[str]) -> bool:
    return any(p.startswith(f"{CHANGES}/archive/") for p in paths)


def waiver_reason(pr_body: str) -> str | None:
    m = WAIVER.search(pr_body or "")
    return m.group("reason").strip() if m else None


def named_changes(pr_body: str) -> list[str]:
    """Every change id the body names on a `Spec-rite: <id>` line, in order; the waiver is not one."""
    return [m.group("id") for m in NAMED_CHANGE.finditer(pr_body or "")
            if m.group("id").lower() != "none"]


def touched_changes(paths: list[str], changes: list[str]) -> list[str]:
    """The active changes whose own directory this diff touches — a tick in tasks.md counts."""
    return sorted(c for c in changes if any(p.startswith(f"{CHANGES}/{c}/") for p in paths))


def evaluate(paths: list[str], changes: list[str], pr_body: str) -> None:
    """The whole decision, as a pure function of its inputs — this is what --selftest exercises."""
    offenders = requires_registration(paths)
    if not offenders:
        return
    if archived_in_diff(paths):
        return

    # Relevance, not existence (S3): the diff is registered by the change it touches or names.
    named = named_changes(pr_body)
    if touched_changes(paths, changes) or any(n in changes for n in named):
        return

    reason = waiver_reason(pr_body)
    if reason is not None:
        if len(reason) < MIN_REASON:
            add("S2 waiver reason", f"the waiver names no usable reason ({reason!r}) — "
                                    "write `Spec-rite: none — <why this change registers nothing>`")
        return

    if WAIVER_NO_REASON.search(pr_body or ""):
        add("S2 waiver reason", "the pull request body carries `Spec-rite: none` with no reason — "
                                "write `Spec-rite: none — <why this change registers nothing>`")
        return

    sample = ", ".join(offenders[:5]) + (f" (+{len(offenders) - 5} more)" if len(offenders) > 5 else "")
    if changes:
        stale = [n for n in named if n not in changes]
        stale_note = (f"; the body names {', '.join(stale)}, which is not an active change"
                      if stale else "")
        add("S3 unrelated change",
            f"this diff touches {len(offenders)} path(s) outside {EXEMPT_PREFIX} — {sample} — and "
            f"{len(changes)} active change(s) exist ({', '.join(changes)}), but the diff touches none "
            f"of their directories and the pull request body names none of them{stale_note}. "
            f"Link the diff to its change: touch {CHANGES}/<id>/ (a tick in tasks.md counts) or add "
            "a line `Spec-rite: <id>` to the pull request body — or waive it with "
            "`Spec-rite: none — <reason>`")
        return

    add("S1 unregistered change",
        f"this diff touches {len(offenders)} path(s) outside {EXEMPT_PREFIX} — {sample} — with no "
        f"active change under {CHANGES}/, no change archived in the same diff, and no waiver. "
        "Open a change (`openspec new change <id> --schema skills-rite`) or add a line "
        "`Spec-rite: none — <reason>` to the pull request body")


# ── selftest ──────────────────────────────────────────────────────────────
# One injected defect per rule, plus the false-positive cases the rules must stay silent on.
DEFECTS = [
    ("S1 unregistered change", (["skills/backlog/SKILL.md"], [], "")),
    ("S2 waiver reason", (["skills/backlog/SKILL.md"], [], "Spec-rite: none — x")),
    ("S2 waiver reason", (["skills/backlog/SKILL.md"], [], "Spec-rite: none")),
    # Until issue #117 this exact input was SILENT[2] "active change present": any active change
    # registered any diff. It is the defect the relevance rule exists to catch.
    ("S3 unrelated change", (["skills/backlog/SKILL.md"], ["add-spec-rite-gate"], "")),
    ("S3 unrelated change", (["skills/backlog/SKILL.md"], ["add-spec-rite-gate"],
                             "Spec-rite: some-archived-change")),
    ("S3 unrelated change", (["skills/backlog/SKILL.md"], ["add-spec-rite-gate"],
                             "see the Spec-rite: add-spec-rite-gate line elsewhere")),
]

SILENT = [
    ("diff confined to openspec/", (["openspec/changes/x/tasks.md"], [], "")),
    ("release automation only", (["VERSION", "CHANGELOG.md", ".claude-plugin/plugin.json"], [], "")),
    ("active change touched in the diff",
     (["skills/backlog/SKILL.md", f"{CHANGES}/add-spec-rite-gate/tasks.md"], ["add-spec-rite-gate"], "")),
    ("active change named in the body",
     (["skills/backlog/SKILL.md"], ["add-spec-rite-gate", "other-change"], "Spec-rite: add-spec-rite-gate")),
    ("active change named in a list item",
     (["README.md"], ["add-spec-rite-gate"], "- Spec-rite: add-spec-rite-gate")),
    ("archived in the same diff", ([f"{CHANGES}/archive/2026-01-01-x/tasks.md", "README.md"], [], "")),
    ("archived with an unrelated active change",
     ([f"{CHANGES}/archive/2026-01-01-x/tasks.md", "README.md"], ["other-change"], "")),
    ("waiver with a reason", (["skills/backlog/SKILL.md"], [], "Spec-rite: none — typo no README")),
    ("waiver with a reason beside an unrelated active change",
     (["skills/backlog/SKILL.md"], ["other-change"], "Spec-rite: none — typo no README")),
    ("waiver quoted in a list item", (["README.md"], [], "- Spec-rite: none — correcao de link quebrado")),
]


@contextlib.contextmanager
def _env(**pairs):
    """Set/unset env vars for one case and put the process back the way it was."""
    saved = {k: os.environ.get(k) for k in pairs}
    try:
        for k, v in pairs.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def selftest_reader() -> int:
    """The reader is the surface this change adds, so it gets cases of its own.

    Exercised against files written here rather than a real event: what a real payload proves that
    this cannot is whether the key is present at all, and that is what the CI run of the pull
    request answers. The fallbacks below are what make that answer non-fatal either way.
    """
    ok = 0
    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "event.json"
        good.write_text(json.dumps({"pull_request": {"body": "Spec-rite: none — from payload"}}))
        broken = Path(td) / "broken.json"
        broken.write_text("{not json")
        keyless = Path(td) / "keyless.json"
        keyless.write_text(json.dumps({"issue": {"body": "wrong event"}}))
        missing = Path(td) / "does-not-exist.json"

        cases = [
            ("payload body is read", {"PR_BODY": None, "GITHUB_EVENT_PATH": str(good)},
             "Spec-rite: none — from payload"),
            ("PR_BODY overrides the payload", {"PR_BODY": "override wins", "GITHUB_EVENT_PATH": str(good)},
             "override wins"),
            ("missing payload file degrades to empty", {"PR_BODY": None, "GITHUB_EVENT_PATH": str(missing)}, ""),
            ("malformed payload degrades to empty", {"PR_BODY": None, "GITHUB_EVENT_PATH": str(broken)}, ""),
            ("payload without the key degrades to empty", {"PR_BODY": None, "GITHUB_EVENT_PATH": str(keyless)}, ""),
            ("no payload path at all degrades to empty", {"PR_BODY": None, "GITHUB_EVENT_PATH": None}, ""),
        ]
        for label, env, expected in cases:
            with _env(**env):
                got = read_pr_body()
            if got == expected:
                print(f"  READER  {label}")
                ok += 1
            else:
                print(f"  READER FAIL  {label}   <-- got {got!r}, expected {expected!r}")
    return ok


def _probe_quoted_path() -> bool:
    """The one git-plumbing probe of the selftest: commit a path git would quote in line mode INSIDE
    an active change and check that the diff registers. core.quotePath is forced on so the probe
    measures the worst case whatever the box's config says. Same shape as the probe in
    validate-skill-version.py; what it asserts differs — there the skill is recognised, here the
    change is."""
    global findings
    change = "probe-quoted"
    quoted = f"{CHANGES}/{change}/specs/café.md"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@localhost",
               "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@localhost"}

        def git(*args: str) -> None:
            subprocess.run(["git", "-C", tmp, "-c", "core.quotePath=true", *args],
                           capture_output=True, text=True, check=True, env=env)

        git("init", "-q", "-b", "main")
        (root / CHANGES / change).mkdir(parents=True)
        (root / CHANGES / change / "tasks.md").write_text("- [ ] E.1 x\n", encoding="utf-8")
        (root / "skills/x").mkdir(parents=True)
        (root / "skills/x/SKILL.md").write_text("---\n  version: 1.0.0\n---\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        (root / CHANGES / change / "specs").mkdir()
        (root / quoted).write_text("delta\n", encoding="utf-8")
        (root / "skills/x/SKILL.md").write_text("---\n  version: 1.0.1\n---\nedit\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "edit")

        paths = changed_paths(root, "HEAD^")
        findings = []
        evaluate(paths, active_changes(root), "")
        return paths == [quoted, "skills/x/SKILL.md"] and findings == []


def selftest_paths() -> tuple[int, int]:
    """The reader collect-side: what the rules never see. A `-z` dropped from changed_paths() makes
    the quoted path an offender and the change untouched at once, and no synthetic case can show it."""
    cases = [
        ("NUL-separated names are read verbatim, quotes and newlines included",
         split_nul_paths(f'{CHANGES}/x/tasks.md\0skills/y/references/café "x"\n.md\0')
         == [f"{CHANGES}/x/tasks.md", 'skills/y/references/café "x"\n.md']),
        ("a quoted path inside an active change registers the diff on a real repository",
         _probe_quoted_path()),
    ]
    ok = 0
    for label, passed in cases:
        print(f"  {'PATHS' if passed else 'PATHS FAIL'}  {label}")
        ok += bool(passed)
    return ok, len(cases)


def selftest() -> int:
    global findings, annotate
    annotate = False
    caught = 0
    for label, (paths, changes, body) in DEFECTS:
        findings = []
        evaluate(paths, changes, body)
        if any(f.startswith(label) for f in findings):
            print(f"  CAUGHT  {label}: {body!r}")
            caught += 1
        else:
            print(f"  MISSED  {label}: {body!r}   <-- the rule cannot fire")

    quiet = 0
    for label, (paths, changes, body) in SILENT:
        findings = []
        evaluate(paths, changes, body)
        if findings:
            print(f"  FALSE POSITIVE  {label}   <-- {findings[0]}")
        else:
            print(f"  SILENT  {label}")
            quiet += 1

    reader_ok = selftest_reader()
    reader_total = 6
    paths_ok, paths_total = selftest_paths()

    print(f"\n{caught}/{len(DEFECTS)} defect classes detected, "
          f"{quiet}/{len(SILENT)} false-positive cases stayed silent, "
          f"{reader_ok}/{reader_total} reader cases correct, "
          f"{paths_ok}/{paths_total} path-reader cases correct")
    return 0 if (caught == len(DEFECTS) and quiet == len(SILENT)
                 and reader_ok == reader_total and paths_ok == paths_total) else 1


# ── main ──────────────────────────────────────────────────────────────────
def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()

    event = os.environ.get("GITHUB_EVENT_NAME", "")
    in_ci = os.environ.get("GITHUB_ACTIONS", "") == "true"
    if in_ci and event and event != "pull_request":
        print(f"  spec-rite gate: skipped (event {event}, not pull_request)")
        return 0

    base = resolve_base(ROOT)
    if base is None:
        # A gate that cannot measure must not approve. In CI an unresolvable base means the checkout
        # was not given enough history (fetch-depth), which is a misconfiguration, not an exemption.
        if in_ci:
            add("S0 base revision", "no base revision to diff against — the checkout needs "
                                    "`fetch-depth: 0` for this gate to measure anything")
            return 1
        print("  spec-rite gate: skipped (no base revision to diff against)")
        return 0

    paths = changed_paths(ROOT, base)
    evaluate(paths, active_changes(ROOT), read_pr_body())
    print(f"  spec-rite gate: {len(findings)} findings "
          f"(base {base}, {len(paths)} changed path(s), "
          f"{len(active_changes(ROOT))} active change(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
