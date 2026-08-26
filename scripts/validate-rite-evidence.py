#!/usr/bin/env python3
"""Evidence gate for the skills-rite mandatory groups.

`scripts/validate-rite.sh` makes the mandatory groups structural — present, correctly positioned.
Its own header states what it cannot do: "a ticked box with no probe behind it looks identical to
one with. The gate makes the evidence a required, reviewable artifact; the review is what judges
it." Measured across the archived corpus, that review half did not happen: of 305 ticked boxes in
mandatory groups, 7 carried a command and its output (2%).

This adds the half a script can honestly do.

  R1 evidence shape     a ticked Evidence & Sources box states what was run, not a conclusion
  R2 simulation shape   a ticked Simulation & Field Proof box states what was EXERCISED and observed

and prints, without gating, how dense every mandatory group's evidence is, so a `Quality Gates 0/5`
is visible on the pull request without reading the diff.

Per-kind rules, because the four E boxes do not share a shape — a uniform "command -> output" rule
was measured first and rejected: it failed 14 of 20 historical boxes, including 3 of the 4 in the
most recently written change, all correct as written.

  E.1  paths opened          a repo-relative path AND the commit sha or date it was read at
  E.2  tools probed          at least one `command` -> output pair
  E.3  what could not be probed   names the gap, or states explicitly that there is none
  E.4  scope check           lists a follow-up, or states explicitly that there is none

The simulation group asks a different question — not what was read before writing, but what was RUN
before calling it delivered. Earned on 2026-08-26 (issue #95): a green `--selftest` and a green CI
still shipped two defects that only an end-to-end run through the real harness surfaced.

  S.1  artifact exercised    an `entry point` -> a fragment of the OBSERVED output, or an explicit
                             statement that the change touches no runtime artifact
  S.2  case matrix           counts, not adjectives: n/n fired, n/n silent, n/n escapes
  S.3  what escaped          names it, or states explicitly that nothing did

KNOWN LIMIT — what this gate does NOT do. A passing run is not proof the evidence is real.
  1. It cannot detect fabricated output. A box padded with `-> ok` passes every rule here. This
     repo already designed and rejected a stronger version for that reason
     (`openspec/changes/archive/2026-08-07-add-verify-before-claiming/design.md`): CI can only prove
     a record is well-typed, which converts an obvious defect into a certified one. What is checked
     here is only that a box STATES what the template already requires it to state.
  2. `Quality Gates` and `Validation & Closure` are reported, never gated. Several of their items
     are judgments rather than executions (`Q.3` is "triggers do not collide"), and demanding a
     command there manufactures padding.
  3. Only the four E kinds and the three S kinds have rules. A fifth `E.5` a change invents is
     counted in the density report and otherwise unchecked. Nothing here reads the artifact that S.1
     names: a box can cite a command that was never run, and the gate cannot tell.
  4. Unticked boxes are ignored. The rule is about what a tick claims, not about progress.
  5. Only active changes are read; `openspec/changes/archive/` is history and is never re-litigated.
  6. It fires on nothing in the current corpus — every historical E box passes. That is calibration
     (no false positives on genuine boxes), not proof it works; `--selftest` is what proves that.

Exit 1 on any finding. Run from the repo root.
Modes: (default) check active changes   |   --selftest inject one defect per rule and assert detection.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
CHANGES = "openspec/changes"

BOX = re.compile(r"^ *- \[(?P<tick>[ x])\] +(?P<id>[A-Z]\.\d+|\d+\.\d+)?(?P<rest>.*)$")
GROUP = re.compile(r"^## +(?P<title>.+?)\s*$")
BACKTICKED = re.compile(r"`([^`]+)`")
ARROW = re.compile(r"->|→")
SHA_OR_DATE = re.compile(r"`[0-9a-f]{7,40}`|\b20\d\d-\d\d-\d\d\b")
PATH_IN_TICKS = re.compile(r"`[^`\s]+\.(?:md|py|sh|ya?ml|json|lua|tsx?|jsx?|cs|sql|toml|ini)[^`]*`")
NEGATIVE = re.compile(r"\bnone\b|\bnothing\b|\bno gaps?\b|\bnenhum", re.I)
# S.2 wants the matrix as numbers. `10/10` and `0 de 6` both count; a sentence claiming "todos os
# casos passaram" does not, which is the whole point of asking for counts.
COUNTS = re.compile(r"\b\d+\s*(?:/|de|of)\s*\d+\b")
# The escape hatch S.1 accepts, paired with NEGATIVE so that "nothing to simulate" reads as a
# deliberate statement rather than an accidental word match.
NO_RUNTIME = re.compile(r"runtime|execut|runnable|artefato|artifact|script|hook|skill", re.I)

findings: list[str] = []

# GitHub turns `::error file=...` into a red annotation on the pull request. During --selftest the
# findings are injected on purpose and their paths do not exist, so annotating them would put four
# bogus failures on a PR whose job passed. Measured on run 31790712710 before this guard existed.
annotate = True


def add(check: str, path: Path, detail: str) -> None:
    # The selftest runs the checks against a temp copy, so the path is not always under ROOT.
    try:
        rel: Path | str = path.relative_to(ROOT)
    except ValueError:
        idx = path.parts.index(CHANGES.split("/")[0]) if CHANGES.split("/")[0] in path.parts else 0
        rel = str(Path(*path.parts[idx:]))
    findings.append(f"{check}: {rel}: {detail}")
    if annotate:
        print(f"::error file={rel}::{check} — {detail}")
    else:
        print(f"    injected: {check} — {detail}")


# ── parsing ───────────────────────────────────────────────────────────────
def parse_boxes(text: str) -> list[tuple[str, str, bool, str]]:
    """Yield (group_title, box_id, ticked, full_text) with continuation lines folded in."""
    out: list[tuple[str, str, bool, str]] = []
    group = ""
    pending: list[str] | None = None
    meta: tuple[str, str, bool] | None = None

    def flush() -> None:
        if pending is not None and meta is not None:
            out.append((meta[0], meta[1], meta[2], " ".join(pending)))

    for line in text.splitlines():
        g = GROUP.match(line)
        if g:
            flush()
            pending, meta = None, None
            group = g.group("title")
            continue
        b = BOX.match(line)
        if b:
            flush()
            box_id = (b.group("id") or "").strip()
            meta = (group, box_id, b.group("tick") == "x")
            pending = [b.group("rest").strip()]
            continue
        if pending is not None and line.strip() and not line.lstrip().startswith("<!--"):
            pending.append(line.strip())
    flush()
    return out


def active_task_files(root: Path) -> list[Path]:
    base = root / CHANGES
    if not base.is_dir():
        return []
    return sorted(
        d / "tasks.md" for d in base.iterdir()
        if d.is_dir() and d.name != "archive" and (d / "tasks.md").is_file()
    )


# ── R1: evidence shape ────────────────────────────────────────────────────
def _shape_ok(box_id: str, body: str) -> tuple[bool, str]:
    if box_id == "E.1":
        if not PATH_IN_TICKS.search(body):
            return False, "cites no repo-relative path — name at least one file that was opened"
        if not SHA_OR_DATE.search(body):
            return False, "names no commit sha or date — state when the paths were read"
        return True, ""
    if box_id == "E.2":
        if not (BACKTICKED.search(body) and ARROW.search(body)):
            return False, "states a conclusion, not a probe — record `command` -> a fragment of its output"
        return True, ""
    if box_id in ("E.3", "E.4"):
        subject = "gap" if box_id == "E.3" else "follow-up"
        if NEGATIVE.search(body) or len(body) > 120:
            return True, ""
        return False, f"neither names a {subject} nor states there is none"
    return True, ""


def check_evidence_shape(root: Path) -> None:
    for tasks in active_task_files(root):
        for group, box_id, ticked, body in parse_boxes(tasks.read_text(encoding="utf-8")):
            if not ticked or "Evidence & Sources" not in group:
                continue
            if box_id not in ("E.1", "E.2", "E.3", "E.4"):
                continue
            ok, why = _shape_ok(box_id, body)
            if not ok:
                add("R1 evidence shape", tasks, f"{box_id} {why}")


# ── R2: simulation shape ──────────────────────────────────────────────────
# The evidence group asks what was READ and PROBED before writing. This one asks what was RUN before
# calling it delivered — a different question, so a different shape per box, for the same reason the
# E rules are per kind: a uniform rule rejects boxes that are correct as written.
def _simulation_shape_ok(box_id: str, body: str) -> "tuple[bool, str]":
    if box_id == "S.1":
        # An explicit "no runtime artifact" is a valid answer: documentation-only work must not be
        # pushed into inventing a simulation, exactly as E.3/E.4 accept an explicit absence.
        if NEGATIVE.search(body) and NO_RUNTIME.search(body):
            return True, ""
        if not (BACKTICKED.search(body) and ARROW.search(body)):
            return False, ("names no entry point and no observed output — record "
                           "`what you ran` -> a fragment of what you SAW, or state explicitly that "
                           "this change touches no runtime artifact")
        return True, ""
    if box_id == "S.2":
        if not COUNTS.search(body):
            return False, ("carries no counts — record the case matrix as numbers (n/n): what had to "
                           "fire and did, what had to stay silent and did, which escapes stayed silent")
        return True, ""
    if box_id == "S.3":
        if NEGATIVE.search(body) or len(body) > 120:
            return True, ""
        return False, "neither names what escaped nor states that nothing did"
    return True, ""


def check_simulation_shape(root: Path) -> None:
    for tasks in active_task_files(root):
        for group, box_id, ticked, body in parse_boxes(tasks.read_text(encoding="utf-8")):
            if not ticked or "Simulation & Field Proof" not in group:
                continue
            if box_id not in ("S.1", "S.2", "S.3"):
                continue
            ok, why = _simulation_shape_ok(box_id, body)
            if not ok:
                add("R2 simulation shape", tasks, f"{box_id} {why}")


CHECKS = (check_evidence_shape, check_simulation_shape)


# ── density report (never gates) ──────────────────────────────────────────
def report_density(root: Path) -> None:
    files = active_task_files(root)
    if not files:
        print("  evidence density: no active change to report on")
        return
    print("  evidence density (report only — not a pass/fail result):")
    for tasks in files:
        change = tasks.parent.name
        per: dict[str, list[bool]] = {}
        for group, _box, ticked, body in parse_boxes(tasks.read_text(encoding="utf-8")):
            if not ticked or "(MANDATORY)" not in group:
                continue
            per.setdefault(group.replace(" (MANDATORY)", ""), []).append(bool(ARROW.search(body)))
        if not per:
            continue
        print(f"    {change}")
        for group, marks in per.items():
            print(f"      {group:<22} {sum(marks)}/{len(marks)} boxes carry a command -> output")


# ── selftest ──────────────────────────────────────────────────────────────
# A checker that never fails is not a checker. One injected defect per rule, asserted detected.
_SCAFFOLD = """## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Read `scripts/validate-rite.sh` at `429d127` on 2026-08-14
- [x] E.2 `python3 --version` -> `Python 3.14.5`
- [x] E.3 Nothing could not be probed: none outstanding
- [x] E.4 Scope check: none noticed, no follow-ups

## 2. Simulation & Field Proof (MANDATORY)

- [x] S.1 `python3 hook.py < payload.json` -> `findings: 2` on the Portuguese path
- [x] S.2 Matrix: 10/10 defects caught, 6/6 correct cases silent, 4/4 known escapes silent
- [x] S.3 Nothing escaped that was not already documented

## 3. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate x --strict` -> valid
"""


def _seed(tmp: Path) -> Path:
    d = tmp / CHANGES / "selftest-change"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "tasks.md"
    p.write_text(_SCAFFOLD, encoding="utf-8")
    return p


def _break_e1(tmp: Path) -> None:
    p = _seed(tmp)
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- [x] E.1 Read `scripts/validate-rite.sh` at `429d127` on 2026-08-14",
        "- [x] E.1 Read the relevant files"), encoding="utf-8")


def _break_e2(tmp: Path) -> None:
    p = _seed(tmp)
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- [x] E.2 `python3 --version` -> `Python 3.14.5`",
        "- [x] E.2 Probed the tool versions"), encoding="utf-8")


def _break_e3(tmp: Path) -> None:
    p = _seed(tmp)
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- [x] E.3 Nothing could not be probed: none outstanding",
        "- [x] E.3 Checked"), encoding="utf-8")


def _break_e4(tmp: Path) -> None:
    p = _seed(tmp)
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- [x] E.4 Scope check: none noticed, no follow-ups",
        "- [x] E.4 Scope respected"), encoding="utf-8")


def _break_s1(tmp: Path) -> None:
    p = _seed(tmp)
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- [x] S.1 `python3 hook.py < payload.json` -> `findings: 2` on the Portuguese path",
        "- [x] S.1 Simulated the hook and it worked"), encoding="utf-8")


def _break_s2(tmp: Path) -> None:
    p = _seed(tmp)
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- [x] S.2 Matrix: 10/10 defects caught, 6/6 correct cases silent, 4/4 known escapes silent",
        "- [x] S.2 Every case in the matrix passed"), encoding="utf-8")


def _break_s3(tmp: Path) -> None:
    p = _seed(tmp)
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- [x] S.3 Nothing escaped that was not already documented",
        "- [x] S.3 Reviewed"), encoding="utf-8")


DEFECTS = (("R1 evidence shape: E.1", _break_e1),
           ("R1 evidence shape: E.2", _break_e2),
           ("R1 evidence shape: E.3", _break_e3),
           ("R1 evidence shape: E.4", _break_e4),
           ("R2 simulation shape: S.1", _break_s1),
           ("R2 simulation shape: S.2", _break_s2),
           ("R2 simulation shape: S.3", _break_s3))


def selftest() -> int:
    global findings, annotate
    annotate = False        # injected paths do not exist; see the note on `annotate`
    caught = 0
    for label, inject in DEFECTS:
        check, box = label.split(": ")
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "repo"
            shutil.copytree(ROOT, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            inject(tmp)
            findings = []
            for run in CHECKS:
                run(tmp)
            if any(f.startswith(check) and box in f for f in findings):
                print(f"  CAUGHT  {label}")
                caught += 1
            else:
                print(f"  MISSED  {label}   <-- the rule cannot fire")
    print(f"\n{caught}/{len(DEFECTS)} defect classes detected")
    return 0 if caught == len(DEFECTS) else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    for run in CHECKS:
        run(ROOT)
    print(f"  rite evidence gate: {len(findings)} findings")
    report_density(ROOT)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
