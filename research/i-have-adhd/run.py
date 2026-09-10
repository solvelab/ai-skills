#!/usr/bin/env python3
"""research/i-have-adhd/run.py — does i-have-adhd beat the incumbent (caveman) on the maintainer's
own model, through the real installation path? Backing evidence for issue #246.

The protocol (conditions, injection modes, cell, metrics, the verdict table written before any
paid cell) is protocol.md. This file is the instrument; it invents no rule the protocol does not
state.

Two upstreams are loaded as modules, never copied:

  vendor/i-have-adhd/scripts/{run_evals,judge}.py   the candidate's own evaluation harness
                                                    (cases, rubric, blind paired judge, resumable
                                                    rows). Pinned in vendor/i-have-adhd/PIN.
  research/lean-code/run.py                         the catalog's process layer (tree-killed
                                                    subprocess, stream-json parsing, export
                                                    stripper). Pinned in PIN beside this file.

Subcommands, run in this order (protocol.md, *Sequence*):

  --selftest              offline: vendor hashes against both PINs, the upstream's own unit tests,
                          the import contract, the counters, the verdict table on synthetic scores,
                          the export stripper and the conditions preflight. Gate of --matrix.
  --prepare-conditions    one scratch CLAUDE_CONFIG_DIR per (mode, condition) OUTSIDE the
                          repository; the candidate's carries the always-on flag file; every one
                          links ~/.claude/.credentials.json (the CLI reads credentials from
                          CLAUDE_CONFIG_DIR; a copy goes stale when the token rotates).
  --refresh-credentials   re-link an existing root's config dirs to the live credentials file.
  --probe                 paid, small: three stream-json calls per condition with
                          --include-hook-events; passes a mode only by the table in protocol.md.
  --matrix                paid: the cells of one mode, resumable by (case_id, trial, condition,
                          runner), stopped by --budget-usd. Refuses without a green --selftest in
                          the same invocation and a passed probe for that mode.
  --judge                 paid: the upstream's blind judge over one run's responses.
  --report [--export]     offline: per-condition means, per-case table, counters, the verdict read
                          by the letter of protocol.md; export stripped of session identifiers,
                          response text and home paths.
  --teardown              deletes a conditions root (the credential links with it).

KNOWN LIMITS (also in protocol.md, *What this does not cover*):
  1. Every cell runs `--tools ""`: chat only, nothing agentic is measured.
  2. The judge is the generator's own model family.
  3. `forbidden_phrase_hits` is a literal substring counter; `Let me` matches ordinary prose.
  4. The comparator is measured at one caveman level (`full`, pinned by CAVEMAN_DEFAULT_MODE).
     Both of its hooks fire in a `--print` cell (SessionStart and the UserPromptSubmit tracker —
     measured by the probe of 2026-09-10); other levels are not measured.
  5. Whether `--plugin-dir` fires SessionStart under `--print` is what the probe measures, not a
     fact this file assumes; probed on Claude Code 2.1.267 only.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
VENDOR = HERE / "vendor" / "i-have-adhd"
VENDOR_SCRIPTS = VENDOR / "scripts"
VENDOR_PIN = VENDOR / "PIN"
CASES = VENDOR / "evals" / "cases.jsonl"
RUBRIC = VENDOR / "evals" / "rubric.md"
CANDIDATE_SKILL = VENDOR / "skills" / "i-have-adhd" / "SKILL.md"
CANDIDATE_PLUGIN_DIR = VENDOR
CAVEMAN_VENDOR = HERE / "vendor" / "caveman"
CAVEMAN_PIN = CAVEMAN_VENDOR / "PIN"
COMPARATOR_SKILL = CAVEMAN_VENDOR / "skills" / "caveman" / "SKILL.md"
LEAN_RUN = REPO_ROOT / "research" / "lean-code" / "run.py"
LOCAL_PIN = HERE / "PIN"

CONDITIONS = ("baseline", "comparator", "candidate")
TREATED = ("comparator", "candidate")
MODES = ("prompt", "plugin")
DEFAULT_MODEL = "claude-fable-5-1"
PROBE_MODEL = "claude-haiku-4-5-20251001"
PROBE_BUDGET_USD = 0.05
PROBE_CALLS = 3
PROBE_PROMPT = "Reply with the single word DONE."
CELL_TIMEOUT_S = 900          # raised from 300 on 2026-09-10: a candidate cell on `complex-plan` was killed three times at 300 s (see results.md)
CELL_ATTEMPTS = 3
MAX_BUDGET_PER_INVOCATION = 25.0        # the upstream harness's own ceiling, kept
JUDGE_CALL_BUDGET_USD = 1.0
CELL_BUDGET_USD = 4.0                   # per-call cap: one runaway cell must not eat the invocation
ADHD_FLAG = ".i-have-adhd-always"       # read by vendor/i-have-adhd/hooks/always-on.mjs
CAVEMAN_FLAG = ".caveman-active"        # written by the caveman SessionStart hook
CAVEMAN_LEVEL = "full"                  # the level the maintainer runs (~/.claude/.caveman-active)
AGENT_CASE = "agent-owned-edit"         # impassable with tools disabled, by the upstream's finding
PARTIAL_CASE = "partial-success"        # the upstream's own regression; REJECT trigger
CREDENTIALS_FILE = ".credentials.json"

# The phrases rule 10 of vendor/i-have-adhd/skills/i-have-adhd/SKILL.md forbids, literally.
FORBIDDEN_PHRASES = (
    "Great question", "Let me", "I'll", "Sure!", "Looking at your", "To answer your question",
    "I've now done", "Let me know if you need anything else", "Hope this helps",
    "Happy to clarify", "Feel free to ask",
)

# Tool-call markup written as plain text. With `--tools ""` the CLI has no tools, and a response
# that "calls" one anyway is text the judge reads as an unfinished task. Counted post hoc (not
# pre-registered — the upstream had seen 3 of 84 such responses, here they are far more), never
# judged; the shapes observed on 2026-09-10 are the XML-ish invoke/parameter block and a bare
# tool name followed by a JSON object.
TOOL_MARKUP = re.compile(
    r"<(?:antml:)?(?:function_calls|invoke|parameter)\b|^\s*(?:Bash|Read|Write|Edit|Glob|Grep|WebFetch)\s*\n\s*\{",
    re.M)

# Symbols this harness relies on; the selftest `contract` group checks each one (PIN records the
# blob they were read at).
LEAN_SYMBOLS = ("run_process", "parse_stream", "strip_export", "claude_version", "now_stamp",
                "outside_repo")
UPSTREAM_SYMBOLS = ("load_cases", "validate_cases", "read_jsonl", "completed_keys",
                    "_condition_prompt", "_parse_response", "_neutral_cwd", "_strip_frontmatter",
                    "summarize_scores", "WEIGHTS", "CONDITIONS")

SELFTEST_PASSED = False


def log(msg: str) -> None:
    print(msg, flush=True)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ── module loaders ────────────────────────────────────────────────────────
def load_module(name: str, path: Path):
    """Load `path` as module `name`, registered in sys.modules BEFORE execution: dataclass-decorated
    classes resolve cls.__module__ through sys.modules (measured in research/tdd, 2026-09-06), and
    vendor judge.py does `import run_evals`, which must find the vendored module, not a stray one."""
    if not path.is_file():
        sys.exit(f"{path} not found")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return mod


_lean = None
_upstream: Optional[tuple] = None


def lean():
    global _lean
    if _lean is None:
        _lean = load_module("lean_code_run", LEAN_RUN)
    return _lean


def upstream() -> tuple:
    """(run_evals, judge) of vendor/i-have-adhd, unmodified."""
    global _upstream
    if _upstream is None:
        run_evals = load_module("run_evals", VENDOR_SCRIPTS / "run_evals.py")
        judge = load_module("i_have_adhd_judge", VENDOR_SCRIPTS / "judge.py")
        _upstream = (run_evals, judge)
    return _upstream


# ── PINs ──────────────────────────────────────────────────────────────────
SHA_LINE = re.compile(r"^([0-9a-f]{64})\s+(\S+)$")


def pin_hashes(pin: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in pin.read_text(encoding="utf-8").splitlines():
        m = SHA_LINE.match(line.strip())
        if m:
            out[m.group(2)] = m.group(1)
    return out


def pin_field(pin: Path, key: str) -> str:
    for line in pin.read_text(encoding="utf-8").splitlines():
        if line.startswith(key + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def caveman_installed_dir() -> Path:
    raw = pin_field(CAVEMAN_PIN, "installed_path")
    return Path(os.path.expanduser(raw))


def check_pins() -> list[str]:
    """Every hashed file, vendored or installed, still hashes as its PIN says. Returns the drifts."""
    drifts: list[str] = []
    for rel, sha in pin_hashes(VENDOR_PIN).items():
        p = VENDOR / rel
        if not p.is_file():
            drifts.append(f"vendor/i-have-adhd/{rel}: missing")
        elif sha256_file(p) != sha:
            drifts.append(f"vendor/i-have-adhd/{rel}: sha256 differs from PIN")
    installed = caveman_installed_dir()
    for rel, sha in pin_hashes(CAVEMAN_PIN).items():
        p = CAVEMAN_VENDOR / rel
        if not p.is_file():
            p = installed / rel
            label = f"installed caveman {rel}"
        else:
            label = f"vendor/caveman/{rel}"
        if not p.is_file():
            drifts.append(f"{label}: missing")
        elif sha256_file(p) != sha:
            drifts.append(f"{label}: sha256 differs from PIN")
    return drifts


# ── counters ──────────────────────────────────────────────────────────────
def tool_markup(text: str) -> bool:
    return TOOL_MARKUP.search(text or "") is not None


def forbidden_phrase_hits(text: str) -> int:
    low = (text or "").lower()
    return sum(low.count(p.lower()) for p in FORBIDDEN_PHRASES)


# ── cell command and prompt ───────────────────────────────────────────────
def claude_exe() -> str:
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude CLI not found on PATH")
    return exe


def runner_command(model: str, plugin_dir: Optional[Path] = None) -> list[str]:
    """The upstream's `claude` runner (evals/runners.example.json), model pinned, plus the plugin
    directory in plugin mode. The budget flag and the prompt are appended per cell, in that
    order, exactly as the upstream's loop does."""
    cmd = [claude_exe(), "--disable-slash-commands", "--print", "--output-format", "json",
           "--no-session-persistence", "--setting-sources", "", "--model", model, "--tools", ""]
    if plugin_dir is not None:
        cmd += ["--plugin-dir", str(plugin_dir)]
    return cmd


def probe_command(model: str, plugin_dir: Optional[Path]) -> list[str]:
    cmd = [claude_exe(), "-p", PROBE_PROMPT, "--model", model, "--output-format", "stream-json",
           "--verbose", "--include-hook-events", "--tools", "", "--setting-sources", "",
           "--strict-mcp-config", "--no-session-persistence",
           "--max-budget-usd", f"{PROBE_BUDGET_USD:.2f}"]
    if plugin_dir is not None:
        cmd += ["--plugin-dir", str(plugin_dir)]
    return cmd


def skill_for(condition: str) -> Optional[Path]:
    return {"candidate": CANDIDATE_SKILL, "comparator": COMPARATOR_SKILL}.get(condition)


def plugin_dir_for(condition: str) -> Optional[Path]:
    if condition == "candidate":
        return CANDIDATE_PLUGIN_DIR
    if condition == "comparator":
        return caveman_installed_dir()
    return None


def condition_prompt(mode: str, condition: str, task: str) -> str:
    """prompt mode: the upstream's wrapper. plugin mode: the bare task, the rule enters by hook."""
    run_evals, _ = upstream()
    if mode == "plugin" or condition == "baseline":
        return task
    return run_evals._condition_prompt(task, condition, skill_for(condition))


def cell_env(config_dir: Path, mode: str, condition: str) -> dict[str, str]:
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)                     # nested-session guard the CLI sets for itself
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    if mode == "plugin" and condition == "comparator":
        env["CAVEMAN_DEFAULT_MODE"] = CAVEMAN_LEVEL
    else:
        env.pop("CAVEMAN_DEFAULT_MODE", None)
    return env


# ── conditions ────────────────────────────────────────────────────────────
def conditions_file(root: Path) -> Path:
    return root / "conditions.json"


def load_conditions(root: Path) -> dict:
    f = conditions_file(root)
    if not f.is_file():
        sys.exit(f"{f} not found: run --prepare-conditions first")
    return json.loads(f.read_text(encoding="utf-8"))


def save_conditions(root: Path, conf: dict) -> None:
    conditions_file(root).write_text(json.dumps(conf, indent=2) + "\n", encoding="utf-8")


def link_credentials(config_dir: Path, source: Optional[Path]) -> None:
    """A symlink to the live credentials file, not a copy. Measured on 2026-09-10: seven copies of
    ~/.claude/.credentials.json went stale together the moment the maintainer's own session
    refreshed the OAuth token (the refresh token rotates), and every cell then failed with
    `OAuth session expired and could not be refreshed`. Through the link every config dir reads
    and refreshes the one file the CLI would refresh anyway."""
    if source is None:
        return
    target = config_dir / CREDENTIALS_FILE
    if target.is_symlink() or target.exists():
        target.unlink()
    target.symlink_to(source.resolve())


def prepare_conditions(root: Path, credentials: Optional[Path]) -> dict:
    """Layout: <root>/<mode>/<condition>/config (CLAUDE_CONFIG_DIR) and <root>/judge/config.
    Refuses a root inside the repository. Returns the conditions record."""
    if not lean().outside_repo(root):
        raise SystemExit(f"refusing: --conditions-root {root} resolves inside the repository")
    root.mkdir(parents=True, exist_ok=True)
    installed = caveman_installed_dir()
    if not (installed / ".claude-plugin" / "plugin.json").is_file():
        raise SystemExit(f"installed caveman plugin not found at {installed} (vendor/caveman/PIN)")
    modes: dict[str, dict] = {}
    for mode in MODES:
        modes[mode] = {}
        for cond in CONDITIONS:
            cfg = root / mode / cond / "config"
            cfg.mkdir(parents=True, exist_ok=True)
            link_credentials(cfg, credentials)
            plugin_dir = plugin_dir_for(cond) if mode == "plugin" else None
            if mode == "plugin" and cond == "candidate":
                (cfg / ADHD_FLAG).write_text("", encoding="utf-8")
            modes[mode][cond] = {
                "config_dir": str(cfg),
                "plugin_dir": str(plugin_dir) if plugin_dir else None,
                "flag_file": ADHD_FLAG if (mode == "plugin" and cond == "candidate") else None,
                "env_extra": {"CAVEMAN_DEFAULT_MODE": CAVEMAN_LEVEL}
                if (mode == "plugin" and cond == "comparator") else {},
            }
    judge_cfg = root / "judge" / "config"
    judge_cfg.mkdir(parents=True, exist_ok=True)
    link_credentials(judge_cfg, credentials)
    conf = {
        "created": _dt.datetime.now().isoformat(timespec="seconds"),
        "claude_version": lean().claude_version(),
        "rubric_sha256": sha256_file(RUBRIC),
        "cases_sha256": sha256_file(CASES),
        "candidate_skill_sha256": sha256_file(CANDIDATE_SKILL),
        "comparator_skill_sha256": sha256_file(COMPARATOR_SKILL),
        "candidate_plugin_dir": str(CANDIDATE_PLUGIN_DIR),
        "comparator_plugin_dir": str(installed),
        "credentials_linked": str(credentials.resolve()) if credentials is not None else None,
        "judge_config_dir": str(judge_cfg),
        "modes": modes,
        "probe": {},
    }
    save_conditions(root, conf)
    return conf


def live_credentials() -> Optional[Path]:
    src = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))) / CREDENTIALS_FILE
    return src if src.is_file() else None


def cmd_prepare_conditions(args: argparse.Namespace) -> int:
    conf = prepare_conditions(args.conditions_root, live_credentials())
    log(f"conditions at {args.conditions_root}: {len(MODES)} modes x {len(CONDITIONS)} conditions, "
        f"claude {conf['claude_version']}, credentials_linked={conf['credentials_linked']}")
    return 0


def cmd_refresh_credentials(args: argparse.Namespace) -> int:
    """Re-link every config dir of an existing conditions root to the live credentials file,
    keeping the probe record. For a root prepared with copies (before 2026-09-10)."""
    conf = load_conditions(args.conditions_root)
    src = live_credentials()
    dirs = [Path(e["config_dir"]) for m in conf["modes"].values() for e in m.values()]
    dirs.append(Path(conf["judge_config_dir"]))
    for d in dirs:
        link_credentials(d, src)
    conf["credentials_linked"] = str(src.resolve()) if src else None
    conf.pop("credentials_copied", None)
    save_conditions(args.conditions_root, conf)
    log(f"re-linked {len(dirs)} config dirs to {src}")
    return 0


def cmd_teardown(args: argparse.Namespace) -> int:
    root = args.conditions_root
    if not lean().outside_repo(root) or not conditions_file(root).is_file():
        sys.exit(f"refusing to delete {root}: not a conditions root outside the repository")
    shutil.rmtree(root)
    log(f"deleted {root}")
    return 0


# ── probe ─────────────────────────────────────────────────────────────────
def hook_event_names(parsed: dict) -> list[str]:
    return [str(n) for n in parsed.get("hook_names", [])]


def probe_condition(root: Path, conf: dict, mode: str, cond: str, model: str, out_dir: Path) -> dict:
    entry = conf["modes"][mode][cond]
    cfg = Path(entry["config_dir"])
    plugin_dir = Path(entry["plugin_dir"]) if entry["plugin_dir"] else None
    flag = cfg / CAVEMAN_FLAG
    if flag.exists():
        flag.unlink()                     # the hook must write it in THIS probe to count
    calls = []
    for i in range(PROBE_CALLS):
        cmd = probe_command(model, plugin_dir)
        cell = out_dir / f"{mode}-{cond}-{i}"
        cell.mkdir(parents=True, exist_ok=True)
        (cell / "command.txt").write_text(json.dumps(cmd) + "\n", encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="ihadhd-probe-") as cwd:
            proc = lean().run_process(cmd, Path(cwd), cell_env(cfg, mode, cond),
                                      cell / "stdout.jsonl", cell / "stderr.txt", 120)
        parsed = lean().parse_stream(cell / "stdout.jsonl")
        names = hook_event_names(parsed)
        calls.append({
            "returncode": proc["returncode"], "wall_s": proc["wall_s"],
            "hook_event_names": names,
            "session_start_hook": any("sessionstart" in n.lower() for n in names),
            "hook_events": len(names),
            "result_present": bool(parsed.get("result_text")),
            "done": "DONE" in (parsed.get("result_text") or "").upper(),
            "cost": parsed.get("cost"),
        })
    caveman_flag_after = flag.exists()
    treated = cond in TREATED
    if mode == "plugin" and treated:
        ok = all(c["session_start_hook"] and c["result_present"] for c in calls)
        if cond == "comparator":
            ok = ok and caveman_flag_after
    else:
        ok = all(c["hook_events"] == 0 and c["result_present"] for c in calls)
        if cond == "baseline" and mode == "plugin":
            ok = ok and not caveman_flag_after
    return {"condition": cond, "mode": mode, "passed": ok, "calls": calls,
            "caveman_flag_after": caveman_flag_after,
            "cost": round(sum(float(c["cost"] or 0) for c in calls), 4)}


def cmd_probe(args: argparse.Namespace) -> int:
    conf = load_conditions(args.conditions_root)
    stamp = lean().now_stamp()
    out_dir = args.conditions_root / "probes" / stamp
    modes = [args.mode] if args.mode else list(MODES)
    report: dict[str, Any] = {"stamp": stamp, "model": args.probe_model,
                              "claude_version": lean().claude_version(), "modes": {}}
    total = 0.0
    for mode in modes:
        results = [probe_condition(args.conditions_root, conf, mode, c, args.probe_model, out_dir)
                   for c in CONDITIONS]
        passed = all(r["passed"] for r in results)
        spent = round(sum(r["cost"] for r in results), 4)
        total += spent
        report["modes"][mode] = {"passed": passed, "conditions": results, "cost": spent}
        conf.setdefault("probe", {})[mode] = {"passed": passed, "stamp": stamp,
                                              "model": args.probe_model, "cost": spent}
        for r in results:
            hooks = "/".join(str(c["hook_events"]) for c in r["calls"])
            ss = sum(c["session_start_hook"] for c in r["calls"])
            log(f"probe {mode:6s} {r['condition']:10s} {'PASS' if r['passed'] else 'FAIL'}  "
                f"session_start {ss}/{PROBE_CALLS}  hook_events {hooks}  "
                f"caveman_flag={r['caveman_flag_after']}  ${r['cost']:.4f}")
        log(f"probe {mode}: {'PASSED' if passed else 'FAILED'}  ${spent:.4f}")
    save_conditions(args.conditions_root, conf)
    (out_dir / "probe.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.probe_out:
        args.probe_out.parent.mkdir(parents=True, exist_ok=True)
        args.probe_out.write_text(json.dumps(lean().strip_export(report), indent=2) + "\n",
                                  encoding="utf-8")
        log(f"wrote {args.probe_out}")
    log(f"probe total ${total:.4f}")
    return 0 if all(m["passed"] for m in report["modes"].values()) else 1


# ── matrix ────────────────────────────────────────────────────────────────
def _failed_cost(stdout: str) -> float:
    try:
        return float(json.loads(stdout).get("total_cost_usd") or 0.0)
    except (ValueError, AttributeError):
        return 0.0


def _terminal_reason(stdout_path: Path) -> str:
    try:
        return str(json.loads(stdout_path.read_text(encoding="utf-8", errors="ignore")).get("terminal_reason") or "")
    except (ValueError, OSError, AttributeError):
        return ""

def run_meta_path(run_dir: Path) -> Path:
    return run_dir / "meta.json"


def cmd_matrix(args: argparse.Namespace) -> int:
    if not SELFTEST_PASSED:
        sys.exit("refusing --matrix: --selftest did not pass in this invocation "
                 "(run `run.py --selftest --matrix ...` so the instruments are proven first)")
    if not args.mode:
        sys.exit("--matrix needs --mode prompt|plugin")
    if args.budget_usd <= 0 or args.budget_usd > MAX_BUDGET_PER_INVOCATION:
        sys.exit(f"--budget-usd must be in (0, {MAX_BUDGET_PER_INVOCATION}]")
    run_evals, _ = upstream()
    conf = load_conditions(args.conditions_root)
    probe = conf.get("probe", {}).get(args.mode)
    if not (probe and probe.get("passed")):
        sys.exit(f"refusing --matrix --mode {args.mode}: no passed probe for that mode "
                 f"(run --probe --mode {args.mode})")
    drifts = check_pins()
    if drifts:
        sys.exit("refusing --matrix: PIN drift\n  " + "\n  ".join(drifts))
    if not lean().outside_repo(args.runs_root):
        sys.exit(f"refusing: --runs-root {args.runs_root} resolves inside the repository")
    cases = run_evals.load_cases(CASES)
    errors = run_evals.validate_cases(cases)
    if errors:
        sys.exit("\n".join(errors))
    if args.case:
        unknown = sorted(set(args.case) - {c["id"] for c in cases})
        if unknown:
            sys.exit(f"--case matched no evaluation case: {', '.join(unknown)}")
        cases = [c for c in cases if c["id"] in set(args.case)]

    mode = args.mode
    stamp = args.stamp or lean().now_stamp()
    run_dir = args.runs_root / f"{stamp}-{mode}"
    run_dir.mkdir(parents=True, exist_ok=True)
    responses = run_dir / "responses.jsonl"
    meta_path = run_meta_path(run_dir)
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta["model"] != args.model or meta["mode"] != mode:
            sys.exit(f"refusing: {run_dir} was started with model {meta['model']} mode {meta['mode']}")
    else:
        meta = {"stamp": stamp, "mode": mode, "model": args.model, "trials": args.trials,
                "claude_version": lean().claude_version(),
                "rubric_sha256": conf["rubric_sha256"], "cases_sha256": conf["cases_sha256"],
                "candidate_skill_sha256": conf["candidate_skill_sha256"],
                "comparator_skill_sha256": conf["comparator_skill_sha256"],
                "probe": probe, "started": _dt.datetime.now().isoformat(timespec="seconds"),
                "case_filter": args.case or None, "spent_usd": 0.0, "failed_cells": 0}
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    runner_name = f"claude-{mode}"
    prior = run_evals.read_jsonl(responses) if responses.exists() else []
    done = run_evals.completed_keys(prior)
    spent_before = float(meta.get("spent_usd") or 0.0)
    spent = 0.0            # this invocation; --budget-usd caps the invocation, meta keeps the run total
    log(f"matrix {stamp} mode={mode} model={args.model}: {len(cases)} cases x {len(CONDITIONS)} "
        f"conditions x {args.trials} trials, {len(done)} done, run spent ${spent_before:.2f}, "
        f"invocation budget ${args.budget_usd:.2f}")
    stopped = None
    failed = meta.get("failed_cells", 0)
    with responses.open("a", encoding="utf-8") as destination:
        for trial in range(1, args.trials + 1):
            for case in cases:
                for cond in CONDITIONS:
                    key = (case["id"], trial, cond, runner_name)
                    if key in done:
                        continue
                    remaining = min(args.budget_usd - spent, CELL_BUDGET_USD)
                    if remaining <= 0:
                        stopped = f"budget ${args.budget_usd:.2f} reached at ${spent:.4f}"
                        break
                    entry = conf["modes"][mode][cond]
                    cfg = Path(entry["config_dir"])
                    plugin_dir = Path(entry["plugin_dir"]) if entry["plugin_dir"] else None
                    prompt = condition_prompt(mode, cond, case["prompt"])
                    cmd = runner_command(args.model, plugin_dir) + \
                        ["--max-budget-usd", f"{remaining:.4f}", prompt]
                    cell = run_dir / "cells" / f"{case['id']}-t{trial}-{cond}"
                    cell.mkdir(parents=True, exist_ok=True)
                    (cell / "command.txt").write_text(json.dumps(cmd) + "\n", encoding="utf-8")
                    proc = None
                    attempts = 0
                    killed_attempts = 0
                    for attempt in range(CELL_ATTEMPTS):
                        if attempt and _terminal_reason(cell / "stdout.json") == "budget_exhausted":
                            break
                        attempts += 1
                        # one stderr per attempt: a killed attempt's "[KILLED after Ns timeout]"
                        # line must survive the retry, or the hang leaves no trace
                        with run_evals._neutral_cwd() as cwd:
                            proc = lean().run_process(cmd, Path(cwd), cell_env(cfg, mode, cond),
                                                      cell / "stdout.json",
                                                      cell / f"stderr-{attempt}.txt",
                                                      CELL_TIMEOUT_S)
                        if proc["killed"]:
                            killed_attempts += 1
                        if proc["returncode"] == 0:
                            break
                        time.sleep(min(2 ** attempt, 5))
                    assert proc is not None
                    stdout = (cell / "stdout.json").read_text(encoding="utf-8", errors="ignore")
                    if proc["returncode"] != 0:
                        # a failed call can still have spent (measured 2026-10: a comparator cell
                        # on complex-plan ended `budget_exhausted` at $3.34); count it, and stop
                        # retrying a cell the per-call budget cut off — it would burn the same again
                        failed += 1
                        failed_cost = _failed_cost(stdout)
                        spent += failed_cost
                        log(f"FAIL {cond:10s} trial {trial}: {case['id']} rc={proc['returncode']} "
                            f"killed={proc['killed']} attempts={attempts} cost=${failed_cost:.4f} (see {cell})")
                        continue
                    try:
                        text, usage, cost = run_evals._parse_response(stdout, "claude-json")
                    except (ValueError, json.JSONDecodeError) as exc:
                        failed += 1
                        log(f"FAIL {cond:10s} trial {trial}: {case['id']} unparseable: {exc}")
                        continue
                    if cost is None:
                        failed += 1
                        log(f"FAIL {cond:10s} trial {trial}: {case['id']} no total_cost_usd")
                        continue
                    spent += float(cost)
                    row = {"case_id": case["id"], "trial": trial, "condition": cond,
                           "runner": runner_name, "response": text, "usage": usage,
                           "cost_usd": cost, "injection_mode": mode, "model": args.model,
                           "output_tokens": (usage or {}).get("output_tokens"),
                           "forbidden_phrase_hits": forbidden_phrase_hits(text),
                           "wall_s": proc["wall_s"], "attempts": attempts,
                           "killed_attempts": killed_attempts}
                    destination.write(json.dumps(row, ensure_ascii=False) + "\n")
                    destination.flush()
                    done.add(key)
                    log(f"{cond:10s} trial {trial}: {case['id']:20s} out_tokens="
                        f"{row['output_tokens']} hits={row['forbidden_phrase_hits']} ${float(cost):.4f}"
                        + (f" attempts={attempts} killed={killed_attempts}" if attempts > 1 else ""))
                if stopped:
                    break
            if stopped:
                break
    meta["spent_usd"] = round(spent_before + spent, 4)
    meta["failed_cells"] = failed
    meta["rows"] = len(done)
    meta["stopped"] = stopped
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    log(f"matrix {stamp}-{mode}: rows {len(done)}, failed {failed}, spent ${spent:.4f} this invocation, "
        f"${spent_before + spent:.4f} in the run" + (f", STOP {stopped}" if stopped else ""))
    return 2 if stopped else (1 if failed else 0)


# ── judge ─────────────────────────────────────────────────────────────────
def cmd_judge(args: argparse.Namespace) -> int:
    run_evals, judge = upstream()
    run_dir = args.judge
    meta_path = run_meta_path(run_dir)
    if not meta_path.is_file():
        sys.exit(f"{run_dir} has no meta.json: not a matrix run")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    conf = load_conditions(args.conditions_root)
    model = args.judge_model or meta["model"]
    cfg = {"claude": {"command": runner_command(model) + ["--max-budget-usd", f"{JUDGE_CALL_BUDGET_USD:.2f}"],
                      "response_format": "claude-json"}}
    cfg_path = run_dir / "judge-runner.json"
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    scores = run_dir / "scores.jsonl"
    argv = ["--responses", str(run_dir / "responses.jsonl"), "--cases", str(CASES),
            "--rubric", str(RUBRIC), "--runner-config", str(cfg_path), "--runner", "claude",
            "--conditions", *CONDITIONS, "--output", str(scores)]
    saved = dict(os.environ)
    os.environ["CLAUDE_CONFIG_DIR"] = conf["judge_config_dir"]
    os.environ.pop("CLAUDECODE", None)
    os.environ.pop("CAVEMAN_DEFAULT_MODE", None)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(_Tee(buf)):
            rc = judge.main(argv)
    finally:
        os.environ.clear()
        os.environ.update(saved)
    m = re.search(r"Reported judge cost: \$([0-9.]+)", buf.getvalue())
    if meta.get("judge_model") not in (None, model):
        sys.exit(f"refusing: {run_dir.name} was judged with {meta['judge_model']}, not {model}")
    meta["judge_model"] = model
    # accumulated across invocations: the judge is resumable by (case_id, trial) group
    meta["judge_cost_usd"] = round((meta.get("judge_cost_usd") or 0.0) + (float(m.group(1)) if m else 0.0), 4)
    meta["judge_rc"] = rc
    meta["judged"] = _dt.datetime.now().isoformat(timespec="seconds")
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    log(f"judge {run_dir.name}: rc={rc} judge_cost=${meta['judge_cost_usd']}")
    return rc


class _Tee(io.TextIOBase):
    def __init__(self, buf: io.StringIO):
        self.buf = buf

    def write(self, s: str) -> int:  # type: ignore[override]
        self.buf.write(s)
        sys.__stdout__.write(s)
        sys.__stdout__.flush()
        return len(s)


# ── report and verdict ────────────────────────────────────────────────────
def _thinking_tokens(row: dict) -> Optional[int]:
    details = ((row.get("usage") or {}).get("output_tokens_details") or {})
    value = details.get("thinking_tokens")
    return int(value) if isinstance(value, (int, float)) else None


def weighted(row: dict, weights: dict) -> float:
    return sum(float(row[m]) * w for m, w in weights.items())


def mode_summary(rows: list[dict], scores: list[dict], weights: dict) -> dict:
    """Per-condition means and the facts the verdict table reads, for one mode."""
    by_cond: dict[str, list[dict]] = {c: [] for c in CONDITIONS}
    for s in scores:
        by_cond.setdefault(s["condition"], []).append(s)
    conditions: dict[str, dict] = {}
    for cond, score_rows in by_cond.items():
        if not score_rows:
            continue
        metrics = {m: sum(float(r[m]) for r in score_rows) / len(score_rows) for m in weights}
        conditions[cond] = {
            "rows": len(score_rows), **metrics,
            "weighted": sum(metrics[m] * w for m, w in weights.items()),
            "blockers": sum(bool(r["blocker"]) for r in score_rows),
            "blockers_outside_agent_case": sum(bool(r["blocker"]) for r in score_rows
                                               if r["case_id"] != AGENT_CASE),
        }
    resp_by_cond: dict[str, list[dict]] = {}
    for r in rows:
        resp_by_cond.setdefault(r["condition"], []).append(r)
    for cond, response_rows in resp_by_cond.items():
        toks = [r.get("output_tokens") for r in response_rows if isinstance(r.get("output_tokens"), (int, float))]
        hits = [r.get("forbidden_phrase_hits") for r in response_rows
                if isinstance(r.get("forbidden_phrase_hits"), (int, float))]
        conditions.setdefault(cond, {})["output_tokens_mean"] = (sum(toks) / len(toks)) if toks else None
        # Fable's `output_tokens` includes thinking; the reader wants to know how much of the
        # output was the answer the user sees
        thinking = [_thinking_tokens(r) for r in response_rows if _thinking_tokens(r) is not None]
        conditions[cond]["thinking_tokens_mean"] = (sum(thinking) / len(thinking)) if thinking else None
        conditions[cond]["visible_tokens_mean"] = (
            conditions[cond]["output_tokens_mean"] - conditions[cond]["thinking_tokens_mean"]
            if toks and thinking and len(toks) == len(thinking) else None)
        conditions[cond]["forbidden_phrase_hits_mean"] = (sum(hits) / len(hits)) if hits else None
        conditions[cond]["tool_markup_responses"] = sum(1 for r in response_rows if tool_markup(r.get("response", "")))
        conditions[cond]["responses"] = len(response_rows)
    per_case: dict[str, dict[str, float]] = {}
    for s in scores:
        per_case.setdefault(s["case_id"], {}).setdefault(s["condition"], []).append(weighted(s, weights))
    per_case_mean = {case: {c: sum(v) / len(v) for c, v in conds.items()} for case, conds in per_case.items()}
    partial_blocker_trials = sum(1 for s in scores
                                 if s["condition"] == "candidate" and s["case_id"] == PARTIAL_CASE
                                 and bool(s["blocker"]))
    return {"conditions": conditions, "per_case": per_case_mean,
            "candidate_partial_success_blocker_trials": partial_blocker_trials}


def verdict_for_mode(summary: dict) -> dict:
    c = summary["conditions"]
    if not all(k in c and "weighted" in c[k] for k in CONDITIONS):
        return {"verdict": "NO-CLAIM", "reasons": ["a condition has no judged rows"], "delta": None}
    delta = c["candidate"]["weighted"] - c["comparator"]["weighted"]
    reject: list[str] = []
    if delta < 0:
        reject.append(f"delta {delta:+.3f} < 0: candidate below comparator")
    if summary["candidate_partial_success_blocker_trials"] >= 2:
        reject.append(f"candidate blocker on {PARTIAL_CASE} in "
                      f"{summary['candidate_partial_success_blocker_trials']} trials (>= 2)")
    if reject:
        return {"verdict": "REJECT", "reasons": reject, "delta": delta}
    adopt_fail: list[str] = []
    if delta < 0.2:
        adopt_fail.append(f"delta {delta:+.3f} < +0.2")
    if c["candidate"]["correctness"] < c["baseline"]["correctness"] - 0.1:
        adopt_fail.append("correctness below baseline - 0.1")
    if c["candidate"]["safety"] < c["baseline"]["safety"] - 0.1:
        adopt_fail.append("safety below baseline - 0.1")
    if c["candidate"]["blockers_outside_agent_case"] > 0:
        adopt_fail.append(f"candidate blockers outside {AGENT_CASE}: "
                          f"{c['candidate']['blockers_outside_agent_case']}")
    if adopt_fail:
        return {"verdict": "NO-CLAIM", "reasons": adopt_fail, "delta": delta}
    return {"verdict": "ADOPT", "reasons": [], "delta": delta}


def combine_verdicts(per_mode: dict[str, dict]) -> dict:
    """ADOPT needs both modes ADOPT; REJECT in any mode is REJECT; else NO-CLAIM."""
    verdicts = {m: v["verdict"] for m, v in per_mode.items()}
    if any(v == "REJECT" for v in verdicts.values()):
        return {"verdict": "REJECT", "modes": verdicts,
                "reasons": [f"{m}: {r}" for m, v in per_mode.items() for r in v["reasons"] if v["verdict"] == "REJECT"]}
    if set(verdicts) == set(MODES) and all(v == "ADOPT" for v in verdicts.values()):
        return {"verdict": "ADOPT", "modes": verdicts, "reasons": []}
    reasons = [f"{m}: {r}" for m, v in per_mode.items() for r in v["reasons"]]
    missing = sorted(set(MODES) - set(verdicts))
    if missing:
        reasons.append(f"mode(s) not measured: {', '.join(missing)}")
    if len(set(verdicts.values())) > 1:
        reasons.append("modes disagree")
    return {"verdict": "NO-CLAIM", "modes": verdicts, "reasons": reasons}


def fmt(x: Any, nd: int = 3) -> str:
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def cmd_report(args: argparse.Namespace) -> int:
    run_evals, _ = upstream()
    weights = run_evals.WEIGHTS
    runs = [Path(p) for p in args.report]
    metas = []
    for r in runs:
        mp = run_meta_path(r)
        if not mp.is_file():
            sys.exit(f"{r}: no meta.json")
        metas.append(json.loads(mp.read_text(encoding="utf-8")))
    for key in ("claude_version", "model", "rubric_sha256", "cases_sha256",
                "candidate_skill_sha256", "comparator_skill_sha256"):
        vals = {m.get(key) for m in metas}
        if len(vals) > 1:
            sys.exit(f"refusing to aggregate runs whose {key} differ: {sorted(map(str, vals))}")
    modes_seen = [m["mode"] for m in metas]
    if len(set(modes_seen)) != len(modes_seen):
        sys.exit(f"refusing: two runs of the same mode ({modes_seen}); report one run per mode")
    payload: dict[str, Any] = {
        "stamps": [m["stamp"] for m in metas], "model": metas[0]["model"],
        "judge_models": sorted({str(m.get("judge_model")) for m in metas}),
        "claude_version": metas[0]["claude_version"], "rubric_sha256": metas[0]["rubric_sha256"],
        "protocol_sha256": sha256_file(HERE / "protocol.md"),
        "weights": weights, "modes": {}, "spend_usd": {},
    }
    per_mode_verdict: dict[str, dict] = {}
    lines: list[str] = []
    for r, meta in zip(runs, metas):
        mode = meta["mode"]
        rows = run_evals.read_jsonl(r / "responses.jsonl")
        scores_path = r / "scores.jsonl"
        # a run that was never judged (the maintainer stopped the spend) still has its counters;
        # its verdict is NO-CLAIM by the letter, and the report says why
        scores = run_evals.read_jsonl(scores_path) if scores_path.is_file() else []
        summary = mode_summary(rows, scores, weights)
        try:
            upstream_gate = run_evals.summarize_scores(scores)["release_gate"] if scores else \
                {"passed": None, "reasons": ["not judged"]}
        except ValueError as exc:
            upstream_gate = {"passed": None, "reasons": [str(exc)]}
        verdict = verdict_for_mode(summary)
        if not scores:
            verdict = {"verdict": "NO-CLAIM", "delta": None,
                       "reasons": [f"{len(rows)} responses, none judged (spend stopped by the maintainer)"]}
        per_mode_verdict[mode] = verdict
        payload["modes"][mode] = {"stamp": meta["stamp"], "summary": summary, "verdict": verdict,
                                  "upstream_release_gate": upstream_gate,
                                  "rows": len(rows), "score_rows": len(scores),
                                  "failed_cells": meta.get("failed_cells"),
                                  "judge_model": meta.get("judge_model")}
        payload["spend_usd"][mode] = {"generation": meta.get("spent_usd"),
                                      "judge": meta.get("judge_cost_usd")}
        c = summary["conditions"]
        lines.append(f"\n## mode `{mode}` — stamp {meta['stamp']}, {len(rows)} responses, "
                     f"{len(scores)} score rows\n")
        lines.append("| condition | rows | correctness | autonomy | actionability | safety | concision "
                     "| **weighted** | blockers | blockers excl. agent case | output_tokens | of which thinking "
                     "| visible | forbidden hits | tool markup |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for cond in CONDITIONS:
            d = c.get(cond, {})
            lines.append(f"| `{cond}` | {d.get('rows', 0)} | {fmt(d.get('correctness'))} | "
                         f"{fmt(d.get('autonomy'))} | {fmt(d.get('actionability'))} | {fmt(d.get('safety'))} | "
                         f"{fmt(d.get('concision'))} | **{fmt(d.get('weighted'))}** | {d.get('blockers', 0)} | "
                         f"{d.get('blockers_outside_agent_case', 0)} | {fmt(d.get('output_tokens_mean'), 1)} | "
                         f"{fmt(d.get('thinking_tokens_mean'), 1)} | {fmt(d.get('visible_tokens_mean'), 1)} | "
                         f"{fmt(d.get('forbidden_phrase_hits_mean'), 2)} | {d.get('tool_markup_responses', 0)}/{d.get('responses', 0)} |")
        lines.append(f"\ndelta (candidate − comparator, weighted): {fmt(verdict['delta'])}; "
                     f"candidate `{PARTIAL_CASE}` blocker trials: "
                     f"{summary['candidate_partial_success_blocker_trials']}")
        lines.append(f"verdict for this mode: **{verdict['verdict']}**"
                     + (" — " + "; ".join(verdict["reasons"]) if verdict["reasons"] else ""))
        lines.append(f"upstream release gate (candidate vs baseline, for comparability): "
                     f"{'passed' if upstream_gate['passed'] else ('failed' if upstream_gate['passed'] is False else 'n/a')}"
                     + (" — " + "; ".join(upstream_gate["reasons"]) if upstream_gate["reasons"] else ""))
        lines.append("\n| case | baseline | comparator | candidate | cand − comp |")
        lines.append("|---|---:|---:|---:|---:|")
        for case_id in sorted(summary["per_case"]):
            pc = summary["per_case"][case_id]
            d = (pc.get("candidate", 0) - pc.get("comparator", 0)) if ("candidate" in pc and "comparator" in pc) else None
            tag = " (impassable without tools)" if case_id == AGENT_CASE else ""
            lines.append(f"| `{case_id}`{tag} | {fmt(pc.get('baseline'), 2)} | {fmt(pc.get('comparator'), 2)} | "
                         f"{fmt(pc.get('candidate'), 2)} | {fmt(d, 2)} |")
    overall = combine_verdicts(per_mode_verdict)
    payload["verdict"] = overall
    lines.append(f"\n## verdict, by the letter of protocol.md: **{overall['verdict']}**")
    for reason in overall["reasons"]:
        lines.append(f"- {reason}")
    lines.append(f"\nspend: " + ", ".join(f"{m}: gen ${fmt(v['generation'], 4)} + judge ${fmt(v['judge'], 4)}"
                                          for m, v in payload["spend_usd"].items()))
    print("\n".join(lines))
    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        stripped = lean().strip_export(payload)
        args.export.write_text(json.dumps(stripped, indent=2) + "\n", encoding="utf-8")
        log(f"wrote {args.export}")
    return 0


# ── selftest ──────────────────────────────────────────────────────────────
class Selftest:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, bool, str]] = []

    def case(self, group: str, name: str, ok: bool, detail: str = "") -> None:
        self.rows.append((group, name, bool(ok), detail))

    def report(self) -> bool:
        groups: dict[str, list[bool]] = {}
        for g, name, ok, detail in self.rows:
            groups.setdefault(g, []).append(ok)
            if not ok:
                log(f"  FAIL [{g}] {name}" + (f": {detail}" if detail else ""))
        for g, oks in groups.items():
            log(f"  {g:10s} {sum(oks)}/{len(oks)}")
        total = sum(ok for _, _, ok, _ in self.rows)
        log(f"selftest {total}/{len(self.rows)}")
        return total == len(self.rows)


def selftest_vendor(st: Selftest) -> None:
    drifts = check_pins()
    st.case("vendor", "every hashed file matches its PIN", not drifts, "; ".join(drifts))
    n = len(pin_hashes(VENDOR_PIN)) + len(pin_hashes(CAVEMAN_PIN))
    st.case("vendor", "PINs carry hashes", n >= 16, f"{n} hashes")


def selftest_upstream(st: Selftest) -> None:
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                          cwd=str(VENDOR), capture_output=True, text=True, timeout=300)
    tail = (proc.stderr.strip().splitlines() or [""])[-1]
    st.case("upstream", "vendor unit tests pass (unittest discover -s tests)", proc.returncode == 0, tail)
    m = re.search(r"Ran (\d+) tests", proc.stderr)
    st.case("upstream", "the suite ran tests", bool(m and int(m.group(1)) > 0), tail)


def selftest_contract(st: Selftest) -> None:
    mod = lean()
    missing = [s for s in LEAN_SYMBOLS if not hasattr(mod, s)]
    st.case("contract", "lean-code symbols exist", not missing, f"missing={missing}")
    run_evals, judge = upstream()
    missing = [s for s in UPSTREAM_SYMBOLS if not hasattr(run_evals, s)]
    st.case("contract", "upstream run_evals symbols exist", not missing, f"missing={missing}")
    st.case("contract", "judge imported the vendored run_evals",
            getattr(judge, "run_evals", None) is run_evals)
    st.case("contract", "judge.main exists", callable(getattr(judge, "main", None)))
    st.case("contract", "upstream CONDITIONS are ours", set(run_evals.CONDITIONS) == set(CONDITIONS))
    st.case("contract", "rubric weights sum to 1", abs(sum(run_evals.WEIGHTS.values()) - 1.0) < 1e-9)
    st.case("contract", "baseline prompt is the bare task",
            run_evals._condition_prompt("T", "baseline", None) == "T")
    wrapped = run_evals._condition_prompt("T", "candidate", CANDIDATE_SKILL)
    st.case("contract", "candidate prompt wraps the skill body", "<response_style>" in wrapped
            and "Lead with the next action" in wrapped and "<task>\nT\n</task>" in wrapped)
    st.case("contract", "plugin mode prompt is bare for every condition",
            all(condition_prompt("plugin", c, "T") == "T" for c in CONDITIONS))
    text, usage, cost = run_evals._parse_response(
        json.dumps({"result": "ok", "usage": {"output_tokens": 7}, "total_cost_usd": 0.01}), "claude-json")
    st.case("contract", "_parse_response reads result, usage and cost",
            text == "ok" and usage["output_tokens"] == 7 and cost == 0.01)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "s.jsonl"
        p.write_text(json.dumps({"type": "system", "subtype": "hook_started", "hook_event_name": "SessionStart"})
                     + "\n" + json.dumps({"type": "result", "result": "DONE", "total_cost_usd": 0.001}) + "\n")
        parsed = mod.parse_stream(p)
        st.case("contract", "parse_stream lists hook events by name",
                hook_event_names(parsed) == ["SessionStart"] and parsed["result_text"] == "DONE")
        p.write_text(json.dumps({"type": "result", "result": "DONE"}) + "\n")
        st.case("contract", "parse_stream without hooks reports none", hook_event_names(mod.parse_stream(p)) == [])
    st.case("contract", "outside_repo tells the repository from /tmp",
            mod.outside_repo(Path(tempfile.gettempdir())) and not mod.outside_repo(HERE))
    st.case("contract", "now_stamp shape", re.fullmatch(r"\d{8}-\d{6}", mod.now_stamp()) is not None)


def selftest_counters(st: Selftest) -> None:
    st.case("counters", "clean text has no hits", forbidden_phrase_hits("Run `npm test`. Next: open the file.") == 0)
    st.case("counters", "three forbidden phrases count three",
            forbidden_phrase_hits("Great question! Let me look. Hope this helps.") == 3)
    st.case("counters", "case-insensitive", forbidden_phrase_hits("great QUESTION") == 1)
    st.case("counters", "empty and None are zero", forbidden_phrase_hits("") == 0 and forbidden_phrase_hits(None) == 0)
    st.case("counters", "tool markup: invoke block, bare tool name + JSON, and clean text",
            tool_markup('<invoke name="Bash">\n<parameter name="command">ls</parameter>') and
            tool_markup('Checking first.\n\nBash\n{\n  "command": "ls"\n}') and
            not tool_markup("Run `ls -la` in Bash, then read the output.") and not tool_markup(""))
    st.case("counters", "the list is rule 10's, literally",
            all(p in CANDIDATE_SKILL.read_text(encoding="utf-8") for p in FORBIDDEN_PHRASES))


def _synthetic(base: float, comp: float, cand: float, *, cand_corr: float = 4.5, base_corr: float = 4.5,
               cand_safety: float = 4.5, base_safety: float = 4.5, cand_blockers_outside: int = 0,
               partial_trials: int = 0) -> dict:
    def cond(w: float, corr: float, safety: float, blockers: int) -> dict:
        return {"rows": 42, "correctness": corr, "autonomy": w, "actionability": w, "safety": safety,
                "concision": w, "weighted": w, "blockers": blockers, "blockers_outside_agent_case": blockers}
    return {"conditions": {"baseline": cond(base, base_corr, base_safety, 0),
                           "comparator": cond(comp, 4.5, 4.5, 0),
                           "candidate": cond(cand, cand_corr, cand_safety, cand_blockers_outside)},
            "per_case": {}, "candidate_partial_success_blocker_trials": partial_trials}


def selftest_verdict(st: Selftest) -> None:
    v = verdict_for_mode
    st.case("verdict", "ADOPT when delta >= 0.2 and nothing regressed", v(_synthetic(4.0, 4.2, 4.4))["verdict"] == "ADOPT")
    st.case("verdict", "ADOPT at exactly +0.2", v(_synthetic(4.0, 4.2, 4.4))["delta"] >= 0.2 - 1e-9)
    st.case("verdict", "NO-CLAIM when 0 <= delta < 0.2", v(_synthetic(4.0, 4.2, 4.3))["verdict"] == "NO-CLAIM")
    st.case("verdict", "REJECT when candidate below comparator", v(_synthetic(4.0, 4.4, 4.3))["verdict"] == "REJECT")
    st.case("verdict", "REJECT on partial-success blocker in 2 trials",
            v(_synthetic(4.0, 4.0, 4.5, partial_trials=2))["verdict"] == "REJECT")
    st.case("verdict", "one partial-success blocker trial is not REJECT",
            v(_synthetic(4.0, 4.0, 4.5, partial_trials=1, cand_blockers_outside=1))["verdict"] == "NO-CLAIM")
    st.case("verdict", "NO-CLAIM on correctness regression beyond 0.1",
            v(_synthetic(4.0, 4.0, 4.5, cand_corr=4.3, base_corr=4.5))["verdict"] == "NO-CLAIM")
    st.case("verdict", "NO-CLAIM on safety regression beyond 0.1",
            v(_synthetic(4.0, 4.0, 4.5, cand_safety=4.3))["verdict"] == "NO-CLAIM")
    st.case("verdict", "NO-CLAIM on a candidate blocker outside the agent case",
            v(_synthetic(4.0, 4.0, 4.5, cand_blockers_outside=1))["verdict"] == "NO-CLAIM")
    st.case("verdict", "NO-CLAIM when a condition is missing",
            v({"conditions": {"baseline": {"weighted": 4}}, "candidate_partial_success_blocker_trials": 0})["verdict"] == "NO-CLAIM")
    adopt = v(_synthetic(4.0, 4.2, 4.4))
    st.case("verdict", "combined ADOPT needs both modes", combine_verdicts({"prompt": adopt, "plugin": adopt})["verdict"] == "ADOPT"
            and combine_verdicts({"prompt": adopt})["verdict"] == "NO-CLAIM")
    st.case("verdict", "combined REJECT on any mode",
            combine_verdicts({"prompt": adopt, "plugin": v(_synthetic(4.0, 4.4, 4.3))})["verdict"] == "REJECT")
    st.case("verdict", "modes that disagree are NO-CLAIM",
            combine_verdicts({"prompt": adopt, "plugin": v(_synthetic(4.0, 4.2, 4.3))})["verdict"] == "NO-CLAIM")
    # mode_summary on synthetic rows: means, blockers, partial trials, counters
    run_evals, _ = upstream()
    scores = []
    for cond, w in (("baseline", 3), ("comparator", 4), ("candidate", 5)):
        for case_id in ("direct-answer", AGENT_CASE, PARTIAL_CASE):
            for trial in (1, 2, 3):
                scores.append({"case_id": case_id, "trial": trial, "condition": cond, "correctness": w,
                               "autonomy": w, "actionability": w, "safety": w, "concision": w,
                               "blocker": (cond == "candidate" and case_id in (AGENT_CASE, PARTIAL_CASE) and trial < 3),
                               "notes": ""})
    rows = [{"condition": c, "output_tokens": t, "forbidden_phrase_hits": h}
            for c, t, h in (("baseline", 100, 2), ("baseline", 200, 0), ("candidate", 50, 0))]
    s = mode_summary(rows, scores, run_evals.WEIGHTS)
    st.case("verdict", "mode_summary means and weighted", s["conditions"]["candidate"]["weighted"] == 5.0
            and s["conditions"]["baseline"]["weighted"] == 3.0)
    st.case("verdict", "mode_summary blockers and the agent-case exclusion",
            s["conditions"]["candidate"]["blockers"] == 4 and s["conditions"]["candidate"]["blockers_outside_agent_case"] == 2)
    st.case("verdict", "mode_summary counts partial-success blocker trials", s["candidate_partial_success_blocker_trials"] == 2)
    st.case("verdict", "mode_summary counters are means",
            s["conditions"]["baseline"]["output_tokens_mean"] == 150 and s["conditions"]["baseline"]["forbidden_phrase_hits_mean"] == 1.0)
    rows2 = [{"condition": "candidate", "output_tokens": 100, "forbidden_phrase_hits": 0,
              "usage": {"output_tokens_details": {"thinking_tokens": 60}}}]
    s2 = mode_summary(rows2, [], run_evals.WEIGHTS)
    st.case("verdict", "mode_summary splits thinking from visible output",
            s2["conditions"]["candidate"]["thinking_tokens_mean"] == 60 and s2["conditions"]["candidate"]["visible_tokens_mean"] == 40
            and s["conditions"]["baseline"]["visible_tokens_mean"] is None)
    st.case("verdict", "mode_summary per-case table", s["per_case"][PARTIAL_CASE]["candidate"] == 5.0)


def selftest_stripper(st: Selftest) -> None:
    home = str(Path.home())
    payload = {"session_id": "x", "nested": {"path": home + "/runs/a", "request_id": "r", "keep": "y"},
               "list": [{"uuid": "u", "v": "123e4567-e89b-12d3-a456-426614174000"}]}
    out = lean().strip_export(payload)
    flat = json.dumps(out)
    st.case("stripper", "session_id, request_id and uuid keys are gone",
            "session_id" not in flat and "request_id" not in flat and '"uuid"' not in flat)
    st.case("stripper", "home path and uuid values are rewritten", home not in flat and "426614174000" not in flat
            and out["nested"]["keep"] == "y")
    st.case("stripper", "report payload carries no response text",
            "SECRET" not in json.dumps(mode_summary([{"condition": "baseline", "response": "SECRET",
                                                          "output_tokens": 1, "forbidden_phrase_hits": 0}], [],
                                                        upstream()[0].WEIGHTS)))


def selftest_preflight(st: Selftest) -> None:
    refused = False
    try:
        prepare_conditions(HERE / "scratch-should-refuse", None)
    except SystemExit:
        refused = True
    st.case("preflight", "a conditions root inside the repository is refused", refused
            and not (HERE / "scratch-should-refuse").exists())
    with tempfile.TemporaryDirectory(prefix="ihadhd-selftest-") as td:
        root = Path(td) / "conds"
        fake = Path(td) / "live-credentials.json"
        fake.write_text("{}", encoding="utf-8")
        conf = prepare_conditions(root, fake)
        flags = sorted(str(p.relative_to(root)) for p in root.rglob(ADHD_FLAG))
        st.case("preflight", "the always-on flag exists only in plugin/candidate",
                flags == [f"plugin/candidate/config/{ADHD_FLAG}"], str(flags))
        credential_files = list(root.rglob(CREDENTIALS_FILE))
        st.case("preflight", "every config dir links to the one live credentials file",
                len(credential_files) == len(MODES) * len(CONDITIONS) + 1
                and all(p.is_symlink() and p.resolve() == fake.resolve() for p in credential_files))
        st.case("preflight", "comparator plugin dir is the installed cache, candidate is the vendor",
                conf["modes"]["plugin"]["comparator"]["plugin_dir"] == str(caveman_installed_dir())
                and conf["modes"]["plugin"]["candidate"]["plugin_dir"] == str(CANDIDATE_PLUGIN_DIR)
                and conf["modes"]["prompt"]["candidate"]["plugin_dir"] is None)
        env = cell_env(Path(conf["modes"]["plugin"]["comparator"]["config_dir"]), "plugin", "comparator")
        st.case("preflight", "comparator cell env pins the caveman level and the config dir",
                env.get("CAVEMAN_DEFAULT_MODE") == CAVEMAN_LEVEL and env["CLAUDE_CONFIG_DIR"].endswith("plugin/comparator/config")
                and "CLAUDECODE" not in env)
        env = cell_env(Path(conf["modes"]["plugin"]["candidate"]["config_dir"]), "plugin", "candidate")
        st.case("preflight", "candidate cell env carries no caveman level", "CAVEMAN_DEFAULT_MODE" not in env)
        cmd = runner_command("m", Path("/p"))
        st.case("preflight", "runner command is the upstream's plus --plugin-dir",
                cmd[1:] == ["--disable-slash-commands", "--print", "--output-format", "json", "--no-session-persistence",
                            "--setting-sources", "", "--model", "m", "--tools", "", "--plugin-dir", "/p"])
        st.case("preflight", "probe command streams hook events under the same isolation",
                all(f in probe_command("m", None) for f in ("--include-hook-events", "--setting-sources", "--verbose")))
        with tempfile.TemporaryDirectory() as td2:
            st.case("preflight", "load_conditions round-trips", load_conditions(root)["credentials_linked"] == str(fake.resolve()))
            refused = False
            try:
                load_conditions(Path(td2))
            except SystemExit:
                refused = True
            st.case("preflight", "load_conditions refuses a root without conditions.json", refused)


def cmd_selftest(args: argparse.Namespace) -> int:
    global SELFTEST_PASSED
    st = Selftest()
    for fn in (selftest_vendor, selftest_upstream, selftest_contract, selftest_counters,
               selftest_verdict, selftest_stripper, selftest_preflight):
        try:
            fn(st)
        except Exception as exc:  # noqa: BLE001
            st.case(fn.__name__.replace("selftest_", ""), "group raised", False, repr(exc))
    ok = st.report()
    SELFTEST_PASSED = ok
    return 0 if ok else 1


# ── main ──────────────────────────────────────────────────────────────────
def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--prepare-conditions", action="store_true")
    p.add_argument("--teardown", action="store_true")
    p.add_argument("--refresh-credentials", action="store_true")
    p.add_argument("--probe", action="store_true")
    p.add_argument("--probe-model", default=PROBE_MODEL)
    p.add_argument("--probe-out", type=Path, help="stripped copy of probe.json (e.g. results/<stamp>-probe.json)")
    p.add_argument("--matrix", action="store_true")
    p.add_argument("--judge", type=Path, metavar="RUN_DIR")
    p.add_argument("--judge-model", default=None, help="defaults to the run's generator model")
    p.add_argument("--report", nargs="+", metavar="RUN_DIR")
    p.add_argument("--export", type=Path)
    p.add_argument("--mode", choices=list(MODES))
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--case", action="append")
    p.add_argument("--stamp", default=None, help="resume a run: its stamp")
    p.add_argument("--budget-usd", type=float, default=10.0)
    p.add_argument("--conditions-root", type=Path, default=None)
    p.add_argument("--runs-root", type=Path, default=None)
    args = p.parse_args(argv)
    needs_root = (args.prepare_conditions or args.teardown or args.probe or args.matrix or args.judge
                  or args.refresh_credentials)
    if needs_root and args.conditions_root is None:
        p.error("--conditions-root is required (outside the repository)")
    if args.matrix and args.runs_root is None:
        p.error("--runs-root is required for --matrix (outside the repository)")
    rc = 0
    if args.selftest:
        rc = cmd_selftest(args)
        if rc:
            return rc
    if args.prepare_conditions:
        rc = cmd_prepare_conditions(args) or rc
    if args.refresh_credentials:
        rc = cmd_refresh_credentials(args) or rc
    if args.probe:
        rc = cmd_probe(args) or rc
    if args.matrix:
        rc = cmd_matrix(args) or rc
    if args.judge:
        rc = cmd_judge(args) or rc
    if args.report:
        rc = cmd_report(args) or rc
    if args.teardown:
        rc = cmd_teardown(args) or rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
