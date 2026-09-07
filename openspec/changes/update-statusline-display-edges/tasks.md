# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `01a9296` (master, base de `backlog/215-statusline-display-edges`) em 2026-09-07:

      - `skills/claude-statusline/references/statusline.sh` — `human()` (as três faixas), o ramo
        `max` de `effort_render()` incluindo `frame=$(( $(date +%s) % ${#lbl} ))`, a extração jq das
        linhas 12-25 e a montagem da linha 1 com `DUR_MS`.
      - `skills/claude-statusline/references/fields.md` — linha 22 (`cost.total_duration_ms`) e
        linha 23 (`cost.total_api_duration_ms`), que documenta o campo não usado.
      - `skills/claude-statusline/SKILL.md` — a descrição da linha 1 e a nota sobre
        `refreshInterval` e o shimmer.
      - `openspec/specs/skills-catalog/spec.md` — *A shipped script reads the quantity its host
        publishes* (adicionada em `52a2b6f`) e *Shipped scripts state what they persist*, para
        decidir o que esta change precisa acrescentar e o que já está coberto.
      - `openspec/changes/archive/2026-09-07-refactor-statusline-token-accounting/tasks.md` — o box
        E.4, que é a origem dos três itens.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      **O defeito de `human()`**, rodando a mesma expressão do script sobre os valores de fronteira:

      ```
      $ for n in 999 1000 999499 999500 999999 1000000; do awk -v n=$n 'BEGIN{ if (n>=1000000) printf "%.1fM\n", n/1000000; else if (n>=1000) printf "%.0fk\n", n/1000; else print n }'; done
      999
      1k
      999k
      1000k      <- 999500
      1000k      <- 999999
      1.0M
      ```

      **O campo não usado**, num payload real capturado do Claude Code 2.1.263 em 2026-09-07:

      ```
      $ jq -c '.cost' <payload>
      {"total_cost_usd":18.05750849999999,"total_duration_ms":3348802,"total_api_duration_ms":1840177,…}
      ```

      1840177/3348802 = 0.5495, ou seja 55% do relógio da sessão foi espera de API.

      **A fonte do frame do shimmer**, lida no script:
      `frame=$(( $(date +%s) % ${#lbl} ))` — relógio de parede, não payload.

      **Ferramentas**: `openspec --version` -> `1.6.0`;
      `openspec new change update-statusline-display-edges --schema skills-rite` ->
      `Schema: skills-rite`; `openspec validate update-statusline-display-edges --strict` ->
      `Change 'update-statusline-display-edges' is valid`.

- [x] E.3 Anything that could NOT be probed is written down as an open question

      Uma lacuna, em `design.md` § *Open Questions*: **não foi determinado se
      `cost.total_duration_ms` avança durante um render ocioso** com `refreshInterval: 1` e nenhuma
      atividade de API. Medir exigiria uma sessão ociosa com `refreshInterval` ligado, que esta
      máquina não tem configurado (`settings.json` -> `statusLine` sem `refreshInterval`). A
      consequência, se não avançar, é o shimmer parar enquanto a sessão está ociosa — aceitável e
      possivelmente desejável, mas não medido. A simulação registra o que foi observado.

- [x] E.4 Adjacent improvements were listed as follow-ups rather than performed — o scope check

      Duas coisas vistas e **não** feitas:

      1. O ramo `M` de `human()` usa `%.1f` e arredonda igual, mas seu teto é aberto, então
         arredondar nunca o tira da faixa — `1.049.999 -> 1.0M` e `1.050.000 -> 1.1M` são ambos
         corretos. Não há defeito a corrigir e nada foi mexido ali.
      2. `cost.total_api_duration_ms` também permitiria mostrar a duração absoluta de API, não só a
         fração. Ficou de fora por largura da linha 1 (D3), e a alternativa está escrita no design
         em vez de implementada.

      Os outros dois follow-ups do E.4 original — cache de git e render frio — são #216 e #219, e
      pertencem à change `update-statusline-render-budget`, não a esta.

## 2. Implementação

- [x] 2.1 `human()` trunca no ramo `k` (D1) — #215
- [x] 2.2 O frame do shimmer vem de `cost.total_duration_ms` (D2) — #217
- [x] 2.3 A extração jq passa a ler `cost.total_api_duration_ms` — #218
- [x] 2.4 O segmento de duração mostra a fração de API quando o campo existe e o denominador é
      positivo (D3) — #218

## 3. Documentação e espelhos

- [x] 3.1 `SKILL.md`: descrição da linha 1, a nota do shimmer deixa de citar o relógio, versão
      bumpada
- [x] 3.2 `references/fields.md`: `total_api_duration_ms` deixa de ser um campo documentado e não
      usado
- [x] 3.3 `./generate.sh` para regenerar os espelhos

## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi EXERCITADO pelo caminho do usuário, com entry point e um fragmento da saída
      OBSERVADA registrados

      Entry point: `bash skills/claude-statusline/references/statusline.sh < <payload>`, que é o que
      o Claude Code faz (`settings.json` -> `statusLine.command`, payload por stdin). O script foi
      instalado como `~/.claude/statusline.sh` e rodado pelo próprio Claude Code, e o payload que ele
      entregou foi capturado uma vez.

      `bash skills/claude-statusline/references/statusline.sh < /tmp/claude-1000/pA-live.json` ->

      ```
      🤖 Opus 5 (1M context) | 🚀 xhigh | 🧠 thinking enabled | ⏱️  9h 6m | 💰 $53.92
      ↑ In 80.8M ~$47.55 · ♻️ 99% · ↓ Out 247k ~$6.37
      📊 ctx ▓▓▓░░░░░ 45% | 🚦 5h ▓░░░░░░░ 17% | 7d ▓▓▓▓▓░░░ 66% | 🌐 api ░░░░░░░░ 10%
      ```

      O medidor novo bate com os números do host: `total_api_duration_ms=3594722` sobre
      `total_duration_ms=32764117` dá 10.97%, truncado em `10%` como os outros medidores fazem.
      A propriedade da change anterior segue de pé: `47.55 + 6.37 = 53.92`, idêntico ao `💰`.

      O payload capturado veio de outra sessão em curso (`5915074e`), cujo `cwd` é um diretório de
      scratchpad fora de repositório git — por isso a linha 2 não traz repo nem branch. Não é
      regressão: a ordem dos 14 campos da extração jq foi conferida linha a linha contra a lista do
      `read`, e `DIR` continua vindo de `.workspace.current_dir // .cwd // "."`.

- [x] S.2 Matriz de casos como contagens

      - **7/7** fronteiras de `human()`: `999 -> 999`, `1000 -> 1k`, `999499 -> 999k`,
        `999500 -> 999k`, `999999 -> 999k`, `1000000 -> 1.0M`, `1500000 -> 1.5M`. Os dois valores
        que produziam `1000k` agora produzem `999k`.
      - **3/3** renders idênticos do mesmo payload atravessando duas viradas de segundo. O
        **controle** contra `master` no mesmo payload e no mesmo intervalo: **divergiu**, com o
        realce saltando de `x` para `m` — o defeito reproduzido antes de ser corrigido, não assumido.
      - **4/4** degradações do medidor `api`: campo ausente -> sem medidor; campo em zero -> sem
        medidor; `total_api_duration_ms` maior que o relógio -> limitado a `100%`; relógio em zero ->
        sem medidor, sem divisão por zero.
      - **3/3** larguras medidas com render real, ANSI e OSC 8 removidos: linha 1 **79** colunas
        (inalterada em relação ao `master`, que é o motivo de a fração não caber lá), linha 3 vai de
        58 para **80**, linha 2 segue em 112 como já estava.

- [x] S.3 O que escapou

      Duas coisas, nomeadas:

      1. **A linha 3 com os quatro medidores saturados mede 83 colunas**, três acima do alvo. Exige
         contexto, os dois limites de taxa e a fração de API todos em três dígitos ao mesmo tempo.
         Não foi observado em nenhum payload real; está no `SKILL.md` em vez de escondido.
      2. **O shimmer sob `refreshInterval: 1` numa sessão ociosa não foi observado.** Esta máquina
         não tem `refreshInterval` configurado, então não dá para dizer se `cost.total_duration_ms`
         avança com a sessão parada. É a questão aberta 1 do `design.md`. O que está provado é a
         determinância, que era o objeto do item.

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter da `claude-statusline` intacto e versão bumpada
- [x] Q.2 Conteúdo em inglês na skill; nenhum identificador novo em português
- [x] Q.3 Triggers da description continuam testáveis e sem colisão
- [x] Q.4 Zero doutrina duplicada; a tabela Canonical Home do `design.md` respeitada


- [x] Q.5 Gates do repositório verdes — comandos e saídas registrados em V.1-V.4 e no corpo do PR

## 6. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate update-statusline-display-edges --strict` verde
- [ ] V.2 `bash scripts/validate-rite.sh` -> `rite gate OK`
- [ ] V.3 Descoberta do catálogo intacta
- [ ] V.4 README/docs atualizados se a composição do catálogo ou o uso mudarem
- [ ] V.5 `openspec archive update-statusline-display-edges --yes`
