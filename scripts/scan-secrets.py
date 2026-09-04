"""Scan the repository for credentials.

Three modes, deliberately different, because they answer different questions:

  (default)     scan the WORKING TREE. Gates CI: exits 1 on any credential class.
                This is the part that can be kept clean, so this is the part that gates.

  --history     scan every blob in the full git history. Reports only, never gates.
                A secret removed in a later commit is still published, so this is worth
                knowing — but it cannot be fixed by a later commit, and a gate that can
                never go green is a gate everyone learns to ignore.

  --selftest    inject one credential per pattern and assert each class is reported. Gates
                CI beside the scan: a clean tree and a pattern that cannot fire are otherwise
                indistinguishable. Samples are BUILT at run time, never written as literals —
                this file is in the tree the default mode scans, and a literal token here would
                fail the build by design.

Private (RFC1918) addresses are reported as operational detail, not as a credential class:
worth removing from a public repo, not a breach, and never a reason to fail a build.

The placeholder filter applies to the MATCHED TOKEN ONLY. It used to also read the forty
characters before the match, which silenced `test_token = ghp_…` and `<ghp_…>` — a real key
after the word `test` or after `<` passed the gate (issue #117, measured 2026-09-04).

KNOWN LIMIT: the selftest proves each pattern fires on its own sample and stays silent on the
placeholder shapes listed below; it does not read the tree, and it cannot judge a placeholder the
documentation invents that the filter does not know. A token that itself contains a placeholder
word (`ghp_test…`) is silenced on purpose and is not a class this scanner claims. The pattern set
is what it is: a credential format not listed in PATTERNS passes.

Usage:  python3 scripts/scan-secrets.py [--history | --selftest]
"""
from __future__ import annotations

import collections
import re
import string
import subprocess
import sys
from pathlib import Path

PATTERNS = {
    "AWS access key":     re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token":       re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b"),
    "sk- API key":        re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),
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

# Applied to the matched token only — never to the text around it (see the module docstring).
PLACEHOLDER = re.compile(
    r"(?i)your|example|changeme|xxx|placeholder|<|\.\.\.|dummy|sample|test|fake|redact|REPLACE_ME")

TEXT_SUFFIXES = (".md", ".py", ".sh", ".yml", ".yaml", ".json", ".lua", ".ts", ".tsx",
                 ".cs", ".xml", ".ini", ".env", ".mdc", ".toml", ".cfg", ".txt")


def find(body: str, where: str, hits: dict) -> None:
    for name, rx in PATTERNS.items():
        for m in rx.finditer(body):
            frag = m.group(0)[:60]
            if PLACEHOLDER.search(m.group(0)):
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


# ── selftest ──────────────────────────────────────────────────────────────
# One sample per pattern, assembled from pieces so that no line of this file matches a pattern.
# `fill(n)` yields n characters of a fixed alphabet that contains no placeholder word.
_ALPHABET = string.ascii_letters + string.digits


def _fill(n: int) -> str:
    return (_ALPHABET * (n // len(_ALPHABET) + 1))[:n]


def _samples() -> dict[str, str]:
    return {
        "AWS access key":            "AKIA" + _fill(16).upper(),
        "GitHub token":              "ghp_" + _fill(36),
        "GitHub fine-grained token": "github_pat_" + _fill(30),
        "sk- API key":               "sk-" + _fill(24),
        "Slack token":               "xoxb-" + _fill(14),
        "Google API key":            "AIza" + _fill(35),
        "private key block":         "-----BEGIN " + "RSA PRIVATE" + " KEY-----",
        "JWT":                       "eyJ" + _fill(12) + "." + _fill(12) + "." + _fill(12),
        "generic assigned secret":   "password = " + '"' + _fill(16) + '"',
        "connection string w/ creds": "postgres://app:" + _fill(10) + "@db.internal/app",
        "public IPv4":               ".".join(["203", "0", "113", "7"]),
        "private IPv4":              ".".join(["10", "0", "0", "1"]),
    }


def _classes(body: str) -> set[str]:
    hits: dict = collections.defaultdict(list)
    find(body, "<selftest>", hits)
    return set(hits)


def selftest() -> int:
    samples = _samples()
    fired = 0
    for name in PATTERNS:
        if name not in samples:
            print(f"  MISSED  {name}: no sample in the selftest   <-- add one")
            continue
        if name in _classes(samples[name]):
            print(f"  CAUGHT  {name}")
            fired += 1
        else:
            print(f"  MISSED  {name}   <-- the pattern cannot fire")

    # The two shapes the old before-window silenced: a placeholder word BEFORE the token, and the
    # token wrapped in angle brackets. Both are real credentials and must be reported.
    context_cases = [
        ("token after the word test", "test_token = " + samples["GitHub token"], "GitHub token"),
        ("token between angle brackets", "<" + samples["GitHub token"] + ">", "GitHub token"),
        ("key after the word example", "example: " + samples["sk- API key"], "sk- API key"),
    ]
    context_ok = 0
    for label, body, expected in context_cases:
        if expected in _classes(body):
            print(f"  CAUGHT  {label}")
            context_ok += 1
        else:
            print(f"  MISSED  {label}   <-- silenced by the text around the token")

    # Placeholder shapes the scanner must stay silent on, and the class that is reported but
    # never fails the build.
    silent_cases = [
        ("token that is itself a placeholder", "ghp_" + "x" * 36),
        ("connection string with a <password> placeholder", "postgres://app:<password>@db/app"),
        ("assigned secret set to a placeholder", "api_key = " + '"' + "REPLACE_ME_WITH_YOURS" + '"'),
    ]
    quiet = 0
    for label, body in silent_cases:
        got = _classes(body)
        if got:
            print(f"  FALSE POSITIVE  {label}   <-- {sorted(got)}")
        else:
            print(f"  SILENT  {label}")
            quiet += 1

    reported_only = _classes(samples["private IPv4"]) == {"private IPv4"}
    print(f"  {'REPORTED' if reported_only else 'GATED'}  private IPv4 is reported, never a credential")

    print(f"\n{fired}/{len(PATTERNS)} patterns fire on their sample, "
          f"{context_ok}/{len(context_cases)} context cases caught, "
          f"{quiet}/{len(silent_cases)} placeholder cases stayed silent")
    return 0 if (fired == len(PATTERNS) and context_ok == len(context_cases)
                 and quiet == len(silent_cases) and reported_only) else 1


# ── main ──────────────────────────────────────────────────────────────────
def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
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
