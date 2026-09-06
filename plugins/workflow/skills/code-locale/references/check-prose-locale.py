#!/usr/bin/env python3
"""check-prose-locale — flag comments, docstrings and Markdown paragraphs in the wrong language.

Doctrine: the `code-locale` skill. Prose follows the repository's working language; the machine
layer is English. `check-identifier-locale.py` beside this file measures the second half and throws
the prose away (its KNOWN LIMIT 7). This script measures the first half — and only where the
repository SAYS what its prose language is.

THE DECLARATION
    A file `.code-locale` at the repository root, one `key: value` per line, `#` opens a comment:

        prose: pt-BR

    Accepted values: pt-BR, pt, en, en-US (normalised to `pt` / `en`). Any other value is an error
    (exit 2) naming the file and the accepted values — a typo must not open or close the gate in
    silence. The file is found by walking up from the scanned root (or --root) until a directory
    holds `.code-locale`, `.git`, or the filesystem ends: the declaration belongs to a repository,
    never to a directory above it. WITHOUT the file the prose direction is silent: zero findings,
    exit 0, and `--explain` says so. That silence is what makes the rule adoptable in a bilingual
    catalog and in a repository that never heard of it. `--prose <lang>` overrides the file for one
    run — the calibration mode, so a foreign tree can be measured without writing into it.

Stdlib-only, Python 3.9+. Ships beside `check-identifier-locale.py`, which it imports by path for
COMMENT_SYNTAX, EXT_LANG, the waiver regex, the allowlist and the vendored rule — the two must sit
in the same directory, and neither table is duplicated here.

    check-prose-locale.py FILE|DIR [...]                 scan files (the declaration decides)
    git diff | check-prose-locale.py --diff -            scan ADDED lines of a unified diff
    check-prose-locale.py --stdin --lang py --path x.py  scan stdin as one file
    check-prose-locale.py --prose pt-BR --report DIR     override the declaration, full breakdown
    check-prose-locale.py --explain DIR                  say what is declared, or why it is silent
    check-prose-locale.py --selftest                     prove every case still decides as recorded

WHAT IS MEASURED, AND HOW
    Comments and docstrings, through the shared tokenizer (`split_prose()` in the sibling): a run of
    consecutive full-line comments, a whole `\"\"\"` block, a whole `/* */` or `--[[ ]]` block is ONE
    fragment anchored at its first line; a comment after code on the same line is a fragment of its
    own. Markdown (.md, .markdown): every paragraph outside fenced blocks and outside the YAML
    frontmatter; table rows, headings under MIN_WORDS words, link markup, inline code and badge
    lines are skipped. Each fragment is cleaned — quoted spans ('...', "...", `...`), URLs, paths,
    identifiers (snake_case, camelCase, ALL_CAPS, dotted), numbers, #tags and @mentions removed —
    and tokenized into lowercase words with their accents kept. The words are counted against two
    CLOSED lists of function words that share no entry (prose-words-pt.txt, prose-words-en.txt;
    how they were built: prose-words.SOURCE.md). Then, with `wrong` the language the repository
    did NOT declare:

        fewer than MIN_WORDS words after cleaning            -> skipped:short
        more than CODE_SHARE of the raw tokens look like code -> skipped:code
        no hit in either list                                -> skipped:unknown
        hits_wrong >= WRONG_MIN and hits_wrong >= 2*hits_right + 1
                                                             -> the fragment reads as the wrong language
            hits_wrong >= STRONG_MIN and hits_right == 0     -> GATING for a comment or docstring
            otherwise, and always for a Markdown paragraph   -> ADVISORY
        anything else                                        -> passes (declared language, or undecided)

    Thresholds after calibration (2026-09-06, issue #179; counts in the change's tasks S.3):
    MIN_WORDS = 4, WRONG_MIN = 2, STRONG_MIN = 3, CODE_SHARE = 0.5 — the values the issue proposed,
    kept because the adjudicated precision on the gating tier was above the 0.90 bar without
    narrowing them.

THE EXITS — named on every finding line
    `locale-ok: <reason>` on the fragment's line or the line above (the identifier check's own
    marker, same regex); the path or one of its segments in `.identifier-locale-allow` (the same
    file); or translate it. LICENSE*, CHANGELOG*, NOTICE* and the vendored trees the sibling names
    are skipped without being asked.

KNOWN LIMIT — what this check does NOT measure. A passing run is not proof of compliance.
    1. String literals — user-facing strings, log messages, error texts — are extracted by the
       tokenizer and NOT judged. Decided, not forgotten: a log KEY is machine layer (the sibling's
       job), a log MESSAGE is prose whose audience may be an operator who reads another language,
       and a gate on `raise ValueError("...")` would fire on every English-speaking client. They
       are counted as `strings (not measured)` in --report so the number is visible.
    2. Only Portuguese and English. A comment in Spanish, French or Italian collects stray hits from
       the Portuguese list (`de`, `que`, `como`) and is reported as Portuguese, or as unknown.
    3. Function words, not a dictionary. A four-word technical comment with no function word at all
       (`TODO fix lru_cache eviction`) is `skipped:unknown`, never "passed"; a comment made of nouns
       alone is invisible to this check by design.
    4. Text inside a fenced code block of a .md file is not measured — it is code in another
       language, and the comments in it belong to the sibling's --markdown-fences mode.
    5. Recall is partial by design: precision first. The thresholds demand dominance and three
       uncontested hits before gating, so a short or mixed comment escapes. A gate that denies a
       correct write is switched off within a week; a gate that misses a short comment is corrected
       at review.
    6. In --diff mode a block or a fence opened on a line the diff did not add is not seen: the
       added lines are scanned as a run, so a `.md` fence that starts above the hunk is read as prose
       (advisory by construction, never a block) and a docstring that starts above it is read as
       code (skipped). The sibling records the same limit for identifiers.
    7. A triple-quoted literal that opens after code on its line (`x = \"\"\"...\"\"\"`) is a string and
       escapes by rule 1; one that opens a line is read as a docstring even when it is a literal.
    8. A file type outside the sibling's EXT_LANG and not Markdown has no comment syntax here and is
       reported as skipped, never as passing.

Exit code: 1 if any gating finding, else 0; 2 on a usage error or an unreadable declaration.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIBLING = HERE / "check-identifier-locale.py"
PT_WORDS_FILE = "prose-words-pt.txt"
EN_WORDS_FILE = "prose-words-en.txt"
DECLARATION_FILE = ".code-locale"
PROSE_VALUES = {"pt-br": "pt", "pt": "pt", "en": "en", "en-us": "en"}
LANG_NAMES = {"pt": "Portuguese", "en": "English"}

# Thresholds — see the header for what each one decides, and the change's tasks S.3 for the
# calibration that fixed them.
MIN_WORDS = 4
WRONG_MIN = 2
STRONG_MIN = 3
CODE_SHARE = 0.5
FRAGMENT_PREVIEW = 80

MARKDOWN_SUFFIXES = {".md", ".markdown"}
SKIP_FILE_PREFIXES = ("LICENSE", "LICENCE", "CHANGELOG", "NOTICE")


def load_sibling():
    """Import check-identifier-locale.py by path (its name has hyphens). A miss is a hard error:
    this check has no tables of its own and must not pretend to measure without them."""
    if not SIBLING.is_file():
        raise SystemExit(f"error: {SIBLING.name} must sit beside {Path(__file__).name} — not found at {SIBLING}")
    spec = importlib.util.spec_from_file_location("check_identifier_locale", SIBLING)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ident = load_sibling()


# ── The declaration ───────────────────────────────────────────────────────
class DeclarationError(Exception):
    """The file exists and cannot be read as a declaration. Never swallowed: exit 2 in the CLI."""


def find_declaration(start: Path) -> "tuple[Path | None, Path | None]":
    """(declaration file or None, repository boundary or None), walking up from `start`.

    The walk stops at the first directory holding `.code-locale` or `.git` — the declaration is the
    repository's, and a directory above the repository must never speak for it. The boundary is
    returned so a caller can tell "no declaration in this repository" from "not in a repository".
    """
    here = start.resolve() if start.exists() else start
    for parent in [here] + list(here.parents):
        candidate = parent / DECLARATION_FILE
        if candidate.is_file():
            return candidate, parent
        if (parent / ".git").exists():
            return None, parent
    return None, None


def load_declaration(path: Path) -> "str | None":
    """The normalised prose language (`pt`/`en`) the file declares, or None when it names none."""
    prose = None
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise DeclarationError(f"{path}:{lineno}: expected `key: value`, got {raw.strip()!r}")
        key, value = (part.strip() for part in line.split(":", 1))
        if key.lower() != "prose":
            continue                                 # other keys may come; none is read today
        lang = PROSE_VALUES.get(value.lower())
        if lang is None:
            accepted = ", ".join(("pt-BR", "pt", "en", "en-US"))
            raise DeclarationError(
                f"{path}:{lineno}: prose: {value!r} is not a language this check knows — accepted values: {accepted}")
        prose = lang
    return prose


def resolve_declaration(start: Path, override: "str | None" = None) -> "tuple[str | None, str]":
    """(declared language or None, one-line explanation). Raises DeclarationError on a bad file
    or a bad --prose value; the explanation is what --explain prints and what the hooks may relay."""
    if override:
        lang = PROSE_VALUES.get(override.lower())
        if lang is None:
            raise DeclarationError(f"--prose {override!r}: accepted values are pt-BR, pt, en, en-US")
        return lang, f"prose locale: {lang} ({override}) from --prose, overriding any {DECLARATION_FILE}"
    found, boundary = find_declaration(start)
    if found is None:
        where = f"up to {boundary} (the repository root)" if boundary else "up to the filesystem root"
        return None, (f"prose locale: no {DECLARATION_FILE} found walking up from {start} {where} — "
                      f"the prose direction is silent: 0 findings, exit 0. Declare it with a file "
                      f"`{DECLARATION_FILE}` at the repository root holding `prose: pt-BR` (or pt, en, en-US).")
    lang = load_declaration(found)
    if lang is None:
        return None, (f"prose locale: {found} carries no `prose:` key — the prose direction is silent. "
                      f"Add `prose: pt-BR` (or pt, en, en-US) to enable it.")
    return lang, f"prose locale: {lang} declared in {found}"


# ── The word lists ────────────────────────────────────────────────────────
_words_cache: "tuple[set, set] | None" = None


def _read_words(path: Path) -> set:
    words: set = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip().lower()
        if line:
            words.add(line)
    return words


def load_words() -> "tuple[set, set]":
    """(portuguese, english), loaded once per process. The intersection MUST be empty: a word in
    both lists would add a hit on both sides of every sentence, which the dominance rule cannot
    absorb, so the load refuses rather than measures."""
    global _words_cache
    if _words_cache is None:
        pt, en = _read_words(HERE / PT_WORDS_FILE), _read_words(HERE / EN_WORDS_FILE)
        shared = sorted(pt & en)
        if shared:
            raise SystemExit(f"error: {PT_WORDS_FILE} and {EN_WORDS_FILE} share words, which is evidence for "
                             f"neither language — remove them from one list: {', '.join(shared)}")
        _words_cache = (pt, en)
    return _words_cache


# ── Cleaning and classification ───────────────────────────────────────────
QUOTED_RE = re.compile(r"`[^`]*`|\"[^\"]*\"|(?<!\w)'[^']*'(?!\w)")
URL_RE = re.compile(r"\b\w+://\S+")
PATH_RE = re.compile(r"(?<!\S)[~./]?[\w.\-{}]*/[\w./\-{}]*")
SNAKE_RE = re.compile(r"\b\w*_\w*\b")
CAMEL_RE = re.compile(r"\b[a-z]+[A-Z]\w*\b|\b[A-Z][a-z]+[A-Z]\w*\b")
CAPS_RE = re.compile(r"\b[A-Z][A-Z0-9]+\b")
DOTTED_RE = re.compile(r"\b\w+(?:\.\w+)+\b")
NUMBER_RE = re.compile(r"\b\d[\w.]*\b")
TAG_RE = re.compile(r"(?<!\w)[#@]\w+")
WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]+")
CODE_CHARS = set("()[]{}=<>|\\/`;")


def clean(text: str) -> str:
    for pattern in (QUOTED_RE, URL_RE, PATH_RE, DOTTED_RE, SNAKE_RE, CAMEL_RE, CAPS_RE, NUMBER_RE, TAG_RE):
        text = pattern.sub(" ", text)
    return text


def looks_like_code(token: str) -> bool:
    """A raw whitespace token that a programmer typed for the machine rather than for the reader."""
    if any(c in CODE_CHARS for c in token):
        return True
    if token.startswith("-") and len(token) > 1:
        return True                                  # a flag: --diff, -v
    if "->" in token or "::" in token:
        return True
    return bool(SNAKE_RE.fullmatch(token) or CAMEL_RE.fullmatch(token) or CAPS_RE.fullmatch(token)
                or DOTTED_RE.fullmatch(token) or NUMBER_RE.fullmatch(token) or TAG_RE.fullmatch(token)
                or URL_RE.fullmatch(token) or PATH_RE.fullmatch(token))


def classify(text: str, declared: str, words: "tuple[set, set]") -> "tuple[str, str | None, bool]":
    """(verdict, language read, strong) for one fragment against the declared language.

    verdict is one of `skipped:short`, `skipped:code`, `skipped:unknown`, `pass`, `wrong`.
    `language read` is `pt`/`en` when the fragment reads as the wrong one, else None; `strong` is
    the gating tier (STRONG_MIN uncontested hits) and is only ever True with verdict `wrong`.
    """
    raw_tokens = text.split()
    if raw_tokens and sum(looks_like_code(t) for t in raw_tokens) > CODE_SHARE * len(raw_tokens):
        return "skipped:code", None, False
    tokens = [w.lower() for w in WORD_RE.findall(clean(text))]
    if len(tokens) < MIN_WORDS:
        return "skipped:short", None, False
    pt, en = words
    hits = {"pt": sum(t in pt for t in tokens), "en": sum(t in en for t in tokens)}
    if hits["pt"] == 0 and hits["en"] == 0:
        return "skipped:unknown", None, False
    wrong = "en" if declared == "pt" else "pt"
    if hits[wrong] >= WRONG_MIN and hits[wrong] >= 2 * hits[declared] + 1:
        strong = hits[wrong] >= STRONG_MIN and hits[declared] == 0
        return "wrong", wrong, strong
    return "pass", None, False


# ── Fragments ─────────────────────────────────────────────────────────────
class Fragment:
    __slots__ = ("kind", "line", "lines", "text")

    def __init__(self, kind: str, line: int, text: str):
        self.kind, self.line, self.lines, self.text = kind, line, 1, text

    def extend(self, text: str) -> None:
        self.text = (self.text + " " + text).strip() if self.text.strip() else text
        self.lines += 1


def fragments_from_code(text: str, lang: str) -> "list[Fragment]":
    """Comments, docstrings and strings of a source file as block-level fragments (D3 of the change).

    Consecutive full-line comments merge into one fragment; a block (`\"\"\"`, `/* */`, `--[[ ]]`)
    is one fragment whatever its length; a trailing comment after code stands alone. Strings are
    collected so the report can count them, and never judged (KNOWN LIMIT 1).
    """
    fragments: list = []
    state = None
    open_block: "Fragment | None" = None           # the fragment of the block still open
    comment_run: "Fragment | None" = None          # the run of full-line comments being merged
    for offset, raw in enumerate(text.splitlines()):
        lineno = offset + 1
        was_open = state is not None
        code, state, pieces = ident.split_prose(raw, lang, state)
        if was_open:
            kind, head = pieces.pop(0)               # the continuation of the open block
            if open_block is None:                   # a run that started mid-block (diff mode)
                open_block = Fragment(kind, lineno, head)
                fragments.append(open_block)
            else:
                open_block.extend(head)
            comment_run = None
            if state is None:
                open_block = None                    # closed on this line
        full_line_comment = (not was_open and state is None and len(pieces) == 1
                             and pieces[0][0] == "comment" and not code.strip())
        for index, (kind, piece) in enumerate(pieces):
            if full_line_comment:
                if comment_run is not None and comment_run.line + comment_run.lines == lineno:
                    comment_run.extend(piece)
                else:
                    comment_run = Fragment(kind, lineno, piece)
                    fragments.append(comment_run)
                continue
            comment_run = None
            fragment = Fragment(kind, lineno, piece)
            fragments.append(fragment)
            if state is not None and index == len(pieces) - 1:
                open_block = fragment                # the block runs past this line
        if not pieces and not was_open:
            comment_run = None
    return fragments


FENCE_RE = re.compile(r"^\s*(```|~~~)")
TABLE_RE = re.compile(r"^\s*\|")
HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.*)$")
BADGE_RE = re.compile(r"\[!\[|^\s*!\[")
LINK_RE = re.compile(r"!?\[[^\]]*\]\([^)]*\)|\[[^\]]*\]:\s*\S+")
LIST_MARK_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def fragments_from_markdown(text: str) -> "list[Fragment]":
    """Paragraphs outside fenced blocks and the YAML frontmatter, as `paragraph` fragments.

    A paragraph is a run of consecutive lines that are not blank, not a table row, not a fence, not a
    badge and not a short heading; link markup is dropped whole, and the classifier's own cleaning
    removes inline code. Headings of MIN_WORDS words or more are measured as a paragraph of their
    own; shorter ones are titles, not prose.
    """
    fragments: list = []
    lines = text.splitlines()
    i = 0
    in_fence = False
    if lines and lines[0].strip() == "---":            # YAML frontmatter
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    current: "Fragment | None" = None
    while i < len(lines):
        raw = lines[i]
        lineno = i + 1
        i += 1
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            current = None
            continue
        if in_fence:
            continue
        stripped = raw.strip()
        heading = HEADING_RE.match(raw)
        if not stripped or TABLE_RE.match(raw) or BADGE_RE.search(raw):
            current = None
            continue
        if heading:
            current = None
            title = LINK_RE.sub(" ", heading.group(1))
            if len(WORD_RE.findall(clean(title))) >= MIN_WORDS:
                fragments.append(Fragment("paragraph", lineno, title))
            continue
        body = LIST_MARK_RE.sub("", LINK_RE.sub(" ", raw)).strip()
        if current is None:
            current = Fragment("paragraph", lineno, body)
            fragments.append(current)
        else:
            current.extend(body)
    return fragments


# ── Findings ──────────────────────────────────────────────────────────────
class ProseFinding:
    def __init__(self, path: str, line: int, kind: str, lang: str, declared: str, fragment: str,
                 advisory: bool):
        self.path, self.line, self.kind, self.lang, self.declared = path, line, kind, lang, declared
        self.fragment, self.advisory = " ".join(fragment.split()), advisory

    def preview(self) -> str:
        text = self.fragment
        return text if len(text) <= FRAGMENT_PREVIEW else text[:FRAGMENT_PREVIEW - 1] + "…"

    def render(self) -> str:
        tier = "advisory" if self.advisory else "gating"
        return (
            f'{self.path}:{self.line}: [{tier}] {self.kind} reads as {self.lang}, repo prose is '
            f'{self.declared}: "{self.preview()}"\n'
            f"    translate it to {LANG_NAMES[self.declared]}, or waive with a reason: `locale-ok: <reason>` "
            f"on the line or the line above; or list the path in {ident.ALLOWLIST_FILE}"
        )


def kind_for(path: Path) -> "str | None":
    """`markdown`, a COMMENT_SYNTAX language, or None for a file type this check cannot read."""
    suffix = path.suffix.lower()
    if suffix in MARKDOWN_SUFFIXES:
        return "markdown"
    return ident.EXT_LANG.get(suffix)


def is_skipped_file(path: Path) -> bool:
    return path.name.upper().startswith(SKIP_FILE_PREFIXES)


def path_allowlisted(rel: str, allow: set) -> bool:
    if rel in allow or rel.lower() in allow:
        return True
    return any(part in allow or part.lower() in allow for part in Path(rel).parts)


def waived(lines: list, fragment: Fragment) -> bool:
    """`locale-ok:` on any line of the fragment or on the line above its first one — the reach the
    sibling gives an identifier, applied to a block."""
    first = fragment.line - 1
    span = lines[max(first - 1, 0): first + fragment.lines]
    return any(ident.WAIVER_RE.search(line) for line in span)


def scan_text(text: str, lang: str, path: str, declared: str, allow: set, first_line: int = 1,
              words: "tuple[set, set] | None" = None, stats: "Counter | None" = None) -> list:
    """Findings for one file body. `lang` is `markdown` or a COMMENT_SYNTAX key; `first_line`
    offsets the reported line numbers (diff runs, edited fragments). `stats` collects the counts
    the report prints, so a run with zero findings still says what it skipped."""
    stats = stats if stats is not None else Counter()
    words = words or load_words()
    if path_allowlisted(path, allow):
        stats["files:allowlisted"] += 1
        return []
    lines = text.splitlines()
    fragments = fragments_from_markdown(text) if lang == "markdown" else fragments_from_code(text, lang)
    findings = []
    for fragment in fragments:
        if fragment.kind == "string":
            stats["strings"] += 1
            continue
        if waived(lines, fragment):
            stats["waived"] += 1
            continue
        verdict, read_as, strong = classify(fragment.text, declared, words)
        if verdict != "wrong":
            stats[verdict] += 1
            continue
        advisory = fragment.kind == "paragraph" or not strong
        stats["advisory" if advisory else "gating"] += 1
        findings.append(ProseFinding(path, first_line + fragment.line - 1, fragment.kind, read_as,
                                     declared, fragment.text, advisory))
    return findings


def scan_diff(stream, declared: str, allow: set, words: "tuple[set, set] | None" = None,
              stats: "Counter | None" = None, vendored: "list | None" = None) -> list:
    """Added lines only — the adoption mode, for the same reason the sibling's --diff exists.

    Added lines of one hunk are scanned as a run so a block that opens and closes inside the hunk is
    one fragment; a vendored `+++` path is skipped whole and appended to `vendored` (KNOWN LIMIT 6
    names what a run cannot see).
    """
    stats = stats if stats is not None else Counter()
    findings, path, lang, lineno = [], "<diff>", None, 0
    run: list = []

    def flush() -> None:
        if run and lang:
            body = "\n".join(t for _n, t in run)
            for f in scan_text(body, lang, path, declared, allow, words=words, stats=stats):
                idx = f.line - 1
                f.line = run[idx][0] if 0 <= idx < len(run) else f.line
                findings.append(f)
        run.clear()

    for raw in stream:
        line = raw.rstrip("\n")
        if line.startswith("+++ "):
            flush()
            candidate = line[4:].strip()
            path = candidate[2:] if candidate.startswith("b/") else candidate
            lang = None
            if path == "/dev/null":
                continue
            if ident.is_vendored(Path(path)):
                stats["files:vendored"] += 1
                if vendored is not None:
                    vendored.append(path)
            elif is_skipped_file(Path(path)):
                stats["files:license"] += 1
            else:
                lang = kind_for(Path(path))
                if lang is None:
                    stats["files:no-profile"] += 1
            continue
        if line.startswith("--- "):
            continue
        if line.startswith("@@"):
            flush()
            m = re.search(r"\+(\d+)", line)
            lineno = int(m.group(1)) if m else 0
            continue
        if line.startswith("+") and not line.startswith("+++"):
            if lang:
                run.append((lineno, line[1:]))
            lineno += 1
        elif not line.startswith("-"):
            lineno += 1
    flush()
    return findings


def scan_file(path: Path, declared: str, allow: set, root: Path, words, stats: Counter) -> list:
    if ident.is_vendored(path):
        stats["files:vendored"] += 1
        return []
    if is_skipped_file(path):
        stats["files:license"] += 1
        return []
    lang = kind_for(path)
    if lang is None:
        stats["files:no-profile"] += 1
        return []
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        stats["files:unreadable"] += 1
        return []
    if ident.is_minified(body):
        stats["files:vendored"] += 1
        return []
    rel = str(ident.project_relative(path, root))
    return scan_text(body, lang, rel, declared, allow, words=words, stats=stats)


# ── Report ────────────────────────────────────────────────────────────────
def summary(stats: Counter, gating: int, advisory: int, report: bool) -> str:
    lines = [f"findings: {gating}"]
    if advisory:
        lines.append(f"  advisory: {advisory} fragment(s) read as the other language with weak evidence, "
                     "or in Markdown — they do not fail this run")
    skipped = {k: v for k, v in stats.items() if k.startswith("skipped:")}
    if report:
        parts = [f"{k.split(':', 1)[1]} {v}" for k, v in sorted(skipped.items())]
        if stats["waived"]:
            parts.append(f"waived {stats['waived']}")
        lines.append("  skipped fragments (counted, not passed): " + (", ".join(parts) or "0"))
    files = {k: v for k, v in stats.items() if k.startswith("files:")}
    if files:
        lines.append("  skipped files: " + ", ".join(f"{k.split(':', 1)[1]} {v}" for k, v in sorted(files.items())))
    if report:
        lines.append(f"  measured fragments in the declared language: {stats['pass']}")
        lines.append(f"  strings (not measured — KNOWN LIMIT 1): {stats['strings']}")
        lines.append(f"  thresholds: MIN_WORDS={MIN_WORDS} WRONG_MIN={WRONG_MIN} STRONG_MIN={STRONG_MIN} "
                     f"CODE_SHARE={CODE_SHARE}")
    return "\n".join(lines)


# ── Self-test ─────────────────────────────────────────────────────────────
EN_COMMENT = "# compute the total for the order and apply the discount before saving it\ntotal = 0\n"
PT_COMMENT = "# calcula o total do pedido e aplica o desconto antes de salvar\ntotal = 0\n"
EN_DOCSTRING = '"""Load the model once and keep it in memory for the next requests.\n\nReturns None on failure.\n"""\nx = 1\n'


def selftest() -> int:
    failed: list = []
    checked = 0
    words = load_words()

    def case(name: str, ok: bool, detail: str = "") -> None:
        nonlocal checked
        checked += 1
        print(f"  {'OK     ' if ok else 'FAILED '} {name}{('  -> ' + detail) if detail and not ok else ''}")
        if not ok:
            failed.append(name)

    def run(src: str, lang: str = "python", declared: str = "pt", allow: set = None, path: str = "orders/x.py"):
        stats: Counter = Counter()
        found = scan_text(src, lang, path, declared, allow or set(), words=words, stats=stats)
        return found, stats

    pt, en = words
    case("the two word lists share no word", not (pt & en), ", ".join(sorted(pt & en)))
    case("ambiguous words are in neither list",
         not ({"a", "as", "no", "do", "me", "sem", "so", "for", "um", "em", "para"} & (pt | en)))

    found, _ = run(PT_COMMENT)
    case("PT comment under prose: pt passes", not found, found[0].render() if found else "")
    found, _ = run(EN_COMMENT)
    case("EN comment under prose: pt is gating", len(found) == 1 and not found[0].advisory and found[0].kind == "comment",
         found[0].render() if found else "no finding")
    case("finding names the line, the kind, both languages and the exits",
         bool(found) and found[0].render().startswith('orders/x.py:1: [gating] comment reads as en, repo prose is pt: "')
         and "locale-ok:" in found[0].render() and ident.ALLOWLIST_FILE in found[0].render())
    found, _ = run(EN_DOCSTRING)
    case("EN docstring under prose: pt is gating, one finding for the block",
         len(found) == 1 and not found[0].advisory and found[0].kind == "docstring" and found[0].line == 1,
         "; ".join(f.render() for f in found) or "no finding")
    found, stats = run("# TODO: fix lru_cache\ntotal = 0\n")
    case("short technical comment is skipped:short", not found and stats["skipped:short"] == 1, str(dict(stats)))
    found, stats = run("# see 'the order total' in docs\ntotal = 0\n")
    case("quoted span is ignored (skipped:short after cleaning)", not found and stats["skipped:short"] == 1, str(dict(stats)))
    found, stats = run("# order_total = compute_total(order) -> Decimal; see OrderService.apply()\ntotal = 0\n")
    case("line that is mostly code is skipped:code", not found and stats["skipped:code"] == 1, str(dict(stats)))
    found, stats = run("# lru cache eviction threshold tuning\ntotal = 0\n")
    case("words in neither list are skipped:unknown", not found and stats["skipped:unknown"] == 1, str(dict(stats)))
    found, stats = run("# compute the total for the order\n# locale-ok: upstream comment mirrored verbatim\ntotal = 0\n")
    case("waiver on the fragment's own line silences it", not found and stats["waived"] == 1, str(dict(stats)))
    found, stats = run("# locale-ok: upstream comment mirrored verbatim\ntotal = 0  # compute the total for the order and apply it\n")
    case("waiver on the line above silences it", not found and stats["waived"] >= 1 and not stats["gating"], str(dict(stats)))
    found, stats = run(EN_COMMENT, allow={"orders/x.py"})
    case("path in the allowlist is skipped whole", not found and stats["files:allowlisted"] == 1, str(dict(stats)))
    found, stats = run(EN_COMMENT, allow={"orders"})
    case("path segment in the allowlist is skipped whole", not found and stats["files:allowlisted"] == 1)
    found, _ = run("This paragraph explains how the order total is computed for the customer.\n", lang="markdown", path="README.md")
    case(".md English paragraph under prose: pt is advisory only",
         len(found) == 1 and found[0].advisory and found[0].kind == "paragraph", "; ".join(f.render() for f in found) or "no finding")
    found, stats = run("---\ntitle: x\n---\n\n# Título\n\n| the | table | of | the | rows |\n\n```python\n# compute the total for the order and apply the discount\n```\n\n[![badge](https://x/y.svg)](https://x)\n\nUm parágrafo em português que fala do total do pedido e explica.\n", lang="markdown", path="README.md")
    case(".md frontmatter, short heading, table row, fence and badge are not measured", not found and stats["pass"] == 1, str(dict(stats)))
    found, _ = run('log.info("compute the total for the order and apply the discount")\ntotal = 0\n')
    case("string literal is not measured (KNOWN LIMIT 1)", not found, found[0].render() if found else "")
    found, _ = run("# calcula o total do pedido e aplica o desconto antes de salvar\ntotal = 0\n", declared="en")
    case("reverse direction: PT comment under prose: en is gating", len(found) == 1 and not found[0].advisory and found[0].lang == "pt",
         found[0].render() if found else "no finding")
    found, _ = run("# the total é computed for the pedido and the order\ntotal = 0\n")
    case("mixed evidence is advisory, not gating", len(found) == 1 and found[0].advisory, "; ".join(f.render() for f in found) or "no finding")
    found, _ = run("-- compute the total for the order and apply the discount\nlocal total = 0\n", lang="lua")
    case("lua line comment through the shared tokenizer", len(found) == 1 and not found[0].advisory)
    found, _ = run("/*\n * compute the total for the order\n * and apply the discount to it\n */\nconst total = 0;\n", lang="typescript")
    case("JS block comment is one fragment anchored at its first line", len(found) == 1 and found[0].line == 1 and found[0].kind == "comment")

    # --diff: added lines only, vendored path skipped and counted
    skipped: list = []
    stats = Counter()
    diff = ("--- a/orders/x.py\n+++ b/orders/x.py\n@@ -1,2 +1,4 @@\n x = 1\n+# compute the total for the order and apply the discount\n+total = 0\n y = 2\n"
            "--- /dev/null\n+++ b/node_modules/pkg/index.js\n@@ -0,0 +1 @@\n+// compute the total for the order and apply the discount\n")
    found = scan_diff(io.StringIO(diff), "pt", set(), words=words, stats=stats, vendored=skipped)
    case("--diff reports the added comment at its real line and skips the vendored file, counted",
         len(found) == 1 and found[0].line == 2 and found[0].path == "orders/x.py" and skipped == ["node_modules/pkg/index.js"],
         f"{[f.render() for f in found]} vendored={skipped}")

    # The declaration and the CLI contract, through the real entry point, in a temporary tree
    # that carries its own `.git` so the walk never reaches the runner's repository.
    with tempfile.TemporaryDirectory(prefix="prose-locale-selftest-") as td:
        tmp = Path(td)
        (tmp / ".git").mkdir()
        (tmp / "orders").mkdir()
        (tmp / "orders" / "x.py").write_text(EN_COMMENT, encoding="utf-8")

        def cli(*args, cwd=tmp):
            return subprocess.run([sys.executable, __file__, *args], cwd=cwd, capture_output=True, text=True)

        r = cli("orders/x.py")
        case("declaration absent: silent, exit 0, says the direction is off",
             r.returncode == 0 and "findings: 0" in r.stdout and DECLARATION_FILE in r.stdout, r.stdout + r.stderr)
        r = cli("--explain", "orders/x.py")
        case("--explain names the missing declaration and how to add it",
             r.returncode == 0 and "prose direction is silent" in r.stdout and "prose: pt-BR" in r.stdout, r.stdout)
        r = cli("--prose", "pt-BR", "orders/x.py")
        case("--prose override measures without a declaration: exit 1 on the gating comment",
             r.returncode == 1 and "[gating] comment reads as en" in r.stdout, r.stdout + r.stderr)
        (tmp / DECLARATION_FILE).write_text("# language of the prose\nprose: pt-BR\n", encoding="utf-8")
        r = cli("orders/x.py")
        case("declaration present: the EN comment fails the run",
             r.returncode == 1 and "findings: 1" in r.stdout, r.stdout + r.stderr)
        r = cli("x.py", cwd=tmp / "orders")
        case("declaration found walking up from a subdirectory", r.returncode == 1, r.stdout + r.stderr)
        r = subprocess.run([sys.executable, __file__, "--stdin", "--lang", "py", "--path", "orders/x.py", "--prose", "pt"],
                           input=PT_COMMENT, cwd=tmp, capture_output=True, text=True)
        case("--stdin with a PT comment passes", r.returncode == 0 and "findings: 0" in r.stdout, r.stdout + r.stderr)
        (tmp / DECLARATION_FILE).write_text("prose: portugues\n", encoding="utf-8")
        r = cli("orders/x.py")
        case("bad declaration value: exit 2 naming the file and the accepted values",
             r.returncode == 2 and DECLARATION_FILE in r.stderr and "pt-BR" in r.stderr, r.stdout + r.stderr)
        r = cli("--prose", "klingon", "orders/x.py")
        case("bad --prose value: exit 2", r.returncode == 2 and "accepted values" in r.stderr, r.stderr)
        r = cli("--bogus")
        case("unknown flag prints usage and exits 2", r.returncode == 2 and "usage:" in r.stderr)

    print()
    if failed:
        print("selftest FAILED: " + "; ".join(failed))
        return 1
    print(f"selftest OK: {checked} cases — the word lists, both directions, the skips, the waivers, the "
          "allowlist, Markdown, --diff, and the declaration through the real entry point")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────
def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--diff", metavar="FILE", help="read a unified diff ('-' for stdin), added lines only")
    ap.add_argument("--stdin", action="store_true", help="read one file body from stdin")
    ap.add_argument("--lang", help="language or extension for --stdin (py, md, lua, ...)")
    ap.add_argument("--path", default="<stdin>", help="path to report for --stdin (also matched against the allowlist)")
    ap.add_argument("--prose", metavar="LANG", help="declared prose language, overriding .code-locale (pt-BR, pt, en, en-US)")
    ap.add_argument("--root", metavar="DIR", help="where the declaration walk and the relative paths start (default: cwd)")
    ap.add_argument("--explain", action="store_true", help="say what is declared, or why the prose direction is silent")
    ap.add_argument("--report", action="store_true", help="print the full breakdown of measured and skipped fragments")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    root = Path(args.root).resolve() if args.root else Path.cwd()
    try:
        declared, explanation = resolve_declaration(root, args.prose)
    except DeclarationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.explain:
        print(explanation)
    if declared is None:
        print(f"findings: 0\n  prose direction silent: no {DECLARATION_FILE} declares a prose language "
              f"(run with --explain)")
        return 0
    if args.explain:
        pt, en = load_words()
        print(f"  {len(pt)} Portuguese and {len(en)} English function words; MIN_WORDS={MIN_WORDS} "
              f"WRONG_MIN={WRONG_MIN} STRONG_MIN={STRONG_MIN} CODE_SHARE={CODE_SHARE}")

    allow = ident.load_allowlist(root)
    words = load_words()
    stats: Counter = Counter()
    findings: list = []

    if args.diff:
        stream = sys.stdin if args.diff == "-" else open(args.diff, encoding="utf-8", errors="replace")
        findings.extend(scan_diff(stream, declared, allow, words=words, stats=stats))
    elif args.stdin:
        lang = kind_for(Path("x." + (args.lang or "").lstrip("."))) or (args.lang if args.lang in ident.COMMENT_SYNTAX else None)
        if lang is None:
            print(f"skipped: stdin (unknown language {args.lang!r})\nfindings: 0")
            return 0
        findings.extend(scan_text(sys.stdin.read(), lang, args.path, declared, allow, words=words, stats=stats))
    else:
        if not args.paths:
            ap.error("no paths given (or use --diff / --stdin)")
        targets: list = []
        for p in args.paths:
            path = Path(p)
            if path.is_dir():
                targets.extend(sorted(f for f in path.rglob("*") if f.is_file() and ".git" not in f.parts))
            else:
                targets.append(path)
        for path in targets:
            findings.extend(scan_file(path, declared, allow, root, words, stats))

    gating = [f for f in findings if not f.advisory]
    advisory = [f for f in findings if f.advisory]
    for f in gating + advisory:
        print(f.render())
    if findings:
        print()
    print(summary(stats, len(gating), len(advisory), args.report))
    return 1 if gating else 0


if __name__ == "__main__":
    sys.exit(main())
