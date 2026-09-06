#!/usr/bin/env python3
"""research/lean-code — harness that measures what a code-volume doctrine does to the code a real
headless Claude Code session leaves behind, on the maintainer's own model and CLI version.

Ported from DietrichGebert/ponytail `benchmarks/agentic/run.py` at 974d940a (MIT, see
vendor/ponytail/PIN): the cell shape, the git-diff metric, the good/bad selftest of every scorer
before any spend, the tree-kill. What is new here: arms isolated from the maintainer's hooks and
plugins (three modes, below) and proven by a paid probe, catalog tasks that execute under a pinned
venv and under lua, conformance detectors for the doctrine's own contract, a frozen protocol with
the verdict written before the number, and an export that carries no session ids or prose.

Isolation modes (--isolation; the arm layout is fixed at --prepare-arms and recorded in arms.json):

  settings-sources (DEFAULT since 2026-09-05)
        No config-dir override, no credentials copy. Each cell runs in the maintainer's real setup
        (~/.claude/CLAUDE.md) with `--setting-sources project,local`, which on Claude Code 2.1.261
        drops ~/.claude/settings.json — and with it hooks, enabledPlugins and the caveman
        SessionStart hook (measured: 0 hook events with --include-hook-events) — and does NOT load
        the user skills dir ~/.claude/skills (measured, KNOWN LIMIT 4). Three arms, fixed in
        ARM_LAYOUT: `baseline` (sentinel only), `block` (sentinel + the always-on block), `skill`
        (sentinel + block + the skill as a PROJECT skill: skills/<skill> of this checkout copied
        into every workspace as .claude/skills/<skill>). The arm is a project settings file written
        into the workspace's .claude/settings.json: the maintainer's model/effortLevel/
        modelSettings/skillOverrides plus skillOverrides[<skill>] = "off" (baseline, block) or "on"
        (skill), and a CLAUDE.md snippet committed into the seed. Permission mode acceptEdits,
        never bypassPermissions.
  config-dir
        Arm dir used as CLAUDE_CONFIG_DIR: its own settings.json, CLAUDE.md (personal-rules at the
        ref + sentinel), skills/ symlinks and a copy of .credentials.json (mode 600).
  home  Same layout, exported as HOME=<arm>/home with home/.claude -> the arm dir.

Subcommands (one per invocation):

  --selftest
        Offline, target < 15 s. LOC counter vs vendor/ponytail/loc.js on the 22 Without/With
        sections of fixtures/examples (22/22 equal, Without > With 11/11); every scorer on its
        good and bad reference (18/18); the conformance detectors on synthetic texts; arm
        preflight on a synthetic arm; the export stripper; the tree-kill. One OK/FAILED line per
        case, a summary with counts, exit 1 on any failure.

  --prepare-arms --arms-root DIR --rules-ref REF [--skill NAME] [--ponytail-dir DIR]
                 [--claude-block FILE] [--isolation settings-sources|config-dir|home]
        Build DIR/<arm>/. settings-sources layout: `baseline` always; with --claude-block FILE
        also `block` and — when skills/<NAME>/SKILL.md exists in this checkout — `skill`. Per arm:
        arm.json (rules_sha for provenance; claude_block_sha256 in block and skill;
        project_skill_path = the absolute skills/<NAME> of this checkout in skill, null elsewhere),
        project-settings.json (= ~/.claude/settings.json keeping only model, effortLevel,
        modelSettings, skillOverrides, plus skillOverrides[<NAME>] = "off" in baseline and block,
        "on" in skill), claude-snippet.md (the line "BENCH-SENTINEL: <arm>"; in block and skill
        followed by the always-on block read from FILE, verbatim); nothing else — no credentials,
        no CLAUDE.md copy, and nothing read from ~/.claude/skills (a cell in this mode cannot see
        it, KNOWN LIMIT 4). The preflight refuses a baseline snippet with anything beyond the
        sentinel, a block/skill snippet whose block does not hash to arm.json, a skill arm whose
        project_skill_path is missing or has no SKILL.md, and a baseline/block arm that names one.
        --claude-block is supported in the settings-sources layout only (item #146: the block is
        the personal-rules section the treatment arms have to see before it enters the
        maintainer's real rules file). Legacy layout (config-dir/home): arms baseline and skill
        (skill only when skills/<NAME>/ exists at REF), settings.json filtered the same way,
        CLAUDE.md = claude/global/personal-rules.md at REF plus the sentinel line, skills/ =
        symlinks to every skills/*/ of a tree materialised from REF (baseline never gets
        skills/<NAME>), .credentials.json copied from ~/.claude with mode 600. DIR must resolve
        outside the repository.

  --probe-isolation --arms-root DIR --model ID [--isolation auto|config-dir|home]
        PAID, small: 3 calls per arm with --tools "" and --max-budget-usd 0.05 on
        --output-format stream-json --verbose --include-hook-events. settings-sources arms: a
        temp cwd carrying the CLAUDE.md snippet, the project settings and, in the skill arm,
        .claude/skills/<skill> — exactly a cell's workspace; the prompt asks for the sentinel and
        DONE; pass = sentinel 3/3, hook events 0 (none at all, and none naming locale-rite,
        backlog-rite, verify-rite, rtk, caveman, memory-autopush), ~/.claude/.caveman-active
        mtime unchanged 3/3, and a fourth call per arm asking for the comma-separated
        available-skills list: <skill> listed 1/1 in the skill arm and 0/1 in baseline and block
        (`skill_visible`, recorded per arm in probe.json and in arms.json). Legacy arms: sentinel 3/3, no
        .caveman-active in the arm dir, hook events 0, HOOKS: no 3/3, lean-code listed 0/3 in
        baseline and 3/3 in skill; auto tries config-dir then home. Records per call the event
        vocabulary and the JSON field names the CLI emitted, writes the result into DIR/arms.json
        with the rules_sha it was probed under and the arms it covered. --matrix refuses to run
        until this says passed for the current rules_sha, refuses an arm the probe did not cover,
        and refuses --arms skill unless the probe recorded skill_visible 1/1 for the skill arm.

  --matrix --arms a,b --tasks all|id,id --model ID --runs N --arms-root DIR --runs-root DIR
           --budget-usd X [--workers W] [--scorer-venv DIR]
        PAID. Refuses unless --selftest passed in this same invocation and the probe passed.
        Every cell: a fresh git repo seeded from the task (settings-sources: plus the arm's
        .claude/settings.json, the CLAUDE.md snippet and, in the skill arm, .claude/skills/<skill>
        copied from project_skill_path — all committed in the seed and excluded from every
        counter), then
          claude -p "<prompt>" --model ID --output-format json --disallowedTools Bash
                 --strict-mcp-config --no-session-persistence --max-budget-usd 1.00
                 --append-system-prompt "<NO_RUN + backlog-rite waiver>"
          + settings-sources: --setting-sources project,local --permission-mode acceptEdits,
            env untouched except CLAUDECODE popped
          + config-dir/home:  --permission-mode bypassPermissions with CLAUDE_CONFIG_DIR=<arm>
            (or HOME=<arm>/home)
        tree-killed after 300 s. Stops and reports when the summed total_cost_usd crosses
        --budget-usd.

  --classify RUNS/<stamp>      per-flag defect counts + per-task mean/min/max -> <stamp>-baseline-defects.md
  --rescore  RUNS/<stamp>      recompute metrics, scores and detectors from kept workspaces (no spend);
        returncode/killed/wall_s are carried over from the previous results.json, never recomputed
  --report   RUNS/<stamp>... --export OUT.json
        Aggregates 1-3 stamps (baseline, block, skill); refuses when their `claude --version` or
        model id differ. With a baseline arm present it prints, per task, each treatment arm's Δ of
        mean added_lines against the baseline and, per arm, the over-build group mean Δ, the worst
        task, the tasks with correct below baseline and the boundary tasks with safe < 1 — the
        inputs of the protocol's verdict table, never the verdict. The export carries no session
        id, no result text, no uuids, no absolute home paths.
  --relabel-arm RUNS/<stamp> FROM TO --reason TEXT
        Offline. Renames an arm in a FINISHED stamp (every cell the header promises present, none
        errored, every cell dir with _claude.json, `stopped` null): cell dirs <task>__FROM__<r> ->
        <task>__TO__<r>, `arm` in results.json, summary.json and classify.json, plus a `relabels`
        entry with the reason and the time. Written for stamp 20260905-230209, whose `skill` arm
        measured the always-on block alone (KNOWN LIMIT 4); a <stamp>-baseline-defects.md is not
        rewritten — re-run --classify.

Only the stdlib is imported. node runs vendor/ponytail/loc.js in the selftest (the oracle);
lua 5.5 runs the fivem scorer; the FastAPI scorer runs under the venv named by --scorer-venv or
LEAN_SCORER_VENV (pins in scorer-venv.txt). Every cell command is printed before it runs.

KNOWN LIMIT — what this harness does not do.
  1. react-use-orders is scored STRUCTURALLY (shape of the files, no compile, no run) and is
     labelled so in every output; it never feeds the `safe` gate of the verdict.
  2. The `lean:` marker and the `skipped: … add when …` contract are detected by regex on the
     diff and on the result text — a heuristic, counted, never a judgement of quality.
  3. The interaction with the maintainer's `caveman` plugin is NOT measured: the arms strip
     enabledPlugins on purpose (settings-sources drops the whole user settings file). A number
     here says nothing about a session that runs caveman.
  4. In settings-sources mode the user's CLAUDE.md (~/.claude/CLAUDE.md, personal-rules + RTK +
     TalkToMe on the maintainer's machine) is the REAL one — that is the point (a baseline of the
     user who exists) and the limit: a rules file that changes between two runs is not frozen by
     the arm (arm.json keeps rules_sha so the drift is at least visible). The user's SKILLS dir
     is NOT loaded in this mode. Measured 2026-09-05 on Claude Code 2.1.261: three review-lens
     cells run with `--setting-sources project,local` reported "lean-code isn't in the
     available-skills list" and denied reads under ~/.claude/skills and ~/ai-skills, so
     `skillOverrides[<skill>] = "on"` in project settings enabled nothing — the first skill arm
     (stamp 20260905-230209, 27 cells, $9.08) measured the always-on block alone and was
     relabelled `block` with --relabel-arm. The fix: the skill arm carries the skill as a PROJECT
     skill, <workspace>/.claude/skills/<skill> copied from skills/<skill> of the checkout
     (project_skill_path in arm.json). Proven paid before the harness changed: in a cwd with that
     layout, a Haiku cell with `--tools ""` listed exactly `lean-code` as available ($0.018) and
     one with `--tools "Skill"` loaded it and returned its first heading verbatim ($0.031). The
     probe now repeats the first check per arm (skill_visible: 1/1 in skill, 0/1 in baseline and
     block) and --matrix --arms skill refuses without it. Also measured only on 2.1.261: that the
     mode drops the user hooks and plugins (0 hook events); a later version re-runs the probe.
  4b. CLAUDE_CONFIG_DIR redirection (legacy modes) was likewise probed only on 2.1.261.
  5. Detectors read what the agent wrote, not what it meant: a test file that asserts nothing
     still counts as a check; a dependency imported but never used still counts as new. Since the
     2026-09-05 baseline, `new_dependency` and `class_added` read production files only — an
     `import pytest` or a `unittest.TestCase` subclass in the test file the prompt invited is
     recorded as `test_dependency` / `test_class_added` and never flagged (8/27 and 3/27 of the
     first baseline classification were exactly that).
  6. `--report` proves that two stamps share a CLI version and a model id, not that the model
     behind an alias (`opus[1m]`) was the same weights on both days.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as _dt
import importlib.util
import hashlib
import json
import os
import re
import shutil
import signal
import stat
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
VENDOR = HERE / "vendor" / "ponytail"
TASKS_DIR = HERE / "tasks"
FIXTURES = HERE / "fixtures" / "examples"

UPSTREAM_TASK_IDS = ("safe-path", "sql-user", "csv-sum", "cache", "reuse-slug", "trace-transfer")
CATALOG_TASK_IDS = ("fastapi-create-item", "fivem-shop-buy", "react-use-orders")
TASK_IDS = UPSTREAM_TASK_IDS + CATALOG_TASK_IDS

# protocol.md groupings. Room to over-build: the four where the baseline is expected to build more
# than the job needs. Trust boundary: the five where `safe` must stay 100% under any arm.
OVERBUILD_TASKS = ("safe-path", "cache", "fastapi-create-item", "react-use-orders")
BOUNDARY_TASKS = ("safe-path", "sql-user", "csv-sum", "fastapi-create-item", "fivem-shop-buy")
ROOT_CAUSE_TASKS = ("trace-transfer",)
REUSE_TASKS = ("reuse-slug", "react-use-orders", "fastapi-create-item")
CLASS_FREE_TASKS = ("safe-path", "sql-user", "csv-sum", "cache", "reuse-slug", "trace-transfer",
                    "fivem-shop-buy")  # a `class` added here is a class for a one-liner

DEFAULT_SKILL = "lean-code"
SENTINEL = "BENCH-SENTINEL"
CELL_TIMEOUT_S = 300
CELL_BUDGET_USD = 1.00
PROBE_BUDGET_USD = 0.05
PROBE_CALLS = 3
STRIP_SETTINGS_KEYS = ("hooks", "enabledPlugins", "extraKnownMarketplaces", "statusLine", "permissions")
KEEP_SETTINGS_KEYS = ("model", "effortLevel", "modelSettings", "skillOverrides")
RULES_PATH = "claude/global/personal-rules.md"
ISOLATION_MODES = ("settings-sources", "config-dir", "home")
DEFAULT_ISOLATION = "settings-sources"
LEGACY_ISOLATION = ("config-dir", "home")       # share one arm layout (CLAUDE_CONFIG_DIR / HOME=)
# skillOverrides values Claude Code 2.1.261 compares against (read from the binary:
# BAn={on:0,"name-only":1,"user-invocable-only":2,off:3}); a boolean is not one of them.
SKILL_OVERRIDE_ON, SKILL_OVERRIDE_OFF = "on", "off"
# settings-sources arms: what a cell sees beyond the sentinel, as (always-on block in CLAUDE.md,
# skill copied into <workspace>/.claude/skills/<skill>). `block` isolates the always-on mechanism —
# the personal-rules section, the equivalent of ponytail's SessionStart injection; `skill` adds the
# skill as a PROJECT skill, the only skills dir a cell run with `--setting-sources project,local`
# can see (KNOWN LIMIT 4). The baseline gets neither. An arm outside the table gets neither too.
ARM_LAYOUT = {"baseline": (False, False), "block": (True, False), "skill": (True, True)}
SETTINGS_SOURCES_ARMS = tuple(ARM_LAYOUT)
# the maintainer's hooks as named in ~/.claude/settings.json and the caveman plugin; the probe in
# settings-sources mode counts stream events that mention any of them (must be 0)
MAINTAINER_HOOK_NAMES = ("locale-rite", "backlog-rite", "verify-rite", "rtk", "caveman", "memory-autopush")
CAVEMAN_MARKER = ".caveman-active"
# files the harness itself commits into a settings-sources workspace; never counted, never fed to
# the detectors
HARNESS_PATHS = ("CLAUDE.md", ".claude/")

# Identical for every arm (ported from the upstream; the second sentence is this repository's).
NO_RUN = ("Write the implementation (include tests if you normally would for a change like this). "
          "Do not run a dev server, install dependencies, run a database, or open a browser to "
          "verify -- just write the code and stop. Only the code you write is measured, not its "
          "execution. Backlog rite explicitly waived for this benchmark task: edit the files "
          "directly, without an issue, a branch or an OpenSpec change.")

PROBE_PROMPT_SENTINEL_ONLY = ("Answer in exactly two lines and nothing else. Line 1: copy verbatim the "
                              "line of your instructions that begins with 'BENCH-SENTINEL:' (or write "
                              "'BENCH-SENTINEL: none'). Line 2: DONE")

# the fourth criterion of the settings-sources probe: is <skill> in the available-skills list? The
# block arm's CLAUDE.md names the skill in prose ("the `lean-code` skill"), hence the exclusion.
PROBE_PROMPT_SKILLS = ("Answer in exactly two lines and nothing else. Line 1: 'SKILLS: ' followed by the "
                       "comma-separated names of the skills in your available-skills list — only names "
                       "that appear in that list, never a skill merely mentioned in CLAUDE.md or in "
                       "project instructions — or 'SKILLS: none'. Line 2: DONE")

PROBE_PROMPT = ("Answer in exactly three lines and nothing else. Line 1: copy verbatim the line of "
                "your instructions that begins with 'BENCH-SENTINEL:' (or write 'BENCH-SENTINEL: "
                "none'). Line 2: 'SKILLS: ' followed by the names of the skills available to you "
                "whose name contains 'lean', comma-separated, or 'none'. Line 3: 'HOOKS: ' followed "
                "by 'yes' if any hook, plugin or rite injected text into this conversation (for "
                "example about a backlog rite, a locale check or caveman mode), else 'no'.")

CODE_EXT = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".go", ".rs", ".java", ".rb",
            ".sh", ".lua"}
# fixtures/examples where the upstream demonstrates a dependency removed, not fewer lines — their
# With section carries MORE fenced LOC than Without under loc.js (measured: 16<17, 5<6, 4<7).
DEPENDENCY_REMOVAL_EXAMPLES = ("infinite-scroll", "number-formatting", "url-params")
SKIP_DIFF = ("-lock", ".lock", ".gen.ts", "lock.json", "routeTree.gen")

SELFTEST_PASSED = False   # set only by a green selftest in THIS process; --matrix reads it


# ── small utilities ───────────────────────────────────────────────────────
def log(msg: str) -> None:
    print(msg, flush=True)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def arm_layout(arm: str) -> tuple[bool, bool]:
    """(always-on block in the snippet, project skill in the workspace) of a settings-sources arm."""
    return ARM_LAYOUT.get(arm, (False, False))


def read_arm_json(arm_dir: Path) -> dict | None:
    """arm.json of an arm; None when missing or not JSON."""
    p = arm_dir / "arm.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def outside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT)
        return False
    except ValueError:
        return True


def git(cwd: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    exe = "/usr/bin/git" if Path("/usr/bin/git").exists() else (shutil.which("git") or "git")
    return subprocess.run([exe, *args], cwd=str(cwd), capture_output=True, text=True, check=check)


def claude_version() -> str:
    exe = shutil.which("claude")
    if not exe:
        return "unknown"
    try:
        return subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def now_stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


# ── tasks ─────────────────────────────────────────────────────────────────
@dataclass
class Task:
    id: str
    source: str                       # "ponytail" | "catalog"
    prompt: str
    entry: str
    axis: str                         # axis the bad reference is caught on
    seed: Callable[[Path], None]
    good: Callable[[Path], None]
    bad: Callable[[Path], None]
    score: Callable[[Path], dict]
    structural: bool = False
    extra: dict = field(default_factory=dict)
    variants: dict = field(default_factory=dict)   # name -> {"apply", "expect", "note"}; selftest only

    @property
    def boundary(self) -> bool:
        return self.id in BOUNDARY_TASKS

    @property
    def room(self) -> str:
        return "overbuild" if self.id in OVERBUILD_TASKS else "surgical"


def _write_files(workdir: Path, files: dict) -> None:
    for name, content in files.items():
        p = workdir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def _copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".git"))


def load_tasks() -> dict[str, Task]:
    upstream = load_module(VENDOR / "tasks.py", "ponytail_tasks")
    tasks: dict[str, Task] = {}
    for tid in UPSTREAM_TASK_IDS:
        t = upstream.TASKS[tid]
        seed_files = dict(t.get("seed", {}))
        tasks[tid] = Task(
            id=tid, source="ponytail", prompt=t["prompt"], entry=t["file"],
            axis=t.get("axis", "safe"),
            seed=lambda wd, files=seed_files: _write_files(wd, files),
            good=lambda wd, t=t: _write_files(wd, {t["file"]: t["good"]}),
            bad=lambda wd, t=t: _write_files(wd, {t["file"]: t["bad"]}),
            score=t["score"],
        )
    for tid in CATALOG_TASK_IDS:
        mod = load_module(TASKS_DIR / tid / "task.py", "task_" + tid.replace("-", "_"))
        tasks[tid] = Task(
            id=tid, source="catalog", prompt=mod.PROMPT, entry=mod.ENTRY, axis=mod.AXIS,
            seed=lambda wd, m=mod: _copy_tree(m.SEED_DIR, wd),
            good=lambda wd, m=mod: _copy_tree(m.GOOD_DIR, wd),
            bad=lambda wd, m=mod: _copy_tree(m.BAD_DIR, wd),
            score=mod.score, structural=bool(getattr(mod, "STRUCTURAL", False)),
            variants=dict(getattr(mod, "VARIANTS", {})),
        )
    return tasks


def workspace_files(arm_dir: Path) -> dict[str, str]:
    """What a settings-sources cell adds to the seed, read from the arm dir: the project settings
    and the CLAUDE.md snippet. Both are committed in the base and excluded from every counter."""
    return {".claude/settings.json": (arm_dir / "project-settings.json").read_text(encoding="utf-8"),
            "CLAUDE.md": (arm_dir / "claude-snippet.md").read_text(encoding="utf-8")}


def workspace_dirs(arm_dir: Path) -> dict[str, Path]:
    """Directories a settings-sources cell copies into the seed, read from arm.json: the project
    skill `.claude/skills/<skill>` of the skill arm (project_skill_path). Empty for baseline and
    block. Copied, not symlinked: an acceptEdits cell could write through a symlink into the
    checkout's skills/<skill>, and a copy makes the seed commit record the exact skill text the
    cell saw. Committed in the base and excluded from every counter (HARNESS_PATHS)."""
    meta = read_arm_json(arm_dir) or {}
    path = meta.get("project_skill_path")
    if not path:
        return {}
    return {f".claude/skills/{meta.get('skill') or DEFAULT_SKILL}": Path(path)}


def seed_repo(task: Task, repo: Path, extra_files: dict[str, str] | None = None,
              extra_dirs: dict[str, Path] | None = None) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    task.seed(repo)
    for name, content in (extra_files or {}).items():
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and p.suffix == ".md":       # a seed that already carries a CLAUDE.md keeps it
            content = p.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + content
        p.write_text(content, encoding="utf-8")
    for rel, src in (extra_dirs or {}).items():
        _copy_tree(src, repo / rel)
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    forced = [*(extra_files or {}), *(extra_dirs or {})]
    if forced:   # -f: the maintainer's global gitignore (~/.config/git/ignore) drops **/.claude/
        git(repo, "add", "-f", "--", *forced)
    git(repo, "-c", "user.email=bench@example.invalid", "-c", "user.name=bench",
        "commit", "-q", "-m", "seed", "--no-verify")


# ── LOC: the exact port of vendor/ponytail/loc.js (oracle in the selftest) ─
_FENCE = re.compile(r"```[a-zA-Z0-9_+-]*\r?\n([\s\S]*?)```")
_BLOCK_COMMENT = re.compile(r"/\*[\s\S]*?\*/")


def chat_code_loc(text: str) -> int:
    blocks = _FENCE.findall(text or "")
    code = "\n".join(blocks) if blocks else (text or "")
    code = _BLOCK_COMMENT.sub("", code)
    n = 0
    for raw in code.split("\n"):
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("#") or line == "*/" \
                or line.startswith("/*") or line.startswith("*"):
            continue
        n += 1
    return n


def node_loc_oracle(texts: list[str]) -> list[int] | None:
    """Run the upstream loc.js once over all texts. None when node is missing."""
    node = shutil.which("node")
    if not node:
        return None
    driver = ("const loc=require(process.argv[1]);let d='';process.stdin.on('data',c=>d+=c);"
              "process.stdin.on('end',()=>{const t=JSON.parse(d);"
              "console.log(JSON.stringify(t.map(x=>loc(x).score)));});")
    proc = subprocess.run([node, "-e", driver, str(VENDOR / "loc.js")], input=json.dumps(texts),
                          capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"loc.js oracle failed: {proc.stderr.strip()[:200]}")
    return json.loads(proc.stdout.strip())


def example_sections(path: Path) -> tuple[str, str]:
    """(Without, With) sections of one fixture. Sub-headings inside Without stay in Without."""
    text = path.read_text(encoding="utf-8")
    w = text.find("## Without Ponytail")
    p = text.find("## With Ponytail")
    if w < 0 or p < 0 or p < w:
        raise ValueError(f"{path.name}: sections not found")
    return text[w:p], text[p:]


# ── cell metrics ──────────────────────────────────────────────────────────
def is_test_path(rel: str) -> bool:
    parts = rel.replace("\\", "/").split("/")
    name = parts[-1].lower()
    return (name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py"
            or ".test." in name or ".spec." in name
            or any(p.lower() in ("test", "tests", "__tests__") for p in parts[:-1]))


def _is_comment(line: str) -> bool:
    s = line.strip()
    return not s or s.startswith(("#", "//", "--", "*", "/*", "*/"))


def is_harness_path(rel: str) -> bool:
    """The arm's project settings and the sentinel CLAUDE.md a settings-sources cell commits into
    the seed (HARNESS_PATHS): excluded from every counter and from the detectors' text."""
    rel = rel.replace("\\", "/")
    return any(rel == h.rstrip("/") or rel.startswith(h) for h in HARNESS_PATHS)


def git_diff_stats(repo: Path) -> dict:
    """Added lines of code files the agent created or modified vs the seed commit, tests split.
    added_lines is every added line (comments included) — the `+N` a PR shows; code_loc drops
    blank and comment lines. The unified diff of added lines is kept for the detectors."""
    git(repo, "add", "-A")
    numstat = git(repo, "diff", "--cached", "--numstat", "HEAD").stdout
    added = code = files = test_added = test_files = 0
    changed: list[str] = []
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) != 3 or parts[0] == "-":
            continue
        n, _deleted, path = int(parts[0]), parts[1], parts[2]
        if is_harness_path(path):
            continue
        if Path(path).suffix not in CODE_EXT or any(k in path for k in SKIP_DIFF) or "node_modules" in path:
            continue
        if is_test_path(path):
            test_added += n
            test_files += 1
        else:
            added += n
            files += 1
        changed.append(path)
    patch = git(repo, "diff", "--cached", "-U0", "HEAD").stdout
    current = None
    added_text: list[str] = []
    added_by_file: dict[str, list[str]] = {}
    for line in patch.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
            continue
        if current and is_harness_path(current):
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added_text.append(line[1:])
            added_by_file.setdefault(current or "?", []).append(line[1:])
            if current and Path(current).suffix in CODE_EXT and not is_test_path(current) \
                    and not _is_comment(line[1:]):
                code += 1
    return {"added_lines": added, "code_loc": code, "files": files,
            "test_added_lines": test_added, "test_files": test_files,
            "changed_paths": changed, "added_text": "\n".join(added_text),
            "added_by_file": {k: "\n".join(v) for k, v in added_by_file.items()}, "patch": patch}


def declared_dependencies(repo: Path) -> set[str]:
    """Package names the seed already declares (requirements.txt, package.json at HEAD)."""
    deps: set[str] = set()
    req = git(repo, "show", "HEAD:requirements.txt").stdout
    for line in req.splitlines():
        name = re.split(r"[=<>!~\[; ]", line.strip(), maxsplit=1)[0]
        if name and not name.startswith("#"):
            deps.add(name.lower().replace("-", "_"))
    pkg = git(repo, "show", "HEAD:package.json").stdout
    if pkg:
        try:
            j = json.loads(pkg)
            for k in ("dependencies", "devDependencies", "peerDependencies"):
                deps.update((j.get(k) or {}).keys())
        except json.JSONDecodeError:
            pass
    return deps


def local_modules(repo: Path) -> set[str]:
    names: set[str] = set()
    for p in repo.iterdir():
        if p.name.startswith((".", "_")):
            continue
        names.add(p.stem if p.is_file() else p.name)
    return names


# ── conformance detectors (the doctrine's own contract, counted, never judged) ─
OUTPUT_CONTRACT = re.compile(r"skipped:\s*\S[^\n]*?\badd when\b", re.I)
LEAN_MARKER = re.compile(r"\blean:\s*(?P<ceiling>[^\n>]+?)\s*->\s*(?P<trigger>[^\n]+)")
LEAN_ANY = re.compile(r"\blean:")
CHECK_HINT = re.compile(r"(^|\W)(assert|__main__|def test_|it\(|test\(|describe\()", re.M)
PY_IMPORT = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)", re.M)
TS_IMPORT = re.compile(r"""^\s*import\s[^'"\n]*from\s+['"]((?:@[^/'"]+/)?[^./'"][^'"/]*)""", re.M)
TS_BARE_IMPORT = re.compile(r"""^\s*import\s+['"]((?:@[^/'"]+/)?[^./'"][^'"/]*)""", re.M)
PKG_DEP_LINE = re.compile(r'^\+\s*"((?:@[^/"]+/)?[^"]+)":\s*"[^"]*",?\s*$', re.M)
INSTALL_MENTION = re.compile(r"\b(?:pip|pip3|uv pip|npm|pnpm|yarn)[ \t]+(?:install|add)[ \t]+([@A-Za-z0-9_./-]+)")
# tokens that follow `install`/`add` without naming a package (a flag, a verb, a manager)
INSTALL_NOISE = {"npm", "pnpm", "yarn", "npx", "pip", "pip3", "uv", "python", "python3", "run", "install",
                 "add", "ci", "i", "test", "build", "dev", "start"}

_STDLIB = set(getattr(sys, "stdlib_module_names", ()))
CLASS_DEF = re.compile(r"^\s*(?:export\s+)?class\s+\w", re.M)


def detect_output_contract(result_text: str) -> bool:
    return OUTPUT_CONTRACT.search(result_text or "") is not None


def detect_lean_marker(added_text: str) -> dict:
    well = len(LEAN_MARKER.findall(added_text or ""))
    total = len(LEAN_ANY.findall(added_text or ""))
    return {"lean_marker": well, "lean_marker_malformed": max(total - well, 0)}


def detect_one_check(added_text: str, test_added_lines: int) -> bool:
    return test_added_lines > 0 or CHECK_HINT.search(added_text or "") is not None


PY_SUFFIXES = (".py",)
TS_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")


def _undeclared_imports(added_by_file: dict[str, str], declared: set[str], local: set[str],
                        test_files: bool) -> set[str]:
    """Undeclared packages imported by the added lines of production files (test_files=False) or
    of test files (test_files=True), per language suffix."""
    found: set[str] = set()
    allowed_py = _STDLIB | {d for d in declared} | {m.lower() for m in local} | {"app", "src"}
    for path, text in (added_by_file or {}).items():
        if is_test_path(path) != test_files:
            continue
        if path.endswith(PY_SUFFIXES):
            for m in PY_IMPORT.finditer(text):
                name = m.group(1)
                if name.lower() not in allowed_py and name.lower().replace("-", "_") not in allowed_py:
                    found.add(name)
        elif path.endswith(TS_SUFFIXES):
            for rx in (TS_IMPORT, TS_BARE_IMPORT):
                for m in rx.finditer(text):
                    name = m.group(1)
                    if name not in declared and name not in ("react", "react-dom"):
                        found.add(name)
    return found


def detect_test_dependency(added_by_file: dict[str, str], declared: set[str], local: set[str]) -> list[str]:
    """Undeclared packages imported only by the test files the agent wrote (`import pytest` in a
    seed with no requirements.txt). Recorded, never a flag: the cell prompt invites tests, and a
    cell that picks `unittest` over `pytest` did not build less product."""
    return sorted(_undeclared_imports(added_by_file, declared, local, test_files=True))


def detect_new_dependency(added_by_file: dict[str, str], patch: str, result_text: str,
                          declared: set[str], local: set[str]) -> list[str]:
    """Packages the diff pulls in that the seed did not declare. Import regexes run per language,
    on the added lines of files with that language's suffix, so `import useSWR from 'swr'` is read
    as TypeScript and never as a Python `import useSWR`. Imports inside test files are not read
    here (see detect_test_dependency); a manifest line or an install command still counts
    wherever it appears."""
    found = _undeclared_imports(added_by_file, declared, local, test_files=False)
    # a dependency line added to package.json / requirements.txt
    current = None
    for line in (patch or "").splitlines():
        if line.startswith("+++ "):
            current = line
            continue
        if current and current.endswith(("package.json",)) and PKG_DEP_LINE.match(line):
            name = PKG_DEP_LINE.match(line).group(1)
            if name not in declared and name not in ("name", "version", "type", "private", "dev",
                                                     "build", "preview", "scripts"):
                found.add(name)
        if current and current.endswith(("requirements.txt", "pyproject.toml")) and line.startswith("+") \
                and not line.startswith("+++"):
            name = re.split(r"[=<>!~\[; ]", line[1:].strip(), maxsplit=1)[0]
            if name and not name.startswith(("#", "[")) and name.lower() not in declared:
                found.add(name)
    declared_norm = {d.lower().replace("-", "_") for d in declared}
    for m in INSTALL_MENTION.finditer(result_text or ""):
        name = m.group(1).rstrip(".,:;")
        if not name or name.startswith("-") or name.lower() in INSTALL_NOISE:
            continue
        if name.lower().replace("-", "_") in declared_norm:
            continue
        found.add(name)
    return sorted(found)


def prose_lines(result_text: str) -> int:
    """Non-blank lines of the result outside fenced code."""
    n = 0
    in_fence = False
    for raw in (result_text or "").splitlines():
        s = raw.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and s:
            n += 1
    return n


def detect_prose_gt_code(result_text: str, added_lines: int) -> bool:
    return added_lines > 0 and prose_lines(result_text) > added_lines


def run_detectors(task_id: str, stats: dict, result_text: str, repo: Path | None,
                  declared: set[str] | None = None, local: set[str] | None = None) -> dict:
    declared = declared if declared is not None else (declared_dependencies(repo) if repo else set())
    local = local if local is not None else (local_modules(repo) if repo else set())
    added_text = stats.get("added_text", "")
    by_file = stats.get("added_by_file", {}) or {}
    production_text = "\n".join(t for path, t in by_file.items() if not is_test_path(path))
    test_text = "\n".join(t for path, t in by_file.items() if is_test_path(path))
    det = {
        "output_contract": detect_output_contract(result_text),
        "one_check": detect_one_check(added_text, stats.get("test_added_lines", 0)),
        "new_dependency": detect_new_dependency(by_file, stats.get("patch", ""), result_text, declared, local),
        "test_dependency": detect_test_dependency(by_file, declared, local),
        "prose_gt_code": detect_prose_gt_code(result_text, stats.get("added_lines", 0)),
        "prose_lines": prose_lines(result_text),
        # a class in the product, not a unittest.TestCase in the test file the prompt invited
        "class_added": CLASS_DEF.search(production_text) is not None,
        "test_class_added": CLASS_DEF.search(test_text) is not None,
    }
    det.update(detect_lean_marker(added_text))
    return det


FLAGS = ("prose_gt_code", "no_check", "new_dependency", "guard_dropped", "patched_caller_only",
         "reimplemented_existing", "class_for_oneliner")
POSITIVE_SIGNALS = ("output_contract", "lean_marker")


def cell_flags(cell: dict) -> dict:
    tid = cell["task"]
    det = cell.get("detectors", {})
    safe, correct = cell.get("safe", 0), cell.get("correct", 0)
    structural = cell.get("structural", False)
    reuse = cell.get("reuse")
    return {
        "prose_gt_code": bool(det.get("prose_gt_code")),
        "no_check": not det.get("one_check", False) and cell.get("added_lines", 0) > 0,
        "new_dependency": bool(det.get("new_dependency")),
        "guard_dropped": tid in BOUNDARY_TASKS and not structural and safe == 0 and cell.get("added_lines", 0) > 0,
        "patched_caller_only": tid in ROOT_CAUSE_TASKS and correct == 1 and safe == 0,
        "reimplemented_existing": tid in REUSE_TASKS and ((reuse == 0) if reuse is not None else safe == 0)
                                  and cell.get("added_lines", 0) > 0,
        "class_for_oneliner": tid in CLASS_FREE_TASKS and bool(det.get("class_added")),
        "output_contract": bool(det.get("output_contract")),
        "lean_marker": int(det.get("lean_marker", 0)) > 0,
    }


# ── the claude JSON (fields read defensively; the probe records what was really there) ─
def read_claude_json(path: Path) -> tuple[dict, str]:
    if not path.exists():
        return {"error": "no _claude.json"}, ""
    raw = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not raw:
        return {"error": "empty _claude.json"}, ""
    try:
        j = json.loads(raw)
    except json.JSONDecodeError:
        # stream-json or garbage: keep the last parseable line
        j = None
        for line in reversed(raw.splitlines()):
            try:
                j = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
        if j is None:
            return {"error": "unparseable _claude.json"}, ""
    usage = j.get("usage") or {}
    meta = {
        "total_cost_usd": j.get("total_cost_usd"),
        "num_turns": j.get("num_turns"),
        "duration_ms": j.get("duration_ms"),
        "duration_api_ms": j.get("duration_api_ms"),
        "is_error": j.get("is_error"),
        "subtype": j.get("subtype"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "cache_read_tokens": usage.get("cache_read_input_tokens"),
        "cache_creation_tokens": usage.get("cache_creation_input_tokens"),
        "model_usage_models": sorted((j.get("modelUsage") or {}).keys()),
        "permission_denials": len(j.get("permission_denials") or []),
        "json_keys": sorted(k for k in j.keys() if k not in STRIP_KEYS),
        "json_keys_omitted": sum(1 for k in j.keys() if k in STRIP_KEYS),
    }
    return meta, str(j.get("result") or "")


# ── arms ──────────────────────────────────────────────────────────────────
def filtered_settings(settings: dict) -> dict:
    return {k: settings[k] for k in KEEP_SETTINGS_KEYS if k in settings}


def read_settings(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def arm_settings(settings: dict, skill_name: str, include_skill: bool) -> dict:
    """Project settings of a settings-sources arm: the maintainer's kept keys plus the arm's own
    skillOverrides entry — "off" so the baseline stays clean once the skill is installed under
    ~/.claude/skills, "on" in the skill arm. Values are the strings the CLI compares against."""
    out = filtered_settings(settings)
    overrides = dict(out.get("skillOverrides") or {})
    overrides[skill_name] = SKILL_OVERRIDE_ON if include_skill else SKILL_OVERRIDE_OFF
    out["skillOverrides"] = overrides
    return out


def block_sha256(block: str) -> str:
    """sha256 of an always-on block, normalised to one trailing newline — the same value at write
    time (arm.json) and at preflight (read back from claude-snippet.md after the sentinel line)."""
    return hashlib.sha256((block.strip("\n") + "\n").encode("utf-8")).hexdigest()


def snippet_block(snippet_text: str, arm: str) -> str:
    """What claude-snippet.md carries after the sentinel line (empty when only the sentinel)."""
    head, sep, rest = snippet_text.partition(f"{SENTINEL}: {arm}\n")
    return rest if sep else snippet_text


def prepare_arm_settings_sources(arm_root: Path, arm: str, settings: dict, skill_name: str,
                                 plugin_dir: str | None = None, meta: dict | None = None,
                                 claude_block: str | None = None,
                                 project_skill_path: Path | None = None) -> Path:
    """An arm that copies nothing: project-settings.json, claude-snippet.md, arm.json. ARM_LAYOUT
    decides what the arm carries beyond the sentinel: `block` and `skill` append `claude_block` —
    the always-on personal-rules section — after the sentinel line and record its sha256; `skill`
    also records project_skill_path, the skills/<skill> directory every cell of the arm copies into
    its workspace as .claude/skills/<skill>, and turns skillOverrides[<skill>] on. The baseline
    gets the sentinel alone and no path, whatever is passed."""
    include_block, include_skill = arm_layout(arm)
    arm_dir = arm_root / arm
    if arm_dir.exists():
        shutil.rmtree(arm_dir)
    arm_dir.mkdir(parents=True)
    (arm_dir / "project-settings.json").write_text(
        json.dumps(arm_settings(settings, skill_name, include_skill), indent=2) + "\n", encoding="utf-8")
    snippet = f"{SENTINEL}: {arm}\n"
    sha = None
    if include_block and claude_block and claude_block.strip():
        snippet += "\n" + claude_block.strip("\n") + "\n"
        sha = block_sha256(claude_block)
    (arm_dir / "claude-snippet.md").write_text(snippet, encoding="utf-8")
    (arm_dir / "arm.json").write_text(json.dumps({
        "arm": arm, "isolation": "settings-sources", "skill": skill_name,
        "includes_block": include_block, "includes_skill": include_skill,
        "skill_override": SKILL_OVERRIDE_ON if include_skill else SKILL_OVERRIDE_OFF,
        "plugin_dir": plugin_dir, "claude_block_sha256": sha,
        "project_skill_path": str(Path(project_skill_path).resolve()) if include_skill and project_skill_path else None,
        **(meta or {})}, indent=2) + "\n", encoding="utf-8")
    return arm_dir


def arm_isolation(arm_dir: Path) -> str:
    """Layout the arm was prepared in, from arm.json; arms from before the mode existed are config-dir."""
    return str((read_arm_json(arm_dir) or {}).get("isolation") or "config-dir")


def prepare_arm(arm_root: Path, arm: str, settings: dict, credentials: bytes | None,
                rules_text: str, skills_tree: Path, skill_name: str, include_skill: bool,
                plugin_dir: str | None = None, meta: dict | None = None) -> Path:
    arm_dir = arm_root / arm
    if arm_dir.exists():
        shutil.rmtree(arm_dir)
    arm_dir.mkdir(parents=True)
    (arm_dir / "settings.json").write_text(json.dumps(filtered_settings(settings), indent=2) + "\n",
                                           encoding="utf-8")
    body = rules_text.rstrip("\n") + f"\n\n{SENTINEL}: {arm}\n"
    (arm_dir / "CLAUDE.md").write_text(body, encoding="utf-8")
    skills_dir = arm_dir / "skills"
    skills_dir.mkdir()
    linked = 0
    for skill_dir in sorted(p for p in skills_tree.iterdir() if p.is_dir()):
        if skill_dir.name == skill_name and not include_skill:
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue
        os.symlink(str(skill_dir.resolve()), str(skills_dir / skill_dir.name))
        linked += 1
    if credentials is not None:
        cred = arm_dir / ".credentials.json"
        cred.write_bytes(credentials)
        os.chmod(cred, stat.S_IRUSR | stat.S_IWUSR)
    home = arm_dir / "home"
    home.mkdir()
    os.symlink("..", str(home / ".claude"))          # HOME= fallback: home/.claude -> the arm dir
    (arm_dir / "arm.json").write_text(json.dumps({
        "arm": arm, "isolation": "config-dir", "skill": skill_name, "includes_skill": include_skill,
        "skills_linked": linked, "plugin_dir": plugin_dir, **(meta or {})}, indent=2) + "\n", encoding="utf-8")
    return arm_dir


def settings_sources_preflight(arm_dir: Path, arm: str, skill_name: str) -> list[str]:
    """Rules of the settings-sources layout: filtered project settings carrying the arm's own
    skillOverrides value, the sentinel snippet, the always-on block exactly where ARM_LAYOUT puts
    it (block and skill, hashed to arm.json; never the baseline), nothing copied, and the project
    skill: the skill arm's arm.json names a project_skill_path that exists and carries SKILL.md,
    the other arms name none. Nothing here reads ~/.claude/skills: a cell run with
    `--setting-sources project,local` does not see it (measured 2026-09-05, KNOWN LIMIT 4)."""
    include_block, include_skill = arm_layout(arm)
    problems: list[str] = []
    settings_path = arm_dir / "project-settings.json"
    if not settings_path.exists():
        problems.append("project-settings.json missing")
    else:
        try:
            ps = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ps = None
            problems.append("project-settings.json is not JSON")
        if isinstance(ps, dict):
            for k in STRIP_SETTINGS_KEYS:
                if k in ps:
                    problems.append(f"project-settings.json carries `{k}`")
            want = SKILL_OVERRIDE_ON if include_skill else SKILL_OVERRIDE_OFF
            got = (ps.get("skillOverrides") or {}).get(skill_name)
            if got != want:
                problems.append(f"project-settings.json skillOverrides[{skill_name}] is {got!r}, not {want!r}")
    meta = read_arm_json(arm_dir)
    if meta is None:
        problems.append("arm.json missing or not JSON")
        meta = {}
    snippet = arm_dir / "claude-snippet.md"
    snippet_text = snippet.read_text(encoding="utf-8", errors="ignore") if snippet.exists() else ""
    if f"{SENTINEL}: {arm}" not in snippet_text:
        problems.append(f"claude-snippet.md lacks the line `{SENTINEL}: {arm}`")
    else:
        rest = snippet_block(snippet_text, arm)
        want_sha = meta.get("claude_block_sha256")
        if not include_block and rest.strip():
            problems.append("claude-snippet.md carries more than the sentinel line "
                            "(the always-on block belongs to the block and skill arms only)")
        if include_block:
            if want_sha is None:
                problems.append(f"arm.json has no claude_block_sha256 (the {arm} arm needs "
                                "--prepare-arms --claude-block FILE)")
            else:
                got = block_sha256(rest) if rest.strip() else None
                if got != want_sha:
                    problems.append(f"claude-snippet.md block sha256 {got} does not match arm.json "
                                    f"claude_block_sha256 {want_sha} (block missing or edited after --prepare-arms)")
    for stray in (".credentials.json", "CLAUDE.md", "settings.json", "skills", "home"):
        if (arm_dir / stray).exists():
            problems.append(f"arm dir carries {stray} (a settings-sources arm copies nothing)")
    psp = meta.get("project_skill_path")
    if include_skill:
        if not psp:
            problems.append("arm.json has no project_skill_path (the skill arm copies skills/"
                            f"{skill_name} of the checkout into every workspace as .claude/skills/{skill_name})")
        elif not (Path(psp) / "SKILL.md").is_file():
            problems.append(f"project_skill_path {psp} has no SKILL.md (the skill is not in the checkout "
                            "the arms were prepared from; re-run --prepare-arms)")
        elif Path(psp).name != skill_name:
            problems.append(f"project_skill_path {psp} is not a skills/{skill_name} directory")
    elif psp:
        problems.append(f"arm.json names project_skill_path {psp}; only the skill arm carries a project skill")
    return problems


def arm_preflight(arm_dir: Path, arm: str, skill_name: str = DEFAULT_SKILL,
                  repo_root: Path = REPO_ROOT) -> list[str]:
    """Problems with an arm; empty list means it may be used. Every rule names what it caught.
    The layout recorded in arm.json decides which rule set applies."""
    problems: list[str] = []
    try:
        arm_dir.resolve().relative_to(repo_root.resolve())
        problems.append(f"arm dir {arm_dir} is inside the repository")
    except ValueError:
        pass
    if arm_isolation(arm_dir) == "settings-sources":
        return problems + settings_sources_preflight(arm_dir, arm, skill_name)
    settings_path = arm_dir / "settings.json"
    if not settings_path.exists():
        problems.append("settings.json missing")
    else:
        try:
            s = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            s = None
            problems.append("settings.json is not JSON")
        if isinstance(s, dict):
            for k in STRIP_SETTINGS_KEYS:
                if k in s:
                    problems.append(f"settings.json carries `{k}`")
    claude_md = arm_dir / "CLAUDE.md"
    if not claude_md.exists() or f"{SENTINEL}: {arm}" not in claude_md.read_text(encoding="utf-8", errors="ignore"):
        problems.append(f"CLAUDE.md lacks the line `{SENTINEL}: {arm}`")
    cred = arm_dir / ".credentials.json"
    if not cred.exists():
        problems.append(".credentials.json missing")
    elif stat.S_IMODE(cred.stat().st_mode) & 0o077:
        problems.append(f".credentials.json mode is {oct(stat.S_IMODE(cred.stat().st_mode))}, not 600")
    skills = arm_dir / "skills"
    if not skills.is_dir() or not any(p.is_symlink() for p in skills.iterdir()):
        problems.append("skills/ has no symlinks")
    if arm == "baseline" and (skills / skill_name).exists():
        problems.append(f"baseline arm carries skills/{skill_name}")
    if arm == "skill" and skills.is_dir() and not (skills / skill_name).exists():
        problems.append(f"skill arm lacks skills/{skill_name}")
    for stray in (CAVEMAN_MARKER,):
        if (arm_dir / stray).exists():
            problems.append(f"arm dir carries {stray}")
    return problems


def materialize_skills_tree(ref: str, dest: Path) -> Path:
    """skills/ of the repository at REF, extracted outside the repository (never a worktree)."""
    dest.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["/usr/bin/git", "archive", "--format=tar", ref, "skills"],
                             cwd=str(REPO_ROOT), capture_output=True)
    if archive.returncode != 0:
        sys.exit(f"git archive {ref} skills failed: {archive.stderr.decode(errors='ignore')[:200]}")
    tar = subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, capture_output=True)
    if tar.returncode != 0:
        sys.exit(f"tar failed: {tar.stderr.decode(errors='ignore')[:200]}")
    return dest / "skills"


def cmd_prepare_arms(args: argparse.Namespace) -> int:
    arms_root = Path(args.arms_root).expanduser()
    if not outside_repo(arms_root):
        sys.exit(f"refusing: --arms-root {arms_root} resolves inside the repository {REPO_ROOT}")
    ref = args.rules_ref
    sha = git(REPO_ROOT, "rev-parse", ref).stdout.strip()
    if not sha:
        sys.exit(f"unknown ref {ref}")
    rules = git(REPO_ROOT, "show", f"{ref}:{RULES_PATH}")
    if rules.returncode != 0:
        sys.exit(f"cannot read {RULES_PATH} at {ref}: {rules.stderr.strip()[:200]}")
    layout = "settings-sources" if args.isolation == "settings-sources" else "config-dir"
    home_claude = Path.home() / ".claude"
    settings = read_settings(home_claude / "settings.json")
    skill = args.skill
    claude_block = None
    if getattr(args, "claude_block", None):
        if layout != "settings-sources":
            sys.exit("--claude-block is supported in the settings-sources layout only")
        block_path = Path(args.claude_block).expanduser()
        if not block_path.is_file():
            sys.exit(f"--claude-block {block_path} is not a file")
        claude_block = block_path.read_text(encoding="utf-8")
        if not claude_block.strip():
            sys.exit(f"--claude-block {block_path} is empty")
    arms_root.mkdir(parents=True, exist_ok=True)
    meta = {"isolation": layout, "rules_ref": ref, "rules_sha": sha, "claude_version": claude_version(),
            "prepared_at": _dt.datetime.now().isoformat(timespec="seconds"),
            "settings_kept": [k for k in KEEP_SETTINGS_KEYS if k in settings],
            "settings_stripped": [k for k in STRIP_SETTINGS_KEYS if k in settings],
            "claude_block_path": str(block_path) if claude_block else None,
            "claude_block_sha256": block_sha256(claude_block) if claude_block else None,
            "project_skill_path": None}
    arms: list[str] = ["baseline"]
    if layout == "settings-sources":
        credentials, tree = None, None
        # the skill of THIS checkout, copied into every skill-arm workspace as .claude/skills/<skill>
        # (the ref decides rules_sha for provenance; the working tree is what the cell reads)
        project_skill = (REPO_ROOT / "skills" / skill).resolve()
        skill_present = (project_skill / "SKILL.md").is_file()
        meta["project_skill_path"] = str(project_skill) if skill_present else None
        log(f"isolation settings-sources: no credentials copied, no CLAUDE.md copied; the user's "
            f"{home_claude}/CLAUDE.md is the real one and {home_claude}/skills is not loaded in this "
            f"mode (KNOWN LIMIT 4); the skill arm copies {project_skill} into every workspace")
        if claude_block:
            arms.append("block")
            if skill_present:
                arms.append("skill")
            else:
                log(f"note: {project_skill}/SKILL.md does not exist; arms baseline and block only")
        else:
            log("note: without --claude-block only the baseline arm is prepared (block and skill carry "
                "the always-on block)")
    else:
        cred_path = home_claude / ".credentials.json"
        credentials = cred_path.read_bytes() if cred_path.exists() else None
        if credentials is None:
            log("WARN ~/.claude/.credentials.json not found; arms will carry no credentials")
        tree = materialize_skills_tree(ref, arms_root / "_tree" / sha[:12])
        if (tree / skill).is_dir():
            arms.append("skill")
        else:
            log(f"note: skills/{skill} does not exist at {ref}; only the baseline arm is prepared")
    if args.ponytail_dir:
        arms.append("ponytail-ref")
    for arm in arms:
        plugin = args.ponytail_dir if arm == "ponytail-ref" else None
        if layout == "settings-sources":
            include_block, include_skill = arm_layout(arm)
            arm_meta = {k: v for k, v in meta.items() if k not in ("claude_block_sha256", "project_skill_path")}
            arm_dir = prepare_arm_settings_sources(arms_root, arm, settings, skill, plugin, arm_meta,
                                                   claude_block=claude_block,
                                                   project_skill_path=project_skill if include_skill else None)
            log(f"arm {arm:12} claude-snippet.md = sentinel" + (" + always-on block" if include_block else " only")
                + (f"; workspace gets .claude/skills/{skill} copied from {project_skill}" if include_skill else ""))
        else:
            arm_dir = prepare_arm(arms_root, arm, settings, credentials, rules.stdout, tree, skill,
                                  arm == "skill", plugin, meta)
        problems = arm_preflight(arm_dir, arm, skill)
        status = "OK" if not problems else "FAILED " + "; ".join(problems)
        log(f"arm {arm:12} {arm_dir}  preflight {status}")
    existing = {}
    arms_json = arms_root / "arms.json"
    if arms_json.exists():
        try:
            existing = json.loads(arms_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    # a probe stays valid only for the exact arms it saw: same rules, same layout, same block, same
    # project skill, same arm list
    keep_probe = (all(existing.get(k) == meta.get(k)
                      for k in ("rules_sha", "isolation", "claude_block_sha256", "project_skill_path"))
                  and existing.get("arms") == arms)
    existing.update({"arms": arms, "skill": skill, **meta,
                     "probe": existing.get("probe") if keep_probe else None})
    arms_json.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    log(f"wrote {arms_json}")
    return 0


# ── cells ─────────────────────────────────────────────────────────────────
def cell_env(arm_dir: Path, isolation: str) -> dict:
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)              # a nested-session guard the CLI sets for itself
    if isolation == "settings-sources":
        return env                           # the real setup on purpose; the flags do the isolating
    if isolation == "home":
        env["HOME"] = str(arm_dir / "home")
        env.pop("CLAUDE_CONFIG_DIR", None)
    else:
        env["CLAUDE_CONFIG_DIR"] = str(arm_dir)
    return env


def cell_command(prompt: str, model: str, budget_usd: float, isolation: str,
                 plugin_dir: str | None = None, extra_system: str = NO_RUN) -> list[str]:
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude CLI not found on PATH")
    cmd = [exe, "-p", prompt, "--model", model, "--output-format", "json"]
    if isolation == "settings-sources":
        cmd += ["--setting-sources", "project,local", "--permission-mode", "acceptEdits"]
    else:
        cmd += ["--permission-mode", "bypassPermissions"]
    cmd += ["--disallowedTools", "Bash", "--strict-mcp-config", "--no-session-persistence",
            "--max-budget-usd", f"{budget_usd:.2f}", "--append-system-prompt", extra_system]
    if plugin_dir:
        cmd += ["--plugin-dir", plugin_dir]
    return cmd


def tree_kill(proc: subprocess.Popen) -> None:
    """Kill one timed-out cell's whole process group, never a blanket kill."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_process(cmd: list[str], cwd: Path, env: dict, out_path: Path, err_path: Path,
                timeout_s: int) -> dict:
    started = time.time()
    killed = False
    with open(out_path, "wb") as so, open(err_path, "wb") as se:
        proc = subprocess.Popen(cmd, cwd=str(cwd), env=env, stdout=so, stderr=se,
                                start_new_session=(os.name != "nt"))
        try:
            proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            tree_kill(proc)
            killed = True
            try:
                proc.wait(timeout=15)
            except Exception:  # noqa: BLE001
                pass
            se.write(f"\n[KILLED after {timeout_s}s timeout]".encode())
    return {"returncode": proc.returncode, "killed": killed, "wall_s": round(time.time() - started, 1)}


def score_cell(task: Task, cell_dir: Path, arm: str, model: str, run_index: int) -> dict:
    repo = cell_dir / "repo"
    meta, result_text = read_claude_json(cell_dir / "_claude.json")
    stats = git_diff_stats(repo)
    sc = task.score(repo)
    det = run_detectors(task.id, stats, result_text, repo)
    (cell_dir / "_diff.patch").write_text(stats.pop("patch"), encoding="utf-8")
    (cell_dir / "_result.txt").write_text(result_text, encoding="utf-8")
    stats.pop("added_text", None)
    stats.pop("added_by_file", None)
    cell = {"task": task.id, "arm": arm, "model": model, "run": run_index,
            "source": task.source, "room": task.room, "boundary": task.boundary,
            "structural": task.structural, **sc, **stats, "detectors": det, **meta}
    cell["flags"] = cell_flags(cell)
    return cell


def run_cell(task: Task, arm: str, arm_dir: Path, model: str, isolation: str, cell_dir: Path,
             run_index: int, plugin_dir: str | None) -> dict:
    cell_dir.mkdir(parents=True, exist_ok=True)
    repo = cell_dir / "repo"
    ss = isolation == "settings-sources"
    seed_repo(task, repo, workspace_files(arm_dir) if ss else None, workspace_dirs(arm_dir) if ss else None)
    cmd = cell_command(task.prompt, model, CELL_BUDGET_USD, isolation, plugin_dir)
    (cell_dir / "_command.txt").write_text(" ".join(json.dumps(c) for c in cmd) + "\n", encoding="utf-8")
    proc = run_process(cmd, repo, cell_env(arm_dir, isolation), cell_dir / "_claude.json",
                       cell_dir / "_claude.stderr.txt", CELL_TIMEOUT_S)
    cell = score_cell(task, cell_dir, arm, model, run_index)
    cell.update({"returncode": proc["returncode"], "killed": proc["killed"], "wall_s": proc["wall_s"]})
    return cell


def load_arms_json(arms_root: Path) -> dict:
    p = arms_root / "arms.json"
    if not p.exists():
        sys.exit(f"{p} missing: run --prepare-arms first")
    return json.loads(p.read_text(encoding="utf-8"))


def probe_gate(arms_meta: dict, arms: list[str] | None = None) -> str | None:
    """Why --matrix must refuse these arms, or None: the probe has to have passed, under the arms'
    current rules_sha, in a mode the arm layout supports, covering every requested arm — and for
    the skill arm it has to have SEEN the skill (skill_visible 1/1). A skill arm whose probe never
    listed <skill> measures the always-on block alone: stamp 20260905-230209 did exactly that
    before the criterion existed and was relabelled `block`."""
    probe = arms_meta.get("probe") or {}
    if not probe.get("passed"):
        return ("the isolation probe has not passed for these arms (run --probe-isolation; arms.json "
                "probe.passed must be true)")
    if probe.get("rules_sha") != arms_meta.get("rules_sha"):
        return (f"the probe passed under rules_sha {probe.get('rules_sha')} but the arms are at "
                f"{arms_meta.get('rules_sha')}; re-run --probe-isolation")
    layout = arms_meta.get("isolation", "config-dir")
    if (probe.get("isolation") == "settings-sources") != (layout == "settings-sources"):
        return (f"the probe passed in {probe.get('isolation')} but the arms carry the {layout} layout; "
                "re-run --prepare-arms and the probe")
    probed_arms = probe.get("arms")
    for arm in arms or []:
        if probed_arms is not None and arm not in probed_arms:
            return f"arm {arm} was not covered by the last probe (probed: {probed_arms}); re-run --probe-isolation"
    if arms and "skill" in arms and layout == "settings-sources":
        seen = (probe.get("skill_visible") or {}).get("skill")
        if seen != "1/1":
            return (f"the last probe did not see {arms_meta.get('skill', DEFAULT_SKILL)} in the skill arm "
                    f"(skill_visible {seen!r}, need '1/1'): the arm would measure the always-on block only "
                    "— re-run --probe-isolation (a probe from before the project-skill layout has no record)")
    return None


def cmd_matrix(args: argparse.Namespace) -> int:
    if not SELFTEST_PASSED:
        sys.exit("refusing --matrix: --selftest did not pass in this invocation "
                 "(run `run.py --selftest --matrix ...` so the instruments are proven first)")
    arms_root, runs_root = Path(args.arms_root).expanduser(), Path(args.runs_root).expanduser()
    for p in (arms_root, runs_root):
        if not outside_repo(p):
            sys.exit(f"refusing: {p} resolves inside the repository")
    arms_meta = load_arms_json(arms_root)
    arms = [a.strip() for a in args.arms.split(",")]
    refusal = probe_gate(arms_meta, arms)
    if refusal:
        sys.exit("refusing --matrix: " + refusal)
    isolation = arms_meta["probe"]["isolation"]
    if args.scorer_venv:
        os.environ["LEAN_SCORER_VENV"] = str(Path(args.scorer_venv).expanduser())
    tasks = load_tasks()
    task_ids = list(TASK_IDS) if args.tasks == "all" else [t.strip() for t in args.tasks.split(",")]
    unknown = [t for t in task_ids if t not in tasks]
    if unknown:
        sys.exit(f"unknown task(s): {unknown}; known: {list(TASK_IDS)}")
    for arm in arms:
        problems = arm_preflight(arms_root / arm, arm, arms_meta.get("skill", DEFAULT_SKILL))
        if problems:
            sys.exit(f"arm {arm} failed preflight: " + "; ".join(problems))
    version = claude_version()
    if arms_meta.get("claude_version") and arms_meta["claude_version"] != version:
        sys.exit(f"claude --version is {version!r} but the arms were prepared under "
                 f"{arms_meta['claude_version']!r}; re-run --prepare-arms and the probe")
    stamp = now_stamp()
    out_dir = runs_root / stamp
    out_dir.mkdir(parents=True)
    header = {"stamp": stamp, "claude_version": version, "model": args.model, "arms": arms,
              "tasks": task_ids, "runs": args.runs, "isolation": isolation,
              "rules_sha": arms_meta.get("rules_sha"), "budget_usd": args.budget_usd,
              "cell_budget_usd": CELL_BUDGET_USD, "cell_timeout_s": CELL_TIMEOUT_S,
              "started_at": _dt.datetime.now().isoformat(timespec="seconds")}
    cells = [(tid, arm, r) for tid in task_ids for arm in arms for r in range(args.runs)]
    results: list[dict] = []
    spent = 0.0
    stopped = None
    log(f"matrix {stamp}: {len(cells)} cells, {args.workers} at a time, run budget ${args.budget_usd:.2f}")

    def one(spec):
        tid, arm, r = spec
        plugin = None
        arm_json = arms_root / arm / "arm.json"
        if arm_json.exists():
            plugin = json.loads(arm_json.read_text(encoding="utf-8")).get("plugin_dir")
        cell_dir = out_dir / f"{tid}__{arm}__{r}"
        log(f"  start {tid} / {arm} #{r}")
        return run_cell(tasks[tid], arm, arms_root / arm, args.model, isolation, cell_dir, r, plugin)

    def flush():
        (out_dir / "results.json").write_text(json.dumps(
            {**header, "spent_usd": round(spent, 4), "stopped": stopped, "results": results},
            indent=2, default=str), encoding="utf-8")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        pending = list(cells)
        futures: dict = {}
        while pending or futures:
            while pending and len(futures) < args.workers and stopped is None:
                spec = pending.pop(0)
                futures[ex.submit(one, spec)] = spec
            if not futures:
                break
            done, _ = concurrent.futures.wait(list(futures), return_when=concurrent.futures.FIRST_COMPLETED)
            for fut in done:
                spec = futures.pop(fut)
                try:
                    cell = fut.result()
                except Exception as exc:  # noqa: BLE001
                    cell = {"task": spec[0], "arm": spec[1], "run": spec[2], "error": str(exc)[:200]}
                results.append(cell)
                spent += float(cell.get("total_cost_usd") or 0.0)
                log(f"  [{len(results)}/{len(cells)}] {cell['task']} / {cell['arm']} #{cell['run']}  "
                    f"added={cell.get('added_lines')} correct={cell.get('correct')} safe={cell.get('safe')} "
                    f"cost=${cell.get('total_cost_usd')} spent=${spent:.2f}")
                flush()
                if spent > args.budget_usd and stopped is None:
                    stopped = f"run budget ${args.budget_usd:.2f} exceeded at ${spent:.2f}; {len(pending)} cells not run"
                    log("STOP " + stopped)
                    pending.clear()
    flush()
    rows = aggregate(results)
    (out_dir / "summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print_table(rows)
    log(f"wrote {out_dir}/results.json + summary.json ({len(results)} cells, ${spent:.2f})")
    return 0 if stopped is None else 2


# ── aggregate / report / classify / rescore ───────────────────────────────
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.mean(xs), 3) if xs else None


def aggregate(results: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for r in results:
        if "error" in r:
            continue
        groups.setdefault((r["task"], r["arm"]), []).append(r)
    rows = []
    for (task, arm), cells in sorted(groups.items()):
        n = len(cells)
        added = [c.get("added_lines", 0) for c in cells]
        rows.append({
            "task": task, "arm": arm, "n": n,
            "correct_rate": round(sum(c.get("correct", 0) for c in cells) / n, 3),
            "safe_rate": round(sum(c.get("safe", 0) for c in cells) / n, 3),
            "structural": any(c.get("structural") for c in cells),
            "added_lines_mean": _mean(added), "added_lines_min": min(added), "added_lines_max": max(added),
            "added_lines_median": statistics.median(added),
            "code_loc_mean": _mean([c.get("code_loc", 0) for c in cells]),
            "test_added_lines_mean": _mean([c.get("test_added_lines", 0) for c in cells]),
            "wrote_tests_rate": round(sum(1 for c in cells if c.get("test_files", 0) > 0) / n, 3),
            "cost_mean_usd": _mean([c.get("total_cost_usd") for c in cells]),
            "turns_mean": _mean([c.get("num_turns") for c in cells]),
            "output_tokens_mean": _mean([c.get("output_tokens") for c in cells]),
            "duration_s_mean": _mean([(c["duration_ms"] or 0) / 1000 for c in cells if c.get("duration_ms") is not None]),
            "flags": {f: sum(1 for c in cells if (c.get("flags") or {}).get(f)) for f in FLAGS + POSITIVE_SIGNALS},
        })
    return rows


def print_table(rows: list[dict]) -> None:
    by_task: dict[str, list[dict]] = {}
    for r in rows:
        by_task.setdefault(r["task"], []).append(r)
    for task, rs in sorted(by_task.items()):
        label = " (STRUCTURAL scorer)" if any(r["structural"] for r in rs) else ""
        print(f"\n=== {task}{label} ===")
        print(f"  {'arm':14} {'n':>3} {'correct':>8} {'safe':>6} {'added mean':>11} {'min':>5} {'max':>5} {'$/cell':>8} {'turns':>6}")
        for r in sorted(rs, key=lambda x: x["arm"]):
            cost = f"${r['cost_mean_usd']:.4f}" if r["cost_mean_usd"] is not None else "-"
            print(f"  {r['arm']:14} {r['n']:>3} {r['correct_rate']:>8} {r['safe_rate']:>6} "
                  f"{r['added_lines_mean']:>11} {r['added_lines_min']:>5} {r['added_lines_max']:>5} "
                  f"{cost:>8} {r['turns_mean'] if r['turns_mean'] is not None else '-':>6}")


def load_results(stamp_dir: Path) -> dict:
    p = stamp_dir / "results.json"
    if not p.exists():
        sys.exit(f"{p} missing")
    return json.loads(p.read_text(encoding="utf-8"))


def check_same_conditions(headers: list[dict]) -> str | None:
    versions = {h.get("claude_version") for h in headers}
    models = {h.get("model") for h in headers}
    if len(versions) > 1:
        return f"claude versions differ: {sorted(map(str, versions))}"
    if len(models) > 1:
        return f"model ids differ: {sorted(map(str, models))}"
    return None


UUID_RX = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
# The session key is spelled in two halves on purpose: issue #145 accepts this directory only when
# `git ls-files research/lean-code | xargs grep -l <that key>` is empty, and scripts/scan-secrets.py
# sets the precedent of building a sensitive literal at run time instead of writing it in a scanned file.
SESSION_KEY = "session" + "_id"
STRIP_KEYS = {SESSION_KEY, "result", "uuid", "session_uuid", "message_id", "request_id"}


def strip_export(obj, home: str | None = None):
    home = home or str(Path.home())
    if isinstance(obj, dict):
        return {k: strip_export(v, home) for k, v in obj.items()
                if k not in STRIP_KEYS and not k.endswith("uuid")}
    if isinstance(obj, list):
        return [strip_export(v, home) for v in obj]
    if isinstance(obj, str):
        s = obj.replace(home, "~") if home else obj
        return UUID_RX.sub("<uuid>", s)
    return obj


def arm_deltas(rows: list[dict]) -> list[dict]:
    """Per task, each treatment arm against the baseline row of the same aggregate: Δ% of the mean
    added_lines (the protocol's Δ), with correct and safe rates side by side as (baseline, arm).
    Empty when the aggregate has no baseline row."""
    by_key = {(r["task"], r["arm"]): r for r in rows}
    out = []
    for r in rows:
        if r["arm"] == "baseline":
            continue
        b = by_key.get((r["task"], "baseline"))
        if b is None:
            continue
        bm, am = b["added_lines_mean"], r["added_lines_mean"]
        delta = round((am - bm) / bm * 100, 1) if bm else None
        out.append({"task": r["task"], "arm": r["arm"], "n_baseline": b["n"], "n": r["n"],
                    "baseline_added_mean": bm, "added_mean": am, "delta_pct": delta,
                    "correct_rate": [b["correct_rate"], r["correct_rate"]],
                    "safe_rate": [b["safe_rate"], r["safe_rate"]],
                    "structural": bool(r["structural"]), "overbuild": r["task"] in OVERBUILD_TASKS})
    return out


def delta_groups(deltas: list[dict]) -> dict[str, dict]:
    """Per treatment arm, the inputs of the protocol's verdict table — never the verdict: mean Δ over
    the over-build group, the worst (highest) Δ over every task, the tasks with correct below the
    baseline, the trust-boundary tasks with safe below 1 (the structural task never counts there)."""
    groups: dict[str, dict] = {}
    for arm in sorted({d["arm"] for d in deltas}):
        ds = [d for d in deltas if d["arm"] == arm]
        ob = [d["delta_pct"] for d in ds if d["overbuild"] and d["delta_pct"] is not None]
        with_delta = [d for d in ds if d["delta_pct"] is not None]
        worst = max(with_delta, key=lambda d: d["delta_pct"]) if with_delta else None
        groups[arm] = {
            "overbuild_mean_delta_pct": round(statistics.mean(ob), 1) if ob else None,
            "overbuild_tasks": len(ob),
            "worst_task": worst["task"] if worst else None,
            "worst_delta_pct": worst["delta_pct"] if worst else None,
            "correct_below_baseline": [d["task"] for d in ds if d["correct_rate"][1] < d["correct_rate"][0]],
            "boundary_safe_below_1": [d["task"] for d in ds
                                      if d["task"] in BOUNDARY_TASKS and not d["structural"] and d["safe_rate"][1] < 1.0],
        }
    return groups


def print_deltas(deltas: list[dict], groups: dict[str, dict]) -> None:
    if not deltas:
        print("\n(no baseline arm in these stamps: no delta to print)")
        return
    print("\n=== delta vs baseline (mean added_lines; the protocol's Δ) ===")
    print(f"  {'task':22} {'arm':10} {'base':>7} {'arm':>7} {'delta%':>8}  correct b->a  safe b->a")
    for d in deltas:
        label = f"{d['task']} (S)" if d["structural"] else d["task"]
        delta = f"{d['delta_pct']:+.1f}" if d["delta_pct"] is not None else "-"
        print(f"  {label:22} {d['arm']:10} {d['baseline_added_mean']:>7} {d['added_mean']:>7} {delta:>8}  "
              f"{d['correct_rate'][0]}->{d['correct_rate'][1]:<7} {d['safe_rate'][0]}->{d['safe_rate'][1]}")
    for arm, g in groups.items():
        mean = f"{g['overbuild_mean_delta_pct']:+.1f}%" if g["overbuild_mean_delta_pct"] is not None else "-"
        worst = f"{g['worst_task']} {g['worst_delta_pct']:+.1f}%" if g["worst_task"] else "-"
        print(f"  {arm}: over-build group mean delta {mean} over {g['overbuild_tasks']} tasks; worst task {worst}; "
              f"correct below baseline: {', '.join(g['correct_below_baseline']) or 'none'}; "
              f"boundary safe < 1: {', '.join(g['boundary_safe_below_1']) or 'none'}")


def cmd_report(args: argparse.Namespace) -> int:
    stamps = [Path(s).expanduser() for s in args.report]
    payloads = [load_results(s) for s in stamps]
    problem = check_same_conditions(payloads)
    if problem:
        sys.exit(f"refusing to aggregate: {problem}")
    results = [r for p in payloads for r in p["results"]]
    rows = aggregate(results)
    print_table(rows)
    deltas = arm_deltas(rows)
    groups = delta_groups(deltas)
    print_deltas(deltas, groups)
    if args.export:
        out = strip_export({
            "stamps": [p["stamp"] for p in payloads], "claude_version": payloads[0]["claude_version"],
            "model": payloads[0]["model"], "arms": sorted({a for p in payloads for a in p["arms"]}),
            "isolation": sorted({str(p.get("isolation")) for p in payloads}),
            "rules_sha": sorted({str(p.get("rules_sha")) for p in payloads}),
            "relabels": [{"stamp": p["stamp"], **r} for p in payloads for r in (p.get("relabels") or [])],
            "cells": len(results), "spent_usd": round(sum(float(p.get("spent_usd") or 0) for p in payloads), 4),
            "summary": rows, "deltas": deltas, "delta_groups": groups,
            "cells_detail": [{k: v for k, v in r.items() if k not in ("changed_paths",)} for r in results],
        })
        Path(args.export).write_text(json.dumps(out, indent=2, default=str) + "\n", encoding="utf-8")
        log(f"wrote {args.export}")
    return 0


def render_defects_md(payload: dict, rows: list[dict]) -> str:
    results = [r for r in payload["results"] if "error" not in r]
    arms = sorted({r["arm"] for r in results})
    lines = [f"# Baseline defects — {payload['stamp']}", "",
             f"- model: `{payload['model']}`", f"- claude: `{payload['claude_version']}`",
             f"- arms: {', '.join(arms)}; isolation: `{payload.get('isolation')}`; rules sha: `{payload.get('rules_sha')}`",
             f"- cells: {len(results)} (n={payload.get('runs')} per task × arm); spent: ${payload.get('spent_usd')}",
             f"- stopped: {payload.get('stopped') or 'no'}", "",
             "Counts are cells carrying the flag, out of the cells of that arm. A flag is a regex or a",
             "scorer axis, not a judgement — see run.py docstring KNOWN LIMIT 2 and 5.", "",
             "## Flags per arm", "",
             "| flag | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for f in FLAGS + POSITIVE_SIGNALS:
        cells = []
        for arm in arms:
            arm_cells = [r for r in results if r["arm"] == arm]
            cells.append(f"{sum(1 for r in arm_cells if (r.get('flags') or {}).get(f))}/{len(arm_cells)}")
        lines.append(f"| `{f}` | " + " | ".join(cells) + " |")
    lines += ["", "## added_lines per task (mean / min / max) and gates", "",
              "| task | arm | n | correct | safe | added mean | min | max | tests written |",
              "|---|---|--:|--:|--:|--:|--:|--:|--:|"]
    for r in rows:
        label = f"{r['task']} (STRUCTURAL)" if r["structural"] else r["task"]
        lines.append(f"| {label} | {r['arm']} | {r['n']} | {r['correct_rate']} | {r['safe_rate']} | "
                     f"{r['added_lines_mean']} | {r['added_lines_min']} | {r['added_lines_max']} | {r['wrote_tests_rate']} |")
    lines += ["", "## Per-cell flags", "", "| task | arm | run | correct | safe | added | flags | reason |", "|---|---|--:|--:|--:|--:|---|---|"]
    for r in sorted(results, key=lambda x: (x["task"], x["arm"], x["run"])):
        on = [f for f in FLAGS + POSITIVE_SIGNALS if (r.get("flags") or {}).get(f)]
        lines.append(f"| {r['task']} | {r['arm']} | {r['run']} | {r.get('correct')} | {r.get('safe')} | "
                     f"{r.get('added_lines')} | {', '.join(on) or '-'} | {str(r.get('reason', ''))[:80]} |")
    lines += ["", "## What this does not cover", "",
              "- react-use-orders is scored structurally; its `safe` column is the reuse axis.",
              "- No cell ran with the maintainer's caveman plugin or hooks (stripped on purpose).",
              "- One model id, one CLI version, one machine; n as stated above."]
    return "\n".join(lines) + "\n"


def cmd_classify(args: argparse.Namespace) -> int:
    stamp_dir = Path(args.classify).expanduser()
    payload = load_results(stamp_dir)
    for r in payload["results"]:
        if "error" not in r:
            r["flags"] = cell_flags(r)
    rows = aggregate(payload["results"])
    md = render_defects_md(payload, rows)
    out = stamp_dir / f"{payload['stamp']}-baseline-defects.md"
    out.write_text(md, encoding="utf-8")
    (stamp_dir / "classify.json").write_text(json.dumps(strip_export(
        {"stamp": payload["stamp"], "model": payload["model"], "claude_version": payload["claude_version"],
         "rows": rows}), indent=2) + "\n", encoding="utf-8")
    print(md)
    log(f"wrote {out}")
    return 0


PROCESS_FIELDS = ("returncode", "killed", "wall_s")


def carry_process_fields(previous: list[dict], rescored: list[dict]) -> int:
    """score_cell knows nothing about the process that produced a cell: run_cell adds returncode,
    killed and wall_s after scoring, and nothing under the cell directory records them. A rescore
    that only calls score_cell therefore deletes them from results.json — which is what happened to
    the two stamps of 2026-09-05 (rescored before this existed; their fields are gone for good, see
    tasks.md S.3). Copy the fields from the previous results, matched by (task, arm, run), and never
    invent one that was not there. Returns how many rescored cells received at least one field."""
    by_key = {(c.get("task"), c.get("arm"), c.get("run")): c for c in previous}
    carried = 0
    for cell in rescored:
        prev = by_key.get((cell["task"], cell["arm"], cell["run"])) or {}
        found = {k: prev[k] for k in PROCESS_FIELDS if k in prev}
        if found:
            cell.update(found)
            carried += 1
    return carried


def cmd_rescore(args: argparse.Namespace) -> int:
    stamp_dir = Path(args.rescore).expanduser()
    payload = load_results(stamp_dir)
    if args.scorer_venv:
        os.environ["LEAN_SCORER_VENV"] = str(Path(args.scorer_venv).expanduser())
    tasks = load_tasks()
    rescored = []
    for cell_dir in sorted(p for p in stamp_dir.iterdir() if p.is_dir() and "__" in p.name):
        tid, arm, r = cell_dir.name.split("__")
        if tid not in tasks:
            continue
        cell = score_cell(tasks[tid], cell_dir, arm, payload["model"], int(r))
        rescored.append(cell)
    carried = carry_process_fields(payload.get("results") or [], rescored)
    payload["results"] = rescored
    payload["rescored_at"] = _dt.datetime.now().isoformat(timespec="seconds")
    (stamp_dir / "results.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    rows = aggregate(rescored)
    (stamp_dir / "summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print_table(rows)
    log(f"rescored {len(rescored)} cells in {stamp_dir} (process fields carried on {carried}/{len(rescored)})")
    return 0


def stamp_unfinished(payload: dict, stamp_dir: Path) -> list[str]:
    """Why a stamp is NOT finished, or []: `stopped` null, every cell the header promises present
    in results.json and none errored, every cell directory carrying its _claude.json."""
    problems: list[str] = []
    if payload.get("stopped"):
        problems.append(f"stopped: {payload['stopped']}")
    expected = [(t, a, r) for t in payload.get("tasks") or [] for a in payload.get("arms") or []
                for r in range(int(payload.get("runs") or 0))]
    have = {(c.get("task"), c.get("arm"), c.get("run")) for c in payload.get("results") or []}
    missing = [k for k in expected if k not in have]
    if missing:
        problems.append(f"{len(missing)} of {len(expected)} cells missing from results.json (first: {missing[0]})")
    errored = sum(1 for c in payload.get("results") or [] if "error" in c)
    if errored:
        problems.append(f"{errored} cells carry an error")
    no_json = [f"{t}__{a}__{r}" for t, a, r in expected if not (stamp_dir / f"{t}__{a}__{r}" / "_claude.json").exists()]
    if no_json:
        problems.append(f"{len(no_json)} cell dirs without _claude.json (first: {no_json[0]})")
    return problems


def relabel_arm(stamp_dir: Path, src: str, dst: str, reason: str) -> dict:
    """Rename arm `src` to `dst` in a FINISHED stamp: cell directories <task>__<src>__<r> ->
    <task>__<dst>__<r>, `arm` in results.json (cells and header), summary.json and classify.json
    when present, and a `relabels` entry carrying the reason and the time. Refuses an unfinished
    stamp, an unknown destination, a destination already in the stamp, a source that is not, and an
    empty reason. Directories are checked before any rename and renamed before any file is
    rewritten, so a refusal leaves the stamp untouched."""
    payload = load_results(stamp_dir)
    known = (*SETTINGS_SOURCES_ARMS, "ponytail-ref")
    if dst not in known:
        sys.exit(f"refusing --relabel-arm: unknown destination arm {dst!r}; known: {list(known)}")
    if src not in (payload.get("arms") or []):
        sys.exit(f"refusing --relabel-arm: arm {src!r} is not in {stamp_dir}/results.json (arms: {payload.get('arms')})")
    if dst in payload["arms"]:
        sys.exit(f"refusing --relabel-arm: arm {dst!r} is already in the stamp; two arms cannot merge")
    if not reason or len(reason.strip()) < 8:
        sys.exit("refusing --relabel-arm: --reason must say why (recorded in results.json)")
    problems = stamp_unfinished(payload, stamp_dir)
    if problems:
        sys.exit("refusing --relabel-arm: the matrix has not finished: " + "; ".join(problems))
    renames: list[tuple[Path, Path]] = []
    for d in sorted(p for p in stamp_dir.iterdir() if p.is_dir() and p.name.split("__")[1:2] == [src]):
        target = d.with_name(d.name.replace(f"__{src}__", f"__{dst}__", 1))
        if target.exists():
            sys.exit(f"refusing --relabel-arm: {target} already exists")
        renames.append((d, target))
    for d, target in renames:
        d.rename(target)
    cells = 0
    for c in payload["results"]:
        if c.get("arm") == src:
            c["arm"] = dst
            cells += 1
    payload["arms"] = [dst if a == src else a for a in payload["arms"]]
    entry = {"from": src, "to": dst, "reason": reason.strip(), "at": _dt.datetime.now().isoformat(timespec="seconds"),
             "cells": cells, "dirs_renamed": len(renames)}
    payload.setdefault("relabels", []).append(entry)
    (stamp_dir / "results.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    for name in ("summary.json", "classify.json"):
        p = stamp_dir / name
        if not p.exists():
            continue
        j = json.loads(p.read_text(encoding="utf-8"))
        for row in (j if isinstance(j, list) else j.get("rows") or []):
            if row.get("arm") == src:
                row["arm"] = dst
        p.write_text(json.dumps(j, indent=2, default=str) + ("\n" if name == "classify.json" else ""), encoding="utf-8")
    return entry


def cmd_relabel(args: argparse.Namespace) -> int:
    stamp_dir, src, dst = Path(args.relabel_arm[0]).expanduser(), args.relabel_arm[1], args.relabel_arm[2]
    entry = relabel_arm(stamp_dir, src, dst, args.reason or "")
    log(f"relabelled {entry['cells']} cells and {entry['dirs_renamed']} cell dirs {src} -> {dst} in {stamp_dir}; "
        f"reason recorded in results.json relabels")
    return 0


# ── isolation probe (paid, small) ─────────────────────────────────────────
def probe_command(model: str, budget_usd: float, isolation: str = "config-dir",
                  prompt: str | None = None) -> list[str]:
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude CLI not found on PATH")
    if isolation == "settings-sources":
        return [exe, "-p", prompt or PROBE_PROMPT_SENTINEL_ONLY, "--model", model, "--output-format", "stream-json",
                "--verbose", "--include-hook-events", "--tools", "", "--setting-sources", "project,local",
                "--strict-mcp-config", "--no-session-persistence", "--max-budget-usd", f"{budget_usd:.2f}"]
    return [exe, "-p", PROBE_PROMPT, "--model", model, "--output-format", "stream-json", "--verbose",
            "--include-hook-events", "--tools", "", "--permission-mode", "bypassPermissions",
            "--strict-mcp-config", "--no-session-persistence", "--max-budget-usd", f"{budget_usd:.2f}"]


def parse_stream(path: Path) -> dict:
    """Events of a stream-json run. Hook lifecycle events (system/hook_started, hook_response, …,
    emitted with --include-hook-events) are listed by name, and the ones naming one of the
    maintainer's hooks (MAINTAINER_HOOK_NAMES) are counted separately."""
    events: list[str] = []
    hook_names: list[str] = []
    maintainer_hook_events = 0
    result_text = ""
    result_keys: list[str] = []
    cost = None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(ev, dict):
            continue
        kind = str(ev.get("type", "?"))
        sub = ev.get("subtype")
        label = f"{kind}/{sub}" if sub else kind
        events.append(label)
        if "hook" in label.lower():
            hook_names.append(str(ev.get("hook_name") or ev.get("hook_event_name") or ev.get("hook_event") or "?"))
            if any(name in line for name in MAINTAINER_HOOK_NAMES):
                maintainer_hook_events += 1
        if kind == "result":
            result_text = str(ev.get("result") or "")
            result_keys = sorted(k for k in ev.keys() if k not in STRIP_KEYS)
            cost = ev.get("total_cost_usd")
    return {"events": events, "hook_names": hook_names, "maintainer_hook_events": maintainer_hook_events,
            "result_text": result_text, "result_keys": result_keys, "cost": cost}


SKILLS_LINE = re.compile(r"^\s*SKILLS:\s*(?P<names>.*)$", re.I | re.M)


def skills_visible_in(result_text: str, skill: str) -> bool:
    """Whether the probe's answer lists `skill` as available. The `SKILLS:` line is judged alone
    when present, so a mention elsewhere in the answer does not count; without one the whole
    answer minus the closing DONE is read — the shape the first manual probe returned
    (`lean-code\\nDONE`). Whole-word: `lean-code-extra` is not `lean-code`."""
    text = result_text or ""
    m = SKILLS_LINE.search(text)
    haystack = m.group("names") if m else "\n".join(ln for ln in text.splitlines() if ln.strip().upper() != "DONE")
    return re.search(r"(?<![\w-])" + re.escape(skill) + r"(?![\w-])", haystack, re.I) is not None


def marker_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None


def probe_workspace(arm_dir: Path, cwd: Path) -> Path:
    """A throwaway cwd for one settings-sources probe call: the CLAUDE.md snippet, the arm's
    project settings and, in the skill arm, .claude/skills/<skill> — exactly what a cell's
    workspace carries, nothing else."""
    cwd.mkdir(parents=True, exist_ok=True)
    for name, content in workspace_files(arm_dir).items():
        p = cwd / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    for rel, src in workspace_dirs(arm_dir).items():
        _copy_tree(src, cwd / rel)
    # The probe cwd is a git repository for the same reason every cell workspace is one: Claude Code
    # discovers project skills (.claude/skills/<skill>) only under a git root. Measured 2026-09-06
    # on 2.1.261 with the same skill-arm cwd: without `git init` the skills-list probe answered
    # "SKILLS: none"; with it, "SKILLS: bench-sentinel, lean-code".
    if not (cwd / ".git").exists():
        git(cwd, "init", "-q")
        git(cwd, "add", "-f", "-A")
        git(cwd, "-c", "user.email=bench@example.invalid", "-c", "user.name=bench",
            "commit", "-q", "-m", "probe", "--no-verify")
    return cwd


def snapshot(dir_: Path) -> set[str]:
    return {str(p.relative_to(dir_)) for p in dir_.rglob("*") if "_tree" not in p.parts and "skills" not in p.parts}


def probe_skill_visibility(arm: str, arm_dir: Path, model: str, out_dir: Path, skill_name: str) -> dict:
    """The fourth criterion of the settings-sources probe, one call per arm: with --tools "" the
    model is asked for its available-skills list. The skill arm's workspace carries
    .claude/skills/<skill> and must list it; baseline and block must not (measured 2026-09-05 on
    2.1.261: the user skills dir is not loaded under --setting-sources project,local, so nothing
    else could put the skill there)."""
    cmd = probe_command(model, PROBE_BUDGET_USD, "settings-sources", prompt=PROBE_PROMPT_SKILLS)
    out = out_dir / f"{arm}-settings-sources-skills.jsonl"
    err = out_dir / f"{arm}-settings-sources-skills.stderr.txt"
    log("  " + " ".join(json.dumps(c) for c in cmd[:6]) + " ...  (skills list)")
    cwd = probe_workspace(arm_dir, out_dir / f"{arm}-cwd-skills")
    proc = run_process(cmd, cwd, cell_env(arm_dir, "settings-sources"), out, err, 120)
    parsed = parse_stream(out)
    text = parsed["result_text"]
    seen = skills_visible_in(text, skill_name)
    expected = arm_layout(arm)[1]
    skills_line = next((ln for ln in text.splitlines() if ln.strip().upper().startswith("SKILLS:")), text.strip()[:200])
    return {"returncode": proc["returncode"], "wall_s": proc["wall_s"], "skills_line": skills_line,
            "skill_visible": seen, "expected": expected, "ok": seen == expected,
            "hook_events": [e for e in parsed["events"] if "hook" in e.lower()],
            "cost_usd": parsed["cost"], "stderr_tail": err.read_text(encoding="utf-8", errors="ignore")[-300:]}


def probe_arm(arm: str, arm_dir: Path, model: str, isolation: str, out_dir: Path,
              user_claude_dir: Path | None = None, skill_name: str = DEFAULT_SKILL) -> dict:
    marker = (user_claude_dir or Path.home() / ".claude") / CAVEMAN_MARKER
    calls = []
    for i in range(PROBE_CALLS):
        cmd = probe_command(model, PROBE_BUDGET_USD, isolation)
        out = out_dir / f"{arm}-{isolation}-{i}.jsonl"
        err = out_dir / f"{arm}-{isolation}-{i}.stderr.txt"
        log("  " + " ".join(json.dumps(c) for c in cmd[:6]) + " ...")
        marker_before = marker_mtime(marker)
        if isolation == "settings-sources":
            cwd = probe_workspace(arm_dir, out_dir / f"{arm}-cwd-{i}")
            before = after = set()
            proc = run_process(cmd, cwd, cell_env(arm_dir, isolation), out, err, 120)
        else:
            before = snapshot(arm_dir)
            proc = run_process(cmd, out_dir, cell_env(arm_dir, isolation), out, err, 120)
            after = snapshot(arm_dir)
        marker_after = marker_mtime(marker)
        parsed = parse_stream(out)
        text = parsed["result_text"]
        skills_line = next((ln for ln in text.splitlines() if ln.strip().upper().startswith("SKILLS:")), "")
        hooks_line = next((ln for ln in text.splitlines() if ln.strip().upper().startswith("HOOKS:")), "")
        calls.append({
            "call": i, "returncode": proc["returncode"], "wall_s": proc["wall_s"],
            "sentinel_ok": f"{SENTINEL}: {arm}" in text,
            "done_ok": "DONE" in text.upper(),
            "caveman_active_absent": not (arm_dir / CAVEMAN_MARKER).exists(),
            "caveman_marker_untouched": marker_before == marker_after,
            "hook_events": [e for e in parsed["events"] if "hook" in e.lower()],
            "hook_names": parsed["hook_names"],
            "maintainer_hook_events": parsed["maintainer_hook_events"],
            "hooks_reported": "yes" in hooks_line.lower(),
            "skill_listed": skill_name in skills_line.lower(),
            "event_vocabulary": sorted(set(parsed["events"])),
            "result_keys": parsed["result_keys"],
            "config_dir_wrote": sorted(after - before)[:20],
            "cost_usd": parsed["cost"],
            "stderr_tail": err.read_text(encoding="utf-8", errors="ignore")[-300:],
        })
    n = len(calls)
    summary = {
        "arm": arm, "isolation": isolation, "calls": calls,
        "sentinel": f"{sum(c['sentinel_ok'] for c in calls)}/{n}",
        "caveman_active_absent": f"{sum(c['caveman_active_absent'] for c in calls)}/{n}",
        "caveman_marker_untouched": f"{sum(c['caveman_marker_untouched'] for c in calls)}/{n}",
        "hook_events_total": sum(len(c["hook_events"]) for c in calls),
        "maintainer_hook_events": sum(c["maintainer_hook_events"] for c in calls),
        "hooks_reported": f"{sum(c['hooks_reported'] for c in calls)}/{n}",
        "skill_listed": f"{sum(c['skill_listed'] for c in calls)}/{n}",
        "cost_usd": round(sum(float(c["cost_usd"] or 0) for c in calls), 4),
    }
    if isolation == "settings-sources":
        # sentinel echoed, no hook event at all (so none of the maintainer's), the real
        # ~/.claude/.caveman-active never rewritten (the plugin's SessionStart hook did not run),
        # and the skill visible exactly in the skill arm
        sv = probe_skill_visibility(arm, arm_dir, model, out_dir, skill_name)
        summary["skill_visible_call"] = sv
        summary["skill_visible"] = f"{int(sv['skill_visible'])}/1"
        summary["skill_visible_expected"] = f"{int(sv['expected'])}/1"
        summary["hook_events_total"] += len(sv["hook_events"])
        summary["cost_usd"] = round(summary["cost_usd"] + float(sv["cost_usd"] or 0), 4)
        summary["passed"] = (sum(c["sentinel_ok"] for c in calls) == n
                             and summary["hook_events_total"] == 0
                             and summary["maintainer_hook_events"] == 0
                             and sum(c["caveman_marker_untouched"] for c in calls) == n
                             and sv["ok"])
    else:
        summary["passed"] = (sum(c["sentinel_ok"] for c in calls) == n
                             and sum(c["caveman_active_absent"] for c in calls) == n
                             and summary["hook_events_total"] == 0
                             and sum(c["hooks_reported"] for c in calls) == 0
                             and (sum(c["skill_listed"] for c in calls) == (n if arm == "skill" else 0)))
    return summary


def cmd_probe(args: argparse.Namespace) -> int:
    arms_root = Path(args.arms_root).expanduser()
    if not outside_repo(arms_root):
        sys.exit(f"refusing: --arms-root {arms_root} resolves inside the repository")
    meta = load_arms_json(arms_root)
    arms = meta["arms"]
    for arm in arms:
        problems = arm_preflight(arms_root / arm, arm, meta.get("skill", DEFAULT_SKILL))
        if problems:
            sys.exit(f"arm {arm} failed preflight: " + "; ".join(problems))
    layout = meta.get("isolation", "config-dir")
    if layout == "settings-sources":
        if args.isolation not in ("settings-sources", "auto"):
            sys.exit(f"these arms carry the settings-sources layout; --isolation {args.isolation} needs "
                     f"arms prepared with `--prepare-arms --isolation {args.isolation}`")
        modes = ["settings-sources"]
    else:
        if args.isolation == "settings-sources":
            sys.exit("these arms carry the config-dir/home layout; re-run --prepare-arms (default "
                     "settings-sources) or pass --isolation auto|config-dir|home")
        modes = ["config-dir", "home"] if args.isolation == "auto" else [args.isolation]
    out_dir = arms_root / "_probe" / now_stamp()
    out_dir.mkdir(parents=True)
    record = {"model": args.model, "claude_version": claude_version(), "rules_sha": meta.get("rules_sha"),
              "at": _dt.datetime.now().isoformat(timespec="seconds"), "rounds": [], "passed": False,
              "isolation": None, "cost_usd": 0.0}
    for mode in modes:
        log(f"probe round: isolation={mode}")
        round_ = {"isolation": mode, "arms": [probe_arm(a, arms_root / a, args.model, mode, out_dir,
                                                        skill_name=meta.get("skill", DEFAULT_SKILL)) for a in arms]}
        record["rounds"].append(round_)
        record["cost_usd"] = round(record["cost_usd"] + sum(a["cost_usd"] for a in round_["arms"]), 4)
        for a in round_["arms"]:
            if mode == "settings-sources":
                log(f"  {a['arm']:10} sentinel {a['sentinel']}  hook-events {a['hook_events_total']} "
                    f"(maintainer {a['maintainer_hook_events']})  caveman-marker-untouched "
                    f"{a['caveman_marker_untouched']}  skill-visible {a['skill_visible']} (want "
                    f"{a['skill_visible_expected']}: {a['skill_visible_call']['skills_line'][:60]!r})  "
                    f"${a['cost_usd']}  -> {'PASS' if a['passed'] else 'FAIL'}")
            else:
                log(f"  {a['arm']:10} sentinel {a['sentinel']}  caveman-absent {a['caveman_active_absent']}  "
                    f"hook-events {a['hook_events_total']}  hooks-reported {a['hooks_reported']}  "
                    f"skill-listed {a['skill_listed']}  ${a['cost_usd']}  -> {'PASS' if a['passed'] else 'FAIL'}")
        if all(a["passed"] for a in round_["arms"]):
            record["passed"], record["isolation"] = True, mode
            break
    last_round = record["rounds"][-1]["arms"] if record["rounds"] else []
    meta["probe"] = {"passed": record["passed"], "isolation": record["isolation"], "at": record["at"],
                     "rules_sha": meta.get("rules_sha"), "model": args.model, "cost_usd": record["cost_usd"],
                     "arms": list(arms),
                     "skill_visible": {a["arm"]: a.get("skill_visible") for a in last_round},
                     "record": str(out_dir / "probe.json")}
    (arms_root / "arms.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (out_dir / "probe.json").write_text(json.dumps(strip_export(record), indent=2) + "\n", encoding="utf-8")
    if args.export:
        Path(args.export).write_text(json.dumps(strip_export(record), indent=2) + "\n", encoding="utf-8")
        log(f"wrote {args.export}")
    log(f"probe {'PASSED' if record['passed'] else 'FAILED'} isolation={record['isolation']} "
        f"cost=${record['cost_usd']}  ({out_dir / 'probe.json'})")
    return 0 if record["passed"] else 1


# ── selftest ──────────────────────────────────────────────────────────────
class Selftest:
    def __init__(self) -> None:
        self.results: dict[str, list[bool]] = {}

    def case(self, group: str, name: str, ok: bool, detail: str = "") -> bool:
        self.results.setdefault(group, []).append(bool(ok))
        print(f"{'OK    ' if ok else 'FAILED'} {group:10} {name}{('  ' + detail) if detail else ''}")
        return bool(ok)

    def summary(self) -> bool:
        total = sum(len(v) for v in self.results.values())
        passed = sum(sum(v) for v in self.results.values())
        parts = ", ".join(f"{g} {sum(v)}/{len(v)}" for g, v in self.results.items())
        print(f"\nselftest: {passed}/{total} OK  ({parts})")
        return passed == total


def selftest_loc(st: Selftest) -> None:
    files = sorted(p for p in FIXTURES.glob("*.md") if p.name != "README.md")
    st.case("loc", "fixtures present", len(files) == 11, f"{len(files)}/11 files")
    sections: list[tuple[str, str, str]] = []
    for f in files:
        w, p = example_sections(f)
        sections += [(f.stem, "without", w), (f.stem, "with", p)]
    ours = [chat_code_loc(t) for _, _, t in sections]
    oracle = node_loc_oracle([t for _, _, t in sections])
    if oracle is None:
        st.case("loc", "loc.js oracle", False, "node not on PATH")
        return
    for (stem, kind, _), a, b in zip(sections, ours, oracle):
        st.case("loc", f"{stem}/{kind} port == loc.js", a == b, f"{a} vs {b}")
    for f in files:
        w = chat_code_loc(example_sections(f)[0])
        p = chat_code_loc(example_sections(f)[1])
        if f.stem in DEPENDENCY_REMOVAL_EXAMPLES:
            # Measured 2026-09-05: the plan assumed Without > With on all 11; on these three the
            # upstream's own counter says otherwise, because the gain shown is a dependency removed
            # ("1 dependency → 0 dependencies"), demonstrated with a longer usage snippet. The
            # selftest pins that reading instead of asserting a false 11/11.
            with_text = example_sections(f)[1]
            st.case("loc", f"{f.stem} is a dependency-removal example (With >= Without, says so)",
                    p >= w and "0 dependencies" in with_text, f"{w} vs {p}")
        else:
            st.case("loc", f"{f.stem} Without > With", w > p, f"{w} > {p}")


def selftest_scorers(st: Selftest, tasks: dict[str, Task]) -> None:
    for tid in TASK_IDS:
        task = tasks[tid]
        for kind in ("good", "bad"):
            with tempfile.TemporaryDirectory(prefix="lean-selftest-") as d:
                wd = Path(d)
                task.seed(wd)
                getattr(task, kind)(wd)
                r = task.score(wd)
            if kind == "good":
                ok = r.get("correct") == 1 and r.get("safe") == 1
            else:
                ok = r.get(task.axis) == 0
            label = f"{tid} {kind}" + (" [STRUCTURAL]" if task.structural else "")
            st.case("scorers", label, ok, f"correct={r.get('correct')} safe={r.get('safe')} axis={task.axis}  {str(r.get('reason', ''))[:70]}")
        # variants: the good reference with one decision changed, and the verdict decided in task.py
        for name, variant in task.variants.items():
            with tempfile.TemporaryDirectory(prefix="lean-selftest-") as d:
                wd = Path(d)
                task.seed(wd)
                task.good(wd)
                variant["apply"](wd)
                r = task.score(wd)
            expect = variant["expect"]
            ok = all(r.get(k) == v for k, v in expect.items())
            st.case("scorers", f"{tid} variant {name}", ok,
                    f"expect={expect} got={{'correct': {r.get('correct')}, 'safe': {r.get('safe')}}}  {str(r.get('reason', ''))[:70]}")


def selftest_detectors(st: Selftest) -> None:
    yes = "Done.\n\n```python\nx = 1\n```\n\nskipped: retry logic, add when the upstream API starts timing out."
    no = "Done. I did not add retries; they could be added later if needed."
    st.case("detectors", "output_contract fires on `skipped: … add when …`", detect_output_contract(yes))
    st.case("detectors", "output_contract silent without the pair", not detect_output_contract(no))
    st.case("detectors", "output_contract silent on `skipped:` alone",
            not detect_output_contract("skipped: nothing else to say here"))

    marker_ok = "def f(x):\n    return x * 2  # lean: ints only -> accept floats when the CSV carries them\n"
    marker_bad = "def f(x):\n    return x * 2  # lean: ints only, upgrade later\n"
    m1 = detect_lean_marker(marker_ok)
    m2 = detect_lean_marker(marker_bad)
    m3 = detect_lean_marker("def f(x):\n    return x\n")
    st.case("detectors", "lean_marker counts ceiling -> trigger", m1 == {"lean_marker": 1, "lean_marker_malformed": 0}, str(m1))
    st.case("detectors", "lean_marker flags a marker without `->`", m2 == {"lean_marker": 0, "lean_marker_malformed": 1}, str(m2))
    st.case("detectors", "lean_marker silent with no marker", m3 == {"lean_marker": 0, "lean_marker_malformed": 0}, str(m3))

    st.case("detectors", "one_check via test lines", detect_one_check("def f(): pass", 3))
    st.case("detectors", "one_check via __main__ guard", detect_one_check("if __name__ == '__main__':\n    assert f(1) == 2", 0))
    st.case("detectors", "one_check silent with no check", not detect_one_check("def f(x):\n    return x\n", 0))

    declared, local = {"fastapi", "pydantic"}, {"app", "textutils"}
    d1 = detect_new_dependency({"articles.py": "import requests\nfrom textutils import slugify\nimport os\n"}, "", "", declared, local)
    d2 = detect_new_dependency({"app/api/items.py": "from fastapi import APIRouter\nfrom app.core import x\nimport json\n"}, "", "", declared, local)
    d3 = detect_new_dependency({}, "+++ b/package.json\n+    \"swr\": \"^2.3.0\",\n", "", {"axios", "zod"}, set())
    d4 = detect_new_dependency({"src/hooks/useOrders.ts": "import useSWR from 'swr';\nimport { z } from 'zod';\n"}, "", "", {"axios", "zod"}, set())
    d5 = detect_new_dependency({}, "", "Run `npm install lodash` first.", set(), set())
    st.case("detectors", "new_dependency: requests flagged, stdlib and local not", d1 == ["requests"], str(d1))
    st.case("detectors", "new_dependency silent on declared + stdlib + local package", d2 == [], str(d2))
    st.case("detectors", "new_dependency: package.json line", d3 == ["swr"], str(d3))
    st.case("detectors", "new_dependency: ts import of undeclared package", d4 == ["swr"], str(d4))
    st.case("detectors", "new_dependency: install mentioned in the answer", d5 == ["lodash"], str(d5))
    for text in ("Run `pip install -r requirements.txt`", "Then run:\nnpm install\nnpm run dev",
                 "pip install pytest to run the tests."):
        d6 = detect_new_dependency({}, "", text, {"pytest", "fastapi"}, set())
        st.case("detectors", f"new_dependency silent on {text.splitlines()[0][:34]!r}", d6 == [], str(d6))
    # the 2026-09-05 baseline: `import pytest` in the test file, stdlib in the product (8/27 cells)
    seed_like = {"db.py": "import sqlite3\n", "test_db.py": "import sqlite3\n\nimport pytest\n\nfrom db import get_user\n"}
    d7 = detect_new_dependency(seed_like, "", "", set(), {"db"})
    t7 = detect_test_dependency(seed_like, set(), {"db"})
    st.case("detectors", "new_dependency silent on `import pytest` in a test file", d7 == [], str(d7))
    st.case("detectors", "test_dependency records the pytest import instead", t7 == ["pytest"], str(t7))
    d8 = detect_new_dependency({"db.py": "import requests\n", "test_db.py": "import pytest\n"}, "", "", set(), {"db"})
    st.case("detectors", "new_dependency still flags a production import next to a test import", d8 == ["requests"], str(d8))
    d9 = detect_new_dependency({"src/hooks/useOrders.test.ts": "import { it } from 'vitest';\n"}, "", "", {"zod"}, set())
    st.case("detectors", "new_dependency silent on a vitest import in a .test.ts", d9 == [], str(d9))
    # the class heuristic: a unittest.TestCase in the test file is not a class in the product (3/27 cells)
    only_test_class = {"added_text": "class GetUserTest(unittest.TestCase):\n    pass\n", "added_lines": 7,
                       "added_by_file": {"db.py": "    cur = conn.execute(q, (username,))\n",
                                         "test_db.py": "class GetUserTest(unittest.TestCase):\n    pass\n"}}
    dt = run_detectors("sql-user", only_test_class, "", None, set(), {"db"})
    st.case("detectors", "class_added silent when the only class is in the test file",
            not dt["class_added"] and dt["test_class_added"], str({k: dt[k] for k in ("class_added", "test_class_added")}))
    prod_class = {"added_text": "class InsufficientFunds(Exception):\n    pass\n", "added_lines": 3,
                  "added_by_file": {"bank.py": "class InsufficientFunds(Exception):\n    pass\n",
                                    "test_bank.py": "def test_x():\n    assert True\n"}}
    dp = run_detectors("trace-transfer", prod_class, "", None, set(), {"bank"})
    st.case("detectors", "class_added fires on a class in the product file",
            dp["class_added"] and not dp["test_class_added"], str({k: dp[k] for k in ("class_added", "test_class_added")}))

    long_prose = "\n".join(f"Explanation line {i}." for i in range(12)) + "\n```python\nx = 1\n```\n"
    st.case("detectors", "prose_gt_code fires: 12 prose lines vs 4 added", detect_prose_gt_code(long_prose, 4))
    st.case("detectors", "prose_gt_code silent: 12 prose lines vs 40 added", not detect_prose_gt_code(long_prose, 40))
    st.case("detectors", "prose_gt_code silent when nothing was added", not detect_prose_gt_code(long_prose, 0))
    st.case("detectors", "prose_lines ignores fenced code", prose_lines(long_prose) == 12, str(prose_lines(long_prose)))

    # flags derived from a cell
    cell = {"task": "trace-transfer", "correct": 1, "safe": 0, "added_lines": 5,
            "detectors": {"one_check": False, "new_dependency": [], "prose_gt_code": False, "class_added": True}}
    fl = cell_flags(cell)
    st.case("detectors", "flags: patched_caller_only + no_check + class_for_oneliner on trace-transfer",
            fl["patched_caller_only"] and fl["no_check"] and fl["class_for_oneliner"] and not fl["guard_dropped"], str({k: v for k, v in fl.items() if v}))
    cell2 = {"task": "react-use-orders", "correct": 1, "safe": 0, "reuse": 0, "structural": True, "added_lines": 9,
             "detectors": {"one_check": True, "new_dependency": ["swr"], "prose_gt_code": False}}
    fl2 = cell_flags(cell2)
    st.case("detectors", "flags: structural task never yields guard_dropped, does yield reimplemented_existing",
            not fl2["guard_dropped"] and fl2["reimplemented_existing"] and fl2["new_dependency"], str({k: v for k, v in fl2.items() if v}))


def selftest_arms(st: Selftest) -> None:
    settings = {"model": "opus[1m]", "effortLevel": "high", "modelSettings": {"x": {"effortLevel": "xhigh"}},
                "skillOverrides": {"documentation": "off"}, "hooks": {"Stop": []},
                "enabledPlugins": {"caveman@caveman": True}, "extraKnownMarketplaces": {"caveman": {}},
                "statusLine": {"type": "command"}, "permissions": {"allow": ["Bash(ls)"]}, "theme": "dark"}
    fs = filtered_settings(settings)
    st.case("arms", "filtered settings keep exactly model/effortLevel/modelSettings/skillOverrides",
            set(fs) == set(KEEP_SETTINGS_KEYS), str(sorted(fs)))
    with tempfile.TemporaryDirectory(prefix="lean-arms-") as d:
        root = Path(d)
        tree = root / "tree" / "skills"
        for name in ("bug-hunter", "fivem-lua", DEFAULT_SKILL):
            (tree / name).mkdir(parents=True)
            (tree / name / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
        rules = "# Personal Rules (Global)\n\nSome rule.\n"
        base = prepare_arm(root / "arms", "baseline", settings, b'{"claudeAiOauth": {}}', rules, tree, DEFAULT_SKILL, False)
        skill = prepare_arm(root / "arms", "skill", settings, b'{"claudeAiOauth": {}}', rules, tree, DEFAULT_SKILL, True)
        st.case("arms", "baseline preflight OK", arm_preflight(base, "baseline") == [], "; ".join(arm_preflight(base, "baseline")))
        st.case("arms", "skill preflight OK", arm_preflight(skill, "skill") == [], "; ".join(arm_preflight(skill, "skill")))
        st.case("arms", "baseline has no skills/lean-code, skill arm has it",
                not (base / "skills" / DEFAULT_SKILL).exists() and (skill / "skills" / DEFAULT_SKILL).is_symlink())
        st.case("arms", "skills/ entries are symlinks (install.sh shape)",
                all(p.is_symlink() for p in (base / "skills").iterdir()) and len(list((base / "skills").iterdir())) == 2)
        st.case("arms", "CLAUDE.md ends with the sentinel line",
                (base / "CLAUDE.md").read_text(encoding="utf-8").rstrip().endswith(f"{SENTINEL}: baseline"))
        st.case("arms", "HOME fallback: home/.claude -> arm dir", (base / "home" / ".claude" / "settings.json").exists())
        # injected defects, one per rule
        s = json.loads((base / "settings.json").read_text(encoding="utf-8"))
        s["hooks"] = {"Stop": []}
        (base / "settings.json").write_text(json.dumps(s), encoding="utf-8")
        st.case("arms", "preflight catches `hooks` in settings.json", any("hooks" in p for p in arm_preflight(base, "baseline")))
        s.pop("hooks"); s["enabledPlugins"] = {"caveman@caveman": True}
        (base / "settings.json").write_text(json.dumps(s), encoding="utf-8")
        st.case("arms", "preflight catches `enabledPlugins`", any("enabledPlugins" in p for p in arm_preflight(base, "baseline")))
        s.pop("enabledPlugins")
        (base / "settings.json").write_text(json.dumps(s), encoding="utf-8")
        (base / "CLAUDE.md").write_text(rules, encoding="utf-8")
        st.case("arms", "preflight catches a missing sentinel", any(SENTINEL in p for p in arm_preflight(base, "baseline")))
        (base / "CLAUDE.md").write_text(rules + f"\n{SENTINEL}: baseline\n", encoding="utf-8")
        os.chmod(base / ".credentials.json", 0o644)
        st.case("arms", "preflight catches credentials mode 644", any("mode" in p for p in arm_preflight(base, "baseline")))
        os.chmod(base / ".credentials.json", 0o600)
        os.symlink(str(tree / DEFAULT_SKILL), str(base / "skills" / DEFAULT_SKILL))
        st.case("arms", "preflight catches skills/lean-code in the baseline", any(DEFAULT_SKILL in p for p in arm_preflight(base, "baseline")))
        os.unlink(base / "skills" / DEFAULT_SKILL)
        (base / ".caveman-active").write_text("1", encoding="utf-8")
        st.case("arms", "preflight catches a stray .caveman-active", any("caveman" in p for p in arm_preflight(base, "baseline")))
        (base / ".caveman-active").unlink()
        st.case("arms", "preflight clean again after repairs", arm_preflight(base, "baseline") == [])
    inside = REPO_ROOT / "research" / "lean-code" / "_would_be_inside"
    st.case("arms", "roots inside the repository are refused",
            not outside_repo(inside) and outside_repo(Path(tempfile.gettempdir()) / "x")
            and any("inside the repository" in p for p in arm_preflight(inside, "baseline")))


def selftest_isolation(st: Selftest, tasks: dict[str, Task]) -> None:
    """settings-sources mode: the three arms copy nothing and carry their skillOverrides value, the
    block exactly where ARM_LAYOUT puts it and the project skill only in the skill arm; the cell
    workspace commits the arm files (and the skill arm's .claude/skills/<skill>) in the seed and the
    counters ignore them; the command has the setting-sources flags and acceptEdits; the probe
    workspace, the stream parser and the skills-line parser."""
    settings = {"model": "opus[1m]", "effortLevel": "high", "modelSettings": {"x": {"effortLevel": "xhigh"}},
                "skillOverrides": {"documentation": "off"}, "hooks": {"Stop": []},
                "enabledPlugins": {"caveman@caveman": True}, "extraKnownMarketplaces": {"caveman": {}},
                "statusLine": {"type": "command"}, "permissions": {"allow": ["Bash(ls)"]}, "theme": "dark"}
    with tempfile.TemporaryDirectory(prefix="lean-ss-") as d:
        root = Path(d)
        checkout = root / "checkout" / "skills" / DEFAULT_SKILL       # stands in for <worktree>/skills/lean-code
        (checkout / "references").mkdir(parents=True)
        (checkout / "SKILL.md").write_text(f"---\nname: {DEFAULT_SKILL}\n---\n# Lean code\n", encoding="utf-8")
        (checkout / "references" / "upstream.md").write_text("# upstream\n", encoding="utf-8")
        block = "Before writing a line, climb the ladder.\n- one guard where all callers route through.\n"
        meta = {"rules_sha": "abc123"}
        base = prepare_arm_settings_sources(root / "arms", "baseline", settings, DEFAULT_SKILL, meta=meta,
                                            claude_block=block, project_skill_path=checkout)
        blk = prepare_arm_settings_sources(root / "arms", "block", settings, DEFAULT_SKILL, meta=meta,
                                           claude_block=block, project_skill_path=checkout)
        skill = prepare_arm_settings_sources(root / "arms", "skill", settings, DEFAULT_SKILL, meta=meta,
                                             claude_block=block, project_skill_path=checkout)
        ps_b = json.loads((base / "project-settings.json").read_text(encoding="utf-8"))
        ps_k = json.loads((blk / "project-settings.json").read_text(encoding="utf-8"))
        ps_s = json.loads((skill / "project-settings.json").read_text(encoding="utf-8"))
        st.case("isolation", "project-settings.json keeps model/effortLevel/modelSettings/skillOverrides; hooks, enabledPlugins absent",
                set(ps_b) == set(KEEP_SETTINGS_KEYS) and not any(k in ps_b for k in STRIP_SETTINGS_KEYS), str(sorted(ps_b)))
        st.case("isolation", "skillOverrides[lean-code] is 'off' in baseline and block, 'on' in the skill arm; the maintainer's entries kept",
                ps_b["skillOverrides"][DEFAULT_SKILL] == SKILL_OVERRIDE_OFF and ps_k["skillOverrides"][DEFAULT_SKILL] == SKILL_OVERRIDE_OFF
                and ps_s["skillOverrides"][DEFAULT_SKILL] == SKILL_OVERRIDE_ON
                and all(ps["skillOverrides"]["documentation"] == "off" for ps in (ps_b, ps_k, ps_s)),
                f"baseline={ps_b['skillOverrides']} block={ps_k['skillOverrides']} skill={ps_s['skillOverrides']}")
        st.case("isolation", "arm dirs have no .credentials.json, CLAUDE.md, settings.json, skills/ or home/",
                not any((a / n).exists() for a in (base, blk, skill) for n in (".credentials.json", "CLAUDE.md", "settings.json", "skills", "home")),
                ", ".join(sorted(p.name for p in skill.iterdir())))
        snip_b = (base / "claude-snippet.md").read_text(encoding="utf-8")
        snip_k = (blk / "claude-snippet.md").read_text(encoding="utf-8")
        snip_s = (skill / "claude-snippet.md").read_text(encoding="utf-8")
        st.case("isolation", "snippets: baseline = sentinel only (block passed and ignored); block and skill = sentinel + blank line + block",
                snip_b == f"{SENTINEL}: baseline\n" and snip_k == f"{SENTINEL}: block\n\n{block}"
                and snip_s == f"{SENTINEL}: skill\n\n{block}", repr(snip_k))
        aj_b = json.loads((base / "arm.json").read_text(encoding="utf-8"))
        aj_k = json.loads((blk / "arm.json").read_text(encoding="utf-8"))
        aj_s = json.loads((skill / "arm.json").read_text(encoding="utf-8"))
        st.case("isolation", "arm.json records isolation=settings-sources, rules_sha, skill_override off/off/on and includes_block/includes_skill per ARM_LAYOUT",
                all(a["isolation"] == "settings-sources" and a["rules_sha"] == "abc123" for a in (aj_b, aj_k, aj_s))
                and arm_isolation(base) == "settings-sources"
                and (aj_b["skill_override"], aj_k["skill_override"], aj_s["skill_override"]) == (SKILL_OVERRIDE_OFF, SKILL_OVERRIDE_OFF, SKILL_OVERRIDE_ON)
                and (aj_b["includes_block"], aj_b["includes_skill"]) == (False, False)
                and (aj_k["includes_block"], aj_k["includes_skill"]) == (True, False)
                and (aj_s["includes_block"], aj_s["includes_skill"]) == (True, True))
        st.case("isolation", "arm.json claude_block_sha256: null in baseline, the block's sha in block and skill",
                aj_b["claude_block_sha256"] is None and aj_k["claude_block_sha256"] == block_sha256(block)
                and aj_s["claude_block_sha256"] == block_sha256(block))
        st.case("isolation", "arm.json project_skill_path: the resolved skills/<skill> of the checkout in the skill arm, null in baseline and block",
                aj_s["project_skill_path"] == str(checkout.resolve()) and aj_b["project_skill_path"] is None
                and aj_k["project_skill_path"] is None, str(aj_s["project_skill_path"]))
        st.case("isolation", "workspace_dirs: {} for baseline and block, .claude/skills/<skill> -> project_skill_path for the skill arm",
                workspace_dirs(base) == {} and workspace_dirs(blk) == {}
                and workspace_dirs(skill) == {f".claude/skills/{DEFAULT_SKILL}": Path(str(checkout.resolve()))})
        st.case("isolation", "baseline + block + skill preflight OK (nothing read from ~/.claude/skills)",
                arm_preflight(base, "baseline") == [] and arm_preflight(blk, "block") == [] and arm_preflight(skill, "skill") == [],
                "; ".join(arm_preflight(base, "baseline") + arm_preflight(blk, "block") + arm_preflight(skill, "skill")))
        ws_s = workspace_files(skill)["CLAUDE.md"]
        st.case("isolation", "the skill cell's CLAUDE.md carries the block after the sentinel, still a harness path",
                ws_s.startswith(f"{SENTINEL}: skill\n") and block in ws_s and is_harness_path("CLAUDE.md"))
        # injected defects, one per rule
        (base / "claude-snippet.md").write_text(f"{SENTINEL}: baseline\n\n{block}", encoding="utf-8")
        st.case("isolation", "preflight catches the block in the baseline snippet",
                any("more than the sentinel" in p for p in arm_preflight(base, "baseline")))
        (base / "claude-snippet.md").write_text(snip_b, encoding="utf-8")
        (blk / "claude-snippet.md").write_text(f"{SENTINEL}: block\n", encoding="utf-8")
        st.case("isolation", "preflight catches a block snippet without the block arm.json promises",
                any("claude_block_sha256" in p for p in arm_preflight(blk, "block")))
        (blk / "claude-snippet.md").write_text(f"{SENTINEL}: block\n\n{block}edited\n", encoding="utf-8")
        st.case("isolation", "preflight catches a block edited after --prepare-arms (sha mismatch)",
                any("does not match" in p for p in arm_preflight(blk, "block")))
        (blk / "claude-snippet.md").write_text(snip_k, encoding="utf-8")
        aj_k2 = dict(aj_k); aj_k2["claude_block_sha256"] = None
        (blk / "arm.json").write_text(json.dumps(aj_k2), encoding="utf-8")
        st.case("isolation", "preflight catches a block arm prepared without --claude-block",
                any("needs --prepare-arms --claude-block" in p for p in arm_preflight(blk, "block")))
        aj_k2["claude_block_sha256"] = block_sha256(block); aj_k2["project_skill_path"] = str(checkout)
        (blk / "arm.json").write_text(json.dumps(aj_k2), encoding="utf-8")
        st.case("isolation", "preflight catches a project_skill_path in the block arm (only the skill arm carries one)",
                any("only the skill arm" in p for p in arm_preflight(blk, "block")))
        (blk / "arm.json").write_text(json.dumps(aj_k), encoding="utf-8")
        aj_s2 = dict(aj_s); aj_s2["project_skill_path"] = str(root / "gone" / DEFAULT_SKILL)
        (skill / "arm.json").write_text(json.dumps(aj_s2), encoding="utf-8")
        st.case("isolation", "preflight refuses a skill arm whose project_skill_path is missing",
                any("has no SKILL.md" in p for p in arm_preflight(skill, "skill")))
        aj_s2["project_skill_path"] = None
        (skill / "arm.json").write_text(json.dumps(aj_s2), encoding="utf-8")
        st.case("isolation", "preflight refuses a skill arm without project_skill_path",
                any("has no project_skill_path" in p for p in arm_preflight(skill, "skill")))
        (skill / "arm.json").write_text(json.dumps(aj_s), encoding="utf-8")
        (base / ".credentials.json").write_text("{}", encoding="utf-8")
        st.case("isolation", "preflight catches a stray .credentials.json",
                any("credentials" in p for p in arm_preflight(base, "baseline")))
        (base / ".credentials.json").unlink()
        ps_b["skillOverrides"][DEFAULT_SKILL] = SKILL_OVERRIDE_ON
        (base / "project-settings.json").write_text(json.dumps(ps_b), encoding="utf-8")
        st.case("isolation", "preflight catches skillOverrides 'on' in the baseline",
                any("skillOverrides" in p for p in arm_preflight(base, "baseline")))
        ps_b["skillOverrides"][DEFAULT_SKILL] = SKILL_OVERRIDE_OFF
        ps_b["hooks"] = {"Stop": []}
        (base / "project-settings.json").write_text(json.dumps(ps_b), encoding="utf-8")
        st.case("isolation", "preflight catches `hooks` in project-settings.json",
                any("hooks" in p for p in arm_preflight(base, "baseline")))
        ps_b.pop("hooks")
        (base / "project-settings.json").write_text(json.dumps(ps_b), encoding="utf-8")
        (base / "claude-snippet.md").write_text("nothing here\n", encoding="utf-8")
        st.case("isolation", "preflight catches a missing sentinel",
                any(SENTINEL in p for p in arm_preflight(base, "baseline")))
        (base / "claude-snippet.md").write_text(snip_b, encoding="utf-8")
        st.case("isolation", "preflight clean again after repairs",
                arm_preflight(base, "baseline") == [] and arm_preflight(blk, "block") == [] and arm_preflight(skill, "skill") == [])

        # the cell workspace: seed + arm files in one base commit, counters blind to them
        repo = root / "repo"
        seed_repo(tasks["trace-transfer"], repo, workspace_files(base), workspace_dirs(base))
        tracked = git(repo, "ls-tree", "-r", "--name-only", "HEAD").stdout.split()
        st.case("isolation", "baseline workspace commits .claude/settings.json and CLAUDE.md in the seed commit, no .claude/skills",
                ".claude/settings.json" in tracked and "CLAUDE.md" in tracked
                and not any(t.startswith(".claude/skills/") for t in tracked) and not (repo / ".claude" / "skills").exists(),
                " ".join(sorted(tracked)))
        st.case("isolation", "workspace CLAUDE.md is the sentinel; .claude/settings.json equals the arm's",
                (repo / "CLAUDE.md").read_text(encoding="utf-8") == f"{SENTINEL}: baseline\n"
                and json.loads((repo / ".claude" / "settings.json").read_text(encoding="utf-8")) == ps_b)
        repo_k = root / "repo-block"
        seed_repo(tasks["trace-transfer"], repo_k, workspace_files(blk), workspace_dirs(blk))
        st.case("isolation", "block workspace: CLAUDE.md = sentinel + block, no .claude/skills",
                (repo_k / "CLAUDE.md").read_text(encoding="utf-8") == snip_k and not (repo_k / ".claude" / "skills").exists())
        repo_s = root / "repo-skill"
        seed_repo(tasks["trace-transfer"], repo_s, workspace_files(skill), workspace_dirs(skill))
        tracked_s = git(repo_s, "ls-tree", "-r", "--name-only", "HEAD").stdout.split()
        proj = repo_s / ".claude" / "skills" / DEFAULT_SKILL
        st.case("isolation", "skill workspace: .claude/skills/<skill> is a real directory (copied, not a symlink) committed in the seed, content == the checkout's",
                proj.is_dir() and not proj.is_symlink()
                and f".claude/skills/{DEFAULT_SKILL}/SKILL.md" in tracked_s
                and f".claude/skills/{DEFAULT_SKILL}/references/upstream.md" in tracked_s
                and (proj / "SKILL.md").read_text(encoding="utf-8") == (checkout / "SKILL.md").read_text(encoding="utf-8"),
                " ".join(sorted(t for t in tracked_s if t.startswith(".claude"))))
        s0 = git_diff_stats(repo_s)
        st.case("isolation", "fresh skill workspace: added_lines 0, no changed paths", s0["added_lines"] == 0 and s0["changed_paths"] == [])
        (repo_s / "CLAUDE.md").write_text(f"{SENTINEL}: skill\n# lean: x -> y\n", encoding="utf-8")
        (repo_s / ".claude" / "helper.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
        (proj / "SKILL.md").write_text("# edited by the cell\nimport requests\n", encoding="utf-8")
        tasks["trace-transfer"].bad(repo_s)
        s1 = git_diff_stats(repo_s)
        st.case("isolation", "CLAUDE.md, .claude/ and .claude/skills/<skill> edits excluded from added_lines, code_loc, changed_paths and detector text",
                s1["added_lines"] == 2 and s1["code_loc"] == 2 and not any(is_harness_path(p) for p in s1["changed_paths"])
                and "lean:" not in s1["added_text"] and "helper" not in s1["added_text"] and "requests" not in s1["added_text"],
                f"added={s1['added_lines']} code={s1['code_loc']} paths={s1['changed_paths']}")
        st.case("isolation", "is_harness_path: CLAUDE.md, .claude/** and .claude/skills/<skill>/** yes; src/CLAUDE.md and claude.py no",
                is_harness_path("CLAUDE.md") and is_harness_path(".claude/settings.json") and is_harness_path(".claude/a/b.py")
                and is_harness_path(f".claude/skills/{DEFAULT_SKILL}/SKILL.md")
                and not is_harness_path("src/CLAUDE.md") and not is_harness_path("claude.py") and not is_harness_path(".claude_x/y"))
        fake = Task(id="fake", source="selftest", prompt="", entry="a.py", axis="safe",
                    seed=lambda wd: _write_files(wd, {"CLAUDE.md": "# Project rules\n", "a.py": "x = 1\n"}),
                    good=lambda wd: None, bad=lambda wd: None, score=lambda wd: {})
        seed_repo(fake, root / "repo2", workspace_files(base))
        txt = (root / "repo2" / "CLAUDE.md").read_text(encoding="utf-8")
        st.case("isolation", "a seed that already has a CLAUDE.md keeps it and gets the sentinel appended",
                txt.startswith("# Project rules") and txt.rstrip().endswith(f"{SENTINEL}: baseline"), repr(txt))

        # command and env
        cmd = cell_command("p", "m", CELL_BUDGET_USD, "settings-sources")
        st.case("isolation", "cell command: --setting-sources project,local + acceptEdits, no bypassPermissions, protocol flags kept",
                cmd[cmd.index("--setting-sources") + 1] == "project,local" and cmd[cmd.index("--permission-mode") + 1] == "acceptEdits"
                and "bypassPermissions" not in cmd
                and all(f in cmd for f in ("--disallowedTools", "Bash", "--strict-mcp-config", "--no-session-persistence",
                                           "--output-format", "json", "--max-budget-usd", "1.00")) and NO_RUN in cmd)
        env = cell_env(root / "nowhere", "settings-sources")
        st.case("isolation", "cell env: CLAUDECODE popped, HOME and CLAUDE_CONFIG_DIR untouched",
                "CLAUDECODE" not in env and env.get("HOME") == os.environ.get("HOME")
                and env.get("CLAUDE_CONFIG_DIR") == os.environ.get("CLAUDE_CONFIG_DIR"))
        pc = probe_command("m", PROBE_BUDGET_USD, "settings-sources")
        st.case("isolation", "probe command: stream-json --verbose --include-hook-events --tools '' + setting sources, no bypassPermissions",
                all(f in pc for f in ("stream-json", "--verbose", "--include-hook-events", "--tools", "", "--setting-sources", "project,local"))
                and "bypassPermissions" not in pc and PROBE_PROMPT_SENTINEL_ONLY in pc)
        cwd = probe_workspace(base, root / "probe-cwd")
        st.case("isolation", "probe workspace carries the sentinel CLAUDE.md and the arm's .claude/settings.json",
                (cwd / "CLAUDE.md").read_text(encoding="utf-8") == f"{SENTINEL}: baseline\n"
                and json.loads((cwd / ".claude" / "settings.json").read_text(encoding="utf-8")) == ps_b
                and not (cwd / ".claude" / "skills").exists())
        cwd_s = probe_workspace(skill, root / "probe-cwd-skill")
        st.case("isolation", "probe workspace of the skill arm carries .claude/skills/<skill>/SKILL.md (what the skills-list call must see)",
                (cwd_s / ".claude" / "skills" / DEFAULT_SKILL / "SKILL.md").is_file())
        pk = probe_command("m", PROBE_BUDGET_USD, "settings-sources", prompt=PROBE_PROMPT_SKILLS)
        st.case("isolation", "probe skills-list command carries PROBE_PROMPT_SKILLS, --tools '' and the setting sources",
                PROBE_PROMPT_SKILLS in pk and PROBE_PROMPT_SENTINEL_ONLY not in pk
                and all(f in pk for f in ("--tools", "", "--setting-sources", "project,local")))
        with tempfile.TemporaryDirectory() as td:
            _arm = Path(td) / "arm"; _arm.mkdir()
            (_arm / "project-settings.json").write_text("{}\n", encoding="utf-8")
            (_arm / "claude-snippet.md").write_text("BENCH-SENTINEL: t\n", encoding="utf-8")
            (_arm / "arm.json").write_text(json.dumps({"arm": "baseline", "skill": "lean-code", "includes_skill": False,
                                                       "layout": "settings-sources", "project_skill_path": None}), encoding="utf-8")
            _cwd = probe_workspace(_arm, Path(td) / "cwd")
            st.case("isolation", "probe cwd is a git repository root (project skills are discovered only under one)",
                    (_cwd / ".git").is_dir() and (_cwd / "CLAUDE.md").exists(), str(sorted(p.name for p in _cwd.iterdir())))
        # the skills-line parser: the SKILLS: line alone when present, whole answer otherwise, whole-word
        st.case("isolation", "skills_visible_in: `SKILLS: lean-code` and the manual probe's bare `lean-code\\nDONE` are visible",
                skills_visible_in(f"SKILLS: {DEFAULT_SKILL}\nDONE", DEFAULT_SKILL)
                and skills_visible_in(f"SKILLS: bug-hunter, {DEFAULT_SKILL}, fivem-lua\nDONE", DEFAULT_SKILL)
                and skills_visible_in(f"{DEFAULT_SKILL}\nDONE", DEFAULT_SKILL))
        st.case("isolation", "skills_visible_in: `SKILLS: none`, an empty answer and a mention outside the SKILLS: line are not visible",
                not skills_visible_in("SKILLS: none\nDONE", DEFAULT_SKILL) and not skills_visible_in("", DEFAULT_SKILL)
                and not skills_visible_in(f"SKILLS: none\n(CLAUDE.md mentions the {DEFAULT_SKILL} skill)\nDONE", DEFAULT_SKILL))
        st.case("isolation", "skills_visible_in: whole-word (`lean-code-extra` and `my-lean-code` are not `lean-code`)",
                not skills_visible_in(f"SKILLS: {DEFAULT_SKILL}-extra, my-{DEFAULT_SKILL}\nDONE", DEFAULT_SKILL))

        # the stream parser on a clean and on a contaminated run
        result = json.dumps({"type": "result", "subtype": "success", "result": f"{SENTINEL}: baseline\nDONE",
                             "total_cost_usd": 0.01, "num_turns": 1, "duration_ms": 5,
                             "modelUsage": {"claude-haiku-4-5-20251001": {}}, SESSION_KEY: "x"})
        clean = root / "clean.jsonl"
        clean.write_text('{"type":"system","subtype":"init"}\n{"type":"assistant"}\n' + result + "\n", encoding="utf-8")
        dirty = root / "dirty.jsonl"
        dirty.write_text('{"type":"system","subtype":"init"}\n'
                         '{"type":"system","subtype":"hook_started","hook_id":"1","hook_name":"python3 /x/hooks/locale-rite.py","hook_event":"PreToolUse"}\n'
                         '{"type":"system","subtype":"hook_response","hook_id":"2","hook_name":"caveman-activate","hook_event":"SessionStart"}\n'
                         '{"type":"system","subtype":"hook_started","hook_id":"3","hook_name":"some-other-hook","hook_event":"Stop"}\n'
                         + result + "\n", encoding="utf-8")
        pa, pb = parse_stream(clean), parse_stream(dirty)
        st.case("isolation", "stream parse: clean run has 0 hook events, the sentinel, cost and keys without the session id",
                pa["hook_names"] == [] and pa["maintainer_hook_events"] == 0 and f"{SENTINEL}: baseline" in pa["result_text"]
                and pa["cost"] == 0.01 and "total_cost_usd" in pa["result_keys"] and SESSION_KEY not in pa["result_keys"],
                str(pa["result_keys"]))
        st.case("isolation", "stream parse: 3 hook events, 2 naming the maintainer's hooks (locale-rite, caveman)",
                len(pb["hook_names"]) == 3 and pb["maintainer_hook_events"] == 2
                and pb["hook_names"][:2] == ["python3 /x/hooks/locale-rite.py", "caveman-activate"], str(pb["hook_names"]))
        st.case("isolation", "marker mtime: None when absent, equal when untouched, differs when rewritten",
                marker_mtime(root / "absent") is None and marker_mtime(clean) == marker_mtime(clean)
                and (os.utime(clean, (1, 1)) or marker_mtime(clean) == 1.0))


def selftest_export(st: Selftest) -> None:
    home = str(Path.home())
    sample = {SESSION_KEY: "abc", "result": "the whole answer", "uuid": "x",
              "message_uuid": "y", "nested": [{SESSION_KEY: "z", "path": f"{home}/.claude/arms/baseline",
                                              "id": "123e4567-e89b-12d3-a456-426614174000", "cost": 0.1}],
              "total_cost_usd": 0.12}
    out = strip_export(sample)
    dumped = json.dumps(out)
    keys_left = set(out) | set(out["nested"][0])
    st.case("export", "strips session/result/uuid keys",
            not (keys_left & {SESSION_KEY, "result", "uuid", "message_uuid"}) and "whole answer" not in dumped,
            dumped[:120])
    st.case("export", "replaces the home path and uuid-shaped strings",
            home not in dumped and "<uuid>" in dumped and "~/.claude/arms/baseline" in dumped, dumped[:160])
    st.case("export", "keeps the numbers", out["total_cost_usd"] == 0.12 and out["nested"][0]["cost"] == 0.1)


def selftest_kill(st: Selftest) -> None:
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=(os.name != "nt"))
    tree_kill(p)
    try:
        ok = p.wait(timeout=10) is not None
    except subprocess.TimeoutExpired:
        ok = False
        p.kill()
    st.case("kill", "tree_kill terminates a timed-out cell", ok)


def selftest_refusals(st: Selftest) -> None:
    st.case("refusals", "--matrix guard reads SELFTEST_PASSED (False before a green selftest)", SELFTEST_PASSED is False)
    same = check_same_conditions([{"claude_version": "2.1.261 (Claude Code)", "model": "opus[1m]"},
                                  {"claude_version": "2.1.261 (Claude Code)", "model": "opus[1m]"}])
    diff_v = check_same_conditions([{"claude_version": "2.1.261 (Claude Code)", "model": "opus[1m]"},
                                    {"claude_version": "2.1.262 (Claude Code)", "model": "opus[1m]"}])
    diff_m = check_same_conditions([{"claude_version": "2.1.261 (Claude Code)", "model": "opus[1m]"},
                                    {"claude_version": "2.1.261 (Claude Code)", "model": "claude-haiku-4-5-20251001"}])
    st.case("refusals", "--report accepts identical version + model", same is None)
    st.case("refusals", "--report refuses different claude versions", diff_v is not None and "versions" in diff_v, str(diff_v))
    st.case("refusals", "--report refuses different model ids", diff_m is not None and "model" in diff_m, str(diff_m))
    cmd = cell_command("p", "m", CELL_BUDGET_USD, "config-dir")
    st.case("refusals", "legacy cell command carries the protocol flags (bypassPermissions, no setting sources)",
            all(f in cmd for f in ("--permission-mode", "bypassPermissions", "--disallowedTools", "Bash",
                                   "--strict-mcp-config", "--no-session-persistence", "--output-format", "json",
                                   "--max-budget-usd", "1.00")) and NO_RUN in cmd and "--setting-sources" not in cmd)
    st.case("refusals", "probe_gate: no probe -> refuse", "has not passed" in (probe_gate({"rules_sha": "a"}) or ""))
    st.case("refusals", "probe_gate: probe under another rules_sha -> refuse",
            "rules_sha" in (probe_gate({"rules_sha": "b", "isolation": "settings-sources",
                                        "probe": {"passed": True, "rules_sha": "a", "isolation": "settings-sources"}}) or ""))
    st.case("refusals", "probe_gate: legacy probe on settings-sources arms -> refuse",
            "layout" in (probe_gate({"rules_sha": "a", "isolation": "settings-sources",
                                     "probe": {"passed": True, "rules_sha": "a", "isolation": "config-dir"}}) or ""))
    st.case("refusals", "probe_gate: passed, same sha, matching layout -> None",
            probe_gate({"rules_sha": "a", "isolation": "settings-sources",
                        "probe": {"passed": True, "rules_sha": "a", "isolation": "settings-sources"}}) is None
            and probe_gate({"rules_sha": "a", "probe": {"passed": True, "rules_sha": "a", "isolation": "home"}}) is None)
    probed = {"rules_sha": "a", "isolation": "settings-sources", "skill": DEFAULT_SKILL,
              "probe": {"passed": True, "rules_sha": "a", "isolation": "settings-sources",
                        "arms": ["baseline", "block", "skill"],
                        "skill_visible": {"baseline": "0/1", "block": "0/1", "skill": "1/1"}}}
    st.case("refusals", "probe_gate: --arms baseline,block,skill pass when the probe covered them and saw the skill in the skill arm",
            probe_gate(probed, ["baseline", "block", "skill"]) is None)
    unseen = json.loads(json.dumps(probed)); unseen["probe"]["skill_visible"]["skill"] = "0/1"
    st.case("refusals", "probe_gate: --arms skill refused when the probe did not see the skill (skill_visible 0/1)",
            "did not see" in (probe_gate(unseen, ["skill"]) or "") and probe_gate(unseen, ["baseline", "block"]) is None,
            str(probe_gate(unseen, ["skill"]))[:90])
    old = {"rules_sha": "a", "isolation": "settings-sources",
           "probe": {"passed": True, "rules_sha": "a", "isolation": "settings-sources"}}
    st.case("refusals", "probe_gate: a probe from before the criterion (no skill_visible) refuses --arms skill, still passes --arms baseline",
            "did not see" in (probe_gate(old, ["skill"]) or "") and probe_gate(old, ["baseline"]) is None)
    st.case("refusals", "probe_gate: an arm the probe did not cover is refused",
            "not covered" in (probe_gate({**probed, "probe": {**probed["probe"], "arms": ["baseline", "skill"]}}, ["block"]) or ""))


def selftest_metrics(st: Selftest, tasks: dict[str, Task]) -> None:
    """git_diff_stats on a real seed repo: the bad reference of trace-transfer adds exactly the two
    guard lines; a test file is split out; a comment is counted in added_lines and not in code_loc."""
    with tempfile.TemporaryDirectory(prefix="lean-metrics-") as d:
        repo = Path(d) / "repo"
        seed_repo(tasks["trace-transfer"], repo)
        tasks["trace-transfer"].bad(repo)
        (repo / "tests").mkdir()
        (repo / "tests" / "test_bank.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
        (repo / "notes.py").write_text("# a comment\nVALUE = 1\n", encoding="utf-8")
        s = git_diff_stats(repo)
        st.case("metrics", "added_lines counts code files, tests split",
                s["added_lines"] == 4 and s["test_added_lines"] == 2 and s["test_files"] == 1,
                f"added={s['added_lines']} code={s['code_loc']} test_added={s['test_added_lines']}")
        st.case("metrics", "code_loc drops the comment line", s["code_loc"] == 3, str(s["code_loc"]))
        det = run_detectors("trace-transfer", s, "", repo)
        st.case("metrics", "detectors see the check in tests/ and no new dependency",
                det["one_check"] and det["new_dependency"] == [], str(det))
        meta, text = read_claude_json(repo / "missing.json")
        st.case("metrics", "missing _claude.json is an error field, not a crash", meta.get("error") is not None and text == "")


def selftest_rescore(st: Selftest, tasks: dict[str, Task]) -> None:
    """--rescore on a one-cell stamp: the cell is rebuilt by score_cell and the process fields the
    matrix wrote (returncode, killed, wall_s) survive in results.json; a previous cell that never
    had them gets none (a rescore recovers, it does not invent)."""
    import contextlib
    import io
    with tempfile.TemporaryDirectory(prefix="lean-rescore-") as d:
        stamp = Path(d) / "20000101-000000"
        cell_dir = stamp / "trace-transfer__baseline__0"
        repo = cell_dir / "repo"
        seed_repo(tasks["trace-transfer"], repo)
        tasks["trace-transfer"].bad(repo)
        (cell_dir / "_claude.json").write_text(json.dumps(
            {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 10, "num_turns": 1,
             "total_cost_usd": 0.01, "result": "done", "usage": {}}), encoding="utf-8")
        (cell_dir / "_claude.stderr.txt").write_text("", encoding="utf-8")
        previous = {"task": "trace-transfer", "arm": "baseline", "run": 0, "correct": 1,
                    "returncode": 0, "killed": False, "wall_s": 12.3}
        (stamp / "results.json").write_text(json.dumps(
            {"stamp": stamp.name, "model": "selftest", "claude_version": "selftest", "arms": ["baseline"],
             "runs": 1, "results": [previous]}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cmd_rescore(argparse.Namespace(rescore=str(stamp), scorer_venv=None))
        after = json.loads((stamp / "results.json").read_text(encoding="utf-8"))
        cell = after["results"][0] if after.get("results") else {}
        st.case("rescore", "--rescore keeps returncode/killed/wall_s from the previous results.json",
                rc == 0 and len(after["results"]) == 1 and cell.get("returncode") == 0
                and cell.get("killed") is False and cell.get("wall_s") == 12.3 and "rescored_at" in after,
                str({k: cell.get(k) for k in PROCESS_FIELDS}))
        st.case("rescore", "the cell was really rebuilt (scorer and metrics ran)",
                "added_lines" in cell and "detectors" in cell and cell.get("subtype") == "success",
                f"added_lines={cell.get('added_lines')} correct={cell.get('correct')}")
        bare = [{"task": "trace-transfer", "arm": "baseline", "run": 0}]
        fresh = [{"task": "trace-transfer", "arm": "baseline", "run": 0},
                 {"task": "trace-transfer", "arm": "baseline", "run": 1}]
        carried = carry_process_fields(bare + [{"task": "trace-transfer", "arm": "baseline", "run": 1,
                                                "returncode": 0, "killed": True, "wall_s": 300.0}], fresh)
        st.case("rescore", "a previous cell without the fields gets none; matching is per (task, arm, run)",
                carried == 1 and not (set(fresh[0]) & set(PROCESS_FIELDS))
                and fresh[1].get("killed") is True and fresh[1].get("wall_s") == 300.0, str(fresh))


def selftest_relabel(st: Selftest) -> None:
    """--relabel-arm on a synthetic two-cell stamp: refuses while a cell dir lacks _claude.json (and
    leaves the stamp untouched), refuses an unknown destination, then renames the cell dirs,
    rewrites `arm` in results.json / summary.json / classify.json and records the reason."""
    import contextlib
    import io
    with tempfile.TemporaryDirectory(prefix="lean-relabel-") as d:
        stamp = Path(d) / "20000101-000000"
        for r in range(2):
            (stamp / f"trace-transfer__skill__{r}").mkdir(parents=True)
            (stamp / f"trace-transfer__skill__{r}" / "_claude.json").write_text("{}", encoding="utf-8")
        results = [{"task": "trace-transfer", "arm": "skill", "run": r, "added_lines": 5 + r} for r in range(2)]
        header = {"stamp": stamp.name, "model": "m", "claude_version": "v", "arms": ["skill"],
                  "tasks": ["trace-transfer"], "runs": 2, "stopped": None, "results": results}
        (stamp / "results.json").write_text(json.dumps(header), encoding="utf-8")
        (stamp / "summary.json").write_text(json.dumps([{"task": "trace-transfer", "arm": "skill", "n": 2}]), encoding="utf-8")
        (stamp / "classify.json").write_text(json.dumps({"stamp": stamp.name, "rows": [{"task": "trace-transfer", "arm": "skill"}]}), encoding="utf-8")
        reason = "the skill arm measured the always-on block only (user skills dir not visible)"

        def attempt(src: str, dst: str, why: str = reason) -> str:
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    relabel_arm(stamp, src, dst, why)
                    return ""
                except SystemExit as exc:
                    return str(exc)

        (stamp / "trace-transfer__skill__1" / "_claude.json").unlink()
        msg = attempt("skill", "block")
        st.case("relabel", "an unfinished stamp (a cell dir without _claude.json) is refused and left untouched",
                "has not finished" in msg and (stamp / "trace-transfer__skill__0").exists()
                and json.loads((stamp / "results.json").read_text(encoding="utf-8"))["arms"] == ["skill"], msg[:100])
        (stamp / "trace-transfer__skill__1" / "_claude.json").write_text("{}", encoding="utf-8")
        st.case("relabel", "unknown destination, source not in the stamp, and an empty reason are refused",
                "unknown destination" in attempt("skill", "treatment") and "is not in" in attempt("baseline", "block")
                and "--reason" in attempt("skill", "block", ""))
        payload = json.loads((stamp / "results.json").read_text(encoding="utf-8"))
        payload["stopped"] = "run budget exceeded"
        (stamp / "results.json").write_text(json.dumps(payload), encoding="utf-8")
        st.case("relabel", "a stopped run is refused", "stopped" in attempt("skill", "block"))
        payload["stopped"] = None
        (stamp / "results.json").write_text(json.dumps(payload), encoding="utf-8")
        msg = attempt("skill", "block")
        after = json.loads((stamp / "results.json").read_text(encoding="utf-8"))
        dirs = sorted(p.name for p in stamp.iterdir() if p.is_dir())
        st.case("relabel", "cell dirs renamed *__skill__* -> *__block__*, none left behind",
                msg == "" and dirs == ["trace-transfer__block__0", "trace-transfer__block__1"]
                and (stamp / "trace-transfer__block__1" / "_claude.json").exists(), str(dirs))
        st.case("relabel", "results.json: header arms and every cell say block; cells otherwise intact",
                after["arms"] == ["block"] and all(c["arm"] == "block" for c in after["results"])
                and [c["added_lines"] for c in after["results"]] == [5, 6])
        rel = after.get("relabels") or []
        st.case("relabel", "results.json records the relabel with from/to, the reason, the time and the counts",
                len(rel) == 1 and rel[0]["from"] == "skill" and rel[0]["to"] == "block" and rel[0]["reason"] == reason
                and rel[0]["cells"] == 2 and rel[0]["dirs_renamed"] == 2 and "at" in rel[0], str(rel))
        summ = json.loads((stamp / "summary.json").read_text(encoding="utf-8"))
        clas = json.loads((stamp / "classify.json").read_text(encoding="utf-8"))
        st.case("relabel", "summary.json and classify.json rows say block",
                summ[0]["arm"] == "block" and clas["rows"][0]["arm"] == "block")
        st.case("relabel", "a second relabel to an arm already in the stamp is refused",
                "already in the stamp" in attempt("block", "block") or "is not in" in attempt("skill", "block"))


def selftest_report(st: Selftest) -> None:
    """--report deltas on synthetic aggregate rows: Δ% per task and treatment arm against the
    baseline, the over-build group mean, the worst task, correct/safe regressions; no baseline ->
    no deltas; and the table prints."""
    import contextlib
    import io

    def row(task, arm, mean, correct=1.0, safe=1.0):
        return {"task": task, "arm": arm, "n": 3, "correct_rate": correct, "safe_rate": safe,
                "structural": task == "react-use-orders", "added_lines_mean": mean}
    rows = [row("safe-path", "baseline", 60.0), row("safe-path", "block", 30.0), row("safe-path", "skill", 15.0),
            row("cache", "baseline", 10.0), row("cache", "block", 12.0), row("cache", "skill", 8.0),
            row("sql-user", "baseline", 8.0), row("sql-user", "block", 8.0, correct=0.667, safe=0.667),
            row("sql-user", "skill", 4.0),
            row("react-use-orders", "baseline", 20.0), row("react-use-orders", "skill", 10.0, safe=0.0)]
    deltas = arm_deltas(rows)
    by = {(d["task"], d["arm"]): d for d in deltas}
    st.case("report", "deltas: Δ% per (task, arm) vs the baseline row; baseline rows yield none",
            by[("safe-path", "block")]["delta_pct"] == -50.0 and by[("safe-path", "skill")]["delta_pct"] == -75.0
            and by[("cache", "block")]["delta_pct"] == 20.0 and by[("sql-user", "skill")]["delta_pct"] == -50.0
            and not any(d["arm"] == "baseline" for d in deltas) and len(deltas) == 7, str(sorted(by)))
    groups = delta_groups(deltas)
    st.case("report", "groups: over-build mean over safe-path+cache(+react) per arm, worst task, correct below baseline, boundary safe < 1",
            groups["block"]["overbuild_mean_delta_pct"] == -15.0 and groups["block"]["overbuild_tasks"] == 2
            and groups["block"]["worst_task"] == "cache" and groups["block"]["worst_delta_pct"] == 20.0
            and groups["block"]["correct_below_baseline"] == ["sql-user"] and groups["block"]["boundary_safe_below_1"] == ["sql-user"]
            and groups["skill"]["overbuild_mean_delta_pct"] == round((-75.0 - 20.0 - 50.0) / 3, 1)
            and groups["skill"]["correct_below_baseline"] == [] and groups["skill"]["boundary_safe_below_1"] == [],
            json.dumps(groups))
    st.case("report", "the structural task never lands in boundary_safe_below_1",
            "react-use-orders" not in groups["skill"]["boundary_safe_below_1"])
    st.case("report", "no baseline arm -> no deltas", arm_deltas([row("cache", "skill", 8.0)]) == [])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_deltas(deltas, groups)
        print_deltas([], {})
    out = buf.getvalue()
    st.case("report", "print_deltas prints every treatment row and the group line; says so without a baseline",
            "safe-path" in out and "block:" in out and "skill:" in out and "-50.0" in out and "no baseline arm" in out)


def cmd_selftest(args: argparse.Namespace) -> int:
    global SELFTEST_PASSED
    started = time.time()
    if args.scorer_venv:
        os.environ["LEAN_SCORER_VENV"] = str(Path(args.scorer_venv).expanduser())
    st = Selftest()
    tasks = load_tasks()
    st.case("tasks", "nine tasks wired (6 upstream + 3 catalog)",
            len(tasks) == 9 and all(t in tasks for t in TASK_IDS), ", ".join(tasks))
    selftest_loc(st)
    selftest_scorers(st, tasks)
    selftest_detectors(st)
    selftest_arms(st)
    selftest_isolation(st, tasks)
    selftest_export(st)
    selftest_kill(st)
    selftest_refusals(st)
    selftest_metrics(st, tasks)
    selftest_rescore(st, tasks)
    selftest_relabel(st)
    selftest_report(st)
    ok = st.summary()
    elapsed = time.time() - started
    print(f"selftest wall time: {elapsed:.1f}s (target < 15s){'' if elapsed < 15 else '  SLOW'}")
    SELFTEST_PASSED = ok
    return 0 if ok else 1


# ── main ──────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--prepare-arms", action="store_true")
    ap.add_argument("--probe-isolation", action="store_true")
    ap.add_argument("--matrix", action="store_true")
    ap.add_argument("--classify", metavar="RUNS_STAMP_DIR")
    ap.add_argument("--rescore", metavar="RUNS_STAMP_DIR")
    ap.add_argument("--report", nargs="+", metavar="RUNS_STAMP_DIR")
    ap.add_argument("--relabel-arm", nargs=3, metavar=("RUNS_STAMP_DIR", "FROM", "TO"),
                    help="offline: rename arm FROM to TO in a FINISHED stamp (cell dirs, results.json, "
                         "summary.json, classify.json) and record --reason in results.json `relabels`")
    ap.add_argument("--reason", help="--relabel-arm: why the arm is relabelled (recorded in the stamp)")
    ap.add_argument("--export", metavar="OUT_JSON")
    ap.add_argument("--arms-root")
    ap.add_argument("--runs-root")
    ap.add_argument("--rules-ref", default="HEAD")
    ap.add_argument("--skill", default=DEFAULT_SKILL)
    ap.add_argument("--ponytail-dir")
    ap.add_argument("--claude-block", metavar="FILE",
                    help="--prepare-arms, settings-sources only: append this file (the always-on Lean Code "
                         "block) to the skill arm's CLAUDE.md snippet after the sentinel; the baseline never sees it")
    ap.add_argument("--isolation", default=DEFAULT_ISOLATION, choices=(*ISOLATION_MODES, "auto"),
                    help="arm layout at --prepare-arms and mode at --probe-isolation (default "
                         f"{DEFAULT_ISOLATION}; auto = try config-dir then home on legacy arms)")
    ap.add_argument("--model")
    ap.add_argument("--arms", default="baseline")
    ap.add_argument("--tasks", default="all")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--budget-usd", type=float)
    ap.add_argument("--scorer-venv", default=os.environ.get("LEAN_SCORER_VENV"))
    args = ap.parse_args(argv)

    rc = 0
    if args.selftest:
        rc = cmd_selftest(args)
        if rc:
            return rc
    if args.prepare_arms:
        if not args.arms_root:
            ap.error("--prepare-arms needs --arms-root")
        return cmd_prepare_arms(args)
    if args.probe_isolation:
        if not (args.arms_root and args.model):
            ap.error("--probe-isolation needs --arms-root and --model")
        return cmd_probe(args)
    if args.matrix:
        for need in ("arms_root", "runs_root", "model", "budget_usd"):
            if getattr(args, need) is None:
                ap.error(f"--matrix needs --{need.replace('_', '-')}")
        return cmd_matrix(args)
    if args.classify:
        return cmd_classify(args)
    if args.rescore:
        return cmd_rescore(args)
    if args.report:
        return cmd_report(args)
    if args.relabel_arm:
        return cmd_relabel(args)
    if not args.selftest:
        ap.print_help()
        return 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
