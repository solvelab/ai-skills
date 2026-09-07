# Design: três arestas de exibição do status line

## Context

Os três defeitos vivem em `skills/claude-statusline/references/statusline.sh`, todos na camada de
apresentação, nenhum tocando a contabilidade de tokens que a change anterior reescreveu.

## Goals / Non-Goals

**Goals**
- `human()` nunca emite um rótulo fora da própria faixa.
- O render volta a ser função pura do payload, sem perder a animação.
- A fração de relógio gasta em API aparece, sem estourar 80 colunas.

**Non-Goals**
- Não tocar no bloco de tokens nem no cursor do transcript.
- Não mudar paleta, ícones ou a ordem dos segmentos.
- Não adicionar dependência.

## Decisions

### D1 — `human()` trunca no ramo `k`

`%.0f` arredonda; `int(n/1000)` trunca. `999999 -> 999k`, e o ramo `M` continua com `%.1f`, que em
1.000.000 dá `1.0M`. O ramo `M` não precisa do mesmo tratamento: seu teto é aberto, então arredondar
nunca o tira da faixa.

Alternativa considerada e rejeitada: promover para `M` quando o arredondamento alcançar 1000
(`999999 -> 1.0M`). Rejeitada porque mostra `1.0M` para um número que ainda não chegou a 1M — troca
um rótulo impossível por um rótulo falso.

### D2 — O frame do shimmer vem de `cost.total_duration_ms`

`cost.total_duration_ms` é o relógio de parede desde o início da sessão, e o host o avança a cada
render. `frame = (total_duration_ms / 1000) % 3` dá o mesmo passo de 1 fps que `date +%s` dava, com
duas diferenças: o valor vem do payload, então dois renders do mesmo payload são idênticos; e a
animação passa a acompanhar o tempo da **sessão**, não o do processo.

Alternativas consideradas e rejeitadas:
- **Manter o relógio e declarar a não-determinância**, com uma variável de ambiente que a desliga
  para testes. Rejeitada: adiciona configuração para contornar um defeito que a fonte certa
  elimina de graça.
- **Remover o shimmer.** Rejeitada: o efeito é intencional, documentado, e não é ele o problema —
  é a fonte do frame.

### D3 — A fração de API é um quarto medidor na linha 3, não um sufixo na linha 1

A intenção original era `⏱️ 55m 48s (55% API)`, um segmento só. **A medição derrubou isso antes da
implementação sair do branch**: a linha 1 do `master` já ocupa **79 colunas** com um payload
comum (`Opus 5 (1M context)`, effort `max`, thinking ligado, duração e custo). Qualquer coisa
acrescentada ali estoura 80 — a forma com sufixo mediu 89, e com um nome de modelo mais longo, 97.

A linha 1 não tem folga. A linha 3, que é a linha dos medidores, tem: 58 colunas com os três
medidores atuais. Um quarto medidor no mesmo formato dos vizinhos (ícone, rótulo, barra de 8, valor)
leva a linha a **80 colunas exatas** em valores típicos.

E a fração de API **é** um medidor: uma porcentagem com barra, exatamente como `ctx`, `5h` e `7d`.
Colocá-la na linha 1 sempre foi o encaixe pior; a medição só tornou isso obrigatório de enxergar.

Alternativas consideradas e rejeitadas:
- **Sufixo na linha 1** — 89 colunas típicas, 97 no pior caso. Rejeitada pela medição acima.
- **Duas durações** (`⏱️ 55m 48s · 🌐 30m 40s`) — mais larga ainda, na linha que já não cabe.
- **Não mostrar** e registrar a decisão — era saída legítima do item #218, e teria sido a resposta
  se a linha 3 também não coubesse.

A fração só é calculada quando `total_api_duration_ms` está presente e `total_duration_ms` é
positivo — o campo é opcional e uma divisão por zero num status line é um render quebrado. O valor é
limitado a 100 para o caso de os dois relógios discordarem.

## Canonical Home & Cross-Links (MANDATORY)

| Cross-cutting rule | Canonical home | Action |
|---|---|---|
| Procedência de uma grandeza exibida e o dever de ler o que o host publica | `openspec/specs/skills-catalog` § *A shipped script reads the quantity its host publishes* | **already canonical** — D3 é uma aplicação dela: a fração é derivada de dois campos do host, nenhum inventado |
| Determinância do render de um artefato publicado | esta change, § delta | **move** — a regra não tinha casa; passa a ser requisito de `skills-catalog`, e o `SKILL.md` da skill deixa de descrever o shimmer como dependente do relógio |
| Quanto código uma mudança deixa para trás | skill `lean-code` | **link** — D2 troca a fonte de um valor em vez de adicionar uma chave de configuração |
| Idioma de identificadores vs. prosa | skill `code-locale` | **already canonical** — nenhum identificador novo em português |
| Onde um script publicado persiste estado | `openspec/specs/skills-catalog` § *Shipped scripts state what they persist* | **already canonical** — esta change não persiste nada novo |

## Risks / Trade-offs

- **`human()` passa a mostrar `999k` onde mostrava `1000k`** → é a correção, não um efeito colateral.
- **A animação passa a depender de o host avançar `total_duration_ms`** → se o campo congelar, o
  shimmer congela junto. É preferível a um render que muda sozinho: um efeito parado é visível, uma
  saída não determinística é invisível até quebrar um teste.
- **Largura** → medida com render real, não estimada. Linha 1 fica em 79 colunas (inalterada), linha
  3 vai de 58 para 80. Com os quatro medidores em 100% a linha 3 chega a 83, três colunas acima do
  alvo — estado raro (exige contexto, ambos os limites de taxa e a fração de API todos saturados) e
  registrado em vez de escondido. A linha 2 já ocupava 112 colunas antes desta change, o que diz que
  o alvo de 80 nunca valeu para ela.

## Migration Plan

Nenhuma. Três mudanças de apresentação, sem estado, sem formato persistido. Rollback é reverter o
commit.

## Open Questions

1. Não foi determinado se `cost.total_duration_ms` avança durante um render ocioso com
   `refreshInterval: 1` e nenhuma atividade de API. Se não avançar, o shimmer para enquanto a sessão
   está ociosa — comportamento aceitável e possivelmente desejável, mas não medido. A simulação
   registra o que foi observado.
2. Não foi determinado se `total_api_duration_ms` inclui o tempo de chamadas de subagente. Se
   incluir, a fração pode passar de 100% numa sessão com muito paralelismo — daí o limite explícito
   em 100. O limite é uma proteção, não uma medição: nenhum payload observado chegou perto.
