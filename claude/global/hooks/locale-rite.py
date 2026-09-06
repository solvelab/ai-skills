#!/usr/bin/env python3
"""PreToolUse + PostToolUse hook — enforces the code-locale rite at the moment a file is written.

Reads the hook payload on stdin and, when a Write/Edit is about to land (PreToolUse) or has just
landed (PostToolUse), runs the shipped identifier-locale check against the written PATH and the
written CONTENT. One decision, two envelopes, chosen by `hook_event_name`:

    PreToolUse   a gating finding (pt-verb, pt-noun in the added content; path-pt-* in a path the write
                 CREATES) DENIES the tool call, with the findings and the three exits in the reason; an
                 advisory finding alone (en-unknown) denies nothing, and neither does a clean write.
                 A file that already exists is never denied for its own name: the name is on disk
                 already, existing names change through a deprecation window and not through a blocked
                 edit, and a denial naming a file the model did not name has no exit but the allowlist.
    PostToolUse  advisory only, exactly as before this mode existed: findings go back to the assistant
                 as context for the next turn, gating and advisory alike — a legacy path included, so
                 the name stays visible. Silent when the write is clean.

    On both events a `# locale-ok: <reason>` that already sits in the file on the line above the
    fragment an Edit replaces counts as if it were part of the new text (D9 of the change): the
    denial's first exit tells the model to put the waiver there, and a hook that then cannot see it
    produces the blind second attempt issue #137 lists as a risk.

Why deny and not only inform: the rule already existed in three layers — the Code Locale section of
personal-rules.md, the `code-locale` skill and this hook on PostToolUse — and Portuguese identifiers
kept reaching code in new sessions (issues #95, #137). With the hook only informing, the model reads
the finding and moves on; nothing obliges it to rename. PreToolUse has the content in the payload, so
this is measurement of the write itself, not a proxy for it.

WHY `hookSpecificOutput.additionalContext` AND NOT PLAIN STDOUT (PostToolUse)
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

WHY `hookSpecificOutput.permissionDecision` AND NOT `exit 2` (PreToolUse)
    Probed 2026-09-05 on the same 2.1.261 bundle with `re.finditer` over the bytes (the machine's
    grep is ugrep and refuses the pattern with context). The output schema for the event is
    `c({hookEventName:C("PreToolUse"),permissionDecision:boe().optional(),permissionDecisionReason:
    s().optional(),updatedInput:pe(s(),se()).optional(),additionalContext:s().optional()})`, and the
    normaliser keeps the reason only when the decision is deny or ask:
    `let o=t.permissionDecision==="deny"||t.permissionDecision==="ask"; ... d=o?X5(e,
    "permissionDecisionReason",t.permissionDecisionReason):void 0`. `X5` applies TWO caps, read
    from `AKr={...,additionalContext:8000,permissionDecisionReason:2000}` (characters) and
    `RKr={...,additionalContext:200,permissionDecisionReason:20}` (lines): the reason is cut to 20
    lines and 2000 characters, the context to 200 lines and 8000 characters — the line cap was not
    recorded here before. An envelope whose `hookEventName` does not match the event is dropped
    (`if(t.hookEventName!==r){Ik(e,"hookSpecificOutput_event_mismatch",!0);return}`), which is why
    the event name comes from the payload and not from a constant. `exit 2` also denies (the bundle
    wraps stderr as the reason), but through a cap this hook did not measure; JSON keeps one output
    format for both events. The bundle also honours `additionalContext` on PreToolUse — the schema
    above carries it, and the run loop yields it as `hook_additional_context` with
    `hookEvent:"PreToolUse"` — but this hook does not use it: with both events wired, the advisory
    would reach the model twice for one write, and PostToolUse already carries it.

MODES
    default                  PreToolUse denies on a gating finding; PostToolUse informs.
    LOCALE_RITE_MODE=inform  PreToolUse never denies; PostToolUse informs as before. The whole
                             session, for the rare tree where the lexicon is wrong more often than
                             right. Any other value of the variable — empty, absent, misspelt — is the
                             default mode, so a typo cannot open the door in silence.
    The two exits the check already honours still apply and are named in every denial:
    `# locale-ok: <reason>` on the line above an identifier, and the name or the path listed in
    .identifier-locale-allow (the only waiver a file name can carry).

WHAT THIS HOOK DELIBERATELY DOES NOT DO
    - It never denies on PostToolUse (the tool already ran) and never denies on an advisory finding
      alone: a word the English list does not know is a question, not a verdict.
    - It never rewrites the tool input (`updatedInput` exists in the bundle): renaming on the model's
      behalf would be an invented translation, and the rite forbids exactly that.
    - It never writes state, reads credentials, or calls the network.
    - It reports nothing when the shipped check is missing: a gate that is absent must not present
      itself to the user as an error.
    - It inherits every limit of the check it calls, including the open-vocabulary escape — a
      Portuguese word outside the lexicon passes here exactly as it passes in CI.

THE PROSE DIRECTION (issue #179)
    Where the repository the written file belongs to declares its prose language — a `.code-locale`
    file with `prose: pt-BR` (or `en`), found by walking up from the written file's directory until
    `.code-locale`, `.git` or the filesystem root, with the payload's `cwd` as the fallback when the
    walk met no repository at all — the same write is also measured by the prose detector beside the
    check (`check-prose-locale.py`): comments and docstrings of the written text, and paragraphs of
    a written `.md`. PreToolUse denies a comment or docstring with strong evidence of the wrong
    language, with the same three exits in the reason (the inline `locale-ok:` also covers the
    fragment's own line); a Markdown paragraph and weak evidence never deny and reach the assistant
    as advisory on PostToolUse. Without the declaration nothing about prose is measured and the hook
    behaves exactly as before #179. A declaration the detector cannot read leaves this hook silent
    for prose — one error per write would be noise — and the Stop gate names it once per turn.
    What each tool hands over: Write its `content`, Edit its `new_string`, MultiEdit every
    `new_string` joined (a joined text cannot be anchored in the file, so its findings are numbered
    inside the joined text — `first_line_of` falls back to 1), NotebookEdit its `new_source` read as
    Python for a code cell and as Markdown for a `cell_type: markdown` cell (`.ipynb` has no entry
    in EXT_LANG, so the identifier tier does not measure notebooks — a pre-existing gap, see KNOWN
    LIMIT).

KNOWN LIMIT
    Only the harness write tools pass through here (Write, Edit, MultiEdit, NotebookEdit). A file
    written by a Bash command — heredoc, `sed -i`, a script — is never seen, so a denied write is not
    proof that no Portuguese name can land. Closing that path is the Stop gate of issue #138.
    The prose direction inherits every limit the prose detector declares (strings and log messages
    not measured, only Portuguese and English, function words rather than a dictionary), and is
    silent wherever the detector file is absent or the declaration is unreadable.
    A NotebookEdit is measured for prose only: the identifier tier reads the language off the file
    suffix through EXT_LANG, which has no `.ipynb`, so a Portuguese name in a notebook cell passes
    the write hook (the Stop gate does not read notebooks either).

Wiring (~/.claude/settings.json) — BOTH blocks, same command. PreToolUse is the one that denies;
PostToolUse is the one that carries the advisory and the `inform` mode. Wiring only the first loses
en-unknown; wiring only the second is the behaviour before issue #137.

    "hooks": {
      "PreToolUse": [
        {"matcher": "Write|Edit|MultiEdit|NotebookEdit",
         "hooks": [{"type": "command",
                    "command": "python3 ~/ai-skills/claude/global/hooks/locale-rite.py",
                    "timeout": 10}]}
      ],
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
The selftest feeds only the fields this hook reads (`hook_event_name`, `tool_name`, `tool_input`,
`cwd`), in the shape the 2.1.261 bundle declares; that the harness still sends them under those names
is what the wired session proves, not the selftest. The prose cases build their own temporary trees,
each with a `.git` directory that stops the declaration walk, so the selftest never reads the
declaration or the allowlist of whoever runs it.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# The check lives in the skill that owns the doctrine. parents[3] of this file is the repository
# root — three directories up from claude/global/hooks/ (hooks -> global -> claude -> root); the path
# is resolved, never guessed, and a miss exits silently.
CHECK_PATH = Path(__file__).resolve().parents[3] / "skills/code-locale/references/check-identifier-locale.py"
# The prose detector ships beside the check and imports it by path; a miss leaves the prose
# direction silent, never the whole hook.
PROSE_CHECK_PATH = CHECK_PATH.parent / "check-prose-locale.py"
_prose_cache: "tuple | None" = None

# The harness truncates a longer value; truncating here keeps the tail we choose rather than the
# tail it chooses. Measured caps (see the docstring for the probes): `additionalContext:8000`
# characters in claude 2.1.246, 2.1.260 and 2.1.261, plus 200 lines in 2.1.261;
# `permissionDecisionReason:2000` characters and 20 lines in 2.1.261.
CONTEXT_CAP = 8000
CONTEXT_LINE_CAP = 200
REASON_CAP = 2000
REASON_LINE_CAP = 20
# Header (1) + findings (<= 12) + "+N more" (1) + advisory count (1) + exits (3, or 4 with the prose
# line) = 19 < 20 lines.
REASON_MAX_FINDINGS = 12

PRE_EVENT = "PreToolUse"
POST_EVENT = "PostToolUse"

MODE_ENV = "LOCALE_RITE_MODE"
MODE_INFORM = "inform"

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

PROSE_HEADER = (
    "CODE-LOCALE: the write that just landed carries a comment or docstring that does not read as the "
    "repository's declared prose language (.code-locale, code-locale skill). Translate it before "
    "continuing, or waive it with `locale-ok: <reason>` on its line or the line above.\n\n"
)

PROSE_ADVISORY_HEADER = (
    "CODE-LOCALE (advisory): the write that just landed carries prose that reads as a language other "
    "than the one .code-locale declares — a Markdown paragraph, or a fragment with weak evidence. "
    "Advisory only: it never denies, and the author decides.\n\n"
)

DENY_HEADER = (
    "CODE-LOCALE: write denied — {count} non-English name{plural} in the machine layer. Identifiers, "
    "file and directory names are English (code-locale skill); comments, docstrings and strings keep "
    "the repository's language. Rename, or waive with a reason:"
)
DENY_PROSE_HEADER = (
    "CODE-LOCALE: write denied — {count} comment{plural} or docstring{plural} not in the repository's "
    "prose language ({declared}, declared in .code-locale; code-locale skill). Translate, or waive with "
    "a reason:"
)
DENY_BOTH_HEADER = (
    "CODE-LOCALE: write denied — {names} non-English name{names_plural} in the machine layer and "
    "{count} comment{plural} or docstring{plural} not in the repository's prose language ({declared}, "
    ".code-locale). Rename or translate, or waive with a reason:"
)
PROSE_EXIT = (
    "  (prose) the same `locale-ok: <reason>` on the comment's own line or the line above, or translate "
    "it to the declared language;"
)

# The three exits, literal, so the model can act without opening the skill. A denial that only says
# "there are exits" produces the blind second attempt issue #137 lists as a risk.
EXITS = (
    "Exits: (1) `# locale-ok: <reason>` on the line above the name (identifiers only — a file name "
    "has nowhere to carry it);",
    "  (2) list the name or the path in .identifier-locale-allow (the only waiver for a file name);",
    f"  (3) export {MODE_ENV}={MODE_INFORM} to make this hook advisory for the whole session.",
)


def load_check():
    """Import the shipped check by path. Its file name has hyphens, so it is not importable by name."""
    if not CHECK_PATH.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("check_identifier_locale", CHECK_PATH)
        module = importlib.util.module_from_spec(spec)
        sys.dont_write_bytecode = True       # no __pycache__ beside the shipped files
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def load_prose():
    """Import the prose detector by path, once per process. None when it is absent or does not load:
    the prose direction is then silent, and the identifier direction is unaffected."""
    global _prose_cache
    if _prose_cache is None:
        module = None
        if PROSE_CHECK_PATH.is_file():
            try:
                spec = importlib.util.spec_from_file_location("check_prose_locale", PROSE_CHECK_PATH)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception:
                module = None
        _prose_cache = (module,)
    return _prose_cache[0]


def declared_prose(prose, path: Path, cwd: str) -> "str | None":
    """The prose language the written file's repository declares, or None (undeclared, or unreadable).

    The walk starts at the file's directory; the payload's cwd is the fallback only when that walk
    met no repository boundary at all — a file inside a repository that does not declare is never
    judged by another directory's declaration.
    """
    found, boundary = prose.find_declaration(path.parent)
    if found is None and boundary is None and cwd:
        found, _boundary = prose.find_declaration(Path(cwd))
    if found is None:
        return None
    try:
        return prose.load_declaration(found)
    except prose.DeclarationError:
        return None                          # named by the Stop gate once per turn, not per write


def prose_findings_for(prose, file_path: str, text: str, cwd: str, anchor: str, check,
                       kind: "str | None" = None) -> list:
    """Prose findings for one write, empty wherever the repository declares nothing. `kind` names
    the language when the path cannot (a notebook cell); else the detector reads it off the suffix."""
    if prose is None or not text:
        return []
    path = Path(file_path)
    if check.is_vendored(path):
        return []
    kind = kind or prose.kind_for(path)
    if kind is None:
        return []
    declared = declared_prose(prose, path, cwd)
    if declared is None:
        return []
    root = Path(cwd) if cwd else Path.cwd()
    allow = check.load_allowlist(root)
    rel = check.project_relative(path, root)
    first_line = first_line_of(path, anchor)
    findings = prose.scan_text(text, kind, str(rel), declared, allow, first_line=first_line)
    if waiver_above(check, path, first_line):
        findings = [f for f in findings if f.line != first_line]
    return findings


def is_prose(f) -> bool:
    return hasattr(f, "fragment")


def current_mode() -> str:
    """The session mode from the environment. Anything but `inform` is the default (denying) mode."""
    return os.environ.get(MODE_ENV, "").strip().lower()


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


def first_line_of(path: Path, anchor: str) -> int:
    """Where the written fragment starts in the file, so a finding points at a real line.

    An Edit hands over `new_string` alone, and scanning it in isolation numbers its lines from 1 —
    which reads as "line 1 of the file" and sends the reader to the wrong place. Locating the
    fragment in the file is what makes the number true. After the write (PostToolUse) the anchor is
    the `new_string` the tool has already put there; before it (PreToolUse) the `new_string` is not
    in the file yet, so the anchor is the `old_string` it will replace, which sits exactly where the
    new text will start. An anchor that cannot be located (a replace_all whose copies differ, a file
    already changed again, a Write) falls back to 1, which is the previous behaviour and never worse
    than it.
    """
    if not anchor:
        return 1
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        return 1
    index = body.find(anchor)
    return body.count("\n", 0, index) + 1 if index >= 0 else 1


def waiver_above(check, path: Path, first_line: int) -> bool:
    """True when the file line immediately above the located fragment carries `locale-ok: <reason>`.

    `scan_text()` honours a waiver on the line above a name, but only inside the text it is given; an
    Edit hands over `new_string` alone, so a waiver that already sits in the file — including one the
    model just added because the denial told it to — is outside that text. `first_line` is 1 when
    the fragment was not located (or is the whole file), and then there is no line above to read.
    The regex is the check's own, so the two never drift apart.
    """
    if first_line <= 1:
        return False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    above = first_line - 2                       # 0-based index of the line before the fragment
    return above < len(lines) and bool(check.WAIVER_RE.search(lines[above]))


def findings_for(check, file_path: str, text: str, cwd: str, anchor: str, pre: bool = False) -> list:
    """Path findings plus content findings for one write.

    Before the write (`pre`), the path is judged only when the write CREATES it — a file already on
    disk is never denied for its own name, and its path findings are left out of the reason entirely
    (D8). After the write the path is reported as it always was, so a legacy name stays visible.
    """
    path = Path(file_path)
    if check.is_vendored(path):
        return []
    root = Path(cwd) if cwd else Path.cwd()
    allow = check.load_allowlist(root)
    english = check.load_english() if hasattr(check, "load_english") else None
    creates = not path.exists()
    findings = list(check.scan_path(path, allow, root, english)) if (creates or not pre) else []
    lang = check.EXT_LANG.get(path.suffix.lower())
    if lang and text:
        rel = check.project_relative(path, root)
        first_line = first_line_of(path, anchor)
        fragment = check.scan_text(text, lang, str(rel), allow, first_line=first_line, english=english)
        if waiver_above(check, path, first_line):
            fragment = [f for f in fragment if f.line != first_line]
        findings.extend(fragment)
    return findings


def split_findings(findings: list) -> "tuple[list, list]":
    gating = [f for f in findings if not getattr(f, "advisory", False)]
    advisory = [f for f in findings if getattr(f, "advisory", False)]
    return gating, advisory


def report(findings: list) -> dict:
    """The PostToolUse envelope — advisory, the tool call already ran. Unchanged by issue #137."""
    # Gating first, advisory after, and the header says which is which: an advisory finding is a
    # question for the author ("is this English?"), not a defect the check is sure of.
    gating, advisory = split_findings(findings)
    gating_names = [f for f in gating if not is_prose(f)]
    gating_prose = [f for f in gating if is_prose(f)]
    advisory_names = [f for f in advisory if not is_prose(f)]
    advisory_prose = [f for f in advisory if is_prose(f)]
    header = (HEADER if gating_names else PROSE_HEADER if gating_prose
              else ADVISORY_HEADER if advisory_names else PROSE_ADVISORY_HEADER)
    body = header + "\n".join(f.render() for f in gating + advisory)
    if len(body) > CONTEXT_CAP:
        body = body[:CONTEXT_CAP - 80].rstrip() + "\n    … truncated; run the check on the file for the rest."
    parts = []
    if gating_names:
        parts.append(f"{len(gating_names)} non-English name{'s' if len(gating_names) != 1 else ''}")
    if gating_prose:
        parts.append(f"{len(gating_prose)} comment{'s' if len(gating_prose) != 1 else ''}/docstring{'s' if len(gating_prose) != 1 else ''} "
                     "in the wrong language")
    if advisory_names:
        parts.append(f"{len(advisory_names)} unrecognised word{'s' if len(advisory_names) != 1 else ''} (advisory)")
    if advisory_prose:
        parts.append(f"{len(advisory_prose)} prose fragment{'s' if len(advisory_prose) != 1 else ''} in the wrong language (advisory)")
    return {
        "hookSpecificOutput": {"hookEventName": POST_EVENT, "additionalContext": body},
        "systemMessage": "code-locale: " + ", ".join(parts) + " in the last write",
    }


def finding_line(f) -> str:
    """One line per finding. The check's own render() spends 4-5 lines each, which the 20-line cap
    would spend on the first four findings and then cut the exits — the part that must survive."""
    where = f"{f.path}:{f.line}" if getattr(f, "line", 0) else f.path
    if is_prose(f):
        return f'  {where}: {f.kind} reads as {f.lang}, repo prose is {f.declared}: "{f.preview()}"'
    return f"  {where}: {f.token}  [{f.tier}: '{f.segment}']"


def deny_reason(gating: list, advisory: list) -> str:
    """Header, one line per distinct (path, token), `+N more`, the advisory count, the three exits.

    Built to fit REASON_LINE_CAP lines by construction and REASON_CAP characters by trimming finding
    lines from the end — never the exits, which the harness would otherwise be the one to cut.
    """
    seen = set()
    distinct = []
    for f in gating:
        key = (f.path, f.line, "prose") if is_prose(f) else (f.path, f.token)
        if key not in seen:
            seen.add(key)
            distinct.append(f)
    names = [f for f in distinct if not is_prose(f)]
    prose = [f for f in distinct if is_prose(f)]
    plural = "s" if len(prose) != 1 else ""
    if names and prose:
        header = DENY_BOTH_HEADER.format(names=len(names), names_plural="s" if len(names) != 1 else "",
                                         count=len(prose), plural=plural, declared=prose[0].declared)
    elif prose:
        header = DENY_PROSE_HEADER.format(count=len(prose), plural=plural, declared=prose[0].declared)
    else:
        header = DENY_HEADER.format(count=len(names), plural="s" if len(names) != 1 else "")
    tail = []
    advisory_names = [f for f in advisory if not is_prose(f)]
    advisory_prose = [f for f in advisory if is_prose(f)]
    if advisory_names:
        tail.append(f"  (+{len(advisory_names)} unrecognised word{'s' if len(advisory_names) != 1 else ''}, "
                    "advisory: never denies, reported after a clean write lands)")
    if advisory_prose:
        tail.append(f"  (+{len(advisory_prose)} prose fragment{'s' if len(advisory_prose) != 1 else ''} "
                    "with weak evidence or in Markdown, advisory: never denies)")
    tail.append(EXITS[0])
    if prose:
        tail.append(PROSE_EXIT)
    tail.extend(EXITS[1:])
    shown = min(len(distinct), REASON_MAX_FINDINGS)
    while True:
        lines = [header] + [finding_line(f) for f in distinct[:shown]]
        if len(distinct) > shown:
            lines.append(f"  (+{len(distinct) - shown} more — run the check on the file for the rest)")
        text = "\n".join(lines + tail)
        if len(text) <= REASON_CAP or shown == 0:
            return text
        shown -= 1


def deny(findings: list) -> dict:
    """The PreToolUse envelope. Shape probed on the 2.1.261 bundle (see the docstring)."""
    gating, advisory = split_findings(findings)
    return {
        "hookSpecificOutput": {
            "hookEventName": PRE_EVENT,
            "permissionDecision": "deny",
            "permissionDecisionReason": deny_reason(gating, advisory),
        }
    }


def evaluate(payload: dict, check, mode: "str | None" = None) -> "dict | None":
    """The whole decision, isolated from stdin and stdout so the selftest can drive it.

    `mode` defaults to the environment (LOCALE_RITE_MODE); the selftest passes it explicitly so it
    fixes both modes without touching os.environ, and proves the default through a subprocess.
    """
    if check is None:
        return None
    tool_name = payload.get("tool_name") or ""
    if tool_name not in WRITE_TOOLS:
        return None
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return None
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not isinstance(file_path, str) or not file_path:
        return None
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()
    # In doubt the hook informs and never denies: a payload with no event name, or one this hook does
    # not know, is treated as the event that follows the write.
    pre = payload.get("hook_event_name") == PRE_EVENT
    text = written_text(tool_name, tool_input)
    anchor = (tool_input.get("old_string") or "") if (pre and tool_name == "Edit") else text
    if not isinstance(anchor, str):
        anchor = ""
    kind = None
    if tool_name == "NotebookEdit":
        kind = "markdown" if tool_input.get("cell_type") == "markdown" else "python"
    try:
        findings = findings_for(check, file_path, text, cwd, anchor, pre=pre)
        findings.extend(prose_findings_for(load_prose(), file_path, text, cwd, anchor, check, kind=kind))
    except Exception:
        return None                      # a check that crashes must not crash the write
    if not findings:
        return None
    if not pre:
        return report(findings)
    if (mode if mode is not None else current_mode()) == MODE_INFORM:
        return None                      # the write lands; PostToolUse informs, as before #137
    gating, _ = split_findings(findings)
    return deny(findings) if gating else None


def selftest() -> int:
    check = load_check()
    if check is None:
        print(f"selftest FAILED: check not found at {CHECK_PATH}")
        return 1
    cwd = "/tmp/locale-rite-selftest"
    # The PostToolUse cases carry no hook_event_name on purpose: the payloads that reached this hook
    # before issue #137 must decide exactly as they did, so a missing event name is the advisory path.
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
        ("PostToolUse by name is the advisory envelope", True, {
            "hook_event_name": POST_EVENT, "tool_name": "Write", "cwd": cwd,
            "tool_input": {"file_path": f"{cwd}/orders/service.py",
                           "content": "def buscar_order(x):\n    return x\n"}}),
    ]
    failed = []
    for name, should_report, payload in cases:
        got = evaluate(payload, check)
        ok = bool(got) == should_report and (not got or "permissionDecision" not in got["hookSpecificOutput"])
        print(f"  {'OK     ' if ok else 'FAILED '} {name}")
        if not ok:
            failed.append(name)
    reported = evaluate(cases[0][2], check)
    shape_ok = (
        isinstance(reported, dict)
        and reported["hookSpecificOutput"]["hookEventName"] == POST_EVENT
        and isinstance(reported["hookSpecificOutput"]["additionalContext"], str)
        and len(reported["hookSpecificOutput"]["additionalContext"]) <= CONTEXT_CAP
    )
    print(f"  {'OK     ' if shape_ok else 'FAILED '} output shape is the field the harness reads (PostToolUse)")
    if not shape_ok:
        failed.append("output shape")

    # PreToolUse: `deny` is the denial envelope, None is silence, `advisory` is the PostToolUse
    # envelope (only reachable here when the event name is missing — kept out of this list on
    # purpose: a PreToolUse payload never gets the advisory shape, which the harness would drop).
    def pre(tool_input, tool_name="Write", cwd_=cwd, event=PRE_EVENT):
        return {"hook_event_name": event, "tool_name": tool_name, "cwd": cwd_, "tool_input": tool_input}

    pt_ident = {"file_path": f"{cwd}/orders/service.py", "content": "def buscar_order(x):\n    return x\n"}
    pre_cases = [
        ("PreToolUse denies a portuguese identifier", "deny", None, pre(pt_ident)),
        ("PreToolUse denies a portuguese path", "deny", None,
         pre({"file_path": f"{cwd}/servicos_pedido/shipping.py", "content": "x = 1\n"})),
        ("PreToolUse denies an Edit whose new_string is portuguese", "deny", None,
         pre({"file_path": f"{cwd}/orders/service.py", "old_string": "a", "new_string": "usuario_count = 1\n"},
             tool_name="Edit")),
        ("PreToolUse allows the same name with locale-ok on the line above", None, None,
         pre({"file_path": f"{cwd}/orders/service.py",
              "content": "# locale-ok: legacy wire name mirrored in the adapter\ndef buscar_order(x):\n    return x\n"})),
        ("PreToolUse allows a clean write", None, None,
         pre({"file_path": f"{cwd}/orders/shipping_cost.py", "content": "def compute_shipping(order_id):\n    return 0\n"})),
        ("PreToolUse in inform mode never denies", None, MODE_INFORM, pre(pt_ident)),
        ("PreToolUse with a misspelt mode still denies", "deny", "informar", pre(pt_ident)),
        ("PreToolUse ignores another tool", None, None,
         pre({"command": "ls servicos_pedido"}, tool_name="Bash")),
        ("PreToolUse ignores a payload without file_path", None, None, pre({})),
        ("PreToolUse ignores a tool_input that is not an object", None, None, pre("x")),
        ("PreToolUse ignores a file_path that is not a string", None, None, pre({"file_path": 42, "content": "a"})),
        ("PreToolUse with a cwd that is not a string still denies", "deny", None,
         pre(pt_ident, cwd_=42)),
    ]
    for name, expect, mode, payload in pre_cases:
        got = evaluate(payload, check, mode=mode)
        kind = None
        if got:
            kind = "deny" if got["hookSpecificOutput"].get("permissionDecision") == "deny" else "advisory"
        ok = kind == expect
        print(f"  {'OK     ' if ok else 'FAILED '} {name}")
        if not ok:
            failed.append(name)

    # inform mode: the same payload, on the event that follows the write, is the advisory as before.
    post_inform = evaluate({**pre(pt_ident), "hook_event_name": POST_EVENT}, check, mode=MODE_INFORM)
    ok = bool(post_inform) and "additionalContext" in post_inform["hookSpecificOutput"]
    print(f"  {'OK     ' if ok else 'FAILED '} inform mode: PostToolUse still carries the advisory")
    if not ok:
        failed.append("inform mode PostToolUse")

    # en-unknown alone never denies on PreToolUse, and is the advisory on PostToolUse. The token is
    # asserted to be an advisory-only finding first, so the case cannot pass on a clean write.
    unknown = {"file_path": f"{cwd}/orders/service.py", "content": "zqxbrv_count = 1\n"}
    gating, advisory = split_findings(findings_for(check, unknown["file_path"], unknown["content"], cwd, unknown["content"]))
    only_advisory = not gating and bool(advisory)
    pre_unknown = evaluate(pre(unknown), check)
    post_unknown = evaluate({**pre(unknown), "hook_event_name": POST_EVENT}, check)
    ok = only_advisory and pre_unknown is None and bool(post_unknown) and \
        "additionalContext" in post_unknown["hookSpecificOutput"]
    print(f"  {'OK     ' if ok else 'FAILED '} en-unknown alone: PreToolUse silent, PostToolUse advisory")
    if not ok:
        failed.append("en-unknown alone")

    # The allowlist is found from the payload's cwd, so the case builds one in a temporary tree and
    # never reads the allowlist of whoever runs the selftest.
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / check.ALLOWLIST_FILE).write_text("buscar_order\n", encoding="utf-8")
        allowed = pre({"file_path": f"{tmp}/orders/service.py", "content": "def buscar_order(x):\n    return x\n"}, cwd_=tmp)
        ok = evaluate(allowed, check) is None and evaluate({**allowed, "hook_event_name": POST_EVENT}, check) is None
        print(f"  {'OK     ' if ok else 'FAILED '} PreToolUse allows a name listed in {check.ALLOWLIST_FILE} of the cwd")
        if not ok:
            failed.append("allowlist")

    # A file that already exists is never denied for its own name (D8), and a waiver already in the
    # file on the line above the edited fragment counts (D9). Both need a real file, built in a
    # temporary tree; both were review findings on the first version of this mode.
    with tempfile.TemporaryDirectory() as tmp:
        legacy = Path(tmp) / "servico_pedido.py"
        legacy.write_text("total = 0\n", encoding="utf-8")
        edit = {"file_path": str(legacy), "old_string": "total = 0", "new_string": "total = 1\n"}
        pre_edit = evaluate(pre(edit, tool_name="Edit", cwd_=tmp), check)
        post_edit = evaluate({**pre(edit, tool_name="Edit", cwd_=tmp), "hook_event_name": POST_EVENT}, check)
        ok = pre_edit is None and bool(post_edit) and "servico_pedido" in post_edit["hookSpecificOutput"]["additionalContext"]
        print(f"  {'OK     ' if ok else 'FAILED '} PreToolUse allows a clean Edit on a legacy portuguese-named file; PostToolUse still reports the path")
        if not ok:
            failed.append("legacy path edit")
        pt_edit = {**edit, "new_string": "usuario_count = 1\n"}
        denied = evaluate(pre(pt_edit, tool_name="Edit", cwd_=tmp), check)
        reason = denied["hookSpecificOutput"]["permissionDecisionReason"] if denied else ""
        ok = "1 non-English name " in reason and "usuario_count" in reason and "path-pt-noun" not in reason
        print(f"  {'OK     ' if ok else 'FAILED '} PreToolUse denies the identifier in that Edit and names only the identifier, not the legacy path")
        if not ok:
            failed.append("legacy path identifier")
        overwrite = evaluate(pre({"file_path": str(legacy), "content": "total = 2\n"}, cwd_=tmp), check)
        fresh = evaluate(pre({"file_path": f"{tmp}/novo_servico.py", "content": "total = 2\n"}, cwd_=tmp), check)
        ok = overwrite is None and bool(fresh) and fresh["hookSpecificOutput"].get("permissionDecision") == "deny"
        print(f"  {'OK     ' if ok else 'FAILED '} PreToolUse allows a clean Write over the legacy file and still denies the Write that creates a portuguese path")
        if not ok:
            failed.append("legacy path write")
        two = Path(tmp) / "two.py"
        two.write_text("a = 1\n# locale-ok: wire name from the legacy adapter\nb = 2\n", encoding="utf-8")
        waived = {"file_path": str(two), "old_string": "b = 2", "new_string": "usuario = 2"}
        pre_waived = evaluate(pre(waived, tool_name="Edit", cwd_=tmp), check)
        two.write_text("a = 1\n# locale-ok: wire name from the legacy adapter\nusuario = 2\n", encoding="utf-8")
        post_waived = evaluate({**pre(waived, tool_name="Edit", cwd_=tmp), "hook_event_name": POST_EVENT}, check)
        two.write_text("a = 1\nb = 2\n", encoding="utf-8")
        unwaived = evaluate(pre(waived, tool_name="Edit", cwd_=tmp), check)
        ok = pre_waived is None and post_waived is None and bool(unwaived) \
            and unwaived["hookSpecificOutput"].get("permissionDecision") == "deny"
        print(f"  {'OK     ' if ok else 'FAILED '} locale-ok already in the file above old_string: PreToolUse silent, PostToolUse silent, denied without it")
        if not ok:
            failed.append("waiver above the fragment")

    # ── The prose direction (issue #179): measured only where .code-locale declares it ──
    # Each tree carries its own `.git` so the declaration walk stops there and never reaches the
    # runner's repository; the second tree declares nothing and must decide exactly as before.
    prose = load_prose()
    prose_ok = prose is not None
    print(f"  {'OK     ' if prose_ok else 'FAILED '} prose detector loads from {PROSE_CHECK_PATH.name}")
    if not prose_ok:
        failed.append("prose detector missing")
    en_comment = "# compute the total for the order and apply the discount before saving\ntotal = 0\n"
    pt_comment = "# calcula o total do pedido e aplica o desconto antes de salvar\ntotal = 0\n"
    prose_decisions = 0
    with tempfile.TemporaryDirectory() as declared, tempfile.TemporaryDirectory() as silent:
        for tree in (declared, silent):
            (Path(tree) / ".git").mkdir()
            (Path(tree) / "orders").mkdir()
        (Path(declared) / prose.DECLARATION_FILE).write_text("prose: pt-BR\n", encoding="utf-8")

        def prose_case(name, expect, payload, mode=None):
            nonlocal prose_decisions
            prose_decisions += 1
            got = evaluate(payload, check, mode=mode)
            kind = None
            if got:
                kind = "deny" if got["hookSpecificOutput"].get("permissionDecision") == "deny" else "advisory"
            ok = kind == expect
            print(f"  {'OK     ' if ok else 'FAILED '} {name}")
            if not ok:
                failed.append(name)
            return got

        py = f"{declared}/orders/total.py"
        denied = prose_case("prose: PreToolUse denies an English comment where .code-locale says pt-BR", "deny",
                            pre({"file_path": py, "content": en_comment}, cwd_=declared))
        reason = denied["hookSpecificOutput"]["permissionDecisionReason"] if denied else ""
        named = (reason.startswith("CODE-LOCALE: write denied — 1 comment or docstring not in the repository's prose language (pt")
                 and "orders/total.py:1: comment reads as en, repo prose is pt" in reason
                 and PROSE_EXIT in reason and reason.endswith(EXITS[-1])
                 and reason.count("\n") + 1 <= REASON_LINE_CAP and len(reason) <= REASON_CAP)
        print(f"  {'OK     ' if named else 'FAILED '} prose: the reason names the line, the fragment, both languages and four exits")
        if not named:
            failed.append("prose reason")
        prose_case("prose: PreToolUse lets a Portuguese comment through", None,
                   pre({"file_path": py, "content": pt_comment}, cwd_=declared))
        prose_case("prose: locale-ok on the line above the comment lands in silence", None,
                   pre({"file_path": py, "content": "# locale-ok: upstream comment kept verbatim\n" + en_comment}, cwd_=declared))
        prose_case("prose: PreToolUse denies an English docstring", "deny",
                   pre({"file_path": py, "content": '"""Load the model once and keep it warm for the next requests."""\nx = 1\n'}, cwd_=declared))
        prose_case("prose: a short technical comment is not a finding", None,
                   pre({"file_path": py, "content": "# TODO: fix lru_cache\ntotal = 0\n"}, cwd_=declared))
        md = {"file_path": f"{declared}/NOTES.md",
              "content": "This paragraph explains how the order total is computed for the customer.\n"}
        prose_case("prose: PreToolUse never denies a Markdown paragraph", None, pre(md, cwd_=declared))
        post_md = prose_case("prose: PostToolUse reports the Markdown paragraph as advisory", "advisory",
                             {**pre(md, cwd_=declared), "hook_event_name": POST_EVENT})
        ctx = post_md["hookSpecificOutput"]["additionalContext"] if post_md else ""
        md_ok = "[advisory] paragraph reads as en" in ctx and ctx.startswith("CODE-LOCALE (advisory)")
        print(f"  {'OK     ' if md_ok else 'FAILED '} prose: the advisory names the paragraph and never the deny header")
        if not md_ok:
            failed.append("prose md advisory")
        prose_case("prose: inform mode never denies the English comment", None,
                   pre({"file_path": py, "content": en_comment}, cwd_=declared), mode=MODE_INFORM)
        # An Edit anchors the finding at the replaced fragment's line, as the identifier tier does.
        target = Path(declared) / "orders" / "edit.py"
        target.write_text("x = 1\ny = 2\n", encoding="utf-8")
        edited = prose_case("prose: an Edit whose new_string adds an English comment is denied", "deny",
                            pre({"file_path": str(target), "old_string": "y = 2",
                                 "new_string": "# compute the total for the order and apply the discount\ny = 2"},
                                tool_name="Edit", cwd_=declared))
        line_ok = bool(edited) and "orders/edit.py:2: comment reads as en" in edited["hookSpecificOutput"]["permissionDecisionReason"]
        print(f"  {'OK     ' if line_ok else 'FAILED '} prose: the Edit finding carries the file line of old_string")
        if not line_ok:
            failed.append("prose edit line")
        # A notebook cell: `.ipynb` has no suffix entry, so the tool names the kind.
        nb = f"{declared}/orders/nb.ipynb"
        prose_case("prose: a NotebookEdit code cell with an English comment is denied",
                   "deny", pre({"notebook_path": nb, "new_source": en_comment, "cell_type": "code"}, tool_name="NotebookEdit", cwd_=declared))
        prose_case("prose: a NotebookEdit markdown cell is advisory on PostToolUse, never denied", None,
                   pre({"notebook_path": nb, "new_source": md["content"], "cell_type": "markdown"}, tool_name="NotebookEdit", cwd_=declared))
        prose_case("prose: a NotebookEdit markdown cell reports on PostToolUse", "advisory",
                   {**pre({"notebook_path": nb, "new_source": md["content"], "cell_type": "markdown"}, tool_name="NotebookEdit", cwd_=declared),
                    "hook_event_name": POST_EVENT})
        # MultiEdit: the joined new_strings are measured; the line is inside the joined text (docstring).
        target.write_text("x = 1\ny = 2\nz = 3\n", encoding="utf-8")
        prose_case("prose: a MultiEdit whose second edit adds an English comment is denied", "deny",
                   pre({"file_path": str(target), "edits": [
                       {"old_string": "y = 2", "new_string": "y = 2"},
                       {"old_string": "z = 3", "new_string": "# compute the total for the order and apply the discount\nz = 3"}]},
                       tool_name="MultiEdit", cwd_=declared))
        # Both directions: an identifier AND a comment in one write share one reason.
        both = prose_case("prose: identifier and comment findings share one denial", "deny",
                          pre({"file_path": py, "content": en_comment.replace("total = 0", "usuario_count = 0")}, cwd_=declared))
        both_reason = both["hookSpecificOutput"]["permissionDecisionReason"] if both else ""
        both_ok = both_reason.startswith("CODE-LOCALE: write denied — 1 non-English name in the machine layer and 1 comment") \
            and "usuario_count" in both_reason and "comment reads as en" in both_reason
        print(f"  {'OK     ' if both_ok else 'FAILED '} prose: the combined header counts names and prose apart")
        if not both_ok:
            failed.append("prose combined header")
        # Silent tree: no declaration, so the English comment is exactly as invisible as before #179.
        silent_py = f"{silent}/orders/total.py"
        prose_case("prose: without .code-locale an English comment is not measured (PreToolUse)", None,
                   pre({"file_path": silent_py, "content": en_comment}, cwd_=silent))
        prose_case("prose: without .code-locale an English comment is not measured (PostToolUse)", None,
                   {**pre({"file_path": silent_py, "content": en_comment}, cwd_=silent), "hook_event_name": POST_EVENT})
        prose_case("prose: without .code-locale a Portuguese identifier is still denied", "deny",
                   pre({"file_path": silent_py, "content": "def buscar_order(x):\n    return x\n"}, cwd_=silent))
        # The reverse direction: prose: en and a Portuguese comment.
        (Path(declared) / prose.DECLARATION_FILE).write_text("prose: en\n", encoding="utf-8")
        prose_case("prose: under prose: en a Portuguese comment is denied", "deny",
                   pre({"file_path": py, "content": pt_comment}, cwd_=declared))
        prose_case("prose: under prose: en an English comment lands", None,
                   pre({"file_path": py, "content": en_comment}, cwd_=declared))
        # A declaration the detector cannot read leaves the write hook silent for prose.
        (Path(declared) / prose.DECLARATION_FILE).write_text("prose: klingon\n", encoding="utf-8")
        prose_case("prose: an unreadable declaration leaves the write hook silent for prose", None,
                   pre({"file_path": py, "content": en_comment}, cwd_=declared))
        # cwd fallback: a file outside any repository, judged by the cwd's declaration.
        (Path(declared) / prose.DECLARATION_FILE).write_text("prose: pt-BR\n", encoding="utf-8")
        with tempfile.TemporaryDirectory() as nowhere:
            outside, _boundary = prose.find_declaration(Path(nowhere))
            if outside is None and _boundary is None:
                prose_case("prose: a file outside any repository falls back to the cwd's declaration", "deny",
                           pre({"file_path": f"{nowhere}/total.py", "content": en_comment}, cwd_=declared))
            else:
                print("  SKIP    prose: cwd fallback (the temporary directory sits inside a repository or a declared tree)")

    # Denial envelope: the shape the 2.1.261 bundle parses, within both measured caps, each distinct
    # name once, the three exits at the end — on a write with 30 gating findings plus an advisory one.
    many = "\n".join(f"preco_{i} = {i}" for i in range(30)) + "\nzqxbrv_count = 1\n"
    denied = evaluate(pre({"file_path": f"{cwd}/orders/service.py", "content": many}), check)
    reason = denied["hookSpecificOutput"]["permissionDecisionReason"] if denied else ""
    deny_ok = (
        bool(denied)
        and denied["hookSpecificOutput"]["hookEventName"] == PRE_EVENT
        and denied["hookSpecificOutput"]["permissionDecision"] == "deny"
        and len(reason) <= REASON_CAP
        and reason.count("\n") + 1 <= REASON_LINE_CAP
        and reason.startswith("CODE-LOCALE: write denied — 30 non-English names")
        and reason.count("preco_0 ") == 1
        and "(+18 more" in reason
        and "(+1 unrecognised word, advisory" in reason
        and reason.endswith(EXITS[-1])
        and "locale-ok:" in reason and check.ALLOWLIST_FILE in reason and f"{MODE_ENV}={MODE_INFORM}" in reason
    )
    print(f"  {'OK     ' if deny_ok else 'FAILED '} denial envelope: PreToolUse shape, <= {REASON_CAP} chars, "
          f"<= {REASON_LINE_CAP} lines, three exits last")
    if not deny_ok:
        failed.append("denial envelope")
    # The issue's own example: preco on two lines is one line in the reason.
    issue = evaluate(pre({"file_path": f"{cwd}/servico_pedido.py",
                          "content": "def calcular_total(preco):\n    return preco\n"}), check)
    reason = issue["hookSpecificOutput"]["permissionDecisionReason"] if issue else ""
    distinct_ok = reason.startswith("CODE-LOCALE: write denied — 3 non-English names") and reason.count(" preco ") == 1
    print(f"  {'OK     ' if distinct_ok else 'FAILED '} denial reason names each distinct token once")
    if not distinct_ok:
        failed.append("distinct tokens")

    # The mode's default reads the environment; only the real entry point can prove that.
    raw = json.dumps(pre(pt_ident))
    env = {k: v for k, v in os.environ.items() if k != MODE_ENV}
    run_default = subprocess.run([sys.executable, __file__], input=raw, capture_output=True, text=True, env=env)
    run_inform = subprocess.run([sys.executable, __file__], input=raw, capture_output=True, text=True,
                                env={**env, MODE_ENV: MODE_INFORM})
    env_ok = (
        run_default.returncode == 0 and '"permissionDecision": "deny"' in run_default.stdout
        and run_inform.returncode == 0 and run_inform.stdout == "" and run_inform.stderr == ""
    )
    print(f"  {'OK     ' if env_ok else 'FAILED '} {MODE_ENV}={MODE_INFORM} read from the environment through stdin")
    if not env_ok:
        failed.append("environment mode")

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
    print(f"selftest OK: {len(cases)} PostToolUse decisions, {len(pre_cases)} PreToolUse decisions, "
          "inform mode, en-unknown, the allowlist, the legacy path, the waiver above the fragment, "
          f"both envelopes, the environment, the argv contract and {prose_decisions} prose decisions "
          "with and without .code-locale")
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
