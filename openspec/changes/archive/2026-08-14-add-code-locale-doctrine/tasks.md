## 1. Evidence & Sources (MANDATORY)

<!-- Always the FIRST group: probe before you write. Record the COMMAND and a fragment of its
     RAW OUTPUT, never a conclusion. Doctrine: the verify-before-claiming skill. -->

- [x] E.1 Every local path this change relies on was OPENED and read at HEAD `429d127` on
      2026-08-14, not recalled: `openspec/specs/skills-authoring/spec.md:62-69` (*English as catalog
      locale*, the rule this change scopes) and `:225-256` (*Authoring rules are machine-enforced*,
      which dictates the script + self-test shape) and *Single canonical home per rule* and
      *Checklists are scored against field defects*; `openspec/schemas/skills-rite/templates/tasks.md:20-45`
      (the Q.1-Q.4 group Q.5 joins); `scripts/validate-skills.py:1-116` (the C1-C8 docstring contract
      and the `looks_skillish` tuple); `scripts/validate-rite.sh:30-50`; `.github/workflows/ci.yml:40-95`
      (the exact gate order); `skills/backlog/references/issue-template.md:1-45` and
      `skills/backlog/SKILL.md:1-60`; `skills/execute-backlog/SKILL.md:37-96` (the 8 safety rails and
      the 11 workflow steps); `skills/conventional-commit/SKILL.md:25-40` and `:108-119`;
      `skills/documentation/SKILL.md:157`; `skills/execute-backlog/references/acceptance-tracking.md:15`;
      `generate.sh:1-60`; `README.md:315,335,785-805`;
      `openspec/changes/archive/2026-08-07-add-verify-before-claiming/{proposal,design,tasks}.md` and
      its two spec deltas (the precedent this change's shape follows).
- [x] E.2 Every external tool and version this change asserts was probed on this machine on
      2026-08-14: `python3 --version` -> `Python 3.14.5`; `openspec --version` -> `1.6.0`;
      `gh --version` -> `gh version 2.92.0 (2026-04-28)`; `git --version` -> `git version 2.47.3`;
      `node --version` -> `v26.0.0`. Lua toolchain probed and recorded as it actually is:
      `command -v luac` -> `/home/linuxbrew/.linuxbrew/bin/luac`, while `luac5.4`, `luac5.3` and
      `lua5.4` are ABSENT — so C3's Lua path resolves through `luac` here and the detector must not
      assume a versioned binary name.
      The claims the proposal makes were probed, not recalled:
      `grep -rniE "identifier language|english identifier|nome em ingl|identificador" skills/ | wc -l` -> `0`;
      `grep -rnE '"/[a-z0-9_-]*(usuarios|clientes|pedidos|jogadores|veiculos|corridas|produtos|vendas)' skills/ | wc -l` -> `0`;
      `grep -n "working language" skills/backlog/references/issue-template.md` -> `8:in the repository's working language (default: the language of its README).`;
      `grep -n "Portuguese docs stay Portuguese" skills/documentation/SKILL.md` -> `157:...`;
      `grep -n "repo's working language" skills/execute-backlog/references/acceptance-tracking.md` -> `15:...`;
      `sed -n '105,109p' scripts/validate-skills.py` -> the prefix tuple, confirming `"code-"` is
      absent; `git ls-files shared/` -> `shared/conventions/.gitkeep` and
      `shared/skills/openspec-drivezone/content.md`, with zero inbound references outside
      `CHANGELOG.md:367` and the archive; `ls skills | wc -l` -> `33`;
      `grep -n "all 33" README.md .claude-plugin/marketplace.json` -> `README.md:55`, `README.md:82`,
      `.claude-plugin/marketplace.json:15`.
- [x] E.3 Anything that could NOT be probed is written down rather than stated as fact: the field
      defect itself (Portuguese identifiers and route paths shipped in target repos) is a maintainer
      field report of 2026-08-14 recorded in issue #76, not a measurement taken in this repository —
      `design.md` states plainly that the catalog's own examples are clean and that Q.5 is therefore
      a regression gate on the exemplar rather than remediation. The detector's real-world precision
      is likewise unproven until task V.5 runs it against a target repo; no precision claim is made
      before that number exists.
- [x] E.4 Scope check: this change does only what the proposal asked. Noticed and **not** performed,
      listed as follow-ups: (a) `shared/conventions/` is inert — advertised by `README.md:792` as the
      home for "Code style guides (naming…)" but loaded by nothing (not generated, not installed,
      not in any plugin, not walked by `scripts/validate-skills.py`); it needs its own item to
      either delete it or document it as inert. (b) Wiring the detector into each target repo's CI
      and pre-commit and seeding its `.identifier-locale-allow` — one item per repo. (c) The
      frontmatter keys `metadata.author` and `compatibility` are required by the spec and by Q.1 but
      are not grepped by the CI frontmatter step, so they remain review-only; not widened here.

## 2. Canonical skill

- [x] 2.1 Create `skills/code-locale/SKILL.md` with the contracted frontmatter (`name` == directory,
      folded `description` carrying pt-BR + English triggers and `Do NOT use for` boundaries,
      `metadata.author: solvelab`, `metadata.version: 1.0.0`, `metadata.category: process`,
      `license: MIT`, `compatibility`) and no forbidden meta sections (C8)
- [x] 2.2 Body: the one-sentence rule, then the two-layer boundary table — prose layer first, so the
      doctrine cannot be misread as "everything English"
- [x] 2.3 Body: the ASCII sub-rule; Portuguese in values never keys; the BR domain-term exception
      **with its gate** (Glossary row or inline `locale-ok: <reason>`), grounded in DDD ubiquitous
      language
- [x] 2.4 Body: the anti-corruption-layer rule for foreign Portuguese payloads, citing
      `react-api-client` as the shipped JS instance rather than restating it
- [x] 2.5 Body: a "Reviewing a diff" section giving the exact commands, and a `## See also` group
- [x] 2.6 `references/boundary-map.md` — per-stack enumeration with PT-wrong → EN-right pairs for
      Python/FastAPI, Lua/FiveM, C#, React/TS, SQL, Helm/env
- [x] 2.7 `references/glossary-protocol.md` — how the glossary is produced at grooming (harvest
      first, then decide) and consumed at execution
- [x] 2.8 `references/migration.md` — the three tiers (new code / opportunistic internal rename /
      contract-bearing expand-contract), the no-big-bang rule with the string-referenced-name
      failure mode, and the `.identifier-locale-allow` debt ledger; links to `bug-hunter` and to
      `python-rest-api`'s rollout-gated enforcement instead of restating either

## 3. Prevention at the source

- [x] 3.1 `skills/backlog/references/issue-template.md`: add the `## Glossary (domain term →
      identifier)` section with the mandatory **Origin** column, placed immediately before
      `## Technical requirements`
- [x] 3.2 Same file, line 8: add the prose-only clause and the link to `code-locale`
- [x] 3.3 Same file: one conditional line in the acceptance-criteria guidance for code-producing items
- [x] 3.4 `skills/backlog/SKILL.md`: step 3 harvests the repo's existing identifier vocabulary;
      step 6 fills the Glossary and turns an unresolvable term into a gap question; ground rule 2
      gains "a translation is an invention too"

## 4. Consumption and rite gates

- [x] 4.1 `skills/execute-backlog/SKILL.md`: safety rail 9 (machine layer is English; an unlisted
      term is a stop-and-ask, linking to `code-locale`)
- [x] 4.2 Same file: step 3 treats a missing Glossary on a code-producing item as a soft signal;
      step 4 harvests vocabulary; steps 8/9 give the locale criterion a verdict like any other
- [x] 4.3 `skills/execute-backlog/references/execution-flow.md`: the `**Glossary**` line in the
      approval-gated plan format, and the soft-signal row
- [x] 4.4 Carve-outs, one line each, no existing rule changed: `skills/documentation/SKILL.md:157`,
      `skills/conventional-commit/SKILL.md:30-31`,
      `skills/execute-backlog/references/acceptance-tracking.md:15`
- [x] 4.5 `openspec/schemas/skills-rite/templates/tasks.md`: add Q.5 to the Quality Gates group, with
      its provenance recorded here (maintainer field report 2026-08-14, issue #76)

## 5. Detector and machine enforcement

<!-- Order matters: the script lands first because C9 shells out to it. -->

- [x] 5.1 `skills/code-locale/references/check-identifier-locale.py` — stdlib-only; modes `<paths…>`,
      `--diff -`, `--stdin --lang <lang>`, `--markdown-fences`, `--selftest`
- [x] 5.2 Tier 0 implemented first (strip comments and non-path literals; re-add path-shaped literals
      and DDL fragments; extract identifiers; segment by case convention; whole-segment match;
      4-char floor), then tiers 1-4
- [x] 5.3 `LEXICON ∩ ENGLISH_COLLISIONS == ∅` asserted at import; `-mento`, `-dor`, `-vel` excluded
      and declared as escapes
- [x] 5.4 Two waivers: inline `locale-ok: <reason>` and `.identifier-locale-allow`; every finding
      prints `path:line:token` plus the exact allowlist line to add
- [x] 5.5 The check declares what escapes it, in the check itself (*Partial coverage is declared, not
      implied*): English-colliding words, open vocabulary, the three excluded suffixes, sub-4-char
      abbreviations, other Romance languages, runtime-built identifiers, comments and non-path
      literals, untagged fences, and branch/PR/issue text
- [x] 5.6 False-positive proof 1: `check-identifier-locale.py skills/assettoserver-csp-lua/references/snippets.lua`
      -> `findings: 0` (accented text in Lua comments and inside a UTF-8-escaped literal)
- [x] 5.7 False-positive proof 2: `check-identifier-locale.py --markdown-fences skills/conventional-commit/SKILL.md`
      -> `findings: 0` (the untagged Portuguese commit fence is skipped by design)
- [x] 5.8 True-positive proof: `def buscar_usuario(codigo)` -> 3 findings, exit 1
      (`pt-verb: 'buscar'`, `pt-noun: 'codigo'` x2); `class Customer: cpf, boleto_id` -> exit 0
- [x] 5.9 `scripts/validate-skills.py`: add `C9 identifier locale` to the docstring contract and a
      `check_locale()` called from `main()`, over language-tagged fences only, plus
      `skills/*/references/*.{py,lua,sh}`; finding label exactly `"C9 identifier locale"`;
      `KNOWN LIMIT` docstring inside the function
- [x] 5.10 Same file: add `"code-"` to the `looks_skillish` prefix tuple at `:105-109`, so a mistyped
      `code-locale` cross-link is caught by C2
- [x] 5.11 `scripts/selftest-validate-skills.py`: one MUTATIONS entry for C9, valid Python so C3 stays
      silent, whose dict *value* string asserts that Tier 0 strips literals
- [x] 5.12 `.github/workflows/ci.yml`: a step running the detector's own `--selftest`, beside the two
      existing self-test steps

## 6. Cross-links and the always-on layer

- [x] 6.1 One `## See also` bullet each, naming that skill's machine-layer artifact, in
      `python-rest-api`, `fivem-lua`, `fivem-nui-react`, `react-api-client`, `assettoserver-plugin`,
      `backend-resilience`, `log-event-collector`, `api-resilience-testing`, `documentation`
- [x] 6.2 `claude/global/personal-rules.md`: new *Code Locale* section placed after *Grounding (no
      achismo)*, in the same shape — short bullets plus a link line to the canonical skill
- [x] 6.3 Verify no doctrine was restated inline: every touched sibling carries a link, not a copy

## 7. Removal and catalog plumbing

- [x] 7.1 `git rm shared/skills/openspec-drivezone/content.md` (stale Portuguese duplicate, zero
      inbound references)
- [x] 7.2 `README.md`: new row in the `### Process & git` table; counts `all 33` → `all 34` at `:55`
      and `:82`
- [x] 7.3 `.claude-plugin/marketplace.json:15`: the same count
- [x] 7.4 `generate.sh` `GROUP_DESC[workflow]` and the `ai-skills-workflow` marketplace description
      name the new skill
- [x] 7.5 `./generate.sh` last, and commit its output

## 8. Quality Gates (MANDATORY)

<!-- Adversarial review of the skills touched — not happy-path. Q.5 is introduced by this change and
     is backfilled here: a gate introduced mid-flight does not exempt the work that introduces it. -->

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [x] Q.2 All touched skill content in English (catalog locale)
- [x] Q.3 Description triggers testable: phrases a user would actually say route to `code-locale` and
      do NOT collide with `conventional-commit`, `documentation` or `verify-before-claiming`;
      "Do NOT use for" boundary present
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

## 9. Validation & Closure (MANDATORY)

<!-- Always the last group. "Done" is verifiable, not an opinion. -->

- [x] V.1 `openspec validate add-code-locale-doctrine --strict` green, and `bash scripts/validate-rite.sh` green
- [x] V.2 Catalog discovery intact: `npx skills add solvelab/ai-skills --list` finds every skill,
      count 34, no orphan/renamed leftovers; `ls skills | wc -l` -> `34`
- [x] V.3 README / docs updated where the change alters catalog composition or usage; the full CI
      loop green locally: `python3 scripts/validate-skills.py`,
      `python3 scripts/selftest-validate-skills.py` (prints `CAUGHT C9 identifier locale`),
      `python3 scripts/validate-repo-hygiene.py`, `python3 scripts/validate-repo-hygiene.py --selftest`,
      `python3 scripts/scan-secrets.py`, `./generate.sh && git diff --exit-code`
- [x] V.4 `openspec archive add-code-locale-doctrine --yes` after all groups above are `[x]`
- [x] V.5 Field scoring recorded, and it changed the detector. Run on 2026-08-14 against two real
      local projects: `omnivoice-tts/server_addons` (8 Python files, 1432 lines) and a TypeScript
      VS Code extension (233 files, 970,389 lines).
      **First run: 9 findings, all 9 false positives** —
      `pasta` x2 (`pt-noun`; also the English food noun),
      `sfrancia` x2 (`pt-morphology` `-ancia`; a GitHub handle),
      `Warting` x3 and a 4-glyph token x2 (`non-ascii`; minified vendor bundles).
      Two fixes earned by that measurement, each recorded with the identifier that earned it:
      (a) `pasta` moved from NOUNS to ENGLISH_COLLISIONS, where the import assertion now keeps it out;
      (b) vendored/generated/minified files are skipped (`node_modules`, `.venv`, `dist`, `build`,
      `.vscode-test`, `site-packages`, `*.min.*`, and any file with a >400-char line), because 7 of
      the 9 findings came from third-party bundles that are not the project's machine layer; plus a
      `NOT_PORTUGUESE` set for proper names the morphology tier wrongly matched.
      **Re-run after the fixes: 0 findings, 0 false positives**, 226 vendored files reported as
      skipped and 7 project source files scanned. Both cases are permanent regressions in
      `--selftest`, which now covers 6 firing tiers and 13 silent clean cases
