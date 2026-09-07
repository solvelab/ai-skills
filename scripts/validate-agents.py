#!/usr/bin/env python3
"""Catalog-wide agent validator.

Implements the mechanically checkable half of openspec/specs/agents-catalog:

  A1 frontmatter parses and carries every required field
  A2 name == file stem, 3-50 chars, lowercase/digits/hyphen, alphanumeric at both ends
  A3 description within 10-5000 characters
  A4 model and color from the accepted sets
  A5 tools declared explicitly, as a non-empty list of strings
  A6 body within 20-10000 characters and carrying a "When to invoke" section
  A7 no orphan agent in a generated tree, and the canonical directory is flat

WHAT THIS DOES NOT COVER, on purpose:
  - Whether the output contract in the body is honoured at run time. That is a judgement, and a
    judgement is not sold as a gate (skills/agent-delegation/SKILL.md).
  - Whether `tools` is actually minimal for the contract the body states. A5 proves the declaration
    exists, which is the difference between a stated privilege and an unstated one; that the set is
    the smallest possible is review-only.
  - The three admission tests. They are written per agent in README.md and read by a human.

The limits come from the agent format the harness documents, recorded in the add-agents-layer
change (E.2), not from an open specification: unlike skills, agents have no reference validator to
defer to. When the harness changes them, this file is where the change lands.

Exit 1 on any finding. Run from the repo root.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                  # reported as a skip, never as a pass
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
GENERATED = ROOT / "plugins"

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]$")
WHEN_TO_INVOKE = re.compile(r"^##+ +When to invoke *$", re.M | re.I)

REQUIRED = ("name", "description", "model", "color", "tools")
MODELS = {"inherit", "opus", "sonnet", "haiku"}
COLORS = {"blue", "cyan", "green", "yellow", "magenta", "red"}

DESCRIPTION_MIN, DESCRIPTION_MAX = 10, 5000
BODY_MIN, BODY_MAX = 20, 10000

findings: list[str] = []


def add(agent: str, check: str, msg: str) -> None:
    findings.append(f"{agent}\n   [{check}] {msg}")


def split(text: str) -> tuple[str | None, str]:
    """Frontmatter block and body. Returns (None, text) when there is no frontmatter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5:]


def check_file(path: Path) -> None:
    agent = path.stem
    text = path.read_text(encoding="utf-8")
    raw, body = split(text)

    if raw is None:
        add(agent, "A1 frontmatter", "no YAML frontmatter delimited by --- at the top of the file")
        return

    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError as exc:                    # noqa: BLE001 - the parser's message is the finding
        add(agent, "A1 frontmatter", f"YAML does not parse: {exc}")
        return
    if not isinstance(meta, dict):
        add(agent, "A1 frontmatter", "frontmatter is not a mapping")
        return

    for field in REQUIRED:
        if field not in meta:
            add(agent, "A1 frontmatter", f"missing `{field}` — required for every agent")

    name = meta.get("name")
    if name is not None:
        if name != agent:
            add(agent, "A2 name", f"`name: {name}` does not match the file name `{agent}.md`")
        if not isinstance(name, str) or not NAME_RE.match(name):
            add(agent, "A2 name", f"`{name}` is not 3-50 lowercase letters, digits and hyphens "
                                  "starting and ending alphanumeric")

    desc = meta.get("description")
    if desc is not None:
        if not isinstance(desc, str):
            add(agent, "A3 description", "description is not a string")
        elif not DESCRIPTION_MIN <= len(desc) <= DESCRIPTION_MAX:
            add(agent, "A3 description",
                f"{len(desc)} characters — the accepted range is "
                f"{DESCRIPTION_MIN}-{DESCRIPTION_MAX}")

    model = meta.get("model")
    if model is not None and model not in MODELS:
        add(agent, "A4 model/color", f"`model: {model}` is not one of {sorted(MODELS)}")
    color = meta.get("color")
    if color is not None and color not in COLORS:
        add(agent, "A4 model/color", f"`color: {color}` is not one of {sorted(COLORS)}")

    tools = meta.get("tools")
    if tools is not None:
        if not isinstance(tools, list) or not tools:
            add(agent, "A5 tools", "`tools` must be a non-empty list — omitting it grants every "
                                   "tool, so the declaration is the privilege")
        elif not all(isinstance(t, str) and t for t in tools):
            add(agent, "A5 tools", "every entry of `tools` must be a non-empty string")

    stripped = body.strip()
    if not BODY_MIN <= len(stripped) <= BODY_MAX:
        add(agent, "A6 body", f"{len(stripped)} characters — the accepted range is "
                              f"{BODY_MIN}-{BODY_MAX}")
    if not WHEN_TO_INVOKE.search(body):
        add(agent, "A6 body", "no `## When to invoke` section — a description routes to the agent, "
                              "this section tells the agent what the caller expected")


def check_layout() -> None:
    """A7 — the canonical directory is flat, and nothing is published without a source there.

    Flat because a subdirectory changes the name under which the agent is invoked. Orphan because an
    agent living only in a generated tree escapes this validator, the generator and the README while
    still installing for users — the same law scripts/validate-skills.py applies to wrapper skills.
    """
    for sub in sorted(p for p in AGENTS.iterdir() if p.is_dir()):
        add(sub.name, "A7 layout",
            f"agents/{sub.name}/ is a directory — the canonical directory is flat, because a "
            "subdirectory changes the name the agent is invoked under")

    canonical = {p.stem for p in AGENTS.glob("*.md")}
    for generated in sorted(GENERATED.glob("*/agents/*.md")):
        if generated.stem not in canonical:
            rel = generated.relative_to(ROOT)
            add(generated.stem, "A7 layout",
                f"{rel} has no source at agents/{generated.stem}.md — regenerate with "
                "./generate.sh, or delete it")


def main() -> int:
    if yaml is None:
        print("❌ PyYAML is not installed — the agent frontmatter cannot be parsed. "
              "This is a SKIPPED check, not a pass.", file=sys.stderr)
        return 1
    if not AGENTS.is_dir():
        print("agents/ not found — nothing to check.")
        return 0

    files = sorted(AGENTS.glob("*.md"))
    for path in files:
        check_file(path)
    check_layout()

    print(f"agents checked: {len(files)}   findings: {len(findings)}")
    if findings:
        print()
        for f in findings:
            print(f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
