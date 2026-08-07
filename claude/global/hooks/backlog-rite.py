#!/usr/bin/env python3
"""UserPromptSubmit hook — carries the backlog-first development rite into context.

Reads the hook payload on stdin and, when the prompt looks like a request to change
code, prints a short reminder that becomes additional context for the turn. Silent
otherwise: diagnosing, reading and answering are free.

Why a hook and not only a rule in personal-rules.md: the harness runs this on every
prompt, so enforcement does not depend on the assistant noticing a rule already in
context. It informs — it never blocks a tool call, and the user can always waive.

Wiring (~/.claude/settings.json):

    "hooks": {
      "UserPromptSubmit": [
        {"hooks": [{"type": "command",
                    "command": "python3 ~/ai-skills/claude/global/hooks/backlog-rite.py",
                    "timeout": 10}]}
      ]
    }

Like personal-rules.md, this is the maintainer's config — edit the signal list and the
reminder to match your own process instead of adopting it blindly.
"""

import json
import re
import sys

# Verbs and nouns that signal "code is about to change" (pt-BR + English).
CHANGE_SIGNALS = re.compile(
    r"\b("
    r"implementa\w*|implement\w*|"
    r"corrig\w*|conserta\w*|arruma\w*|resolv\w*|"
    r"refator\w*|refactor\w*|"
    r"adiciona\w*|acrescenta\w*|cria\w*|criar|add|"
    r"remov\w*|delet\w*|apaga\w*|drop|"
    r"ajusta\w*|altera\w*|muda\w*|troca\w*|atualiza\w*|change|update|"
    r"migra\w*|migrate|renomeia\w*|rename|"
    r"fix|bug|erro|error|falha|quebr\w*|broken|"
    r"feature|funcionalidade|endpoint|"
    r"melhora\w*|otimiza\w*|improve|optimi[sz]e"
    r")\b",
    re.IGNORECASE,
)

# Prompts already inside the rite, or explicitly opting out of it.
SKIP = re.compile(
    r"(^\s*/[a-z-]+"
    r"|sem\s+backlog|pula\s+o\s+rito|fora\s+do\s+rito|n[ãa]o\s+precisa\s+de\s+issue"
    r"|skip\s+the\s+(rite|backlog)|no\s+issue\s+needed)",
    re.IGNORECASE,
)

REMINDER = (
    "DEVELOPMENT RITE (backlog-first): this prompt looks like a request to change code. "
    "Before editing any file, the work becomes a backlog item: /backlog <idea> -> issue in the "
    "GitHub Project -> /execute-backlog <n> -> branch and PR with Closes #n. "
    "Diagnosing, reading and answering are free — the rite starts when code is going to change. "
    "Plan mode is NOT a shortcut: an approved plan still becomes an issue before the first edit. "
    "The user may waive this explicitly; without a waiver, ask before coding."
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    prompt = payload.get("prompt") or ""
    if not prompt or SKIP.search(prompt):
        return 0

    if CHANGE_SIGNALS.search(prompt):
        print(REMINDER)

    return 0


if __name__ == "__main__":
    sys.exit(main())
