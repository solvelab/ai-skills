#!/usr/bin/env python3
"""UserPromptSubmit hook — carries the anti-guessing (verify-before-claiming) rite into context.

Reads the hook payload on stdin and, when the prompt reads as a guess being caught or research
being demanded, prints a short reminder that becomes additional context for the turn. Silent
otherwise.

Why a hook and not only a rule in personal-rules.md: the harness runs this on every prompt, so
enforcement does not depend on the assistant noticing a rule already in context. It informs — it
never blocks a tool call, and the user can always waive.

KNOWN LIMIT: this hook fires on *corrections*, not on the guess itself. The moment worth
intercepting is internal to the model — "I am about to write a flag I have not read" — and no
prompt regex can see it. A per-turn preventive matcher was designed and rejected: every plausible
signal list (library, API, flag, version, "how do I") matches most technical prompts, and a
reminder that fires on every prompt stops being read, which would also degrade the backlog-rite.py
reminder sitting next to it in the same hook array. Preventive coverage lives in personal-rules.md
instead, which loads once per session and costs nothing per turn.

A PreToolUse variant on Edit/Write was also considered: it could parse transcript_path and flag
"about to write having read nothing this turn". That is a proxy, not a measurement — it
false-positives on legitimate new-file creation and false-negatives on "read one file, then invent
a flag" — and it couples the hook to an undocumented JSONL layout. Per
openspec/specs/skills-authoring ("Advisory mechanisms are not sold as hard gates"), a proxy is not
shipped as a detector.

This hook does not run in CI and does not run for a contributor who clones the repo without wiring
it. The gate that survives an unwired contributor is scripts/validate-rite.sh.

Wiring (~/.claude/settings.json) — alongside the backlog rite, in the same array:

    "hooks": {
      "UserPromptSubmit": [
        {"hooks": [
          {"type": "command",
           "command": "python3 ~/ai-skills/claude/global/hooks/backlog-rite.py", "timeout": 10},
          {"type": "command",
           "command": "python3 ~/ai-skills/claude/global/hooks/verify-rite.py", "timeout": 10}
        ]}
      ]
    }

Like personal-rules.md, this is the maintainer's config — edit the signal list and the reminder to
match your own process instead of adopting it blindly.

Modes: (default) read one payload from stdin   |   --selftest assert the decisions against synthetic payloads.

WHAT THE SELFTEST DOES NOT COVER: the harness's real payload is not reproduced — only the one
field this hook reads (`prompt`) is fed to `evaluate()`. That the harness still sends it under that
name is a premise of the pinned docs (code.claude.com/docs/en/hooks), not something the selftest
measures. The KNOWN LIMIT above is not measurable by any selftest: no case here can assert that a
guess was caught before it was written, because the hook itself cannot see that moment.
"""

import io
import json
import re
import sys

# Phrases that signal "a guess was just caught, or research is being demanded" (pt-BR + English).
# Deliberately narrow: these are corrections, which are rare and unambiguous. Widening this list
# to preventive signals is what the KNOWN LIMIT above rejects.
GUESS_SIGNALS = re.compile(
    r"("
    r"\bachismo\b|\bachi[sm]\w*\b|\bchut(e|ou|ando|ar|ei)\b|\bpalpite\b|"
    r"\b(voc[êe]\s+)?inventou\b|\bn[ãa]o\s+invent[ae]\b|\bt[áa]\s+inventando\b|\binventad[oa]\b|"
    r"\bde\s+onde\s+(voc[êe]\s+)?tirou\b|\bonde\s+(voc[êe]\s+)?viu\b|\bfonte\s+diss[oe]\b|"
    r"\bcad[êe]\s+a\s+fonte\b|\bpesquis(a|e|ou|ar)\s+(antes|primeiro|isso)\b|"
    r"\bn[ãa]o\s+pesquisou\b|\bdocumenta[çc][ãa]o\s+oficial\b|\bl[êe]\s+a\s+doc\b|"
    # "essa opção não existe" / "esse parâmetro não existe": one optional noun between the
    # demonstrative and the negation, which is the ordinary shape in pt-BR.
    r"\bn[ãa]o\s+existe\s+(ess[ae]|iss[oe])\b|\b(ess[ae]|iss[oe])\s+(\w+\s+)?n[ãa]o\s+existe\b|"
    r"\bfora\s+do\s+(escopo|roteiro)\b|\bn[ãa]o\s+foi\s+isso\s+que\s+eu\s+pedi\b|"
    r"\bn[ãa]o\s+pedi\s+isso\b|"
    r"\byou\s+(just\s+)?(made\s+(that|it)\s+up|invented|hallucinat\w+)\b|"
    r"\b(stop|don'?t|do\s+not)\s+guess\w*\b|\bno\s+guess\w*\b|\bstop\s+assuming\b|"
    r"\bwhere\s+did\s+you\s+(get|see|find|read)\s+(that|this|it)\b|"
    r"\bcite\s+(the\s+|your\s+)?sources?\b|\bwhat'?s\s+your\s+source\b|"
    r"\b(read|check)\s+the\s+(docs|source|manual|changelog)\b|\bresearch\s+(it|this|first)\b|"
    r"\b(that|this)\s+(flag|option|param\w*|method|field|api|key|arg\w*)\s+does\s?n[o']?t\s+exist\b|"
    r"\bout\s+of\s+scope\b|\b(that'?s|this\s+is)\s+not\s+what\s+I\s+asked\b|"
    r"\bI\s+did\s?n[o']?t\s+ask\s+for\s+(that|this)\b"
    r")",
    re.IGNORECASE,
)

# Only explicit waivers silence it. Unlike backlog-rite.py this does NOT skip slash commands:
# a correction typed inside a slash command still deserves the reminder.
SKIP = re.compile(
    r"(de\s+cabe[çc]a|sem\s+pesquisar|n[ãa]o\s+precisa\s+(pesquisar|verificar|checar)|"
    r"pode\s+chutar|chuta\s+mesmo|"
    r"from\s+memory\s+is\s+fine|no\s+need\s+to\s+(research|check|verify)|"
    r"(a\s+)?guess\s+is\s+(ok|fine)|just\s+guess)",
    re.IGNORECASE,
)

REMINDER = (
    "GROUNDING RITE (verify-before-claiming): this prompt reads as a guess being caught or research "
    "being demanded. Before the next answer or edit, research in cheapest-first order — this "
    "session's context, this repo, the installed dependency source (the lockfile decides the "
    "version), the tool itself (--help / --version / --dry-run), docs pinned to that version, web "
    "search, then ask. Stop at the first rung that answers. "
    "Label every load-bearing claim with its source (file:line, the command and its output line, or "
    "the URL plus the version it documents) or explicitly as inferred. "
    "If the fact is not found, say so and list the commands you ran and the rungs you could not "
    "reach — never substitute a plausible answer. "
    "Your memory of a library API is a hypothesis dated at your cutoff; the lockfile wins. "
    "Scope: do only what was asked; adjacent improvements are proposed, not performed."
)


def read_payload(stream) -> "dict | None":
    """One JSON object from the stream, or None for anything the hook must ignore.

    A payload that is not an object (`[]`, `"x"`, `null`, empty stdin) is not a hook event this
    script can read, and a hook that crashes on it costs the turn it was meant to inform.
    """
    try:
        payload = json.load(stream)
    except (json.JSONDecodeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def evaluate(payload: dict) -> "str | None":
    """The whole decision, isolated from stdin and stdout so the selftest can drive it."""
    prompt = payload.get("prompt") or ""
    if not isinstance(prompt, str) or not prompt or SKIP.search(prompt):
        return None
    if not GUESS_SIGNALS.search(prompt):
        return None
    return REMINDER


def selftest() -> int:
    failed = []
    cases = [
        ("portuguese caught guess fires", True, {"prompt": "isso é achismo"}),
        ("english demand for a source fires", True, {"prompt": "where did you see that"}),
        ("'essa flag não existe' fires", True, {"prompt": "essa flag não existe, lê a doc"}),
        ("'that's not what I asked' fires", True, {"prompt": "that's not what I asked for"}),
        # Deliberately the opposite of backlog-rite.py: a correction typed inside a slash command
        # still deserves the reminder (see the comment above SKIP). A future "harmonisation" of
        # the two hooks must break this case, not silently erase the difference.
        ("correction inside a slash command still fires", True,
         {"prompt": "/backlog você inventou essa flag"}),
        ("waiver 'pode chutar' is silent", False, {"prompt": "pode chutar, de onde tirou isso?"}),
        ("waiver 'from memory is fine' is silent", False,
         {"prompt": "from memory is fine, where did you see that?"}),
        ("implementation request is silent", False, {"prompt": "implementa o endpoint"}),
        ("neutral question is silent", False, {"prompt": "o que é um hook?"}),
        ("empty prompt is silent", False, {"prompt": ""}),
        ("payload without prompt is silent", False, {}),
        ("prompt that is not a string is silent", False, {"prompt": 42}),
    ]
    for name, should_fire, payload in cases:
        got = evaluate(payload)
        ok = bool(got) == should_fire
        print(f"  {'OK     ' if ok else 'FAILED '} {name}")
        if not ok:
            failed.append(name)

    # The harness reads plain stdout for UserPromptSubmit: what fires must be the reminder text.
    fired = evaluate(cases[0][2])
    shape_ok = isinstance(fired, str) and fired.startswith("GROUNDING RITE")
    print(f"  {'OK     ' if shape_ok else 'FAILED '} output shape is the reminder the harness reads")
    if not shape_ok:
        failed.append("output shape")

    # Malformed payloads are ignored, never raised on (issue #115: `[]`, `"x"`, empty stdin).
    malformed = [("json array", "[]"), ("json string", '"x"'), ("empty stdin", ""),
                 ("json null", "null"), ("json number", "42"), ("not json", "{not json")]
    for name, raw in malformed:
        ok = read_payload(io.StringIO(raw)) is None
        print(f"  {'OK     ' if ok else 'FAILED '} malformed payload is ignored: {name}")
        if not ok:
            failed.append(f"malformed: {name}")
    well_formed = read_payload(io.StringIO('{"prompt": "x"}'))
    ok = well_formed == {"prompt": "x"}
    print(f"  {'OK     ' if ok else 'FAILED '} well-formed payload is read")
    if not ok:
        failed.append("well-formed payload")

    print()
    if failed:
        print("selftest FAILED: " + "; ".join(failed))
        return 1
    print(f"selftest OK: {len(cases)} decisions, {len(malformed)} malformed payloads, plus the output shape")
    return 0


def main() -> int:
    if "--selftest" in sys.argv[1:]:
        return selftest()
    payload = read_payload(sys.stdin)
    if payload is None:
        return 0
    result = evaluate(payload)
    if result:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
