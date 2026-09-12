#!/usr/bin/env python3
"""Measure a repository's documentation LAYOUT against the map in `SKILL.md`.

The sibling script `check-doc-structure.py` asks whether one page is navigable (rules R1-R7). This
one asks whether the repository puts its documents where the map says, calls them what the map says,
keeps each fact in the document that owns it, and keeps the language trees in step (L1-L7).

    check-doc-layout.py REPO                     audit the repository rooted at REPO
    check-doc-layout.py --rules L2,L4 REPO       run only these rules
    check-doc-layout.py --exclude 'content/*' REPO   skip paths nobody in this repo owns
    check-doc-layout.py --locale-checker PATH    where code-locale's checker lives, for L5
    check-doc-layout.py --list                   print the rule table and exit
    check-doc-layout.py --map                    print the document map and exit
    check-doc-layout.py --selftest               prove every rule fires, and stays silent

Exit codes: 1 when any finding is reported, 0 when none, 2 on a usage error.

KNOWN LIMIT — what this script does NOT judge, and why:

  A CONDITIONAL slot is never reported as missing. Whether a project earns an API reference or an
     operations document is a fact about the code, not about the tree, and a script that guessed it
     would reprove the projects that correctly have neither. Only the always-slots (L1) are owed,
     and everything else is judged when it EXISTS: wrong name, wrong place, or absent from the index.
  L5 does not carry a word list. It delegates to `check-identifier-locale.py` of the `code-locale`
     skill, which already decides whether a name is English and already carries the waiver protocol.
     When that script cannot be found, or fails, L5 says NOT RUN **on stderr** and the verdict is
     unchanged: a missing engine is a diagnostic about this tool, not a defect in the repository
     being audited, and failing a clean repository over it is how a gate gets switched off. Point at
     the checker with `--locale-checker` when the two skills are installed apart, as they are in
     this catalog's plugin layout, where they ship in different plugins.
     Only that script's VERDICTS are raised; its advisory tier is not. Probed 2026-09-12: a file
     name built on a Portuguese verb ending is a `path-pt-morphology` verdict, so L5 reports it,
     while a name whose first segment is merely absent from the English word list is advisory there
     — and a rule that failed on every unknown word would reprove product names. Known names of that
     second kind are caught by the map's legacy list under L2, which also says where each one goes.
  L6 compares STRUCTURE, never meaning: the twin exists, the `##` count and numbering match, the
     fenced blocks match. Whether the translated prose still says what the source says is a
     judgement about meaning across two languages, and this catalog has measured twice what a gate
     over meaning costs (7 of 10 wrong for heading nesting, 3 of 4 for justification prose). A
     mirror that changes only a fence's info string (```bash -> ```sh) also escapes: the fence line
     is dropped before the blocks are compared.
  L6 knows a language tree by a CLOSED list of tags. An unusual tag is invisible rather than
     guessed: measured 2026-09-12, an earlier two-letter pattern read `docs/db/` and `docs/ui/` as
     languages and produced six findings against a correct repository.
  L7 recognizes an owned table only by its CANONICAL header row. A table with improvised columns
     escapes it. That is the deliberate trade: the alternative is guessing what a table is about
     from its content, which is the same class of judgement L6 refuses.
  `docs/reports/` is skipped by L2 and L7. A dated record is a snapshot of one moment, and a
     snapshot may legitimately quote a table or a name that is no longer current. L4 and L5 still
     apply to it.
  Nothing here moves, renames or writes a file. Every finding names a destination; performing the
     migration is the caller's job, in one commit with the links it breaks.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# ── The map ───────────────────────────────────────────────────────────────────

#: Language tags a `docs/<tag>/` directory may carry. A closed list on purpose: a two-letter pattern
#: reads `docs/db/`, `docs/ui/` and `docs/qa/` as languages and turns a correct repository into
#: findings (measured 2026-09-12: six, from two such directories).
LANGUAGE_TAGS = (
    "en", "en-US", "en-GB", "pt", "pt-BR", "pt-PT", "es", "es-419", "es-ES", "fr", "fr-CA",
    "de", "it", "nl", "pl", "tr", "ru", "uk", "ar", "he", "hi", "id", "ja", "ko", "sv", "nb",
    "da", "fi", "cs", "el", "ro", "hu", "th", "vi", "zh", "zh-CN", "zh-TW",
)

#: The tree the map names as the source. Everything else under `docs/` mirrors it.
SOURCE_TREE = "en"

#: Where transient records live, and the shape of their names.
REPORTS_DIR = "docs/reports"
DATED_NAME = re.compile(r"\d{4}-\d{2}-\d{2}")

#: Words that say "this is a record of one moment", matched as WHOLE words anywhere in the name.
#: As substrings they overreached: `diagnostic` swallowed `DIAGNOSTICS.md` (measured 2026-09-12).
WORD_MARKERS = (
    "homolog", "homologation", "homologacao", "diagnose", "diagnosis", "validation",
    "correcao", "roteiro", "continuar", "revalidacao", "postmortem", "mortem",
)

#: Words common enough to name a feature, so they mark a record only when they are the WHOLE name.
#: `PROGRESS.md` is a status note; `progress-bar.md` is a component, and reporting it is the kind of
#: false positive that gets a gate switched off (measured 2026-09-12).
STANDALONE_MARKERS = ("progress", "todo", "teste")

#: `.md` files that belong at the repository root, as bare stems. `claude` and `gemini` are
#: agent-instruction files, the same class as `agents`; the community-health names are GitHub's,
#: which reads them from the root and nowhere else.
ROOT_ALLOWED = ("readme", "agents", "claude", "gemini", "changelog", "contributing",
                "license", "licence", "code_of_conduct", "notice", "security",
                "support", "governance", "authors", "maintainers", "codeowners")


class Slot:
    """One entry of the document map."""

    def __init__(self, key: str, name: str, at_root: bool, always: bool,
                 legacy: tuple[str, ...] = ()) -> None:
        self.key = key
        self.name = name          # canonical basename
        self.at_root = at_root    # lives at the repository root, not in a language tree
        self.always = always      # owed by every project
        self.legacy = legacy      # basenames this slot absorbs, lowercased

    def canonical(self, tree: str = SOURCE_TREE) -> str:
        return self.name if self.at_root else "docs/%s/%s" % (tree, self.name)


SLOTS = (
    Slot("entry", "README.md", at_root=True, always=True),
    Slot("requirements", "REQUIREMENTS.md", at_root=False, always=True,
         legacy=("requisitos.md", "srs.md")),
    Slot("tutorial", "SETUP.md", at_root=False, always=False,
         legacy=("como-subir.md", "install.md", "installation.md", "getting-started.md")),
    Slot("explanation", "ARCHITECTURE.md", at_root=False, always=False,
         legacy=("technical.md", "design.md", "arquitetura.md")),
    Slot("api", "API.md", at_root=False, always=False,
         legacy=("api-contract.md", "endpoints.md")),
    Slot("operation", "OPERATIONS.md", at_root=False, always=False,
         legacy=("deployment.md", "deploy.md", "infrastructure.md", "runbook.md",
                 "deployment_guide.md", "operacao.md")),
    Slot("security", "SECURITY.md", at_root=False, always=False),
    Slot("agents", "AGENTS.md", at_root=True, always=False),
    Slot("history", "CHANGELOG.md", at_root=True, always=False),
    Slot("contribution", "CONTRIBUTING.md", at_root=True, always=False),
)

#: Paths a slot is allowed to occupy even though the map files it under a tree. GitHub reads
#: `SECURITY.md` from the repository root and nowhere else, so a root copy is the platform's
#: document, not a misplaced tier.
ROOT_EXEMPT = {"SECURITY.md"}

#: The README section that carries the index of every slot.
INDEX_HEADINGS = ("documentation", "documentacao")

#: How a slot the project does not earn is declared: the slot's own name, then the waiver, on ONE
#: index entry. The subject is read from the START of the entry so that a reason merely CONTAINING
#: another slot's word cannot waive it — measured 2026-09-12, "not applicable: no infrastructure
#: requirements" silently waived the requirements slot.
NOT_APPLICABLE = re.compile(r"not applicable|nao se aplica", re.I)
INDEX_ENTRY = re.compile(r"^\s*(?:[-*+]|\|)\s*\[?([^\]|—:]+)")

#: How a project declares it documents in one language on purpose.
SINGLE_LANGUAGE = re.compile(r"english only|one language|single language|idioma unico|"
                             r"somente em ingles|apenas em ingles", re.I)

#: A fact's canonical header row -> the document that owns it. Folded cells, in order.
OWNERSHIP = {
    ("variable", "type", "default", "required", "description"): "SETUP.md",
    ("variavel", "tipo", "padrao", "obrigatoria", "descricao"): "SETUP.md",
    ("symptom", "cause", "fix"): "SETUP.md",
    ("sintoma", "causa", "correcao"): "SETUP.md",
    ("method", "path", "auth", "description"): "API.md",
    ("metodo", "rota", "auth", "descricao"): "API.md",
    ("resource", "value", "source"): "OPERATIONS.md",
    ("recurso", "valor", "fonte"): "OPERATIONS.md",
    ("command", "what it does"): "README.md",
    ("comando", "o que faz"): "README.md",
}

RULES = {
    "L1": "every always-slot is present, or declared not applicable in the README index",
    "L2": "a legacy name is reported with the canonical path it migrates to",
    "L3": "no loose '.md' at the repository root",
    "L4": "a dated or transient record lives in %s/" % REPORTS_DIR,
    "L5": "file and directory names are English (delegated to code-locale)",
    "L6": "the mirror tree matches the source tree in structure",
    "L7": "an owned table's canonical header row appears only in its owning document",
}

SKIP_DIRECTORIES = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache",
                    "dist", "build", "vendor", ".tox", ".mypy_cache", "openspec", ".next"}

FENCE = re.compile(r"^\s*(?:```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
TABLE_DIVIDER = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
NUMBER_PREFIX = re.compile(r"^\s*(\d+)[.)]")

#: How many paths go into one delegated call. A documentation site with tens of thousands of pages
#: overflows `ARG_MAX` otherwise — reproduced at 40k paths against a 2 MB limit.
ARGV_CHUNK = 400

#: Things the tool needs to say about ITSELF. Never findings: a finding is about the repository.
_diagnostics: list[str] = []

#: Set from `--locale-checker`, read by L5.
_locale_checker_path: "str | None" = None


def diagnostic(message: str) -> None:
    if message not in _diagnostics:
        _diagnostics.append(message)


# ── Findings ──────────────────────────────────────────────────────────────────


class Finding:
    """One reported defect in the audited repository. `path` is repo-relative."""

    def __init__(self, path: str, rule: str, message: str) -> None:
        self.path = path
        self.rule = rule
        self.message = message

    def render(self) -> str:
        return "%s: [%s] %s" % (self.path or ".", self.rule, self.message)


# ── Parsing ───────────────────────────────────────────────────────────────────


def fold(text: str) -> str:
    """Accent-folded, lowercase, punctuation-free. `Descrição` and `descricao` are one word."""
    text = text.replace("`", "").replace("*", "").strip().lower()
    stripped = unicodedata.normalize("NFD", text)
    kept = "".join(c for c in stripped if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s-]", "", kept)).strip()


def words(text: str) -> list[str]:
    """The folded words of a name, split on every separator a file name uses."""
    return [w for w in re.split(r"[^a-z0-9]+", fold(text)) if w]


def normalize_tag(name: str) -> str:
    """`pt_BR` and `pt-br` are the same tag as `pt-BR`."""
    tag = name.replace("_", "-")
    parts = tag.split("-")
    if len(parts) == 2:
        return "%s-%s" % (parts[0].lower(), parts[1].upper())
    return tag.lower()


KNOWN_TAGS = {normalize_tag(t) for t in LANGUAGE_TAGS}


def is_language_tree(name: str) -> bool:
    return normalize_tag(name) in KNOWN_TAGS


def language_suffix(name: str) -> "str | None":
    """`README.pt-BR.md` -> `pt-BR`. Only a KNOWN tag counts.

    Folding any middle segment turned `API.v2.md` into `API.md` and `SETUP.draft.md` into
    `SETUP.md`, so a stale second copy of an owned table read as the owner itself and escaped every
    rule (measured 2026-09-12).
    """
    parts = name.split(".")
    if len(parts) == 3 and is_language_tree(parts[1]):
        return normalize_tag(parts[1])
    return None


def owning_name(name: str) -> str:
    """`README.pt-BR.md` -> `README.md`. A mirror is the same document in another language."""
    tag = language_suffix(name)
    if tag is None:
        return name
    parts = name.split(".")
    return "%s.%s" % (parts[0], parts[2])


def relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def read_or_report(path: Path, root: Path, rule: str) -> "tuple[list[str], Finding | None]":
    """Lines of a document. An unreadable file is a finding of its own, never silent emptiness.

    Measured 2026-09-12: a README saved in latin-1 read as zero lines, so its index vanished and
    L1 blamed the content — three findings, every one of them wrong, and the real defect unnamed.
    """
    rel = relative(path, root)
    try:
        return path.read_text(encoding="utf-8").splitlines(), None
    except UnicodeDecodeError:
        return [], Finding(rel, rule, "not valid UTF-8, so nothing in it could be read; re-save it "
                                      "as UTF-8 before trusting any other finding about it")
    except OSError as exc:
        return [], Finding(rel, rule, "could not be read (%s)" % exc.__class__.__name__)


def strip_fences(lines: list[str]) -> list[str]:
    out, inside = [], False
    for line in lines:
        if FENCE.match(line):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return out


def sections(lines: list[str]) -> list[str]:
    """Every `##` heading text, in order, fences removed."""
    out = []
    for line in strip_fences(lines):
        m = HEADING.match(line)
        if m and len(m.group(1)) == 2:
            out.append(m.group(2))
    return out


def code_blocks(lines: list[str]) -> list[str]:
    """The body of every fenced block, right-stripped per line. The fence line itself is dropped."""
    out, buf, inside = [], [], False
    for line in lines:
        if FENCE.match(line):
            if inside:
                out.append("\n".join(buf))
                buf = []
            inside = not inside
            continue
        if inside:
            buf.append(line.rstrip())
    if inside and buf:
        out.append("\n".join(buf))
    return out


def header_rows(lines: list[str]) -> list[tuple[int, tuple[str, ...]]]:
    """(line number, folded cells) for the first row of every pipe table outside a fence."""
    out, expecting = [], None
    for i, line in enumerate(strip_fences(lines), start=1):
        m = TABLE_ROW.match(line)
        if not m:
            expecting = None
            continue
        if TABLE_DIVIDER.match(line):
            if expecting:
                out.append(expecting)
            expecting = None
            continue
        if expecting is None:
            expecting = (i, tuple(fold(c) for c in m.group(1).split("|")))
    return out


def markdown_files(root: Path, excludes: list[str]) -> list[Path]:
    """Every markdown document under the repository, pruning skipped directories as it walks.

    The extension match is case-insensitive: `NOTES.MD` is invisible to a case-sensitive glob on
    Linux and audited on macOS, and a gate that disagrees with itself across machines is a gate
    nobody can reproduce locally. Exclusion globs are matched against the `/`-separated path, which
    is what the caller types, on every platform.
    """
    out = []
    for current, directories, files in os.walk(root):
        directories[:] = [d for d in directories if d not in SKIP_DIRECTORIES]
        here = Path(current)
        for name in files:
            if not name.lower().endswith(".md"):
                continue
            path = here / name
            rel = relative(path, root)
            if any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel, "*/" + g) for g in excludes):
                continue
            out.append(path)
    return sorted(out)


def language_trees(root: Path) -> list[str]:
    docs = root / "docs"
    if not docs.is_dir():
        return []
    return sorted(d.name for d in docs.iterdir() if d.is_dir() and is_language_tree(d.name))


def readme_index(root: Path, name: str = "README.md") -> "tuple[list[str], bool, Finding | None]":
    """(lines of that README's documentation index, index section found, unreadable finding)."""
    readme = root / name
    if not readme.is_file():
        return [], False, None
    lines, problem = read_or_report(readme, root, "L1")
    if problem is not None:
        return [], False, problem
    lines = strip_fences(lines)
    start = None
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if not m:
            continue
        if start is not None and len(m.group(1)) <= 2:
            return lines[start:i], True, None
        if len(m.group(1)) == 2 and fold(m.group(2)) in INDEX_HEADINGS:
            start = i
    if start is not None:
        return lines[start:], True, None
    return [], False, None


def declares_absent(index: list[str], slot: Slot) -> bool:
    """A waiver is one index ENTRY naming this slot, not any line mentioning its word."""
    wanted = fold(slot.name.replace(".md", ""))
    key = fold(slot.key)
    for line in index:
        if not NOT_APPLICABLE.search(line):
            continue
        entry = INDEX_ENTRY.match(line)
        subject = fold(entry.group(1)) if entry else fold(line)
        if wanted in subject or key in subject:
            return True
    return False


# ── The rules ─────────────────────────────────────────────────────────────────


def check_slots(root: Path, files: list[Path]) -> list[Finding]:
    """L1 — an always-slot is present, or its absence is declared. An earned slot is in the index."""
    out: list[Finding] = []
    rel = {relative(p, root) for p in files}
    trees = language_trees(root) or [SOURCE_TREE]

    if "README.md" not in rel:
        return [Finding("README.md", "L1", "no README.md; every project owes the entry document")]

    index, has_index, problem = readme_index(root)
    if problem is not None:
        return [problem]
    if not has_index:
        out.append(Finding("README.md", "L1",
                           "no '## Documentation' section; the index is where a reader learns which "
                           "slots this project earned and which it declined"))

    index_text = "\n".join(index)

    for slot in SLOTS:
        if not slot.always or slot.key == "entry":
            continue
        present = any(slot.canonical(t) in rel for t in trees) or slot.name in rel
        if present or declares_absent(index, slot):
            continue
        out.append(Finding(slot.canonical(), "L1",
                           "always-slot missing and not declared; write it, or put "
                           "'not applicable: <reason>' for it in the README index"))

    for slot in SLOTS:
        if slot.at_root:
            continue
        for tree in trees:
            path = slot.canonical(tree)
            if path in rel and path not in index_text and slot.name not in index_text:
                out.append(Finding(path, "L1",
                                   "exists but the README index does not list it; an unlisted "
                                   "document is one a reader has no way to discover"))
                break

    # The root half of the pair. L6 only walks `docs/<tree>/`, so without this the mirrored README
    # the map mandates could be missing entirely and nothing would say so.
    for tree in trees:
        if tree == SOURCE_TREE:
            continue
        mirror = "README.%s.md" % tree
        if mirror not in rel:
            out.append(Finding(mirror, "L1",
                               "the %s tree exists with no %s; both READMEs carry the index, each "
                               "linking its own tree" % (tree, mirror)))
            continue
        _, mirror_has_index, mirror_problem = readme_index(root, mirror)
        if mirror_problem is not None:
            out.append(mirror_problem)
        elif not mirror_has_index:
            out.append(Finding(mirror, "L1", "no '## Documentation' section in the mirror README"))
    return out


def check_legacy(root: Path, files: list[Path]) -> list[Finding]:
    """L2 — a legacy name, or a canonical name in the wrong place, with its destination."""
    out = []
    trees = language_trees(root) or [SOURCE_TREE]
    canonical_paths = {slot.canonical(t) for slot in SLOTS for t in trees}
    canonical_paths |= {slot.name for slot in SLOTS if slot.at_root}
    canonical_paths |= {"README.%s.md" % t for t in trees if t != SOURCE_TREE}
    canonical_paths |= {"CONTRIBUTING.%s.md" % t for t in trees if t != SOURCE_TREE}
    canonical_paths |= ROOT_EXEMPT

    for p in files:
        rel = relative(p, root)
        if rel in canonical_paths or rel.startswith(REPORTS_DIR + "/"):
            continue
        # The destination follows the tree the document is already in: telling the author of
        # `docs/pt-BR/DESIGN.md` to move it to `docs/en/` destroys the mirror.
        parts = rel.split("/")
        tree = parts[1] if len(parts) > 2 and parts[0] == "docs" and is_language_tree(parts[1]) \
            else SOURCE_TREE
        base = owning_name(p.name).lower()
        # A root slot is only MISPLACED when it sits in the documentation tree. `k8s/README.md` and
        # `.github/workflows/README.md` are that directory's own entry document, which GitHub renders
        # as such — reporting them moved L2 from 38 findings to 59, every one of the 21 wrong
        # (measured 2026-09-12).
        in_docs = parts[0] == "docs"
        for slot in SLOTS:
            target = slot.name if slot.at_root else slot.canonical(tree)
            if base in slot.legacy:
                out.append(Finding(rel, "L2", "legacy name for the %s slot -> %s"
                                   % (slot.key, target)))
                break
            if base == slot.name.lower() and (in_docs or not slot.at_root):
                out.append(Finding(rel, "L2", "canonical name outside its place -> %s" % target))
                break
    return out


def check_root(root: Path, files: list[Path]) -> list[Finding]:
    """L3 — the root carries the entry documents and nothing else."""
    out = []
    # Computed unconditionally, never from the selected rule set: with `--rules L3` alone, a file
    # another rule would have claimed used to vanish from the report entirely.
    claimed = {f.path for f in check_legacy(root, files)}
    claimed |= {f.path for f in check_reports(root, files)}
    for p in files:
        rel = relative(p, root)
        if "/" in rel or rel in claimed:
            continue
        stem = fold(owning_name(p.name)[: -len(".md")]).replace("-", "_")
        if stem in ROOT_ALLOWED:
            continue
        out.append(Finding(rel, "L3",
                           "loose document at the root; every tier lives under docs/<tree>/ and "
                           "every transient record under %s/" % REPORTS_DIR))
    return out


def check_reports(root: Path, files: list[Path]) -> list[Finding]:
    """L4 — a record of one moment lives with the other records of one moment."""
    out = []
    anywhere = {fold(m) for m in WORD_MARKERS}
    alone = {fold(m) for m in STANDALONE_MARKERS}
    for p in files:
        rel = relative(p, root)
        if rel.startswith(REPORTS_DIR + "/"):
            continue
        stem_words = words(p.stem)
        dated = bool(DATED_NAME.search(p.stem))
        marked = any(w in anywhere for w in stem_words) or \
            (len(stem_words) == 1 and stem_words[0] in alone)
        if dated or marked:
            out.append(Finding(rel, "L4",
                               "transient record outside %s/ -> %s/YYYY-MM-DD-<slug>.md"
                               % (REPORTS_DIR, REPORTS_DIR)))
    return out


def locale_checker(explicit: "str | None" = None) -> "Path | None":
    """The `code-locale` checker, in the layouts this catalog installs.

    The plugin layout ships the two skills in different plugins, so a sibling search finds nothing
    there — which is why a missing engine must never fail the audit, and why `--locale-checker`
    exists.
    """
    if explicit:
        candidate = Path(explicit)
        return candidate if candidate.is_file() else None
    here = Path(__file__).resolve().parent
    name = "check-identifier-locale.py"
    candidates = [
        here.parent.parent / "code-locale" / "references" / name,
        here.parent.parent.parent / "skills" / "code-locale" / "references" / name,
        here.parent.parent.parent.parent / "workflow" / "skills" / "code-locale" / "references" / name,
        Path.home() / "ai-skills" / "skills" / "code-locale" / "references" / name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def check_names(root: Path, files: list[Path]) -> list[Finding]:
    """L5 — delegated. This rule owns no word list; `code-locale` owns that question."""
    checker = locale_checker(_locale_checker_path)
    if checker is None:
        diagnostic("L5 NOT RUN: code-locale's check-identifier-locale.py was not found; "
                   "pass --locale-checker PATH to enable the rule")
        return []
    if not files:
        return []

    by_relative = {relative(p, root): p for p in files}
    ordered = sorted(by_relative)
    out: list[Finding] = []
    seen: set = set()

    for start in range(0, len(ordered), ARGV_CHUNK):
        chunk = ordered[start:start + ARGV_CHUNK]
        try:
            proc = subprocess.run(
                [sys.executable, str(checker), *[str(by_relative[r]) for r in chunk]],
                capture_output=True, text=True,
            )
        except OSError as exc:
            diagnostic("L5 NOT RUN: could not run %s (%s)" % (checker.name, exc.__class__.__name__))
            return []
        if proc.returncode not in (0, 1) and not proc.stdout.strip():
            last = ((proc.stderr or "").strip().splitlines() or ["no stderr"])[-1]
            diagnostic("L5 NOT RUN: %s exited %d without output (%s)"
                       % (checker.name, proc.returncode, last))
            return []
        for line in proc.stdout.splitlines():
            m = re.match(r"^(\S+\.md):\s+\S+\s+\[path-(\S+?):", line)
            if not m or m.group(2).startswith("en-unknown"):
                continue
            name, tier = m.group(1), m.group(2)
            # The sibling names the file the way it was given it: a path when the file is under the
            # caller's directory, a bare name when it is not. Resolve EVERY match, not the first:
            # the same basename exists in both trees, and one of them was being dropped.
            # One reported path is one file, so take the LONGEST suffix that matches, not every
            # one: `scripts/simulacao/README.md` also ends with `/README.md`, and matching both
            # invented a finding against the repository's own README (measured 2026-09-12 on
            # `ferdinand`). Taking only the first match had the opposite failure — the second of
            # two twins was dropped — so the resolution is by specificity, not by order.
            candidates = [r for r in chunk if r == name or name.endswith("/" + r)]
            if not candidates:
                candidates = [r for r in chunk if Path(r).name == name]
            hits = [max(candidates, key=len)] if candidates else [name]
            for hit in hits or [name]:
                if (hit, tier) in seen:
                    continue
                seen.add((hit, tier))
                out.append(Finding(hit, "L5", "file name is not English (%s); rename it, or waive "
                                              "it the way code-locale waives a path" % tier))
    return out


def check_parity(root: Path, files: list[Path]) -> list[Finding]:
    """L6 — the mirror is the same document in another language, not another document."""
    out = []
    trees = language_trees(root)
    if not trees:
        return []
    if len(trees) == 1 and trees[0] == SOURCE_TREE:
        # The pair is the default. One tree is legitimate, and it is a DECLARED decision: without
        # the declaration a reader cannot tell "one language is enough here" from "somebody stopped
        # halfway", which is the same question the map answers for a slot nobody earned.
        index, _, _ = readme_index(root)
        if not any(SINGLE_LANGUAGE.search(line) for line in index):
            return [Finding("docs/%s" % SOURCE_TREE, "L6",
                            "source tree with no mirror and no declaration; write the mirror, or "
                            "say 'documented in English only' in the README index")]
        return []
    if SOURCE_TREE not in trees:
        return [Finding("docs/%s" % SOURCE_TREE, "L6",
                        "mirror trees exist (%s) with no source tree; the map names docs/%s the "
                        "source and every other tree its mirror" % (", ".join(trees), SOURCE_TREE))]

    def in_tree(tree: str) -> dict:
        # Resolved on both sides so that a tree hosted through a symlink — a normal way to keep a
        # translation beside its source — is read as the tree it points at instead of as empty.
        base = (root / "docs" / tree).resolve()
        found = {}
        for p in files:
            try:
                found[str(p.resolve().relative_to(base)).replace("\\", "/")] = p
            except ValueError:
                continue
        return found

    source = in_tree(SOURCE_TREE)
    for tree in trees:
        if tree == SOURCE_TREE:
            continue
        mirror = in_tree(tree)
        for name, src in sorted(source.items()):
            twin = mirror.get(name)
            where = "docs/%s/%s" % (tree, name)
            if twin is None:
                out.append(Finding(where, "L6",
                                   "no mirror for docs/%s/%s; the pair is written in one commit"
                                   % (SOURCE_TREE, name)))
                continue
            a, problem_a = read_or_report(src, root, "L6")
            b, problem_b = read_or_report(twin, root, "L6")
            if problem_a or problem_b:
                out.append(problem_a or problem_b)
                continue
            sa, sb = sections(a), sections(b)
            if len(sa) != len(sb):
                out.append(Finding(where, "L6",
                                   "%d '##' sections against %d in the source" % (len(sb), len(sa))))
                continue
            na = [m.group(1) for s in sa for m in [NUMBER_PREFIX.match(s)] if m]
            nb = [m.group(1) for s in sb for m in [NUMBER_PREFIX.match(s)] if m]
            if na != nb:
                out.append(Finding(where, "L6",
                                   "section numbering %s against %s in the source"
                                   % (",".join(nb) or "none", ",".join(na) or "none")))
                continue
            ca, cb = code_blocks(a), code_blocks(b)
            if ca != cb:
                differing = sum(1 for x, y in zip(ca, cb) if x != y) + abs(len(ca) - len(cb))
                out.append(Finding(where, "L6",
                                   "%d code block(s) differ from the source; the reader pastes "
                                   "them, so they are copied, never translated" % differing))
        for name in sorted(set(mirror) - set(source)):
            out.append(Finding("docs/%s/%s" % (tree, name), "L6",
                               "mirror document with no source under docs/%s/" % SOURCE_TREE))
    return out


def check_ownership(root: Path, files: list[Path]) -> list[Finding]:
    """L7 — the canonical header row of an owned fact, outside the document that owns it."""
    out = []
    for p in files:
        rel = relative(p, root)
        if rel.startswith(REPORTS_DIR + "/"):
            continue
        lines, problem = read_or_report(p, root, "L7")
        if problem is not None:
            continue
        for line_no, cells in header_rows(lines):
            owner = OWNERSHIP.get(cells)
            if owner and owning_name(p.name) != owner:
                out.append(Finding("%s:%d" % (rel, line_no), "L7",
                                   "this table is owned by %s; everywhere else links to it"
                                   % owner))
    return out


CHECKS = {
    "L1": check_slots,
    "L2": check_legacy,
    "L3": check_root,
    "L4": check_reports,
    "L5": check_names,
    "L6": check_parity,
    "L7": check_ownership,
}


def audit(root: Path, rules: list[str], excludes: list[str]) -> list[Finding]:
    files = markdown_files(root, excludes)
    out: list[Finding] = []
    for rule in rules:
        out.extend(CHECKS[rule](root, files))
    return sorted(out, key=lambda f: (f.rule, f.path))


# ── Self-test ─────────────────────────────────────────────────────────────────

#: A layout the map approves of. Any rule firing on it is a false positive.
CLEAN = {
    "README.md": "# T\n\nDoes one thing.\n\n## Documentation\n\n"
                 "- [Requirements](docs/en/REQUIREMENTS.md)\n"
                 "- [Setup](docs/en/SETUP.md)\n"
                 "- Operation — not applicable: one environment, started by one command\n"
                 "- Architecture — not applicable: three modules, the tree says it\n\n"
                 "## Development\n\n| Command | What it does |\n|---|---|\n| `make test` | runs tests |\n",
    # The root mirror carries its owner's table: it IS the README, in another language.
    "README.pt-BR.md": "# T\n\nFaz uma coisa.\n\n## Documentation\n\n"
                       "- [Requisitos](docs/pt-BR/REQUIREMENTS.md)\n"
                       "- [Setup](docs/pt-BR/SETUP.md)\n"
                       "- Operation — not applicable: um ambiente\n"
                       "- Architecture — not applicable: tres modulos\n\n"
                       "## Desenvolvimento\n\n| Comando | O que faz |\n|---|---|\n"
                       "| `make test` | roda os testes |\n",
    "docs/en/REQUIREMENTS.md": "# Requirements\n\n## 1. Purpose\n\nOne thing.\n\n## 2. Glossary\n\nNone.\n",
    "docs/pt-BR/REQUIREMENTS.md": "# Requisitos\n\n## 1. Proposito\n\nUma coisa.\n\n## 2. Glossario\n\nNenhum.\n",
    "docs/en/SETUP.md": "# Setup\n\n## 1. Environment\n\n"
                        "| Variable | Type | Default | Required | Description |\n|---|---|---|---|---|\n"
                        "| `PORT` | port | `8080` | no | http port |\n\n```bash\nmake run\n```\n",
    "docs/pt-BR/SETUP.md": "# Setup\n\n## 1. Ambiente\n\n"
                           "| Variavel | Tipo | Padrao | Obrigatoria | Descricao |\n|---|---|---|---|---|\n"
                           "| `PORT` | porta | `8080` | nao | porta http |\n\n```bash\nmake run\n```\n",
    "docs/reports/2026-01-09-homologation.md": "# Report\n\nRan it.\n",
}

#: One injected defect per case, as a patch over CLEAN. `None` deletes the file; `bytes` writes raw.
SELFTEST_CASES = {
    "L1": {"docs/en/REQUIREMENTS.md": None, "docs/pt-BR/REQUIREMENTS.md": None},
    # a waiver naming another slot must not silence this one
    "L1-wrong-slot": {"docs/en/REQUIREMENTS.md": None, "docs/pt-BR/REQUIREMENTS.md": None,
                      "README.md": CLEAN["README.md"].replace(
                          "- Operation — not applicable: one environment, started by one command",
                          "- Operation — not applicable: no infrastructure requirements")},
    "L1-no-index": {"README.md": "# T\n\nDoes one thing.\n"},
    "L1-unlisted": {"docs/en/API.md": "# API\n", "docs/pt-BR/API.md": "# API\n"},
    "L1-root-mirror": {"README.pt-BR.md": None},
    "L1-unreadable": {"README.md": b"# T\n\n## Documentation\n\n- caf\xe9 n\xe3o\n"},
    "L2": {"docs/en/TECHNICAL.md": "# Technical\n", "docs/pt-BR/TECHNICAL.md": "# Technical\n"},
    "L2-outside": {"docs/API.md": "# API\n"},
    "L2-rootslot-in-docs": {"docs/CHANGELOG.md": "# Changelog\n"},
    "L3": {"NOTES.md": "# Notes\n"},
    "L3-suffixed": {"README.backup.md": "# Backup\n"},
    "L4-dated": {"docs/en/2026-04-17-run.md": "# D\n", "docs/pt-BR/2026-04-17-run.md": "# D\n"},
    "L4-marked": {"docs/en/homologation-notes.md": "# H\n",
                  "docs/pt-BR/homologation-notes.md": "# H\n"},
    "L4-standalone": {"docs/en/PROGRESS.md": "# P\n", "docs/pt-BR/PROGRESS.md": "# P\n"},
    "L5": {"docs/en/revalidacao-hermes.md": "# R\n", "docs/pt-BR/revalidacao-hermes.md": "# R\n"},
    "L6": {"docs/pt-BR/SETUP.md": None},
    "L6-lone": {"docs/pt-BR/SETUP.md": None, "docs/pt-BR/REQUIREMENTS.md": None,
                "README.pt-BR.md": None},
    "L6-count": {"docs/pt-BR/SETUP.md": "# Setup\n\n## 1. Ambiente\n\n## 2. Extra\n\n"
                                        "```bash\nmake run\n```\n"},
    "L6-numbering": {"docs/pt-BR/SETUP.md": "# Setup\n\n## 2. Ambiente\n\n```bash\nmake run\n```\n"},
    "L6-blocks": {"docs/pt-BR/SETUP.md": "# Setup\n\n## 1. Ambiente\n\n"
                                         "```bash\nmake rodar\n```\n"},
    "L6-orphan": {"docs/pt-BR/EXTRA.md": "# Extra\n"},
    "L7": {"docs/en/ARCHITECTURE.md": "# A\n\n| Variable | Type | Default | Required | Description |\n"
                                      "|---|---|---|---|---|\n| `PORT` | port | `8080` | no | http |\n",
           "docs/pt-BR/ARCHITECTURE.md": "# A\n\n| Variavel | Tipo | Padrao | Obrigatoria | Descricao |\n"
                                         "|---|---|---|---|---|\n| `PORT` | porta | `8080` | nao | http |\n"},
    "L7-suffixed": {"docs/en/SETUP.draft.md":
                    "# S\n\n| Variable | Type | Default | Required | Description |\n"
                    "|---|---|---|---|---|\n| `PORT` | port | `8080` | no | http |\n",
                    "docs/pt-BR/SETUP.draft.md":
                    "# S\n\n| Variable | Type | Default | Required | Description |\n"
                    "|---|---|---|---|---|\n| `PORT` | port | `8080` | no | http |\n"},
}

#: Overlays that must produce NO finding for the named rule. A detector with no vocabulary for
#: "stay silent here" only ever grows: every false positive measured on a real repository became a
#: case in this dict.
SELFTEST_SILENT = {
    "L6": [
        # two-letter directories that are not languages
        {"docs/db/schema.md": "# S\n", "docs/ui/components.md": "# C\n"},
    ],
    "L4": [
        # `diagnostic` is not a word in `DIAGNOSTICS`, nor `progress` one in `progress-bar`
        {"docs/en/DIAGNOSTICS.md": "# D\n", "docs/pt-BR/DIAGNOSTICS.md": "# D\n",
         "docs/en/progress-bar.md": "# P\n", "docs/pt-BR/progress-bar.md": "# P\n"},
    ],
    "L2": [
        # GitHub reads a root SECURITY.md, and only from the root
        {"SECURITY.md": "# Security policy\n"},
        # a nested README is that directory's own entry document, not a misplaced root one
        {"k8s/README.md": "# Manifests\n", ".github/workflows/README.md": "# CI\n"},
    ],
    "L1": [
        # a project may document in one language, when it says so
        {"docs/pt-BR/SETUP.md": None, "docs/pt-BR/REQUIREMENTS.md": None,
         "README.pt-BR.md": None,
         "README.md": CLEAN["README.md"].replace(
             "## Development",
             "- Mirror — documented in English only\n\n## Development")},
    ],
}


def _materialize(base: Path, overlay: dict) -> None:
    tree = dict(CLEAN)
    tree.update(overlay)
    for rel, body in tree.items():
        if body is None:
            continue
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, bytes):
            p.write_bytes(body)
        else:
            p.write_text(body, encoding="utf-8")


def selftest() -> int:
    import tempfile

    global _locale_checker_path
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        _materialize(clean, {})
        noise = [f.render() for f in audit(clean, sorted(CHECKS), [])]
        if noise:
            failures.append("clean layout reproved: %s" % "; ".join(noise))

        for case, overlay in SELFTEST_CASES.items():
            rule = case.split("-")[0]
            base = Path(tmp) / ("case-" + case)
            _materialize(base, overlay)
            fired = [f.rule for f in audit(base, [rule], [])]
            if rule not in fired:
                failures.append("%s did not fire on its own injected defect" % case)

        for rule, overlays in SELFTEST_SILENT.items():
            for i, overlay in enumerate(overlays):
                base = Path(tmp) / ("silent-%s-%d" % (rule, i))
                _materialize(base, overlay)
                fired = [f.render() for f in audit(base, [rule], [])]
                if fired:
                    failures.append("%s fired on a layout it must accept: %s"
                                    % (rule, "; ".join(fired)))

        # A subset must never report less than the union of its parts.
        subset = Path(tmp) / "subset"
        _materialize(subset, {"DEPLOY.md": "# D\n"})
        if not audit(subset, ["L3"], []) and not audit(subset, ["L2"], []):
            failures.append("a root DEPLOY.md was reported by neither L2 nor L3 alone")

        # A missing or broken engine is a diagnostic, never a finding: the plugin layout ships the
        # two skills apart, and a red gate on a perfect repository is how a gate gets switched off.
        keep = _locale_checker_path
        _locale_checker_path = str(Path(tmp) / "does-not-exist.py")
        _diagnostics.clear()
        if audit(clean, ["L5"], []):
            failures.append("L5 produced a finding when its engine was missing")
        if not _diagnostics:
            failures.append("L5 said nothing when its engine was missing")
        broken = Path(tmp) / "broken-checker.py"
        broken.write_text("import sys\nsys.stderr.write('boom\\n')\nsys.exit(3)\n", encoding="utf-8")
        _locale_checker_path = str(broken)
        _diagnostics.clear()
        if audit(clean, ["L5"], []) or not _diagnostics:
            failures.append("L5 answered clean while its engine was failing")
        _locale_checker_path = keep

    for line in failures:
        print("selftest: %s" % line, file=sys.stderr)
    detected = len(SELFTEST_CASES) - len([f for f in failures if "did not fire" in f])
    silent_total = sum(len(v) for v in SELFTEST_SILENT.values())
    silent_ok = silent_total - len([f for f in failures if "must accept" in f])
    print("selftest: %d/%d injected defects detected; %d/%d silent cases silent; clean layout %s"
          % (detected, len(SELFTEST_CASES), silent_ok, silent_total,
             "silent" if not any("reproved" in f for f in failures) else "REPROVED"))
    return 1 if failures else 0


# ── CLI ───────────────────────────────────────────────────────────────────────


def main(argv: "list[str] | None" = None) -> int:
    global _locale_checker_path

    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("repo", nargs="?", help="repository root to audit")
    ap.add_argument("--rules", help="comma-separated subset, e.g. L2,L4 (default: all)")
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="skip paths matching this glob; repeatable")
    ap.add_argument("--locale-checker", metavar="PATH",
                    help="code-locale's check-identifier-locale.py, for L5")
    ap.add_argument("--list", action="store_true", help="print the rules and exit")
    ap.add_argument("--map", action="store_true", help="print the document map and exit")
    ap.add_argument("--selftest", action="store_true", help="prove every rule still fires")
    args = ap.parse_args(argv)

    _locale_checker_path = args.locale_checker

    if args.list:
        for rule in sorted(RULES):
            print("%s  %s" % (rule, RULES[rule]))
        return 0

    if args.map:
        print("%-14s %-34s %s" % ("SLOT", "CANONICAL", "OWED"))
        for slot in SLOTS:
            print("%-14s %-34s %s" % (slot.key, slot.canonical(),
                                      "always" if slot.always else "when earned"))
        return 0

    if args.selftest:
        return selftest()

    if not args.repo:
        ap.error("no repository given; pass a path, or use --selftest")

    root = Path(args.repo)
    if not root.is_dir():
        print("check-doc-layout: not a directory: %s" % args.repo, file=sys.stderr)
        return 2

    rules = sorted(CHECKS)
    if args.rules:
        rules = [r.strip().upper() for r in args.rules.split(",")]
        unknown = [r for r in rules if r not in CHECKS]
        if unknown:
            ap.error("unknown rule(s): %s" % ", ".join(unknown))

    findings = audit(root, rules, args.exclude)
    for finding in findings:
        print(finding.render())
    for line in _diagnostics:
        print("check-doc-layout: %s" % line, file=sys.stderr)
    print("findings: %d; rules run: %s" % (len(findings), ",".join(rules)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
