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

KNOWN LIMIT: this proves that a change EXISTS, never that it is honest — a change scaffolded to
satisfy the gate passes it, exactly as a padded evidence box passes the shape gate. Existence is a
required, reviewable artifact; the review is what judges it. The selftest exercises the decision
rules against synthetic inputs, not the git plumbing that feeds them: a misconfigured checkout is
caught by the CI-only base-resolution failure below, not by the selftest.

Exit 1 on any finding. Run from the repo root.
Modes: (default) check this diff   |   --selftest inject one defect per rule and assert detection.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
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


def changed_paths(root: Path, base: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "diff", "--name-only", f"{base}...HEAD"],
                         capture_output=True, text=True, check=True).stdout
    return [line for line in out.splitlines() if line]


# ── rules ─────────────────────────────────────────────────────────────────
def requires_registration(paths: list[str]) -> list[str]:
    return [p for p in paths if not p.startswith(EXEMPT_PREFIX) and p not in EXEMPT_PATHS]


def archived_in_diff(paths: list[str]) -> bool:
    return any(p.startswith(f"{CHANGES}/archive/") for p in paths)


def waiver_reason(pr_body: str) -> str | None:
    m = WAIVER.search(pr_body or "")
    return m.group("reason").strip() if m else None


def evaluate(paths: list[str], changes: list[str], pr_body: str) -> None:
    """The whole decision, as a pure function of its inputs — this is what --selftest exercises."""
    offenders = requires_registration(paths)
    if not offenders:
        return
    if changes or archived_in_diff(paths):
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
]

SILENT = [
    ("diff confined to openspec/", (["openspec/changes/x/tasks.md"], [], "")),
    ("release automation only", (["VERSION", "CHANGELOG.md", ".claude-plugin/plugin.json"], [], "")),
    ("active change present", (["skills/backlog/SKILL.md"], ["add-spec-rite-gate"], "")),
    ("archived in the same diff", ([f"{CHANGES}/archive/2026-01-01-x/tasks.md", "README.md"], [], "")),
    ("waiver with a reason", (["skills/backlog/SKILL.md"], [], "Spec-rite: none — typo no README")),
    ("waiver quoted in a list item", (["README.md"], [], "- Spec-rite: none — correcao de link quebrado")),
]


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

    print(f"\n{caught}/{len(DEFECTS)} defect classes detected, "
          f"{quiet}/{len(SILENT)} false-positive cases stayed silent")
    return 0 if caught == len(DEFECTS) and quiet == len(SILENT) else 1


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
    evaluate(paths, active_changes(ROOT), os.environ.get("PR_BODY", ""))
    print(f"  spec-rite gate: {len(findings)} findings "
          f"(base {base}, {len(paths)} changed path(s), "
          f"{len(active_changes(ROOT))} active change(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
