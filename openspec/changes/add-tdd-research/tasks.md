# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `0959ccc` (master, base de `backlog/182-tdd-research`) em 2026-09-06:

      - `research/lean-code/run.py` — nível de módulo (linhas 155-258), `load_module` (:266),
        `Task` (:321), `load_tasks` (:356), `seed_repo` (:403), `is_test_path` (:469),
        `git_diff_stats` (:489), `read_settings` (:775), `arm_settings` (:779), `snippet_block` (:796),
        `prepare_arm_settings_sources` (:802), `prepare_arm` (:840), `settings_sources_preflight` (:874),
        `arm_preflight` (:941), `materialize_skills_tree` (:987), `cell_env` (:1101),
        `cell_command` (:1114-1128), `run_process` (:1143), `score_cell` (:1163), `run_cell` (:1180),
        `load_arms_json` (:1195), `probe_gate` (:1202), `cmd_matrix` (:1232), `aggregate` (:1330),
        `print_table` (:1359), `strip_export` (:1399), `cmd_report` (:1475), `cmd_selftest` (:2652),
        `main` (:2681) e o guard `if __name__ == "__main__"` (:2747).
      - `research/lean-code/protocol.md` — cabeçalho de congelamento (linhas 3-19), `## Arms` (:32),
        `## Cell` (:155), `## Metrics per cell` (:179), `## Tasks (9)` (:221), `## Sequence` (:254),
        `## Verdict (written before the number)` (:276).
      - `research/lean-code/README.md` (tabela "Read in this order", :13-25), `results.md`
        (cabeçalhos e tabela principal, :67-127, veredito :176-260), `results/README.md`,
        `scorer-venv.txt`, `arms-block.md`.
      - `research/lean-code/tasks/fastapi-create-item/` — `task.py` inteiro (contrato `ID`, `SOURCE`,
        `ROOM`, `BOUNDARY`, `AXIS`, `ENTRY`, `SEED_DIR`, `GOOD_DIR`, `BAD_DIR`, `PROMPT`, `VARIANTS`,
        `score()`), `scorer_probe.py`, e a árvore `seed/`, `good/`, `bad/`.
      - `openspec/schemas/skills-rite/templates/{tasks,proposal,design,spec}.md` e
        `openspec/schemas/skills-rite/schema.yaml`.
      - `openspec/specs/skills-catalog/spec.md:1196-1268` — o requisito *A published cost claim
        carries re-runnable backing* inteiro, copiado por completo no delta antes da extensão.
      - `openspec/specs/skills-authoring/spec.md:11-21` — o mapa de canonical home.
      - `openspec/changes/archive/2026-09-06-add-lean-code-research/` — `.openspec.yaml`,
        `proposal.md`, `design.md` (seção Canonical Home, :88-100), `tasks.md` (grupos :3, :97, :130,
        :206, :257, :294, :427, :485), `specs/skills-catalog/spec.md`.
      - `skills/execute-backlog/SKILL.md:116-126`, `skills/bug-hunter/SKILL.md:4` e `:27-28`,
        `skills/lean-code/SKILL.md:123-131` e `:158-161`.
      - `generate.sh:39-68`, `:224-234`, `:241-268`; `.github/workflows/ci.yml:25-234`;
        `scripts/` (lista completa e docstrings de `validate-skills.py`, `validate-rite.sh`,
        `validate-rite-evidence.py`, `validate-spec-rite.py`, `validate-skill-version.py`,
        `validate-repo-hygiene.py`, `scan-secrets.py`).
      - `.github/backlog.yml`, `openspec/config.yaml`.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      `claude --version` -> `2.1.263 (Claude Code)`

      `claude --help | grep -A4 -- "--output-format <format>"` ->
      `Output format (only works with --print): "text" (default), "json" (single result), or`
      `"stream-json" (realtime streaming) (choices: "text", "json", "stream-json")`

      `claude --help | grep -A3 -- "--permission-mode <mode>"` ->
      `(choices: "acceptEdits", "auto", "bypassPermissions", "manual", "dontAsk", "plan")`

      `openspec --version` -> `1.6.0`

      `openspec new change add-tdd-research --schema skills-rite` ->
      `Created change 'add-tdd-research' at openspec/changes/add-tdd-research/` / `Schema: skills-rite`

      `openspec status --change add-tdd-research` -> `Progress: 0/4 artifacts complete`

      `python3 --version` -> `Python 3.14.5`

      `python3 -c "import pytest, sys; print(pytest.__version__)"` ->
      `Traceback (most recent call last): File "<string>", line 1, in <module>` (pytest ausente no
      python do sistema; por isso a suíte oculta exige venv fixado)

      `node --version` -> `v26.0.0`

      `grep -rniE "\btdd\b|test-driven|red[- ]green|test first|failing test" skills/ claude/ plugins/ openspec/`
      -> um único match, `skills/claude-statusline/SKILL.md:79`, `Each bar is colored green <50,`
      `yellow 50-79, red >=80` — limiar de cor, não metodologia

      `grep -m1 '^schema:' openspec/config.yaml` -> `schema: skills-rite`

      `gh issue list -R solvelab/ai-skills --state open` -> `[]` antes da criação de #182/#183

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Três lacunas, nenhuma preenchida com substituto plausível:

      (a) ~~**Se `--output-format stream-json` em `2.1.263` emite eventos `tool_use` com o caminho
      do arquivo.**~~ **FECHADA em 2026-09-06 pelo piloto.** Emite: o piloto (2 células, Haiku,
      `$0.0903`) marcou `order_source=transcript` nas duas, e a matriz completa em `transcript`
      36/36 — zero células no fallback de mtime.

      (b) ~~**Se `research/lean-code/run.py` importa sem efeito colateral quando carregado de outro
      diretório.**~~ **FECHADA em 2026-09-06, com correção.** A leitura estática dizia que sim; a
      execução disse que não, na primeira tentativa:
      `AttributeError: 'NoneType' object has no attribute '__dict__'` em
      `dataclasses.py:814`, porque `@dataclass` (`research/lean-code/run.py:320`) resolve
      `cls.__module__` por `sys.modules` e o módulo não estava registrado lá durante o
      `exec_module`. Registrar antes de executar resolve; está no `lean()` de `research/tdd/run.py`
      com o motivo inline e no `PIN`. É exatamente o tipo de fato que leitura não entrega.

      (c) ~~**Se as seis tarefas separam os arms com n=3.**~~ **FECHADA em 2026-09-06, com
      resposta dividida.** Separam totalmente em `order`, `red` e escrita de teste (0/18 contra
      18/18, sem sobreposição) e **não podem separar** em `green`: o baseline acertou 18/18, então
      não há folga para o tratamento melhorar. É o teto que leva o veredito a NO-CLAIM, está escrito
      em `research/tdd/results.md` na seção *Why `green` could not move* e vira follow-up (E.4).

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Follow-ups anotados e **não** feitos:

      - Liberar Bash na célula com sandbox de verdade, para medir o laço de feedback e não só a
        ordem de escrita (só se o veredito sair INCONCLUSIVE por essa razão — D3 do `design.md`).
      - Extrair uma camada de harness compartilhada entre `research/lean-code` e `research/tdd`
        (recusado aqui em D4: mexeria num experimento arquivado e reprodutível).
      - Step de CI para `research/tdd/run.py --selftest` (exigiria o venv fixado no runner; o
        `research/lean-code` tem o mesmo follow-up em aberto).
      - Tracks de TDD para outros stacks além de pytest — decisão de #183, que nasce com um track só.
      - Um arm `skill` medindo a skill publicada — é #183 por definição.
      - Um conjunto de tarefas com folga em `green` (o baseline precisa errar a uma taxa
        mensurável), escolhido a partir de um run só-baseline para não selecionar contra o
        tratamento. Levantado pelo resultado desta medição, não executado aqui.
      - Reexpressar a guarda de `test_added_lines` como teto absoluto em vez de razão contra o
        baseline (Amendment 1 do `protocol.md`); é nova versão de protocolo, não um edit desta.

      Nada em `skills/`, `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`, `generate.sh`,
      `README.md` da raiz ou `.github/workflows/` foi tocado.

## 2. Protocolo congelado

- [x] 2.1 `research/tdd/protocol.md` com o cabeçalho de congelamento: sha base, data, e a frase de
      que os vereditos foram escritos antes de qualquer célula paga
- [x] 2.2 Seção `## Arms`: `baseline` e `doctrine`, com o que cada sessão vê, e a nota de que o arm
      `skill` é de #183
- [x] 2.3 Seção `## Cell`: o comando literal, incluindo `--output-format stream-json`,
      `--disallowedTools Bash` e o texto integral de `NO_RUN_TDD`
- [x] 2.4 Seção `## Metrics per cell`: `order`, `red`, `green`, `test_added_lines`, cada um com
      como é medido e o que o desqualifica
- [x] 2.5 Seção `## Verdict (written before the number)`: SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE
      com limiares numéricos
- [x] 2.6 Seção do que a medição **não** cobre, com o KNOWN LIMIT do Bash bloqueado escrito por
      extenso
- [x] 2.7 `research/tdd/arms-block.md` com o bloco de doutrina que define o arm `doctrine`

## 3. Harness

- [x] 3.1 `research/tdd/run.py` importa a camada genérica de `research/lean-code/run.py` via
      `load_module`; `research/tdd/PIN` grava o sha lido e a lista de símbolos
- [x] 3.2 Parser de `stream-json` produzindo `order`, com fallback de mtime marcado como fallback
- [x] 3.3 Detectores `red` e `green` executando fora da célula, no venv de `scorer-venv.txt`
- [x] 3.4 `--selftest` com um defeito injetado por instrumento, mais o teste de contrato dos
      símbolos importados
- [x] 3.5 `--matrix` recusa rodar sem `--selftest` verde na mesma invocação e sem sonda passada
- [x] 3.6 `--report` recusa agregar stamps de versões ou modelos diferentes; `--export` remove
      `session_id`, texto de resposta, uuids e caminhos absolutos de HOME

## 4. Tarefas e suítes ocultas

- [x] 4.1 Seis tarefas em `research/tdd/tasks/`, cada uma com semente commitada, prompt, referência
      boa, referência ruim e suíte oculta
- [x] 4.2 `research/tdd/scorer-venv.txt` com as versões efetivamente instaladas
- [x] 4.3 O `--selftest` prova cada scorer contra a referência boa e a ruim antes de qualquer
      célula paga

      O instrumento pegou um defeito na referência **boa** do `slug-truncate` antes de qualquer
      célula: `slugify("antidisestablishmentarianism", 5)` devolvia `"antid"` onde o enunciado
      exige `""`. Corrigido; `scorers 18/18` depois disso.

## 5. Medição

- [x] 5.1 `--prepare-arms` e `--probe-isolation` (pago, mínimo, em Haiku)
- [x] 5.2 Piloto n=1 antes da matriz, e a lacuna (a) de E.3 fechada com o que o transcrito mostrou
- [x] 5.3 Matriz nos dois arms no modelo diário, n>=3, dentro do `--budget-usd`
- [x] 5.4 `results.md` com a tabela por tarefa e arm, o veredito citado verbatim do protocolo e
      conferido condição por condição, a seção de gasto e a do que não cobre

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      O artefato executável é `research/tdd/run.py`, e o caminho real é a matriz paga.

      `python3 research/tdd/run.py --selftest --matrix --arms baseline,block --tasks all --runs 3
      --model "opus[1m]" --arms-root <scratch>/tdd-arms --runs-root <scratch>/tdd-runs
      --budget-usd 20 --scorer-venv <scratch>/tdd-venv`

      `research/tdd/run.py --selftest --matrix ... --model "opus[1m]" --runs 3` -> `selftest 70/70`
      -> `matrix 20260906-150952: 6 tasks x 2 arms x 3 runs = 36 cells, budget $20.0`
      -> `parse-duration  baseline  run 0  order=False (transcript)  red=False  green=True  testLOC=0  $0.1930`
      -> `parse-duration  block     run 0  order=True (transcript)  red=True  green=True  testLOC=39  $0.2187`
      -> `spent $6.7351`

      `research/tdd/run.py --probe-isolation --model claude-haiku-4-5-20251001`
      -> `probe PASSED isolation=settings-sources cost=$0.127`

      `research/tdd/run.py --report <stamp> --export research/tdd/results/20260906-150952-export.json`
      -> `wrote research/tdd/results/20260906-150952-export.json`
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      **Tinham de disparar e dispararam**: instrumentos offline com defeito injetado 70/70; leitura
      de ordem pelo transcrito 36/36 (nenhum fallback de mtime); `red` verdadeiro nas 18 células do
      arm `block` onde `order` é verdadeiro; `green` medido pela suíte oculta em 36/36; sonda de
      isolamento 2/2 arms PASS.

      **Tinham de ficar em silêncio e ficaram**: arm `skill` não foi preparado (0 arms, porque
      `skills/tdd/SKILL.md` não existe); `skill_visible` `0/1` nos dois arms; eventos de hook do
      mantenedor 0 em 8 chamadas de sonda; nenhuma célula parada por orçamento (0/36); nenhum
      arquivo criado em `skills/` (0).

      **Escapes conhecidos que ficaram em silêncio**: o piloto em Haiku e a matriz em `opus[1m]`
      não foram agregados juntos — `--report` recusaria por modelo diferente, e não foram
      submetidos a ele; as duas condições `test_added_lines` do veredito não dispararam porque a
      razão contra um baseline de zero é indefinida (Amendment 1 do `protocol.md`).
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      Três coisas se comportaram diferente do esperado, todas registradas:

      1. **O veredito não foi SHIP.** O baseline acertou `green` 18/18, então não havia folga para
         medir ganho de correção. NO-CLAIM pela letra. A consequência para #183 é dura e está
         escrita: a skill pode existir pela disciplina, sem número nenhum.
      2. **Duas condições do veredito eram indefinidas.** `test_added_lines` como razão contra um
         baseline que escreveu zero linhas de teste divide por zero. Não foram editadas — mexer no
         limiar depois do número seria nova versão de protocolo. Amendment 1.
      3. **O baseline não escreveu um único teste em 18/18 células**, sob o `CLAUDE.md` real do
         mantenedor, que carrega o piso de uma checagem do `lean-code`. Observação pós-hoc em
         `results.md`, não uma conclusão desta medição.

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em toda SKILL.md tocada — **nenhuma skill é tocada por esta change**

      `git diff --name-only origin/master...HEAD -- skills/ claude/ plugins/` -> (vazio)
- [x] Q.2 Conteúdo de skill em inglês — nenhuma skill tocada

      `python3 scripts/validate-skills.py` -> `skills checked: 36   findings: 0`
- [x] Q.3 Triggers de description testáveis — nenhuma skill tocada

      Nenhuma `description` de skill mudou; a redação da skill `tdd` e seus triggers são #183.
- [x] Q.4 Sem doutrina duplicada: a tabela Canonical Home do `design.md` declara onde cada regra
      mora, e este item não redige a doutrina TDD

      `grep -c "^| " openspec/changes/add-tdd-research/design.md` -> 9 linhas de tabela canônica.
      O `arms-block.md` é o tratamento medido, não a skill; a linha da tabela diz isso por extenso.
- [x] Q.5 Identificadores em inglês em todo código novo (`research/tdd/run.py`, tarefas, scorers),
      com a prosa em português como no resto do repositório

      Todo identificador novo é inglês (`order`, `red`, `green`, `hidden_suite`, `test_added_lines`,
      `arm`, `cell`); nenhum `# locale-ok` foi necessário. `python3 scripts/validate-skills.py`
      -> `findings: 0` (a checagem C9 de identificadores roda sobre o catálogo).

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-tdd-research --strict` green

      `openspec validate add-tdd-research --strict` -> `Change 'add-tdd-research' is valid`
      `bash scripts/validate-rite.sh` -> `Totals: 3 passed, 0 failed (3 items)`, `rite gate OK`
- [x] V.2 Catalog discovery intact: contagem de skills inalterada, nenhum órfão

      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`
      `python3 scripts/validate-skill-version.py` -> `0 skill(s) changed, 0 with content changes`
      `python3 scripts/scan-secrets.py` -> `no credentials found`
- [x] V.3 `research/tdd/README.md` com a ordem de leitura e a linha de status

      `grep -n "## Read in this order\|## Status" research/tdd/README.md` -> ambas presentes; a
      linha de status diz **Measured on 2026-09-06. Verdict: NO-CLAIM.** e nomeia modelo
      `opus[1m]`, CLI `2.1.263`, 36 células, `$6.7351`.
- [ ] V.4 `openspec archive add-tdd-research --yes` after all groups above are `[x]`
