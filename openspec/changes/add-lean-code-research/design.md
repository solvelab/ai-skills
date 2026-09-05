# Design — research/lean-code

## Context

O ponytail mede o efeito da sua doutrina com `benchmarks/agentic/run.py`: uma sessão headless real do
Claude Code por célula, workspace semeado, LOC pelo `git diff`, scorers determinísticos que executam
o código produzido contra entrada adversarial. É o instrumento certo e é MIT; o que não serve é o
ambiente em que ele rodou (Haiku 4.5, CC 2.1.177, plugins ativados por `--plugin-dir`) e o fato de o
próprio upstream ter contaminado um baseline com um hook de `SessionStart`.

Este repositório já tem o precedente: `research/svg-animation/` mede antes, a skill cita a medida.

## Goals / Non-Goals

**Goals:**
- Um harness re-executável, `stdlib` só, com `--selftest` offline que prova cada instrumento
  (contador de LOC contra o `loc.js` do upstream, scorer bom/ruim, detectores, preflight de arm,
  stripper de export, tree-kill) **antes** de qualquer gasto.
- Arms em `CLAUDE_CONFIG_DIR` fora do repositório, sem os hooks e plugins do mantenedor, com
  sentinela verificável, e uma sonda paga mínima que decide se o isolamento vale — não a doc.
- Um protocolo congelado com vereditos escritos antes de rodar, para que o item 2 não possa mover
  a meta depois de ver o número.
- Um baseline no modelo diário do mantenedor (`opus[1m]`, resolvido do `settings.json`), n=3, nove
  tarefas, com contagens de defeito por flag — o insumo do `proposal.md` da skill.

**Non-Goals:**
- A skill `lean-code`, a lente de revisão, o bloco em `personal-rules.md` (item 2).
- Juízes LLM (`judge.py`/`complete.py` do upstream), `promptfoo`, o arm `ponytail-ref` (opcional no
  item 2; o harness só reserva o `--ponytail-dir`).
- Step de CI para `run.py --selftest` (depende de `lua`, `node` e de um venv; decisão registrada em
  E.4 como follow-up).

## Decisions

- **Métrica primária: `git diff --cached --numstat HEAD` (linhas adicionadas em arquivos de código,
  testes à parte).** É o `+N` que um PR mostra. O `loc.js` conta LOC de blocos de chat — a métrica
  que o próprio upstream retratou como inflada — e fica só como **oráculo do selftest**: o contador
  portado tem de coincidir com ele 22/22 nos fixtures.
- **Isolamento por `CLAUDE_CONFIG_DIR`, com fallback `HOME=`.** `claude --help` em 2.1.261 não tem
  `--config-dir`; o binário carrega a string `CLAUDE_CONFIG_DIR` e o `caveman-activate.js` a lê
  para escrever `.caveman-active`. Se a sonda mostrar que `CLAUDE_CONFIG_DIR` não redireciona
  `skills/`, `CLAUDE.md` ou `settings.json`, o harness troca para `HOME=<arm>/home` com
  `home/.claude -> ..`, o padrão que `scripts/smoke-install-scripts.sh` já usa.
- **`settings.json` do arm = o do mantenedor menos o que contamina.** Remove `hooks`,
  `enabledPlugins`, `extraKnownMarketplaces`, `statusLine`, `permissions`; mantém `model`,
  `effortLevel`, `modelSettings`, `skillOverrides`. `skillOverrides` fica porque o mantenedor roda
  com ele — um baseline sem ele mediria um usuário que não existe.
- **`skills/` por symlink para uma árvore materializada do ref (`git archive <ref> skills/`)**, nunca
  para a working tree: o arm fica congelado no sha mesmo que o repositório mude durante a matriz.
  O baseline nunca recebe `skills/lean-code`.
- **Scorers executam.** Python importa o módulo produzido; FastAPI roda sob `fastapi.testclient` num
  venv pinado (`scorer-venv.txt`); Lua roda sob `lua` 5.5 com um stub de `RegisterNetEvent`/`source`.
  O React é a exceção declarada: scorer **estrutural** (package.json intacto, `z.object`/`.parse`,
  `apiClient` importado, sem `fetch(`/`axios.create(`), rotulado como tal em toda saída.
- **Vereditos antes do número** (`protocol.md`): SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE com
  limiares numéricos; qualquer guard perdido ou tarefa acima de baseline+10% é REWRITE.
- **`--matrix` recusa sem selftest verde na mesma invocação; `--report` recusa agregar versões ou
  modelos diferentes.** Um número de duas versões do CLI não é um número.
- **`--export` remove `session_id`, `result`, uuids e caminhos absolutos de HOME.** O que vai para
  `results/` é agregado e anonimizado; os workspaces ficam no scratch.
- **Orçamento em duas camadas:** `--max-budget-usd 1.00` por célula e `--budget-usd` na run; a run
  para e reporta ao bater o teto.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Método de medição de ganho de comportamento (arms, célula, métricas, vereditos, sonda) | `research/lean-code/protocol.md` (este diretório; não é skill, não é publicado) | already canonical — nada em `skills/` restata |
| A doutrina lean-code em si (escada, causa raiz, carve-outs, marcador `lean:`) | futura `lean-code` (item 2, `add-lean-code-doctrine`) | **não mora aqui**: o harness só a detecta (`lean_marker`, `output_contract`); a redação é do item 2 |
| Fronteira de confiança (validar payload, ator vem de `source`, `clampNum`) | `fivem-lua`, `fivem-fallback`, `backend-resilience` | link — as tarefas `fivem-shop-buy`/`fastapi-create-item` exercitam a regra; não a reescrevem |
| Envelope, registry de códigos, 422 no envelope, isolamento de tenant | `python-rest-api` (`references/fastapi-envelope.md`) | link — a semente do `fastapi-create-item` é construída a partir dela |
| Reusar `apiClient`, parser zod por domínio | `react-api-client` | link — semente do `react-use-orders` |
| Claim publicado carrega backing re-executável, método e alcance | `skills-catalog` spec (MODIFIED aqui) | move — o requisito ganha o caso "ganho de comportamento" |
| Escopo *Doing / Not doing / Assumptions*, nada de achismo | `verify-before-claiming` | link — `tasks.md` cita, não restata |
| Simulação antes de entregar | `execute-backlog` (passo 8) e o grupo S do schema | already canonical |

## Risks / Trade-offs

- **`CLAUDE_CONFIG_DIR` pode não redirecionar tudo.** Mitigação: a sonda paga (3 chamadas Haiku,
  `--max-budget-usd 0.05`) decide entre `config-dir` e `home`; nenhuma célula roda antes de 3/3.
- **A sonda não vê hooks diretamente.** O binário 2.1.261 não carrega as strings `hook_started`/
  `hook_response` (`grep -c` -> 0), então o `stream-json` provavelmente não emite eventos de hook.
  A sonda registra o vocabulário de eventos observado e os efeitos colaterais que os hooks do
  mantenedor deixariam (`.caveman-active` no dir do arm; texto do rito de backlog no contexto). É um
  proxy e está declarado como tal.
- **Scorer React estrutural pode aceitar código errado.** Declarado em toda saída; não entra no eixo
  `safe` do veredito, só no `reuse`.
- **Custo.** Piloto em Haiku antes; teto por célula e por run; a run para e reporta ao bater.
- **`skillOverrides` mantido desliga 16 skills no arm.** É o ambiente real do mantenedor; a alternativa
  mede outro usuário. Registrado no `protocol.md`.
