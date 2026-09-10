# Tasks

## 1. Evidence & Sources (MANDATORY)

- [ ] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at
- [ ] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded
- [ ] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute
- [ ] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

## 2. A skill

- [ ] 2.1 `skills/terse-response/SKILL.md`: frontmatter uniforme (`process`, `1.0.0`, MIT,
      compatibility, `Verified against` sem dependência de versão), doutrina de um nível só, o que
      nunca cai, frase de saída, auto-clareza, fronteiras; prosa em inglês; sem seção *Usage*
- [ ] 2.2 `skills/terse-response/references/upstream.md`: PIN (commit, sha256, licença), o que
      entrou, o que ficou de fora e por quê, e o checklist de remoção do plugin

## 3. Casa canônica e always-on

- [ ] 3.1 Bloco `## Terse Response` em `claude/global/personal-rules.md`, com link para a skill
- [ ] 3.2 Mapa canônico de `openspec/specs/skills-authoring` ganha a entrada (delta MODIFIED)

## 4. Catálogo

- [ ] 4.1 `generate.sh` sem diff pendente; `plugins/workflow` embarca a skill; descrição do plugin
      regenerada
- [ ] 4.2 `README.md`: tabela de plugins, tabela de skills, contagem

## 5. Medição (gate de não-regressão, pré-declarado)

- [ ] 5.1 `research/i-have-adhd/run.py` ganha `--candidate-skill <path>` (o candidato deixa de ser
      fixo no vendor); selftest cobre o flag
- [ ] 5.2 Matriz Haiku, modo `prompt`, 14 casos × 3 condições × n=1, teto $3, sem juiz; razão
      pareada de caracteres candidate/comparator registrada em `research/i-have-adhd/results.md`
      (seção datada) e o veredito lido pelo limiar de D4

## 6. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 7. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [ ] Q.2 All touched skill content in English (catalog locale)
- [ ] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [ ] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [ ] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown

## 8. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate <id> --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive <id> --yes` after all groups above are `[x]`
