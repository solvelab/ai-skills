## Why

The catalog rules the language of skill **documentation** and says nothing about the language of the
**code the skills teach and produce**. `openspec/specs/skills-authoring` → *English as catalog
locale* binds prose ("All skill content SHALL be written in English"), enforced as the review-only
checkbox Q.2 at `openspec/schemas/skills-rite/templates/tasks.md:31`. Nothing binds an identifier.

Measured on this catalog at HEAD `429d127` over 33 skills:

```
$ grep -rniE "identifier language|english identifier|nome em ingl|identificador" skills/ | wc -l
0
```

Three instructions actively pull the other way, and none of them carves out that language matching
governs prose only:

```
$ grep -n "working language" skills/backlog/references/issue-template.md
8:in the repository's working language (default: the language of its README).
$ grep -n "Portuguese docs stay Portuguese" skills/documentation/SKILL.md
157:7. **Match the project's existing language and voice.** Portuguese docs stay Portuguese.
$ grep -n "repo's working language" skills/execute-backlog/references/acceptance-tracking.md
15:Headings may be in the repo's working language (`Critérios de aceite`, `Testes & Bug-Hunter`) —
```

`skills/conventional-commit/SKILL.md:30-31` then names Portuguese as the solvelab default, and its
only worked example block (`:108-119`, an untagged fence) is entirely Portuguese. An agent reading
this catalog concludes "this project is Portuguese" and carries that conclusion into identifiers,
which no rule forbids.

The leak path is mechanical: the backlog item is written in the repo's working language — correct,
humans read it — `execute-backlog` reads the item and mirrors its Portuguese domain nouns straight
into code. **The translation decision is never taken at any point on the path.** The reported field
defect is Portuguese variable names, function names and REST route segments shipped in target repos
(maintainer field report, 2026-08-14, issue #76).

This is a missing rule rather than a bad exemplar. The catalog's own examples are already clean:

```
$ grep -rnE '"/[a-z0-9_-]*(usuarios|clientes|pedidos|jogadores|veiculos|corridas|produtos|vendas)' skills/ | wc -l
0
```

## What Changes

- Add `skills/code-locale/`, the canonical home for the **prose layer / machine layer** boundary:
  prose (commits, PRs, issues, docs, code comments, user-facing strings) follows the repository's
  working language; anything a machine parses (identifiers, file and module names, REST path
  segments and query params, DB tables/columns/indexes, enum values, event and topic names, config
  keys, log field keys, test names) is English and ASCII.
- The doctrine defines Portuguese as belonging to **values, never keys**, and keeps Brazilian
  domain terms with legal or regulatory meaning (`cpf`, `cnpj`, `boleto`, `pix`, `nota_fiscal`)
  inside English grammar — legitimate only when the backlog item's Glossary lists them or the code
  carries an inline `locale-ok: <reason>`. Without that gate, "it is a domain term" is an unlimited
  escape hatch.
- Prevent the defect at its source: `skills/backlog/references/issue-template.md` gains a
  `## Glossary (domain term → identifier)` section with a mandatory **Origin** column (harvested
  from the codebase, or decided in the item), and line 8 gains a prose-only clause.
  `skills/execute-backlog` consumes that glossary and surfaces it in the approval-gated plan, so the
  translation decision is reviewed before any file is touched.
- Ship four reference files, one of them executable: `references/boundary-map.md` (per-stack
  enumeration), `references/glossary-protocol.md`, `references/migration.md` (new-code-only policy,
  expand/contract for contract-bearing names), and `references/check-identifier-locale.py` — a
  stdlib-only detector that target repos copy into their own CI and pre-commit.
- Wire the detector into this catalog's CI as `scripts/validate-skills.py` check
  `C9 identifier locale`, shelling out to the shipped script so the catalog proves the script
  actually runs; add its `scripts/selftest-validate-skills.py` MUTATIONS entry and a CI step for the
  detector's own `--selftest`.
- Add Quality Gate Q.5 to `openspec/schemas/skills-rite/templates/tasks.md`.
- Add one-line carve-outs to the three prose-language instructions above and one `## See also` link
  to nine code-producing skills. No doctrine is restated inline.
- Add a *Code Locale* section to `claude/global/personal-rules.md`, the only surface that acts with
  no trigger.
- Remove `shared/skills/openspec-drivezone/content.md`, a stale Portuguese duplicate of a skill that
  was translated to English in `2026-07-01-refactor-skills-quality-review` and merged per
  `CHANGELOG.md:367`. It has zero inbound references and is greppable Portuguese content — the very
  contamination vector this change addresses.
- Fix a real gap in the same file the change already edits: the `looks_skillish` prefix tuple at
  `scripts/validate-skills.py:105-109` does not contain `"code-"`, so a mistyped `code-locale`
  cross-link would escape check C2 and every cross-link added here would be unvalidated.
- **BREAKING for catalog consumers**: the catalog grows from 33 to 34 skills, which changes what
  `npx skills add solvelab/ai-skills --list` returns and adds a skill to the `ai-skills-workflow`
  plugin bundle.

## Capabilities

### New Capabilities

_None._ The behaviour belongs to the two existing capabilities below.

### Modified Capabilities

- `skills-authoring`: the canonical map gains an owner for the identifier/prose language boundary,
  and *English as catalog locale* declares its scope explicitly (this catalog's documentation prose)
  and names the sibling rule that governs the language of code — closing in the spec the ambiguity
  that produced the field defect, not only in a skill.
- `skills-catalog`: the catalog gains a skill whose subject is which natural language each artifact
  of a change is written in, and a rule that a shipped detector must declare what escapes it.

## Impact

- `skills/code-locale/` — new: `SKILL.md` plus `references/boundary-map.md`,
  `references/glossary-protocol.md`, `references/migration.md`,
  `references/check-identifier-locale.py`.
- `skills/backlog/SKILL.md`, `skills/backlog/references/issue-template.md` — the Glossary section
  and the vocabulary-harvest step; the prose-only clause on line 8.
- `skills/execute-backlog/SKILL.md` (safety rail 9, steps 3/4/5/8/9),
  `skills/execute-backlog/references/execution-flow.md` (the plan-format Glossary line),
  `skills/execute-backlog/references/acceptance-tracking.md:15` (carve-out).
- `skills/documentation/SKILL.md:157` and `skills/conventional-commit/SKILL.md:30-31` — one carve-out
  line each; neither existing rule is changed.
- `skills/python-rest-api`, `skills/fivem-lua`, `skills/fivem-nui-react`, `skills/react-api-client`,
  `skills/assettoserver-plugin`, `skills/backend-resilience`, `skills/log-event-collector`,
  `skills/api-resilience-testing`, `skills/documentation` — one `## See also` link each, no doctrine
  removed.
- `scripts/validate-skills.py` (C9 + the `"code-"` prefix fix),
  `scripts/selftest-validate-skills.py` (one MUTATIONS entry),
  `.github/workflows/ci.yml` (the detector's `--selftest` step).
- `openspec/schemas/skills-rite/templates/tasks.md` — Q.5.
- `claude/global/personal-rules.md` — the always-on layer. Not generated; edited directly.
- `README.md` — a new row in the Process & git table and the count `all 33` → `all 34` at `:55` and
  `:82`; `.claude-plugin/marketplace.json:15` — the same count; `generate.sh`
  (`GROUP_DESC[workflow]`) — the bundle description names the new skill.
- `shared/skills/openspec-drivezone/content.md` — removed.
- Generated trees `claude/ codex/ cursor/ copilot/ plugins/` — rewritten by `./generate.sh`.
- Consumers of the `ai-skills-workflow` plugin receive one additional skill; nothing is removed or
  renamed, so no existing cross-reference breaks.
- Target repositories are **not** wired to the detector by this change. Adoption is one follow-up
  backlog item per repo.
