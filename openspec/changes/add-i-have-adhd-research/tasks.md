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

## 2. Vendor e proveniência

- [x] 2.1 `research/i-have-adhd/vendor/i-have-adhd/` com `scripts/run_evals.py`, `scripts/judge.py`,
      `evals/cases.jsonl`, `evals/rubric.md`, os testes que passam aqui, `.claude-plugin/plugin.json`,
      `hooks/`, `skills/i-have-adhd/SKILL.md`, `LICENSE`, sem modificação; `PIN` com commit, data e
      sha256 por arquivo
- [x] 2.2 `research/i-have-adhd/vendor/caveman/` com `skills/caveman/SKILL.md`, `LICENSE` (parte MIT)
      e `PIN` com versão, commit instalado e sha256 do que o hook carrega
- [x] 2.3 `research/i-have-adhd/PIN` com o blob de `research/lean-code/run.py` lido e a lista de
      símbolos importados

## 3. Protocolo congelado

- [x] 3.1 `research/i-have-adhd/protocol.md` com o cabeçalho de congelamento: sha base, data, e a
      frase de que os vereditos foram escritos antes de qualquer célula paga
- [x] 3.2 Seções `## Conditions` e `## Injection modes`: o que cada célula vê em cada modo, o
      comando literal do runner, e como o hook entra
- [x] 3.3 Seção `## Metrics per response`: as cinco do juiz, `blocker`, `output_tokens`,
      `forbidden_phrase_hits` com a lista literal de frases
- [x] 3.4 Seção `## Verdict (written before the number)`: ADOPT / NO-CLAIM / REJECT com limiares
      numéricos e a regra do `partial-success`
- [x] 3.5 Seção do que a medição **não** cobre: chat sem ferramentas, juiz da mesma família, três
      trials, caveman medido pelo que o hook injeta

## 4. Harness

- [x] 4.1 `research/i-have-adhd/run.py` carrega `run_evals` e `judge` do vendor e a camada de
      processo e sonda de `research/lean-code/run.py` por `importlib`; nada copiado
- [x] 4.2 `--prepare-conditions`: um `CLAUDE_CONFIG_DIR` de rascunho por condição fora do
      repositório, o flag `.i-have-adhd-always` no candidato, `conditions.json` com os caminhos e
      hashes; recusa uma raiz dentro do repositório
- [x] 4.3 `--probe`: uma chamada por condição e modo com `stream-json --include-hook-events`;
      passa só com hook 3/3 nas condições tratadas e 0/3 no baseline (modo `plugin`) e 0/3 em
      todas (modo `prompt`); grava `probe.json`
- [x] 4.4 `--matrix`: laço próprio de células (D2), resumível pela chave do upstream, comando de
      cada célula gravado antes de rodar, teto `--budget-usd`; recusa sem `--selftest` verde na
      mesma invocação e sem sonda passada para o modo pedido
- [x] 4.5 `--judge`: chama o `judge.py` do upstream com o runner do juiz e as três condições, um
      arquivo por modo
- [x] 4.6 `--report --export`: tabelas por dimensão e por caso, blockers, `output_tokens`,
      `forbidden_phrase_hits`, gasto; recusa agregar stamps com `claude --version`, modelo ou sha
      da rubrica diferentes; export sem `session_id`, texto de resposta ou caminho de HOME
- [x] 4.7 `--selftest` (offline): hashes do vendor contra os `PIN`, testes do upstream, contrato
      dos símbolos importados, contador de frases com defeito injetado, tabela de veredito sobre
      notas sintéticas, stripper de export, preflight das condições

## 5. Medição

- [x] 5.1 Piloto Haiku n=1 em dois casos, ambos os modos (nunca reportado)

      Stamps `20260909-222611-prompt` e `20260909-222653-plugin`: 6 células cada, 0 falhas,
      $0.1204 + $0.1049; juiz Haiku $0.0606 + $0.0523, 4/4 grupos julgados; `--report --export`
      produziu as tabelas e o export sem `session_id` nem texto de resposta. Números não
      reportados, por protocolo.
- [x] 5.2 Sonda nos dois modos; a lacuna do `--plugin-dir` em `-p` fechada com o que o stream mostrou

      Sonda `20260909-222459` (Haiku, $0.2707): modo `prompt` hook events 0/0/0 nas três
      condições; modo `plugin` `SessionStart` 3/3 em `candidate` (`hook_response` com
      `ADHD MODE ACTIVE (always-on)…`) e 3/3 em `comparator` (`CAVEMAN MODE ACTIVE — level: full…`
      mais o `UserPromptSubmit` do tracker), 0/3 em `baseline`; `.caveman-active` só no
      comparador. `results/20260909-222459-probe.json`.
- [ ] 5.3 Matriz no modelo diário, 14 casos × 3 condições × 3 trials, modos `prompt` e `plugin`,
      dentro do `--budget-usd`
- [ ] 5.4 Juiz cego nos dois arquivos de respostas
- [ ] 5.5 `results.md` com as tabelas, o veredito citado verbatim do protocolo e conferido condição
      por condição, a seção de gasto e a do que não cobre; `README.md` com a linha de status

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
