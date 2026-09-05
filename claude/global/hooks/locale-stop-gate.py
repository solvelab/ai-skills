#!/usr/bin/env python3
"""Stop hook — measures the code-locale rite on the turn's uncommitted diff, whatever wrote it.

Reads the Stop payload on stdin, finds the git work tree the working directory is in, builds the
diff the turn left uncommitted — tracked files against the current commit, plus every untracked file
the repository does not ignore, each as an added file — and runs the shipped identifier-locale check
over it in diff mode. A gating finding blocks the end of the turn; the reason lists every finding and
the exits. Silent when there is nothing to measure.

WHY A STOP HOOK WHEN A WRITE HOOK ALREADY EXISTS
    `locale-rite.py` sees `Write|Edit|MultiEdit|NotebookEdit`. Nothing written through Bash — a
    heredoc, `sed -i`, a script — passes through it, and the harness's auto mode instructs the
    assistant to edit files exactly that way. Measured live on 2026-09-05 (issue #138): a heredoc
    wrote `servico_cliente.py` with `def buscar_cliente(id_usuario)` and no hook fired. The write
    hook covers the tool; this one covers the result. It measures only what the turn left
    uncommitted: history and untouched lines never enter, so a legacy repository is not judged for
    what it already had.

WHY `{"decision": "block", "reason": ...}` AT THE TOP LEVEL AND NOTHING NESTED
    The docs pages disagree on whether Stop reads the decision at the top level or under
    `hookSpecificOutput`. Probed against the installed bundle rather than recalled:
    `readlink -f $(which claude)` -> ~/.local/share/claude/versions/2.1.261 (`claude --version` ->
    `2.1.261 (Claude Code)`; a single ELF, so the grep needs `-a`). Fragments, minified names as
    found:
      - input schema:  `hook_event_name:C("Stop"),stop_hook_active:P(),last_assistant_message:...`
        (and `C("SubagentStop"),stop_hook_active:P(),agent_id:s(),...`)
      - what blocks:   `function eg(e){if("decision"in e&&e.decision==="block")return!0;
                        if("continue"in e&&e.continue===!1)return!0; ...permissionDecision...}`
      - what is read:  `f=...X5(r,"reason",o.reason), y=X5(r,"systemMessage",o.systemMessage)` and
                       the answer is `{...o.decision==="block"&&{decision:"block"},
                       ...y!==void 0&&{systemMessage:y}, ...f!==void 0&&{reason:f}, ...}`
      - nested Stop:   `function LU(e,t,r){let o=X5(e,"additionalContext",r.additionalContext);
                        return{hookEventName:t,...o!==void 0&&{additionalContext:o}}}` — for Stop,
                       `hookSpecificOutput` yields only `additionalContext`; any other nested key
                       (a nested `decision`) is dropped without an error.
      - caps:          `AKr={reason:2000,stopReason:2000,systemMessage:4000,additionalContext:8000,...}`
      - loop guard:    `let Od=a.CLAUDE_CODE_STOP_HOOK_BLOCK_CAP??8;if(Od>0&&Pc>Od)` -> "A hook
                       blocked the turn from ending N consecutive times — overriding and ending turn.
                       For Stop/SubagentStop hooks, check stop_hook_active in the input and return
                       success while it's true."
    So the top level is what the bundle reads, the nested form is ignored, and this hook emits the
    top level only — emitting both would document a shape the bundle demonstrably does not read.
    Docs as the second source: code.claude.com/docs/en/hooks (read 2026-09-05).

WHY THE DIFF SHAPE IS PINNED AGAINST THE USER'S GIT CONFIG
    `scan_diff` reads `--- /dev/null`, `+++ b/<path>` and `+` lines. Three ordinary settings in
    `~/.gitconfig` change that shape and, measured on git 2.47.3 (review of #138), each one silenced
    or misreported the gate: `diff.external = true` (difftastic/delta users) hands the diff to the
    tool and stdout is EMPTY — `git diff HEAD --no-color | wc -l` -> 0, hook silent on a Portuguese
    edit; `diff.mnemonicPrefix = true` prints `+++ w/shipping.py`, so every finding named a path that
    does not exist (`w/shipping.py`) and `.identifier-locale-allow` path entries no longer matched;
    `core.quotePath` (default TRUE) prints `+++ "b/relat\303\263rio.py"` with the quotes, the suffix
    becomes `.py"`, no language matches and the added lines are never scanned — exactly the
    `non-ascii` tier the check exists for. A `.gitattributes` `textconv` rewrites the content the
    same way (`tr a-z A-Z <` upper-cased every identifier). So every git call runs as
    `git --no-pager -c core.quotePath=false`, and both diffs add `--no-ext-diff --no-textconv
    --no-color --no-relative --src-prefix=a/ --dst-prefix=b/`; probed with all of those settings on
    at once (plus `diff.noprefix`, `diff.relative`, `color.ui = always`): the headers come back as
    `--- a/shipping.py` / `+++ b/shipping.py` and `+++ b/relatório.py`. The selftest carries that
    gitconfig as a fixture, because its default fixture (`GIT_CONFIG_GLOBAL=/dev/null`) proves the
    decisions only under a blank config. A path with a double quote or a control character is still
    quoted by git with `quotePath=false`, and stays a declared limit.

WHY A TRUNCATED DIFF IS NEVER A SILENT PASS
    The cap (`MAX_DIFF_LINES`) exists so a huge diff cannot push the hook past the harness timeout.
    The first version attached the truncation note to the reason — and only to the reason: when the
    cap was eaten by clean or vendored content that sorts BEFORE the Portuguese file (`aaa_generated.py`
    with 5000 English lines, 5000 lines appended to a tracked file, an unignored `build/gen.py`, 1500
    empty files under `build/`), the Portuguese file was never measured and the hook emitted nothing
    (measured, review of #138: rc=0, no output, in all four cases). Now: untracked paths the check
    calls vendored, and empty files (git prints no `+++` for them anyway), are skipped BEFORE git is
    called, so they consume neither the cap nor a subprocess; and when the cap was reached and the
    measured part is clean, the hook still blocks once — the reason says the tail was NOT measured
    and how to measure it — then, on the Stop that follows (`stop_hook_active`), reports and lets the
    turn end. "Cannot measure" becomes "does not block" only on a git timeout (see KNOWN LIMIT).

WHY `stop_hook_active` NEVER BLOCKS TWICE
    The harness sets `stop_hook_active: true` on the Stop that follows a block. This hook blocks
    once; on the next Stop it returns only a `systemMessage` naming what is still in Portuguese and
    lets the turn end. The second turn is the last chance, not a loop: whoever read the reason and did
    not rename has decided. The bundle's own cap (8 consecutive blocks) stays as the second net.

KNOWN LIMIT — what this hook does NOT see
    - A file committed inside the same turn: the diff is against HEAD, and a commit moves HEAD.
    - A repository other than the one `cwd` is in, or a working directory outside any git work tree.
    - Inside a subagent the event is `SubagentStop`, and this hook is wired on `Stop`; it accepts
      both names, so wiring it on `SubagentStop` works without an edit, but nothing wires it there.
    - A Portuguese file MOVED without an edit: rename detection stays at git's default, so it is a
      rename, not an added file, and the path tier does not fire ("legacy enters only if the turn
      touched it"). A binary file (NUL in its first 8 KiB) and an EMPTY file are skipped before git
      is called, so their NAMES are not measured either (git itself prints no `+++` for an empty
      file — probed: `git diff --no-index /dev/null relatorio.py` on an empty file prints the
      `diff --git` and `index` lines only — and no `+` line for a binary).
    - An untracked path with a double quote, a backslash or a control character in its name: git
      quotes it even with `core.quotePath=false`, the check sees the quotes, and the file is not
      measured. Non-ASCII letters (`relatório.py`) ARE measured; see the pinned diff shape above.
    - A diff longer than MAX_DIFF_LINES: the rest is not measured, and the hook SAYS so — in the
      reason when it has findings, and as a block of its own when the measured part is clean. A git
      call that exceeds GIT_TIMEOUT makes the hook silent — the one case where "cannot measure"
      becomes "does not block", because a gate that cannot measure must not hold the turn forever.
    - Advisory findings (`en-unknown`): the check itself declares them non-gating; this hook runs
      without the English word list and never blocks on a question.
    - Whatever the check itself cannot see (open vocabulary, the escapes its docstring declares).
    - Only `LOCALE_RITE_MODE=inform` silences it for a whole session; `locale-ok:` and
      `.identifier-locale-allow` are per name and per path. The variable is the one issue #137 gives
      the write gate (`locale-rite.py`, same name, same value); until #137 merges, this hook is its
      only reader — one variable per rite, not per hook.

Wiring (~/.claude/settings.json), beside any Stop hook already there:

    "hooks": {
      "Stop": [
        {"hooks": [{"type": "command",
                    "command": "python3 ~/ai-skills/claude/global/hooks/locale-stop-gate.py",
                    "timeout": 30}]}
      ]
    }

Like personal-rules.md, this is the maintainer's config — edit the message and the cap to match your
own process instead of adopting it blindly.

Modes: (default) read one payload from stdin   |   --selftest assert the decisions against a temporary git repository.
Any other argument prints usage to stderr and exits 2 — the same contract as the sibling hooks, so a
misspelt flag cannot fall through to the stdin path and exit 0.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# The check lives in the skill that owns the doctrine. parents[3] of this file is the repository
# root (hooks -> global -> claude -> root); the path is resolved, never guessed, and a miss exits
# silently — the same rule as locale-rite.py.
CHECK_PATH = Path(__file__).resolve().parents[3] / "skills/code-locale/references/check-identifier-locale.py"

# Declared, not silent: past this many diff lines the rest is not measured and the reason says so.
MAX_DIFF_LINES = 4000
# Per git call. The harness kills slow hooks; a git that does not answer makes this hook silent.
GIT_TIMEOUT = 5
# Measured caps in the bundle (see the docstring): truncating here keeps the tail we choose — the
# exits — rather than the tail the harness chooses.
REASON_CAP = 2000
SYSTEM_MESSAGE_CAP = 4000
# NUL in the first 8 KiB is git's own binary heuristic.
BINARY_PROBE_BYTES = 8192
# The diff shape scan_diff reads, pinned against ~/.gitconfig (see the docstring): every git call
# gets GIT_PIN, every diff gets DIFF_FLAGS. Measured: `diff.external` empties stdout,
# `diff.mnemonicPrefix` renames `b/` to `w/`, `core.quotePath` (default true) quotes `relatório.py`.
GIT_PIN = ["--no-pager", "-c", "core.quotePath=false"]
DIFF_FLAGS = ["--no-ext-diff", "--no-textconv", "--no-color", "--no-relative",
              "--src-prefix=a/", "--dst-prefix=b/"]

STOP_EVENTS = {"Stop", "SubagentStop"}
MODE_VAR = "LOCALE_RITE_MODE"
INFORM = "inform"
# `git hash-object -t tree /dev/null` in a SHA-1 repository — the base for a repository with no
# commit yet, where `git diff HEAD` fails with rc=128. Recomputed per repository when git answers, so
# a SHA-256 repository gets its own value; this constant is only the fallback.
EMPTY_TREE_SHA1 = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

HEADER = (
    "CODE-LOCALE (stop gate): the turn is ending with uncommitted changes that carry a non-English "
    "name in the machine layer. Whatever wrote them — an edit tool, a shell heredoc, sed — the diff "
    "is what is measured. Rename before ending the turn, or take one of the exits at the end.\n\n"
)
TRUNCATED_NOTE = (
    "\n\n[diff truncated at {n} lines; the rest was NOT measured — run "
    "`check-identifier-locale.py --diff -` on the full diff before trusting a clean result]"
)
# The cap was reached and the measured part is clean: an unmeasured tail is not a clean result, so
# the gate blocks once and says how to measure the rest (then the second Stop reports and lets go).
UNMEASURED_REASON = (
    "CODE-LOCALE (stop gate): the uncommitted diff is longer than {n} lines and was measured only up "
    "to that cap. Nothing non-English was found in the measured part, but the rest was NOT measured, "
    "and an unmeasured tail is not a clean result. Before ending the turn, run the check on the whole "
    "diff — `git diff HEAD | python3 {check} --diff -`, plus `git diff --no-index /dev/null <path>` "
    "for each untracked file — and rename or waive what it reports; then end the turn again (the next "
    "Stop reports without blocking). If the bulk is generated, commit it or list it in .gitignore so "
    "the gate measures what the turn wrote."
)
UNMEASURED_MESSAGE = (
    "code-locale: the turn is ending with an uncommitted diff longer than {n} lines; the part past "
    "the cap was NOT measured (second Stop — not blocking again). Run `python3 {check} --diff -` on "
    "the full diff before trusting it."
)
FOOTER = (
    "\n\nExits: `# locale-ok: <reason>` on the line or the line above; the token or path in "
    "`.identifier-locale-allow` at the repository root (the only exit for a file name); "
    "`LOCALE_RITE_MODE=inform` for the whole session. Doctrine: the code-locale skill."
)
ELLIPSIS = "\n    … more findings elided; run the check on the diff for the rest."


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


def run_git(args: list, cwd: str, env=None) -> "tuple[int, str] | None":
    """(returncode, stdout) or None when git is missing, hangs, or cannot be started."""
    try:
        run = subprocess.run(["git", *GIT_PIN, *args], cwd=cwd, env=env, capture_output=True,
                             text=True, errors="replace", timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None
    return run.returncode, run.stdout


def is_measurable(path: Path) -> bool:
    """False for an empty or binary file — git prints no `+++` for the first and no `+` line for
    the second, so asking it costs a subprocess and cap lines for nothing measurable."""
    try:
        if path.stat().st_size == 0:
            return False
        with open(path, "rb") as fh:
            return b"\0" not in fh.read(BINARY_PROBE_BYTES)
    except OSError:
        return False                     # unreadable is skipped like binary: nothing to measure


def uncommitted_diff(cwd: str, max_lines: int, env=None,
                     vendored=None) -> "tuple[str, list, bool] | None":
    """(work tree root, diff lines, truncated) — or None when cwd is not inside a git work tree.

    `vendored(Path) -> bool` names the untracked paths that never enter the diff (the check's own
    vendored rule): filtering them AFTER the scan let an unignored `build/` eat the whole cap.
    """
    top = run_git(["rev-parse", "--show-toplevel"], cwd, env)
    if top is None or top[0] != 0 or not top[1].strip():
        return None
    root = top[1].strip()

    head = run_git(["rev-parse", "--verify", "-q", "HEAD"], root, env)
    if head is None:
        return None
    if head[0] == 0:
        base = "HEAD"
    else:
        empty = run_git(["hash-object", "-t", "tree", "/dev/null"], root, env)
        base = empty[1].strip() if empty and empty[0] == 0 and empty[1].strip() else EMPTY_TREE_SHA1

    lines: list = []
    truncated = False

    def take(text: str) -> bool:
        """Append diff text; False once the cap is reached (callers stop asking git)."""
        nonlocal truncated
        for line in text.splitlines():
            if len(lines) >= max_lines:
                truncated = True
                return False
            lines.append(line)
        return True

    tracked = run_git(["diff", *DIFF_FLAGS, base], root, env)
    if tracked is None or tracked[0] not in (0, 1):
        return None
    if not take(tracked[1]):
        return root, lines, truncated

    others = run_git(["ls-files", "--others", "--exclude-standard", "-z"], root, env)
    if others is None or others[0] != 0:
        return None
    for rel in others[1].split("\0"):
        if not rel:
            continue
        if vendored is not None and vendored(Path(rel)):
            continue
        if not is_measurable(Path(root) / rel):
            continue
        added = run_git(["diff", *DIFF_FLAGS, "--no-index", "/dev/null", rel], root, env)
        if added is None or added[0] not in (0, 1):
            continue                     # one unreadable path must not silence the rest
        if not take(added[1]):
            break
    return root, lines, truncated


def gating_findings(check, root: str, lines: list) -> list:
    """The findings the check is sure of, minus vendored paths (diff mode does not filter them)."""
    allow = check.load_allowlist(Path(root))
    findings = check.scan_diff(iter(line + "\n" for line in lines), allow, None)
    return [f for f in findings
            if not getattr(f, "advisory", False) and not check.is_vendored(Path(f.path))]


def capped(head: str, body: str, tail: str, cap: int) -> str:
    text = head + body + tail
    if len(text) <= cap:
        return text
    room = cap - len(head) - len(tail) - len(ELLIPSIS)
    return head + body[:max(room, 0)].rstrip() + ELLIPSIS + tail


def block_reason(findings: list, truncated: bool) -> str:
    body = "\n".join(f.render() for f in findings)
    tail = (TRUNCATED_NOTE.format(n=MAX_DIFF_LINES) if truncated else "") + FOOTER
    return capped(HEADER, body, tail, REASON_CAP)


def remaining_message(findings: list, truncated: bool) -> str:
    n = len(findings)
    head = (f"code-locale: the turn is ending with {n} non-English name{'s' if n != 1 else ''} still "
            "uncommitted (second Stop — not blocking again; rename or waive before committing):\n")
    # A path finding carries line 0 (there is no line): print the path alone rather than `:0`.
    body = "\n".join(f"  {f.path}{':' + str(f.line) if f.line else ''}: {f.token}  [{f.tier}]"
                     for f in findings)
    tail = TRUNCATED_NOTE.format(n=MAX_DIFF_LINES) if truncated else ""
    return capped(head, body, tail, SYSTEM_MESSAGE_CAP)


def evaluate(payload: dict, check, env=None, max_lines: int = MAX_DIFF_LINES) -> "dict | None":
    """The whole decision, isolated from stdin and stdout so the selftest can drive it.

    `env` is the process environment the mode is read from and git is run with; the selftest hands
    its own so that no case mutates os.environ. `max_lines` exists so the truncation path is testable
    without a 4000-line fixture.
    """
    if check is None:
        return None
    environment = os.environ if env is None else env
    if str(environment.get(MODE_VAR, "")).strip().lower() == INFORM:
        return None
    event = payload.get("hook_event_name")
    if event is not None and event not in STOP_EVENTS:
        return None                      # a wrong matcher must not become a block on another event
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd or not os.path.isdir(cwd):
        return None                      # a gate that cannot locate what to measure does not block
    git_env = None if env is None else dict(env)
    try:
        measured = uncommitted_diff(cwd, max_lines, git_env,
                                    vendored=lambda rel: check.is_vendored(rel))
        if measured is None:
            return None
        root, lines, truncated = measured
        if not lines:
            return None
        findings = gating_findings(check, root, lines)
    except Exception:
        return None                      # a check that crashes must not crash the turn
    active = bool(payload.get("stop_hook_active"))
    if not findings:
        if not truncated:
            return None
        # Clean up to the cap is not clean: the tail was not measured, and silence would say it was.
        fill = {"n": max_lines, "check": str(CHECK_PATH)}
        if active:
            return {"systemMessage": UNMEASURED_MESSAGE.format(**fill)[:SYSTEM_MESSAGE_CAP]}
        return {"decision": "block", "reason": UNMEASURED_REASON.format(**fill)[:REASON_CAP]}
    if active:
        return {"systemMessage": remaining_message(findings, truncated)}
    return {"decision": "block", "reason": block_reason(findings, truncated)}


# ── Self-test ─────────────────────────────────────────────────────────────

PT_SOURCE = "def buscar_cliente(id_usuario):\n    return id_usuario\n"
EN_SOURCE = "def find_customer(user_id):\n    return user_id\n"


def _fixture_env(tmp: str, **extra) -> dict:
    """An environment that ignores the machine's git config and never discovers a repo above tmp."""
    env = dict(os.environ)
    env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                "GIT_CEILING_DIRECTORIES": tmp, "GIT_AUTHOR_NAME": "selftest",
                "GIT_AUTHOR_EMAIL": "selftest@example.invalid", "GIT_COMMITTER_NAME": "selftest",
                "GIT_COMMITTER_EMAIL": "selftest@example.invalid"})
    env.pop(MODE_VAR, None)
    env.update(extra)
    return env


def _git(repo: Path, env: dict, *args) -> None:
    subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + os.devnull, *args],
                   cwd=repo, env=env, check=True, capture_output=True)


def _repo(tmp: Path, env: dict, name: str, commit: bool = True) -> Path:
    repo = tmp / name
    (repo / "orders").mkdir(parents=True)
    (repo / "orders" / "service.py").write_text("def compute_shipping(order_id):\n    return 0\n")
    _git(repo, env, "init", "-q", "-b", "main")
    if commit:
        _git(repo, env, "add", "-A")
        _git(repo, env, "commit", "-q", "-m", "init")
    return repo


def _payload(cwd, active: bool = False, event: str = "Stop") -> dict:
    return {"session_id": "selftest", "transcript_path": "/dev/null", "cwd": str(cwd),
            "hook_event_name": event, "stop_hook_active": active}


def selftest() -> int:
    check = load_check()
    if check is None:
        print(f"selftest FAILED: check not found at {CHECK_PATH}")
        return 1
    failed = []
    decisions = 0

    def case(name: str, expect: str, got) -> None:
        nonlocal decisions
        decisions += 1
        kind = "silent" if got is None else "block" if got.get("decision") == "block" else \
            "message" if set(got) == {"systemMessage"} else "other"
        ok = kind == expect
        print(f"  {'OK     ' if ok else 'FAILED '} {name}  ->  {kind}")
        if not ok:
            failed.append(name)

    with tempfile.TemporaryDirectory(prefix="locale-stop-gate-") as td:
        tmp = Path(td)
        env = _fixture_env(td)

        # ── the heredoc case: an untracked Portuguese file, no write tool involved ──
        repo = _repo(tmp, env, "heredoc")
        (repo / "servico_cliente.py").write_text(PT_SOURCE)
        blocked = evaluate(_payload(repo), check, env)
        case("untracked portuguese file blocks the stop", "block", blocked)
        case("second stop (stop_hook_active) reports and does not block", "message",
             evaluate(_payload(repo, active=True), check, env))
        case("LOCALE_RITE_MODE=inform is silent", "silent",
             evaluate(_payload(repo), check, {**env, MODE_VAR: INFORM}))
        case("SubagentStop payload is evaluated too", "block",
             evaluate(_payload(repo, event="SubagentStop"), check, env))
        case("another event name is silent", "silent",
             evaluate(_payload(repo, event="PostToolUse"), check, env))
        case("payload without cwd is silent", "silent",
             evaluate({"hook_event_name": "Stop", "stop_hook_active": False}, check, env))
        case("cwd in a subdirectory still measures the whole work tree", "block",
             evaluate(_payload(repo / "orders"), check, env))
        # FR2: renamed and translated, the turn ends.
        (repo / "servico_cliente.py").rename(repo / "customer_service.py")
        (repo / "customer_service.py").write_text(EN_SOURCE)
        case("renamed and translated, the stop is allowed", "silent",
             evaluate(_payload(repo), check, env))

        # ── a tracked file edited in place ──
        repo = _repo(tmp, env, "tracked")
        service = repo / "orders" / "service.py"
        service.write_text(service.read_text() + "usuario_count = 1\n")
        case("tracked file edited with a portuguese identifier blocks", "block",
             evaluate(_payload(repo), check, env))
        service.write_text(service.read_text().replace("usuario_count", "user_count"))
        case("clean edit is silent", "silent", evaluate(_payload(repo), check, env))
        service.write_text("def compute_shipping(order_id):\n    return 0\n"
                           "# locale-ok: legal term with no faithful English name\nnota_fiscal_number = 1\n")
        case("locale-ok waiver on the line above is silent", "silent",
             evaluate(_payload(repo), check, env))
        service.unlink()
        case("deleted tracked file is silent", "silent", evaluate(_payload(repo), check, env))

        # ── what the diff builder deliberately skips ──
        repo = _repo(tmp, env, "skips")
        (repo / "relatorio.bin").write_bytes(b"\0\1binary")
        case("binary untracked file is skipped (declared limit)", "silent",
             evaluate(_payload(repo), check, env))
        (repo / "vendor").mkdir()
        (repo / "vendor" / "servico.py").write_text(PT_SOURCE)
        case("vendored untracked path is silent", "silent", evaluate(_payload(repo), check, env))
        (repo / "node_modules").mkdir()
        (repo / "node_modules" / "pedido.js").write_text("var valorTotal = 1\n")
        (repo / ".gitignore").write_text("node_modules/\n")
        case("ignored path never enters the diff", "silent", evaluate(_payload(repo), check, env))
        (repo / ".identifier-locale-allow").write_text("fatura_id\n")
        (repo / "orders" / "billing.py").write_text("fatura_id = 1\n")
        case("token in the repository allowlist is silent", "silent",
             evaluate(_payload(repo), check, env))
        (repo / "orders" / "billing.py").write_text("fatura_id = 1\ncobranca_total = 2\n")
        case("allowlist covers only what it names", "block", evaluate(_payload(repo), check, env))

        # ── a repository with no commit yet, and a truncated diff ──
        repo = _repo(tmp, env, "unborn", commit=False)
        (repo / "servico.py").write_text(PT_SOURCE)
        _git(repo, env, "add", "servico.py")
        case("repository without a commit measures staged files", "block",
             evaluate(_payload(repo), check, env))
        repo = _repo(tmp, env, "long")
        (repo / "big.py").write_text("".join(f"pedido_{i} = {i}\n" for i in range(600)))
        long_diff = evaluate(_payload(repo), check, env, max_lines=100)
        case("diff over the cap still blocks", "block", long_diff)
        says_so = bool(long_diff) and "truncated" in long_diff.get("reason", "")
        print(f"  {'OK     ' if says_so else 'FAILED '} truncation is stated in the reason")
        if not says_so:
            failed.append("truncation stated")

        # ── a clean measured part over the cap is not a clean result ──
        repo = _repo(tmp, env, "clean-ahead")
        (repo / "aaa_generated.py").write_text("".join(f"value_{i} = {i}\n" for i in range(200)))
        ahead = evaluate(_payload(repo), check, env, max_lines=100)
        unmeasured_ok = (isinstance(ahead, dict) and ahead.get("decision") == "block"
                         and "NOT measured" in ahead.get("reason", "")
                         and str(CHECK_PATH) in ahead.get("reason", "")
                         and len(ahead["reason"]) <= REASON_CAP)
        print(f"  {'OK     ' if unmeasured_ok else 'FAILED '} clean diff over the cap blocks once and says the tail was not measured")
        if not unmeasured_ok:
            failed.append("unmeasured tail")
        case("clean diff over the cap on the second stop reports and does not block", "message",
             evaluate(_payload(repo, active=True), check, env, max_lines=100))
        (repo / "servico_cliente.py").write_text(PT_SOURCE)
        case("clean lines ahead of a portuguese file never make it a silent pass", "block",
             evaluate(_payload(repo), check, env, max_lines=100))
        # vendored and empty untracked files consume neither the cap nor a git call
        repo = _repo(tmp, env, "cap-eaters")
        (repo / "build").mkdir()
        (repo / "build" / "gen.py").write_text("".join(f"value_{i} = {i}\n" for i in range(200)))
        for i in range(60):                      # outside build/, so only the size rule skips them
            (repo / "orders" / f"empty_{i}.py").touch()
        (repo / "servico_cliente.py").write_text(PT_SOURCE)
        eaters = evaluate(_payload(repo), check, env, max_lines=100)
        case("unignored vendored and empty files do not eat the cap ahead of a portuguese file",
             "block", eaters)
        not_truncated = bool(eaters) and "truncated" not in eaters.get("reason", "") \
            and "servico_cliente.py" in eaters.get("reason", "")
        print(f"  {'OK     ' if not_truncated else 'FAILED '} the portuguese file is measured with no truncation note (cap untouched)")
        if not not_truncated:
            failed.append("cap eaters")

        # ── the user's ~/.gitconfig must not change what is measured ──
        gitconfig = tmp / "gitconfig"
        # `diff.noprefix` is deliberately NOT in this fixture: it strips the prefix altogether, which
        # scan_diff already reads correctly, and it overrides mnemonicPrefix — with it set, dropping
        # the --src-prefix/--dst-prefix pin would go unnoticed (measured: that mutant stayed green).
        gitconfig.write_text("[diff]\n\texternal = true\n\tmnemonicPrefix = true\n"
                             "\trelative = true\n[core]\n\tquotePath = true\n"
                             "[color]\n\tui = always\n\tdiff = always\n")
        configured = {**env, "GIT_CONFIG_GLOBAL": str(gitconfig), "GIT_EXTERNAL_DIFF": "true"}
        repo = _repo(tmp, configured, "configured")
        service = repo / "orders" / "service.py"
        service.write_text(service.read_text() + "usuario_count = 1\n")
        pinned = evaluate(_payload(repo), check, configured)
        case("diff.external, mnemonicPrefix, relative and color.ui do not silence the gate",
             "block", pinned)
        path_ok = bool(pinned) and "\norders/service.py:3: usuario_count" in pinned.get("reason", "")
        print(f"  {'OK     ' if path_ok else 'FAILED '} the finding names the repository path, not w/ or a bare one")
        if not path_ok:
            failed.append("pinned prefix")
        # non-ASCII names: core.quotePath (default true) would print `"b/relat\303\263rio.py"`
        (repo / "orders" / "relatório.py").write_text(PT_SOURCE)
        non_ascii = evaluate(_payload(repo), check, configured)
        case("untracked file with a non-ASCII name is measured, name and content", "block", non_ascii)
        named_ok = bool(non_ascii) and "orders/relatório.py: relatório" in non_ascii.get("reason", "") \
            and "orders/relatório.py:1: buscar_cliente" in non_ascii.get("reason", "")
        print(f"  {'OK     ' if named_ok else 'FAILED '} the non-ASCII path is reported unquoted, with its identifiers")
        if not named_ok:
            failed.append("non-ascii path")
        service.write_text("def compute_shipping(order_id):\n    return 0\n")
        _git(repo, configured, "add", "-A")
        _git(repo, configured, "commit", "-q", "-m", "track")
        (repo / "orders" / "relatório.py").write_text(EN_SOURCE + "id_pedido = 1\n")
        case("tracked file with a non-ASCII name edited in place is measured", "block",
             evaluate(_payload(repo), check, configured))

        # ── outside any git work tree ──
        outside = tmp / "no-repo"
        outside.mkdir()
        (outside / "servico_cliente.py").write_text(PT_SOURCE)
        case("cwd outside a git work tree is silent", "silent",
             evaluate(_payload(outside), check, env))

        # ── output shape: the fields the bundle reads, and nothing nested ──
        shape_ok = (
            isinstance(blocked, dict) and set(blocked) == {"decision", "reason"}
            and blocked["decision"] == "block" and isinstance(blocked["reason"], str)
            and len(blocked["reason"]) <= REASON_CAP
            and blocked["reason"].startswith("CODE-LOCALE") and blocked["reason"].endswith(FOOTER)
            and "servico_cliente.py" in blocked["reason"] and "buscar_cliente" in blocked["reason"]
            and "hookSpecificOutput" not in blocked
        )
        print(f"  {'OK     ' if shape_ok else 'FAILED '} block shape is top-level decision/reason within the cap, findings and exits named")
        if not shape_ok:
            failed.append("block shape")
        repo = _repo(tmp, env, "active")
        (repo / "servico_cliente.py").write_text(PT_SOURCE)
        active = evaluate(_payload(repo, active=True), check, env)
        active_ok = (isinstance(active, dict) and set(active) == {"systemMessage"}
                     and len(active["systemMessage"]) <= SYSTEM_MESSAGE_CAP
                     and "servico_cliente.py" in active["systemMessage"])
        print(f"  {'OK     ' if active_ok else 'FAILED '} second-stop shape is systemMessage only, within the cap")
        if not active_ok:
            failed.append("second-stop shape")

    # ── the entry point: malformed payloads and the argv contract ──
    malformed = 0
    for label, stdin in (("json array", "[]"), ("json string", '"x"'), ("empty stdin", ""),
                         ("json null", "null"), ("not json", "{oops")):
        run = subprocess.run([sys.executable, __file__], input=stdin, capture_output=True, text=True)
        ok = run.returncode == 0 and run.stdout == "" and run.stderr == ""
        print(f"  {'OK     ' if ok else 'FAILED '} malformed payload is silent, exit 0: {label}")
        malformed += ok
        if not ok:
            failed.append(f"malformed {label}")
    run = subprocess.run([sys.executable, __file__, "--bogus"], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    argv_ok = run.returncode == 2 and "usage:" in run.stderr and run.stdout == ""
    print(f"  {'OK     ' if argv_ok else 'FAILED '} unknown flag prints usage and exits 2")
    if not argv_ok:
        failed.append("unknown flag")
    run = subprocess.run([sys.executable, __file__, "--selftest", "extra"], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    extra_ok = run.returncode == 2 and "usage:" in run.stderr
    print(f"  {'OK     ' if extra_ok else 'FAILED '} --selftest with an extra argument exits 2")
    if not extra_ok:
        failed.append("selftest extra argument")

    print()
    if failed:
        print("selftest FAILED: " + "; ".join(failed))
        return 1
    print(f"selftest OK: {decisions} decisions in temporary git repositories, 2 output shapes, "
          f"{malformed} malformed payloads, plus the argv contract")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args == ["--selftest"]:
        return selftest()
    if args:
        # An unknown argument must not fall through to the stdin path: a misspelt flag in a CI step
        # would then read empty stdin and exit 0 — the silent no-op the selftest mode exists to make
        # impossible (#115).
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
