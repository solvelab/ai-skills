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

      (a) **Se `--output-format stream-json` em `2.1.263` emite eventos `tool_use` com o caminho do
      arquivo em `Write`/`Edit`, e em que forma.** O `--help` confirma que o valor existe; a forma
      dos eventos só aparece rodando uma sessão. Não foi probado — exige uma chamada paga. O desenho
      já prevê o fallback (D2 do `design.md`) e a marca de fallback no registro, em vez de assumir a
      forma. Fecha na tarefa 3.2 e no piloto.

      (b) **Se `research/lean-code/run.py` importa sem efeito colateral quando carregado de outro
      diretório.** A leitura estática de todas as linhas em coluna zero não achou statement fora de
      docstring/import/def/class/constante, e `main()` está guardado em `:2747` — mas isso é leitura,
      não execução. Fecha na tarefa 3.1, que importa o módulo de fato e roda o teste de contrato.

      (c) **Se as seis tarefas separam os arms com n=3.** Não é probável nem improvável antes de
      rodar; é o que a matriz responde. O protocolo escreve o critério de dispersão e as repetições
      adicionais antes de qualquer célula paga.

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

      Nada em `skills/`, `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`, `generate.sh`,
      `README.md` da raiz ou `.github/workflows/` foi tocado.

## 2. Protocolo congelado

- [ ] 2.1 `research/tdd/protocol.md` com o cabeçalho de congelamento: sha base, data, e a frase de
      que os vereditos foram escritos antes de qualquer célula paga
- [ ] 2.2 Seção `## Arms`: `baseline` e `doctrine`, com o que cada sessão vê, e a nota de que o arm
      `skill` é de #183
- [ ] 2.3 Seção `## Cell`: o comando literal, incluindo `--output-format stream-json`,
      `--disallowedTools Bash` e o texto integral de `NO_RUN_TDD`
- [ ] 2.4 Seção `## Metrics per cell`: `order`, `red`, `green`, `test_added_lines`, cada um com
      como é medido e o que o desqualifica
- [ ] 2.5 Seção `## Verdict (written before the number)`: SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE
      com limiares numéricos
- [ ] 2.6 Seção do que a medição **não** cobre, com o KNOWN LIMIT do Bash bloqueado escrito por
      extenso
- [ ] 2.7 `research/tdd/arms-block.md` com o bloco de doutrina que define o arm `doctrine`

## 3. Harness

- [ ] 3.1 `research/tdd/run.py` importa a camada genérica de `research/lean-code/run.py` via
      `load_module`; `research/tdd/PIN` grava o sha lido e a lista de símbolos
- [ ] 3.2 Parser de `stream-json` produzindo `order`, com fallback de mtime marcado como fallback
- [ ] 3.3 Detectores `red` e `green` executando fora da célula, no venv de `scorer-venv.txt`
- [ ] 3.4 `--selftest` com um defeito injetado por instrumento, mais o teste de contrato dos
      símbolos importados
- [ ] 3.5 `--matrix` recusa rodar sem `--selftest` verde na mesma invocação e sem sonda passada
- [ ] 3.6 `--report` recusa agregar stamps de versões ou modelos diferentes; `--export` remove
      `session_id`, texto de resposta, uuids e caminhos absolutos de HOME

## 4. Tarefas e suítes ocultas

- [ ] 4.1 Seis tarefas em `research/tdd/tasks/`, cada uma com semente commitada, prompt, referência
      boa, referência ruim e suíte oculta
- [ ] 4.2 `research/tdd/scorer-venv.txt` com as versões efetivamente instaladas
- [ ] 4.3 O `--selftest` prova cada scorer contra a referência boa e a ruim antes de qualquer
      célula paga

## 5. Medição

- [ ] 5.1 `--prepare-arms` e `--probe-isolation` (pago, mínimo, em Haiku)
- [ ] 5.2 Piloto n=1 antes da matriz, e a lacuna (a) de E.3 fechada com o que o transcrito mostrou
- [ ] 5.3 Matriz nos dois arms no modelo diário, n>=3, dentro do `--budget-usd`
- [ ] 5.4 `results.md` com a tabela por tarefa e arm, o veredito citado verbatim do protocolo e
      conferido condição por condição, a seção de gasto e a do que não cobre

## 6. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 7. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em toda SKILL.md tocada — **nenhuma skill é tocada por esta change**
- [ ] Q.2 Conteúdo de skill em inglês — nenhuma skill tocada
- [ ] Q.3 Triggers de description testáveis — nenhuma skill tocada
- [ ] Q.4 Sem doutrina duplicada: a tabela Canonical Home do `design.md` declara onde cada regra
      mora, e este item não redige a doutrina TDD
- [ ] Q.5 Identificadores em inglês em todo código novo (`research/tdd/run.py`, tarefas, scorers),
      com a prosa em português como no resto do repositório

## 8. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-tdd-research --strict` green
- [ ] V.2 Catalog discovery intact: contagem de skills inalterada, nenhum órfão
- [ ] V.3 `research/tdd/README.md` com a ordem de leitura e a linha de status
- [ ] V.4 `openspec archive add-tdd-research --yes` after all groups above are `[x]`
