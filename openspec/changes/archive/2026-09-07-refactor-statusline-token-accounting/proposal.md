# Change: A contabilidade de tokens do status line passa a ler o razão do host

## Why

O `statusline.sh` reconstrói o custo da sessão amostrando `context_window.current_usage` a cada
render (no máximo 1×/s) e multiplicando o resultado por uma tabela de preços hardcoded. O Claude
Code já mantém essa contabilidade exata, por modelo, no transcript da própria sessão — e é dela que
sai o `💰` mostrado três colunas ao lado.

Medido em 2026-09-07 contra o `modelUsage` do transcript, na sessão `0dd79f69` (um modelo,
901 chamadas): cache write **+11.5%**, cache read **+2.0%**, input fresco **−92.7%**, output
**−54.5%**, custo total **−7.6%**. Na sessão `c972f399` (quatro modelos): custo total **−35.4%**.

O sintoma que o usuário relata cai exatamente disso: `↑ In` é dominado por cache read e cache
write, os dois superestimados, enquanto `💰` continua correto — então a parcela passa o total, e a
tela se contradiz.

## What Changes

- **BREAKING (comportamento do script, não da API):** o segmento de tokens deixa de acumular
  `context_window.current_usage`. As contagens passam a vir das linhas `message.usage` do transcript
  apontado por `transcript_path`, deduplicadas por `requestId` — uma linha por chamada de API, sem
  amostragem.
- **O custo por segmento passa a ser um rateio de `cost.total_cost_usd`**, não um cálculo
  independente: as taxas decidem só a proporção entre entrada e saída, o valor absoluto é do host, e
  `↑ In $ + ↓ Out $ ≡ 💰` por construção. Os valores rateados aparecem marcados como derivados.
- Removidos: o acumulador (~70 linhas), o diretório de estado `~/.claude/statusline-usage/` e a
  poda `find -mtime +30 -delete` que o mantinha.
- `references/fields.md` deixa de instruir a acumulação no script e passa a documentar
  `transcript_path` + `modelUsage` como a fonte, com o motivo medido.
- Nova requisição de catálogo: um script publicado lê a grandeza que o host publica em vez de
  reconstruí-la por amostragem, e as partes de um todo publicado pelo host são um rateio dele — não
  um cálculo independente que pode ultrapassá-lo.

## Capabilities

- **New Capabilities**: nenhuma.
- **Modified Capabilities**: `skills-catalog` — uma requisição ADDED sobre a procedência de
  grandezas exibidas por scripts publicados.

## Impact

- `skills/claude-statusline/references/statusline.sh` — troca da fonte, remoção do acumulador,
  rateio do total do host
- `skills/claude-statusline/references/fields.md` — a nota de acumulação e o campo `transcript_path`
- `skills/claude-statusline/SKILL.md` — bloco `Verified against` e a descrição do que o script faz
- espelhos gerados por `./generate.sh`: `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/tooling/`
- `openspec/specs/skills-catalog/spec.md` — via delta
- Usuários que já tenham `~/.claude/statusline-usage/` ficam com um diretório órfão; a migração é
  documentada, não automática (o script não apaga estado que não escreve mais).
