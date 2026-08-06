"""Catalog-wide skill validator.

Implements the mechanically checkable half of openspec/specs/skills-authoring:

  C1 referenced repo paths exist            (links + inline paths inside skills/)
  C2 cross-skill references name a real skill
  C3 code blocks parse                      (bash -n, yaml, json, lua -p, python)
  C4 description agrees with body           (heuristic: absolute promise vs qualifying rule)
  C5 versioned external APIs are pinned     (code-heavy skill without a version statement)
  C6 fence tags match content               (a block tagged X that is obviously not X)
  C7 no orphan wrapper skills               (every generated skill has a canonical source)

Exit 1 on any finding. Run from the repo root.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
SKILLS = sorted(p for p in (ROOT / "skills").glob("*/SKILL.md"))
NAMES = {p.parent.name for p in SKILLS}

# capture the fence's own indentation so a block nested in a list is dedented before parsing
_FENCE_RE = re.compile(r"^([ \t]*)```(\w*)\n(.*?)^\1```", re.S | re.M)


class _Fence:
    """Yields (lang, dedented_body) pairs, like the old FENCE.findall()."""
    @staticmethod
    def findall(text: str):
        out = []
        for m in _FENCE_RE.finditer(text):
            indent, lang, body = m.group(1), m.group(2), m.group(3)
            if indent:
                body = "\n".join(l[len(indent):] if l.startswith(indent) else l
                                  for l in body.splitlines()) + "\n"
            out.append((lang, body))
        return out

    @staticmethod
    def sub(repl, text: str):
        return _FENCE_RE.sub(repl, text)


FENCE = _Fence()
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
INLINE = re.compile(r"`([^`\n]+)`")
PLACEHOLDER = re.compile(r"[*<>{}\[\]]|\.\.\.|YOUR|yourname|example\.com|\$\{")

# Ubuntu ships the compiler as luac5.4; brew/arch ship it as luac.
LUAC = next((c for c in ("luac", "luac5.4", "luac5.3") if shutil.which(c)), None)

findings: list[tuple[str, str, str]] = []          # (skill, check, message)


def add(skill: str, check: str, msg: str) -> None:
    findings.append((skill, check, msg))


def repo_has(rel: str) -> bool:
    rel = rel.removeprefix("./").strip("/")
    return (ROOT / rel).exists()


# ── C1/C2: references ─────────────────────────────────────────────────────
def check_refs(skill: str, path: Path, text: str) -> None:
    # A path inside a fenced block is example content, not a claim about this repo.
    text = FENCE.sub("", text)
    # a link inside an inline-code span is being shown AS an example of a link
    text = INLINE.sub(lambda m: "" if "](" in m.group(1) else m.group(0), text)
    # references/ is always relative to the skill directory, even when cited from a reference file
    base = path.parent if path.name == "SKILL.md" else path.parent.parent
    for m in LINK.finditer(text):
        t = m.group(1).split("#")[0]
        if not t or t.startswith(("http", "mailto:", "#")) or PLACEHOLDER.search(t):
            continue
        if not ((base / t).exists() or repo_has(t)):
            add(skill, "C1 missing path", f"link -> {t}")

    for m in INLINE.finditer(text):
        s = m.group(1).strip()
        if PLACEHOLDER.search(s) or " " in s or s.startswith(("~", "/", "$", "http")):
            continue
        # only judge paths that point inside this skill or into skills/
        if s.startswith("references/") or s.startswith("skills/"):
            if not ((base / s).exists() or repo_has(s)):
                add(skill, "C1 missing path", f"inline -> {s}")

    # cross-skill references: `skill-name` in backticks that looks like a skill slug
    for m in INLINE.finditer(text):
        s = m.group(1).strip()
        if re.fullmatch(r"[a-z][a-z0-9]+(-[a-z0-9]+)+", s) and s not in NAMES:
            # only flag when it really looks like a sibling reference, not a CLI flag or filename
            if "." not in s and "/" not in s and s.count("-") <= 3:
                looks_skillish = any(
                    s.startswith(p) for p in
                    ("r3f-", "fivem-", "openspec", "assettoserver-", "python-", "backend-",
                     "api-", "log-", "react-", "bug-", "helm-", "k8s-", "claude-", "conventional-")
                )
                ctx = text[max(0, m.start() - 90):m.end() + 40].lower()
                cited_as_skill = any(k in ctx for k in ("skill", "see also", "use ", "that is "))
                is_repo = any(k in ctx for k in ("repo", "repositor", "drivezone ("))
                if looks_skillish and cited_as_skill and not is_repo:
                    add(skill, "C2 unknown skill", f"`{s}` is not a skill in the catalog")


# ── C3: code blocks parse ─────────────────────────────────────────────────
def run(cmd: list[str], data: str | None = None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, input=data, capture_output=True, text=True, timeout=25)
        return p.returncode, (p.stderr or p.stdout).strip()
    except Exception as exc:                        # tool missing → skip, not a finding
        return -1, str(exc)


def check_blocks(skill: str, text: str) -> None:
    for i, (lang, body) in enumerate(FENCE.findall(text)):
        lang = lang.lower()
        if re.match(r"\s*(//|#|--)\s*excerpt", body) or PLACEHOLDER.search(body[:400]) and lang in ("bash", "sh"):
            continue
        if lang in ("bash", "sh", "shell"):
            if any(t in body for t in ("<", ">", "$(", "${", "…")):
                continue                             # templated command, not runnable as-is
            rc, err = run(["bash", "-n"], body)
            if rc > 0:
                add(skill, "C3 bash syntax", f"block#{i}: {err.splitlines()[0][:90]}")
        elif lang in ("yaml", "yml"):
            rc, err = run([sys.executable, "-c",
                           "import sys,yaml;list(yaml.safe_load_all(sys.stdin.read()))"], body)
            if rc > 0:
                add(skill, "C3 yaml parse", f"block#{i}: {err.splitlines()[-1][:90]}")
        elif lang == "json":
            try:
                json.loads(body)
            except Exception as exc:
                add(skill, "C3 json parse", f"block#{i}: {exc}")
        elif lang == "lua" and LUAC:
            with tempfile.NamedTemporaryFile("w", suffix=".lua", delete=False) as fh:
                fh.write(body); tmp = fh.name
            rc, err = run([LUAC, "-p", tmp])
            if rc > 0:
                add(skill, "C3 lua syntax", f"block#{i}: {err.splitlines()[0][:90]}")
        elif lang == "python":
            rc, err = run([sys.executable, "-c",
                           "import sys,ast;ast.parse(sys.stdin.read())"], body)
            if rc > 0:
                add(skill, "C3 python syntax", f"block#{i}: {err.splitlines()[-1][:90]}")


# ── C4: description agrees with body ──────────────────────────────────────
ABSOLUTE = re.compile(r"\b(ALWAYS creates?|ALWAYS generates?|ALWAYS produces?|always creates? all|"
                      r"all three \w+ tiers|creates? all \w+ (tiers|documents|files))\b", re.I)
QUALIFIER = re.compile(r"\b(only (when|if|what)|do not create|unless|earned|decision table|"
                       r"skip|when applicable|if (it |the )?applies)\b", re.I)


def check_description(skill: str, text: str) -> None:
    fm = text.split("---", 2)
    if len(fm) < 3:
        add(skill, "C4 frontmatter", "no frontmatter block")
        return
    desc = re.search(r"^description:\s*(.*?)(?=^\w+:)", fm[1], re.S | re.M)
    desc = desc.group(1) if desc else ""
    body = fm[2]
    promises = []
    for m in ABSOLUTE.finditer(desc):
        tail = desc[m.end():m.end() + 120]           # does the promise carry its own condition?
        if not re.search(r"\b(only when|only if|unless|when the|if the)\b", tail, re.I):
            promises.append(m.group(0))
    if promises and QUALIFIER.search(body):
        add(skill, "C4 desc vs body",
            f"description promises {promises[:2]} while the body qualifies it")


# ── C5: versioned APIs pinned ─────────────────────────────────────────────
# A pin is any concrete "this was checked against version X" statement, in prose or in a fence.
PIN = re.compile(r"[Vv]erified against|[Mm]easured on|[Pp]robed on|version[s]? pinned"
                 r"|@[\d]+\.[\d]+|targets? v?\d+\.\d+"
                 r"|\b(?:runtime|tag|CLI|preset)\s+v?\d+\.\d+"
                 r"|pydantic v\d|SQLAlchemy \d|Python .{0,3}\d\.\d+|\b\w+ \d+\.\d+")
API_HINT = re.compile(r"@react-three|@react-spring|fastapi|pydantic|sqlalchemy|helm |kubectl|"
                      r"citizenfx|Qmmands|AssettoServer|openspec|gh project|zod|vite", re.I)


def check_pin(skill: str, text: str) -> None:
    """KNOWN LIMIT: only fires on skills carrying 40+ lines of fenced code. A skill that makes
    the same versioned claims in prose (config keys, CLI flags, API names in bullets) escapes
    this check and must be reviewed by hand. Widening the trigger produced false positives on
    every skill that merely names a tool, so the gap is stated instead of guessed at."""
    blocks = FENCE.findall(text)
    code_lines = sum(len(b.splitlines()) for _, b in blocks)
    if code_lines < 40:
        return
    defers = re.search(r"source of truth, not this skill|read the local copy first", text, re.I)
    if API_HINT.search(text) and not PIN.search(text) and not defers:
        add(skill, "C5 no version pin",
            f"{code_lines} lines of code against a versioned API, no version statement")


# ── C6: fence tag matches content ─────────────────────────────────────────
def check_tags(skill: str, text: str) -> None:
    for i, (lang, body) in enumerate(FENCE.findall(text)):
        head = next((l for l in body.splitlines() if l.strip()), "")
        if lang in ("tsx", "ts", "jsx", "javascript"):
            if re.match(r"^\s*(varying|uniform|attribute|precision)\s+\w", head):
                add(skill, "C6 wrong tag", f"block#{i} tagged {lang} but looks like GLSL")
            if (re.match(r"^[\w\s,#.\-]+\{\s*$", head)
                    and not re.match(r"^\s*(import|export|const|let|var|return|type|interface)\b", head)
                    and "function" not in head and "=>" not in head):
                add(skill, "C6 wrong tag", f"block#{i} tagged {lang} but looks like CSS")
        if lang in ("yaml", "yml") and head.strip().startswith(("{", "[")):
            add(skill, "C6 wrong tag", f"block#{i} tagged {lang} but looks like JSON")


# ── C7: no orphan wrapper skills ──────────────────────────────────────────
def check_orphans() -> None:
    """A skill living only in a generated tree is outside generate.sh, outside the
    frontmatter check, outside this validator, and absent from the README."""
    for tree in ("claude/skills", "codex/skills"):
        base = ROOT / tree
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            if d.is_dir() and d.name not in NAMES:
                add(d.name, "C7 orphan wrapper",
                    f"{tree}/{d.name} has no canonical skills/{d.name}/SKILL.md")


def main() -> int:
    check_orphans()
    for p in SKILLS:
        skill = p.parent.name
        text = p.read_text(encoding="utf-8")
        check_refs(skill, p, text)
        check_blocks(skill, text)
        check_description(skill, text)
        check_pin(skill, text)
        check_tags(skill, text)
        for ref in (p.parent / "references").glob("*.md"):
            rtext = ref.read_text(encoding="utf-8")
            check_refs(f"{skill}/{ref.name}", ref, rtext)
            check_blocks(f"{skill}/{ref.name}", rtext)

    by_check: dict[str, int] = {}
    for _, c, _ in findings:
        by_check[c] = by_check.get(c, 0) + 1
    skipped = []
    if not LUAC:
        skipped.append("lua syntax (luac not installed)")
    try:
        import yaml  # noqa: F401
    except ImportError:
        skipped.append("yaml parse (PyYAML not installed)")
    print(f"skills checked: {len(SKILLS)}   findings: {len(findings)}")
    if skipped:
        print("  checks skipped: " + "; ".join(skipped))
    for c, n in sorted(by_check.items(), key=lambda x: -x[1]):
        print(f"  {c:<22} {n}")
    print()
    cur = None
    for skill, check, msg in sorted(findings):
        if skill != cur:
            print(f"\n{skill}"); cur = skill
        print(f"   [{check}] {msg}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
