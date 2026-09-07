# Change: três arestas de exibição do status line

## Why

O `statusline.sh` que a skill entrega carrega três defeitos de exibição, todos vistos durante a
change `2026-09-07-refactor-statusline-token-accounting` e deliberadamente adiados para não expandir
o escopo dela (box E.4).

1. **`human()` emite uma unidade que não existe.** O ramo `k` usa `%.0f`, que arredonda: entre
   999.500 e 999.999 o resultado é `1000k`, justamente onde o ramo `M` começa. Reproduzido:
   `999499 -> 999k`, `999500 -> 1000k`, `999999 -> 1000k`, `1000000 -> 1.0M`.
2. **O render não é função do seu input.** O shimmer do nível `max` deriva o frame de
   `$(date +%s)`, então dois renders do mesmo payload produzem saídas diferentes. Isso derruba a
   técnica de teste mais barata que existe para um status line — e é exatamente a que provou a
   change anterior (6/6 renders idempotentes).
3. **`cost.total_api_duration_ms` está no payload e não chega à tela.** Medido num payload real:
   `3348802` ms de relógio contra `1840177` de API — 55% da sessão foi espera de modelo, um número
   que muda como se trabalha e que hoje se perde.

## What Changes

- `human()` passa a truncar no ramo `k`, nunca arredondar para fora da própria faixa.
- O frame do shimmer passa a vir de `cost.total_duration_ms`, que o host avança a cada render: a
  animação continua a 1 fps sob `refreshInterval`, e o render volta a ser função pura do payload.
- O segmento de duração passa a mostrar a fração de relógio gasta esperando a API.
- Nova requisição de catálogo: a saída de um script publicado é função do payload que ele recebe.

## Capabilities

- **New Capabilities**: nenhuma.
- **Modified Capabilities**: `skills-catalog` — uma requisição ADDED sobre determinância do render.

## Impact

- `skills/claude-statusline/references/statusline.sh` — `human()`, `effort_render()`, extração jq e
  montagem da linha 1
- `skills/claude-statusline/SKILL.md` — descrição da linha 1 e do shimmer
- espelhos gerados por `./generate.sh`
- `openspec/specs/skills-catalog/spec.md` — via delta
- Fecha #215, #217 e #218
