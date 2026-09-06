#!/usr/bin/env python3
"""research/tdd — harness that measures what a test-order doctrine does to what a real headless
Claude Code session writes, on the maintainer's own model and CLI version.

WHAT IT MEASURES, per cell (one task x one arm x one repetition):

  order             the first Write/Edit whose path is a test path came BEFORE the first one in a
                    production path. Read from the session transcript (--output-format stream-json).
  order_source      "transcript" or "mtime". A cell scored from mtime is a FALLBACK and is never
                    published as a measurement of order (see openspec skills-catalog, the
                    order-of-production requirement).
  red               the test files the agent wrote, applied ALONE on the pristine seed, FAIL.
                    A suite that passes without the implementation tests nothing.
  green             the HIDDEN suite -- which the agent never sees -- passes against the final code.
  test_added_lines  added lines in test paths, from the imported git_diff_stats. Guard against a
                    doctrine that buys order by inflating the suite.

WHAT IT DOES NOT MEASURE. Bash is disallowed in every cell, inherited from the isolation apparatus
of research/lean-code (its cell_command passes --disallowedTools Bash, and the settings-sources
layout runs under --permission-mode acceptEdits). The agent therefore never runs a test and never
sees red turn green. What is measured is the ORDER IN WHICH ARTIFACTS WERE WRITTEN and the QUALITY
OF WHAT REMAINED, not the feedback loop. The bias is identical in both arms, so the comparison
holds; the absolute value of `green` is a floor, not the model's capability.

REUSE. The generic arm, isolation, process and diff layer is IMPORTED from research/lean-code/run.py
rather than copied: that module imports clean (module level is docstring, imports, defs/classes and
pure constants; main() is guarded). research/tdd/PIN records the sha the symbols were read at, and
--selftest carries a contract test over every imported symbol. The contract test gates --matrix, so
an edit over there that breaks the contract stops paid cells here.

ARMS. `baseline` and `block`. The arm id `block` is the one research/lean-code uses for an always-on
doctrine block appended to the cell's CLAUDE.md with no skill installed, and ARM_LAYOUT over there
is keyed by that id -- so the treatment arm carries that name and the imported preparation and
preflight apply unchanged. The `skill` arm (the published skill loaded as a project skill) belongs
to the item that writes skills/tdd (#183) and does not run here: skills/tdd does not exist in this
checkout, so --prepare-arms produces baseline and block only.

USAGE
  python3 -m venv <dir> && <dir>/bin/pip install -r research/tdd/scorer-venv.txt
  run.py --selftest --scorer-venv <dir>
  run.py --prepare-arms --arms-root <outside-repo> --rules-ref <sha> \
         --claude-block research/tdd/arms-block.md
  run.py --probe-isolation --arms-root <outside-repo> --model claude-haiku-4-5-20251001   # PAID
  run.py --selftest --matrix --arms baseline,block --tasks all --model <id> --runs 3 \
         --arms-root <...> --runs-root <...> --budget-usd 20 --scorer-venv <dir>          # PAID
  run.py --report <stamp> [<stamp> ...] --export research/tdd/results/<stamp>-export.json

KNOWN LIMITS
  1. Bash disallowed in the cell (above). The red-green loop is not exercised by the agent.
  2. `order` depends on the transcript exposing tool_use events with a file path. Where it does
     not, the harness falls back to file mtimes and MARKS the cell; fallback cells are reported
     separately and never aggregated into a published order figure.
  3. The hidden suite scores behaviour named in the prompt, never internal structure. An
     implementation that is correct but organised differently still passes.
  4. Six tasks, all Python/pytest. Nothing here says anything about other stacks.
  5. The imported layer is pinned by sha in PIN, not vendored. A lean-code edit that keeps the
     contract but changes behaviour would not be caught by the contract test.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
TASKS_DIR = HERE / "tasks"
LEAN_RUN = REPO_ROOT / "research" / "lean-code" / "run.py"

TASK_IDS = ("parse-duration", "money-round", "date-range", "chunk-list", "slug-truncate",
            "fix-percent-bug")
SKILL = "tdd"
ARMS = ("baseline", "block")
CELL_TIMEOUT_S = 300
CELL_BUDGET_USD = 1.00
PYTEST_TIMEOUT_S = 120

# Identical for every arm. Deliberately NOT research/lean-code's NO_RUN: that text says "include
# tests if you normally would" and "Only the code you write is measured, not its execution", and
# the second sentence tells a model that tests do not count -- a treatment variable in an
# experiment about test order. This text forbids execution (the reason the original existed, still
# valid with Bash disallowed) and says nothing about whether to write tests.
NO_RUN_TDD = ("Do not run a dev server, install dependencies, run a database, or open a browser: "
              "write files and stop. Backlog rite explicitly waived for this benchmark task: edit "
              "the files directly, without an issue, a branch or an OpenSpec change.")

WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit", "str_replace_editor", "create_file")
HARNESS_SCORE_DIRS = ("_hidden", "_agent_tests")

_lean = None


def lean():
    """research/lean-code/run.py as a module. Imported, never copied: see the module docstring."""
    global _lean
    if _lean is None:
        if not LEAN_RUN.is_file():
            sys.exit(f"{LEAN_RUN} not found: research/tdd imports its generic arm and cell layer")
        import importlib.util
        name = "lean_code_run"
        spec = importlib.util.spec_from_file_location(name, LEAN_RUN)
        mod = importlib.util.module_from_spec(spec)
        # Registered BEFORE exec_module on purpose: that module decorates a class with
        # @dataclass, and dataclasses resolves cls.__module__ through sys.modules. Executing it
        # unregistered raises AttributeError: 'NoneType' object has no attribute '__dict__'
        # (measured 2026-09-06 on Python 3.14.5). Nothing else about the import has side effects.
        sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)
        except BaseException:
            sys.modules.pop(name, None)
            raise
        _lean = mod
    return _lean


IMPORTED_SYMBOLS = ("arm_layout", "is_test_path", "git_diff_stats", "block_sha256", "snippet_block",
                    "read_settings", "arm_settings", "prepare_arm_settings_sources", "arm_preflight",
                    "settings_sources_preflight", "cell_env", "run_process", "probe_gate",
                    "load_arms_json", "outside_repo", "now_stamp", "claude_version", "git",
                    "workspace_files", "workspace_dirs", "strip_export", "read_claude_json",
                    "cmd_prepare_arms", "cmd_probe", "_copy_tree", "parse_stream")


def log(msg: str) -> None:
    print(msg, flush=True)


# ── tasks ─────────────────────────────────────────────────────────────────
class Task:
    def __init__(self, mod):
        self.id = mod.ID
        self.kind = mod.KIND
        self.entry = mod.ENTRY
        self.prompt = mod.PROMPT
        self.seed_dir = Path(mod.SEED_DIR)
        self.good_dir = Path(mod.GOOD_DIR)
        self.bad_dir = Path(mod.BAD_DIR)
        self.hidden_dir = Path(mod.HIDDEN_DIR)


def load_tasks() -> dict[str, Task]:
    import importlib.util
    out: dict[str, Task] = {}
    for tid in TASK_IDS:
        path = TASKS_DIR / tid / "task.py"
        if not path.is_file():
            sys.exit(f"task {tid}: {path} missing")
        spec = importlib.util.spec_from_file_location(f"tdd_task_{tid.replace('-', '_')}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if mod.ID != tid:
            sys.exit(f"task {tid}: task.py declares ID {mod.ID!r}")
        out[tid] = Task(mod)
    return out


def seed_workspace(task: Task, repo: Path, extra_files=None, extra_dirs=None) -> None:
    """The cell's workspace: the task seed, plus whatever the arm contributes, committed so the
    diff has a base and so Claude Code sees a git root (project skills are only discovered under
    one -- measured by research/lean-code, probe_workspace)."""
    repo.mkdir(parents=True, exist_ok=True)
    lean()._copy_tree(task.seed_dir, repo)
    for name, content in (extra_files or {}).items():
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    for rel, src in (extra_dirs or {}).items():
        lean()._copy_tree(src, repo / rel)
    g = lean().git
    g(repo, "init", "-q")
    g(repo, "add", "-f", "-A")
    g(repo, "-c", "user.email=bench@example.invalid", "-c", "user.name=bench",
      "commit", "-q", "-m", "seed", "--no-verify")


# ── pytest, always in the pinned venv ─────────────────────────────────────
def venv_python(scorer_venv: str | None) -> str | None:
    root = scorer_venv or os.environ.get("TDD_SCORER_VENV")
    if not root:
        return None
    exe = Path(root).expanduser() / "bin" / "python"
    return str(exe) if exe.is_file() else None


def run_pytest(python: str, workdir: Path, target: str) -> dict:
    """pytest under the pinned venv, in a harness-owned workspace with a harness-owned ini, so
    nothing the agent wrote to pytest.ini or conftest.py can influence a score."""
    cmd = [python, "-m", "pytest", target, "-q", "-p", "no:cacheprovider", "--rootdir", str(workdir)]
    try:
        proc = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True,
                              timeout=PYTEST_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"passed": False, "returncode": None, "timeout": True, "tail": "pytest timed out"}
    tail = (proc.stdout or "").strip().splitlines()
    return {"passed": proc.returncode == 0, "returncode": proc.returncode, "timeout": False,
            "tail": tail[-1] if tail else (proc.stderr or "").strip()[-200:]}


def scoring_workspace(src_dir: Path, tests_src: Path, tests_rel: str) -> Path:
    """A throwaway workspace: the src/ under test, a harness-owned pytest.ini, and the tests to
    run. Nothing else the cell produced comes along."""
    work = Path(tempfile.mkdtemp(prefix="tdd-score-"))
    if src_dir.is_dir():
        lean()._copy_tree(src_dir, work / "src")
    else:
        (work / "src").mkdir(parents=True)
    (work / "pytest.ini").write_text("[pytest]\npythonpath = src .\n", encoding="utf-8")
    lean()._copy_tree(tests_src, work / tests_rel)
    return work


def agent_test_files(repo: Path) -> dict[str, str]:
    """Test files the cell added or changed, relative path -> content. The seed's own tests are
    excluded unless the cell changed them; a harness scoring directory never counts."""
    is_test = lean().is_test_path
    g = lean().git
    g(repo, "add", "-A")
    names = g(repo, "diff", "--cached", "--name-only", "HEAD").stdout.splitlines()
    out: dict[str, str] = {}
    for rel in names:
        rel = rel.strip()
        if not rel or not is_test(rel) or not rel.endswith(".py"):
            continue
        if any(part in HARNESS_SCORE_DIRS for part in Path(rel).parts):
            continue
        p = repo / rel
        if p.is_file():
            out[rel] = p.read_text(encoding="utf-8", errors="ignore")
    return out


def measure_red(task: Task, repo: Path, python: str | None) -> dict:
    """The cell's own tests, applied ALONE on the pristine seed. They must FAIL: a suite that
    passes with no implementation is a suite of nothing."""
    tests = agent_test_files(repo)
    if not tests:
        return {"red": False, "reason": "the cell wrote no test file", "test_files": 0}
    if not python:
        return {"red": None, "reason": "scorer venv not found (--scorer-venv / TDD_SCORER_VENV)",
                "test_files": len(tests)}
    work = scoring_workspace(task.seed_dir / "src", task.hidden_dir, "_unused")
    shutil.rmtree(work / "_unused", ignore_errors=True)
    agent_dir = work / "_agent_tests"
    agent_dir.mkdir(parents=True)
    for rel, content in tests.items():
        p = agent_dir / Path(rel).name
        n = 1
        while p.exists():
            p = agent_dir / f"{Path(rel).stem}_{n}.py"
            n += 1
        p.write_text(content, encoding="utf-8")
    res = run_pytest(python, work, "_agent_tests")
    shutil.rmtree(work, ignore_errors=True)
    return {"red": (res["passed"] is False) and res["returncode"] not in (5,), "reason": res["tail"],
            "test_files": len(tests), "pytest_returncode": res["returncode"]}


def measure_green(task: Task, repo: Path, python: str | None) -> dict:
    """The hidden suite -- which the cell never saw -- against the final src/."""
    if not python:
        return {"green": None, "reason": "scorer venv not found (--scorer-venv / TDD_SCORER_VENV)"}
    work = scoring_workspace(repo / "src", task.hidden_dir, "_hidden")
    res = run_pytest(python, work, "_hidden")
    shutil.rmtree(work, ignore_errors=True)
    return {"green": bool(res["passed"]), "reason": res["tail"]}


# ── order, from the transcript ────────────────────────────────────────────
def stream_writes(path: Path) -> list[str]:
    """File paths written by the cell, in the order the transcript shows them. Reads
    --output-format stream-json: assistant messages carry content blocks, and a tool_use block for
    a write tool carries the path in its input."""
    writes: list[str] = []
    if not path.exists():
        return writes
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        for block in _content_blocks(ev):
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if str(block.get("name")) not in WRITE_TOOLS:
                continue
            inp = block.get("input") or {}
            target = inp.get("file_path") or inp.get("path") or inp.get("notebook_path")
            if target:
                writes.append(str(target))
    return writes


def _content_blocks(ev) -> list:
    if not isinstance(ev, dict):
        return []
    msg = ev.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("content"), list):
        return msg["content"]
    if isinstance(ev.get("content"), list):
        return ev["content"]
    return []


def mtime_writes(repo: Path) -> list[str]:
    """Fallback ordering: paths the cell changed, by modification time. Coarser than the
    transcript -- a file rewritten late moves to the end -- so a cell scored this way is marked."""
    g = lean().git
    g(repo, "add", "-A")
    names = [n.strip() for n in g(repo, "diff", "--cached", "--name-only", "HEAD").stdout.splitlines()
             if n.strip()]
    stamped = []
    for rel in names:
        p = repo / rel
        try:
            stamped.append((p.stat().st_mtime, rel))
        except FileNotFoundError:
            continue
    return [rel for _, rel in sorted(stamped)]


def order_from(writes: list[str], repo: Path, source: str) -> dict:
    """order = the first write in a test path precedes the first write in a production path."""
    is_test = lean().is_test_path
    first_test = first_prod = None
    for i, raw in enumerate(writes):
        rel = _relative(raw, repo)
        if any(part in HARNESS_SCORE_DIRS for part in Path(rel).parts):
            continue
        if not rel.endswith(".py"):
            continue
        if is_test(rel):
            if first_test is None:
                first_test = (i, rel)
        elif first_prod is None:
            first_prod = (i, rel)
    order = bool(first_test and first_prod and first_test[0] < first_prod[0])
    return {"order": order, "order_source": source,
            "first_test_write": first_test[1] if first_test else None,
            "first_production_write": first_prod[1] if first_prod else None,
            "writes_seen": len(writes)}


def _relative(raw: str, repo: Path) -> str:
    try:
        return str(Path(raw).resolve().relative_to(repo.resolve()))
    except (ValueError, OSError):
        return str(raw).replace("\\", "/")


def measure_order(cell_dir: Path, repo: Path) -> dict:
    writes = stream_writes(cell_dir / "_claude.jsonl")
    if writes:
        return order_from(writes, repo, "transcript")
    return order_from(mtime_writes(repo), repo, "mtime")


# ── cells ─────────────────────────────────────────────────────────────────
def cell_command(prompt: str, model: str, budget_usd: float, isolation: str) -> list[str]:
    """As research/lean-code's, with one difference that matters: --output-format stream-json, so
    the write order is readable. Bash stays disallowed (KNOWN LIMIT 1)."""
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude CLI not found on PATH")
    cmd = [exe, "-p", prompt, "--model", model, "--output-format", "stream-json", "--verbose"]
    if isolation == "settings-sources":
        cmd += ["--setting-sources", "project,local", "--permission-mode", "acceptEdits"]
    else:
        cmd += ["--permission-mode", "bypassPermissions"]
    cmd += ["--disallowedTools", "Bash", "--strict-mcp-config", "--no-session-persistence",
            "--max-budget-usd", f"{budget_usd:.2f}", "--append-system-prompt", NO_RUN_TDD]
    return cmd


def result_meta(path: Path) -> tuple[dict, str]:
    """Cost, turns and the result text from a stream-json transcript's final `result` event."""
    parsed = lean().parse_stream(path) if path.exists() else {}
    meta = {"total_cost_usd": parsed.get("cost"), "result_keys": parsed.get("result_keys") or []}
    for line in (path.read_text(encoding="utf-8", errors="ignore").splitlines() if path.exists() else []):
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(ev, dict) and ev.get("type") == "result":
            for k in ("num_turns", "duration_ms", "is_error", "subtype"):
                if k in ev:
                    meta[k] = ev[k]
            usage = ev.get("usage") or {}
            for k in ("input_tokens", "output_tokens"):
                if k in usage:
                    meta[k] = usage[k]
    return meta, parsed.get("result_text") or ""


def score_cell(task: Task, cell_dir: Path, arm: str, model: str, run_index: int,
               python: str | None) -> dict:
    repo = cell_dir / "repo"
    meta, result_text = result_meta(cell_dir / "_claude.jsonl")
    stats = lean().git_diff_stats(repo)
    (cell_dir / "_diff.patch").write_text(stats.pop("patch", ""), encoding="utf-8")
    (cell_dir / "_result.txt").write_text(result_text, encoding="utf-8")
    for k in ("added_text", "added_by_file"):
        stats.pop(k, None)
    order = measure_order(cell_dir, repo)
    red = measure_red(task, repo, python)
    green = measure_green(task, repo, python)
    return {"task": task.id, "arm": arm, "model": model, "run": run_index, "kind": task.kind,
            **order, **red, **green, **stats, **meta}


def run_cell(task: Task, arm: str, arm_dir: Path, model: str, isolation: str, cell_dir: Path,
             run_index: int, python: str | None) -> dict:
    cell_dir.mkdir(parents=True, exist_ok=True)
    repo = cell_dir / "repo"
    ss = isolation == "settings-sources"
    seed_workspace(task, repo,
                   lean().workspace_files(arm_dir) if ss else None,
                   lean().workspace_dirs(arm_dir) if ss else None)
    cmd = cell_command(task.prompt, model, CELL_BUDGET_USD, isolation)
    (cell_dir / "_command.txt").write_text(" ".join(json.dumps(c) for c in cmd) + "\n",
                                           encoding="utf-8")
    proc = lean().run_process(cmd, repo, lean().cell_env(arm_dir, isolation),
                              cell_dir / "_claude.jsonl", cell_dir / "_claude.stderr.txt",
                              CELL_TIMEOUT_S)
    cell = score_cell(task, cell_dir, arm, model, run_index, python)
    cell.update({"returncode": proc["returncode"], "killed": proc["killed"], "wall_s": proc["wall_s"]})
    return cell


# ── aggregation and report ────────────────────────────────────────────────
def _rate(values: list) -> str:
    known = [v for v in values if v is not None]
    return f"{sum(1 for v in known if v)}/{len(known)}" if known else "0/0"


def _ratio(values: list) -> float | None:
    known = [v for v in values if v is not None]
    return round(sum(1 for v in known if v) / len(known), 4) if known else None


def aggregate(results: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for cell in results:
        if "error" in cell:
            continue
        groups.setdefault((cell["task"], cell["arm"]), []).append(cell)
    rows = []
    for (task, arm), cells in sorted(groups.items()):
        tests = [c.get("test_added_lines") or 0 for c in cells]
        costs = [c.get("total_cost_usd") for c in cells if c.get("total_cost_usd") is not None]
        rows.append({
            "task": task, "arm": arm, "n": len(cells), "kind": cells[0].get("kind"),
            "order": _rate([c.get("order") for c in cells]),
            "order_ratio": _ratio([c.get("order") for c in cells]),
            "order_fallback_cells": sum(1 for c in cells if c.get("order_source") != "transcript"),
            "red": _rate([c.get("red") for c in cells]),
            "red_ratio": _ratio([c.get("red") for c in cells]),
            "green": _rate([c.get("green") for c in cells]),
            "green_ratio": _ratio([c.get("green") for c in cells]),
            "wrote_tests": _rate([bool(c.get("test_files")) for c in cells]),
            "test_added_lines_mean": round(sum(tests) / len(tests), 2),
            "test_added_lines_min": min(tests), "test_added_lines_max": max(tests),
            "cost_mean_usd": round(sum(costs) / len(costs), 4) if costs else None,
        })
    return rows


def print_table(rows: list[dict]) -> None:
    for task in sorted({r["task"] for r in rows}):
        kind = next((r["kind"] for r in rows if r["task"] == task), "")
        print(f"\n=== {task} ({kind}) ===")
        print(f"{'arm':10} {'n':>2}  {'order':>7} {'red':>7} {'green':>7} {'wrote':>7} "
              f"{'testLOC mean':>13} {'min-max':>9} {'$/cell':>8}")
        for r in [x for x in rows if x["task"] == task]:
            fb = f" (fallback {r['order_fallback_cells']})" if r["order_fallback_cells"] else ""
            cost = f"{r['cost_mean_usd']:.4f}" if r["cost_mean_usd"] is not None else "-"
            print(f"{r['arm']:10} {r['n']:>2}  {r['order']:>7} {r['red']:>7} {r['green']:>7} "
                  f"{r['wrote_tests']:>7} {r['test_added_lines_mean']:>13} "
                  f"{str(r['test_added_lines_min']) + '-' + str(r['test_added_lines_max']):>9} "
                  f"{cost:>8}{fb}")


def arm_deltas(rows: list[dict]) -> list[dict]:
    base = {r["task"]: r for r in rows if r["arm"] == "baseline"}
    out = []
    for r in rows:
        if r["arm"] == "baseline" or r["task"] not in base:
            continue
        b = base[r["task"]]
        entry = {"task": r["task"], "arm": r["arm"], "kind": r["kind"]}
        for metric in ("order_ratio", "red_ratio", "green_ratio"):
            entry[metric] = {"baseline": b[metric], "arm": r[metric]}
        bm, am = b["test_added_lines_mean"], r["test_added_lines_mean"]
        entry["test_added_lines"] = {"baseline": bm, "arm": am,
                                     "factor": round(am / bm, 3) if bm else None}
        out.append(entry)
    return out


def print_deltas(deltas: list[dict]) -> None:
    if not deltas:
        print("\nno treatment arm to compare against baseline")
        return
    print(f"\n{'task':18} {'arm':8} {'order b->a':>16} {'red b->a':>16} {'green b->a':>16} "
          f"{'testLOC x':>10}")
    for d in deltas:
        def pair(k):
            v = d[k]
            f = lambda x: "-" if x is None else f"{x:.2f}"  # noqa: E731
            return f"{f(v['baseline'])} -> {f(v['arm'])}"
        factor = d["test_added_lines"]["factor"]
        print(f"{d['task']:18} {d['arm']:8} {pair('order_ratio'):>16} {pair('red_ratio'):>16} "
              f"{pair('green_ratio'):>16} {('-' if factor is None else f'{factor:.2f}'):>10}")


def load_results(stamp_dir: Path) -> dict:
    p = stamp_dir / "results.json"
    if not p.exists():
        sys.exit(f"{p} missing")
    return json.loads(p.read_text(encoding="utf-8"))


def check_same_conditions(payloads: list[dict]) -> None:
    for key in ("claude_version", "model"):
        seen = {p.get(key) for p in payloads}
        if len(seen) > 1:
            sys.exit(f"refusing to aggregate stamps with different {key}: {sorted(map(str, seen))}")


def cmd_report(args: argparse.Namespace) -> int:
    payloads = [load_results(Path(s).expanduser()) for s in args.report]
    check_same_conditions(payloads)
    results = [c for p in payloads for c in p.get("results", [])]
    if not results:
        sys.exit("no cells in those stamps")
    rows = aggregate(results)
    print_table(rows)
    deltas = arm_deltas(rows)
    print_deltas(deltas)
    fallback = sum(r["order_fallback_cells"] for r in rows)
    if fallback:
        print(f"\nWARNING {fallback} cell(s) scored order from mtime, not the transcript. "
              "Those are FALLBACK cells and must not be published as a measurement of order.")
    if args.export:
        payload = lean().strip_export({
            "stamps": [str(Path(s).expanduser()) for s in args.report],
            "claude_version": payloads[0].get("claude_version"), "model": payloads[0].get("model"),
            "arms": sorted({c["arm"] for c in results}),
            "isolation": sorted({p.get("isolation") for p in payloads if p.get("isolation")}),
            "rules_sha": sorted({p.get("rules_sha") for p in payloads if p.get("rules_sha")}),
            "cells": len(results),
            "spent_usd": round(sum(p.get("spent_usd") or 0 for p in payloads), 4),
            "order_fallback_cells": fallback,
            "summary": rows, "deltas": deltas,
            "cells_detail": [{k: v for k, v in c.items() if k != "changed_paths"} for c in results],
        })
        out = Path(args.export).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        log(f"wrote {out}")
    return 0


# ── matrix ────────────────────────────────────────────────────────────────
SELFTEST_PASSED = False


def cmd_matrix(args: argparse.Namespace) -> int:
    if not SELFTEST_PASSED:
        sys.exit("refusing --matrix: --selftest did not pass in this invocation "
                 "(run `run.py --selftest --matrix ...` so the instruments are proven first)")
    python = venv_python(args.scorer_venv)
    if not python:
        sys.exit("refusing --matrix: no scorer venv (--scorer-venv DIR or TDD_SCORER_VENV); "
                 "red and green would be unscorable")
    arms_root = Path(args.arms_root).expanduser()
    runs_root = Path(args.runs_root).expanduser()
    for path, flag in ((arms_root, "--arms-root"), (runs_root, "--runs-root")):
        if not lean().outside_repo(path):
            sys.exit(f"refusing: {flag} {path} resolves inside the repository")
    meta = lean().load_arms_json(arms_root)
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = [a for a in arms if a not in meta.get("arms", [])]
    if unknown:
        sys.exit(f"arms {unknown} were not prepared (prepared: {meta.get('arms')})")
    refusal = lean().probe_gate(meta, arms)
    if refusal:
        sys.exit("refusing --matrix: " + refusal)
    isolation = (meta.get("probe") or {}).get("isolation") or meta.get("isolation", "config-dir")
    for arm in arms:
        problems = lean().arm_preflight(arms_root / arm, arm, meta.get("skill", SKILL))
        if problems:
            sys.exit(f"arm {arm} failed preflight: " + "; ".join(problems))
    version = lean().claude_version()
    if meta.get("claude_version") and meta["claude_version"] != version:
        sys.exit(f"arms were prepared under claude {meta['claude_version']}, now {version}: "
                 "re-run --prepare-arms and the probe")
    tasks = load_tasks()
    task_ids = list(TASK_IDS) if args.tasks == "all" else [t.strip() for t in args.tasks.split(",")]
    unknown = [t for t in task_ids if t not in tasks]
    if unknown:
        sys.exit(f"unknown tasks: {unknown}")
    stamp = lean().now_stamp()
    out_dir = runs_root / stamp
    out_dir.mkdir(parents=True)
    header = {"stamp": stamp, "claude_version": version, "model": args.model,
              "isolation": isolation, "rules_sha": meta.get("rules_sha"), "arms": arms,
              "tasks": task_ids, "runs": args.runs, "budget_usd": args.budget_usd,
              "no_run_system_prompt": NO_RUN_TDD,
              "started_at": _dt.datetime.now().isoformat(timespec="seconds")}
    log(f"matrix {stamp}: {len(task_ids)} tasks x {len(arms)} arms x {args.runs} runs = "
        f"{len(task_ids) * len(arms) * args.runs} cells, budget ${args.budget_usd}")
    results: list[dict] = []
    spent = 0.0
    stopped = None

    def flush():
        (out_dir / "results.json").write_text(
            json.dumps({**header, "spent_usd": round(spent, 4), "stopped": stopped,
                        "results": results}, indent=2) + "\n", encoding="utf-8")

    for tid in task_ids:
        for arm in arms:
            for r in range(args.runs):
                if stopped:
                    break
                cell_dir = out_dir / f"{tid}__{arm}__{r}"
                try:
                    cell = run_cell(tasks[tid], arm, arms_root / arm, args.model, isolation,
                                    cell_dir, r, python)
                except Exception as exc:  # noqa: BLE001
                    cell = {"task": tid, "arm": arm, "run": r, "error": repr(exc)}
                results.append(cell)
                spent += cell.get("total_cost_usd") or 0.0
                flush()
                log(f"  {tid:18} {arm:9} run {r}  order={cell.get('order')} "
                    f"({cell.get('order_source')})  red={cell.get('red')}  "
                    f"green={cell.get('green')}  testLOC={cell.get('test_added_lines')}  "
                    f"${(cell.get('total_cost_usd') or 0):.4f}")
                if spent > args.budget_usd:
                    stopped = f"budget ${args.budget_usd} exceeded at ${spent:.4f}"
                    log("STOP " + stopped)
    flush()
    rows = aggregate(results)
    (out_dir / "summary.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print_table(rows)
    print_deltas(arm_deltas(rows))
    log(f"\nspent ${spent:.4f}  ->  {out_dir}")
    return 0 if not stopped else 2


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
        for group, values in self.results.items():
            print(f"  {group:10} {sum(values)}/{len(values)}")
        print(f"selftest {passed}/{total}")
        return passed == total


def _tmp_repo(task: Task) -> Path:
    repo = Path(tempfile.mkdtemp(prefix="tdd-self-")) / "repo"
    seed_workspace(task, repo)
    return repo


def selftest_contract(st: Selftest) -> None:
    """Every symbol imported from research/lean-code/run.py exists and still behaves as this
    harness assumes. This is what makes importing safe instead of copying 2748 lines."""
    mod = lean()
    missing = [s for s in IMPORTED_SYMBOLS if not hasattr(mod, s)]
    st.case("contract", "every imported symbol exists", not missing, f"missing={missing}" if missing else "")
    if missing:
        return
    st.case("contract", "arm_layout('block') carries the always-on block",
            mod.arm_layout("block") == (True, False))
    st.case("contract", "arm_layout('baseline') carries neither", mod.arm_layout("baseline") == (False, False))
    st.case("contract", "an arm id outside ARM_LAYOUT would carry NO block "
                        "(why the treatment arm is named `block`)",
            mod.arm_layout("doctrine") == (False, False))
    st.case("contract", "is_test_path knows test files",
            all(mod.is_test_path(p) for p in ("tests/test_x.py", "test_x.py", "src/x_test.py"))
            and not mod.is_test_path("src/duration.py"))
    st.case("contract", "block_sha256 is newline-normalised",
            mod.block_sha256("a\nb") == mod.block_sha256("a\nb\n\n"))
    st.case("contract", "read_settings/arm_settings set skillOverrides off for a non-skill arm",
            mod.arm_settings({"model": "m"}, SKILL, False)["skillOverrides"][SKILL] == "off")
    task = load_tasks()[TASK_IDS[0]]
    repo = _tmp_repo(task)
    (repo / "src" / "duration.py").write_text("def parse_duration(t):\n    return 1\n", encoding="utf-8")
    (repo / "tests" / "test_new.py").write_text("def test_a():\n    assert 1\n", encoding="utf-8")
    stats = mod.git_diff_stats(repo)
    st.case("contract", "git_diff_stats splits test lines from production lines",
            stats.get("test_added_lines", 0) > 0 and stats.get("added_lines", 0) > 0,
            f"added={stats.get('added_lines')} test={stats.get('test_added_lines')}")
    shutil.rmtree(repo.parent, ignore_errors=True)


def selftest_tasks(st: Selftest) -> None:
    tasks = load_tasks()
    st.case("tasks", f"{len(TASK_IDS)} tasks wired", len(tasks) == len(TASK_IDS))
    for tid, task in tasks.items():
        dirs_ok = all(d.is_dir() for d in (task.seed_dir, task.good_dir, task.bad_dir, task.hidden_dir))
        st.case("tasks", f"{tid} carries seed/good/bad/hidden", dirs_ok)
        # The prompt must not itself ask for tests: that is the treatment, and it lives in the
        # block arm's CLAUDE.md, never in the task.
        leaks = [w for w in ("test", "tdd", "pytest", "assert") if w in task.prompt.lower()]
        st.case("tasks", f"{tid} prompt does not instruct testing", not leaks,
                f"leaked={leaks}" if leaks else "")


def selftest_scorers(st: Selftest, python: str | None) -> None:
    if not python:
        st.case("scorers", "scorer venv available", False,
                "pass --scorer-venv DIR (or TDD_SCORER_VENV); the green instrument cannot run")
        return
    for tid, task in load_tasks().items():
        for ref, expected in (("seed", False), ("good", True), ("bad", False)):
            repo = Path(tempfile.mkdtemp(prefix="tdd-ref-"))
            lean()._copy_tree(task.seed_dir, repo)
            if ref != "seed":
                lean()._copy_tree(getattr(task, f"{ref}_dir"), repo)
            got = measure_green(task, repo, python)
            st.case("scorers", f"{tid} {ref} green={expected}", got["green"] is expected,
                    got["reason"][:70])
            shutil.rmtree(repo, ignore_errors=True)


def selftest_red(st: Selftest, python: str | None) -> None:
    if not python:
        st.case("red", "scorer venv available", False, "the red instrument cannot run")
        return
    tasks = load_tasks()
    for tid in (TASK_IDS[0], TASK_IDS[3], TASK_IDS[5]):
        task = tasks[tid]
        real = next(p for p in task.hidden_dir.iterdir() if p.name.startswith("test_"))
        # a real test of the requested behaviour, applied on the pristine seed -> must be red
        repo = _tmp_repo(task)
        (repo / "tests" / "test_written_first.py").write_text(
            real.read_text(encoding="utf-8"), encoding="utf-8")
        got = measure_red(task, repo, python)
        st.case("red", f"{tid} a real test on the seed is red", got["red"] is True, got["reason"][:60])
        shutil.rmtree(repo.parent, ignore_errors=True)
        # INJECTED DEFECT: a vacuous test passes without any implementation -> must NOT be red
        repo = _tmp_repo(task)
        (repo / "tests" / "test_vacuous.py").write_text(
            "def test_nothing():\n    assert True\n", encoding="utf-8")
        got = measure_red(task, repo, python)
        st.case("red", f"{tid} a vacuous test is not red", got["red"] is False, got["reason"][:60])
        shutil.rmtree(repo.parent, ignore_errors=True)
        # no test file at all
        repo = _tmp_repo(task)
        (repo / "src" / Path(task.entry).name).write_text("x = 1\n", encoding="utf-8")
        got = measure_red(task, repo, python)
        st.case("red", f"{tid} no test file is not red",
                got["red"] is False and got["test_files"] == 0, got["reason"][:60])
        shutil.rmtree(repo.parent, ignore_errors=True)


def _stream(*blocks: tuple[str, str]) -> str:
    lines = []
    for tool, path in blocks:
        lines.append(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": tool, "input": {"file_path": path}}]}}))
    lines.append(json.dumps({"type": "result", "result": "done", "total_cost_usd": 0.01}))
    return "\n".join(lines) + "\n"


def selftest_order(st: Selftest) -> None:
    task = load_tasks()[TASK_IDS[0]]
    repo = _tmp_repo(task)
    cell = repo.parent

    def score(stream_text: str | None) -> dict:
        path = cell / "_claude.jsonl"
        if stream_text is None:
            path.unlink(missing_ok=True)
        else:
            path.write_text(stream_text, encoding="utf-8")
        return measure_order(cell, repo)

    got = score(_stream(("Write", str(repo / "tests/test_duration.py")),
                        ("Write", str(repo / "src/duration.py"))))
    st.case("order", "test written before production is order=True",
            got["order"] is True and got["order_source"] == "transcript")
    # INJECTED DEFECT: the same two writes in the other order must not score as order
    got = score(_stream(("Write", str(repo / "src/duration.py")),
                        ("Write", str(repo / "tests/test_duration.py"))))
    st.case("order", "production written first is order=False", got["order"] is False)
    got = score(_stream(("Write", str(repo / "src/duration.py"))))
    st.case("order", "production only is order=False",
            got["order"] is False and got["first_test_write"] is None)
    got = score(_stream(("Write", str(repo / "tests/test_duration.py"))))
    st.case("order", "test only is order=False (nothing to precede)", got["order"] is False)
    got = score(_stream(("Write", str(repo / "_hidden/test_x.py")),
                        ("Write", str(repo / "src/duration.py"))))
    st.case("order", "a harness scoring directory never counts as the first test write",
            got["order"] is False and got["first_test_write"] is None)
    got = score(_stream(("Edit", str(repo / "tests/test_duration.py")),
                        ("MultiEdit", str(repo / "src/duration.py"))))
    st.case("order", "Edit and MultiEdit count as writes", got["order"] is True)
    got = score(None)
    st.case("order", "no transcript falls back to mtime and says so", got["order_source"] == "mtime")
    (repo / "src" / "duration.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "tests" / "test_late.py").write_text("def test_a():\n    assert 1\n", encoding="utf-8")
    got = score(None)
    st.case("order", "the mtime fallback still produces a verdict",
            got["order"] in (True, False) and got["order_source"] == "mtime")
    shutil.rmtree(cell, ignore_errors=True)


def selftest_refusals(st: Selftest) -> None:
    st.case("refusals", "SELFTEST_PASSED is False before the selftest finishes", SELFTEST_PASSED is False)
    ok = False
    try:
        check_same_conditions([{"claude_version": "2.1.263", "model": "a"},
                               {"claude_version": "2.1.999", "model": "a"}])
    except SystemExit:
        ok = True
    st.case("refusals", "--report refuses stamps from different CLI versions", ok)
    ok = False
    try:
        check_same_conditions([{"claude_version": "2.1.263", "model": "a"},
                               {"claude_version": "2.1.263", "model": "b"}])
    except SystemExit:
        ok = True
    st.case("refusals", "--report refuses stamps from different models", ok)
    check_same_conditions([{"claude_version": "2.1.263", "model": "a"},
                           {"claude_version": "2.1.263", "model": "a"}])
    st.case("refusals", "--report accepts identical conditions", True)
    st.case("refusals", "an arms root inside the repository is refused",
            not lean().outside_repo(REPO_ROOT / "x") and lean().outside_repo(Path("/tmp/x")))
    st.case("refusals", "probe_gate refuses arms with no passed probe",
            lean().probe_gate({"arms": list(ARMS), "rules_sha": "abc"}, list(ARMS)) is not None)
    st.case("refusals", "probe_gate refuses a probe from another rules_sha",
            lean().probe_gate({"arms": list(ARMS), "rules_sha": "abc", "isolation": "settings-sources",
                               "probe": {"passed": True, "rules_sha": "zzz",
                                         "isolation": "settings-sources", "arms": list(ARMS)}},
                              list(ARMS)) is not None)
    st.case("refusals", "probe_gate passes a matching probe",
            lean().probe_gate({"arms": list(ARMS), "rules_sha": "abc", "isolation": "settings-sources",
                               "skill": SKILL,
                               "probe": {"passed": True, "rules_sha": "abc",
                                         "isolation": "settings-sources", "arms": list(ARMS)}},
                              list(ARMS)) is None)


def selftest_export(st: Selftest) -> None:
    payload = lean().strip_export({"session_id": "s", "result": "text", "keep": 3,
                                   "nested": {"uuid": "u", "n": 1}})
    st.case("export", "session id, result text and uuids are stripped",
            "session_id" not in payload and "result" not in payload
            and "uuid" not in payload.get("nested", {}))
    st.case("export", "numbers survive", payload.get("keep") == 3 and payload["nested"]["n"] == 1)


def selftest_aggregate(st: Selftest) -> None:
    cells = [
        {"task": "t", "arm": "baseline", "kind": "specified", "order": False, "order_source": "transcript",
         "red": False, "green": True, "test_added_lines": 4, "total_cost_usd": 0.1, "test_files": 1},
        {"task": "t", "arm": "block", "kind": "specified", "order": True, "order_source": "transcript",
         "red": True, "green": True, "test_added_lines": 8, "total_cost_usd": 0.1, "test_files": 1},
        {"task": "t", "arm": "block", "kind": "specified", "order": True, "order_source": "mtime",
         "red": True, "green": False, "test_added_lines": 12, "total_cost_usd": 0.1, "test_files": 1},
    ]
    rows = aggregate(cells)
    block = next(r for r in rows if r["arm"] == "block")
    st.case("aggregate", "rates are counted over known values",
            block["order"] == "2/2" and block["green"] == "1/2")
    st.case("aggregate", "fallback cells are counted separately", block["order_fallback_cells"] == 1)
    st.case("aggregate", "test line inflation is visible as a factor",
            arm_deltas(rows)[0]["test_added_lines"]["factor"] == 2.5)
    rows2 = aggregate([c for c in cells if c["arm"] == "block"])
    st.case("aggregate", "no baseline means no deltas, not a crash", arm_deltas(rows2) == [])


def cmd_selftest(args: argparse.Namespace) -> int:
    global SELFTEST_PASSED
    python = venv_python(args.scorer_venv)
    st = Selftest()
    selftest_contract(st)
    selftest_tasks(st)
    selftest_order(st)
    selftest_red(st, python)
    selftest_scorers(st, python)
    selftest_refusals(st)
    selftest_export(st)
    selftest_aggregate(st)
    ok = st.summary()
    SELFTEST_PASSED = ok
    return 0 if ok else 1


# ── main ──────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="research/tdd harness")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--prepare-arms", action="store_true")
    p.add_argument("--probe-isolation", action="store_true")
    p.add_argument("--matrix", action="store_true")
    p.add_argument("--report", nargs="+", metavar="STAMP_DIR")
    p.add_argument("--export", metavar="FILE")
    p.add_argument("--arms-root", default=None)
    p.add_argument("--runs-root", default=None)
    p.add_argument("--rules-ref", default="HEAD")
    p.add_argument("--claude-block", default=str(HERE / "arms-block.md"))
    p.add_argument("--arms", default=",".join(ARMS))
    p.add_argument("--tasks", default="all")
    p.add_argument("--model", default=None)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--budget-usd", type=float, default=20.0)
    p.add_argument("--scorer-venv", default=None)
    args = p.parse_args(argv)

    rc = 0
    if args.selftest:
        rc = cmd_selftest(args)
        if rc:
            return rc
    if args.prepare_arms:
        if not args.arms_root:
            sys.exit("--prepare-arms needs --arms-root DIR (outside the repository)")
        ns = argparse.Namespace(arms_root=args.arms_root, rules_ref=args.rules_ref,
                                isolation="settings-sources", skill=SKILL,
                                claude_block=args.claude_block, ponytail_dir=None)
        rc = lean().cmd_prepare_arms(ns) or rc
    if args.probe_isolation:
        if not (args.arms_root and args.model):
            sys.exit("--probe-isolation needs --arms-root DIR and --model ID")
        ns = argparse.Namespace(arms_root=args.arms_root, isolation="auto", model=args.model,
                                export=None)
        rc = lean().cmd_probe(ns) or rc
    if args.matrix:
        if not (args.arms_root and args.runs_root and args.model):
            sys.exit("--matrix needs --arms-root, --runs-root and --model")
        rc = cmd_matrix(args) or rc
    if args.report:
        rc = cmd_report(args) or rc
    if not any((args.selftest, args.prepare_arms, args.probe_isolation, args.matrix, args.report)):
        p.print_help()
        return 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
