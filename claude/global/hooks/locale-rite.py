#!/usr/bin/env python3
"""PostToolUse hook — measures the code-locale rite at the moment a file is written.

Reads the hook payload on stdin and, when a Write/Edit just landed, runs the shipped
identifier-locale check against the written PATH and the written CONTENT. Findings go back to the
assistant as context for the next turn. Silent when the write is clean.

Why a hook and not only the skill and the global rule: both were already in place — the `code-locale`
skill in the catalog and the Code Locale section of personal-rules.md — and Portuguese identifiers
and file names kept reaching code in new sessions (issue #95). Doctrine in context is not
measurement. This is the same argument `backlog-rite.py` states for its own rule, applied to the one
rule whose violation is visible in the artifact itself.

WHY `hookSpecificOutput.additionalContext` AND NOT PLAIN STDOUT
    For PostToolUse, plain stdout goes to the debug log and the model never sees it. The events that
    turn stdout into context are UserPromptSubmit, UserPromptExpansion and SessionStart — which is
    why the repo's other two rite hooks can print and this one cannot. Probed against the installed
    binary rather than recalled. First measured on 2.1.246 (2026-08-26): the bundle reads
    `let {additionalContext:a,...l}=e.hookSpecificOutput` with the cap `additionalContext:8000`.
    Re-measured 2026-09-05 on `readlink -f $(which claude)` ->
    ~/.local/share/claude/versions/2.1.261 (`claude --version` -> `2.1.261 (Claude Code)`; a
    single ELF, so the grep needs `-a`): `grep -a -o -E 'additionalContext:[0-9]+'` prints
    `additionalContext:8000` exactly once, and the same on the 2.1.260 bundle beside it.
    Docs: code.claude.com/docs/en/hooks (read 2026-08-26).

WHAT THIS HOOK DELIBERATELY DOES NOT DO
    - It never blocks. The tool already ran, and the rite informs; the user waives.
    - It never writes state, reads credentials, or calls the network.
    - It reports nothing when the shipped check is missing: a gate that is absent must not present
      itself to the user as an error.
    - It inherits every limit of the check it calls, including the open-vocabulary escape — a
      Portuguese word outside the lexicon passes here exactly as it passes in CI.

Wiring (~/.claude/settings.json):

    "hooks": {
      "PostToolUse": [
        {"matcher": "Write|Edit|MultiEdit|NotebookEdit",
         "hooks": [{"type": "command",
                    "command": "python3 ~/ai-skills/claude/global/hooks/locale-rite.py",
                    "timeout": 10}]}
      ]
    }

Like personal-rules.md, this is the maintainer's config — edit the matcher and the message to match
your own process instead of adopting it blindly.

Modes: (default) read one payload from stdin   |   --selftest assert the decisions against synthetic payloads.
Any other argument prints usage to stderr and exits 2 — the same contract as backlog-rite.py and
verify-rite.py since #115, so a misspelt flag cannot fall through to the stdin path and exit 0.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

# The check lives in the skill that owns the doctrine. parents[3] of this file is the repository
# root — three directories up from claude/global/hooks/ (hooks -> global -> claude -> root); the path
# is resolved, never guessed, and a miss exits silently.
CHECK_PATH = Path(__file__).resolve().parents[3] / "skills/code-locale/references/check-identifier-locale.py"

# The harness truncates a longer value; truncating here keeps the tail we choose rather than the
# tail it chooses. Measured cap: `additionalContext:8000` in claude 2.1.246, 2.1.260 and 2.1.261
# (see the docstring for the probe).
CONTEXT_CAP = 8000

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

ADVISORY_HEADER = (
    "CODE-LOCALE (advisory): the write that just landed carries a word the English list does not "
    "know. If it is English, it belongs in programming-words.txt; if it is not, rename it. This is a "
    "question, not a verdict — the check is not sure, which is why it does not fail the run.\n\n"
)

HEADER = (
    "CODE-LOCALE: the write that just landed carries a non-English name in the machine layer. "
    "Identifiers, file and directory names are English (code-locale skill); comments, docstrings "
    "and user-facing strings keep the repository's language. Rename before continuing, or state the "
    "reason the name is correct as written.\n\n"
)


def load_check():
    """Import the shipped check by path. Its file name has hyphens, so it is not importable by name."""
    if not CHECK_PATH.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("check_identifier_locale", CHECK_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def written_text(tool_name: str, tool_input: dict) -> str:
    """The text this tool call added — never the file's existing content, which the rite does not judge."""
    if tool_name == "Write":
        return tool_input.get("content") or ""
    if tool_name == "Edit":
        return tool_input.get("new_string") or ""
    if tool_name == "MultiEdit":
        return "\n".join(e.get("new_string") or "" for e in tool_input.get("edits") or [])
    if tool_name == "NotebookEdit":
        return tool_input.get("new_source") or ""
    return ""


def first_line_of(path: Path, text: str) -> int:
    """Where the written fragment starts in the file, so a finding points at a real line.

    An Edit hands over `new_string` alone, and scanning it in isolation numbers its lines from 1 —
    which reads as "line 1 of the file" and sends the reader to the wrong place. Locating the
    fragment in the file that the tool has already written is what makes the number true. A fragment
    that cannot be located (a replace_all whose copies differ, a file already changed again) falls
    back to 1, which is the previous behaviour and never worse than it.
    """
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        return 1
    index = body.find(text)
    return body.count("\n", 0, index) + 1 if index >= 0 else 1


def findings_for(check, file_path: str, text: str, cwd: str) -> list:
    path = Path(file_path)
    if check.is_vendored(path):
        return []
    root = Path(cwd) if cwd else Path.cwd()
    allow = check.load_allowlist(root)
    english = check.load_english() if hasattr(check, "load_english") else None
    findings = list(check.scan_path(path, allow, root, english))
    lang = check.EXT_LANG.get(path.suffix.lower())
    if lang and text:
        rel = check.project_relative(path, root)
        findings.extend(check.scan_text(text, lang, str(rel), allow,
                                        first_line=first_line_of(path, text), english=english))
    return findings


def report(findings: list) -> dict:
    # Gating first, advisory after, and the header says which is which: an advisory finding is a
    # question for the author ("is this English?"), not a defect the check is sure of.
    gating = [f for f in findings if not getattr(f, "advisory", False)]
    advisory = [f for f in findings if getattr(f, "advisory", False)]
    body = (HEADER if gating else ADVISORY_HEADER) + "\n".join(f.render() for f in gating + advisory)
    if len(body) > CONTEXT_CAP:
        body = body[:CONTEXT_CAP - 80].rstrip() + "\n    … truncated; run the check on the file for the rest."
    parts = []
    if gating:
        parts.append(f"{len(gating)} non-English name{'s' if len(gating) != 1 else ''}")
    if advisory:
        parts.append(f"{len(advisory)} unrecognised word{'s' if len(advisory) != 1 else ''} (advisory)")
    return {
        "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": body},
        "systemMessage": "code-locale: " + ", ".join(parts) + " in the last write",
    }


def evaluate(payload: dict, check) -> "dict | None":
    """The whole decision, isolated from stdin and stdout so the selftest can drive it."""
    if check is None:
        return None
    tool_name = payload.get("tool_name") or ""
    if tool_name not in WRITE_TOOLS:
        return None
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return None
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        return None
    cwd = payload.get("cwd") or os.getcwd()
    try:
        findings = findings_for(check, file_path, written_text(tool_name, tool_input), cwd)
    except Exception:
        return None                      # a check that crashes must not crash the write
    return report(findings) if findings else None


def selftest() -> int:
    check = load_check()
    if check is None:
        print(f"selftest FAILED: check not found at {CHECK_PATH}")
        return 1
    cwd = "/tmp/locale-rite-selftest"
    cases = [
        ("portuguese path reported", True, {
            "tool_name": "Write", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/servicos_pedido/shipping.py", "content": "x = 1\n"}}),
        ("portuguese identifier reported", True, {
            "tool_name": "Write", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/orders/service.py",
                           "content": "def buscar_order(x):\n    return x\n"}}),
        ("edit reports its new_string", True, {
            "tool_name": "Edit", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/orders/service.py", "old_string": "a",
                           "new_string": "usuario_count = 1\n"}}),
        ("no language profile still measures the path", True, {
            "tool_name": "Write", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/reports/cadastro.xlsx", "content": ""}}),
        ("clean write is silent", False, {
            "tool_name": "Write", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/orders/shipping_cost.py",
                           "content": "def compute_shipping(order_id):\n    return 0\n"}}),
        ("portuguese comment is prose, not a finding", False, {
            "tool_name": "Write", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/orders/shipping.py",
                           "content": "# calcula o frete do pedido\ntotal = 0\n"}}),
        ("vendored path is silent", False, {
            "tool_name": "Write", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/node_modules/servicos/pedido.js", "content": "var a=1\n"}}),
        ("another tool is ignored", False, {
            "tool_name": "Bash", "cwd": cwd, "tool_input": {"command": "ls servicos_pedido"}}),
        ("payload without file_path is ignored", False, {
            "tool_name": "Write", "cwd": cwd, "tool_input": {}}),
        ("payload without tool_input is ignored", False, {"tool_name": "Write", "cwd": cwd}),
        ("empty payload is ignored", False, {}),
        ("missing file on disk still reports the path", True, {
            "tool_name": "Edit", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/servicos/x.py", "old_string": "a",
                           "new_string": "b = 1\n"}}),
    ]
    failed = []
    for name, should_report, payload in cases:
        got = evaluate(payload, check)
        ok = bool(got) == should_report
        print(f"  {'OK     ' if ok else 'FAILED '} {name}")
        if not ok:
            failed.append(name)
    reported = evaluate(cases[0][2], check)
    shape_ok = (
        isinstance(reported, dict)
        and reported["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        and isinstance(reported["hookSpecificOutput"]["additionalContext"], str)
        and len(reported["hookSpecificOutput"]["additionalContext"]) <= CONTEXT_CAP
    )
    print(f"  {'OK     ' if shape_ok else 'FAILED '} output shape is the field the harness reads")
    if not shape_ok:
        failed.append("output shape")
    # The argv contract can only be measured through the real entry point: a misspelt flag must
    # print usage and exit 2, never read stdin and exit 0 (the silent no-op #115 closed in the
    # sibling hooks).
    run = subprocess.run([sys.executable, __file__, "--bogus"], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    argv_ok = run.returncode == 2 and "usage:" in run.stderr and run.stdout == ""
    print(f"  {'OK     ' if argv_ok else 'FAILED '} unknown flag prints usage and exits 2")
    if not argv_ok:
        failed.append("unknown flag")
    print()
    if failed:
        print("selftest FAILED: " + "; ".join(failed))
        return 1
    print(f"selftest OK: {len(cases)} decisions, the output shape, plus the argv contract")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args == ["--selftest"]:
        return selftest()
    if args:
        # An unknown argument must not fall through to the stdin path: a misspelt flag in a CI
        # step would then read empty stdin and exit 0 — the silent no-op the selftest mode exists
        # to make impossible.
        print(f"usage: {sys.argv[0]} [--selftest]", file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0
    result = evaluate(payload, load_check())
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
