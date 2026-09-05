## Context

`claude/global/hooks/locale-rite.py` lido em `80ee53c` (2026-09-05): 260 linhas. `evaluate(payload,
check)` em 175-193 lê `tool_name`, `tool_input.file_path`/`notebook_path`, `cwd`, chama
`findings_for()` e devolve `report(findings)`; `report()` em 155-172 monta sempre
`{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": ...}, "systemMessage":
...}` e trunca em `CONTEXT_CAP = 8000`. O hook não lê `hook_event_name`, então rodá-lo em
`PreToolUse` hoje devolve um envelope com `hookEventName: "PostToolUse"` — que o bundle descarta por
`hookSpecificOutput_event_mismatch` (ver D1). O docstring já registra o probe do
`additionalContext:8000` contra o bundle 2.1.246/2.1.260/2.1.261.

O que o bundle instalado (`readlink -f $(which claude)` -> `~/.local/share/claude/versions/2.1.261`,
`claude --version` -> `2.1.261 (Claude Code)`, ELF único) mostra sobre `PreToolUse`, extraído com um
`re.finditer` em Python sobre os bytes (o `grep` da máquina é `ugrep` e recusa o padrão):

- Schema de saída aceito:
  `c({hookEventName:C("PreToolUse"),permissionDecision:boe().optional(),permissionDecisionReason:s().optional(),updatedInput:pe(s(),se()).optional(),additionalContext:s().optional()})`.
- Normalização: `case"PreToolUse":{let o=t.permissionDecision==="deny"||t.permissionDecision==="ask";
  ... let d=o?X5(e,"permissionDecisionReason",t.permissionDecisionReason):void 0,
  f=X5(e,"additionalContext",t.additionalContext);return{hookEventName:"PreToolUse",...o&&{permissionDecision:t.permissionDecision},...d!==void 0&&{permissionDecisionReason:d},...f!==void 0&&{additionalContext:f}}}`
  — o motivo só sobrevive com `deny`/`ask`; `additionalContext` sobrevive em qualquer decisão.
- Caps: `AKr={reason:2000,stopReason:2000,systemMessage:4000,additionalContext:8000,permissionDecisionReason:2000}`
  (caracteres) e `RKr={reason:20,...,additionalContext:200,permissionDecisionReason:20}` (linhas);
  `X5(e,t,r)` chama `Phn(r,AKr[t],RKr[t])`, que corta em `o.slice(0,r)` linhas e depois em `t`
  caracteres. O cap de **linhas** não estava registrado no docstring: `additionalContext` também tem
  um, de 200.
- Payload de entrada: `c({hook_event_name:C("PreToolUse"),tool_name:s(),tool_input:se(),tool_use_id:s()})`
  sobre a base `c({session_id:s(),transcript_path:s(),cwd:s(),...})`; `PostToolUse` acrescenta
  `tool_response` e `duration_ms`.
- Descarte por evento: `function PKr(e,t,r){if(t.hookEventName!==r){Ik(e,"hookSpecificOutput_event_mismatch",!0);return}`.
- O caminho de `exit 2` também nega: `if(e!=="PreToolUse")return{...o,decision:"block",reason:t};
  ... return{...o,hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:t,...}}`
  com o stderr como motivo — não usado aqui (D2).
- O `additionalContext` de `PreToolUse` chega ao modelo: `yield{type:"additionalContext",message:{message:fn({type:"hook_additional_context",content:q.additionalContexts,hookName:\`PreToolUse:${t.name}\`,...,hookEvent:"PreToolUse"})}}`.

## Goals / Non-Goals

**Goals:**

- Um `Write`/`Edit`/`MultiEdit`/`NotebookEdit` cujo conteúdo novo ou caminho carrega achado gating é
  negado antes de gravar; o motivo lista cada achado (deduplicado por token) e termina com as três
  saídas; cabe em 2000 caracteres e 20 linhas.
- A mesma escrita com `# locale-ok: <motivo>` ou com o nome em `.identifier-locale-allow` é gravada
  em silêncio; só `en-unknown` nunca nega; `LOCALE_RITE_MODE=inform` nunca nega.
- `PostToolUse` idêntico ao de hoje: os 12 casos do selftest atual continuam verdes sem edição.
- Payload sem `hook_event_name`, ou com um valor que não é `PreToolUse`, cai no envelope consultivo:
  na dúvida o hook informa, nunca nega.

**Non-Goals:**

- Escritas via Bash. O hook só vê as ferramentas de escrita do harness; heredoc, `sed` e scripts
  passam. É o gate de Stop da issue #138, declarado como KNOWN LIMIT no docstring.
- `README.md`. A seção dos hooks é documentada por outro item, junto com o wiring de todos.
- Reescrever `report()` do `PostToolUse` para o cap de 200 linhas recém-medido. O harness corta o
  fim, e cada achado é autocontido; registrado no docstring, não tratado.
- `updatedInput`. O bundle aceita reescrever o input da ferramenta; renomear por conta própria seria
  inventar uma tradução — a regra de Grounding proíbe, e o motivo da negação já pede que o modelo
  renomeie ou dispense.

## Decisions

### D1 — O evento vem do payload, e o envelope segue o evento

`payload.get("hook_event_name")` decide o envelope; `evaluate()` continua a única função que decide
se há achado. `"PreToolUse"` com achado gating -> envelope de negação com `hookEventName:
"PreToolUse"`. Qualquer outro valor (`"PostToolUse"`, ausente, não-string) -> o envelope consultivo
de hoje, byte a byte. O bundle descarta um `hookEventName` que não bate com o evento
(`hookSpecificOutput_event_mismatch`), então errar o nome do evento não bloqueia nem informa: por
isso o nome sai do payload e não de uma constante.

### D2 — JSON com `permissionDecision`, não `exit 2`

Os dois negam (Context). O JSON leva o motivo por um campo com cap conhecido (2000/20) e deixa o
stderr livre; `exit 2` usa o stderr como motivo e o bundle o embrulha em `[label]: ...`, com um cap
que não medimos. O hook já fala JSON no `PostToolUse`; um só formato de saída é mais fácil de fixar
no selftest.

### D3 — O motivo é compacto: uma linha por achado, deduplicado, as saídas no fim

O `render()` do check gasta 5 linhas por identificador e 4 por caminho; com o cap de 20 linhas, 4
achados já estourariam e o harness cortaria justamente as saídas, que ficam no fim. O motivo da
negação usa uma forma própria: cabeçalho (1 linha), até `REASON_MAX_FINDINGS = 12` linhas
`path:line: token  [tier: 'segment']` deduplicadas por `(path, token)` — no exemplo da issue, `preco`
aparece em duas linhas e vira uma —, uma linha `+N more` quando sobra, uma linha contando os
`en-unknown` (advisory, que não negam e chegam pelo `PostToolUse` quando a escrita limpa acontecer) e
as três saídas em 3 linhas. Máximo 18 linhas. O corte em caracteres é feito no hook, antes do
harness, preservando o rabo (as saídas) — o mesmo argumento do `CONTEXT_CAP` de hoje.

### D4 — `en-unknown` sozinho não nega, e em `PreToolUse` fica mudo

O bundle honra `additionalContext` em `PreToolUse` (Context), então o aviso **poderia** sair antes da
escrita. Não sai: com os dois eventos wired, o mesmo aviso chegaria duas vezes — antes e depois da
mesma escrita — e o `PostToolUse` já o entrega hoje. Em `PreToolUse`, achado só advisory -> `None`.
Fica registrado que o campo é honrado, para quem vier a precisar dele; a decisão de não usar é por
duplicação, não por limitação do harness.

### D5 — `LOCALE_RITE_MODE=inform` desliga a negação, não o hook

Com a variável em `inform` (comparação case-insensitive, espaços aparados), `PreToolUse` devolve
`None` para qualquer achado: a escrita acontece e o `PostToolUse` informa como hoje. O aviso não é
duplicado no `PreToolUse` pelo mesmo motivo de D4. Qualquer outro valor da variável (vazio, ausente,
grafado errado) é o modo padrão, que nega: um `LOCALE_RITE_MODE=informar` por engano não abre a
porta em silêncio. `evaluate()` recebe o modo como parâmetro com default lido do ambiente, para que
o selftest fixe os dois modos sem tocar `os.environ`; um caso extra passa a variável pelo caminho
real (subprocess com `env`), porque é a única forma de provar que o default lê o ambiente.

### D6 — A linha do achado num `Edit` em `PreToolUse` é a do `old_string`

`first_line_of()` localiza o `new_string` no arquivo já gravado. Antes da escrita ele ainda não está
lá; o que está é o `old_string`, no ponto onde o `new_string` vai entrar. Em `PreToolUse` a âncora
passa a ser `old_string` quando existe; para `Write` o conteúdo inteiro começa na linha 1 e nada
muda. Fragmento não localizado cai em 1, como hoje.

### D7 — As três saídas no motivo, nomeadas, não descritas

O motivo termina com as três linhas literais: `# locale-ok: <reason>` na linha acima (só
identificadores — um nome de arquivo não tem onde carregar comentário, como o check já diz), a
entrada em `.identifier-locale-allow` (a única saída para caminho), e
`export LOCALE_RITE_MODE=inform`. O modelo que lê o motivo tem de conseguir agir sem abrir a skill;
um motivo que só diz "há saídas" gera a segunda tentativa cega que a issue lista como risco.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Camada de máquina em inglês; `locale-ok:` e `.identifier-locale-allow` como dispensas | `code-locale` | already canonical — o motivo da negação **nomeia** as dispensas e aponta para a skill; nada é reescrito |
| O hook mede no momento da escrita e o que escapa dele | `skills-catalog` (spec do repositório, *The code-locale rite is enforced at the moment of the write*) | already canonical — o delta modifica esse requisito; o docstring declara o KNOWN LIMIT |
| Forma da saída probada contra o bundle, não recordada | `verify-before-claiming` | already canonical — Context registra os fragmentos e a versão |
| Regra em contexto na seção *Code Locale* das regras pessoais | `claude/global/personal-rules.md` (link para `code-locale`) | link — a seção ganha uma frase e continua apontando para a skill |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — `REASON_CAP`, `REASON_LINE_CAP`, `deny_reason`, `MODE_ENV`, `LOCALE_RITE_MODE` |

Nenhuma skill do catálogo é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **Negar uma escrita legítima com termo de domínio** -> as três saídas estão no motivo, literais
  (D7); `locale-ok:` custa uma linha. O check já mantém `DOMAIN_KEEP` (CPF, CNPJ, PIX...) fora dos
  achados.
- **Loop modelo-tenta-de-novo** -> o motivo pede "rename it, or waive it" e nomeia as saídas; o
  número de tentativas até a saída é medido na sessão real do mantenedor (S.1 declara que a simulação
  daqui é por stdin).
- **O cap de 20 linhas corta as saídas** -> D3 limita o motivo a 18 linhas por construção; o selftest
  afirma `len(reason) <= 2000` e `reason.count("\n") < 20` num payload com 30 achados.
- **Wired só o bloco `PreToolUse`** -> `en-unknown` nunca chega e `inform` fica mudo, porque os dois
  dependem do `PostToolUse` (D4, D5). O docstring mostra os dois blocos juntos e diz por quê.
- **Bash continua passando** -> KNOWN LIMIT declarado; fechado pela issue #138, não por esta.

## Open Questions

Nenhuma sobre o harness: forma, caps, campo de evento e descarte por mismatch foram lidos no bundle
instalado (Context), não na doc. O que esta change não mede é o comportamento numa sessão real com o
hook wired — a simulação daqui alimenta o hook por stdin com payloads na forma do bundle, e a corrida
na sessão do mantenedor é o passo de aceite (tasks.md, S.1).
