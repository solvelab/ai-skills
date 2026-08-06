"""Scan the repository for credentials.

Two modes, deliberately different, because they answer different questions:

  (default)     scan the WORKING TREE. Gates CI: exits 1 on any credential class.
                This is the part that can be kept clean, so this is the part that gates.

  --history     scan every blob in the full git history. Reports only, never gates.
                A secret removed in a later commit is still published, so this is worth
                knowing — but it cannot be fixed by a later commit, and a gate that can
                never go green is a gate everyone learns to ignore.

Private (RFC1918) addresses are reported as operational detail, not as a credential class:
worth removing from a public repo, not a breach, and never a reason to fail a build.

Usage:  python3 scripts/scan-secrets.py [--history]
"""
from __future__ import annotations

import collections
import re
import subprocess
import sys
from pathlib import Path

PATTERNS = {
    "AWS access key":     re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token":       re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Slack token":        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "Google API key":     re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    "private key block":  re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "JWT":                re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
    "generic assigned secret": re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|token|access[_-]?key)\b\s*[:=]\s*"
        r"['\"]([^'\"\s]{12,})['\"]"),
    "connection string w/ creds": re.compile(
        r"(?i)\b(postgres|postgresql|mysql|mongodb|redis|amqp)://[^:\s]+:[^@\s]{6,}@"),
    "public IPv4": re.compile(
        r"\b(?!10\.|127\.|169\.254\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|0\.)"
        r"(\d{1,3}\.){3}\d{1,3}\b"),
    "private IPv4": re.compile(
        r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b"),
}

# A credential class fails the build. Everything else is reported.
NOT_A_CREDENTIAL = {"private IPv4"}

PLACEHOLDER = re.compile(
    r"(?i)your|example|changeme|xxx|placeholder|<|\.\.\.|dummy|sample|test|fake|redact|REPLACE_ME")

TEXT_SUFFIXES = (".md", ".py", ".sh", ".yml", ".yaml", ".json", ".lua", ".ts", ".tsx",
                 ".cs", ".xml", ".ini", ".env", ".mdc", ".toml", ".cfg", ".txt")


def find(body: str, where: str, hits: dict) -> None:
    for name, rx in PATTERNS.items():
        for m in rx.finditer(body):
            frag = m.group(0)[:60]
            before = body[max(0, m.start() - 40):m.start()]
            if PLACEHOLDER.search(m.group(0)) or PLACEHOLDER.search(before):
                continue
            if name == "public IPv4" and any(int(o) > 255 for o in frag.split(".") if o.isdigit()):
                continue                                   # a version string, not an address
            hits[name].append((where, frag))


def scan_worktree(hits: dict) -> int:
    n = 0
    for p in Path(".").rglob("*"):
        if not p.is_file() or any(x in p.parts for x in (".git", "node_modules", ".venv")):
            continue
        if p.suffix not in TEXT_SUFFIXES:
            continue
        try:
            find(p.read_text(encoding="utf-8", errors="ignore"), str(p), hits)
        except Exception:
            continue
        n += 1
    return n


def scan_history(hits: dict) -> int:
    objects = subprocess.run(["git", "rev-list", "--objects", "--all"],
                             capture_output=True, text=True).stdout.splitlines()
    paths = {}
    for line in objects:
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1].endswith(TEXT_SUFFIXES):
            paths[parts[0]] = parts[1]
    for sha, path in paths.items():
        try:
            body = subprocess.run(["git", "cat-file", "-p", sha],
                                  capture_output=True, text=True, timeout=15).stdout
        except Exception:
            continue
        find(body, path, hits)
    return len(paths)


def main() -> int:
    history = "--history" in sys.argv
    hits: dict = collections.defaultdict(list)
    n = scan_history(hits) if history else scan_worktree(hits)
    scope = "full git history" if history else "working tree"
    print(f"scanned {n} files ({scope})\n")

    if not hits:
        print("  no credentials found")
        return 0

    for name, items in sorted(hits.items()):
        uniq = sorted({f for _, f in items})
        tag = "operational detail" if name in NOT_A_CREDENTIAL else "CREDENTIAL"
        print(f"  [{tag}] {name}: {len(items)} occurrence(s), {len(uniq)} distinct")
        for f in uniq[:8]:
            where = next(w for w, x in items if x == f)
            print(f"      {f:<48} in {where}")

    severe = sorted(k for k in hits if k not in NOT_A_CREDENTIAL)
    if history:
        print(f"\nreport only — history findings cannot be fixed by a later commit"
              f"{'; credential classes present: ' + str(severe) if severe else ''}")
        return 0
    if severe:
        print(f"\nFAIL: credential class(es) in the working tree: {severe}")
        return 1
    print("\nOK: no credential classes in the working tree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
