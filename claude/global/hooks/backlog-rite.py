#!/usr/bin/env python3
"""UserPromptSubmit hook — carries the backlog-first development rite into context.

Reads the hook payload on stdin and, when the prompt looks like a request to change
code, prints a short reminder that becomes additional context for the turn. Silent
otherwise: diagnosing, reading and answering are free.

Where the work runs a spec-driven workflow, the reminder gains one extra sentence naming
that workflow's gate. The workflow is looked for where the work belongs, not in the working
directory alone (requirement "The development rite is enforced outside the model's
discretion", openspec/specs/skills-catalog/spec.md):

- inside a repository, at any depth: in the working directory and in every directory above
  it up to the repository's root — the first directory holding `.git`, a directory or a
  file (a linked work tree, a submodule), found by stat and never by calling git. The
  nearest `openspec/` counts, which is how the openspec CLI resolves its own root
  (findRepoPlanningRootSync, @fission-ai/openspec 1.6.0), stopped here at the root;
- outside any repository, a working directory that holds `openspec/` itself keeps the
  sentence: the workflow does not require git;
- at a workspace root — outside any repository, with repositories as its direct
  subdirectories, the backlog skill's definition — one sentence names the children whose
  root holds `openspec/`, and only them, with no sentence when none does.

It is conditional on purpose: a reminder that fires everywhere stops being read, which
would also cost the backlog sentence next to it. The payload's `cwd` is a documented field
common to every hook event; os.getcwd() is the fallback for the case where it is missing.

KNOWN LIMIT: one workspace level only, and the workspace's own list (`workspace.repos` in
its backlog.yml) is not read — every direct child holding `.git` counts, hidden ones
included. From inside one repository, another repository the work targets is not looked
at. A `.git` file whose gitdir is gone still marks a root, where git itself answers "not a
git repository". A workspace root that holds `openspec/` itself gets the repository sentence and
its children are not named (the branch order of design.md D3).

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
(code.claude.com/docs/en/hooks), not something the selftest measures. Every fixture lives in a
temporary directory and every case passes one as `cwd`; each fixture that stands for a repository
carries a `.git` marker, so the walk stops inside the temporary directory and the result does not
depend on where the selftest runs. The two cases that exercise the os.getcwd() fallback move the
process cwd into a fixture for the duration of the call and restore it afterwards, so the selftest
never stats the real cwd. The cases that need a directory outside any repository — a workspace
root with and without a child that runs the workflow, one with a symlink loop beside a child, one
that holds `openspec/` itself, and a directory outside any repository that holds `openspec/` —
check that the temporary directory sits outside one and print SKIP with the reason when it does
not, instead of passing or failing on the runner's layout. The `.git` file
fixture holds a gitdir line nothing reads: no real linked work tree or submodule is built, because
the hook never asks git.
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

# The workspace root's form: one sentence naming every child repo that runs the workflow, and no
# other. The change is created and validated inside that child, because the openspec CLI takes no
# path and, run from the workspace root, answers "No active changes found.".
WORKSPACE_SPEC_RITE = (
    " Repos in this workspace that run a spec-driven rite (openspec/): {names}. For work in one of "
    "them, the item also becomes an OpenSpec change, created and validated with "
    "`openspec validate <id> --strict` inside THAT repo, BEFORE the first edit outside its "
    "openspec/. Skipping it needs a written waiver, not a silent judgement."
)

# Directory that marks the workflow. One name, checked literally — guessing at variants would be
# the same achismo the rite exists to stop.
SPEC_RITE_DIR = "openspec"


def find_repo_root(start: str) -> "str | None":
    """The first directory holding `.git` at or above `start` (resolved), or None outside any repo.

    `.git` is a directory in a plain clone and a file in a linked work tree or a submodule, so both
    count. A stat per level answers it: a UserPromptSubmit hook does not start a git process to
    learn what the filesystem already says.
    """
    # lean: the same walk lives in locale-rite.py -> extract one helper when a third caller appears
    here = os.path.realpath(start)
    while not os.path.exists(os.path.join(here, ".git")):
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent
    return here


def child_repos(directory: str) -> "list[str]":
    """Names of the direct subdirectories of `directory` that hold `.git`, sorted by name.

    The backlog skill's workspace: a directory whose subdirectories are git repos. One level only,
    hidden directories included, sorted so the sentence is the same on every run; a directory that
    cannot be listed has no children.
    """
    # lean: every child holding .git counts -> read workspace.repos from backlog.yml when a foreign
    # clone named by the sentence is reported as noise
    try:
        with os.scandir(directory) as entries:
            names = []
            for entry in entries:
                try:
                    if entry.is_dir() and os.path.exists(os.path.join(entry.path, ".git")):
                        names.append(entry.name)
                except OSError:
                    continue             # a symlink loop or an unreadable target hides only itself
            return sorted(names)
    except (OSError, ValueError):
        return []


def spec_sentence(payload: dict) -> "str | None":
    """The spec sentence the reminder carries, or None. Four branches, in this order:

    1. inside a repository: SPEC_RITE when the working directory or a directory above it, up to and
       including the root, holds openspec/ (the nearest counts), else None;
    2. outside any repository, the working directory holds openspec/ itself: SPEC_RITE, as before;
    3. outside any repository, child repositories hold openspec/ at their root: WORKSPACE_SPEC_RITE
       naming them, and only them;
    4. otherwise None, as before.
    """
    # A `cwd` that is missing, empty or not a string falls back to the process cwd: the field is
    # read from untrusted JSON, and os.path.join on a non-string would cost the turn. A path no
    # directory can have (an embedded NUL) gets no sentence, as it did when the only probe was
    # isdir: realpath raises on it, as os.getcwd() does when the process cwd was deleted.
    cwd = payload.get("cwd")
    try:
        here = os.path.realpath(cwd if isinstance(cwd, str) and cwd else os.getcwd())
    except (OSError, ValueError):
        return None
    root = find_repo_root(here)
    if root is not None:
        while not os.path.isdir(os.path.join(here, SPEC_RITE_DIR)):
            if here == root or os.path.dirname(here) == here:
                return None
            here = os.path.dirname(here)
        return SPEC_RITE
    if os.path.isdir(os.path.join(here, SPEC_RITE_DIR)):
        return SPEC_RITE
    running = [name for name in child_repos(here)
               if os.path.isdir(os.path.join(here, name, SPEC_RITE_DIR))]
    return WORKSPACE_SPEC_RITE.format(names=", ".join(running)) if running else None


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
    sentence = spec_sentence(payload)
    if sentence:
        reminder += sentence
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
    skipped = []
    with tempfile.TemporaryDirectory() as td:
        # Every fixture that stands for a repository carries `.git`, so the walk stops inside the
        # temporary directory and no case depends on where the selftest runs. `workspace`,
        # `workspace-none`, `workspace-loop`, `workspace-own` and `loose` carry none on purpose:
        # they stand for directories outside any repository. In `workspace`, `api` and `docs` run
        # the workflow, `web` is a repo that does not, and `notes` holds openspec/ without being a
        # repo, so only the first two may be named.
        for relative in ("with-rite/.git", "with-rite/openspec", "with-rite/src/deep",
                         "without-rite/.git", "without-rite/src/deep",
                         "mono/.git", "mono/packages/app/openspec", "mono/packages/app/src",
                         "linked/openspec", "linked/pkg",
                         "outer/.git", "outer/openspec", "outer/inner/.git",
                         "outer/inner/sub/.git", "outer/inner/sub/openspec",
                         "workspace/api/.git", "workspace/api/openspec",
                         "workspace/docs/.git", "workspace/docs/openspec",
                         "workspace/web/.git", "workspace/notes/openspec",
                         "workspace-none/web/.git", "workspace-none/notes/openspec",
                         "workspace-loop/api/.git", "workspace-loop/api/openspec",
                         "workspace-own/openspec", "workspace-own/api/.git",
                         "workspace-own/api/openspec",
                         "loose/openspec"):
            os.makedirs(os.path.join(td, relative))
        # A symlink to itself: stat on it raises ELOOP, not ENOENT, so DirEntry.is_dir() raises
        # instead of answering False. It must hide only itself, never the child beside it.
        os.symlink("loop", os.path.join(td, "workspace-loop", "loop"))
        # A linked work tree and a submodule mark their root with a `.git` FILE. The gitdir it
        # names does not exist: the hook never asks git, so nothing reads it.
        with open(os.path.join(td, "linked", ".git"), "w", encoding="utf-8") as marker:
            marker.write("gitdir: /nowhere/.git/worktrees/linked\n")
        with_rite = os.path.join(td, "with-rite")
        without_rite = os.path.join(td, "without-rite")
        login = "implementa o endpoint de login"

        # (name, should_fire, payload, sentence[, process cwd]) — sentence is None when the case
        # does not care what follows the reminder, True when exactly SPEC_RITE must, False when
        # nothing may, and a string when exactly that string must.
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
            # Where the workflow is looked for (#261): from the working directory up to and
            # including the root of the repository it is in, the nearest openspec/ counting.
            ("subdirectory of a repo whose root has openspec/ appends the spec sentence", True,
             {"prompt": login, "cwd": os.path.join(with_rite, "src", "deep")}, True),
            ("subdirectory of a repo without openspec/ omits the spec sentence", True,
             {"prompt": login, "cwd": os.path.join(without_rite, "src", "deep")}, False),
            # The root does not hold openspec/, the package the cwd sits in does. Looking only at
            # <root>/openspec would silence a sentence that fired before the walk existed.
            ("cwd that holds openspec/ below a root that does not keeps the spec sentence", True,
             {"prompt": login, "cwd": os.path.join(td, "mono", "packages", "app")}, True),
            # The nearest openspec/ is neither the cwd nor the root: a walk that probed only those
            # two would pass every other case and fail this one.
            ("openspec/ in a directory between cwd and the root appends the spec sentence", True,
             {"prompt": login, "cwd": os.path.join(td, "mono", "packages", "app", "src")}, True),
            ("a .git file (linked work tree, submodule) marks the root", True,
             {"prompt": login, "cwd": os.path.join(td, "linked", "pkg")}, True),
            # The outer repo runs the workflow, the inner one (the cwd) does not, and a repo inside
            # the inner one does. The first `.git` up from the cwd bounds the walk, as it does for
            # git, so the outer openspec/ is never seen; and the repos inside a repo are never a
            # workspace, which needs a cwd outside any repository.
            ("nested repo: the first .git up from the cwd wins, and the repos inside it are not a "
             "workspace", True,
             {"prompt": login, "cwd": os.path.join(td, "outer", "inner")}, False),
            # realpath raises on an embedded NUL where the old isdir probe answered False: the
            # sentence is dropped, the reminder still fires, and nothing reaches a traceback.
            ("cwd with an embedded NUL omits the spec sentence instead of raising", True,
             {"prompt": login, "cwd": with_rite + "\x00"}, False),
        ]
        # These need a directory outside any repository. With the temporary directory inside one,
        # the walk would find that repository first and the case would measure the runner's layout
        # instead of the branch it names, so it is skipped, never counted as passing.
        outside_cases = [
            ("workspace root names the child repos that hold openspec/, and only them", True,
             {"prompt": login, "cwd": os.path.join(td, "workspace")},
             WORKSPACE_SPEC_RITE.format(names="api, docs")),
            ("workspace root with no child repo holding openspec/ omits the spec sentence", True,
             {"prompt": login, "cwd": os.path.join(td, "workspace-none")}, False),
            ("directory outside any repo that holds openspec/ keeps the spec sentence", True,
             {"prompt": login, "cwd": os.path.join(td, "loose")}, True),
            # One listing entry whose stat raises must not empty the whole listing: the loop is
            # skipped and `api` is still named.
            ("workspace root: a symlink loop beside a child does not hide the child", True,
             {"prompt": login, "cwd": os.path.join(td, "workspace-loop")},
             WORKSPACE_SPEC_RITE.format(names="api")),
            # design.md D3 orders branch 2 before branch 3: the cwd's own openspec/ wins and the
            # children are not named (the docstring's KNOWN LIMIT). Swapping the two breaks this.
            ("workspace root that holds openspec/ itself keeps its own sentence, as D3 orders",
             True, {"prompt": login, "cwd": os.path.join(td, "workspace-own")}, True),
        ]
        enclosing = find_repo_root(td)
        if enclosing is None:
            cases += outside_cases
        else:
            skipped = [name for name, *_ in outside_cases]
        for name, should_fire, payload, sentence, *rest in cases:
            with process_cwd(rest[0] if rest else None):
                got = evaluate(payload)
            ok = bool(got) == should_fire
            if ok and got and sentence is not None:
                tail = SPEC_RITE if sentence is True else "" if sentence is False else sentence
                ok = got == REMINDER + tail
            print(f"  {'OK     ' if ok else 'FAILED '} {name}")
            if not ok:
                failed.append(name)
        for name in skipped:
            print(f"  SKIP    {name} (the temporary directory sits inside the repository at "
                  f"{enclosing})")

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
    note = (f" ({len(skipped)} skipped: the temporary directory sits inside a repository)"
            if skipped else "")
    print(f"selftest OK: {len(cases)} decisions{note}, {len(malformed)} malformed payloads, "
          "plus the output shape")
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
