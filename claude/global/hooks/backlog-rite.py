#!/usr/bin/env python3
"""UserPromptSubmit hook — carries the backlog-first development rite into context.

Reads the hook payload on stdin and, when the prompt looks like a request to change
code, prints a short reminder that becomes additional context for the turn. Silent
otherwise: diagnosing, reading and answering are free.

Where the working directory runs a spec-driven workflow, the reminder gains one extra
sentence naming that workflow's gate. It is conditional on purpose: a reminder that
fires everywhere stops being read, which would also cost the backlog sentence next to
it. The payload's `cwd` is a documented field common to every hook event; os.getcwd()
is the fallback for the case where it is missing.

Why a hook and not only a rule in personal-rules.md: the harness runs this on every
prompt, so enforcement does not depend on the assistant noticing a rule already in
context. It informs — it never blocks a tool call, and the user can always waive.

ACCEPTED FALSE POSITIVE: a diagnostic question that contains a change word — "por que o
teste falha?", "why does the build fail?", "como corrijo esse bug?" — fires. The matcher is
deliberately generous: a false positive costs one line of context, a false negative
costs traceability, and the injected text itself says diagnosis is free. Decided in
openspec/changes/archive/2026-08-07-add-backlog-first-rite/design.md:32 and :78; fixed
below as a self-test case that FIRES, so a well-meant "fix" breaks the test and reads the
reason first. A question-shape exclusion was measured and rejected: it silences real
requests ("por que não implementa o endpoint de login?") and does not remove the class it
aims at ("como corrijo esse bug?" still fires).

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

Modes: (default) read one payload from stdin   |   --selftest assert the decisions against synthetic payloads.

WHAT THE SELFTEST DOES NOT COVER: the harness's real payload is not reproduced — only the
two fields this hook reads (`prompt`, `cwd`) are fed to `evaluate()`. That the harness still
sends those fields under those names is a premise of the pinned docs
(code.claude.com/docs/en/hooks), not something the selftest measures. The `openspec/`
fixture lives in a temporary directory and every case passes it as `cwd`; the two cases that
exercise the os.getcwd() fallback move the process cwd into that fixture for the duration of the
call and restore it afterwards, so the selftest never stats the real cwd and its result does not
depend on where it runs.
"""

import contextlib
import io
import json
import os
import re
import sys
import tempfile

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
    # `fail(s|ed|ing)?` is the verb's four forms and nothing else: `fail\w*` was measured firing
    # on failover / failsafe / failure, concept nouns that are questions, not change requests.
    r"fix|bug|erro|error|falha|fail(s|ed|ing)?|quebr\w*|broken|"
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

# Appended only where the workflow exists. Naming a gate that is not there would teach a step the
# repo does not have, and would spend the reminder's credibility on noise.
SPEC_RITE = (
    " This repo runs a spec-driven rite (openspec/): the item also becomes an OpenSpec change, "
    "validated with `openspec validate <id> --strict`, BEFORE the first edit outside openspec/. "
    "Skipping it needs a written waiver, not a silent judgement."
)

# Directory that marks the workflow. One name, checked literally — guessing at variants would be
# the same achismo the rite exists to stop.
SPEC_RITE_DIR = "openspec"


def has_spec_rite(payload: dict) -> bool:
    # A `cwd` that is missing, empty or not a string falls back to the process cwd: the field is
    # read from untrusted JSON, and os.path.join on a non-string would cost the turn.
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()
    return os.path.isdir(os.path.join(cwd, SPEC_RITE_DIR))


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
    if not CHANGE_SIGNALS.search(prompt):
        return None
    reminder = REMINDER
    if has_spec_rite(payload):
        reminder += SPEC_RITE
    return reminder


@contextlib.contextmanager
def process_cwd(path: "str | None"):
    """Run the block with the process cwd moved to `path` (no-op for None), always restoring it."""
    if path is None:
        yield
        return
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def selftest() -> int:
    failed = []
    with tempfile.TemporaryDirectory() as td:
        with_rite = os.path.join(td, "with-rite")
        without_rite = os.path.join(td, "without-rite")
        os.makedirs(os.path.join(with_rite, SPEC_RITE_DIR))
        os.makedirs(without_rite)

        # (name, should_fire, payload, spec_sentence) — spec_sentence is None when the case does
        # not care whether the SPEC_RITE sentence is appended, True/False when it must/must not be.
        cases = [
            ("change request fires", True,
             {"prompt": "implementa o endpoint de login", "cwd": without_rite}, False),
            ("english change request fires", True,
             {"prompt": "add a retry to the http client", "cwd": without_rite}, False),
            ("cwd with openspec/ appends the spec sentence", True,
             {"prompt": "implementa o endpoint de login", "cwd": with_rite}, True),
            ("cwd without openspec/ omits the spec sentence", True,
             {"prompt": "implementa o endpoint de login", "cwd": without_rite}, False),
            # ACCEPTED TRADE-OFF, not a defect: a diagnostic question containing a change word
            # fires. openspec/changes/archive/2026-08-07-add-backlog-first-rite/design.md:32
            # ("the matcher is deliberately generous") and :78 ("accepted deliberately: the
            # injected text says diagnosis is free"). Turning this case to False reverts a
            # recorded decision — read the design first.
            ("diagnostic question containing 'falha' fires (accepted trade-off)", True,
             {"prompt": "por que o teste falha?", "cwd": without_rite}, False),
            ("english 'fail' (verb forms fail/fails/failed/failing) fires", True,
             {"prompt": "why does the build fail?", "cwd": without_rite}, False),
            ("english 'failing' fires", True,
             {"prompt": "the tests are failing", "cwd": without_rite}, False),
            # Fixes the narrowing: a concept noun that merely starts with "fail" is not a change
            # request. Widening to `fail\w*` must break this case, not silently fire here.
            ("english noun 'failover' is silent", False,
             {"prompt": "what is a failover cluster?", "cwd": without_rite}, None),
            # The prompt carries a change word on purpose: silence can then only come from the
            # slash-command SKIP rule. "/backlog nova ideia" has no signal and stays silent even
            # with that rule deleted — it never exercised the decision it was named for.
            ("slash command carrying a change word is silent", False,
             {"prompt": "/execute-backlog 12 implementa o endpoint", "cwd": with_rite}, None),
            ("waiver 'sem backlog' is silent", False,
             {"prompt": "faz isso sem backlog, corrige o typo", "cwd": with_rite}, None),
            ("neutral question is silent", False,
             {"prompt": "o que é um hook?", "cwd": with_rite}, None),
            ("empty prompt is silent", False, {"prompt": "", "cwd": with_rite}, None),
            ("payload without prompt is silent", False, {"cwd": with_rite}, None),
            ("prompt that is not a string is silent", False, {"prompt": 42, "cwd": with_rite}, None),
            # The fallback for a malformed cwd is os.getcwd(). A fifth field moves the process cwd
            # into the named fixture for the call (restored right after), so the fallback is measured
            # against both fixtures instead of the real cwd (TR1) — and a fallback that ignored the
            # process cwd, or always omitted the sentence, would fail one of the two.
            ("cwd that is not a string falls back to the process cwd (with openspec/)", True,
             {"prompt": "implementa o endpoint", "cwd": 42}, True, with_rite),
            ("cwd that is not a string falls back to the process cwd (without openspec/)", True,
             {"prompt": "implementa o endpoint", "cwd": 42}, False, without_rite),
        ]
        for name, should_fire, payload, spec_sentence, *rest in cases:
            with process_cwd(rest[0] if rest else None):
                got = evaluate(payload)
            ok = bool(got) == should_fire
            if ok and got and spec_sentence is not None:
                ok = (SPEC_RITE in got) == spec_sentence
            print(f"  {'OK     ' if ok else 'FAILED '} {name}")
            if not ok:
                failed.append(name)

        # The harness reads plain stdout for UserPromptSubmit: what fires must be the reminder text.
        fired = evaluate(cases[0][2])
        shape_ok = isinstance(fired, str) and fired.startswith("DEVELOPMENT RITE")
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
    args = sys.argv[1:]
    if args == ["--selftest"]:
        return selftest()
    if args:
        # An unknown argument must not fall through to the stdin path: a misspelt flag in a CI
        # step would then read empty stdin and exit 0 — the silent no-op the selftest mode exists
        # to make impossible.
        print(f"usage: {sys.argv[0]} [--selftest]", file=sys.stderr)
        return 2
    payload = read_payload(sys.stdin)
    if payload is None:
        return 0
    result = evaluate(payload)
    if result:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
