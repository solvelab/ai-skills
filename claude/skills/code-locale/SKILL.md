---
name: code-locale
description: >-
  Decides which natural language each artifact is written in: prose follows the repository's
  working language, anything a machine parses is English. Use when naming a variable, function,
  class, file, route, query param, DB table or column, enum value, event, config key or log field;
  when reviewing a diff that introduces names; when a backlog item in another language becomes
  code; when a domain term like CPF, CNPJ, boleto, PIX or nota fiscal may keep its name; when an
  external API's payload is in another language; or when the user says "código em português",
  "nome de variável em inglês", "rota em português", "traduz esse nome", "identificador em
  inglês", "should this be in English", "our code is half Portuguese", "naming convention",
  "ubiquitous language", "anti-corruption layer". Do NOT use for commit subjects or PR bodies
  (that is conventional-commit), for docs prose (that is documentation), for case style or test
  naming (each stack's skill), or for i18n and user-facing translation.
metadata:
  author: solvelab
  version: 1.4.1
  category: process
license: MIT
compatibility: >-
  The doctrine is language- and stack-agnostic and needs no runtime. The shipped detector
  `references/check-identifier-locale.py` needs Python 3.9+ and no third-party package (its word
  list is read with the standard library's gzip module); it tokenizes Python, Lua, JavaScript,
  TypeScript, C#, SQL, YAML, JSON and Bash and reports any other file type as skipped. The
  optional hook `locale-rite.py` (linked from the body) was built against Claude Code 2.1.246 and
  exits silently anywhere else.
---

Read and follow all instructions in ~/ai-skills/skills/code-locale/SKILL.md

Reference files are in ~/ai-skills/skills/code-locale/references/ — read them when the skill instructions point to them.
