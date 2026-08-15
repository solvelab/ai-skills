#!/usr/bin/env python3
"""check-identifier-locale — flag non-English identifiers in the machine layer.

Doctrine: the `code-locale` skill. Prose (comments, docstrings, commit and issue text, docs,
user-facing strings) follows the repository's working language. Anything a machine parses —
identifiers, file and module names, REST path segments, DB tables and columns, enum values, event
and topic names, config keys, log field keys — is English and ASCII. This script checks the second
half only.

Stdlib-only, Python 3.9+. Copy it into a target repository and wire it into pre-commit and CI.

    check-identifier-locale.py FILE [FILE...]     scan files
    git diff | check-identifier-locale.py --diff -   scan ADDED lines of a unified diff
    check-identifier-locale.py --markdown-fences DIR  scan language-tagged fences in .md files
    check-identifier-locale.py --stdin --lang python  scan stdin as one file
    check-identifier-locale.py --selftest            prove every tier still fires

WHY --diff IS THE DEFAULT ADOPTION MODE
    Whole-tree enforcement turns a legacy repository red on day one, and a check that blocks every
    pipeline is bypassed within a week. `--diff` reads only added lines, which is the mechanical
    form of the "new code is English; existing names migrate by tier" policy in
    `references/migration.md`.

KNOWN LIMIT — what this check does NOT catch. A passing run is not proof of full compliance.
    1. Portuguese words that are also English words are deliberately absent from the lexicon
       (`data`, `total`, `real`, `local`, `custom`, `nota`, `valor`, `sensor`, `motor`, `area`,
       `agenda`, `media`, `mesa`, `favor`). `dataUsuario` is caught through `usuario`; a bare
       `data` is not, and never will be.
    2. This is a word list, not a language model. Open vocabulary escapes: any Portuguese noun
       outside LEXICON passes.
    3. Suffixes -mento, -dor and -vel are NOT rules, because of `memento`, `vendor` and `level`.
       A CI blocker on `vendorId` would end the rule, so those families escape by design.
    4. Segments under MIN_SEGMENT characters are skipped, so abbreviations escape: `qtd`, `usr`,
       `pgto`, `end`.
    5. Spanish, Italian and French are out of scope.
    6. Identifiers built at runtime escape: dynamic SQL, template strings, getattr, Lua table keys
       assembled from variables.
    7. Comments, docstrings and non-path string literals are stripped before analysis, including
       multi-line blocks (Python triple quotes, `/* */`, `--[[ ]]`) whose interior lines carry no
       delimiter. They are the prose layer, and scanning them would fire on every correct
       Portuguese comment. In --diff mode this holds only for blocks whose added lines are
       contiguous in the hunk; a block opened in an added line and closed in an unchanged one keeps
       the scanner in prose state to the end of the run, which under-reports rather than over-reports.
    8. In --markdown-fences mode, untagged fences are skipped. This is load-bearing, not an
       oversight: a fence of Portuguese commit-message examples is prose and must not be flagged.
    9. Branch names, PR titles and issue text are not files and are never scanned. They are
       convention-only.
    10. Only the languages in COMMENT_SYNTAX are tokenized. Files with any other extension are
       skipped and reported as skipped, never counted as passing.

Exit code: 1 if any finding, else 0.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

MIN_SEGMENT = 4
ALLOWLIST_FILE = ".identifier-locale-allow"
WAIVER_RE = re.compile(r"locale-ok\s*:\s*(\S.*)$")

# ── Portuguese signals ────────────────────────────────────────────────────
# Tier 2: morphology, matched against a whole segment.
# A bare `oes$` was tried and removed: it fires on the English `Does`, found in `DoesNotContain`
# in skills/assettoserver-plugin/SKILL.md:263 and skills/bug-hunter/references/track-dotnet-plugin.md:19.
# Only the consonant-led forms of the -ões plural are kept, which no English word carries.
MORPHOLOGY = re.compile(r"(cao|coes|soes|zoes|agem|idade|ancia|encia)$")

# Tier 3: verb heads. A function named for a Portuguese action is the single most common form of
# the defect, because the verb carries no domain meaning at all.
VERBS = {
    "criar", "buscar", "atualizar", "excluir", "deletar", "listar", "salvar", "enviar", "obter",
    "cadastrar", "consultar", "remover", "alterar", "gerar", "carregar", "inserir", "editar",
    "validar", "calcular", "processar", "tratar", "montar", "apagar", "pesquisar", "adicionar",
}

# Tier 4: nouns. Every entry must be a word that is NOT also an English word — see ENGLISH_COLLISIONS
# and the assertion below.
NOUNS = {
    "usuario", "usuarios", "senha", "pedido", "pedidos", "cliente", "clientes", "produto",
    "produtos", "endereco", "cidade", "telefone", "pagamento", "entrega", "veiculo", "veiculos",
    "motorista", "jogador", "jogadores", "arquivo", "arquivos", "sobrenome", "fatura",
    "cobranca", "cadastro", "empresa", "funcionario", "permissao", "tentativa", "quantidade",
    "preco", "desconto", "saldo", "corrida", "corridas", "compra", "venda", "estoque", "carrinho",
    "assinatura", "mensagem", "recibo", "apelido", "aniversario", "bairro", "estado", "codigo",
}
# `pasta` was here and was removed: the field score below found it firing on the English noun.


# Words that exist in both languages. Keeping them out of the lexicon is what makes the check
# usable; the assertion below stops a future contributor from quietly adding one back and turning
# the gate into noise.
ENGLISH_COLLISIONS = {
    # `pasta` earned its place here: it shipped in the lexicon and fired on the English noun in
    # vendored JavaScript during the first field score (970k lines, 2 hits, both false).
    "pasta",
    "data", "total", "real", "local", "custom", "media", "agenda", "area", "sensor", "motor",
    "favor", "valor", "nota", "mesa", "banana", "final", "normal", "material", "capital", "animal",
    "central", "digital", "global", "legal", "modal", "moral", "natural", "oral", "radio", "solo",
    "taxa", "via", "visa", "gene", "base", "casino", "extra", "gala", "logo", "mango", "opera",
    "piano", "radar", "regime", "salsa", "silo", "tempo", "torso", "vista",
}

# Proper names and handles that the morphology tier wrongly matches. Not English words, so they do
# not belong in ENGLISH_COLLISIONS, but not Portuguese either. This set grows only from a false
# positive observed in real code — never from imagination — and each entry names where it was seen.
# Seeds from the first field score (970k lines of vendored JavaScript): `sfrancia` (a GitHub
# handle), `valencia` (a place name), both matched by `-ancia`.
NOT_PORTUGUESE = {
    "sfrancia", "valencia", "francia", "provencia", "florencia",
}

_overlap = (VERBS | NOUNS) & (ENGLISH_COLLISIONS | NOT_PORTUGUESE)
assert not _overlap, (
    "lexicon contains words that are also English or known proper names: "
    + ", ".join(sorted(_overlap))
    + " — a word in both languages produces false positives and must stay out"
)

# Domain terms kept on purpose. Brazilian legal and regulatory instruments have no faithful English
# translation, and inventing one destroys traceability to the law, the regulator's schema and the
# payment provider's API. See `code-locale` for the rule that governs this list.
# Deliberately SHORT. This list is the only place a foreign word passes with no reviewer seeing it,
# so it holds unambiguous named instruments and nothing else. Anything else — a term that is
# arguably domain-specific, a term someone likes better in Portuguese — goes through the item's
# Glossary or an inline `locale-ok: <reason>`, where a human reads the reason. A broad auto-allow
# list is how "it is a domain term" stops meaning anything.
#
# Two exclusions worth naming:
#   - `simples` is NOT here. It is the ordinary adjective; only the compound `simples_nacional`
#     names the tax regime, and `simples = True` must not pass silently.
#   - Acronyms under MIN_SEGMENT (cpf, cep, pix, nfe, rg, sus, iss, cbo, mei, pis, ie, im) are not
#     listed: the length floor already lets them through, and listing them would suggest this set
#     is doing work it is not.
DOMAIN_KEEP = {
    "cnpj", "boleto", "nfse", "sefaz", "renavam", "crlv", "cofins", "icms", "cnae", "fgts",
    "inss", "nota_fiscal", "notafiscal", "simples_nacional",
}

# ── Language profiles ─────────────────────────────────────────────────────
# (line comment prefixes, block comment pairs, string quote sequences)
COMMENT_SYNTAX = {
    "python": (["#"], [('"""', '"""'), ("'''", "'''")], ['"""', "'''", '"', "'"]),
    "lua": (["--"], [("--[[", "]]")], ['"', "'", "[["]),
    "javascript": (["//"], [("/*", "*/")], ['"', "'", "`"]),
    "typescript": (["//"], [("/*", "*/")], ['"', "'", "`"]),
    "csharp": (["//"], [("/*", "*/")], ['"', "'"]),
    "sql": (["--"], [("/*", "*/")], ["'", '"']),
    "yaml": (["#"], [], ['"', "'"]),
    "json": ([], [], ['"']),
    "bash": (["#"], [], ['"', "'"]),
}

EXT_LANG = {
    ".py": "python", ".lua": "lua", ".js": "javascript", ".jsx": "javascript",
    ".mjs": "javascript", ".cjs": "javascript", ".ts": "typescript", ".tsx": "typescript",
    ".cs": "csharp", ".sql": "sql", ".yml": "yaml", ".yaml": "yaml", ".json": "json",
    ".sh": "bash", ".bash": "bash",
}

FENCE_LANG = {
    "python": "python", "py": "python", "lua": "lua", "js": "javascript",
    "javascript": "javascript", "jsx": "javascript", "ts": "typescript",
    "typescript": "typescript", "tsx": "typescript", "csharp": "csharp", "cs": "csharp",
    "sql": "sql", "yaml": "yaml", "yml": "yaml", "json": "json", "bash": "bash", "sh": "bash",
}

# Keywords are not identifiers the author chose, so they never carry a locale decision.
KEYWORDS = {
    "def", "class", "return", "import", "from", "for", "while", "if", "else", "elif", "try",
    "except", "finally", "with", "pass", "raise", "yield", "lambda", "async", "await", "self",
    "none", "true", "false", "null", "local", "function", "end", "then", "nil", "require",
    "const", "let", "var", "new", "this", "export", "default", "interface", "type", "public",
    "private", "protected", "static", "void", "string", "int", "bool", "float", "select",
    "insert", "update", "delete", "create", "table", "where", "join", "index", "alter", "add",
    "column", "primary", "key", "foreign", "references", "not", "and", "or", "in", "is", "as",
}

# String literals that ARE the machine layer, re-added after literals are stripped.
PATH_LITERAL = re.compile(r"^/[a-z0-9\-/_{}:.]+$", re.I)
DDL_RE = re.compile(r"\b(create\s+table|alter\s+table|add\s+column|create\s+index)\b", re.I)

IDENT_RE = re.compile(r"[A-Za-z_À-ɏ][A-Za-z0-9_À-ɏ]*")
SEGMENT_SPLIT = re.compile(r"[_\-./]+")
CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


class Finding:
    def __init__(self, path: str, line: int, token: str, segment: str, tier: str):
        self.path, self.line, self.token, self.segment, self.tier = path, line, token, segment, tier

    def render(self) -> str:
        return (
            f"{self.path}:{self.line}: {self.token}  [{self.tier}: '{self.segment}']\n"
            f"    machine layer must be English (code-locale). If this name is correct as written, "
            f"add a reason:\n"
            f"      # locale-ok: <why this term has no faithful English name>\n"
            f"    or grandfather it in {ALLOWLIST_FILE}:\n"
            f"      {self.token}"
        )


def strip_prose(line: str, lang: str, state: "str | None" = None) -> "tuple[str, str | None]":
    """Remove comments and string literals — the prose layer — but keep machine-layer literals.

    Character-scanned rather than regex-replaced, because a '#' inside a string is not a comment
    and a quote inside a comment does not open a string.

    `state` carries an open block across lines: it is the closing delimiter still being waited for,
    or None. Returns (code, new_state). Line-at-a-time scanning was the original design and it was
    wrong — the interior lines of a `\"\"\"` docstring or a `/* */` block carry no delimiter at all,
    so they were read as code and every Portuguese word in them was flagged as an identifier. On one
    real Portuguese codebase that was 4219 of 4340 findings (see issue #85).
    """
    line_syntax, blocks, quotes = COMMENT_SYNTAX.get(lang, (["#"], [], ['"', "'"]))

    if state is not None:                           # continuing a block opened on an earlier line
        close = line.find(state)
        if close == -1:
            return "", state                        # the whole line is prose
        line = line[close + len(state):]            # resume scanning after the closer
        state = None

    out: list[str] = []
    i = 0
    while i < len(line):
        # Block openers are tested FIRST: `--[[` starts with the Lua line comment `--`, and `\"\"\"`
        # starts with the Python quote `"`. Checking either of those first would swallow the block.
        opener = next((o for o, _c in blocks if line.startswith(o, i)), None)
        if opener is not None:
            closer = next(c for o, c in blocks if o == opener)
            close = line.find(closer, i + len(opener))
            if close == -1:
                return "".join(out), closer         # block runs past this line
            out.append(" ")
            i = close + len(closer)
            continue
        if any(line.startswith(p, i) for p in line_syntax):
            break                                   # rest of the line is prose
        matched_quote = next((q for q in quotes if line.startswith(q, i)), None)
        if matched_quote:
            close = line.find(matched_quote, i + len(matched_quote))
            if close == -1:
                break                               # unterminated: treat the remainder as prose
            body = line[i + len(matched_quote):close]
            # A literal that is a route path or a DDL fragment IS the machine layer.
            if PATH_LITERAL.match(body) or DDL_RE.search(body):
                out.append(" " + body.replace("/", " ") + " ")
            else:
                out.append(" ")
            i = close + len(matched_quote)
            continue
        out.append(line[i])
        i += 1
    return "".join(out), state


def segments(identifier: str) -> list[str]:
    parts: list[str] = []
    for chunk in SEGMENT_SPLIT.split(identifier):
        if chunk:
            parts.extend(p for p in CAMEL_SPLIT.split(chunk) if p)
    return parts


def deaccent(word: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", word) if not unicodedata.combining(c))


def classify(segment: str) -> "str | None":
    """Return the tier name that fires on this whole segment, or None."""
    raw = segment.lower()
    if len(raw) < MIN_SEGMENT:
        return None
    if any(ord(c) > 127 for c in raw):
        return "non-ascii"
    if raw in DOMAIN_KEEP or raw in KEYWORDS or raw in NOT_PORTUGUESE:
        return None
    if raw in VERBS:
        return "pt-verb"
    if raw in NOUNS:
        return "pt-noun"
    if MORPHOLOGY.search(raw) and raw not in ENGLISH_COLLISIONS:
        return "pt-morphology"
    return None


# Vendored and generated code is not this project's machine layer, and minified bundles produce
# meaningless identifiers. Earned by the first field score: 7 of 9 findings came from
# `.vscode-test/` bundles, which is how a real signal gets buried.
VENDOR_PARTS = {
    "node_modules", ".venv", "venv", "vendor", "dist", "build", "out", ".vscode-test",
    "site-packages", "third_party", ".next", "__pycache__", "coverage",
}
MINIFIED_LINE = 400          # a source line this long is generated, not written


def is_vendored(path: Path) -> bool:
    return any(part in VENDOR_PARTS for part in path.parts) or ".min." in path.name


def is_minified(text: str) -> bool:
    return any(len(line) > MINIFIED_LINE for line in text.splitlines()[:200])


def load_allowlist(start: Path) -> set:
    allow: set = set()
    for parent in [start] + list(start.parents):
        f = parent / ALLOWLIST_FILE
        if f.is_file():
            for raw in f.read_text(encoding="utf-8").splitlines():
                token = raw.split("#", 1)[0].strip()
                if token:
                    allow.add(token)
            break
    return allow


def scan_text(text: str, lang: str, path: str, allow: set, first_line: int = 1) -> list:
    findings = []
    lines = text.splitlines()
    state: "str | None" = None                       # open block carried across lines
    for offset, raw in enumerate(lines):
        lineno = first_line + offset
        code, state = strip_prose(raw, lang, state)
        if WAIVER_RE.search(raw):
            continue                                 # waived with a stated reason
        prev = lines[offset - 1] if offset else ""
        if WAIVER_RE.search(prev):
            continue                                 # waiver on the preceding line
        for match in IDENT_RE.finditer(code):
            token = match.group(0)
            if token in allow or token.lower() in allow:
                continue
            if token.lower() in DOMAIN_KEEP:
                continue
            for seg in segments(token):
                tier = classify(seg)
                if tier == "non-ascii" and deaccent(seg).lower() in DOMAIN_KEEP:
                    continue
                if tier:
                    findings.append(Finding(path, lineno, token, seg, tier))
                    break
    return findings


# ── Input modes ───────────────────────────────────────────────────────────
FENCE_RE = re.compile(r"^([ \t]*)```(\w*)\n(.*?)^\1```", re.S | re.M)


def scan_markdown_fences(path: Path, allow: set) -> list:
    """Only language-tagged fences. An untagged fence may be prose — see KNOWN LIMIT 8."""
    text = path.read_text(encoding="utf-8")
    findings = []
    for m in FENCE_RE.finditer(text):
        lang = FENCE_LANG.get(m.group(2).lower())
        if not lang:
            continue
        indent = m.group(1)
        body = m.group(3)
        if indent:
            body = "\n".join(
                line[len(indent):] if line.startswith(indent) else line
                for line in body.splitlines()
            )
        first = text[: m.start(3)].count("\n") + 1
        findings.extend(scan_text(body, lang, str(path), allow, first_line=first))
    return findings


def scan_diff(stream, allow: set) -> list:
    """Added lines only. This is what makes the rule adoptable in a legacy repository."""
    findings, path, lineno, lang = [], "<diff>", 0, None
    run: list = []                                   # consecutive added lines, scanned together

    def flush() -> None:
        if not run or not lang:
            run.clear()
            return
        body = "\n".join(t for _n, t in run)
        base = run[0][0]
        for f in scan_text(body, lang, path, allow, first_line=base):
            idx = f.line - base
            f.line = run[idx][0] if 0 <= idx < len(run) else f.line
            findings.append(f)
        run.clear()

    for raw in stream:
        line = raw.rstrip("\n")
        if line.startswith("+++ "):
            flush()
            candidate = line[4:].strip()
            if candidate.startswith("b/"):
                candidate = candidate[2:]
            path = candidate
            lang = EXT_LANG.get(Path(path).suffix.lower())
            continue
        if line.startswith("@@"):
            flush()
            m = re.search(r"\+(\d+)", line)
            lineno = int(m.group(1)) if m else 0
            continue
        if line.startswith("+") and not line.startswith("+++"):
            if lang:
                # Added lines are scanned as a RUN, not individually: a docstring opened on one
                # added line closes on another, and scanning each alone reintroduces the very bug
                # this mode is supposed to enforce against (issue #85). Runs are flushed whenever
                # the file or the hunk changes.
                run.append((lineno, line[1:]))
            lineno += 1
        elif not line.startswith("-"):
            lineno += 1
    flush()
    return findings


# ── Self-test ─────────────────────────────────────────────────────────────
SELFTEST_HITS = [
    ("non-ascii", "python", "def validar_endereço(x):\n    return x\n"),
    ("pt-verb", "python", "def buscar_by_id(x):\n    return x\n"),
    ("pt-noun", "python", "usuario_count = 1\n"),
    ("pt-morphology", "python", "configuracao = {}\n"),
    ("pt-plural", "python", "permissoes = []\n"),
    ("route literal", "python", 'app.get("/api/v1/pedidos")\n'),
    # Guards the opposite failure of the #85 fix: a scanner that enters a block and never leaves
    # would report 0 everywhere and look perfect.
    ("resumes after block", "python",
     '"""\nDocstring em português com saldo e transação.\n"""\ndef buscar_usuario(x):\n    return x\n'),
]

SELFTEST_CLEAN = [
    ("english code", "python", "def find_user_by_id(user_id):\n    return user_id\n"),
    ("BR domain term", "python", "class Customer:\n    cpf = ''\n    boleto_id = ''\n"),
    ("PT comment", "python", "# busca o usuario pelo endereco cadastrado\nuser = 1\n"),
    ("PT string value", "python", 'status = {"status": "pending", "label": "Pendente"}\n'),
    ("PT log message", "python", 'log.info("pedido criado com sucesso", extra={"order_id": 1})\n'),
    ("short segments", "python", "qtd = 1\nusr = 2\nend_at = 3\n"),
    ("english collisions", "python", "data_total = 1\nlocal_media = 2\nsensor_area = 3\n"),
    ("waived", "python", "# locale-ok: SEFAZ document, no faithful translation\nnota_fiscal_x = 1\n"),
    ("english suffixes", "typescript", "const vendorId = 1; const level = 2; const memento = 3;\n"),
    # Regression: `Does` ends in -oes. Found in the catalog by the first full run of this check.
    ("english -oes", "csharp", "Assert.That(x, Does.NotContain(y)); var shoes = 1; var heroes = 2;\n"),
    # Regression: both earned by the first field score over 970k lines of real code.
    ("english pasta", "javascript", "const pasta = require('pasta'); const pastaSauce = 1;\n"),
    ("proper name -ancia", "javascript", "const sfrancia = 1; const valencia = 2;\n"),
    ("PT lua comment", "lua", '-- cria o jogador\nlocal playerId = 1\n'),
    # Regression for #85: interior lines of a multi-line block carry no delimiter. Scanning them
    # line-by-line produced 4219 of 4340 findings on one real Portuguese codebase.
    ("PT python docstring", "python",
     '"""\nAtualiza o cadastro do usuario e devolve a transação.\nVerifica o saldo.\n"""\nx = 1\n'),
    ("PT js block comment", "typescript",
     "/*\n * calcula o saldo do usuario\n * verifica a transação\n */\nconst total = 1;\n"),
    ("PT lua block comment", "lua",
     "--[[\n  cria o jogador e devolve a permissão\n]]\nlocal playerId = 1\n"),
]


def selftest() -> int:
    failed = []
    for name, lang, src in SELFTEST_HITS:
        got = scan_text(src, lang, "<selftest>", set())
        status = "CAUGHT " if got else "MISSED "
        print(f"  {status} hit/{name}")
        if not got:
            failed.append(f"hit/{name}")
    for name, lang, src in SELFTEST_CLEAN:
        got = scan_text(src, lang, "<selftest>", set())
        status = "CLEAN  " if not got else "FALSE+ "
        print(f"  {status} clean/{name}")
        if got:
            failed.append(f"clean/{name} -> {got[0].token}:{got[0].segment}")
    print()
    if failed:
        print("selftest FAILED: " + "; ".join(failed))
        return 1
    print(f"selftest OK: {len(SELFTEST_HITS)} tiers fire, {len(SELFTEST_CLEAN)} clean cases stay silent")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────
def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--diff", metavar="FILE", help="read a unified diff ('-' for stdin)")
    ap.add_argument("--stdin", action="store_true", help="read one file body from stdin")
    ap.add_argument("--lang", help="language for --stdin")
    ap.add_argument("--markdown-fences", action="store_true",
                    help="scan language-tagged fences inside .md files")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    allow = load_allowlist(Path.cwd())
    findings: list = []
    skipped: list = []
    vendored: list = []

    if args.diff:
        stream = sys.stdin if args.diff == "-" else open(args.diff, encoding="utf-8")
        findings.extend(scan_diff(stream, allow))
    elif args.stdin:
        lang = EXT_LANG.get("." + (args.lang or ""), args.lang)
        if lang not in COMMENT_SYNTAX:
            print(f"skipped: stdin (unknown language {args.lang!r})")
            return 0
        findings.extend(scan_text(sys.stdin.read(), lang, "<stdin>", allow))
    else:
        targets: list = []
        for p in args.paths:
            path = Path(p)
            if path.is_dir():
                targets.extend(sorted(path.rglob("*.md")) if args.markdown_fences
                               else sorted(f for f in path.rglob("*") if f.is_file()))
            else:
                targets.append(path)
        for path in targets:
            if args.markdown_fences:
                if path.suffix.lower() == ".md":
                    findings.extend(scan_markdown_fences(path, allow))
                continue
            lang = EXT_LANG.get(path.suffix.lower())
            if not lang:
                skipped.append(str(path))
                continue
            if is_vendored(path):
                vendored.append(str(path))
                continue
            body = path.read_text(encoding="utf-8")
            if is_minified(body):
                vendored.append(str(path))
                continue
            findings.extend(scan_text(body, lang, str(path), allow))

    for f in findings:
        print(f.render())
    print(f"\nfindings: {len(findings)}")
    if skipped:
        print(f"  skipped (no language profile): {len(skipped)} file(s) — reviewed by hand, not passed")
    if vendored:
        print(f"  skipped (vendored/generated/minified): {len(vendored)} file(s) — not this project's machine layer")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
