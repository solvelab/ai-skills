#!/usr/bin/env python3
"""Whole-repository hygiene gate.

The sibling gates each look at one slice: validate-skills.py walks skills/, scan-secrets.py hunts
credentials, validate-rite.sh reads OpenSpec changes, and CI's wrapper-sync step diffs generated
trees. Nothing looked at the repository as a whole, which is how both of these got in:

  H1 no tracked compiled artifacts   (a .pyc reached release 2.6.0; see #70)
  H2 published skill counts are true (README and marketplace drifted to 27/30 against 32; see #65)

Exit 1 on any finding. Run from the repo root.
Modes: (default) check the tree   |   --selftest inject one defect per check and assert detection.
"""
from __future__ import annotations

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
COUNT_FILES = ("README.md", ".claude-plugin/marketplace.json")
COUNT_CLAIM = re.compile(r"\ball (\d+)\b")

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
    """H2 — every published skill count equals the number of directories under skills/.

    KNOWN LIMIT: matches the literal shape `all N` in exactly two files (README.md and
    .claude-plugin/marketplace.json). A count phrased another way — "the 33 skills", "33 skills
    available", a count in a third file — escapes this check and is review-only. That blind spot is
    real and was earned: the sweep that first hunted these counts used a pattern requiring the word
    "skills" after the number and missed `all 30.` in README.md, which has no noun after it.
    """
    real = skill_count(root)
    for rel in COUNT_FILES:
        p = root / rel
        if not p.exists():
            add("H2 missing file", f"{rel} does not exist — update COUNT_FILES")
            continue
        for line_no, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for m in COUNT_CLAIM.finditer(line):
                claimed = int(m.group(1))
                if claimed != real:
                    add("H2 stale count",
                        f"{rel}:{line_no} claims {claimed}, `ls skills | wc -l` says {real}")


CHECKS = (check_no_bytecode, check_counts)


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


DEFECTS = (("H1 tracked bytecode", _defect_bytecode),
           ("H2 stale count", _defect_count))


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
