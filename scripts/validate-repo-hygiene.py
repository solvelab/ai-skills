#!/usr/bin/env python3
"""Whole-repository hygiene gate.

The sibling gates each look at one slice: validate-skills.py walks skills/, scan-secrets.py hunts
credentials, validate-rite.sh reads OpenSpec changes, and CI's wrapper-sync step diffs generated
trees. Nothing looked at the repository as a whole, which is how each of these got in:

  H1 no tracked compiled artifacts   (a .pyc reached release 2.6.0; see #70)
  H2 published skill counts are true (README and marketplace drifted to 27/30 against 32; see #65)
  H3 plugin descriptions match the tree (game said "10 topics" over 12 skills, workflow named 5 of
                                         7, and H2 only ever matched `all N`; see #114)

Exit 1 on any finding. Run from the repo root.
Modes: (default) check the tree   |   --selftest inject one defect per check and assert detection.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mirrors the bytecode rules in .gitignore. Kept in sync by hand on purpose: widening this to every
# conceivable binary would be guesswork about artifacts this repo has never produced.
BYTECODE = re.compile(r"(^|/)__pycache__/|\.py[cod]$")

# Files that publish a skill count, and the shape they publish it in.
COUNT_FILES = ("README.md", ".claude-plugin/marketplace.json", ".claude-plugin/plugin.json")
COUNT_CLAIM = re.compile(r"\ball (\d+)\b")
# A parenthetical count that names no members — `(10 topics)`, `(12 skills)`, and the README
# heading shape `(React Three Fiber — 10 topics)`: a number and its noun right before the closing
# parenthesis. It says nothing about which set it counts, so it cannot be checked against the tree;
# the shape itself is the finding. `(all 35 skills)` is exempt here because COUNT_CLAIM owns it.
UNSCOPED_COUNT_CLAIM = re.compile(r"(?<!all )\b(\d+) (?:topics|skills)\)")

# The shape generate.sh publishes for every plugin group: "<theme> (<N> skill(s): a, b, c)".
MEMBERSHIP_CLAIM = re.compile(r"\((\d+) skills?: ([^)]*)\)")
MARKETPLACE = ".claude-plugin/marketplace.json"
PLUGIN_SOURCE_PREFIX = "./plugins/"

findings: list[str] = []


def add(check: str, detail: str) -> None:
    findings.append(f"{check}: {detail}")


def tracked_files(root: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files"],
                         capture_output=True, text=True, check=True).stdout
    return out.splitlines()


def skill_count(root: Path) -> int:
    return len([p for p in (root / "skills").iterdir() if p.is_dir()])


def check_no_bytecode(root: Path) -> None:
    """H1 — no compiled Python artifact is tracked.

    KNOWN LIMIT: covers the bytecode classes .gitignore names (__pycache__/, *.py[cod]) and nothing
    else — a tracked .so, .class or minified bundle passes. Discovery is `git ls-files`, so an
    ignored-but-present __pycache__ on a developer's machine is correctly not a finding, and a file
    forced in with `git add -f` correctly is. It cannot see a blob already published in a past
    release; removing that needs a history rewrite, which is a separate decision.
    """
    for f in tracked_files(root):
        if BYTECODE.search(f):
            add("H1 tracked bytecode", f"{f} is tracked — untrack it (`git rm --cached`)")


def check_counts(root: Path) -> None:
    """H2 — every published skill count equals the number of directories under skills/, and no
    published file carries a parenthetical count that names no members.

    Two shapes. `all N` is compared with the tree. `(N topics)` / `(N skills)` with no `: names`
    after the noun is refused by shape alone: the text does not say which set it counts, so neither
    the catalog total nor any group is the right number to compare it with. The verifiable forms
    are `all N` (total, this check) and `(N skills: a, b)` (a group, H3).

    KNOWN LIMIT: both patterns run over exactly the files in COUNT_FILES (README.md, the marketplace
    and the root plugin manifest) plus, for the bare shape, every plugins/*/.claude-plugin/plugin.json.
    A count phrased another way — "the 33 skills", "33 skills available", a count in a fourth file —
    escapes this check and is review-only. That blind spot is real and was earned: the sweep that
    first hunted these counts used a pattern requiring the word "skills" after the number and missed
    `all 30.` in README.md, which has no noun after it. In README.md the bare shape is not read
    inside fenced code blocks: README.md:345 carries `(10 topics)` as a comment on `r3f-*` in an
    illustrative directory tree, true today and unverifiable by name — a diagram comment is not the
    same class of claim as a heading or a manifest, and it stays review-only.
    """
    real = skill_count(root)
    group_manifests = sorted(str(p.relative_to(root))
                             for p in (root / "plugins").glob("*/.claude-plugin/plugin.json"))
    for rel in list(COUNT_FILES) + group_manifests:
        p = root / rel
        if not p.exists():
            add("H2 missing file", f"{rel} does not exist — update COUNT_FILES")
            continue
        in_fence = False
        for line_no, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if rel.endswith(".md") and line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if rel in COUNT_FILES:
                for m in COUNT_CLAIM.finditer(line):
                    claimed = int(m.group(1))
                    if claimed != real:
                        add("H2 stale count",
                            f"{rel}:{line_no} claims {claimed}, `ls skills | wc -l` says {real}")
            if in_fence:
                continue
            for m in UNSCOPED_COUNT_CLAIM.finditer(line):
                add("H2 unscoped count",
                    f"{rel}:{line_no} publishes `{m.group(0)}` with no member list — nothing in the "
                    "tree can confirm it; write `all N` (catalog total) or `(N skills: <names>)` "
                    "(group membership, checked by H3)")


def plugin_groups(root: Path) -> dict[str, set[str]]:
    base = root / "plugins"
    if not base.is_dir():
        return {}
    return {g.name: {s.name for s in (g / "skills").iterdir() if s.is_dir()}
            for g in sorted(base.iterdir()) if (g / "skills").is_dir()}


def _membership_finding(rel: str, group: str, description: str, expected: set[str]) -> None:
    m = MEMBERSHIP_CLAIM.search(description)
    if not m:
        add("H3 plugin description membership",
            f"{rel} ({group}) publishes no `(N skills: <names>)` list — without one the tree "
            "cannot confirm what the plugin ships; regenerate with ./generate.sh")
        return
    claimed_count = int(m.group(1))
    names = {n.strip() for n in m.group(2).split(",") if n.strip()}
    extra, missing = sorted(names - expected), sorted(expected - names)
    if extra or missing:
        add("H3 plugin description membership",
            f"{rel} ({group}) names {len(names)} skills but plugins/{group}/skills/ has "
            f"{len(expected)} — in excess: {extra or 'none'}; missing: {missing or 'none'}; "
            "regenerate with ./generate.sh")
    if claimed_count != len(names):
        add("H3 plugin description membership",
            f"{rel} ({group}) says {claimed_count} skills but lists {len(names)} names; "
            "regenerate with ./generate.sh")


def check_plugin_membership(root: Path) -> None:
    """H3 — every published plugin description names exactly the skills under its tree.

    For each plugins/<g>/skills/ the set of directories is the truth. plugins/<g>/.claude-plugin/
    plugin.json and the marketplace entry whose `source` is ./plugins/<g> must both carry a
    `(N skills: a, b, c)` parenthetical whose names equal that set and whose N equals the number
    of names. A finding names the file, the group, the names in excess and the names missing.

    KNOWN LIMIT: the theme — the text before the parenthetical — is not read at all. A theme that
    says "Kubernetes" over a group of FiveM skills passes; only a human review catches a wrong
    theme. The parenthetical is recognised by one shape (MEMBERSHIP_CLAIM), so a generator that
    changes the format silences this check until the regex follows — the selftest is what makes
    that visible. README.md prose that names skills per plugin (the plugin table near the top) is
    not compared with the tree here and is review-only; H2 covers only its counts.
    """
    groups = plugin_groups(root)
    for group, expected in groups.items():
        rel = f"plugins/{group}/.claude-plugin/plugin.json"
        p = root / rel
        if not p.is_file():
            add("H3 plugin description membership", f"{rel} is missing — regenerate with ./generate.sh")
            continue
        _membership_finding(rel, group, json.loads(p.read_text(encoding="utf-8")).get("description", ""),
                            expected)

    mp = root / MARKETPLACE
    if not mp.is_file():
        add("H3 plugin description membership", f"{MARKETPLACE} does not exist")
        return
    seen: set[str] = set()
    for entry in json.loads(mp.read_text(encoding="utf-8")).get("plugins", []):
        source = entry.get("source", "")
        if not source.startswith(PLUGIN_SOURCE_PREFIX):
            continue
        group = source[len(PLUGIN_SOURCE_PREFIX):].strip("/")
        if group not in groups:
            add("H3 plugin description membership",
                f"{MARKETPLACE} entry `{entry.get('name')}` points at {source}, which has no "
                "plugins/<group>/skills/ in the tree")
            continue
        seen.add(group)
        _membership_finding(f"{MARKETPLACE} entry `{entry.get('name')}`", group,
                            entry.get("description", ""), groups[group])
    for group in sorted(set(groups) - seen):
        add("H3 plugin description membership",
            f"{MARKETPLACE} has no entry with source {PLUGIN_SOURCE_PREFIX}{group} — the group "
            "exists in the tree but is not published")


CHECKS = (check_no_bytecode, check_counts, check_plugin_membership)


# ── selftest ──────────────────────────────────────────────────────────────
# A checker that never fails is not a checker. One injected defect per check, asserted detected.

def _defect_bytecode(tmp: Path) -> None:
    d = tmp / "claude" / "global" / "hooks" / "__pycache__"
    d.mkdir(parents=True, exist_ok=True)
    (d / "injected.cpython-314.pyc").write_bytes(b"\x00")
    subprocess.run(["git", "-C", str(tmp), "add", "-f",
                    "claude/global/hooks/__pycache__/injected.cpython-314.pyc"],
                   check=True, capture_output=True)


def _defect_count(tmp: Path) -> None:
    p = tmp / "README.md"
    text = p.read_text(encoding="utf-8")
    real = skill_count(tmp)
    p.write_text(text.replace(f"all {real}", f"all {real + 7}", 1), encoding="utf-8")


def _defect_unscoped_count(tmp: Path) -> None:
    # A heading outside any fence, the exact shape README.md:537 carried until #114.
    p = tmp / "README.md"
    text = p.read_text(encoding="utf-8")
    assert "\n### Frontend\n" in text, "README.md no longer has the '### Frontend' heading"
    p.write_text(text.replace("\n### Frontend\n", "\n### Frontend (2 topics)\n", 1), encoding="utf-8")


def _defect_membership(tmp: Path) -> None:
    # One name swapped in the group manifest: H3 must report both the excess and the missing one.
    p = tmp / "plugins" / "game" / ".claude-plugin" / "plugin.json"
    text = p.read_text(encoding="utf-8")
    assert "r3f-shaders" in text, "plugins/game manifest no longer lists r3f-shaders"
    p.write_text(text.replace("r3f-shaders", "r3f-shadows", 1), encoding="utf-8")


DEFECTS = (("H1 tracked bytecode", _defect_bytecode),
           ("H2 stale count", _defect_count),
           ("H2 unscoped count", _defect_unscoped_count),
           ("H3 plugin description membership", _defect_membership))


def selftest() -> int:
    global findings
    caught = 0
    for label, inject in DEFECTS:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "repo"
            shutil.copytree(ROOT, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            subprocess.run(["git", "-C", str(tmp), "init", "-q"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(tmp), "add", "-A"], check=True, capture_output=True)
            inject(tmp)
            findings = []
            for check in CHECKS:
                check(tmp)
            if any(f.startswith(label) for f in findings):
                print(f"  CAUGHT  {label}")
                caught += 1
            else:
                print(f"  MISSED  {label}   <-- the check cannot fire")
    print(f"\n{caught}/{len(DEFECTS)} defect classes detected")
    return 0 if caught == len(DEFECTS) else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    for check in CHECKS:
        check(ROOT)
    for f in findings:
        print(f"  {f}")
    print(f"\nrepo hygiene: {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
