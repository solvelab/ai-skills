---
name: code-locale
description: >-
  Decides which natural language each artifact of a change is written in: prose follows the
  repository's working language, and anything a machine parses is English. Use when naming a
  variable, function, class, file, module, REST route segment, query param, DB table or column,
  enum value, event or topic name, config key or log field; when reviewing a diff or PR that
  introduces names; when a backlog item written in another language is about to become code; when
  deciding whether a domain term like CPF, CNPJ, boleto, PIX or nota fiscal keeps its name; when an
  external API's payload fields are in another language; or when the user says "código em
  português", "nome de variável em inglês", "rota em português", "traduz esse nome", "identificador
  em inglês", "should this be in English", "our code is half Portuguese", "naming convention",
  "ubiquitous language", "anti-corruption layer". Covers the prose/machine boundary, the
  untranslatable-domain-term exception and its gate, the grooming glossary, the new-code-only
  migration policy, and a shipped detector a repository can wire into CI. Do NOT use for the
  language of commit subjects or PR bodies (that is conventional-commit), for the language of
  documentation prose (that is documentation), for format-level naming conventions like case style
  or test-method patterns (those live in each stack's skill), or for i18n and user-facing
  translation.
metadata:
  author: solvelab
  version: 1.0.0
  category: process
license: MIT
compatibility: >-
  The doctrine is language- and stack-agnostic and needs no runtime. The shipped detector
  `references/check-identifier-locale.py` needs Python 3.9+ and no third-party package; it
  tokenizes Python, Lua, JavaScript, TypeScript, C#, SQL, YAML, JSON and Bash, and reports any
  other file type as skipped rather than passing.
---

# Code locale — prose follows the repo, the machine layer is English

**Prose follows the repository's working language. Anything a machine parses is English.**

The boundary is drawn by *what consumes the artifact*, not by who wrote it. A commit body and a
code comment have the same audience, so they land on the same side. A route segment and a database
column have no audience at all, so they land on the other. That is the only cut a reviewer can apply
without a taste debate.

- **Per-stack enumeration, wrong → right pairs**: `references/boundary-map.md`
- **Producing and consuming the PT→EN glossary**: `references/glossary-protocol.md`
- **Existing names: the three migration tiers**: `references/migration.md`
- **The detector**: `references/check-identifier-locale.py`

## The two layers

| Layer | Language | What belongs to it |
|---|---|---|
| **Prose** | the repository's working language | commit subjects and bodies, PR titles and bodies, issue text, ADRs, README and docs, **code comments and docstrings**, user-facing strings and i18n catalogs, error messages shown to end users, the human sentence part of a log line, seeded content and data |
| **Machine** | English, ASCII | variables, constants, parameters, fields; functions, methods, classes, types, interfaces, enums; module, package, **file and directory names**; REST path segments and query params; custom HTTP header names and JSON body field names; DB schemas, tables, columns, indexes, migration slugs; enum values, status tokens and error codes; event, topic, queue and channel names; config keys (env vars, YAML keys, KV paths, CLI flags); structured-log field keys and metric names; test function names |

Two rules that resolve most arguments before they start:

1. **ASCII, always.** Even when a domain noun is kept, it is deaccented. Accents break shell
   quoting, URL encoding, DB collations, case-folding and some CI toolchains.
2. **Portuguese lives in the values, never in the keys.** `{"status": "pending", "label": "Pendente"}`
   is correct on both halves.

## The domain-term exception, and the gate that keeps it small

A term with legal or regulatory meaning and no faithful English translation is **kept**, deaccented,
inside English grammar: `validateCpf()`, `notaFiscalStatus`, `POST /invoices/{id}/nota-fiscal`,
column `nota_fiscal_number` — not `nota_fiscal_numero`.

A CPF is not a "tax id". A Nota Fiscal is a SEFAZ document with statutory semantics. `boleto` names
an instrument no English word denotes. Inventing `taxpayerRegistryNumber` destroys traceability to
the law, to the regulator's schema and to the payment provider's API, and guarantees two developers
invent two different translations. This is DDD's ubiquitous language: the shared vocabulary covers
domain **terms**, and says nothing about plumbing verbs — `criarPedido`, `buscarUsuarios` and
`salvarDados` translate the plumbing, which carries no domain meaning at all.

**The gate is what makes the exception usable.** A kept term is legitimate only when:

- the backlog item's Glossary lists it in the *keep-as-is* column, or
- the code carries an inline waiver naming the reason:

```python
# locale-ok: SEFAZ fiscal document, no faithful English translation
nota_fiscal_number: str
```

An unlisted foreign noun is a defect, not a domain term. Without this gate, "it is a domain term" is
an unlimited escape hatch and the rule means nothing. Requiring a reason also puts every exception
in front of a reviewer.

## A foreign API that speaks another language stops at the adapter

Mirror the wire names **exactly** inside the adapter or transport schema — fidelity to the wire
beats purity, because renaming a wire field is a bug factory — and translate to the English domain
model at exactly one mapping point. The mirrored names live under `adapters/<vendor>/` or
`schemas/external/` and never appear past the mapper. This is Evans' anti-corruption layer.

```python
class InvoiceWire(BaseModel):
    number: str = Field(alias="numeroDocumento")
    issued_at: datetime = Field(alias="dataEmissao")
```

`react-api-client` ships the JavaScript instance of the same boundary: its zod parser transforms the
wire shape into the domain model, and that transform is the anti-corruption layer.

## Never improvise a translation

A name invented on the spot is an unverified claim about the domain. Take it from the codebase, take
it from the item's Glossary, or ask — the general form of this rule, and the research ladder behind
it, is `verify-before-claiming`. Two developers improvising independently produce two names for one
concept, which is worse than either language used consistently.

The decision is cheapest at grooming time, which is why the backlog item carries the glossary and
`execute-backlog` surfaces it in the plan before any file is touched
(`references/glossary-protocol.md`).

## Reviewing a diff

```bash
# added lines only — this is the enforcement mode, and it is what makes the rule adoptable
git diff origin/main... | python3 references/check-identifier-locale.py --diff -

# a specific file, or a whole tree once a repository is already clean
python3 references/check-identifier-locale.py src/orders/service.py
```

Read the output as a prompt, not a verdict: every finding prints `path:line:token` plus the exact
waiver line to add. A finding the author judges correct as written costs one `locale-ok:` comment
with a reason. **The check declares what escapes it in its own docstring** — a curated word list is
not a language model, so a passing run is not proof of compliance, and names outside its reach are
reviewed by hand.

Probed on 2026-08-14 with `Python 3.14.5`; the detector uses only the standard library, so it has no
pinned dependency.

## Existing code

New code is English. Existing names are not renamed for their own sake, and a contract-bearing name
— a route, a persisted column, an event name, a deployed config key — is never renamed in place.
The three tiers and the expand/contract recipe are in `references/migration.md`.

## See also

- `verify-before-claiming` — the general rule that an improvised name is an unverified claim.
- `conventional-commit` — commit subjects follow the repo's language; this skill governs the code
  the commit carries.
- `documentation` — docs prose follows the project's language; identifiers quoted in docs are copied
  from the code.
- `backlog` / `execute-backlog` — where the glossary is produced and consumed.
- `bug-hunter` — a rename that crosses a wire boundary is a compatibility change and needs a test.
- `react-api-client` — the shipped JavaScript instance of the anti-corruption boundary.
