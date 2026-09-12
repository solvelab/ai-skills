#!/usr/bin/env python3
"""Measure a repository's documentation LAYOUT against the map in `SKILL.md`.

The sibling script `check-doc-structure.py` asks whether one page is navigable (rules R1-R7). This
one asks whether the repository puts its documents where the map says, calls them what the map says,
keeps each fact in the document that owns it, and keeps the two language trees in step (L1-L7).

    check-doc-layout.py REPO                     audit the repository rooted at REPO
    check-doc-layout.py --rules L2,L4 REPO       run only these rules
    check-doc-layout.py --exclude 'vendor/*' REPO   skip paths nobody in this repo owns
    check-doc-layout.py --list                   print the rule table and exit
    check-doc-layout.py --map                    print the document map and exit
    check-doc-layout.py --selftest               prove every rule still fires

Exit codes: 1 when any finding is reported, 0 when none, 2 on a usage error.

KNOWN LIMIT — what this script does NOT judge, and why:

  A CONDITIONAL slot is never reported as missing. Whether a project earns an API reference or an
     operations document is a fact about the code, not about the tree, and a script that guessed it
     would reprove the projects that correctly have neither. Only the always-slots (L1) are owed,
     and everything else is judged when it EXISTS: wrong name, wrong place, or absent from the index.
  L5 does not carry a word list. It delegates to `check-identifier-locale.py` of the `code-locale`
     skill, which already decides whether a name is English and already carries the waiver protocol.
     When that script cannot be found, L5 reports itself as NOT RUN and never passes silently —
     a rule that answers "clean" because its engine is missing is worse than a rule that is absent.
     Only that script's VERDICTS are raised here; its advisory tier is not. Probed 2026-09-12: a
     file name built on a Portuguese verb ending is a `path-pt-morphology` verdict, so L5 reports
     it, while a name whose first segment is merely absent from the English word list is advisory
     there — and a rule that failed on every unknown word would reprove product names. Known names
     of that second kind are caught by the map's legacy list under L2, which also says where each
     one goes.
  L6 compares STRUCTURE, never meaning: the twin exists, the `##` count and numbering match, the
     fenced blocks match. Whether the translated prose still says what the source says is a
     judgement about meaning across two languages, and this catalog has measured twice what a gate
     over meaning costs (7 of 10 wrong for heading nesting, 3 of 4 for justification prose).
  L7 recognizes an owned table only by its CANONICAL header row. A table with improvised columns
     escapes it. That is the deliberate trade: the alternative is guessing what a table is about
     from its content, which is the same class of judgement L6 refuses.
  A root `SECURITY.md` is accepted where it is: GitHub reads that exact path as the vulnerability
     policy. The map's security slot is `docs/<tree>/SECURITY.md`, a different document.
  Nothing here moves, renames or writes a file. Every finding names a destination; performing the
     migration is the caller's job, in one commit with the links it breaks.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# ── The map ───────────────────────────────────────────────────────────────────

#: Language-tree directory under `docs/`: `en`, `pt-BR`, `es`. `reports` is not a language.
TREE_DIR = re.compile(r"^[a-z]{2}(-[A-Za-z]{2,4})?$")

#: The tree the map names as the source. Everything else under `docs/` mirrors it.
SOURCE_TREE = "en"

#: Where transient records live, and the shape of their names.
REPORTS_DIR = "docs/reports"
DATED_NAME = re.compile(r"\d{4}-\d{2}-\d{2}")

#: Names that say "this is a record of one moment", wherever they are written.
TRANSIENT_MARKERS = (
    "homolog", "diagnose", "diagnostic", "validation-report", "progress", "todo",
    "correcao", "correção", "teste-agora", "teste_agora", "roteiro", "continuar",
    "revalidacao", "revalidação", "postmortem", "post-mortem",
)

#: `.md` files that belong at the repository root. A language suffix is accepted on the two
#: documents whose convention is a suffix rather than a tree (GitHub renders both from the root).
#: `claude` and `gemini` are agent-instruction files, the same class as `agents` — measured
#: 2026-09-12 on five fleet repositories, where the only false positive L3 produced was a root
#: `CLAUDE.md` the skill itself names as legitimate. The community-health names are GitHub's,
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

#: The README section that carries the index of every slot.
INDEX_HEADINGS = ("documentation", "documentacao")

#: How a slot the project does not earn is declared in that section.
NOT_APPLICABLE = re.compile(r"not applicable|nao se aplica", re.I)

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


# ── Findings ──────────────────────────────────────────────────────────────────


class Finding:
    """One reported defect. `path` is repo-relative; `destination` names the fix when there is one."""

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


def read(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return []


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
    out = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRECTORIES for part in rel.parts):
            continue
        s = str(rel)
        if any(fnmatch.fnmatch(s, g) or fnmatch.fnmatch(s, "*/" + g) for g in excludes):
            continue
        out.append(p)
    return out


def language_trees(root: Path) -> list[str]:
    docs = root / "docs"
    if not docs.is_dir():
        return []
    return sorted(d.name for d in docs.iterdir() if d.is_dir() and TREE_DIR.match(d.name))


def readme_index(root: Path) -> tuple[list[str], bool]:
    """(lines of the README's documentation index, index section found)."""
    readme = root / "README.md"
    if not readme.is_file():
        return [], False
    lines = strip_fences(read(readme))
    start = None
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if not m:
            continue
        if start is not None and len(m.group(1)) <= 2:
            return lines[start:i], True
        if len(m.group(1)) == 2 and fold(m.group(2)) in INDEX_HEADINGS:
            start = i
    if start is not None:
        return lines[start:], True
    return [], False


# ── The rules ─────────────────────────────────────────────────────────────────


def check_slots(root: Path, files: list[Path]) -> list[Finding]:
    """L1 — an always-slot is present, or its absence is declared. An earned slot is in the index."""
    out: list[Finding] = []
    rel = {str(p.relative_to(root)).replace("\\", "/") for p in files}
    trees = language_trees(root) or [SOURCE_TREE]
    index, has_index = readme_index(root)
    index_text = "\n".join(index)

    if not (root / "README.md").is_file():
        return [Finding("README.md", "L1", "no README.md; every project owes the entry document")]
    if not has_index:
        out.append(Finding("README.md", "L1",
                           "no '## Documentation' section; the index is where a reader learns which "
                           "slots this project earned and which it declined"))

    for slot in SLOTS:
        if not slot.always or slot.key == "entry":
            continue
        present = any(slot.canonical(t) in rel for t in trees) or slot.name in rel
        if present:
            continue
        # The declaration is a LINE, not a document. Searching the whole section accepted an index
        # that declares one slot absent and links another as proof for both.
        wanted = fold(slot.name.replace(".md", ""))
        declared = any(NOT_APPLICABLE.search(line) and wanted in fold(line) for line in index)
        if not declared:
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
    return out


def check_legacy(root: Path, files: list[Path]) -> list[Finding]:
    """L2 — a legacy name, or a canonical name in the wrong place, with its destination."""
    out = []
    trees = language_trees(root) or [SOURCE_TREE]
    canonical_paths = {slot.canonical(t) for slot in SLOTS for t in trees}
    canonical_paths |= {slot.name for slot in SLOTS if slot.at_root}
    for p in files:
        rel = str(p.relative_to(root)).replace("\\", "/")
        if rel in canonical_paths or rel.startswith(REPORTS_DIR + "/"):
            continue
        base = p.name.lower()
        for slot in SLOTS:
            if base in slot.legacy:
                out.append(Finding(rel, "L2", "legacy name for the %s slot -> %s"
                                   % (slot.key, slot.canonical())))
                break
            if base == slot.name.lower() and not slot.at_root:
                out.append(Finding(rel, "L2", "canonical name outside its tree -> %s"
                                   % slot.canonical()))
                break
    return out


def check_root(root: Path, files: list[Path]) -> list[Finding]:
    """L3 — the root carries the entry documents and nothing else."""
    out = []
    claimed = {f.path for f in check_legacy(root, files)} | {f.path for f in check_reports(root, files)}
    for p in files:
        rel = str(p.relative_to(root)).replace("\\", "/")
        if "/" in rel or rel in claimed:
            continue
        # `README.pt-BR.md` -> stem `README.pt-BR` -> the document is `README`. Split before
        # folding: folding strips the dot that separates the name from its language tag, which
        # turned `README.pt-BR` into one unrecognizable word and reproved a correct root file.
        stem = fold(p.stem.split(".")[0]).replace("-", "_")
        if stem in ROOT_ALLOWED:
            continue
        out.append(Finding(rel, "L3",
                           "loose document at the root; every tier lives under docs/<tree>/ and "
                           "every transient record under %s/" % REPORTS_DIR))
    return out


def check_reports(root: Path, files: list[Path]) -> list[Finding]:
    """L4 — a record of one moment lives with the other records of one moment."""
    out = []
    for p in files:
        rel = str(p.relative_to(root)).replace("\\", "/")
        if rel.startswith(REPORTS_DIR + "/"):
            continue
        name = fold(p.stem)
        dated = bool(DATED_NAME.search(p.stem))
        marked = any(m in name for m in (fold(x) for x in TRANSIENT_MARKERS))
        if dated or marked:
            out.append(Finding(rel, "L4",
                               "transient record outside %s/ -> %s/YYYY-MM-DD-<slug>.md"
                               % (REPORTS_DIR, REPORTS_DIR)))
    return out


def locale_checker() -> Path | None:
    """The `code-locale` checker, in the layouts this catalog installs. None when absent."""
    here = Path(__file__).resolve().parent
    for candidate in (
        here.parent.parent / "code-locale" / "references" / "check-identifier-locale.py",
        here.parent.parent.parent / "skills" / "code-locale" / "references" / "check-identifier-locale.py",
    ):
        if candidate.is_file():
            return candidate
    return None


def check_names(root: Path, files: list[Path]) -> list[Finding]:
    """L5 — delegated. This rule owns no word list; `code-locale` owns that question."""
    checker = locale_checker()
    if checker is None:
        return [Finding("", "L5", "NOT RUN: check-identifier-locale.py of the code-locale skill was "
                                  "not found beside this one; L5 never answers 'clean' without it")]
    if not files:
        return []
    proc = subprocess.run(
        [sys.executable, str(checker), *[str(p) for p in files]],
        capture_output=True, text=True,
    )
    out = []
    # The sibling names the file the way it was given it: a path when the file sits under the
    # caller's directory, a bare name when it does not. Measured 2026-09-12 on the fleet, where
    # matching on the basename alone printed a path with the repository prefix twice. Match on
    # either form, and keep the reported name only when neither resolves.
    relative = {str(p.relative_to(root)).replace("\\", "/"): p for p in files}
    for line in proc.stdout.splitlines():
        m = re.match(r"^(\S+\.md):\s+\S+\s+\[path-(\S+?):", line)
        if m and not m.group(2).startswith("en-unknown"):
            name = m.group(1)
            hit = next((rel for rel, p in relative.items()
                        if rel == name or name.endswith(rel) or p.name == name), name)
            out.append(Finding(hit, "L5", "file name is not English (%s); rename it, or waive it "
                                          "the way code-locale waives a path" % m.group(2)))
    return out


def check_parity(root: Path, files: list[Path]) -> list[Finding]:
    """L6 — the mirror is the same document in another language, not another document."""
    out = []
    trees = language_trees(root)
    if len(trees) < 2:
        return []
    if SOURCE_TREE not in trees:
        return [Finding("docs/%s" % SOURCE_TREE, "L6",
                        "mirror trees exist (%s) with no source tree; the map names docs/%s the "
                        "source and every other tree its mirror" % (", ".join(trees), SOURCE_TREE))]

    def in_tree(tree: str) -> dict[str, Path]:
        base = root / "docs" / tree
        return {str(p.relative_to(base)).replace("\\", "/"): p
                for p in files if base in p.parents}

    source = in_tree(SOURCE_TREE)
    for tree in trees:
        if tree == SOURCE_TREE:
            continue
        mirror = in_tree(tree)
        for name, src in sorted(source.items()):
            twin = mirror.get(name)
            if twin is None:
                out.append(Finding("docs/%s/%s" % (tree, name), "L6",
                                   "no mirror for docs/%s/%s; the pair is written in one commit"
                                   % (SOURCE_TREE, name)))
                continue
            a, b = read(src), read(twin)
            sa, sb = sections(a), sections(b)
            if len(sa) != len(sb):
                out.append(Finding("docs/%s/%s" % (tree, name), "L6",
                                   "%d '##' sections against %d in the source" % (len(sb), len(sa))))
                continue
            na = [m.group(1) for s in sa for m in [NUMBER_PREFIX.match(s)] if m]
            nb = [m.group(1) for s in sb for m in [NUMBER_PREFIX.match(s)] if m]
            if na != nb:
                out.append(Finding("docs/%s/%s" % (tree, name), "L6",
                                   "section numbering %s against %s in the source"
                                   % (",".join(nb) or "none", ",".join(na) or "none")))
                continue
            ca, cb = code_blocks(a), code_blocks(b)
            if ca != cb:
                differing = sum(1 for x, y in zip(ca, cb) if x != y) + abs(len(ca) - len(cb))
                out.append(Finding("docs/%s/%s" % (tree, name), "L6",
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
        rel = str(p.relative_to(root)).replace("\\", "/")
        if rel.startswith(REPORTS_DIR + "/"):
            continue
        lines = read(p)
        for line_no, cells in header_rows(lines):
            owner = OWNERSHIP.get(cells)
            if owner and p.name != owner:
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
    "README.pt-BR.md": "# T\n\nFaz uma coisa.\n\n## Documentation\n\n"
                       "- [Requisitos](docs/pt-BR/REQUIREMENTS.md)\n"
                       "- [Setup](docs/pt-BR/SETUP.md)\n"
                       "- Operation — not applicable: um ambiente\n"
                       "- Architecture — not applicable: tres modulos\n",
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

#: One injected defect per rule, as a patch over CLEAN.
SELFTEST_CASES = {
    "L1": {"docs/en/REQUIREMENTS.md": None, "docs/pt-BR/REQUIREMENTS.md": None},
    "L2": {"docs/en/TECHNICAL.md": "# Technical\n", "docs/pt-BR/TECHNICAL.md": "# Technical\n"},
    "L3": {"NOTES.md": "# Notes\n"},
    "L4": {"docs/en/DIAGNOSE-2026-04-17.md": "# D\n", "docs/pt-BR/DIAGNOSE-2026-04-17.md": "# D\n"},
    "L5": {"docs/en/revalidacao-hermes.md": "# R\n"},
    "L6": {"docs/pt-BR/SETUP.md": None},
    "L6-blocks": {"docs/pt-BR/SETUP.md": "# Setup\n\n## 1. Ambiente\n\n"
                                         "| Variavel | Tipo | Padrao | Obrigatoria | Descricao |\n"
                                         "|---|---|---|---|---|\n| `PORT` | porta | `8080` | nao | porta |\n\n"
                                         "```bash\nmake rodar\n```\n"},
    "L7": {"docs/en/ARCHITECTURE.md": "# A\n\n| Variable | Type | Default | Required | Description |\n"
                                      "|---|---|---|---|---|\n| `PORT` | port | `8080` | no | http |\n",
           "docs/pt-BR/ARCHITECTURE.md": "# A\n\n| Variavel | Tipo | Padrao | Obrigatoria | Descricao |\n"
                                         "|---|---|---|---|---|\n| `PORT` | porta | `8080` | nao | http |\n"},
}


def _materialize(base: Path, overlay: dict) -> None:
    tree = dict(CLEAN)
    tree.update(overlay)
    for rel, body in tree.items():
        if body is None:
            continue
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")


def selftest() -> int:
    import tempfile

    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        _materialize(clean, {})
        noise = [f.render() for f in audit(clean, sorted(CHECKS), [])
                 if "NOT RUN" not in f.message]
        if noise:
            failures.append("clean layout reproved: %s" % "; ".join(noise))

        for case, overlay in SELFTEST_CASES.items():
            rule = case.split("-")[0]
            base = Path(tmp) / ("case-" + case)
            _materialize(base, overlay)
            fired = [f.rule for f in audit(base, [rule], []) if "NOT RUN" not in f.message]
            if rule not in fired:
                failures.append("%s did not fire on its own injected defect" % case)

    for line in failures:
        print("selftest: %s" % line, file=sys.stderr)
    detected = len(SELFTEST_CASES) - len([f for f in failures if "did not fire" in f])
    print("selftest: %d/%d injected defects detected; clean layout %s"
          % (detected, len(SELFTEST_CASES),
             "silent" if not any("reproved" in f for f in failures) else "REPROVED"))
    return 1 if failures else 0


# ── CLI ───────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("repo", nargs="?", help="repository root to audit")
    ap.add_argument("--rules", help="comma-separated subset, e.g. L2,L4 (default: all)")
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="skip paths matching this glob; repeatable")
    ap.add_argument("--list", action="store_true", help="print the rules and exit")
    ap.add_argument("--map", action="store_true", help="print the document map and exit")
    ap.add_argument("--selftest", action="store_true", help="prove every rule still fires")
    args = ap.parse_args(argv)

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
    print("findings: %d; rules run: %s" % (len(findings), ",".join(rules)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
