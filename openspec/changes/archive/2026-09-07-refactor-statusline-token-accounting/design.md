# Design: contabilidade de tokens do status line

## Context

`skills/claude-statusline/references/statusline.sh` (idêntico byte a byte ao
`~/.claude/statusline.sh` instalado, verificado com `diff` em 2026-09-07) monta o segmento
`↑ In … · ♻️ … · ↓ Out …` em três etapas:

1. lê `context_window.current_usage` do payload — que é a usage da **última chamada de API**, não do
   turno;
2. banca a tupla anterior num arquivo de estado `~/.claude/statusline-usage/<session_id>` sempre que
   qualquer dos quatro campos muda;
3. multiplica os totais por `price_rates()`, uma tabela de preços embutida no script.

O status line re-renderiza no máximo 1×/s (`refreshInterval`). As chamadas de API não acontecem
nessa cadência. As duas etapas seguintes herdam esse descompasso.

## Goals / Non-Goals

**Goals**

- A soma `↑ In $ + ↓ Out $` bate com `💰` dentro de ±1% em transcripts reais, incluindo
  multi-modelo.
- O script deixa de carregar qualquer preço de modelo.
- Nenhum estado fora do repositório é escrito pelo script.

**Non-Goals**

- Layout, cores, medidores, segmentos de git — intocados.
- Nenhuma tentativa de corrigir a matemática do acumulador mantendo-o.
- Nenhuma migração automática do estado antigo (o script não apaga o que deixou de escrever).

## Decisions

### D1 — Contagens de token vêm do transcript, deduplicadas por `requestId`

`references/fields.md:38` documenta `transcript_path` no payload. O transcript
(`~/.claude/projects/<slug>/<session_id>.jsonl`) carrega uma linha `type: "assistant"` por bloco de
conteúdo, cada uma com `message.usage` completa (incluindo o split
`cache_creation.ephemeral_1h_input_tokens` / `ephemeral_5m_input_tokens`, que o payload não traz) e
`requestId`. Deduplicar por `requestId` recupera uma linha por chamada de API — medido na sessão
`0dd79f69`: 1513 linhas, 901 `requestId` distintos.

Isso substitui a amostragem, que era o defeito dominante: nenhuma chamada é vista duas vezes e
nenhuma é perdida por cair entre dois renders.

Alternativa considerada e rejeitada: consertar o acumulador (bancar por `requestId` a partir do
payload, ler o split de TTL, corrigir a tabela de preços). Rejeitada porque o payload não expõe
`requestId` nem o split de TTL, e porque chamadas que começam e terminam entre dois renders
continuariam invisíveis.

### D2 — Ler a cauda do transcript, não o arquivo inteiro

O transcript cresce sem limite e o status line re-renderiza a cada segundo. Medido em 2026-09-07 num
arquivo de 6.461.943 bytes: `tail -200 | jq` em **7 ms**, `tac | grep -m1` em **13 ms**. Somar
`message.usage` sobre o arquivo inteiro custa muito mais e cresce com a sessão.

A implementação lê a cauda e mantém um acumulado por `requestId` já visto, num cache keyed por
`session_id` — o cache guarda **fatos por chamada** (`requestId` -> usage), não uma estimativa
acumulada, então relê-lo é idempotente e uma leitura perdida não corrompe nada. É a diferença
estrutural para o acumulador removido, cujo estado era uma soma que não podia ser reconferida.

### D3 — Degradar em silêncio, nunca exibir número errado

`transcript_path` ausente, transcript ilegível, ou nenhuma linha com `message.usage` ainda (início de
sessão, logo após `/compact`) ⇒ o segmento de tokens é omitido. Nunca um valor reconstruído sem
marca.

### D4 — O total é do host; o script só o rateia

**Nenhuma fonte viva reconstrói o gasto da sessão.** Medido em 2026-09-07:

- `modelUsage` e `costUSD` só existem em linhas `type: "cost-state"`, escritas no fim da sessão. Um
  transcript vivo tem zero delas (sessão `b7b7e92e`, 368 linhas: 0 ocorrências de `modelUsage`,
  `costUSD` ou `totalCostUSD`).
- As contagens do transcript ficam **abaixo** do que o host cobrou, e o buraco não é recuperável
  dali: na sessão `0dd79f69`, `input` −93.7%, `cache write` −31.2%, `cache read` −13.5%, `output`
  −45.2% contra o razão do host, com todas as 1513 linhas de usage sendo `assistant`,
  `isSidechain: false`, um único modelo.

Logo: a única cifra viva e autoritativa é `cost.total_cost_usd`, e é ela que o `💰` já mostra.

O segmento de custo passa a ser um **rateio** dela. As taxas por modelo decidem apenas a proporção
entre entrada e saída; o valor absoluto vem do host. Consequências:

- `↑ In $ + ↓ Out $ ≡ 💰` por construção — o sintoma que originou o item fica estruturalmente
  impossível, não apenas menos provável;
- uma taxa desatualizada erra o **rateio** em pontos percentuais e nunca produz uma parcela maior
  que o total;
- os valores rateados são marcados como derivados (prefixo `~`), e a skill diz por quê.

Alternativa considerada e rejeitada: exibir o custo calculado token × taxa. Rejeitada porque as
contagens são um piso (acima), então a soma continuaria sem bater com `💰` — 8% de erro na sessão
medida, e o sintoma poderia voltar.

## Canonical Home & Cross-Links (MANDATORY)

| Cross-cutting rule | Canonical home | Action |
|---|---|---|
| Preços por modelo, multiplicadores de cache write (1.25× 5m / 2× 1h) e cache read (0.1×, 0.025× no Fable 5.1) | skill `claude-api` (bundled), `shared/prompt-caching.md` + tabela de modelos | **link** — as taxas deixam de produzir um total e passam a decidir só a proporção do rateio (D4); o que sobra no script é a razão entre entrada e saída, e a skill aponta para a fonte canônica em uma linha, sem restatement |
| Procedência de uma grandeza asserida (measured / derived / assumed) e o dever de dizer o que não deu para verificar | skill `verify-before-claiming` | **link** — o `SKILL.md` referencia; a requisição ADDED do delta é a forma catalogada da mesma regra para scripts publicados |
| Quanto código uma mudança deixa para trás; preferir apagar a remendar | skill `lean-code` | **link** — a decisão D1 é uma aplicação, não uma reformulação |
| Onde um script publicado persiste estado e como o poda | `openspec/specs/skills-catalog` § *Shipped scripts state what they persist* | **already canonical** — inalterada; esta mudança apenas deixa de acioná-la, ao parar de persistir |
| Idioma de identificadores vs. prosa | skill `code-locale` | **already canonical** — nenhum identificador novo em português; nomes vindos do host mantidos literais |

## Risks / Trade-offs

- **Leitura de arquivo a cada render** → cauda com ampliação + teto medido de 50 ms como critério de
  aceitação.
- **`modelUsage` é formato interno do transcript, sem documentação pública** → D3: formato não
  reconhecido degrada para "só `💰`", nunca para um número errado. Registrado como questão aberta.
- **Perda do "custo bancado às taxas daquele turno"** → não é perda real: `modelUsage` já quebra por
  modelo, que é a razão pela qual aquele mecanismo existia.
- **`transcript_path` não observado em payload ao vivo** → questão aberta abaixo; a implementação
  precisa provar antes de depender.

## Migration Plan

Sem migração de dados. Usuários com `~/.claude/statusline-usage/` ficam com um diretório órfão de
alguns KB; o `SKILL.md` diz que pode ser apagado. Rollback é reverter o commit — o script é
stateless depois da mudança, então não há estado a restaurar.

## Open Questions

1. `transcript_path` está documentado em `references/fields.md:38` mas **não** foi observado num
   payload ao vivo: interceptar o payload exigiria editar o `~/.claude/statusline.sh` em uso, o que
   esta análise não fez. A implementação resolve com fallback derivando de `session_id` — o caminho
   `~/.claude/projects/<slug>/<session_id>.jsonl` foi verificado como existente — e a simulação
   registra qual dos dois caminhos foi o usado.
2. **Por que o transcript fica abaixo do razão do host não foi determinado.** As hipóteses
   plausíveis (compactação, retries, chamadas de sistema, o modelo registrado como `claude-opus-5`
   contra `claude-opus-5[1m]` no razão) não foram verificadas. O que está medido é a magnitude do
   buraco, não a sua causa — e é por isso que as contagens são apresentadas como o que são, sem
   serem chamadas de total da sessão.
3. Não foi determinado em que versão do Claude Code as linhas `cost-state` passaram a ser escritas,
   nem se transcripts antigos as carregam. Irrelevante para a implementação, que não as usa.
