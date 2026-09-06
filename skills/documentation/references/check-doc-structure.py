#!/usr/bin/env python3
"""Measure the organization rules of `references/information-architecture.md` against real docs.

The sibling doctrine file states seven rules. This script implements the ones whose false-positive
rate on a real repository justified a gate; the rules it does NOT implement are named in the
KNOWN LIMIT block below, and the doctrine file records the measurement that put them there.

    check-doc-structure.py FILE [FILE...]        scan the given markdown files
    check-doc-structure.py DIR                   scan every *.md under DIR, recursively
    check-doc-structure.py --rules R1,R2 FILE    run only these rules
    check-doc-structure.py --exclude 'spikes/*' DIR   skip documents nobody navigates
    check-doc-structure.py --list                print the rule table and exit
    check-doc-structure.py --selftest            prove every implemented check still fires

Exit codes: 1 when any finding is reported, 0 when none, 2 on a usage error.

KNOWN LIMIT — what this script does NOT judge, and why:

  R5 (reference describes, the why is a link) is not implemented. Deciding whether a sentence is a
     description or a justification is a judgement, and the draft heuristic that looked for causal
     markers reproved correct prose. The doctrine file carries the count.
  R6 (a `###` belongs to the `##` above it) is not implemented as a verdict. Whether a subsection
     belongs to its parent is a question about meaning, not shape. What IS implemented is a size
     signal (C6) that points a long parent section at review — it reports, it does not judge.
  A fenced code block is skipped everywhere. A rule violated only inside an example is not a
     violation of the document.
  R1 judges a document readers NAVIGATE. A one-shot record — a spike, an ADR, a post-mortem — is
     read start to finish and owes no index; the rule cannot tell the two apart from the text, so
     the consumer draws the line with `--exclude`. Measured: without it, 3 of 10 R1 findings on
     `solvelab/ferdinand@66346d4` were spike notes just over the threshold.
  Only GitHub-Flavored Markdown is parsed: ATX headings, pipe tables, fenced blocks. Setext
     headings and HTML tables are invisible to every check here.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

#: A document longer than this owes a table of contents (Standard README; Google's `[TOC]` rule).
INDEX_REQUIRED_ABOVE_LINES = 100

#: A table cell longer than this is prose wearing a table's clothes (Google Markdown style guide).
MAX_CELL_CHARS = 120

#: Above this many rows, a table of options becomes an index plus one section per option.
MAX_OPTION_TABLE_ROWS = 25

#: A parent section longer than this is reported for review, never failed outright.
LONG_SECTION_LINES = 80

#: The five alert types GitHub renders. Anything else renders as a plain blockquote.
GFM_ALERTS = ("NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION")

#: Heading texts that introduce a table of contents, in the languages this catalog documents in.
INDEX_HEADINGS = ("index", "indice", "sumario", "summary", "contents", "table of contents")

#: The field order every option entry repeats. Consistency is what makes reference usable.
ANATOMY_FIELDS = ("Tipo", "Padrão", "Faixa", "Recarrega")

FENCE = re.compile(r"^\s*(?:```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
TABLE_DIVIDER = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
OPTION_NAME = re.compile(r"^`([A-Z][A-Z0-9_]*)`$")
LINK_TARGET = re.compile(r"\]\(#([^)]+)\)")
ALERT = re.compile(r"^\s*>\s*\[!([A-Za-z]+)\]")

RULES = {
    "R1": "a document over %d lines carries an index covering every '##'" % INDEX_REQUIRED_ABOVE_LINES,
    "R2": "no table cell over %d characters" % MAX_CELL_CHARS,
    "R3": "a table of options stops at %d rows" % MAX_OPTION_TABLE_ROWS,
    "R4": "an option entry repeats the same fields in the same order",
    "R6": "a parent section over %d lines is reported for review" % LONG_SECTION_LINES,
    "R7": "an alert uses one of the five types GitHub renders",
}


# ── Findings ──────────────────────────────────────────────────────────────────


class Finding:
    """One reported defect. `line` is 1-indexed; 0 means the document as a whole."""

    def __init__(self, path: str, line: int, rule: str, message: str) -> None:
        self.path = path
        self.line = line
        self.rule = rule
        self.message = message

    def render(self) -> str:
        where = "%s:%d" % (self.path, self.line) if self.line else self.path
        return "%s: [%s] %s" % (where, self.rule, self.message)


# ── Parsing ───────────────────────────────────────────────────────────────────


def strip_fences(lines: list[str]) -> list[str]:
    """Blank out fenced blocks, keeping the line count so reported numbers stay true."""
    out: list[str] = []
    inside = False
    for line in lines:
        if FENCE.match(line):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return out


def headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """(line number, level, text) for every ATX heading outside a fence."""
    found = []
    for i, line in enumerate(lines, start=1):
        m = HEADING.match(line)
        if m:
            found.append((i, len(m.group(1)), m.group(2)))
    return found


def fold(text: str) -> str:
    """Accent-folded, lowercase, letters only. `Índice` and `Indice` are the same heading.

    Measured: without this, `docs/SETUP.md` of `solvelab/ferdinand@66346d4` was reported as having
    no index while carrying `## Índice` at line 10 — a correct document reproved, which is the one
    failure mode that gets a gate switched off.
    """
    stripped = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in stripped if unicodedata.category(c) != "Mn" and c.isalpha())


def anchor_of(text: str) -> str:
    """GitHub's anchor for a heading. Calibrated against returned HTML, not against the rule text.

    The code-span text stays: `#### \\`LEADER_TERM\\`` becomes `#leader_term`. Accents stay too;
    stripping them would reprove a link that works.
    """
    text = text.replace("`", "")
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w \-]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def tables(lines: list[str]) -> list[tuple[int, list[tuple[int, list[str]]]]]:
    """(first row's line number, [(line number, cells), ...]) for every pipe table outside a fence.

    Each row carries its OWN line number rather than an offset from the table's start. The divider
    row is dropped from the list but still occupies a line, so an offset drifts by one for every
    row after it — measured on `docs/REFERENCE.md` of `solvelab/ferdinand@66346d4`, where a cell
    reported at line 220 was actually at 219 and the line the reader opened had no defect in it.
    """
    found = []
    current: list[tuple[int, list[str]]] = []
    start = 0
    for i, line in enumerate(lines, start=1):
        m = TABLE_ROW.match(line)
        if m:
            if not current:
                start = i
            if not TABLE_DIVIDER.match(line):
                current.append((i, [c.strip() for c in m.group(1).split("|")]))
            continue
        if current:
            found.append((start, current))
            current = []
    if current:
        found.append((start, current))
    return found


# ── The checks ────────────────────────────────────────────────────────────────


def check_index(path: str, lines: list[str]) -> list[Finding]:
    """R1 — a long document carries an index, and the index covers every `##`."""
    if len(lines) <= INDEX_REQUIRED_ABOVE_LINES:
        return []

    hs = headings(lines)
    sections = [text for _, level, text in hs if level == 2]
    if not sections:
        return []

    index_start = None
    for line_no, level, text in hs:
        if level == 2 and fold(text) in {fold(h) for h in INDEX_HEADINGS}:
            index_start = line_no
            break

    if index_start is None:
        return [
            Finding(path, 0, "R1", "%d lines and no index; a reader has no way in" % len(lines))
        ]

    linked = {t.lower() for line in lines for t in LINK_TARGET.findall(line)}
    # The index heading is not a section the index owes a link to. Folded, or `Índice` is reported
    # as missing from its own list — measured on `docs/SETUP.md` of `solvelab/ferdinand@66346d4`.
    index_names = {fold(h) for h in INDEX_HEADINGS}
    missing = [
        s for s in sections if anchor_of(s) not in linked and fold(s) not in index_names
    ]
    if missing:
        return [
            Finding(
                path,
                index_start,
                "R1",
                "the index misses %d of %d sections: %s"
                % (len(missing), len(sections), ", ".join(missing[:5])),
            )
        ]
    return []


def check_cell_length(path: str, lines: list[str]) -> list[Finding]:
    """R2 — a cell over the limit is prose, and prose does not fit a cell."""
    out = []
    for _, rows in tables(lines):
        for line_no, row in rows:
            for cell in row:
                if len(cell) > MAX_CELL_CHARS:
                    out.append(
                        Finding(
                            path,
                            line_no,
                            "R2",
                            "cell of %d characters; the limit is %d — this is a section, not a row"
                            % (len(cell), MAX_CELL_CHARS),
                        )
                    )
    return out


def check_option_table(path: str, lines: list[str]) -> list[Finding]:
    """R3 — past the threshold, a catalog is navigated, not scanned.

    Counted per table AND per document. A per-table threshold alone is evaded by splitting one
    catalog across many small tables, which leaves every option without an anchor just the same —
    measured on `docs/REFERENCE.md` of `solvelab/ferdinand@66346d4`, where 101 options spread over
    per-group tables scored zero against the per-table rule.
    """
    out = []
    total = 0
    anchored = sum(
        1 for _, level, text in headings(lines) if level == 4 and OPTION_NAME.match(text.strip())
    )
    for start, rows in tables(lines):
        options = [cells for _, cells in rows if cells and OPTION_NAME.match(cells[0])]
        total += len(options)
        if len(options) > MAX_OPTION_TABLE_ROWS:
            out.append(
                Finding(
                    path,
                    start,
                    "R3",
                    "%d option rows in one table; above %d this becomes an index plus one section "
                    "per option, so each one gets an anchor" % (len(options), MAX_OPTION_TABLE_ROWS),
                )
            )
    if total > MAX_OPTION_TABLE_ROWS and anchored == 0:
        out.append(
            Finding(
                path,
                0,
                "R3",
                "%d options in tables across this document and not one section heading, so none has "
                "an anchor; above %d the catalog is navigated, not scanned"
                % (total, MAX_OPTION_TABLE_ROWS),
            )
        )
    return out


def check_anatomy(path: str, lines: list[str]) -> list[Finding]:
    """R4 — an option section repeats the same fields in the same order, or it is six documents."""
    out = []
    hs = headings(lines)
    for idx, (line_no, level, text) in enumerate(hs):
        if level != 4 or not OPTION_NAME.match(text.strip()):
            continue
        end = hs[idx + 1][0] - 1 if idx + 1 < len(hs) else len(lines)
        body = [l for l in lines[line_no:end] if l.strip()]
        if not body:
            out.append(Finding(path, line_no, "R4", "option entry with no body"))
            continue
        facts = body[0]
        present = [f for f in ANATOMY_FIELDS if "**%s**" % f in facts]
        if not present:
            out.append(
                Finding(
                    path,
                    line_no,
                    "R4",
                    "no facts line under the option; expected %s in this order"
                    % " · ".join("**%s**" % f for f in ANATOMY_FIELDS),
                )
            )
            continue
        positions = [facts.index("**%s**" % f) for f in present]
        if positions != sorted(positions):
            out.append(
                Finding(
                    path, line_no, "R4", "facts out of order: %s" % " · ".join(present)
                )
            )
    return out


def check_long_section(path: str, lines: list[str]) -> list[Finding]:
    """R6 — reports, never judges. A long parent with many children is where the tree lies."""
    out = []
    hs = [(n, lv, t) for n, lv, t in headings(lines) if lv in (2, 3)]
    for idx, (line_no, level, text) in enumerate(hs):
        if level != 2:
            continue
        end = len(lines)
        children = 0
        for next_no, next_level, _ in hs[idx + 1 :]:
            if next_level == 2:
                end = next_no - 1
                break
            children += 1
        size = end - line_no
        if size > LONG_SECTION_LINES and children >= 4:
            out.append(
                Finding(
                    path,
                    line_no,
                    "R6",
                    "%d lines and %d subsections — review whether all %d belong to this parent "
                    "(reported, not failed)" % (size, children, children),
                )
            )
    return out


def check_alerts(path: str, lines: list[str]) -> list[Finding]:
    """R7 — an alert type GitHub does not know renders as a plain quote, silently."""
    out = []
    for i, line in enumerate(lines, start=1):
        m = ALERT.match(line)
        if m and m.group(1).upper() not in GFM_ALERTS:
            out.append(
                Finding(
                    path,
                    i,
                    "R7",
                    "unknown alert type %r; GitHub renders only %s and shows the rest as a plain "
                    "blockquote" % (m.group(1), ", ".join(GFM_ALERTS)),
                )
            )
    return out


CHECKS = {
    "R1": check_index,
    "R2": check_cell_length,
    "R3": check_option_table,
    "R4": check_anatomy,
    "R6": check_long_section,
    "R7": check_alerts,
}


def scan(path: Path, rules: list[str]) -> list[Finding]:
    raw = path.read_text(encoding="utf-8").splitlines()
    lines = strip_fences(raw)
    out: list[Finding] = []
    for rule in rules:
        out.extend(CHECKS[rule](str(path), lines))
    return sorted(out, key=lambda f: (f.path, f.line, f.rule))


# ── Self-test ─────────────────────────────────────────────────────────────────

#: One injected defect per implemented check. A check that stops firing fails here, which is the
#: only gate over this script: `scripts/validate-skills.py` never opens a `.py` under references/.
SELFTEST_CASES = {
    "R1": "# T\n\n## A\n\n" + "x\n" * 120,
    "R2": "# T\n\n| a | b |\n|---|---|\n| `X` | %s |\n" % ("y" * 130),
    "R3": "# T\n\n| v | d |\n|---|---|\n"
    + "".join("| `VAR_%02d` | d |\n" % i for i in range(30)),
    # the per-document arm: many small tables, none over the per-table threshold
    "R3-spread": "# T\n"
    + "".join(
        "\n## G%d\n\n| v | d |\n|---|---|\n" % g
        + "".join("| `V%d_%02d` | d |\n" % (g, i) for i in range(10))
        for g in range(4)
    ),
    "R4": "# T\n\n#### `SOME_VAR`\n\nno facts line here\n",
    "R6": "# T\n\n## Parent\n\n"
    + "".join("### Child %d\n\n%s\n" % (i, "x\n" * 25) for i in range(4)),
    "R7": "# T\n\n> [!DANGER]\n> not a GitHub type\n",
}

#: A document that violates nothing implemented here. A check firing on it is a false positive.
SELFTEST_CLEAN = (
    "# T\n\n## Index\n\n- [Group](#group)\n\n## Group\n\n"
    "| v | d |\n|---|---|\n| `A_VAR` | short |\n\n"
    "#### `A_VAR`\n\n**Tipo** port · **Padrão** `1` · **Faixa** `1`-`2` · **Recarrega** no\n\n"
    "Does one thing.\n\n> [!NOTE]\n> Fine.\n"
)


def selftest() -> int:
    import tempfile

    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for case, body in SELFTEST_CASES.items():
            rule = case.split("-")[0]
            p = Path(tmp) / ("case-%s.md" % case)
            p.write_text(body, encoding="utf-8")
            fired = [f.rule for f in scan(p, [rule])]
            if rule not in fired:
                failures.append("%s did not fire on its own injected defect" % case)

        clean = Path(tmp) / "clean.md"
        clean.write_text(SELFTEST_CLEAN, encoding="utf-8")
        noise = [f.render() for f in scan(clean, sorted(CHECKS))]
        if noise:
            failures.append("clean document reproved: %s" % "; ".join(noise))

    for line in failures:
        print("selftest: %s" % line, file=sys.stderr)
    print(
        "selftest: %d/%d injected defects detected; clean document %s"
        % (len(SELFTEST_CASES) - len([f for f in failures if "did not fire" in f]), len(SELFTEST_CASES),
           "silent" if not any("reproved" in f for f in failures) else "REPROVED")
    )
    return 1 if failures else 0


# ── CLI ───────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("paths", nargs="*", help="markdown files, or directories to walk for *.md")
    ap.add_argument("--rules", help="comma-separated subset, e.g. R1,R2 (default: all implemented)")
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="skip paths matching this glob; repeatable. For records nobody navigates (spikes, ADRs)",
    )
    ap.add_argument("--list", action="store_true", help="print the implemented rules and exit")
    ap.add_argument("--selftest", action="store_true", help="prove every check still fires")
    args = ap.parse_args(argv)

    if args.list:
        for rule in sorted(RULES):
            state = "implemented" if rule in CHECKS else "review-only"
            print("%s  %-12s %s" % (rule, state, RULES[rule]))
        return 0

    if args.selftest:
        return selftest()

    if not args.paths:
        ap.error("no paths given; pass files or a directory, or use --selftest")

    rules = sorted(CHECKS)
    if args.rules:
        rules = [r.strip().upper() for r in args.rules.split(",")]
        unknown = [r for r in rules if r not in CHECKS]
        if unknown:
            ap.error("unknown or unimplemented rule(s): %s" % ", ".join(unknown))

    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print("check-doc-structure: no such path: %s" % raw, file=sys.stderr)
            return 2

    if args.exclude:
        import fnmatch

        files = [
            f
            for f in files
            if not any(fnmatch.fnmatch(str(f), g) or fnmatch.fnmatch(str(f), "*/" + g) for g in args.exclude)
        ]

    findings: list[Finding] = []
    for f in files:
        findings.extend(scan(f, rules))

    for finding in findings:
        print(finding.render())
    print(
        "findings: %d in %d file(s); rules run: %s"
        % (len(findings), len(files), ",".join(rules))
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
