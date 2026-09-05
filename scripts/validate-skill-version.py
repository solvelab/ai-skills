#!/usr/bin/env python3
"""Skill-version gate — a pull request that edits a skill moves that skill's metadata.version.

README.md promises every skill a version of its own: "bump it when that skill's behavior changes.
Repo version = the collection; skill version = the individual contract." Until issue #119 nothing
measured the second half of that sentence. The frontmatter step in ci.yml checks that the field is
present and looks like semver; no gate read its value. Measured on the history: 49 of 165
(commit, skill) pairs that edited skill content left the version where it was, 42 of them from four
catalog-wide sweeps — commit cf767ee alone touched 12 existing skills and bumped none.

This gate reads the diff against the base, the way validate-spec-rite.py does, and asks per skill:

  V1 a skill with changed content has a metadata.version on HEAD that is semver-greater than on the
     base, or the pull request body carries ONE line `Skill-version: none — <reason>` covering the
     whole diff (a catalog-wide sweep costs one line, not one per skill)
  V2 a metadata.version never moves backwards — a lower number is an editing error, and no reason
     makes it right, so the waiver does not cover it
  V3 the waiver names a usable reason (the same minimum length as the spec-rite waiver, imported
     from that script so the two can never drift apart)

What counts as "changed content": any path under skills/<x>/ in the diff — the SKILL.md body, a
references/ file, anything the skill owns — except a SKILL.md whose only difference is the
`  version:` line itself. A skill with no SKILL.md on the base is new and has nothing to move from.
A skill with no SKILL.md on HEAD was removed, which skills-catalog regulates, not this. The generated
trees (claude/ codex/ cursor/ copilot/ plugins/) are never counted: they are generate.sh output with
a gate of their own.

KNOWN LIMIT: this proves that the number MOVED, not that it moved by the right amount (a patch bump
on a breaking rewrite passes) and not that a waiver's reason is honest (any eight characters pass
V3). Both stay with the review; the gate makes them a required, visible artifact. Semver is compared
on the (major, minor, patch) tuple the frontmatter step already requires, so a change confined to a
pre-release suffix reads as "did not move" — no skill in the catalog carries one. A rename or a
whitespace-only edit is a content change here, accepted on issue #119: the written waiver is the exit,
and the finding names it. The selftest exercises the decision rules against synthetic inputs, not the
git plumbing that feeds them: a misconfigured checkout is caught by the CI-only base-resolution
failure below, not by the selftest. The one plumbing probe it does run is the path reader, below.

Paths are read with `git diff --name-only -z` and split on NUL. Without `-z`, git wraps any path that
carries a non-ASCII, control or quote character in double quotes with octal escapes (core.quotePath,
default true on a fresh checkout and on the ubuntu runners), `"skills/x/caf\303\251.md"` no longer
starts with `skills/` and the skill vanishes from the measurement — the gate approved a fixture like
that in the review of issue #119. The selftest commits such a path in a throwaway repository and
asserts the reader hands it back verbatim, so the flag cannot be dropped silently.

The pull request body is read from the event payload the runner already writes (GITHUB_EVENT_PATH),
never from a step's `env:` block, for the reason validate-spec-rite.py records: Actions prints that
block into the build log. PR_BODY survives as the deliberate override for running this outside CI.

Exit 1 on any finding. Run from the repo root.
Modes: (default) check this diff   |   --selftest inject one defect per rule and assert detection.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = "skills"

# The waiver is authored by whoever opened the pull request, including from a fork. It is matched as
# text and never executed, never interpolated into a command. Anchored to the start of a line so a
# mention of the syntax inside a sentence does not silently waive the gate. Same shape, same
# separators and same prefix tolerance as the spec-rite waiver, so a body that carries both lines
# reads as two entries of one list.
WAIVER = re.compile(
    r"^[ \t>*-]*Skill-version:[ \t]*none[ \t]*(?:—|--|–|-)[ \t]*(?P<reason>.*\S)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
WAIVER_NO_REASON = re.compile(
    r"^[ \t>*-]*Skill-version:[ \t]*none[ \t]*(?:(?:—|--|–|-)[ \t]*)?$",
    re.IGNORECASE | re.MULTILINE,
)

VERSION_LINE = re.compile(r"^  version:[ \t]*(?P<value>\S+)[ \t]*$", re.MULTILINE)
SEMVER = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)")


def _sibling_min_reason() -> int:
    """MIN_REASON as validate-spec-rite.py defines it — imported, not copied, so the two waivers
    demand the same reason length by construction. The module name carries a hyphen, hence the
    spec-from-file dance instead of a plain import."""
    path = Path(__file__).resolve().parent / "validate-spec-rite.py"
    spec = importlib.util.spec_from_file_location("validate_spec_rite", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # Registered before exec: a module loaded this way is otherwise absent from sys.modules, and on
    # Python 3.14 a @dataclass in such a module fails at class creation (dataclasses resolves
    # annotations through sys.modules[cls.__module__]). Same rule applies to whoever imports THIS
    # file the same way — the simulation on issue #119 hit it first.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return int(module.MIN_REASON)


MIN_REASON = _sibling_min_reason()

findings: list[str] = []

# GitHub turns `::error` into a red annotation on the pull request. During --selftest the findings
# are injected on purpose, so annotating them would put bogus failures on a PR whose job passed —
# the defect the evidence gate hit on run 31790712710.
annotate = True


def add(check: str, detail: str) -> None:
    findings.append(f"{check}: {detail}")
    if annotate:
        print(f"::error::{check} — {detail}")
    else:
        print(f"    injected: {check} — {detail}")


# ── inputs ────────────────────────────────────────────────────────────────
def resolve_base(root: Path) -> str | None:
    """The revision this branch is measured against, or None when there is nothing to compare to."""
    candidates = []
    for env in ("SKILL_VERSION_BASE", "GITHUB_BASE_REF"):
        ref = os.environ.get(env, "").strip()
        if ref:
            candidates += [f"origin/{ref}", ref]
    candidates += ["origin/master", "origin/main"]
    for ref in candidates:
        probe = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"],
                               capture_output=True, text=True)
        if probe.returncode == 0:
            return ref
    return None


def read_pr_body() -> str:
    """The pull request body, without routing it through anything that echoes it.

    Precedence: PR_BODY when set (local runs and the end-to-end probes of this gate); otherwise
    pull_request.body from the file at GITHUB_EVENT_PATH; otherwise empty. A payload that is
    missing, unreadable or without the key degrades to an empty body rather than an error, so the
    decision falls to the rules that exist instead of the build failing for an unrelated reason.
    """
    override = os.environ.get("PR_BODY")
    if override is not None:
        return override

    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path:
        return ""
    try:
        with open(event_path, encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"  skill-version gate: event payload unreadable ({exc.__class__.__name__}) — "
              "continuing with an empty body")
        return ""
    body = (payload.get("pull_request") or {}).get("body")
    return body if isinstance(body, str) else ""


def split_nul_paths(out: str) -> list[str]:
    """`git diff --name-only -z` output -> paths, verbatim. NUL is the one byte a path cannot contain,
    so nothing here is quoted, escaped or split on a newline inside a name."""
    return [p for p in out.split("\0") if p]


def changed_paths(root: Path, base: str, head: str = "HEAD") -> list[str]:
    # -z: raw names separated by NUL. The default line mode quotes and octal-escapes any name with a
    # non-ASCII, control or quote character, which skills_in() would then fail to recognise.
    out = subprocess.run(["git", "-C", str(root), "diff", "--name-only", "-z", f"{base}...{head}"],
                         capture_output=True, text=True, check=True).stdout
    return split_nul_paths(out)


def merge_base(root: Path, base: str, head: str = "HEAD") -> str:
    """`git diff A...B` measures from the merge base; the blobs must be read from that same commit."""
    return subprocess.run(["git", "-C", str(root), "merge-base", base, head],
                          capture_output=True, text=True, check=True).stdout.strip()


def blob(root: Path, rev: str, path: str) -> str | None:
    """The file at `rev`, or None when it does not exist there."""
    proc = subprocess.run(["git", "-C", str(root), "show", f"{rev}:{path}"],
                          capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else None


# ── the per-skill record the rules read ───────────────────────────────────
@dataclass(frozen=True)
class SkillDiff:
    name: str
    paths: tuple[str, ...]          # the changed paths under skills/<name>/
    base_version: str | None        # None: no SKILL.md on the base (new skill)
    head_version: str | None        # None: no SKILL.md on HEAD (removed skill)
    content_changed: bool           # anything beyond the `  version:` line moved


def version_of(text: str | None) -> str | None:
    if text is None:
        return None
    m = VERSION_LINE.search(text)
    return m.group("value") if m else None


def strip_version_line(text: str) -> str:
    return VERSION_LINE.sub("", text)


def semver_key(value: str | None) -> tuple[int, int, int] | None:
    if value is None:
        return None
    m = SEMVER.match(value)
    if not m:
        return None
    return int(m.group("major")), int(m.group("minor")), int(m.group("patch"))


def skills_in(paths: list[str]) -> dict[str, list[str]]:
    """Changed paths grouped by skill — only the canonical tree, never the generated mirrors."""
    per: dict[str, list[str]] = {}
    for p in paths:
        parts = p.split("/")
        if len(parts) >= 3 and parts[0] == SKILLS:
            per.setdefault(parts[1], []).append(p)
    return per


def collect(root: Path, base: str, head: str = "HEAD") -> list[SkillDiff]:
    """Read the diff into one record per touched skill — this is the git plumbing evaluate() never sees.

    `head` is HEAD in every real run; the parameter exists so the gate can be pointed at a historical
    commit and measured against what actually shipped (the simulation on issue #119 did exactly that).
    """
    mb = merge_base(root, base, head)
    out: list[SkillDiff] = []
    for name, paths in sorted(skills_in(changed_paths(root, base, head)).items()):
        skill_md = f"{SKILLS}/{name}/SKILL.md"
        base_text = blob(root, mb, skill_md)
        head_text = blob(root, head, skill_md)
        if any(p != skill_md for p in paths):
            content_changed = True
        elif base_text is None or head_text is None:
            content_changed = True
        else:
            content_changed = strip_version_line(base_text) != strip_version_line(head_text)
        out.append(SkillDiff(name, tuple(paths), version_of(base_text), version_of(head_text),
                             content_changed))
    return out


# ── rules ─────────────────────────────────────────────────────────────────
def waiver_reason(pr_body: str) -> str | None:
    m = WAIVER.search(pr_body or "")
    return m.group("reason").strip() if m else None


def moved_up(s: SkillDiff) -> bool:
    """HEAD is semver-greater than the base. An unparseable value on either side is not a move."""
    b, h = semver_key(s.base_version), semver_key(s.head_version)
    return b is not None and h is not None and h > b


def evaluate(skills: list[SkillDiff], pr_body: str) -> None:
    """The whole decision, as a pure function of its inputs — this is what --selftest exercises."""
    # V2 first and unconditionally: a regression is a finding whether or not the body waives the bump.
    for s in skills:
        b, h = semver_key(s.base_version), semver_key(s.head_version)
        if b is not None and h is not None and h < b:
            add("V2 version moved backwards",
                f"{SKILLS}/{s.name}/SKILL.md metadata.version went from {s.base_version} (base) to "
                f"{s.head_version} (HEAD). A version never goes down; restore it above "
                f"{s.base_version}. A `Skill-version: none` line does not cover this")

    # New skill (no base), removed skill (no head), and version-only edits are out of the bump rule.
    owed = [s for s in skills
            if s.content_changed and s.base_version is not None and s.head_version is not None
            and not moved_up(s)]
    if not owed:
        return

    reason = waiver_reason(pr_body)
    if reason is not None:
        if len(reason) < MIN_REASON:
            add("V3 waiver reason", f"the waiver names no usable reason ({reason!r}) — write "
                                    "`Skill-version: none — <why these skill edits deserve no bump>`")
        return
    if WAIVER_NO_REASON.search(pr_body or ""):
        add("V3 waiver reason", "the pull request body carries `Skill-version: none` with no reason — "
                                "write `Skill-version: none — <why these skill edits deserve no bump>`")
        return

    for s in owed:
        # A regression already produced V2 above; do not also ask for a bump it cannot satisfy.
        b, h = semver_key(s.base_version), semver_key(s.head_version)
        if b is not None and h is not None and h < b:
            continue
        sample = ", ".join(s.paths[:3]) + (f" (+{len(s.paths) - 3} more)" if len(s.paths) > 3 else "")
        add("V1 unbumped skill",
            f"{SKILLS}/{s.name}/ changed {len(s.paths)} path(s) — {sample} — with metadata.version "
            f"{s.base_version} on the base and {s.head_version} on HEAD. Either raise `  version:` in "
            f"{SKILLS}/{s.name}/SKILL.md above {s.base_version}, or add one line "
            "`Skill-version: none — <reason>` to the pull request body (it covers every skill in this diff)")


# ── selftest ──────────────────────────────────────────────────────────────
def _skill(name: str = "backlog", base: str | None = "1.5.0", head: str | None = "1.5.0",
           content: bool = True, paths: tuple[str, ...] = ("skills/backlog/SKILL.md",)) -> SkillDiff:
    return SkillDiff(name, paths, base, head, content)


# One injected defect per rule, plus the false-positive cases the rules must stay silent on. The
# wrapper-only case is expressed the way collect() would hand it over: no SkillDiff at all, because
# skills_in() drops every path outside skills/.
DEFECTS = [
    ("V1 unbumped skill", ([_skill()], "")),
    ("V1 unbumped skill", ([_skill(paths=("skills/backlog/references/issue-template.md",))], "")),
    ("V1 unbumped skill", ([_skill()], "see the Skill-version: none — reason line elsewhere")),
    ("V2 version moved backwards", ([_skill(base="1.8.0", head="1.7.0")], "")),
    ("V2 version moved backwards", ([_skill(base="1.8.0", head="1.7.0")],
                                    "Skill-version: none — typo fix in one sentence")),
    ("V3 waiver reason", ([_skill()], "Skill-version: none — x")),
    ("V3 waiver reason", ([_skill()], "Skill-version: none")),
]

SILENT = [
    ("edited with a bump", ([_skill(head="1.5.1")], "")),
    ("edited with a minor bump", ([_skill(head="1.6.0")], "")),
    ("edited with a waiver", ([_skill()], "Skill-version: none — cross-reference line added")),
    ("twelve skills, one waiver",
     ([_skill(name=f"skill-{i}", paths=(f"skills/skill-{i}/SKILL.md",)) for i in range(12)],
      "Closes #119\n\nSpec-rite: some-change\n- Skill-version: none — cross-reference line added to each\n")),
    ("new skill", ([_skill(base=None, head="1.0.0")], "")),
    ("removed skill", ([_skill(base="1.5.0", head=None)], "")),
    ("version-only edit", ([_skill(head="1.5.1", content=False)], "")),
    # Expressed the way collect() hands it over: skills_in() drops every path outside skills/, so a
    # diff confined to the generated trees yields no SkillDiff at all.
    ("wrapper-only diff", (list(skills_in(["claude/skills/backlog/SKILL.md",
                                           "plugins/workflow/skills/backlog/SKILL.md"]).values()), "")),
    ("no skill touched", ([], "")),
    ("waiver quoted in a list item", ([_skill()], "- Skill-version: none — whitespace-only reflow")),
    ("bump beside an unrelated spec-rite waiver",
     ([_skill(head="1.5.1")], "Spec-rite: none — README only")),
]


def _probe_quoted_path() -> bool:
    """The one git-plumbing probe of the selftest: commit a path git would quote in line mode and
    check changed_paths() hands it back unquoted. core.quotePath is forced on so the probe measures
    the worst case whatever the box's config says. Same input the review of issue #119 used."""
    import tempfile
    name = "skills/probe/references/caf\u00e9.md"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@localhost",
               "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@localhost"}

        def git(*args: str) -> None:
            subprocess.run(["git", "-C", tmp, "-c", "core.quotePath=true", *args],
                           capture_output=True, text=True, check=True, env=env)

        git("init", "-q", "-b", "main")
        (root / "skills/probe").mkdir(parents=True)
        (root / "skills/probe/SKILL.md").write_text("---\n  version: 1.0.0\n---\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        (root / "skills/probe/references").mkdir()
        (root / name).write_text("x\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "edit")
        return changed_paths(root, "HEAD^") == [name] and list(skills_in(changed_paths(root, "HEAD^"))) == ["probe"]


def selftest_collect_helpers() -> tuple[int, int]:
    """The parsers collect() relies on, exercised on literal text: a wrong VERSION_LINE regex would
    make every skill read as new, and evaluate() would stay silent on everything."""
    cases = [
        ("version parsed from frontmatter",
         version_of("---\nname: x\nmetadata:\n  author: solvelab\n  version: 1.8.0\n---\n") == "1.8.0"),
        ("no version line reads as None", version_of("---\nname: x\n---\n") is None),
        ("version-only edit compares equal",
         strip_version_line("a\n  version: 1.0.0\nb\n") == strip_version_line("a\n  version: 1.0.1\nb\n")),
        ("body edit compares different",
         strip_version_line("a\n  version: 1.0.0\nb\n") != strip_version_line("a\n  version: 1.0.1\nc\n")),
        ("semver orders numerically, not lexically", semver_key("1.10.0") > semver_key("1.9.0")),
        ("generated trees are dropped",
         skills_in(["claude/skills/x/SKILL.md", "plugins/g/skills/x/SKILL.md", "skills/y/SKILL.md"]) == {"y": ["skills/y/SKILL.md"]}),
        ("references group under their skill",
         skills_in(["skills/y/references/a.md", "skills/y/SKILL.md"]) == {"y": ["skills/y/references/a.md", "skills/y/SKILL.md"]}),
        ("MIN_REASON agrees with the spec-rite gate", MIN_REASON == _sibling_min_reason()),
        ("NUL-separated names are read verbatim, quotes and newlines included",
         split_nul_paths('skills/y/SKILL.md\0skills/y/references/caf\u00e9 "x"\n.md\0')
         == ["skills/y/SKILL.md", 'skills/y/references/caf\u00e9 "x"\n.md']),
        ("a non-ASCII name still groups under its skill",
         skills_in(["skills/y/references/caf\u00e9.md"]) == {"y": ["skills/y/references/caf\u00e9.md"]}),
        ("changed_paths() survives core.quotePath on a real repository", _probe_quoted_path()),
    ]
    ok = 0
    for label, passed in cases:
        print(f"  {'HELPER' if passed else 'HELPER FAIL'}  {label}")
        ok += bool(passed)
    return ok, len(cases)


def selftest() -> int:
    global findings, annotate
    annotate = False
    caught = 0
    for label, (skills, body) in DEFECTS:
        findings = []
        evaluate(skills, body)
        if any(f.startswith(label) for f in findings):
            print(f"  CAUGHT  {label}: {body!r}")
            caught += 1
        else:
            print(f"  MISSED  {label}: {body!r}   <-- the rule cannot fire")

    quiet = 0
    for label, (skills, body) in SILENT:
        findings = []
        evaluate(skills, body)
        if findings:
            print(f"  FALSE POSITIVE  {label}   <-- {findings[0]}")
        else:
            print(f"  SILENT  {label}")
            quiet += 1

    helpers_ok, helpers_total = selftest_collect_helpers()

    print(f"\n{caught}/{len(DEFECTS)} defect classes detected, "
          f"{quiet}/{len(SILENT)} false-positive cases stayed silent, "
          f"{helpers_ok}/{helpers_total} helper cases correct")
    return 0 if (caught == len(DEFECTS) and quiet == len(SILENT)
                 and helpers_ok == helpers_total) else 1


# ── main ──────────────────────────────────────────────────────────────────
def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()

    event = os.environ.get("GITHUB_EVENT_NAME", "")
    in_ci = os.environ.get("GITHUB_ACTIONS", "") == "true"
    if in_ci and event and event != "pull_request":
        print(f"  skill-version gate: skipped (event {event}, not pull_request)")
        return 0

    base = resolve_base(ROOT)
    if base is None:
        # A gate that cannot measure must not approve. In CI an unresolvable base means the checkout
        # was not given enough history (fetch-depth), which is a misconfiguration, not an exemption.
        if in_ci:
            add("V0 base revision", "no base revision to diff against — the checkout needs "
                                    "`fetch-depth: 0` for this gate to measure anything")
            return 1
        print("  skill-version gate: skipped (no base revision to diff against)")
        return 0

    skills = collect(ROOT, base)
    evaluate(skills, read_pr_body())
    print(f"  skill-version gate: {len(findings)} findings "
          f"(base {base}, {len(skills)} skill(s) changed, "
          f"{sum(s.content_changed for s in skills)} with content changes)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
