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

      `file ~/.local/share/claude/versions/2.1.261` -> `ELF 64-bit LSB executable`;
      `grep -oaE "CLAUDE_CONFIG_DIR" <binário> | wc -l` -> `59` (sem `-a` o grep imprime
      `binary file matches` e o `wc -l` dá `0` — a primeira redação registrou um `4` que não reproduz);
      `grep -oaE "hook_(started|response|progress|event_name)" <binário> | sort | uniq -c` ->
      `91 hook_event_name`, `19 hook_progress`, `27 hook_response`, `7 hook_started`; contexto no
      binário: `Uu({type:"system",subtype:"hook_started",hook_id:e,hook_name:t,hook_event:r})` — um
      evento `system/hook_started` do `stream-json`, que `parse_stream` lê e o filtro `hook` da sonda conta.

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

- [x] P.1 `research/lean-code/protocol.md` congelado com o sha: arms, célula, métricas, vereditos
      SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE, lista de tarefas, regras de falso positivo da lente

      `grep -c "^| \*\*" research/lean-code/protocol.md` -> `4` linhas de veredito;
      `grep -n "Frozen" research/lean-code/protocol.md` -> `3:**Frozen** at base \`7709622\``;
      cinco regras de falso positivo numeradas na seção *Review lens*.

- [x] P.2 `run.py` stdlib com `--selftest`, `--prepare-arms`, `--probe-isolation`, `--matrix`,
      `--classify`, `--rescore`, `--report --export`; `--matrix` recusa sem selftest verde na mesma
      invocação; `--report` recusa versões/modelos diferentes; `--export` sem ids de sessão, `result`,
      uuids e HOME absoluto

      `python3 research/lean-code/run.py --matrix ... --arms-root /tmp/nowhere ...` (sem `--selftest`)
      -> `refusing --matrix: --selftest did not pass in this invocation`, rc 1.
      `python3 run.py --selftest --matrix ...` com arms preparados e sonda ausente ->
      `refusing --matrix: the isolation probe has not passed for these arms`, rc 1.
      `python3 run.py --report runs-sim/sim-a runs-sim/sim-oldcli` ->
      `refusing to aggregate: claude versions differ: ['2.1.177 (Claude Code)', '2.1.261 (Claude Code)']`;
      `--report runs-sim/sim-a runs-sim/sim-haiku` -> `refusing to aggregate: model ids differ`.
      `--report runs-sim/sim-a runs-sim/sim-b --export runs-sim/export-ab.json` -> `wrote`; depois
      `grep -c session_id export-ab.json` -> `0`, `grep -c /home/diegops` -> `0`, `grep -c '"result"'` -> `0`,
      `grep -c 426614174000` -> `0` (o uuid sintético). `python3 -m py_compile run.py` -> ok; só stdlib
      importada (`import` de `argparse … typing`).

- [x] P.3 Vendor do ponytail em `vendor/ponytail/` (`tasks.py`, `loc.js`, `LICENSE`, `PIN`) e os 11
      `examples/*.md` em `fixtures/examples/`

      `sha256sum tasks.py loc.js LICENSE` -> `68f47355…`, `c3c346f8…`, `fb1bc690…`, gravados no `PIN`
      com o commit `974d940a1c5344210874150b98ff0d2c861fab6a` (2026-09-04 14:35:29 +0200, v4.9.0);
      `ls fixtures/examples/*.md | wc -l` -> `11` (mais o README).

## 3. Arms e isolamento

- [x] A.1 `--prepare-arms` monta `<arms-root>/<arm>/` com `settings.json` filtrado, `CLAUDE.md` do ref
      mais sentinela, `skills/` por symlink à árvore do ref, `.credentials.json` modo 600; baseline sem
      `skills/lean-code`; preflight recusa arms-root dentro do repositório

      `python3 run.py --prepare-arms --arms-root <scratch>/lean-dev/arms --rules-ref HEAD` ->
      `note: skills/lean-code does not exist at HEAD; only the baseline arm is prepared`,
      `arm baseline … preflight OK`, `wrote …/arms.json`. Inspeção: `settings.json` com exatamente
      `model`, `effortLevel`, `modelSettings`, `skillOverrides`; `tail -2 CLAUDE.md` ->
      `BENCH-SENTINEL: baseline`; `stat -c %a .credentials.json` -> `600`;
      `ls skills | wc -l` -> `35`; `readlink skills/bug-hunter` -> `…/arms/_tree/02b1b89faeb4/skills/bug-hunter`
      (árvore materializada por `git archive`, não a working tree). `--prepare-arms --arms-root research/lean-code/_arms`
      -> `refusing: --arms-root research/lean-code/_arms resolves inside the repository`, rc 1.

- [ ] A.2 `--probe-isolation` (parte B, paga): sentinela 3/3, eventos de hook do mantenedor 0/3,
      `.caveman-active` ausente 3/3; saída registrada em `results/`

## 4. Tarefas e scorers

- [x] T.1 Seis tarefas do upstream ligadas: `safe-path`, `sql-user`, `csv-sum`, `cache`, `reuse-slug`,
      `trace-transfer`

      `run.py --selftest` -> `OK tasks nine tasks wired (6 upstream + 3 catalog)` e 12/12 linhas
      `OK scorers <id> good|bad` para as seis (bom `correct=1 safe=1`; ruim pego no eixo:
      `cache bad correct=0 … axis=correct`, `trace-transfer bad … patched only transfer; withdraw still overdraws`).

- [x] T.2 `fastapi-create-item`: semente com envelope + registry + repositório por tenant; cada corpo
      inválido disparado sozinho (`name` vazio, `quantity` -1, 3.7, `"abc"`, e o combinado) tem de dar
      4xx no envelope de erro; `tenant_id` forjado no corpo não pode sobrepor o header; scorer roda sob
      o venv via `fastapi.testclient`

      `LEAN_SCORER_VENV=<venv> python3 tasks/fastapi-create-item/task.py <seed+good>` ->
      `{"correct": 1, "safe": 1, "reuse": 1, "reason": "ok"}`; `<seed+bad>` ->
      `{"correct": 1, "safe": 0, "reuse": 1, "reason": "empty name answered 201 status='success'; negative quantity answered 201 status='success'; fractional quantity answered 500 status='error'; non-numeric quantity answered 500 status='error'; empty name + negative quantity answered 201 status='success'"}`;
      variantes do bom (revisão, antes disparavam `safe=1`): `name: str` sem `min_length` ->
      `safe 0 … empty name answered 201`; `quantity: int` sem `ge` -> `safe 0 … negative quantity answered 201`;
      `quantity: float = Field(ge=0)` -> `safe 0 … fractional quantity answered 500`; `tenant_id` no
      corpo sobrepondo o header -> `safe 0 … body tenant_id overrode the header (B get=200, B listed=True)`.
      As quatro estão em `VARIANTS` e o selftest as exige (`scorers fastapi-create-item variant …` 4/4).
      Diretório sem `app/` -> `import failed: ModuleNotFoundError: No module named 'app'`;
      sem venv -> `scorer venv not found: set LEAN_SCORER_VENV / --scorer-venv (see scorer-venv.txt)`.

- [x] T.3 `fivem-shop-buy`: `fxmanifest.lua`, `Inventory.give`, `Helpers.clampNum`; stub
      `fivem_stub.lua`; `safe` julga o ledger, não o estilo: `playerId=2` forjado com `source=1` nunca
      credita o 2 (creditar o 1 ou rejeitar são ambos seguros, gravado em `outcomes.forged_playerid`);
      `qty` `-5`, `"10"`, `1e9`, `2.5`, `0` ou deixam o ledger intocado ou creditam um inteiro em
      `[1, maxQty]` (clamp); crédito negativo, zero, fracionário ou acima do máximo é inseguro

      `python3 tasks/fivem-shop-buy/task.py <seed+good>` -> `{"correct": 1, "safe": 1, "reason": "ok", "outcomes": {"forged_playerid": "credited_source", "qty_clamped": 0, "qty_rejected": 5}}`;
      `<seed+bad>` -> `{"correct": 1, "safe": 0, "reason": "forged playerId: p1=0 p2=2; qty=-5 accepted (p1 bread=-5); qty=1000000000.0 accepted (p1 bread=1000000000.0); qty=2.5 accepted (p1 bread=2.5); qty=0 accepted (p1 bread=0); unknown item accepted", "outcomes": {"forged_playerid": "credited_forged_id", "qty_clamped": 1, …}}`
      (o `"10"` coagido por `tonumber` cai dentro de `[1, 10]` e conta como clamp, não como guard perdido);
      semente intocada -> `{"correct": 0, "safe": 1, "reason": "valid buy credited 0", …}`.
      Variantes do bom (revisão): `if payload.playerId ~= src then return Helpers.reject(...)` ->
      `safe 1 … ok (forged playerId rejected, not credited)` (antes: `safe 0 … forged playerId: p1=0 p2=0`);
      `math.floor(Helpers.clampNum(payload.qty, 1, item.maxQty, 1))` -> `safe 1 … ok (qty clamped on 5/5 out-of-range cases)`
      (antes: `safe 0` nos cinco casos); `Helpers.clampNum(...)` sem `floor` -> `safe 0 … qty=2.5 accepted (p1 bread=2.5)`.
      As três estão em `VARIANTS` e o selftest as exige (`scorers fivem-shop-buy variant …` 3/3).
      Ordem de carga lida do `fxmanifest.lua` (`shared_scripts` + `server_scripts`).

- [x] T.4 `react-use-orders`: esqueleto Vite+TS com `apiClient`, zod, TanStack; scorer ESTRUTURAL e
      rotulado: `package.json` intacto, `z.object`/`.parse`, `apiClient` importado, sem `fetch(`/
      `axios.create(`

      `run.py --selftest` -> `OK scorers react-use-orders good [STRUCTURAL] correct=1 safe=1 … STRUCTURAL: ok`
      e `react-use-orders bad [STRUCTURAL] correct=0 safe=0 … STRUCTURAL: package.json changed (new dependency?); does not wrap useQuery; …`.
      O rótulo `STRUCTURAL` aparece na `reason`, na tabela do `--report` (`(STRUCTURAL scorer)`) e no
      `baseline-defects.md` (`react-use-orders (STRUCTURAL)`).

## 5. Baseline (parte B)

- [ ] B.1 Piloto Haiku n=1 nas 9 tarefas (nunca reportado como número), campos do JSON registrados
- [ ] B.2 Baseline no modelo diário, n=3, 9 tarefas, `--budget-usd 25`;
      `results/<stamp>-baseline-defects.md` com contagens por flag, média/min/max, `n`, modelo e CLI

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 `python3 research/lean-code/run.py --selftest` pelo caminho real, saída observada registrada

      `LEAN_SCORER_VENV=<scratch>/lean-dev/venv python3 research/lean-code/run.py --selftest` ->
      `selftest: 111/111 OK  (tasks 1/1, loc 34/34, scorers 25/25, detectors 23/23, arms 15/15, export 3/3, kill 1/1, refusals 5/5, metrics 4/4)`
      e `selftest wall time: 2.0s (target < 15s)`, rc 0 (antes da revisão: `101/101`, scorers 18/18,
      detectores 20/20; as 7 variantes e os 3 silêncios do `new_dependency` são o acréscimo). Também
      pelo caminho real, sem gasto: `--prepare-arms` no scratch (A.1); depois da troca dos scorers,
      `--rescore runs-sim/sim-a` -> `rescored 18 cells` e `--classify runs-sim/sim-a` ->
      `wrote …/sim-a-baseline-defects.md` com a mesma tabela de flags (`guard_dropped 5/18`,
      `patched_caller_only 1/18`, `reimplemented_existing 2/18`, `new_dependency 1/18`,
      `output_contract 9/18`) sobre um stamp **sintético** (18 células = 9 tarefas × referência
      boa/ruim com `_claude.json` falso — nenhuma célula paga rodou); só a coluna `reason` mudou
      (`empty name answered 201 …`, `forged playerId: p1=0 p2=2; …`).

- [x] S.2 Matriz de casos como contagens: LOC 22/22 e 11/11, scorers 18/18, detectores, preflight,
      stripper, tree-kill, recusas

      Tinha de bater e bateu: porte == `loc.js` 22/22 seções; `Without > With` 8/8 nos exemplos de
      contagem de linhas; scorers bom 9/9 e ruim pego no eixo 9/9 (18/18) mais 7/7 variantes do bom
      com veredito decidido (fastapi: validação parcial ×3 e `tenant_id` no corpo -> `safe 0`; fivem:
      rejeição do `playerId` forjado -> `safe 1`, `clampNum`+`floor` -> `safe 1`, `clampNum` sem
      `floor` -> `safe 0`); detectores que tinham de disparar 12/12 (`output_contract`, `lean_marker`
      bem formado, `one_check` ×2, `new_dependency` ×4, `prose_gt_code`, flags ×2, `lean_marker`
      malformado); preflight pegou 6/6 defeitos injetados (`hooks`, `enabledPlugins`, sentinela
      ausente, credencial 644, `skills/lean-code` no baseline, `.caveman-active`); recusas 4/4
      (`--matrix` sem selftest, `--matrix` sem sonda, `--report` versão diferente, `--report` modelo
      diferente); tree-kill 1/1.
      Tinha de ficar em silêncio e ficou: detectores 11/11 casos negativos (inclui `pip install -r
      requirements.txt`, `npm install` em linha própria e `pip install pytest` com `pytest` declarado);
      preflight 3/3 arms limpos; `--report` com mesma versão e modelo 1/1; export sem
      `session id`/`result`/uuid/HOME 4/4 greps a zero.
      Escape conhecido que ficou onde devia: 3/3 exemplos de remoção de dependência com `With >= Without`.

- [x] S.3 O que escapou ou se comportou diferente do esperado, nomeado

      Três coisas, e a contagem foi o que pegou. (1) O plano assumia `Without > With` 11/11 nos
      exemplos do ponytail; o próprio `loc.js` dá `16 < 17`, `5 < 6`, `4 < 7` em `infinite-scroll`,
      `number-formatting` e `url-params` — são exemplos de "1 dependency → 0 dependencies", onde o
      ganho é a dependência, não a linha. O selftest passou a pinar esses três como exceção declarada
      (`DEPENDENCY_REMOVAL_EXAMPLES`) em vez de afirmar um 11/11 falso; README e protocolo dizem 8/8 + 3.
      (2) O detector de dependência lia `import useSWR from 'swr'` também como `import` Python e
      acusava `useSWR`; corrigido para rodar cada regex só nos arquivos da sua linguagem
      (`added_by_file`), caso adicionado ao selftest. (3) O inventário `json_keys` gravava a string
      do id de sessão como valor e o `grep` de higiene do export dava 36 em vez de 0; o inventário
      passou a omitir os nomes que o stripper remove e a contar quantos omitiu (`json_keys_omitted`).
      (4) A revisão do PR pegou o que o selftest não pegava, porque só havia bom/ruim: o scorer FastAPI
      disparava um único corpo inválido combinado e nunca um `tenant_id` no corpo (três validações
      parciais e um override de tenant passavam `safe=1`); o scorer Lua exigia que o `playerId` forjado
      fosse creditado ao `source` (rejeitar dava `safe=0`) e marcava inseguro o `clampNum` que o
      próprio catálogo ensina; `INSTALL_MENTION` acusava `-r`, `npm` e um `pytest` declarado; e o E.2
      registrava `0` strings de hook no binário por um `grep` sem `-a`. Cada um virou variante ou caso
      silencioso no selftest (101 -> 111) e a redação do E.2 e do Risk 2 foi corrigida com a saída
      observada. A sonda paga e o piloto ficam para a parte B.

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Nenhuma `SKILL.md` tocada; `python3 scripts/validate-skills.py` e o frontmatter do gate
      inalterados

      `gates.sh` -> `PASS validate-skills :: skills checked: 35   findings: 0`, `PASS frontmatter`;
      `GITHUB_EVENT_PATH=event145.json python3 scripts/validate-skill-version.py` ->
      `skill-version gate: 0 findings (base origin/master, 0 skill(s) changed, 0 with content changes)`.

- [x] Q.2 Todo conteúdo de `research/lean-code/` em inglês onde é máquina: identificadores, nomes de
      arquivo, chaves de JSON, flags; prosa em português onde é prosa

      O hook `locale-rite.py` (PostToolUse) só emitiu avisos `en-unknown` para nomes de biblioteca
      (`fastapi`, `pydantic`, `axios`, `fxmanifest`) e da stdlib (`killpg`, `gmatch`) — nenhum termo
      em português; `deps.py` foi renomeado para `dependencies.py` por ser abreviação, não inglês.
      A prosa dos `.md` do diretório está em inglês, como `research/svg-animation/`; os prompts das
      tarefas em inglês porque são o que o agente lê.

- [x] Q.3 Nenhuma doutrina restatada: o harness detecta o marcador e o contrato de saída, não os
      redige (design.md, Canonical Home)

      `grep -c "lean:" research/lean-code/protocol.md` -> `1` (a única linha com o marcador nomeia o formato
      detectado, `lean: <ceiling> -> <trigger>`); nenhuma escada, regra ou carve-out do ponytail
      transcrito fora de `vendor/`.

- [x] Q.4 `python3 scripts/scan-secrets.py` verde; `git ls-files research/lean-code | xargs grep -l
      session_id` vazio

      `python3 scripts/scan-secrets.py` -> `scanned 765 files (working tree)`, `no credentials found`, rc 0;
      `/usr/bin/git ls-files research/lean-code | xargs grep -l session_id` -> vazio (xargs rc 123 = nenhum match
      em 71 arquivos rastreados).

- [x] Q.5 `bash generate.sh` sem diff; `python3 scripts/validate-repo-hygiene.py` verde

      `gates.sh` -> `PASS generate :: Generated 10 category plugins in plugins/`, `PASS tree-clean-after-generate`,
      `PASS hygiene :: repo hygiene: 0 findings`, `PASS hygiene-selftest :: 4/4 defect classes detected`,
      `PASS plugin-validate :: ✔ Validation passed`, `PASS smoke :: smoke: 17/17 cases passed`, `dirty-after: 0`.

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-lean-code-research --strict` green

      `openspec validate add-lean-code-research --strict` -> `Change 'add-lean-code-research' is valid`.

- [x] V.2 `bash scripts/validate-rite.sh` -> `rite gate OK`; `GITHUB_EVENT_PATH=... python3
      scripts/validate-skill-version.py` -> 0 skills changed

      `GITHUB_EVENT_PATH=event145.json bash scripts/validate-rite.sh` -> `rite gate OK`,
      `spec-rite gate: 0 findings`; `validate-skill-version.py` -> `0 skill(s) changed`.

- [x] V.3 `research/lean-code/README.md` com a ordem de leitura e a linha de status

      `grep -n "## Read in this order\|## Status" research/lean-code/README.md` -> ambas as seções;
      a linha de status diz **No paid cell has run** e nomeia CLI `2.1.261`, Lua `5.5.0`, node `v26.0.0`.

- [ ] V.4 `openspec archive add-lean-code-research --yes` after all groups above are `[x]`
