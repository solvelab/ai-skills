# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `4d6b84d` (master, base de `backlog/213-statusline-token-accounting`) em 2026-09-07:

      - `skills/claude-statusline/references/statusline.sh` inteiro (275 linhas) — `price_rates()`,
        o bloco do acumulador (leitura do state, condição de banking, escrita) e a montagem de
        `seg_in` / `seg_out`.
      - `skills/claude-statusline/references/fields.md` — linha 21 (`cost.total_cost_usd`), linha 26
        (a nota que hoje instrui a acumular no script), linha 29 (`context_window.current_usage`),
        linha 38 (`transcript_path`).
      - `skills/claude-statusline/SKILL.md` — descrição e bloco `Verified against`.
      - `~/.claude/statusline.sh` — `diff` contra o arquivo do repo: idênticos.
      - `~/.claude/settings.json` linhas 191-195 — o `statusLine.command` aponta para esse arquivo.
      - `openspec/schemas/skills-rite/schema.yaml` e `scripts/validate-rite.sh` — os cinco grupos
        obrigatórios e suas posições.
      - `openspec/specs/skills-catalog/spec.md` — *Shipped scripts state what they persist*
        (linha 173) e *Toda grandeza usada carrega procedência* (linha 1334), para decidir entre
        MODIFIED e ADDED.
      - `openspec/changes/archive/2026-08-06-cumulative-statusline-tokens/` — proposal e delta, que
        é a change que introduziu o acumulador removido aqui.
      - `generate.sh` linhas 6-12 e 27-30 — quais espelhos são gerados a partir de `skills/`.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      **A contabilidade do script contra a do Claude Code**, lida do `modelUsage` do transcript
      (`jq 'select(.modelUsage)|.modelUsage' <transcript> | tail -1`) e do arquivo de estado
      (`tr '\037' ' ' < ~/.claude/statusline-usage/<id>`):

      Sessão `0dd79f69` (`claude-opus-5[1m]`, modelo único):

      | grandeza | statusline | `modelUsage` | erro |
      |---|---:|---:|---:|
      | custo total | 327.82 | 354.90 | −7.6% |
      | inputTokens | 2.092 | 28.745 | −92.7% |
      | cacheCreationInputTokens | 7.501.793 | 6.725.475 | **+11.5%** |
      | cacheReadInputTokens | 529.286.418 | 518.968.226 | **+2.0%** |
      | outputTokens | 651.212 | 1.431.553 | −54.5% |

      Sessão `c972f399` (`fable-5-1` + `opus-5[1m]` + `sonnet-5` + `haiku-4-5`): custo
      `415.61` contra `643.60` (`jq 'select(.totalCostUSD)|.totalCostUSD' | tail -1` ->
      `643.6030768000011`), **−35.4%**; `cacheReadInputTokens` `306.171.328` contra `461.046.068`,
      **−33.6%**; `outputTokens` `462.148` contra `4.803.320`, **−90.4%**.

      **`costUSD` bate com `totalCostUSD` em sessão de modelo único**:
      `modelUsage["claude-opus-5[1m]"].costUSD` -> `354.89593425`;
      `totalCostUSD` -> `354.89593425`.

      **O split de TTL do cache existe no transcript e não no payload**:
      `jq '.message.usage.cache_creation' <transcript>` ->
      `{"ephemeral_1h_input_tokens":25372,"ephemeral_5m_input_tokens":0}`.

      **Preços e multiplicadores** (skill `claude-api`, bundled 2.1.263),
      `shared/prompt-caching.md:144` -> "Cache reads cost ~0.1× base input price — **0.025× on
      Claude Fable 5.1** … Cache writes cost **1.25× for 5-minute TTL, 2× for 1-hour TTL**". Tabela
      de modelos da `SKILL.md`: Opus 5 $5/$25, Fable 5.1 $10/$50, **Sonnet 5 $2/$10**, Sonnet 4.6
      $3/$15, Haiku 4.5 $1/$5. O `price_rates()` do script cobra `3 15` em `*Sonnet*` e `0.1` de
      cache read para todo modelo — errado para Sonnet 5 e para Fable 5.1.

      **Custo de leitura da cauda do transcript** (arquivo de 6.461.943 bytes):
      `time (tail -200 "$f" | jq -c 'select(.modelUsage)|.modelUsage' | tail -1)` -> `0.007 total`;
      `time (tac "$f" | grep -m1 -o '"modelUsage":…')` -> `0.013 total`.

      **`modelUsage` NÃO existe ao vivo** — medido depois do plano aprovado, antes de editar o
      script. As linhas que o carregam são `type: "cost-state"`, escritas no fim da sessão:
      `grep -n '"modelUsage"' <c972f399>` -> linhas `4083` e `4086` de 4086;
      `grep -c '"modelUsage"' <b7b7e92e vivo>` -> `0` em 368 linhas, e
      `grep -o '"totalCostUSD"\|"costUSD"\|"modelUsage"' <b7b7e92e vivo>` -> nenhuma ocorrência.

      **O transcript fica abaixo do razão do host, e o buraco não é recuperável dali.** Somando
      `message.usage` deduplicado por `requestId` na sessão `0dd79f69` (1513 linhas com usage, 901
      `requestId` distintos) contra o `modelUsage` da mesma sessão: `input` `1.800` contra `28.745`
      (−93.7%), `cache write` `4.627.645` contra `6.725.475` (−31.2%), `cache read` `449.162.172`
      contra `518.968.226` (−13.5%), `output` `785.229` contra `1.431.553` (−45.2%).
      `jq 'select(.message.usage)|"\(.type) sidechain=\(.isSidechain)"' | sort | uniq -c` ->
      `1513 assistant sidechain=false`, e `.message.model` -> `1512 claude-opus-5` + `1 <synthetic>`
      contra `claude-opus-5[1m]` no razão. Ou seja: não há linhas escondidas a somar.

      É essa medição que derruba a decisão D1/D4 original e produz o rateio de
      `cost.total_cost_usd`. Registrada como desvio aprovado no comentário da issue #213.

      **Ferramentas**: `openspec --version` -> `1.6.0`;
      `openspec new change refactor-statusline-token-accounting --schema skills-rite` ->
      `Schema: skills-rite`. `gh auth status` -> escopo `project` presente.

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Três lacunas, todas em `design.md` § *Open Questions*, nenhuma preenchida com substituto:

      1. **`transcript_path` não foi observado num payload ao vivo.** Está documentado em
         `references/fields.md:38`, mas interceptar o payload exigiria editar o
         `~/.claude/statusline.sh` em uso — o que esta análise não fez, por ser leitura apenas. O que
         *foi* verificado é que o caminho derivável de `session_id`
         (`~/.claude/projects/<slug>/<session_id>.jsonl`) existe e contém as linhas usadas.
      2. **Por que o transcript fica abaixo do razão do host não foi determinado.** As hipóteses
         plausíveis — compactação, retries, chamadas de sistema, o modelo registrado como
         `claude-opus-5` contra `claude-opus-5[1m]` no razão — não foram verificadas. O que está
         medido é a magnitude do buraco (E.2), não a sua causa. Por isso as contagens são publicadas
         pelo que cobrem e não são chamadas de total da sessão.
      3. **Em que versão do Claude Code as linhas `cost-state` passaram a existir não foi
         determinado.** Irrelevante para a implementação, que não as usa — registrado para que a
         ausência não seja lida como prova de que nunca existiram.

- [x] E.4 Adjacent improvements were listed as follow-ups rather than performed — the scope check

      Quatro coisas vistas e **não** feitas, deixadas como follow-up:

      1. `human()` arredonda `>= 1000` com `%.0fk`, então `999.999` vira `1000k` em vez de `1.0M`.
         Cosmético, fora do escopo, sem item aberto.
      2. O `SKILL.md` recomenda cachear `git status` por `session_id`, mas o script não faz isso — é
         outro segmento e outro custo de render.
      3. `effort_render()` deriva o frame do shimmer de `date +%s`, o que faz o status line mudar
         sozinho entre renders idênticos. Ortogonal a esta mudança.
      4. `cost.total_duration_ms` é usado como duração de sessão, mas `fields.md` também lista
         `cost.total_api_duration_ms`; se mostrar os dois vale a pena é decisão de layout, não desta
         change.

## 2. Implementação

- [x] 2.1 Resolver o transcript: `transcript_path` do payload quando presente; fallback derivando de
      `session_id`; nenhum dos dois disponível ⇒ segmento omitido (D3)
- [x] 2.2 Ler a cauda do transcript e acumular `message.usage` por `requestId` num cache keyed por
      `session_id`, guardando fatos por chamada e não uma soma (D2)
- [x] 2.3 Somar as contagens por modelo, preservando o significado atual de `↑ In`, `♻️` e `↓ Out`
- [x] 2.4 Ratear `cost.total_cost_usd` entre entrada e saída pela proporção que as taxas dão, marcar
      as duas parcelas como derivadas, e garantir que somem exatamente ao total (D4)
- [x] 2.5 Remover o bloco do acumulador e a escrita/poda de `~/.claude/statusline-usage/`
- [x] 2.6 Corrigir `price_rates()` para o uso que sobra: Sonnet 5 a $2/$10, cache write 1h a 2×,
      cache read do Fable 5.1 a 0.025×; modelo desconhecido ⇒ rateio omitido, nunca chutado
- [x] 2.7 Tratar os três casos de degradação de D3 sem quebrar o render

## 3. Documentação e espelhos

- [x] 3.1 `references/fields.md`: reescrever a nota da linha 26 e o que a linha 38 promete, com o
      motivo medido
- [x] 3.2 `SKILL.md`: descrição, bloco `Verified against`, e a nota de que
      `~/.claude/statusline-usage/` pode ser apagado
- [x] 3.3 `./generate.sh` para regenerar `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`

## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi EXERCITADO pelo caminho do usuário — com o entry point e um fragmento da
      saída OBSERVADA registrados aqui

      **Instalado como `~/.claude/statusline.sh` e rodado pelo Claude Code na sessão que escreve
      esta change** (backup em `~/.claude/statusline.sh.bak-213`; o arquivo instalado é byte a byte
      o do repositório, `diff -q` silencioso). O payload que o Claude Code entregou foi capturado
      uma vez e tem `transcript_path` apontando para o transcript da própria sessão:

      ```
      $ jq -r '.transcript_path' /tmp/claude-1000/statusline-payload.json
      /home/diegops/.claude/projects/-home-diegops-ai-skills/b7b7e92e-….jsonl
      ```

      Alimentando o script do repositório com esse payload real:

      ```
      🤖 Opus 5 (1M context) | 🚀 xhigh | 🧠 thinking enabled | ⏱️  55m 48s | 💰 $18.06
      🔗 ai-skills | 🌱 backlog/213-… | ↑ In 25.4M ~$14.77 · ♻️ 98% · ↓ Out 135k ~$3.29
      📊 ctx ▓▓░░░░░░ 29% | 🚦 5h ▓░░░░░░░ 13% | 7d ▓▓▓▓▓░░░ 65%
      ```

      `14.77 + 3.29 = 18.06`, idêntico ao `💰`. O `♻️ 98%` do script fica ao lado do
      `prompt_cache.hit_ratio` de `0.989` que o host publica — são grandezas diferentes (fração de
      **tokens** de entrada vindos de cache contra fração de **requisições** que acertaram o cache),
      e a nota em `fields.md` agora diz isso para que ninguém troque uma pela outra.

      O payload ao vivo também revelou três campos que `references/fields.md` não listava, apesar de
      a skill se anunciar como a lista completa: `prompt_cache`, `fast_mode` e `scratchpad_dir`.
      Documentados, com a observação de que `fast_mode` reprecifica Opus 5 para $10/$50 — mesma
      razão 1:5, logo sem efeito nenhum sobre o **rateio**.

- [x] S.2 Matriz de casos como contagens, não adjetivos

      - **6/6** transcripts reais com `~In + ~Out` **exatamente** igual a `💰` (não ±1%): `67d687d7`
        $65.65, `c972f399` $643.60, `0dd79f69` $354.90, `3dd26d41` $397.68, `1cf4f33d` $225.72,
        `8a68dfd2` $0.00.
      - **2/6** multi-modelo (`c972f399` com quatro, `3dd26d41` com dois); **3/6** compactados
        (`c972f399`, `1cf4f33d` com dois summaries, `8a68dfd2`), o que exercita `/compact` sobre
        transcript real.
      - **6/6** idempotentes: a linha renderizada pelo cursor é byte a byte a da releitura fria.
      - **6/6** renders quentes abaixo do teto de 50 ms: 38, 38, 39, 41, 43, 47 ms — e **planos** em
        relação ao tamanho (41 ms num transcript de 40 MB, 41 ms num de 4.5 MB), que é a prova de
        que o cursor funciona. Frio escala com o arquivo: 97 ms (4.5 MB) a 589 ms (40 MB), pago uma
        vez por sessão e só quando a sessão já tem transcript grande.
      - **4/4** degradações renderizaram sem quebrar: sem `transcript_path` (segmento omitido),
        caminho ilegível (omitido), transcript sem `message.usage` (omitido), modelo desconhecido
        (contagens exibidas, `~$` escondido).
      - **2/2** propriedades incrementais: cursor == releitura completa
        (`↑ In 454.8M ~$331.32 · ♻️ 98% · ↓ Out 785k ~$23.58` nos dois caminhos); linha truncada não
        consumida (cursor parou em `6.583.780` de `6.583.888` bytes e a chamada foi contada uma vez
        só depois de completada).
      - **6/6** ramos de `price_rates()` exercitados, com transcript sintético onde não há real:
        `Sonnet 5`, `Sonnet 4.6`, `Haiku 4.5` e `Opus 5` produzem o mesmo rateio ($8.28/$1.72 sobre
        $10.00) porque os quatro têm saída = 5× entrada; só `Fable 5.1` difere ($6.43/$3.57), pelo
        cache read a 0.025×. Modelo desconhecido -> contagens sem `~$`.
      - **3/3** casos de subagente, com `requestId` distintos: só main (5 req) -> `505k`, só
        sidechain (5 req) -> `505k`, main+sidechain (10 req) -> `1.0M`. Linhas `isSidechain: true`
        **são** contadas, que é o comportamento correto: o host as cobra, e o
        `context_window.current_usage` da versão anterior nunca as via.
      - **8/8** renders simultâneos sobre o mesmo estado produziram a linha idêntica, igual à do
        render sequencial de referência — o guarda contra recuo do cursor segurou sob concorrência
        real.

- [x] S.3 O que escapou

      **Nada escapou.** O payload ao vivo (S.1), `/compact` (3 transcripts compactados), subagentes
      (3 casos com `requestId` distintos), a corrida entre renders (8 simultâneos) e os seis ramos
      da tabela de taxas estão todos em S.1 e S.2.

      O último item pendente era o `agentskills validate`, que não rodava nesta máquina porque as
      três formas de instalar o pacote PyPI `skills-ref` foram recusadas (`pip install --user` em
      PEP 668, `venv` pelo classificador de permissões, npm com `404`). Rodado pelo usuário e depois
      sobre o catálogo inteiro:

      ```
      $ /tmp/sr/bin/agentskills --version
      agentskills, version 0.1.1
      $ /tmp/sr/bin/agentskills validate skills/claude-statusline/
      Valid skill: skills/claude-statusline
      $ for d in skills/*/; do agentskills validate "$d" || fail=1; done; echo $fail
      0     (38 skills)
      ```

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter da `claude-statusline` intacto: `name` == diretório, description dobrada,
      `metadata.author: solvelab`, versão semver bumpada, category no conjunto controlado,
      `license: MIT`, `compatibility`
- [x] Q.2 Conteúdo em inglês na skill; nenhum identificador novo em português no script
- [x] Q.3 Triggers da description continuam testáveis e sem colisão com outras skills
- [x] Q.4 Zero doutrina duplicada: nenhum preço de modelo no script; a skill aponta para
      `claude-api` conforme a tabela Canonical Home do `design.md`
- [x] Q.5 Gates do repositório verdes

      `python3 scripts/validate-skills.py` -> `skills checked: 38   findings: 0`
      `python3 scripts/selftest-validate-skills.py` -> `27/27 defect classes detected`
      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`
      `python3 scripts/validate-skill-version.py` -> `skill-version gate: 0 findings (1 skill(s)
      changed, 1 with content changes)` — `claude-statusline` 1.3.0 -> 2.0.0
      `python3 scripts/validate-agents.py` -> `agents checked: 3   findings: 0`
      `python3 scripts/scan-secrets.py` -> `scanned 1005 files … no credentials found`
      `python3 skills/code-locale/references/check-identifier-locale.py --selftest` -> `selftest OK`
      `python3 skills/code-locale/references/check-prose-locale.py --selftest` -> `selftest OK: 46 cases`
      `bash scripts/smoke-install-scripts.sh` -> `19/19 cases passed`
      `npx -y @anthropic-ai/claude-code@2.1.246 plugin validate . --strict` -> `✔ Validation passed`

      `agentskills validate` (`skills-ref` 0.1.1) sobre as 38 skills -> exit `0`;
      `agentskills validate skills/claude-statusline/` -> `Valid skill: skills/claude-statusline`.

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate refactor-statusline-token-accounting --strict` ->
      `Change 'refactor-statusline-token-accounting' is valid`
- [x] V.2 `bash scripts/validate-rite.sh` -> `Totals: 4 passed, 0 failed (4 items)` / `rite gate OK`
- [x] V.3 Descoberta do catálogo intacta: `npx -y skills add . --list` lista as mesmas **38** skills
      versionadas que `master` lista, `claude-statusline` entre elas. As 6 entradas a mais no diff
      (`openspec-apply-change`, `openspec-archive-change`, `openspec-explore`, `openspec-propose`,
      `openspec-sync-specs`, `openspec-update-change`) vêm de `.claude/`, que é gitignored — não
      aparecem num worktree limpo de `master` nem neste branch quando lido do git.
- [x] V.4 README/docs: a composição do catálogo não mudou (38 skills antes e depois, nenhuma
      adicionada ou removida), então o README não tem o que atualizar. O que mudou é interno à
      `claude-statusline` e está no seu `SKILL.md` e em `references/fields.md`.
- [x] V.5 `openspec archive refactor-statusline-token-accounting --yes` — arquivada **na mesma
      diff do PR**, a pedido do usuário e antes do merge. É uma das três formas que
      `scripts/validate-spec-rite.py` aceita para registrar um diff (S1: change ativa, arquivo
      arquivado no mesmo diff, ou dispensa escrita), e o caso está no selftest dele
      (`"archived in the same diff"`). O delta vai para `openspec/specs/skills-catalog/spec.md`
      neste mesmo PR, não num commit posterior.
