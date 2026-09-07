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

HARDENED against the eight attacks the bug-hunter-analyst agent found against the first version
(issue #205). Two of them were false GREEN, not crashes: a required field declared null passed every
check, and a missing canonical directory returned before the orphan check ever ran. The rest were
unhandled exceptions on malformed input, an unbounded YAML alias expansion, an A7 that compared names
and not content, and a heading rule that rejected a tab a Markdown renderer accepts.

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

# `\Z`, not `$`: `$` matches BEFORE a final newline, so `name: "<50 chars>\n"` — a value of 51
# characters — used to satisfy a rule whose message promises 3-50 (measured 2026-09-07).
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]\Z")
# Spaces and tabs after the hashes, not any whitespace: `##\tWhen to invoke` is a heading every
# Markdown renderer accepts, and a gate that rejects what the tool accepts teaches the author to
# ignore the gate (issue #205, attack 8). `\s` was too wide — it includes `\n`, so `##` alone on its
# line with `When to invoke` in the paragraph below matched, and an agent with no heading at all
# passed A6 clean (reproduced 2026-09-07, issue #225 finding 1).
WHEN_TO_INVOKE = re.compile(r"^#{2,}[ \t]+When to invoke[ \t]*$", re.M | re.I)
# A heading inside a fenced block is not rendered as a heading, so it does not satisfy the rule
# either. The sibling validator already strips fences before its own citation scan; same construct,
# same treatment (issue #225, finding 2).
FENCE = re.compile(r"^([ \t]*)(`{3,}|~{3,}).*?^\1\2[ \t]*$", re.M | re.S)

if yaml is not None:
    class _NoAliasLoader(yaml.SafeLoader):
        """SafeLoader that refuses YAML anchors and aliases.

        `safe_load` blocks unsafe tag construction, not alias amplification: nested anchors doubling a
        list at each level expand exponentially and exhaust the runner (issue #205, attack 4). A size
        or time ceiling does not stop a small payload that expands hugely, and is machine-dependent.
        Agent frontmatter has no legitimate use for an anchor, so the class is removed instead of
        bounded.
        """

        def compose_node(self, parent, index):                 # noqa: D102 - PyYAML hook
            if self.check_event(yaml.events.AliasEvent):
                event = self.peek_event()
                raise yaml.YAMLError(
                    f"YAML alias `*{event.anchor}` is not accepted in agent frontmatter "
                    "(anchors and aliases are refused; write the value out)")
            return super().compose_node(parent, index)


REQUIRED = ("name", "description", "model", "color", "tools")
MODELS = {"inherit", "opus", "sonnet", "haiku"}
COLORS = {"blue", "cyan", "green", "yellow", "magenta", "red"}

DESCRIPTION_MIN, DESCRIPTION_MAX = 10, 5000
BODY_MIN, BODY_MAX = 20, 10000

findings: list[str] = []


def _printable(s: str) -> str:
    """Replace characters stdout cannot encode — a lone surrogate from a `\\uD800` escape in the
    frontmatter reaches here as a valid Python str and only fails at `print`, after the summary line
    is already out (issue #205, attack 5). Sanitising at the recording boundary covers every finding,
    present and future; sanitising at each interpolation covers only the sites that exist today."""
    return s.encode("utf-8", "replace").decode("utf-8", "replace")


def add(agent: str, check: str, msg: str) -> None:
    findings.append(_printable(f"{agent}\n   [{check}] {msg}"))


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
    if path.is_dir():
        # A directory carrying the .md suffix is a LAYOUT defect and A7 owns it; reporting it here
        # too would print two findings for one problem. Not silently skipped: A7's own scan sees
        # every directory under agents/ (issue #205, attack 3).
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError, PermissionError, OSError) as exc:
        # Bytes that are not UTF-8, a dangling symlink (which `is_file()` also rejects, so the guard
        # above must not be widened to it), an unreadable file: each was an unhandled exception that
        # ended the run and left every alphabetically later agent unchecked (issue #205, attack 6).
        add(agent, "A1 frontmatter",
            f"{path.relative_to(ROOT)} could not be read as UTF-8 text: "
            f"{type(exc).__name__}: {exc}")
        return
    raw, body = split(text)

    if raw is None:
        add(agent, "A1 frontmatter", "no YAML frontmatter delimited by --- at the top of the file")
        return

    try:
        meta = yaml.load(raw, Loader=_NoAliasLoader)
    except yaml.YAMLError as exc:                    # noqa: BLE001 - the parser's message is the finding
        add(agent, "A1 frontmatter", f"YAML does not parse: {exc}")
        return
    except RecursionError:
        # Raised by the parser, but NOT a subclass of YAMLError, so it used to escape the handler
        # above and end the run by traceback — 500 nested flow sequences in ~1 KB is enough
        # (reproduced 2026-09-07, issue #225 finding 2). Caught around the parse call only: a
        # RecursionError in our own checks is a defect and must still surface.
        add(agent, "A1 frontmatter",
            "YAML nesting exhausts the parser — the payload is small and its structure is not")
        return
    if not isinstance(meta, dict):
        add(agent, "A1 frontmatter", "frontmatter is not a mapping")
        return

    for field in REQUIRED:
        # Presence is a VALUE, not a key. `name:` with nothing after it, `~` and `null` all satisfy a
        # membership test while stating nothing, and every check below is guarded by `is not None` —
        # so an agent with all five fields null used to pass the whole gate clean. `tools: ~` was the
        # sharpest case: null is equivalent at run time to omitting it, which grants every tool
        # (issue #205, attack 1).
        if meta.get(field) is None:
            add(agent, "A1 frontmatter",
                f"missing `{field}` — required for every agent"
                f"{' (declared with no value, which states nothing)' if field in meta else ''}")

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

    # The shape is checked BEFORE the membership test, never around it: `model: [inherit]` used to
    # raise `TypeError: cannot use 'list' as a set element` and end the run, taking every
    # alphabetically later agent with it (reproduced 2026-09-07, issue #225 finding 3). Wrapping the
    # test in a handler instead would turn that crash into a silent pass for the field it owns.
    # `!!set` does not reach here: CPython converts an unhashable set key to a frozenset, so only a
    # list or a mapping ever did.
    for field, allowed in (("model", MODELS), ("color", COLORS)):
        value = meta.get(field)
        if value is None:
            continue
        if not isinstance(value, str):
            add(agent, "A4 model/color",
                f"`{field}` is a {type(value).__name__}, not one of {sorted(allowed)}")
        elif value not in allowed:
            add(agent, "A4 model/color", f"`{field}: {value}` is not one of {sorted(allowed)}")

    tools = meta.get("tools")
    if tools is not None:
        if not isinstance(tools, list) or not tools:
            add(agent, "A5 tools", "`tools` must be a non-empty list — omitting it grants every "
                                   "tool, so the declaration is the privilege")
        elif not all(isinstance(t, str) and t.strip() for t in tools):
            # `.strip()`: `"   "` is truthy, so three spaces used to pass as a tool name — a
            # privilege stated in form and absent in substance (issue #225, finding 11).
            add(agent, "A5 tools", "every entry of `tools` must be a non-blank string")

    stripped = body.strip()
    if not BODY_MIN <= len(stripped) <= BODY_MAX:
        add(agent, "A6 body", f"{len(stripped)} characters — the accepted range is "
                              f"{BODY_MIN}-{BODY_MAX}")
    if not WHEN_TO_INVOKE.search(FENCE.sub("", body)):
        add(agent, "A6 body", "no `## When to invoke` section — a description routes to the agent, "
                              "this section tells the agent what the caller expected")


def is_markdown(path: Path) -> bool:
    """Suffix comparison, case-folded.

    `glob("*.md")` is case-sensitive on the CI filesystem, so `agents/rogue.MD` holding anything at
    all used to be discovered by nothing and reported by nothing — exit 0, and the summary still said
    `agents checked: 1` (reproduced 2026-09-07, issue #225 finding 8). Discovery is the first gate:
    what it misses is unchecked, not approved.
    """
    return path.suffix.lower() == ".md"


def agent_files(directory: Path) -> list:
    """The canonical directory is flat by rule, so this stays one level deep on purpose.

    A subdirectory there is a finding of its own (A7 above), not a place to look for agents.

    Deliberately NOT filtered by `is_file()`: a dangling symlink and a directory carrying the suffix
    are exactly the malformed inputs A1 and A7 own, and `is_file()` is False for both — filtering
    here would make the gate accept them by never looking (the shape the old `glob("*.md")` had, and
    the one the self-test's dangling-symlink case pins).
    """
    return sorted(p for p in directory.iterdir() if is_markdown(p))


def check_layout() -> None:
    """A7 — the canonical directory is flat, nothing is published without a source there, and no
    generated copy has drifted from the source it claims.

    Flat because a subdirectory changes the name under which the agent is invoked. Orphan because an
    agent living only in a generated tree escapes this validator, the generator and the README while
    still installing for users — the same law scripts/validate-skills.py applies to wrapper skills.

    Runs even when `agents/` is absent: a missing canonical directory with generated copies still
    present is exactly the state this check owns, and the early return that used to skip it here made
    the one check that would catch that regression the one that never ran (issue #205, attack 2).

    Content, not just the name: `generate.sh` copies with `cp --no-preserve=mode`, so a published copy
    is byte-identical to its source. A copy that differs was hand-edited or left by a stale generator
    run, and is published content whose canonical source says something else (issue #205, attack 7).
    """
    if AGENTS.is_dir():
        for sub in sorted(p for p in AGENTS.iterdir() if p.is_dir()):
            add(sub.name, "A7 layout",
                f"agents/{sub.name}/ is a directory — the canonical directory is flat, because a "
                "subdirectory changes the name the agent is invoked under")

    canonical = {p.stem: p for p in agent_files(AGENTS) if p.is_file()} if AGENTS.is_dir() else {}
    for generated in sorted(GENERATED.glob("*/agents/**/*")):
        if not is_markdown(generated) or not generated.is_file():
            continue
        rel = generated.relative_to(ROOT)
        source = canonical.get(generated.stem)
        if source is None:
            add(generated.stem, "A7 layout",
                f"{rel} has no source at agents/{generated.stem}.md — regenerate with "
                "./generate.sh, or delete it")
            continue
        try:
            drifted = source.read_bytes() != generated.read_bytes()
        except OSError as exc:
            add(generated.stem, "A7 layout",
                f"{rel} could not be compared with its source: {type(exc).__name__}: {exc}")
            continue
        if drifted:
            add(generated.stem, "A7 layout",
                f"{rel} differs from its canonical source agents/{generated.stem}.md — the published "
                "copy has drifted; regenerate with ./generate.sh")


def main() -> int:
    if yaml is None:
        print("❌ PyYAML is not installed — the agent frontmatter cannot be parsed. "
              "This is a SKIPPED check, not a pass.", file=sys.stderr)
        return 1
    # No early return when agents/ is missing: check_layout() owns exactly that state (issue #205,
    # attack 2). A repository that legitimately publishes no agents still reports zero findings —
    # because the check ran, not because it was skipped.
    files = sorted(agent_files(AGENTS)) if AGENTS.is_dir() else []
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
