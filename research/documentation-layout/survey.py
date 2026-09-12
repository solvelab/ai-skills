#!/usr/bin/env python3
"""Survey the documentation layout of a fleet of repositories, and re-produce the numbers in
`results.md`.

Two passes, both read-only:

  1. **Inventory** — what the repositories actually call their documents, and how many carry two
     names for one concept. This is the measurement that motivated the document map, and it needs
     no checker: it counts file names.
  2. **Detector** — `skills/documentation/references/check-doc-layout.py` over each repository,
     aggregated per rule. This is the measurement that decides whether a rule ships as a gate.

    survey.py --root DIR                 both passes over every git repository under DIR
    survey.py --root DIR --inventory     the first pass only (fast; no checker involved)
    survey.py --root DIR --repositories a,b,c   restrict to these repository names
    survey.py --root DIR --markdown      emit the tables as Markdown, ready for results.md
    survey.py --selftest                 prove every counter on a synthetic tree

Exit codes: 0 when the survey ran, 2 on a usage error. The survey never fails on findings — it is a
measurement, not a gate.

KNOWN LIMIT:

  A repository is a directory holding `.git`, found at depth <= 3 under --root. A deeper monorepo
     package is not counted as its own repository, and its documents are attributed to the
     repository above it.
  Only `.md` at depth <= 2 inside each repository is inventoried: the root and one level under it,
     which is where every tier document of the map lives. A document buried deeper is invisible to
     pass 1 and visible to pass 2, which walks the whole tree.
  The false-positive column of pass 2 is NOT computed here. Confirming a finding is reading it
     against the repository, one at a time, by hand — `results.md` records who did that and when.
"""

from __future__ import annotations

import argparse
import collections
import os
import re
import subprocess
import sys
from pathlib import Path

CHECKER = (Path(__file__).resolve().parents[2]
           / "skills" / "documentation" / "references" / "check-doc-layout.py")

SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", "dist", "build",
        "vendor", ".tox", "openspec", ".claude", ".cursor", ".next"}

#: The concepts the map names, and every spelling the fleet was found to use for each.
CONCEPTS = {
    "entry": ("README.md",),
    "requirements": ("REQUIREMENTS.md", "REQUISITOS.md", "SRS.md"),
    "tutorial": ("SETUP.md", "INSTALL.md", "COMO-SUBIR.md", "GETTING-STARTED.md"),
    "explanation": ("ARCHITECTURE.md", "TECHNICAL.md", "DESIGN.md"),
    "api": ("API.md", "API-CONTRACT.md", "ENDPOINTS.md"),
    "operation": ("OPERATIONS.md", "DEPLOYMENT.md", "DEPLOY.md", "INFRASTRUCTURE.md",
                  "RUNBOOK.md", "DEPLOYMENT_GUIDE.md"),
    "security": ("SECURITY.md",),
    "history": ("CHANGELOG.md",),
    "agents": ("AGENTS.md", "CLAUDE.md"),
}

TRANSIENT = re.compile(
    r"homolog|diagnose|diagnostic|validation-report|progress|todo|correcao|teste[-_]agora|"
    r"roteiro|continuar|revalidacao|postmortem|post-mortem|\d{4}-\d{2}-\d{2}", re.I)

RULE = re.compile(r"\[(L[1-7])\]")


def repositories(root: Path, only: list[str]) -> list[Path]:
    found = []
    for git in sorted(root.glob("*/.git")) + sorted(root.glob("*/*/.git")) + \
            sorted(root.glob("*/*/*/.git")):
        repo = git.parent
        if only and repo.name not in only:
            continue
        if repo not in found:
            found.append(repo)
    return found


def walk(repo: Path, depth: int) -> list[Path]:
    """Every `.md` at most `depth` path segments deep, pruning skipped directories as it goes.

    Pruning matters more than it looks: collecting first and filtering afterwards walked every
    `node_modules` in the fleet, which on a Windows or network mount took longer than the rest of
    the survey put together. `os.walk` lets a skipped directory be dropped before it is entered.
    """
    out = []
    for current, directories, files in os.walk(repo):
        here = Path(current)
        rel_parts = here.relative_to(repo).parts
        directories[:] = [d for d in directories if d not in SKIP]
        if len(rel_parts) + 1 >= depth:
            directories[:] = []
        for name in files:
            if name.endswith(".md"):
                out.append(here / name)
    return out


def documents(repo: Path, depth: int = 2) -> list[Path]:
    return walk(repo, depth)


def inventory(targets: list[Path]) -> dict:
    names: collections.Counter = collections.Counter()
    per_concept: dict[str, collections.Counter] = {c: collections.Counter() for c in CONCEPTS}
    collisions: list[tuple[str, list[str]]] = []
    transient: list[str] = []
    with_openspec = 0

    for repo in targets:
        if (repo / "openspec").is_dir():
            with_openspec += 1
        seen_explanation = []
        for p in documents(repo):
            names[p.name] += 1
            for concept, spellings in CONCEPTS.items():
                # Compare folded on BOTH sides: `.upper()` on the whole name turned `TECHNICAL.md`
                # into `TECHNICAL.MD`, which matched nothing and reported a clean fleet.
                if p.name.lower() in {s.lower() for s in spellings}:
                    per_concept[concept][p.name] += 1
                    if concept == "explanation":
                        seen_explanation.append(str(p.relative_to(repo)))
        for p in walk(repo, 3):
            rel = p.relative_to(repo)
            if TRANSIENT.search(p.stem) and not str(rel).replace("\\", "/").startswith("docs/reports/"):
                transient.append("%s/%s" % (repo.name, rel))
        if len(seen_explanation) >= 2:
            collisions.append((repo.name, seen_explanation))

    return {
        "repositories": len(targets),
        "with_openspec": with_openspec,
        "names": names,
        "per_concept": per_concept,
        "collisions": collisions,
        "transient": transient,
    }


def detector(targets: list[Path]) -> dict:
    if not CHECKER.is_file():
        raise SystemExit("error: checker not found at %s" % CHECKER)
    per_rule: collections.Counter = collections.Counter()
    per_repo: dict[str, collections.Counter] = {}
    for repo in targets:
        proc = subprocess.run([sys.executable, str(CHECKER), str(repo)],
                              capture_output=True, text=True)
        counts: collections.Counter = collections.Counter()
        for line in proc.stdout.splitlines():
            m = RULE.search(line)
            if m:
                counts[m.group(1)] += 1
                per_rule[m.group(1)] += 1
        per_repo[repo.name] = counts
    return {"per_rule": per_rule, "per_repo": per_repo}


def render(inv: dict, det: dict | None, markdown: bool) -> str:
    bar = "| " if markdown else "  "
    lines = []
    lines.append("repositories: %d (with a spec-driven workflow: %d)"
                 % (inv["repositories"], inv["with_openspec"]))
    lines.append("")
    lines.append("## Names per concept" if markdown else "Names per concept")
    lines.append("")
    if markdown:
        lines.append("| Concept | Spellings found |")
        lines.append("|---|---|")
    for concept, counter in inv["per_concept"].items():
        if not counter:
            continue
        spellings = " · ".join("`%s` %d" % (n, c) for n, c in counter.most_common())
        lines.append("%s%s %s %s" % (bar, concept, "|" if markdown else "->",
                                     spellings + (" |" if markdown else "")))
    lines.append("")
    lines.append("repositories carrying two names for the explanation slot: %d"
                 % len(inv["collisions"]))
    for name, paths in inv["collisions"]:
        lines.append("  %s: %s" % (name, ", ".join(paths)))
    lines.append("")
    lines.append("transient records outside docs/reports/: %d" % len(inv["transient"]))
    for path in inv["transient"][:25]:
        lines.append("  %s" % path)

    if det:
        lines.append("")
        lines.append("## Detector findings per rule" if markdown else "Detector findings per rule")
        lines.append("")
        if markdown:
            lines.append("| Rule | Findings |")
            lines.append("|---|---|")
        total = 0
        for rule in sorted(det["per_rule"]):
            total += det["per_rule"][rule]
            lines.append("%s%s %s %d %s" % (bar, rule, "|" if markdown else "->",
                                            det["per_rule"][rule], "|" if markdown else ""))
        lines.append("%s**Total** %s %d %s" % (bar, "|" if markdown else "->", total,
                                               "|" if markdown else ""))
    return "\n".join(lines)


# ── Self-test ─────────────────────────────────────────────────────────────────


def selftest() -> int:
    import tempfile

    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # one repository with two names for the explanation slot and one transient record
        a = root / "alpha"
        (a / ".git").mkdir(parents=True)
        (a / "docs").mkdir()
        (a / "README.md").write_text("# a\n", encoding="utf-8")
        (a / "ARCHITECTURE.md").write_text("# a\n", encoding="utf-8")
        (a / "docs" / "TECHNICAL.md").write_text("# a\n", encoding="utf-8")
        (a / "DIAGNOSE-2026-01-01.md").write_text("# a\n", encoding="utf-8")
        # one clean repository
        b = root / "beta"
        (b / ".git").mkdir(parents=True)
        (b / "README.md").write_text("# b\n", encoding="utf-8")

        targets = repositories(root, [])
        if len(targets) != 2:
            failures.append("found %d repositories, expected 2" % len(targets))

        inv = inventory(targets)
        if inv["per_concept"]["explanation"].get("TECHNICAL.md") != 1:
            failures.append("TECHNICAL.md not counted under the explanation concept")
        if len(inv["collisions"]) != 1:
            failures.append("collision of two explanation names not detected")
        if len(inv["transient"]) != 1:
            failures.append("transient record not detected")
        if inv["names"].get("README.md") != 2:
            failures.append("README.md counted %s times, expected 2" % inv["names"].get("README.md"))

        # a node_modules copy must not be counted
        vendored = b / "node_modules" / "pkg"
        vendored.mkdir(parents=True)
        (vendored / "README.md").write_text("# vendored\n", encoding="utf-8")
        if inventory(repositories(root, []))["names"].get("README.md") != 2:
            failures.append("a vendored README was counted")

    for line in failures:
        print("selftest: %s" % line, file=sys.stderr)
    print("selftest: %d check(s) failed" % len(failures))
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="directory holding the repositories")
    ap.add_argument("--repositories", help="comma-separated repository names to restrict to")
    ap.add_argument("--inventory", action="store_true", help="skip the detector pass")
    ap.add_argument("--markdown", action="store_true", help="emit Markdown tables")
    ap.add_argument("--selftest", action="store_true", help="prove every counter")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.root:
        ap.error("no --root given; pass a directory, or use --selftest")

    root = Path(args.root)
    if not root.is_dir():
        print("survey: not a directory: %s" % args.root, file=sys.stderr)
        return 2

    only = [r.strip() for r in args.repositories.split(",")] if args.repositories else []
    targets = repositories(root, only)
    if not targets:
        print("survey: no git repository found under %s" % root, file=sys.stderr)
        return 2

    inv = inventory(targets)
    det = None if args.inventory else detector(targets)
    print(render(inv, det, args.markdown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
