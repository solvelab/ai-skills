# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `7709622` (base de `backlog/145-lean-code-research`) em 2026-09-05:

      - `openspec/specs/skills-catalog/spec.md` — o requisito *A published cost claim carries
        re-runnable backing* (linhas 1089-1133), copiado por inteiro no delta antes da extensão.
      - `openspec/changes/archive/2026-09-01-add-svg-animation-skill/proposal.md` e `tasks.md` —
        forma da casa: defeitos classificados antes da skill, S.1-S.3 com contagens.
      - `research/svg-animation/README.md` — tabela "read in order" e linha de status.
      - `skills/python-rest-api/references/fastapi-envelope.md` — envelope, handlers, registry.
      - `skills/fivem-lua/SKILL.md` (fronteira de confiança, `clampNum`), `skills/fivem-fallback/SKILL.md`.
      - `skills/react-api-client/references/api-client.md` — `ApiClient`, parser zod.
      - `install.sh` (`setup_claude`, symlinks) e `scripts/smoke-install-scripts.sh` (fallback `HOME=`).
      - `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py`, `scripts/validate-spec-rite.py`,
        `scripts/scan-secrets.py`, `scripts/validate-repo-hygiene.py` — o que os gates leem.
      - Fora do repositório, no clone do ponytail em `974d940a` (2026-09-04):
        `benchmarks/agentic/run.py`, `benchmarks/agentic/tasks.py`, `benchmarks/agentic/README.md`,
        `benchmarks/loc.js`, `benchmarks/results/2026-06-18-agentic.md`, `examples/*.md` (11), `LICENSE`.
      - `~/.claude/settings.json` (só leitura): chaves `model`, `effortLevel`, `modelSettings`,
        `skillOverrides`, `hooks`, `enabledPlugins`, `extraKnownMarketplaces`, `statusLine`, `permissions`.

- [x] E.2 Ferramentas, flags e versões probadas na máquina, não recordadas

      `claude --version` -> `2.1.261 (Claude Code)`

      `claude --help | grep -nE "max-budget|disallowedTools|strict-mcp|session-persistence|append-system-prompt|--tools"`
      -> `--max-budget-usd <amount>`, `--disallowedTools, --disallowed-tools <tools...>`,
      `--strict-mcp-config`, `--no-session-persistence`, `--append-system-prompt <prompt>`,
      `--tools <tools...>`, `--setting-sources <sources>`, `--plugin-dir <path>`; **não** existe
      `--config-dir`.

      `grep -oE "CLAUDE_CONFIG_DIR" ~/.local/share/claude/versions/2.1.261 | wc -l` -> `4`;
      `grep -oE "hook_(started|response|progress|event_name)" <binário> | sort | uniq -c` -> vazio (0).

      `grep -oE "\.caveman-active|CLAUDE_CONFIG_DIR|homedir\(\)" ~/.claude/plugins/cache/caveman/caveman/81536f57b330/src/hooks/caveman-activate.js | sort | uniq -c`
      -> `2 .caveman-active`, `4 CLAUDE_CONFIG_DIR`, `3 homedir()`.

      `openspec --version` -> `1.6.0`; `openspec new change --help` -> `--schema <name>`.

      `lua -v` -> `Lua 5.5.0`; `lua probe.lua` com `math.type` sobre `2, "10", 1e9, -5, 2.5` ->
      `integer nil float integer float`.

      `node --version` -> `v26.0.0`.

      `uv pip install --python venv/bin/python fastapi httpx pydantic` -> `fastapi 0.141.1`,
      `httpx 0.28.1`, `pydantic 2.13.5`, `starlette 1.6.0` (pinados em `scorer-venv.txt`).

      `grep -rniE "yagni|less code|smallest change|speculative|over-engineer|dead code|tech debt" skills/ claude/global/personal-rules.md | wc -l`
      -> `0`.

      `/usr/bin/git ls-tree --name-only 7709622 skills/ | wc -l` -> `35`.

- [x] E.3 O que não pôde ser probado offline fica escrito como pergunta aberta

      Três lacunas, nenhuma preenchida com substituto plausível:
      (a) se `CLAUDE_CONFIG_DIR` redireciona `skills/`, `CLAUDE.md` e `settings.json` em 2.1.261 —
      o binário carrega a string, a doc não foi lida, e só a sonda paga (`--probe-isolation`,
      parte B) decide entre `config-dir` e o fallback `HOME=`;
      (b) os nomes reais dos campos do JSON de `claude -p --output-format json` em 2.1.261
      (`total_cost_usd`, `num_turns`, `duration_ms`, `usage`, `modelUsage`) — o harness lê todos de
      forma defensiva e a sonda grava as chaves observadas em `probe.json`;
      (c) se um `CLAUDE_CONFIG_DIR` sem `.claude.json` (estado de onboarding) roda headless sem
      prompt interativo — a sonda responde.

- [x] E.4 Escopo: só o que o proposal pede; melhorias vizinhas viram follow-ups

      Follow-ups anotados e não feitos: step de CI para `run.py --selftest` (exige `lua`, `node` e o
      venv no runner); a décima tarefa opcional `fastapi-quantity-bug` do plano; o arm `ponytail-ref`
      via `--plugin-dir` (o harness reserva a opção, o item 2 decide); um `--rescore` que reaplique
      scorers novos a workspaces antigos do upstream. Nada em `skills/`, `README.md`, `generate.sh`
      ou `ci.yml` foi tocado.

## 2. Protocolo e harness

- [ ] P.1 `research/lean-code/protocol.md` congelado com o sha: arms, célula, métricas, vereditos
      SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE, lista de tarefas, regras de falso positivo da lente
- [ ] P.2 `run.py` stdlib com `--selftest`, `--prepare-arms`, `--probe-isolation`, `--matrix`,
      `--classify`, `--rescore`, `--report --export`; `--matrix` recusa sem selftest verde na mesma
      invocação; `--report` recusa versões/modelos diferentes; `--export` sem `session_id`, `result`,
      uuids e HOME absoluto
- [ ] P.3 Vendor do ponytail em `vendor/ponytail/` (`tasks.py`, `loc.js`, `LICENSE`, `PIN`) e os 11
      `examples/*.md` em `fixtures/examples/`

## 3. Arms e isolamento

- [ ] A.1 `--prepare-arms` monta `<arms-root>/<arm>/` com `settings.json` filtrado, `CLAUDE.md` do ref
      mais sentinela, `skills/` por symlink à árvore do ref, `.credentials.json` modo 600; baseline sem
      `skills/lean-code`; preflight recusa arms-root dentro do repositório
- [ ] A.2 `--probe-isolation` (parte B, paga): sentinela 3/3, eventos de hook do mantenedor 0/3,
      `.caveman-active` ausente 3/3; saída registrada em `results/`

## 4. Tarefas e scorers

- [ ] T.1 Seis tarefas do upstream ligadas: `safe-path`, `sql-user`, `csv-sum`, `cache`, `reuse-slug`,
      `trace-transfer`
- [ ] T.2 `fastapi-create-item`: semente com envelope + registry + repositório por tenant; ruim devolve
      201/500 para `{"name": "", "quantity": -1}`; scorer roda sob o venv via `fastapi.testclient`
- [ ] T.3 `fivem-shop-buy`: `fxmanifest.lua`, `Inventory.give`, `Helpers.clampNum`; stub
      `fivem_stub.lua`; `playerId=2` forjado com `source=1` credita o 1; `qty` `-5`, `"10"`, `1e9`
      rejeitados
- [ ] T.4 `react-use-orders`: esqueleto Vite+TS com `apiClient`, zod, TanStack; scorer ESTRUTURAL e
      rotulado: `package.json` intacto, `z.object`/`.parse`, `apiClient` importado, sem `fetch(`/
      `axios.create(`

## 5. Baseline (parte B)

- [ ] B.1 Piloto Haiku n=1 nas 9 tarefas (nunca reportado como número), campos do JSON registrados
- [ ] B.2 Baseline no modelo diário, n=3, 9 tarefas, `--budget-usd 25`;
      `results/<stamp>-baseline-defects.md` com contagens por flag, média/min/max, `n`, modelo e CLI

## 6. Simulation & Field Proof (MANDATORY)

- [ ] S.1 `python3 research/lean-code/run.py --selftest` pelo caminho real, saída observada registrada
- [ ] S.2 Matriz de casos como contagens: LOC 22/22 e 11/11, scorers 18/18, detectores, preflight,
      stripper, tree-kill, recusas
- [ ] S.3 O que escapou ou se comportou diferente do esperado, nomeado

## 7. Quality Gates (MANDATORY)

- [ ] Q.1 Nenhuma `SKILL.md` tocada; `python3 scripts/validate-skills.py` e o frontmatter do gate
      inalterados
- [ ] Q.2 Todo conteúdo de `research/lean-code/` em inglês onde é máquina: identificadores, nomes de
      arquivo, chaves de JSON, flags; prosa em português onde é prosa
- [ ] Q.3 Nenhuma doutrina restatada: o harness detecta o marcador e o contrato de saída, não os
      redige (design.md, Canonical Home)
- [ ] Q.4 `python3 scripts/scan-secrets.py` verde; `git ls-files research/lean-code | xargs grep -l
      session_id` vazio
- [ ] Q.5 `bash generate.sh` sem diff; `python3 scripts/validate-repo-hygiene.py` verde

## 8. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-lean-code-research --strict` green
- [ ] V.2 `bash scripts/validate-rite.sh` -> `rite gate OK`; `GITHUB_EVENT_PATH=... python3
      scripts/validate-skill-version.py` -> 0 skills changed
- [ ] V.3 `research/lean-code/README.md` com a ordem de leitura e a linha de status
- [ ] V.4 `openspec archive add-lean-code-research --yes` after all groups above are `[x]`
