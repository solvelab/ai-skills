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


def sized(desc_len: int, body_len: int, name: str = "example-agent") -> str:
    """A conforming agent whose description and stripped body are EXACTLY the lengths asked for.

    The limits are the point: a suite that only ever produces 62, 133 or 163 characters proves that
    a limit fires and never where it sits, so moving the constant breaks nothing. Measured before
    this helper existed: the 33 cases produced body lengths 17, 85 and 163 only, and `BODY_MAX` had
    no witness at all (issue #225, findings 5 and 6).
    """
    # The gate measures `body.strip()`, so the length is built on the STRIPPED form. Measured on the
    # first version of this helper: asking for 19 produced 17 once stripped, which is why the mutant
    # `BODY_MIN = 20 -> 19` still survived a suite that looked like it had a witness there.
    head = "## When to invoke"                       # 17 characters
    if body_len >= 20:
        stripped = head + "\n\n" + "x" * (body_len - 19)
    elif body_len == 19:
        stripped = head + "\nx"
    else:
        stripped = "x" * body_len
    # The padding never ends in whitespace, or `.strip()` would give back a shorter body than asked.
    assert len(stripped) == body_len and stripped == stripped.strip(), (len(stripped), body_len)
    # No blank line between the frontmatter closer and the body: the body's first characters are the
    # heading itself, so an off-by-one in the frontmatter split shows up as a broken heading.
    return (f"---\nname: {name}\n"
            f'description: "{"d" * desc_len}"\n'
            "model: inherit\ncolor: blue\ntools: [\"Read\"]\n---\n" + stripped + "\n")


# (label, expected check id, how to plant it[, fragment the finding must carry])
#
# The fourth element is optional and is asserted IN ADDITION to the check id, never instead of it —
# a defect caught by the right message under the wrong check is still a defect. Use it wherever a
# check owns more than one message: without it, two paths through the same check are
# indistinguishable, which is what let four offset mutants survive the measurement in issue #225.
# Same shape as `scripts/selftest-validate-skills.py`, which reads its own optional element with
# `entry[2] if len(entry) > 2`; one idea, one format (issue #232).
CASES: list[tuple] = [
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
    # ── issue #225: the twelve findings of the #222 field proof ──────────────────────────────
    ("hashes alone on their line, heading text in the paragraph below", "A6",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace("## When to invoke", "##\nWhen to invoke"), encoding="utf-8")),
    ("the only invocation heading lives inside a fenced block", "A6",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace("## When to invoke", "## Something else\n\n```md\n## When to invoke\n```"),
         encoding="utf-8")),
    ("model declared as a sequence", "A4",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace("model: inherit", "model: [inherit]"), encoding="utf-8")),
    ("color declared as a mapping", "A4",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace("color: blue", "color: {a: b}"), encoding="utf-8")),
    ("frontmatter nested deeply enough to exhaust the parser", "A1",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace('tools: ["Read", "Grep"]', "tools: " + "[" * 500 + "]" * 500), encoding="utf-8")),
    ("a tools entry that is whitespace only", "A5",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace('tools: ["Read", "Grep"]', 'tools: ["Read", "   "]'), encoding="utf-8")),
    ("a canonical file whose suffix differs only in case", "A1",
     lambda r: (r / "agents" / "rogue.MD").write_text("garbage with no frontmatter\n",
                                                      encoding="utf-8")),
    ("an orphan nested below plugins/<group>/agents/", "A7", lambda r: (
        (r / "plugins" / "testing" / "agents" / "sub").mkdir(parents=True),
        (r / "plugins" / "testing" / "agents" / "sub" / "ghost.md").write_text(
            GOOD.format(name="ghost"), encoding="utf-8"))),
    ("a name whose value ends in a newline", "A2",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace("name: example-agent", 'name: "example-agent\n"'), encoding="utf-8")),
    ("a description one character under the minimum", "A3",
     lambda r: (r / "agents" / "example-agent.md").write_text(sized(9, 200), encoding="utf-8")),
    ("a description one character over the maximum", "A3",
     lambda r: (r / "agents" / "example-agent.md").write_text(sized(5001, 200), encoding="utf-8")),
    ("a body one character under the minimum", "A6",
     lambda r: (r / "agents" / "example-agent.md").write_text(sized(200, 19), encoding="utf-8")),
    ("a body one character over the maximum", "A6",
     lambda r: (r / "agents" / "example-agent.md").write_text(sized(200, 10001), encoding="utf-8")),
    # A name that sorts BEFORE the file stem. Every mismatch case in this suite happened to sort
    # after it, so `name != agent` and `name > agent` answered identically and the comparison had no
    # witness — found by reading the survivors of the mutation run, not by reading the code.
    ("a name that differs from the file stem and sorts before it", "A2",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         replace("name: example-agent", "name: aaa"), encoding="utf-8")),
    # ── The two documents that separate the frontmatter split offsets (issue #232) ───────────
    # Both are legitimate malformed inputs, and both are asserted BY MESSAGE. Asserting `[A1` alone
    # cannot tell these paths apart, which is exactly why four offset mutants survived the #225
    # measurement with the suite green.
    #
    # Delimiters present with nothing between them: from offset 4 the closing delimiter is NOT found,
    # so the finding is "no YAML frontmatter"; from the mutated offset 3 it IS found, the frontmatter
    # is empty, and the finding becomes "not a mapping". Measured 2026-09-07.
    ("frontmatter delimiters with nothing between them", "A1",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         "---\n---\n\nA body with no frontmatter fields at all, long enough to clear the minimum.\n"
         "\n## When to invoke\n\n- Never. This file exists for the self-test.\n", encoding="utf-8"),
     "no YAML frontmatter"),
    # Frontmatter opening with an empty line puts the closing delimiter at index 4 exactly, so it is
    # found from offset 4 ("not a mapping") and missed from the mutated offset 5 ("no YAML
    # frontmatter"). The document above cannot stand in for this one: from both 4 and 5 it misses.
    ("frontmatter that opens with an empty line", "A1",
     lambda r: (r / "agents" / "example-agent.md").write_text(
         "---\n\n---\n\n## When to invoke\n\n- Never. This file exists for the self-test, and "
         "carries enough body to clear the minimum.\n", encoding="utf-8"),
     "not a mapping"),
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

        for case in CASES:
            label, check, plant = case[0], case[1], case[2]
            fragment = case[3] if len(case) > 3 else ""
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
            elif fragment and fragment not in out:
                # The check fired, but by the other path through it. Print what WAS produced, so the
                # failure is readable without re-running the case by hand.
                print(f"  OTHER  {check}  {label}  — expected the finding to carry "
                      f"{fragment!r}, got:\n{out}")
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

        # ── issue #225 ── The accepting side of every limit. A rejected case one past the limit
        # proves the check fires; only a case AT the value proves where the limit sits. Without
        # these, moving a constant by one breaks no test — 20 of the 54 mutants that survived the
        # 2026-09-07 measurement sat exactly here.
        for label, text in (
            ("a description of exactly DESCRIPTION_MIN characters", sized(10, 200)),
            ("a description of exactly DESCRIPTION_MAX characters", sized(5000, 200)),
            ("a body of exactly BODY_MIN characters", sized(200, 20)),
            ("a body of exactly BODY_MAX characters", sized(200, 10000)),
        ):
            shutil.rmtree(root)
            build(root)
            (root / "agents" / "example-agent.md").write_text(text, encoding="utf-8")
            code, out = run(root)
            if code != 0:
                print(f"  FAIL   {label} was rejected\n{out}")
                failures += 1
            else:
                print(f"  OK     {label} is accepted")

        # A name of exactly 50 characters is legal; the file is renamed so `name != agent` cannot
        # mask the regex. The rejecting side (51) is covered by NAME_RE itself and by the
        # trailing-newline case in CASES.
        shutil.rmtree(root)
        build(root)
        long_name = "a" + "b" * 48 + "c"
        (root / "agents" / "example-agent.md").unlink()
        (root / "agents" / f"{long_name}.md").write_text(sized(200, 200, name=long_name),
                                                         encoding="utf-8")
        code, out = run(root)
        if code != 0:
            print(f"  FAIL   A2  a name of exactly 50 characters was rejected\n{out}")
            failures += 1
        else:
            print("  OK     A2  a name of exactly 50 characters is accepted")

        # ── issue #225, finding 12 ── The property every crash guard rests on: the run REACHES the
        # agent after the bad one. Every case above plants exactly one agent, so a gate that died on
        # the first input looked identical to one that judged it. This is what let the A4 crash stay
        # invisible through issue #205's hardening.
        shutil.rmtree(root)
        build(root)
        (root / "agents" / "example-agent.md").write_text(
            replace("model: inherit", "model: [inherit]"), encoding="utf-8")
        (root / "agents" / "zz-broken.md").write_text("no frontmatter at all\n", encoding="utf-8")
        code, out = run(root)
        if "Traceback (most recent call last)" in out:
            print(f"  CRASH  a defective first agent ended the run\n{out}")
            failures += 1
        elif "zz-broken" not in out:
            print(f"  MISSED the agent after the defective one was never checked\n{out}")
            failures += 1
        else:
            print("  OK     a defective agent does not hide the one after it")

    total = len(CASES) + 4 + 5 + 1
    print(f"\n{total - failures}/{total} cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
