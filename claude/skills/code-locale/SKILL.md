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
  version: 1.1.0
  category: process
license: MIT
compatibility: >-
  The doctrine is language- and stack-agnostic and needs no runtime. The shipped detector
  `references/check-identifier-locale.py` needs Python 3.9+ and no third-party package; it
  tokenizes Python, Lua, JavaScript, TypeScript, C#, SQL, YAML, JSON and Bash, measures the path of
  every file it is given, and reports the contents of any other file type as skipped rather than
  passing. The optional write-time hook `claude/global/hooks/locale-rite.py` needs a harness that
  emits a post-write tool event; it was built against Claude Code 2.1.246 and exits silently
  anywhere else.
---

Read and follow all instructions in ~/ai-skills/skills/code-locale/SKILL.md

Reference files are in ~/ai-skills/skills/code-locale/references/ — read them when the skill instructions point to them.
