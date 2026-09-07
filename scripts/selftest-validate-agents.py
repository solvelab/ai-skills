#!/usr/bin/env python3
"""Self-test for scripts/validate-agents.py — the gate is itself gated.

A validator nobody tests is a validator that can start passing everything. This builds a throwaway
repository under a temporary directory, plants one defect at a time, and asserts that the check that
owns it fires — and, just as importantly, that a conforming agent produces zero findings.

Each case declares the check id it must provoke, so a defect detected by the WRONG check is a
failure here too: that is how a broad regex quietly starts covering for a rule it was never meant to.

Needs only python3 and PyYAML (which validate-agents.py itself needs). Run from anywhere.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REAL = Path(__file__).resolve().parent / "validate-agents.py"

GOOD = """---
name: {name}
description: >-
  Use this agent when a well formed example is needed. Typical triggers include the self-test of the
  validator and nothing else at all.
model: inherit
color: blue
tools: ["Read", "Grep"]
---

You are an example agent used only by the self-test.

## When to invoke

- **Never in real work.** This file exists so the validator has something valid to accept.
"""


def build(root: Path) -> None:
    (root / "scripts").mkdir(parents=True)
    shutil.copy2(REAL, root / "scripts" / "validate-agents.py")
    (root / "agents").mkdir()
    (root / "plugins").mkdir()
    (root / "agents" / "example-agent.md").write_text(GOOD.format(name="example-agent"),
                                                      encoding="utf-8")


def run(root: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(root / "scripts" / "validate-agents.py")],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def drop(field: str) -> str:
    """The good agent with one frontmatter line removed."""
    return "\n".join(l for l in GOOD.format(name="example-agent").splitlines()
                     if not l.startswith(f"{field}:")) + "\n"


def replace(old: str, new: str) -> str:
    return GOOD.format(name="example-agent").replace(old, new, 1)


# (label, expected check id, how to plant it)
CASES: list[tuple[str, str, object]] = [
    ("no frontmatter at all", "A1",
     lambda r: (r / "agents" / "example-agent.md").write_text("just a body\n", encoding="utf-8")),
    ("frontmatter that does not parse", "A1",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace("model: inherit", "model: inherit: broken"), encoding="utf-8")),
    ("missing name", "A1", lambda r: (r / "agents" / "example-agent.md").write_text(
        drop("name"), encoding="utf-8")),
    ("missing description", "A1", lambda r: (r / "agents" / "example-agent.md").write_text(
        "---\nname: example-agent\nmodel: inherit\ncolor: blue\ntools: [\"Read\"]\n---\n\n"
        "Body long enough to pass the body check comfortably.\n\n## When to invoke\n\n- **Never.**\n",
        encoding="utf-8")),
    ("missing model", "A1", lambda r: (r / "agents" / "example-agent.md").write_text(
        drop("model"), encoding="utf-8")),
    ("missing color", "A1", lambda r: (r / "agents" / "example-agent.md").write_text(
        drop("color"), encoding="utf-8")),
    ("missing tools", "A1", lambda r: (r / "agents" / "example-agent.md").write_text(
        drop("tools"), encoding="utf-8")),
    ("name does not match the file", "A2", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace("name: example-agent", "name: other-agent"), encoding="utf-8")),
    ("name with an illegal character", "A2",
     lambda r: (r / "agents" / "example_agent.md").write_text(
         GOOD.format(name="example_agent"), encoding="utf-8")),
    ("description too short", "A3", lambda r: (r / "agents" / "example-agent.md").write_text(
        "---\nname: example-agent\ndescription: short\nmodel: inherit\ncolor: blue\n"
        "tools: [\"Read\"]\n---\n\nBody long enough to pass the body check comfortably.\n\n"
        "## When to invoke\n\n- **Never.**\n", encoding="utf-8")),
    ("description too long", "A3", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace("the self-test of the\n  validator and nothing else at all.",
                "x " * 2600), encoding="utf-8")),
    ("unknown model", "A4", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace("model: inherit", "model: gpt-9"), encoding="utf-8")),
    ("unknown color", "A4", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace("color: blue", "color: taupe"), encoding="utf-8")),
    ("tools declared empty", "A5", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace('tools: ["Read", "Grep"]', "tools: []"), encoding="utf-8")),
    ("tools not a list", "A5", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace('tools: ["Read", "Grep"]', "tools: Read"), encoding="utf-8")),
    ("tools with a non-string entry", "A5", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace('tools: ["Read", "Grep"]', "tools: [Read, 7]"), encoding="utf-8")),
    ("body too short", "A6", lambda r: (r / "agents" / "example-agent.md").write_text(
        "---\nname: example-agent\ndescription: >-\n  Long enough description for the range check "
        "to accept it here.\nmodel: inherit\ncolor: blue\ntools: [\"Read\"]\n---\n\n"
        "## When to invoke\n", encoding="utf-8")),
    ("no When to invoke section", "A6", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace("## When to invoke", "## How to Use"), encoding="utf-8")),
    ("a subdirectory under agents/", "A7",
     lambda r: (r / "agents" / "grouped").mkdir()),
    ("an orphan in a generated tree", "A7", lambda r: (
        (r / "plugins" / "testing" / "agents").mkdir(parents=True),
        (r / "plugins" / "testing" / "agents" / "ghost.md").write_text(
            GOOD.format(name="ghost"), encoding="utf-8"))),

    # ── The eight attacks the bug-hunter-analyst agent found against the first version (issue #205).
    # Two of them were false GREEN, and those two are the reason this block exists: a gate that
    # crashes is loud, a gate that passes a bad agent is not.
    ("name declared with no value", "A1", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace("name: example-agent", "name:"), encoding="utf-8")),
    ("tools declared as an explicit null", "A1",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace('tools: ["Read", "Grep"]', "tools: ~"), encoding="utf-8")),
    ("description declared as null", "A1", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace("description: >-\n  Use this agent when a well formed example is needed. Typical "
                "triggers include the self-test of the\n  validator and nothing else at all.",
                "description: null"), encoding="utf-8")),
    ("a directory named like an agent file", "A7",
     lambda r: (r / "agents" / "ghost.md").mkdir()),
    ("bytes that are not UTF-8", "A1",
     lambda r: (r / "agents" / "broken.md").write_bytes(b"---\nname: broken\n\xff\xfe---\n")),
    ("a dangling symlink", "A1",
     lambda r: (r / "agents" / "dangling.md").symlink_to(r / "nowhere" / "missing.md")),
    ("a lone surrogate in name", "A2", lambda r: (r / "agents" / "example-agent.md").write_text(
        replace("name: example-agent", 'name: "\\uD800"'), encoding="utf-8")),
    ("a YAML anchor and alias in the frontmatter", "A1",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace('tools: ["Read", "Grep"]', "tools: &t [\"Read\"]\nextra: *t"), encoding="utf-8")),
    ("a generated copy that drifted from its source", "A7", lambda r: (
        (r / "plugins" / "testing" / "agents").mkdir(parents=True),
        (r / "plugins" / "testing" / "agents" / "example-agent.md").write_text(
            replace("color: blue", "color: red"), encoding="utf-8"))),
]


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"

        build(root)
        code, out = run(root)
        if code != 0 or "findings: 0" not in out:
            print(f"  FAIL   a conforming agent was rejected\n{out}")
            failures += 1
        else:
            print("  CLEAN  a conforming agent produces zero findings")

        for label, check, plant in CASES:
            shutil.rmtree(root)
            build(root)
            plant(root)
            code, out = run(root)
            if "Traceback (most recent call last)" in out:
                # A gate that ends by exception reports nothing about the inputs after the bad one.
                # Checked for every case, not only the ones we thought could crash (issue #205).
                print(f"  CRASH  {check}  {label}  — the validator raised instead of reporting:\n{out}")
                failures += 1
            elif code == 0:
                print(f"  MISSED {check}  {label}  — the validator accepted it")
                failures += 1
            elif f"[{check}" not in out:
                print(f"  WRONG  {check}  {label}  — detected, but by another check:\n{out}")
                failures += 1
            else:
                print(f"  OK     {check}  {label}")

        # A tab after the hashes is a heading every Markdown renderer accepts, so the gate accepts it
        # too (issue #205, attack 8). A gate that rejects what the tool accepts teaches the author to
        # ignore the gate.
        shutil.rmtree(root)
        build(root)
        (root / "agents" / "example-agent.md").write_text(
            replace("## When to invoke", "##\tWhen to invoke"), encoding="utf-8")
        code, out = run(root)
        if code != 0:
            print(f"  FAIL   A6  a tab after the heading hashes was rejected\n{out}")
            failures += 1
        else:
            print("  OK     A6  a tab after the heading hashes is accepted")

        # The canonical directory is gone and a generated copy is still published: the state A7 owns,
        # and the one the early return used to hide by never running the check (issue #205, attack 2).
        shutil.rmtree(root)
        build(root)
        (root / "plugins" / "testing" / "agents").mkdir(parents=True)
        shutil.copy2(root / "agents" / "example-agent.md",
                     root / "plugins" / "testing" / "agents" / "example-agent.md")
        shutil.rmtree(root / "agents")
        code, out = run(root)
        if code == 0 or "[A7" not in out:
            print(f"  MISSED A7  a missing canonical directory silenced the orphan check\n{out}")
            failures += 1
        else:
            print("  OK     A7  a missing canonical directory does not silence the orphan check")

        # A conforming generated copy is NOT an orphan: the same file with a source present passes.
        shutil.rmtree(root)
        build(root)
        (root / "plugins" / "testing" / "agents").mkdir(parents=True)
        shutil.copy2(root / "agents" / "example-agent.md",
                     root / "plugins" / "testing" / "agents" / "example-agent.md")
        code, out = run(root)
        if code != 0:
            print(f"  FAIL   a generated copy WITH a canonical source was called an orphan\n{out}")
            failures += 1
        else:
            print("  OK     A7  a generated copy with a source is not an orphan")

    total = len(CASES) + 4
    print(f"\n{total - failures}/{total} cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
