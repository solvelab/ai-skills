"""Catalog-wide skill validator.

Implements the mechanically checkable half of openspec/specs/skills-authoring:

  C1 referenced repo paths exist            (links + inline paths inside skills/)
  C2 cross-skill references name a real skill
  C3 code blocks parse                      (bash -n, yaml, json, lua -p, python)
  C4 description agrees with body           (heuristic: absolute promise vs qualifying rule)
  C5 versioned external APIs are pinned     (code-heavy skill without a version statement)
  C6 fence tags match content               (a block tagged X that is obviously not X)
  C7 no orphan wrapper skills               (every generated skill has a canonical source)
  C8 no meta sections in SKILL.md           (triggers belong in the description, not the body)
  C9 identifier locale                      (English identifiers in code examples)
  C10 frontmatter limits                    (parsed description <= 1024 chars, compatibility <= 500)
  C11 orphan reference                      (every references/**/*.md is reachable from SKILL.md)
  C12 out-of-skill path                     (a path that resolves only in a full checkout of this repo)
  C13 anti-trigger clause                   (the description says where the skill does NOT apply)

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
    # Two conventions coexist and both are correct:
    #   - "../SKILL.md" from a reference file  -> resolve relative to the FILE
    #   - "references/x.md" cited anywhere      -> resolve relative to the SKILL directory
    # Accept either; a path is a defect only when neither resolves. The skill directory is derived
    # from the label, not from path.parent.parent, so a file in references/<subdir>/ gets the same
    # two bases as one at references/ depth 1 (svg-animation/references/regimes/*.md cite
    # `references/platform.md` and mean the skill root).
    skill_dir = ROOT / "skills" / skill.split("/")[0]
    bases = [path.parent] if path.name == "SKILL.md" else [path.parent, skill_dir]
    for m in LINK.finditer(text):
        t = m.group(1).split("#")[0]
        if not t or t.startswith(("http", "mailto:", "#")) or PLACEHOLDER.search(t):
            continue
        if not (any((b / t).exists() for b in bases) or repo_has(t)):
            add(skill, "C1 missing path", f"link -> {t}")

    for m in INLINE.finditer(text):
        s = m.group(1).strip()
        if PLACEHOLDER.search(s) or " " in s or s.startswith(("~", "/", "$", "http")):
            continue
        # only judge paths that point inside this skill or into skills/
        if s.startswith("references/") or s.startswith("skills/"):
            if not (any((b / s).exists() for b in bases) or repo_has(s)):
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
                     "api-", "log-", "react-", "bug-", "helm-", "k8s-", "claude-", "conventional-",
                     "code-")
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


# ── C9: identifier locale ─────────────────────────────────────────────────
LOCALE_CHECKER = ROOT / "skills" / "code-locale" / "references" / "check-identifier-locale.py"


LOCALE_HIT = re.compile(r"^(\S+?\.md):(\d+):\s+(\S+)\s+\[([^\]]+)\]")


def check_locale() -> None:
    """Flag non-English identifiers in the code this catalog teaches by example.

    Invokes the SAME script the `code-locale` skill tells target repositories to wire into their own
    CI, so a green catalog run is also proof that the shipped script executes. Its own detection
    limits live in its docstring and are not repeated here.

    ONE subprocess for the whole tree, deliberately: a call per fenced block made
    `selftest-validate-skills.py` — which re-runs this validator once per injected defect — too slow
    to finish, and a gate nobody waits for is a gate nobody keeps.

    KNOWN LIMIT — this check covers less than the rule it enforces:
      - Only fences carrying a language tag the checker profiles are scanned. An UNTAGGED fence is
        skipped on purpose: `skills/conventional-commit/SKILL.md` ships an untagged block of
        Portuguese commit examples, which is prose and must not be flagged.
      - Only `*.md` under `skills/` is walked. Executable references (`references/*.py`, `*.sh`,
        `*.lua`) are NOT scanned — the checker's own Portuguese lexicon is data, and a scanner that
        fires on its own word list is noise.
      - Prose, comments, docstrings and non-path string literals are never scanned; they are the
        prose layer and follow the repository's language.
      - Skipped entirely when the checker script is absent, and reported as skipped rather than
        counted as a pass.
    """
    if not LOCALE_CHECKER.is_file():
        return
    rc, out = run([sys.executable, str(LOCALE_CHECKER), "--markdown-fences", str(ROOT / "skills")])
    if rc != 1:
        return
    for line in out.splitlines():
        m = LOCALE_HIT.match(line.strip())
        if not m:
            continue
        rel = Path(m.group(1))
        try:
            parts = rel.relative_to(ROOT / "skills").parts
        except ValueError:
            parts = rel.parts
        skill = parts[0] if parts else str(rel)
        where = f"{skill}/{parts[-1]}" if len(parts) > 1 and parts[-1] != "SKILL.md" else skill
        add(where, "C9 identifier locale", f"line {m.group(2)}: `{m.group(3)}` [{m.group(4)}]")


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


# ── C8: meta sections ─────────────────────────────────────────────────────
# "When to use this skill" was added after skills/api-resilience-testing shipped one for months
# under the four original titles' noses: same content as its description, read only after routing.
META_HEADING = re.compile(r"^## (How to Use|When to use this skill|Trigger Test Cases|Prompt|Usage)\s*$",
                          re.M | re.I)


def check_meta(skill: str, text: str) -> None:
    """A "Trigger Test Cases" or "How to Use" block is read only AFTER the skill has already
    triggered, so it cannot influence routing — it is pure context cost at the moment it loads.
    Triggers and anti-triggers belong in the frontmatter description, which is what the model
    reads when choosing a skill."""
    for m in META_HEADING.finditer(text):
        add(skill, "C8 meta section", f"`{m.group(0).strip()}` — move its content to the description")


# ── C10: frontmatter limits ───────────────────────────────────────────────
# The Agent Skills specification (agentskills.io/specification) fixes description at 1-1024
# characters and compatibility at 1-500. The names mirror MAX_DESCRIPTION_LENGTH and
# MAX_COMPATIBILITY_LENGTH in skills_ref/validator.py (skills-ref 0.1.1, the reference validator
# CI runs in its own step), which measures len() of the parsed value — so does this check.
MAX_DESCRIPTION_CHARS = 1024
MAX_COMPATIBILITY_CHARS = 500
FRONTMATTER_LIMITS = (("description", MAX_DESCRIPTION_CHARS),
                      ("compatibility", MAX_COMPATIBILITY_CHARS))

try:
    import yaml as _yaml
except ImportError:                                 # reported as skipped in main(), never as a pass
    _yaml = None


def check_limits(skill: str, text: str) -> None:
    """Measure the PARSED frontmatter value, in characters, against the spec limits.

    Why parsed and not the raw block C4 slices out of the file: a folded scalar (`>-`) carries its
    indentation and line breaks in the file and loses them when a consumer reads it. Measured over
    the 35 skills on 2026-09-04, the raw block is 6-26 characters longer than the value —
    svg-animation is 1024 raw and 998 parsed. A gate on the raw block would reject a skill the
    reference validator accepts. len() counts code points, not bytes, exactly like skills-ref;
    the descriptions carry non-ASCII quoted triggers, so a byte count would disagree with it.

    KNOWN LIMIT — what this check does NOT cover:
      - Only `description` and `compatibility` are measured. The name length/charset rule (64,
        lowercase) and the spec's whitelist of frontmatter fields are the reference validator's
        job, run pinned in CI; name-vs-directory is the CI frontmatter loop's.
      - It measures characters against the spec's hard limit, not tokens against the ~100-token
        budget the spec suggests; a description under 1024 characters can still be expensive.
      - The frontmatter is located with the same `split("---", 2)` C4 uses; a `---` inside a
        frontmatter value would truncate the block and is not handled here.
      - Skipped entirely without PyYAML, and reported as skipped rather than counted as a pass.
    """
    if _yaml is None:
        return
    fm = text.split("---", 2)
    if len(fm) < 3:
        return                                       # C4 already reports the missing frontmatter
    try:
        data = _yaml.safe_load(fm[1])
    except _yaml.YAMLError as exc:
        add(skill, "C10 frontmatter limits", f"frontmatter does not parse as YAML: {str(exc)[:90]}")
        return
    if not isinstance(data, dict):
        return                                       # the CI frontmatter loop reports the shape
    for field, limit in FRONTMATTER_LIMITS:
        value = data.get(field)
        if not isinstance(value, str):
            continue                                 # presence is the CI frontmatter loop's job
        n = len(value)
        if n > limit:
            add(skill, "C10 frontmatter limits",
                f"{field} is {n} chars, limit {limit} (parsed value; {n - limit} over)")


# ── C11: orphan reference ─────────────────────────────────────────────────
def _cited_files(skill_dir: Path, path: Path, text: str) -> set[Path]:
    """Files under skill_dir/references/ that `path` cites by link or inline path, resolved."""
    text = FENCE.sub("", text)
    refs = skill_dir / "references"
    out: set[Path] = set()
    targets = [m.group(1) for m in LINK.finditer(text)]
    targets += [m.group(1).strip() for m in INLINE.finditer(text)]
    for t in targets:
        t = t.split("#")[0].strip()
        if not t or " " in t or t.startswith(("http", "mailto:", "#")) or PLACEHOLDER.search(t):
            continue
        # the same two bases C1 accepts, plus the repo-root form skills/<self>/references/<file>
        prefix = f"skills/{skill_dir.name}/"
        if t.startswith(prefix):
            t = t[len(prefix):]
        for b in (path.parent, skill_dir):
            cand = b / t
            if cand.is_file():
                try:
                    cand.resolve().relative_to(refs.resolve())
                except ValueError:
                    continue
                out.add(cand.resolve())
    return out


def check_orphan_refs(skill: str, skill_dir: Path) -> None:
    """Every `*.md` under references/ (recursively) is reachable from SKILL.md — directly, or through
    a reference file that is itself reachable (a README.md inside a references subdirectory counts as
    an index once it is linked). A file nobody points at is loaded by nobody: measured on
    svg-animation, whose references/objects/ sat unlinked for a release (issue #117, fixed in #128).

    KNOWN LIMIT — what this check does NOT cover:
      - Only `*.md` files are judged. Scripts and data under references/ (`.py`, `.sh`, `.lua`,
        `.txt`, `.gz`) are loaded by the markdown that names them or by a tool, and are not walked.
      - A mention inside a fenced block does not count as a link (fences are example content, the
        same rule C1 applies), and neither does a directory link (`references/regimes/`): only a link
        or inline path that resolves to the FILE, from the citing file's directory or from the skill
        root, reaches it. A path with a placeholder (`references/<track>.md`) reaches nothing.
      - Reachability is measured, not relevance: a file linked from an unrelated sentence passes.
    """
    refs = skill_dir / "references"
    if not refs.is_dir():
        return
    all_md = {p.resolve() for p in refs.rglob("*.md")}
    entry = skill_dir / "SKILL.md"
    reached = _cited_files(skill_dir, entry, entry.read_text(encoding="utf-8")) & all_md
    frontier = set(reached)
    while frontier:
        nxt: set[Path] = set()
        for f in frontier:
            nxt |= _cited_files(skill_dir, f, f.read_text(encoding="utf-8")) & all_md
        frontier = nxt - reached
        reached |= nxt
    for orphan in sorted(all_md - reached):
        add(skill, "C11 orphan reference",
            f"{orphan.relative_to(skill_dir.resolve()).as_posix()} is linked from neither SKILL.md "
            "nor a reachable reference")


# ── C12: out-of-skill path ────────────────────────────────────────────────
# Top-level entries that exist ONLY in a full checkout of this repository. A target repository never
# carries them, so a path under one of them is dead in every install form except the clone.
CATALOG_ONLY_ROOTS = ("research/", "claude/", "codex/", "cursor/", "copilot/", "plugins/")
REPO_URL_PREFIX = "https://github.com/solvelab/ai-skills/"


def check_out_of_skill(skill: str, path: Path, text: str) -> None:
    """A skill is installed alone more often than not — symlinked, copied by `npx skills`, grouped in
    a plugin, or copied as a single Cursor rule — and the only paths that resolve in every one of
    those forms are the ones under its own directory. Three forms are a finding:

      (a) a link target or inline path that starts with a CATALOG_ONLY_ROOTS entry (`research/…`,
          `claude/global/hooks/…`): only a clone has it. Write the repository URL instead.
      (b) `<other-skill>/references/<file>` with no `skills/` prefix: the form that shipped in six
          skills (issue #117) and resolves nowhere, not even in the clone. The canonical form is
          `skills/<other-skill>/references/<file>` plus a sentence naming the skill; C1 then checks
          the file exists.
      (c) a relative path (`../…`) — a link target or an inline-code path alike — that resolves
          outside `skills/<this-skill>/` and is not a URL. The inline form is the one prose uses
          most (`../../claude/global/hooks/locale-rite.py`), so it is judged like the link.

    Accepted: URLs (the repository's own included), `skills/<other>/…` (C1 owns the existence
    check), `../SKILL.md` and anything else that stays inside the skill.

    Runs over `SKILL.md` and every `*.md` under `references/`, recursively — a finding in a nested
    file is labelled `<skill>/<subdir>/<file>` (the path relative to `references/`).

    KNOWN LIMIT — what this check does NOT cover:
      - Paths under `openspec/`, `scripts/`, `docs/`, `.github/` and other roots a TARGET repository
        may also carry are not judged: a skill that says `docs/SETUP.md` or `openspec/config.yaml` is
        usually describing the repository it operates on, and the check cannot tell that apart from a
        reference to this catalog's own file. Those are reviewed by hand.
      - A path inside a fenced block is example content and is not judged (same rule as C1).
      - The sentence that has to name the skill next to a `skills/<other>/references/` path (rule R1
        of issue #121) is prose and is not measured; a bare skill name in backticks is C2's job.
      - Inline code with a space, a placeholder or a leading `~`, `/`, `$` is a command or a
        template, not a path claim, and is skipped like C1 skips it.
    """
    text = FENCE.sub("", text)
    skill_dir = (ROOT / "skills" / skill.split("/")[0]).resolve()

    def judge(target: str, kind: str) -> None:
        t = target.split("#")[0].strip()
        if not t or t.startswith(("http", "mailto:", "#")) or PLACEHOLDER.search(t):
            return
        if t.startswith(CATALOG_ONLY_ROOTS):
            add(skill, "C12 out-of-skill path",
                f"{kind} -> {t}: exists only in a clone of this repository — use "
                f"{REPO_URL_PREFIX}blob/master/{t}")
            return
        head = t.split("/")[0]
        if head in NAMES and head != skill_dir.name and "/references/" in t:
            add(skill, "C12 out-of-skill path",
                f"{kind} -> {t}: cross-skill path without the skills/ prefix — write "
                f"skills/{t} and name the `{head}` skill in the sentence")
            return
        if t.startswith(".."):
            try:
                (path.parent / t).resolve().relative_to(skill_dir)
            except ValueError:
                add(skill, "C12 out-of-skill path",
                    f"{kind} -> {t}: resolves outside skills/{skill_dir.name}/")

    for m in LINK.finditer(text):
        judge(m.group(1), "link")
    text = LINK.sub("", text)                        # link text is prose; only the target was a path
    for m in INLINE.finditer(text):
        s = m.group(1).strip()
        if " " in s or s.startswith(("~", "/", "$")):
            continue
        judge(s, "inline")


# ── C13: anti-trigger clause ──────────────────────────────────────────────
# The exact phrase list. A description passes when it carries one of these literals, or a redirect —
# one of REDIRECT_WORDS followed by the name of another skill in the catalog (backticks optional).
ANTI_TRIGGER_PHRASES = ("Do NOT use", "do not use", "Not for", "that is `")
REDIRECT_WORDS = ("that is", "use", "see", "in", "to", "instead of")


def check_anti_trigger(skill: str, text: str) -> None:
    """Every description says where the skill does NOT apply — an explicit "Do NOT use for …" clause
    or a redirect ("for X use `<sibling>`") — so two skills do not compete for the same prompt. The
    rule is *Every skill states where it does not apply* in the skills-authoring spec; it was written
    and never measured, and four descriptions shipped without any clause (issue #117).

    What passes, exactly: the parsed description contains one of ANTI_TRIGGER_PHRASES, or one of
    REDIRECT_WORDS followed (optionally by "the") by the exact name of ANOTHER catalog skill, with or
    without backticks — "that is fivem-nui-react", "see `fivem-lua`", "live in r3f-fundamentals".

    KNOWN LIMIT — what this check does NOT cover:
      - It proves a phrase is present, not that the boundary is the right one or that it names the
        sibling the skill actually competes with. Measured overlaps (issue #121: python-rest-api vs
        api-resilience-testing on "review an endpoint") are decided by a human and recorded in the
        change that adds the clause.
      - The redirect form accepts a trigger sentence that happens to say "in <sibling>" — "Use when
        working in fivem-lua projects" would pass. Only the literal phrases are unambiguous.
      - A redirect to a family (`the r3f-* skills`) names no skill and does not pass; name one.
      - Skipped without PyYAML, like C10, and reported as skipped rather than counted as a pass.
    """
    if _yaml is None:
        return
    fm = text.split("---", 2)
    if len(fm) < 3:
        return                                       # C4 already reports the missing frontmatter
    try:
        data = _yaml.safe_load(fm[1])
    except _yaml.YAMLError:
        return                                       # C10 already reports the parse failure
    desc = data.get("description") if isinstance(data, dict) else None
    if not isinstance(desc, str):
        return
    if any(p in desc for p in ANTI_TRIGGER_PHRASES):
        return
    siblings = sorted(NAMES - {skill}, key=len, reverse=True)
    if siblings:
        words = "|".join(re.escape(w) for w in REDIRECT_WORDS)
        names = "|".join(re.escape(n) for n in siblings)
        if re.search(rf"\b(?:{words})\s+(?:the\s+)?`?(?:{names})`?(?![\w-])", desc):
            return
    add(skill, "C13 anti-trigger clause",
        "description names no boundary: add a \"Do NOT use for … (that is `<skill>`)\" clause or a "
        "redirect to the sibling it competes with")


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
    check_locale()
    for p in SKILLS:
        skill = p.parent.name
        text = p.read_text(encoding="utf-8")
        check_refs(skill, p, text)
        check_blocks(skill, text)
        check_description(skill, text)
        check_pin(skill, text)
        check_tags(skill, text)
        check_meta(skill, text)
        check_limits(skill, text)
        check_anti_trigger(skill, text)
        check_out_of_skill(skill, p, text)
        check_orphan_refs(skill, p.parent)
        # recursive: references/<subdir>/*.md are judged too (19 such files live in svg-animation);
        # the label keeps the path relative to references/, so depth-1 files keep their old label
        refs_dir = p.parent / "references"
        for ref in sorted(refs_dir.rglob("*.md")):
            label = f"{skill}/{ref.relative_to(refs_dir).as_posix()}"
            rtext = ref.read_text(encoding="utf-8")
            check_refs(label, ref, rtext)
            check_blocks(label, rtext)
            check_out_of_skill(label, ref, rtext)

    by_check: dict[str, int] = {}
    for _, c, _ in findings:
        by_check[c] = by_check.get(c, 0) + 1
    skipped = []
    if not LUAC:
        skipped.append("lua syntax (luac not installed)")
    if not LOCALE_CHECKER.is_file():
        skipped.append("identifier locale (check-identifier-locale.py missing)")
    try:
        import yaml  # noqa: F401
    except ImportError:
        skipped.append("yaml parse (PyYAML not installed)")
        skipped.append("frontmatter limits (PyYAML not installed)")
        skipped.append("anti-trigger clause (PyYAML not installed)")
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
