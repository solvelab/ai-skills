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
"""

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


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    prompt = payload.get("prompt") or ""
    if not prompt or SKIP.search(prompt):
        return 0

    if GUESS_SIGNALS.search(prompt):
        print(REMINDER)

    return 0


if __name__ == "__main__":
    sys.exit(main())
