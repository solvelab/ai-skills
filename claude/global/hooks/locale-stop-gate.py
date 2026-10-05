#!/usr/bin/env python3
"""Stop hook — measures the code-locale rite on the turn's uncommitted diff, whatever wrote it.

Reads the Stop payload on stdin, finds the git work tree the working directory is in — or, from a
workspace root, each work tree directly below it — builds the diff the turn left uncommitted —
tracked files against the current commit, plus every untracked file the repository does not ignore,
each as an added file — and runs the shipped identifier-locale check over it in diff mode. A gating
finding blocks the end of the turn; the reason lists every finding and the exits. Silent when there
is nothing to measure.

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
    turn end. "Cannot measure" becomes "does not block" only on a git that fails or exceeds
    GIT_TIMEOUT (see KNOWN LIMIT); the time bound below follows the cap's rule, not that one.

WHY A WORKSPACE ROOT MEASURES EACH CHILD (issue #261)
    A session opened at a workspace root — a directory outside any work tree whose direct
    subdirectories are work trees, the backlog skill's definition — used to end every turn
    unmeasured: `git rev-parse --show-toplevel` exits 128 there, and the hook read that as "nothing
    to measure". Now a non-zero exit lists those children (`child_repos`: `.git` as a directory or a
    file, sorted by name, one level only) and measures each at its own root, with its own
    `.identifier-locale-allow` and its own `.code-locale`: one child's allowlist or declaration
    never speaks for another, and no diff is joined across repositories. The findings reach one
    reason, the first line of each prefixed with `<child>/`, while the allowlist line a file-name
    finding prints stays relative to the child — that is the entry that silences it in the child's
    own allowlist, and `<child>/<path>` there does not (the selftest fixes both). Writing the prefix
    into the finding would print an exit that does not work when followed. A git that is missing, or
    that does not answer that first call, keeps the hook silent as before; so does a directory with
    no child work tree. A child whose allowlist or `.code-locale` cannot be read (not UTF-8, no
    permission) is skipped like a child git cannot read, and its siblings are still measured.

WHY ONE TIME BOUND, AND WHY WHAT IT LEAVES OUT IS NAMED
    The wiring kills a hook at its timeout (30 s below), and what the harness then does with the
    turn was never probed. So the run has one deadline, TIME_BUDGET after it starts: each git call
    gets min(GIT_TIMEOUT, the time left), no call is opened once the deadline passed, and a call the
    deadline cut short is told apart from one that exceeded GIT_TIMEOUT — skipping it like a failed
    call would hand on a partly measured repository as measured. A repository the bound never
    reached, or interrupted partway (its untracked files included), is named as not measured with
    the cap's semantics: in the reason when the measured part has a finding, as a block of its own
    when it is clean, then a message on the Stop that follows. MAX_DIFF_LINES is shared the same
    way: each child gets what the ones before it left. The bound holds for a single repository too,
    where every untracked file costs one git call.

    The cost it bounds, measured 2026-10-04 for the whole hook (process + git), clean diff, 3 runs
    each. Before #261, one repository: 0.65-0.82 s on a 9p mount (a real project under /mnt/d in
    WSL; an earlier, unrecorded series read 1.11-2.12 s) and 0.09-0.16 s on tmpfs. This version, on
    tmpfs, small fixture repositories: 0.11-0.12 s for one, 0.16-0.18 s for a workspace root of 10
    clean children and 0.21-0.23 s for 20 — about 5 ms per extra child, the four git calls a clean
    child costs; on 9p, 1.53-1.89 s over 6 runs for a real workspace root of 3 children (one
    project the size above, two near-empty repositories). So 20 s holds about two dozen children the size of that 9p project (20 / 0.82;
    about nine at the slow series) and far more small ones on tmpfs: the cost follows each child's
    size and untracked files, not only how many children there are. A workspace that does not fit
    blocks once per turn, naming what was left out; the exits are ending the turn from inside the
    child (only its repository is then measured) or LOCALE_RITE_MODE=inform.

WHY `stop_hook_active` NEVER BLOCKS TWICE
    The harness sets `stop_hook_active: true` on the Stop that follows a block. This hook blocks
    once; on the next Stop it returns only a `systemMessage` naming what is still in Portuguese and
    lets the turn end. The second turn is the last chance, not a loop: whoever read the reason and did
    not rename has decided. The bundle's own cap (8 consecutive blocks) stays as the second net.

THE PROSE DIRECTION (issue #179)
    When the work tree root carries `.code-locale` with `prose: pt-BR` (or `en`), the same diff is
    measured a second time by the prose detector beside the check (`check-prose-locale.py`): a
    comment or docstring with strong evidence of the wrong language blocks the turn in the same
    reason as an identifier finding; a Markdown paragraph, or a fragment with weak evidence, is a
    `systemMessage` that never blocks; a declaration the detector cannot read is named once per Stop
    — in a `systemMessage` when the diff is otherwise clean, at the tail of the block reason or of
    the second-Stop message when identifier findings stand — so a typo cannot switch the direction
    off in silence. Without the declaration nothing about prose is measured, and this hook decides
    exactly as before #179.

KNOWN LIMIT — what this hook does NOT see
    - Everything the prose detector declares it does not measure (strings and log messages, languages
      other than Portuguese and English, function words rather than a dictionary, a block or a fence
      opened on a line the diff did not add); and prose anywhere when `.code-locale` is absent.
    - A file committed inside the same turn: the diff is against HEAD, and a commit moves HEAD.
    - Another repository when `cwd` is already inside one (knowing what the turn wrote elsewhere
      would take the transcript); a repository more than one level below a workspace root; and a
      working directory outside any work tree with no direct child that carries `.git`.
    - A `.git` that git cannot open — a file naming a gitdir that does not exist exits with `fatal:
      not a git repository` and rc=128 — reads as "not a work tree": that directory is treated as a
      workspace root and only its children that hold `.git` are measured, where the write-time
      hooks' filesystem walk calls it a repository root. A child like that is skipped, never blocks.
    - Any directory whose direct children are clones is a workspace root — a home directory holding
      a dotfile clone included — and every child is measured, a foreign clone too; the exits are
      that child's `.identifier-locale-allow` and `LOCALE_RITE_MODE=inform`.
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
    - Measuring a child of a workspace root runs the clean filters its own config and attributes
      declare (`filter.<x>.clean`), as `git diff` typed there would; only `core.fsmonitor` is
      pinned off.
    - `git diff` rewrites the measured repository's index, holding `.git/index.lock` for that
      moment, when two or more tracked files are stat-dirty, and GIT_OPTIONAL_LOCKS=0 does not stop
      it (measured on git 2.47.3): a concurrent `git commit` there can meet the lock.
    - A diff longer than MAX_DIFF_LINES (one cap for every child of a workspace root), or a run
      longer than TIME_BUDGET: the rest is not measured, and the hook SAYS so, naming the children
      it left out (the first MAX_NAMED_CHILDREN, then how many more) — in the reason when it has
      findings, and as a block of its own when the measured part is clean. A git call that fails,
      or exceeds GIT_TIMEOUT while the bound still runs, skips what it was reading: the diff of one
      untracked file skips that file alone, and its repository still counts as measured; any other
      call skips the whole repository, and the hook is silent when it was the only one — the one
      case where "cannot measure" becomes "does not block", because a gate that cannot measure must
      not hold the turn forever. A call the bound cut short is not that case: its repository is
      named as not measured.
    - Advisory findings (`en-unknown`): the check itself declares them non-gating; this hook runs
      without the English word list and never blocks on a question.
    - Whatever the check itself cannot see (open vocabulary, the escapes its docstring declares).
    - Only `LOCALE_RITE_MODE=inform` silences it for a whole session; `locale-ok:` and
      `.identifier-locale-allow` are per name and per path. The variable is the one issue #137 gives
      the write gate (`locale-rite.py`, same name, same value); until #137 merges, this hook is its
      only reader — one variable per rite, not per hook.

Wiring (~/.claude/settings.json), beside any Stop hook already there — TIME_BUDGET stays below its
timeout:

    "hooks": {
      "Stop": [
        {"hooks": [{"type": "command",
                    "command": "python3 ~/ai-skills/claude/global/hooks/locale-stop-gate.py",
                    "timeout": 30}]}
      ]
    }

Like personal-rules.md, this is the maintainer's config — edit the message and the cap to match your
own process instead of adopting it blindly.

Modes: (default) read one payload from stdin   |   --selftest assert the decisions against temporary
git repositories and workspace roots.
Any other argument prints usage to stderr and exits 2 — the same contract as the sibling hooks, so a
misspelt flag cannot fall through to the stdin path and exit 0.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# The check lives in the skill that owns the doctrine. parents[3] of this file is the repository
# root (hooks -> global -> claude -> root); the path is resolved, never guessed, and a miss exits
# silently — the same rule as locale-rite.py.
CHECK_PATH = Path(__file__).resolve().parents[3] / "skills/code-locale/references/check-identifier-locale.py"
# The prose detector ships beside the check and imports it by path; a miss leaves the prose
# direction silent, never the whole hook.
PROSE_CHECK_PATH = CHECK_PATH.parent / "check-prose-locale.py"

# Declared, not silent: past this many diff lines the rest is not measured and the reason says so.
# One cap for the whole run: from a workspace root, each child gets what the ones before it left.
MAX_DIFF_LINES = 4000
# Per git call. The harness kills slow hooks; a git that does not answer skips what it was reading —
# one untracked file, or else its repository — and the hook is silent when nothing else was measured.
GIT_TIMEOUT = 5
# One deadline for the whole run, in seconds, below the 30 s the wiring gives the hook (see the
# docstring): every git call gets min(GIT_TIMEOUT, the time left), and what the bound leaves
# unmeasured is named, never dropped.
TIME_BUDGET = 20
# Measured caps in the bundle (see the docstring): truncating here keeps the tail we choose — the
# exits — rather than the tail the harness chooses.
REASON_CAP = 2000
SYSTEM_MESSAGE_CAP = 4000
# The children a limit names as not measured, at most; the rest are counted. The list sits in the
# reason's tail, which `capped` never trims: ten names of 30 characters take about 330 of the 2000,
# the header, the note, the exits and the ellipsis about 1040, and the findings keep the rest.
MAX_NAMED_CHILDREN = 10
# NUL in the first 8 KiB is git's own binary heuristic.
BINARY_PROBE_BYTES = 8192
# The diff shape scan_diff reads, pinned against ~/.gitconfig (see the docstring): every git call
# gets GIT_PIN, every diff gets DIFF_FLAGS. Measured: `diff.external` empties stdout,
# `diff.mnemonicPrefix` renames `b/` to `w/`, `core.quotePath` (default true) quotes `relatório.py`.
# `core.fsmonitor` in a measured repository's own .git/config is a command `git diff` runs (measured
# on git 2.47.3), and from a workspace root that is every child's: pinned off, it runs nothing.
GIT_PIN = ["--no-pager", "-c", "core.quotePath=false", "-c", "core.fsmonitor=false"]
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
PROSE_HEADER = (
    "CODE-LOCALE (stop gate): the turn is ending with uncommitted changes that carry a comment or "
    "docstring not in the prose language .code-locale declares — or a non-English name in the "
    "machine layer. Whatever wrote them — an edit tool, a shell heredoc, sed — the diff is what is "
    "measured. Translate or rename before ending the turn, or take one of the exits at the end.\n\n"
)
PROSE_ADVISORY_MESSAGE = (
    "code-locale: {n} uncommitted prose fragment{plural} read{third} as {lang} while .code-locale declares "
    "{declared} (Markdown or weak evidence — advisory, not blocking):\n"
)
PROSE_ERROR_MESSAGE = (
    "code-locale: the prose direction is OFF this turn because .code-locale could not be read — {error}"
)
# {limit} is "<n> lines" (the cap) or "the <s> s time bound"; {what} is "the rest of the diff"
# inside one work tree, or the `<child>/` names the limit left out from a workspace root (`left_out`).
TRUNCATED_NOTE = (
    "\n\n[diff truncated at {limit}; NOT measured: {what} — run `check-identifier-locale.py --diff -` "
    "on the full diff (`git -C <repo> diff HEAD`) before trusting a clean result]"
)
# The cap or the time bound ended the measurement and the measured part is clean: an unmeasured tail
# is not a clean result, so the gate blocks once and says how to measure the rest (then the second
# Stop reports and lets go). The list goes last, so a cut at the cap shortens the list and never the
# instructions. `git diff HEAD` alone fails at a workspace root, hence `-C <repo>`.
UNMEASURED_REASON = (
    "CODE-LOCALE (stop gate): the uncommitted diff was measured only up to {limit}. Nothing "
    "non-English was found in the measured part, but the rest was NOT measured, and an unmeasured "
    "tail is not a clean result. Before ending the turn, run the check on each unmeasured diff — "
    "`git -C <repo> diff HEAD | python3 {check} --diff -`, plus `git -C <repo> diff --no-index "
    "/dev/null <path>` for each untracked file — and rename or waive what it reports; then end the "
    "turn again (the next Stop reports without blocking). If the bulk is generated, commit it or list "
    "it in .gitignore so the gate measures what the turn wrote; from a workspace root, ending the turn "
    "inside one child measures that child alone. NOT measured: {what}."
)
UNMEASURED_MESSAGE = (
    "code-locale: the turn is ending with an uncommitted diff measured only up to {limit} (second "
    "Stop — not blocking again); NOT measured: {what}. Run `git -C <repo> diff HEAD | python3 {check} "
    "--diff -` on each before trusting it."
)
FOOTER = (
    "\n\nExits: `# locale-ok: <reason>` on the line or the line above (a name or a comment alike); the "
    "token or path in `.identifier-locale-allow` at the root of the repository that holds the file "
    "(the only exit for a file name; from a workspace root, a path entry — a comment's included — is "
    "the path without its `<child>/` prefix, in that child's allowlist); `LOCALE_RITE_MODE=inform` for "
    "the whole session. Doctrine: the code-locale skill."
)
ELLIPSIS = "\n    … more findings elided; run the check on the diff for the rest."


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
    """Import the prose detector by path. None when absent or failing to load: the prose direction is
    then silent, and the identifier direction is unaffected."""
    if not PROSE_CHECK_PATH.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("check_prose_locale", PROSE_CHECK_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def prose_findings(prose, check, root: str, lines: list) -> "tuple[list, list, str | None]":
    """(gating, advisory, declaration error) for the diff, all empty where the root declares nothing."""
    if prose is None:
        return [], [], None
    found, _boundary = prose.find_declaration(Path(root))
    if found is None:
        return [], [], None
    try:
        declared = prose.load_declaration(found)
    except prose.DeclarationError as exc:
        return [], [], str(exc)
    if declared is None:
        return [], [], None
    allow = check.load_allowlist(Path(root))
    findings = prose.scan_diff(iter(line + "\n" for line in lines), declared, allow)
    gating = [f for f in findings if not f.advisory]
    advisory = [f for f in findings if f.advisory]
    return gating, advisory, None


def is_prose(f) -> bool:
    return hasattr(f, "fragment")


def brief(prefix: str, f) -> str:
    """One line per finding for the second-stop message, its path under the `<child>/` prefix a
    workspace root gives it. A path finding carries line 0 (there is no line): print the path alone
    rather than `:0`."""
    where = f"{prefix}{f.path}{':' + str(f.line) if f.line else ''}"
    if is_prose(f):
        return f'  {where}: {f.kind} reads as {f.lang}, repo prose is {f.declared}: "{f.preview()}"'
    return f"  {where}: {f.token}  [{f.tier}]"


class OutOfTime(Exception):
    """The time bound ended: no git call is opened past it, and a call it cut short ends here rather
    than as a git timeout — the repository is then named as not measured, never skipped."""


def run_git(args: list, cwd: str, deadline: float, env=None) -> "tuple[int, str] | None":
    """(returncode, stdout), or None when git is missing, does not answer within GIT_TIMEOUT, or
    cannot be started. Raises OutOfTime once `deadline` (a time.monotonic() value) has passed, and
    when a call the deadline shortened below GIT_TIMEOUT does not answer before it."""
    timeout = min(GIT_TIMEOUT, deadline - time.monotonic())
    if timeout <= 0:
        raise OutOfTime                  # a zero or negative timeout would still start the process
    try:
        run = subprocess.run(["git", *GIT_PIN, *args], cwd=cwd, env=env, capture_output=True,
                             text=True, errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        if timeout < GIT_TIMEOUT:
            raise OutOfTime from None    # the deadline cut it short: not a git that hangs
        return None
    except (OSError, ValueError):
        return None
    return run.returncode, run.stdout


def child_repos(directory: str) -> "list[str]":
    """Names of the direct subdirectories of `directory` that hold `.git`, sorted by name.

    The backlog skill's workspace: a directory whose subdirectories are git repos. One level only,
    hidden directories included, `.git` as a directory or a file (a linked work tree, a submodule),
    sorted so the reason reads the same on every run; a directory that cannot be listed has none.
    """
    # lean: every child holding .git is measured -> read workspace.repos from backlog.yml when a
    # measured foreign clone is reported as noise
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


def uncommitted_diff(root: str, max_lines: int, deadline: float, env=None,
                     vendored=None) -> "tuple[list, str | None] | None":
    """(diff lines, stop) for the work tree at `root` — or None when git fails there, or a call
    exceeds GIT_TIMEOUT, so a repository git cannot read is skipped and never blocks.

    `stop` is None when the whole diff was read, "cap" when `max_lines` ended it and "time" when the
    deadline did: the lines are then the measured part, and the rest was NOT measured. The deadline
    is also checked before each untracked file, not only before a git call, because skipping an
    empty or binary file costs a stat and a read, which is not free on a 9p mount.

    `vendored(Path) -> bool` names the untracked paths that never enter the diff (the check's own
    vendored rule): filtering them AFTER the scan let an unignored `build/` eat the whole cap.
    """
    lines: list = []
    stop = None

    def take(text: str) -> bool:
        """Append diff text; False once the cap is reached (callers stop asking git)."""
        nonlocal stop
        for line in text.splitlines():
            if len(lines) >= max_lines:
                stop = "cap"
                return False
            lines.append(line)
        return True

    try:
        head = run_git(["rev-parse", "--verify", "-q", "HEAD"], root, deadline, env)
        if head is None:
            return None
        if head[0] == 0:
            base = "HEAD"
        else:
            empty = run_git(["hash-object", "-t", "tree", "/dev/null"], root, deadline, env)
            base = empty[1].strip() if empty and empty[0] == 0 and empty[1].strip() else EMPTY_TREE_SHA1

        tracked = run_git(["diff", *DIFF_FLAGS, base], root, deadline, env)
        if tracked is None or tracked[0] not in (0, 1):
            return None
        if not take(tracked[1]):
            return lines, stop

        others = run_git(["ls-files", "--others", "--exclude-standard", "-z"], root, deadline, env)
        if others is None or others[0] != 0:
            return None
        for rel in others[1].split("\0"):
            if not rel:
                continue
            if time.monotonic() >= deadline:
                raise OutOfTime
            if vendored is not None and vendored(Path(rel)):
                continue
            if not is_measurable(Path(root) / rel):
                continue
            added = run_git(["diff", *DIFF_FLAGS, "--no-index", "/dev/null", rel], root, deadline, env)
            if added is None or added[0] not in (0, 1):
                continue                 # one unreadable path must not silence the rest
            if not take(added[1]):
                break
    except OutOfTime:
        return lines, "time"             # partly measured: named as such, never handed on as measured
    return lines, stop


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


def left_out(unmeasured: list) -> str:
    """The `{what}` a limit's message names: "the rest of the diff" inside one work tree; from a
    workspace root, the first MAX_NAMED_CHILDREN children it left out, then how many more."""
    if not any(unmeasured):
        return "the rest of the diff"
    more = len(unmeasured) - MAX_NAMED_CHILDREN
    shown = ", ".join(unmeasured[:MAX_NAMED_CHILDREN])
    return f"{shown} and {more} more" if more > 0 else shown


def error_note(errors: list) -> str:
    """One line per declaration the detector could not read; each names its own file."""
    return "".join("\n\n" + PROSE_ERROR_MESSAGE.format(error=error) for error in errors)


# Findings travel as (prefix, finding) pairs: `<child>/` from a workspace root, empty inside a work
# tree. The prefix goes in front of the first line of each render() and is never written into the
# finding, so the allowlist line a path finding prints last stays relative to the child.
def block_reason(findings: list, note: str, errors: list) -> str:
    body = "\n".join(prefix + f.render() for prefix, f in findings)
    tail = note + error_note(errors) + FOOTER
    head = PROSE_HEADER if any(is_prose(f) for _prefix, f in findings) else HEADER
    return capped(head, body, tail, REASON_CAP)


def advisory_message(advisory: list, errors: list) -> str:
    if errors:
        return error_note(errors).lstrip("\n")[:SYSTEM_MESSAGE_CAP]
    n = len(advisory)
    first = advisory[0][1]
    head = PROSE_ADVISORY_MESSAGE.format(n=n, plural="s" if n != 1 else "", third="" if n != 1 else "s",
                                         lang=first.lang, declared=first.declared)
    return capped(head, "\n".join(brief(prefix, f) for prefix, f in advisory), "", SYSTEM_MESSAGE_CAP)


def remaining_message(findings: list, note: str, errors: list) -> str:
    names = [f for _prefix, f in findings if not is_prose(f)]
    prose = [f for _prefix, f in findings if is_prose(f)]
    parts = []
    if names:
        parts.append(f"{len(names)} non-English name{'s' if len(names) != 1 else ''}")
    if prose:
        parts.append(f"{len(prose)} comment{'s' if len(prose) != 1 else ''}/docstring{'s' if len(prose) != 1 else ''} "
                     f"in the wrong language")
    verb = "rename/translate" if names and prose else "translate" if prose else "rename"
    head = (f"code-locale: the turn is ending with {' and '.join(parts)} still uncommitted "
            f"(second Stop — not blocking again; {verb} or waive before committing):\n")
    body = "\n".join(brief(prefix, f) for prefix, f in findings)
    tail = note + error_note(errors)
    return capped(head, body, tail, SYSTEM_MESSAGE_CAP)


def evaluate(payload: dict, check, env=None, max_lines: int = MAX_DIFF_LINES,
             time_budget: float = TIME_BUDGET) -> "dict | None":
    """The whole decision, isolated from stdin and stdout so the selftest can drive it.

    `env` is the process environment the mode is read from and git is run with; the selftest hands
    its own so that no case mutates os.environ. `max_lines` exists so the truncation path is testable
    without a 4000-line fixture, and `time_budget` so the time bound is testable without a 20-second
    one.
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
    deadline = time.monotonic() + time_budget
    git_env = None if env is None else dict(env)
    findings, advisory, errors, unmeasured = [], [], [], []
    stop = None                          # "cap" or "time" once a limit ended the measurement
    try:
        # Only a bound shorter than GIT_TIMEOUT can end before this first call answers; that
        # OutOfTime, like a git that is missing or hangs, locates nothing and blocks nothing.
        top = run_git(["rev-parse", "--show-toplevel"], cwd, deadline, git_env)
        if top is None:
            return None
        if top[0] == 0:
            if not top[1].strip():
                return None
            work_trees = [("", top[1].strip())]
        else:
            # Not inside a work tree: a workspace root measures each child that holds .git, and a
            # directory without one stays silent, as before.
            work_trees = [(name + "/", os.path.join(cwd, name)) for name in child_repos(cwd)]
        prose = load_prose()
        lines_left = max_lines
        for prefix, root in work_trees:
            if stop:
                unmeasured.append(prefix)        # never reached: the cap or the bound came first
                continue
            try:
                if prefix:                       # a child: its root as git resolves it
                    found = run_git(["rev-parse", "--show-toplevel"], root, deadline, git_env)
                    if found is None or found[0] != 0 or not found[1].strip():
                        continue                 # git cannot read this child: skipped, never blocks
                    root = found[1].strip()
                measured = uncommitted_diff(root, lines_left, deadline, git_env,
                                            vendored=lambda rel: check.is_vendored(rel))
            except OutOfTime:
                measured = [], "time"
            if measured is None:
                continue                         # git failed or exceeded GIT_TIMEOUT: skipped
            lines, stop = measured
            if stop:
                unmeasured.append(prefix)        # interrupted partway: named, never taken as measured
            lines_left -= len(lines)
            if not lines:
                continue
            try:
                gating = gating_findings(check, root, lines)
                prose_gating, prose_advisory, prose_error = prose_findings(prose, check, root, lines)
            except (OSError, ValueError):
                continue                         # its allowlist or .code-locale unreadable: skipped
            findings.extend((prefix, f) for f in gating)
            findings.extend((prefix, f) for f in prose_gating)
            advisory.extend((prefix, f) for f in prose_advisory)
            errors.extend([prose_error] if prose_error else [])
    except Exception:
        return None                      # a check that crashes must not crash the turn
    active = bool(payload.get("stop_hook_active"))
    fill = None
    if stop:
        fill = {"limit": f"{max_lines} lines" if stop == "cap" else f"the {time_budget:g} s time bound",
                "what": left_out(unmeasured),
                "check": str(CHECK_PATH)}
    if not findings:
        if not fill:
            if advisory or errors:
                return {"systemMessage": advisory_message(advisory, errors)}
            return None
        # Clean up to a limit is not clean: the rest was not measured, and silence would say it was.
        if active:
            return {"systemMessage": UNMEASURED_MESSAGE.format(**fill)[:SYSTEM_MESSAGE_CAP]}
        return {"decision": "block", "reason": UNMEASURED_REASON.format(**fill)[:REASON_CAP]}
    note = TRUNCATED_NOTE.format(**fill) if fill else ""
    if active:
        return {"systemMessage": remaining_message(findings, note, errors)}
    return {"decision": "block", "reason": block_reason(findings, note, errors)}


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

    def claim(name: str, ok: bool) -> None:
        """An assertion beside a decision: printed like one, not counted as one."""
        print(f"  {'OK     ' if ok else 'FAILED '} {name}")
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

        # ── the prose direction: measured only where the work tree root declares it (#179) ──
        prose = load_prose()
        print(f"  {'OK     ' if prose else 'FAILED '} prose detector loads from {PROSE_CHECK_PATH.name}")
        if not prose:
            failed.append("prose detector missing")
        en_comment = "# compute the total for the order and apply the discount before saving\ntotal = 0\n"
        pt_comment = "# calcula o total do pedido e aplica o desconto antes de salvar\ntotal = 0\n"
        repo = _repo(tmp, env, "prose-silent")
        (repo / "orders" / "total.py").write_text(en_comment)
        case("prose: without .code-locale an English comment is not measured", "silent",
             evaluate(_payload(repo), check, env))
        repo = _repo(tmp, env, "prose-declared")
        (repo / prose.DECLARATION_FILE).write_text("prose: pt-BR\n")
        case("prose: a declared repository with a clean diff is silent", "silent",
             evaluate(_payload(repo), check, env))
        (repo / "orders" / "total.py").write_text(en_comment)
        blocked_prose = evaluate(_payload(repo), check, env)
        case("prose: heredoc-written English comment blocks where .code-locale says pt-BR", "block", blocked_prose)
        prose_reason_ok = (bool(blocked_prose) and blocked_prose["reason"].startswith("CODE-LOCALE (stop gate)")
                           and 'orders/total.py:1: [gating] comment reads as en, repo prose is pt' in blocked_prose["reason"]
                           and blocked_prose["reason"].endswith(FOOTER) and len(blocked_prose["reason"]) <= REASON_CAP)
        print(f"  {'OK     ' if prose_reason_ok else 'FAILED '} prose: the reason names the path, the line, the fragment and the exits")
        if not prose_reason_ok:
            failed.append("prose reason")
        second = evaluate(_payload(repo, active=True), check, env)
        case("prose: second stop reports the comment and does not block", "message", second)
        second_ok = bool(second) and second["systemMessage"].startswith(
            "code-locale: the turn is ending with 1 comment/docstring in the wrong language still uncommitted") \
            and "translate or waive" in second["systemMessage"] and "non-English name" not in second["systemMessage"]
        print(f"  {'OK     ' if second_ok else 'FAILED '} prose: the second-stop message counts prose apart and says translate, not rename")
        if not second_ok:
            failed.append("prose second-stop head")
        (repo / "orders" / "total.py").write_text(pt_comment)
        case("prose: translated to Portuguese, the turn ends", "silent", evaluate(_payload(repo), check, env))
        (repo / "orders" / "total.py").write_text("# locale-ok: upstream comment kept verbatim\n" + en_comment)
        case("prose: locale-ok on the line above the comment is silent", "silent",
             evaluate(_payload(repo), check, env))
        (repo / "orders" / "total.py").unlink()
        (repo / "NOTES.md").write_text("This paragraph explains how the order total is computed for the customer.\n")
        advisory = evaluate(_payload(repo), check, env)
        case("prose: a Markdown paragraph in English is a message, not a block", "message", advisory)
        advisory_ok = bool(advisory) and "NOTES.md:1: paragraph reads as en" in advisory["systemMessage"] \
            and "advisory" in advisory["systemMessage"]
        print(f"  {'OK     ' if advisory_ok else 'FAILED '} prose: the message names the paragraph as advisory")
        if not advisory_ok:
            failed.append("prose md message")
        (repo / "orders" / "total.py").write_text(en_comment + "usuario_count = 1\n")
        both = evaluate(_payload(repo), check, env)
        case("prose: identifier and comment findings block in one reason", "block", both)
        both_ok = bool(both) and "usuario_count" in both["reason"] and "comment reads as en" in both["reason"]
        print(f"  {'OK     ' if both_ok else 'FAILED '} prose: that reason carries both kinds of finding")
        if not both_ok:
            failed.append("prose combined reason")
        (repo / "orders" / "total.py").unlink()
        (repo / "NOTES.md").unlink()
        (repo / prose.DECLARATION_FILE).write_text("prose: en\n")
        (repo / "orders" / "total.py").write_text(pt_comment)
        case("prose: under prose: en a Portuguese comment blocks", "block", evaluate(_payload(repo), check, env))
        (repo / "orders" / "total.py").write_text(en_comment)
        case("prose: under prose: en an English comment is silent", "silent", evaluate(_payload(repo), check, env))
        (repo / prose.DECLARATION_FILE).write_text("prose: klingon\n")
        unreadable = evaluate(_payload(repo), check, env)
        case("prose: an unreadable declaration is a message naming the file, never a block", "message", unreadable)
        unreadable_ok = bool(unreadable) and prose.DECLARATION_FILE in unreadable["systemMessage"] \
            and "pt-BR" in unreadable["systemMessage"]
        print(f"  {'OK     ' if unreadable_ok else 'FAILED '} prose: the message names the accepted values")
        if not unreadable_ok:
            failed.append("prose unreadable declaration")
        case("prose: LOCALE_RITE_MODE=inform silences the prose direction too", "silent",
             evaluate(_payload(repo), check, {**env, MODE_VAR: INFORM}))
        # the unreadable declaration is still named when an identifier finding carries the block
        (repo / "orders" / "u.py").write_text("usuario_total = 1\n")
        both_err = evaluate(_payload(repo), check, env)
        case("prose: an identifier finding beside an unreadable declaration blocks", "block", both_err)
        err_named = bool(both_err) and "klingon" in both_err["reason"] and "could not be read" in both_err["reason"] \
            and both_err["reason"].endswith(FOOTER)
        print(f"  {'OK     ' if err_named else 'FAILED '} prose: that reason names the unreadable declaration")
        if not err_named:
            failed.append("prose error beside identifier finding")
        both_err_second = evaluate(_payload(repo, active=True), check, env)
        case("prose: the same on the second stop is a message", "message", both_err_second)
        err_second_ok = bool(both_err_second) and "klingon" in both_err_second["systemMessage"] \
            and both_err_second["systemMessage"].startswith("code-locale: the turn is ending with 1 non-English name still")
        print(f"  {'OK     ' if err_second_ok else 'FAILED '} prose: the second-stop message names it too")
        if not err_second_ok:
            failed.append("prose error on second stop")
        (repo / "orders" / "u.py").unlink()
        (repo / prose.DECLARATION_FILE).write_text("prose: pt-BR\n")
        (repo / "orders" / "total.py").write_text(en_comment + "usuario_count = 1\n")
        mixed = evaluate(_payload(repo, active=True), check, env)
        case("prose: identifier and comment on the second stop is a message", "message", mixed)
        mixed_ok = bool(mixed) and mixed["systemMessage"].startswith(
            "code-locale: the turn is ending with 1 non-English name and 1 comment/docstring in the wrong language still") \
            and "rename/translate or waive" in mixed["systemMessage"]
        print(f"  {'OK     ' if mixed_ok else 'FAILED '} prose: that message counts names and prose apart")
        if not mixed_ok:
            failed.append("prose mixed second stop")
        (repo / "orders" / "total.py").unlink()

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

        # ── a workspace root: each child work tree measured at its own root, in one reason (#261) ──
        ws = tmp / "workspace"
        child = _repo(ws, env, "child-a")
        _repo(ws, env, "child-b")
        case("workspace root: clean children are silent", "silent", evaluate(_payload(ws), check, env))
        (ws / "notes").mkdir()
        (ws / "notes" / "servico_cliente.py").write_text(PT_SOURCE)
        case("workspace root: a subdirectory without .git is not measured", "silent",
             evaluate(_payload(ws), check, env))
        (child / "servico_cliente.py").write_text(PT_SOURCE)
        found = evaluate(_payload(ws), check, env)
        case("workspace root: an untracked portuguese file in a child blocks", "block", found)
        reason = found.get("reason", "") if found else ""
        claim("workspace root: the reason names child-a/servico_cliente.py, its identifiers and the exits",
              "\nchild-a/servico_cliente.py: servico_cliente" in reason
              and "\nchild-a/servico_cliente.py:1: buscar_cliente" in reason
              and "child-b/" not in reason and reason.endswith(FOOTER) and len(reason) <= REASON_CAP)
        found = evaluate(_payload(ws, active=True), check, env)
        case("workspace root: the second stop reports and does not block", "message", found)
        claim("workspace root: the second-stop message names the file under its child",
              bool(found)
              and "\n  child-a/servico_cliente.py:1: buscar_cliente" in found.get("systemMessage", ""))
        # the allowlist line a file-name finding prints is the one that silences it in that child
        (child / "servico_cliente.py").write_text(EN_SOURCE)      # its name is now the only finding
        found = evaluate(_payload(ws), check, env)
        case("workspace root: a file whose only finding is its name blocks", "block", found)
        printed = (found.get("reason", "") if found else "").splitlines()
        hint = next((printed[i + 1].strip() for i, line in enumerate(printed[:-1])
                     if line.endswith(check.ALLOWLIST_FILE + ":")), "")
        claim("workspace root: the allowlist line that reason prints is relative to the child",
              hint == "servico_cliente.py"
              and any(line.startswith("child-a/servico_cliente.py: servico_cliente") for line in printed))
        (child / check.ALLOWLIST_FILE).write_text(hint + "\n")
        case("workspace root: that line in the child's allowlist silences it", "silent",
             evaluate(_payload(ws), check, env))
        (child / check.ALLOWLIST_FILE).write_text("child-a/servico_cliente.py\n")
        case("workspace root: the prefixed path in the child's allowlist does not", "block",
             evaluate(_payload(ws), check, env))

        # one child's allowlist and .code-locale speak for that child alone
        ws = tmp / "workspace-pair"
        child, sibling = _repo(ws, env, "child-a"), _repo(ws, env, "child-b")
        (child / check.ALLOWLIST_FILE).write_text("fatura_id\n")
        for repo in (child, sibling):
            (repo / "orders" / "billing.py").write_text("fatura_id = 1\n")
        found = evaluate(_payload(ws), check, env)
        case("workspace root: one child's allowlist does not speak for another", "block", found)
        claim("workspace root: only the child without the entry is named",
              bool(found) and "\nchild-b/orders/billing.py:1: fatura_id" in found.get("reason", "")
              and "child-a/" not in found.get("reason", ""))
        for repo in (child, sibling):
            (repo / "orders" / "billing.py").unlink()
            (repo / "orders" / "total.py").write_text(en_comment)
        (child / prose.DECLARATION_FILE).write_text("prose: pt-BR\n")
        found = evaluate(_payload(ws), check, env)
        case("workspace root: one child's .code-locale does not speak for another", "block", found)
        claim("workspace root: only the declaring child's comment is named",
              bool(found)
              and "\nchild-a/orders/total.py:1: [gating] comment reads as en" in found.get("reason", "")
              and "child-b/" not in found.get("reason", ""))
        # a comment's allowlist entry follows the same rule: the path without its <child>/ prefix
        (child / check.ALLOWLIST_FILE).write_text("orders/total.py\n")
        case("workspace root: a comment's path in the child's allowlist, unprefixed, silences it", "silent",
             evaluate(_payload(ws), check, env))
        (child / check.ALLOWLIST_FILE).write_text("child-a/orders/total.py\n")
        case("workspace root: the same path under its <child>/ prefix does not", "block",
             evaluate(_payload(ws), check, env))

        # a child git cannot open is skipped without blocking; the others are still measured
        ws = tmp / "workspace-broken"
        (ws / "broken").mkdir(parents=True)
        (ws / "broken" / ".git").write_text("gitdir: /nowhere/.git/worktrees/x\n")
        (ws / "broken" / "servico_cliente.py").write_text(PT_SOURCE)
        (_repo(ws, env, "child-a") / "servico_cliente.py").write_text(PT_SOURCE)
        found = evaluate(_payload(ws), check, env)
        case("workspace root: a child git cannot open is skipped, the others still measured", "block", found)
        claim("workspace root: the skipped child is neither reported nor named as not measured",
              bool(found) and "\nchild-a/servico_cliente.py" in found.get("reason", "")
              and "broken/" not in found.get("reason", "") and "NOT measured" not in found.get("reason", ""))

        # an entry whose stat fails (a symlink to itself: ELOOP) hides only itself
        ws = tmp / "workspace-loop"
        (_repo(ws, env, "child-a") / "servico_cliente.py").write_text(PT_SOURCE)
        os.symlink("loop", ws / "loop")
        found = evaluate(_payload(ws), check, env)
        case("workspace root: a symlink loop beside a child does not hide the child", "block", found)
        claim("workspace root: that reason names child-a/servico_cliente.py",
              bool(found) and "\nchild-a/servico_cliente.py:1: buscar_cliente" in found.get("reason", ""))

        # a child whose allowlist cannot be read is skipped alone, as one git cannot read; before,
        # the exception reached evaluate's catch-all and silenced every child
        ws = tmp / "workspace-unreadable"
        child = _repo(ws, env, "child-a")
        allowlist = child / check.ALLOWLIST_FILE
        allowlist.write_bytes(b"relat\xf3rio\n")            # cp1252 from a Windows editor, not UTF-8
        (child / "a1.py").write_text(EN_SOURCE)             # a diff, so that allowlist is read
        (_repo(ws, env, "child-b") / "servico_cliente.py").write_text(PT_SOURCE)
        found = evaluate(_payload(ws), check, env)
        case("workspace root: one child's allowlist that is not UTF-8 does not silence another", "block", found)
        claim("workspace root: that reason names child-b/servico_cliente.py",
              bool(found) and "\nchild-b/servico_cliente.py:1: buscar_cliente" in found.get("reason", ""))
        allowlist.write_text("fatura_id\n")
        allowlist.chmod(0)
        try:
            if os.access(allowlist, os.R_OK):               # root reads it anyway: nothing to prove
                print("  SKIP    workspace root: one child's unreadable (mode 000) allowlist does not "
                      "silence another  ->  the file stays readable to this user")
            else:
                found = evaluate(_payload(ws), check, env)
                case("workspace root: one child's unreadable (mode 000) allowlist does not silence another",
                     "block", found)
                claim("workspace root: that reason names child-b/servico_cliente.py too",
                      bool(found) and "\nchild-b/servico_cliente.py:1: buscar_cliente" in found.get("reason", ""))
        finally:
            allowlist.chmod(0o644)

        # a child's own .git/config can name a command `git diff` runs (core.fsmonitor); measuring a
        # child from a workspace root must not run it
        ws = tmp / "workspace-fsmonitor"
        child = _repo(ws, env, "child-a")
        marker = tmp / "fsmonitor-ran"
        monitor = tmp / "fsmonitor-bin" / "monitor"
        monitor.parent.mkdir()
        monitor.write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 1\n')
        monitor.chmod(0o755)
        _git(child, env, "config", "core.fsmonitor", str(monitor))
        service = child / "orders" / "service.py"
        service.write_text(service.read_text() + "total = 1\n")
        # the precondition: a plain `git diff HEAD` runs the monitor here, or the claim proves nothing
        # (a TMPDIR mounted noexec cannot run it)
        subprocess.run(["git", "diff", "HEAD"], cwd=child, env=env, capture_output=True)
        if not marker.exists():
            print("  SKIP    workspace root: a child's own core.fsmonitor runs nothing when the gate "
                  "measures it  ->  a plain git diff did not run the monitor here")
        else:
            marker.unlink()
            evaluate(_payload(ws), check, env)
            claim("workspace root: a child's own core.fsmonitor runs nothing when the gate measures it",
                  not marker.exists())

        # one line cap for every child: each diff fits under it alone, not all of them together, and
        # what the cap leaves out is named, child by child
        ws = tmp / "workspace-cap"
        generated = "".join(f"value_{i} = {i}\n" for i in range(50))     # 56 diff lines
        child, sibling, last = (_repo(ws, env, name) for name in ("child-a", "child-b", "child-c"))
        (child / "servico_cliente.py").write_text(PT_SOURCE)
        (child / "zz_generated.py").write_text(generated)                  # child-a: 64 lines
        (sibling / "zz_generated.py").write_text(generated)                # 120 together: cut here
        (last / "servico_cliente.py").write_text(PT_SOURCE)                # never reached
        found = evaluate(_payload(ws), check, env, max_lines=100)
        case("workspace root: a diff over the shared cap still blocks", "block", found)
        claim("workspace root: the reason names the children the shared cap left out",
              bool(found) and "\nchild-a/servico_cliente.py:1: buscar_cliente" in found.get("reason", "")
              and "NOT measured: child-b/, child-c/" in found.get("reason", "")
              and "child-c/servico_cliente.py" not in found.get("reason", ""))
        # many children left out: the list sits in the tail `capped` never trims, so it is cut at
        # MAX_NAMED_CHILDREN; uncut, 71 names pushed the exits past the cap and elided every finding
        ws = tmp / "workspace-many"
        child = _repo(ws, env, "child-a")
        (child / "servico_cliente.py").write_text(PT_SOURCE)
        (child / "zz_generated.py").write_text("".join(f"value_{i} = {i}\n" for i in range(200)))
        template = _repo(tmp, env, "workspace-many-template")     # one git init, copied 70 times
        for i in range(70):
            shutil.copytree(template, ws / f"zz-workspace-child-{i:02d}", symlinks=True)
        found = evaluate(_payload(ws), check, env, max_lines=100)
        reason = found.get("reason", "") if found else ""
        case("workspace root: a finding beside 71 children the cap left out blocks", "block", found)
        claim("workspace root: that reason keeps the finding and the exits within the cap",
              len(reason) <= REASON_CAP and reason.endswith(FOOTER)
              and "\nchild-a/servico_cliente.py:1: buscar_cliente" in reason
              and "zz-workspace-child-08/ and 61 more" in reason)

        # the time bound: a git wrapper hangs on one chosen call, and the deadline cuts it short —
        # through the same subprocess timeout a git that really hangs meets. A case whose claim
        # needs the part measured BEFORE the cut gets twice the bound: that part takes about 45 ms
        # here, and a loaded runner must not move the cut into it.
        bound = 0.5
        wrapper = tmp / "slow-bin" / "git"
        wrapper.parent.mkdir()
        calls = tmp / "slow-git.log"
        wrapper.write_text("#!/bin/sh\n"
                           f'echo "$(pwd) $*" >> "{calls}"\n'
                           'case "$(pwd) $*" in *"${SLOW_GIT_WHEN:-//never//}"*) exec sleep 10 ;; esac\n'
                           f'exec "{shutil.which("git")}" "$@"\n')
        wrapper.chmod(0o755)
        slow = {**env, "PATH": f"{wrapper.parent}{os.pathsep}{env.get('PATH', '')}"}
        # the cut is the child's LAST untracked file: a cut call skipped like a failed one would leave
        # nothing after it to give the child away, and the child would pass as measured
        ws = tmp / "workspace-time"
        child = _repo(ws, env, "child-a")
        for name in ("a1.py", "a2.py"):
            (child / name).write_text(EN_SOURCE)
        (_repo(ws, env, "child-b") / "servico_cliente.py").write_text(PT_SOURCE)
        partway = {**slow, "SLOW_GIT_WHEN": "/dev/null a2.py"}
        calls.write_text("")
        found = evaluate(_payload(ws), check, partway, time_budget=bound)
        case("workspace root: the time bound ending partway through a child's untracked files blocks once",
             "block", found)
        opened = calls.read_text()
        claim("workspace root: that child and the one never reached are named; the last gets no git call",
              bool(found) and found.get("reason", "").endswith("NOT measured: child-a/, child-b/.")
              and "servico_cliente" not in found.get("reason", "")
              and "/child-b " not in opened)
        case("workspace root: a child cut partway, on the second stop, is a message", "message",
             evaluate(_payload(ws, active=True), check, partway, time_budget=bound))
        ws = tmp / "workspace-time-before"
        for name in ("child-a", "child-b", "child-c"):
            (_repo(ws, env, name) / "servico_cliente.py").write_text(PT_SOURCE)
        before = {**slow, "SLOW_GIT_WHEN": "/child-b --no-pager"}
        calls.write_text("")
        found = evaluate(_payload(ws), check, before, time_budget=2 * bound)
        case("workspace root: the time bound ending before a child keeps what was measured before it",
             "block", found)
        opened = calls.read_text()
        claim("workspace root: the children it left out are named, and the last one never gets a git call",
              bool(found) and "\nchild-a/servico_cliente.py:1: buscar_cliente" in found.get("reason", "")
              and "NOT measured: child-b/, child-c/" in found.get("reason", "")
              and "child-c/servico_cliente.py" not in found.get("reason", "")
              and "/child-b " in opened and "/child-c " not in opened)
        case("workspace root: children never reached, on the second stop, are a message", "message",
             evaluate(_payload(ws, active=True), check, before, time_budget=bound))
        # one repository answers to the same bound: what it measured before the cut is reported, and
        # the rest is named the same way
        repo = _repo(tmp, env, "time-single")
        (repo / "a1.py").write_text(PT_SOURCE)
        (repo / "a2.py").write_text(EN_SOURCE)
        found = evaluate(_payload(repo), check, partway, time_budget=2 * bound)
        case("one repository: the time bound ending partway blocks once", "block", found)
        claim("one repository: the reason keeps the measured part's finding and names the rest",
              bool(found) and "\na1.py:1: buscar_cliente" in found.get("reason", "")
              and f"[diff truncated at the {2 * bound:g} s time bound; NOT measured: the rest of the diff"
              in found.get("reason", ""))
        # past the deadline no git process is started at all (a zero or negative timeout would still
        # start one), and a first call that never ran locates nothing, so nothing blocks
        started = []
        real_run = subprocess.run
        subprocess.run = lambda *args, **options: started.append(args) or real_run(*args, **options)
        try:
            spent = evaluate(_payload(repo), check, env, time_budget=0)
        finally:
            subprocess.run = real_run
        claim("past the deadline no git process is started, and the hook stays silent",
              spent is None and not started)

        # skipping untracked files counts against the bound too: each costs a stat and a read
        class SlowSkip:
            """The shipped check, except that judging one path takes the whole bound."""

            def __getattr__(self, name):
                return getattr(check, name)

            def is_vendored(self, path):
                if path == Path("vendor/x.py"):
                    time.sleep(bound)
                return check.is_vendored(path)

        repo = _repo(tmp, env, "time-skips")
        (repo / "a1.py").write_text(EN_SOURCE)
        (repo / "vendor").mkdir()
        (repo / "vendor" / "x.py").write_text(EN_SOURCE)
        (repo / "zz_empty.py").touch()
        case("one repository: the bound ending among skipped untracked files blocks once", "block",
             evaluate(_payload(repo), SlowSkip(), env, time_budget=bound))

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
    print(f"selftest OK: {decisions} decisions in temporary git repositories and workspace roots (the "
          f"prose direction with and without .code-locale, the shared line cap and the time bound "
          f"included), 2 output shapes, {malformed} malformed payloads, plus the argv contract")
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
