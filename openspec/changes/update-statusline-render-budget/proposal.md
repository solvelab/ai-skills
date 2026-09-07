# Change: orçamento de render do status line

## Why

Duas metades do mesmo assunto, ambas registradas como follow-up da change
`2026-09-07-refactor-statusline-token-accounting`.

**#216 — a skill manda cachear o git e o script dela não cacheia.** O `SKILL.md` diz duas vezes
(linhas 109 e 131) que `git status` deve ser cacheado por `session_id` em repositórios grandes. O
script dispara quatro processos git por render. Medido em 2026-09-07 no `ai-skills` (1032 arquivos,
um repositório pequeno), média de 20 execuções:

| chamada | ms |
|---|---:|
| `git remote get-url origin` | 1 |
| `git symbolic-ref --short HEAD` | 1 |
| `git rev-parse --git-dir` | 1 |
| **`git status --porcelain`** | **9** |

Uma das quatro custa três quartos do total, e é a única que escala com o tamanho do repositório.

**#219 — o render frio passa do teto de 50 ms.** Entre 97 ms (4.5 MB) e 589 ms (40 MB). A medição
decompôs esse custo e mudou a resposta: o gargalo é o `jq`, não o I/O — no transcript de 40 MB,
`grep -c` custa 3 ms e `jq` com parse completo custa 336 ms. E o custo é pago **uma vez por sessão,
para sempre**: o cursor é keyed por `session_id`, e um transcript observado abrange sete dias com
`sessionId` constante, ou seja, sobrevive a todo `--resume`.

## What Changes

- `git status --porcelain` passa a ser cacheado por sessão e diretório, com validade curta. As
  outras três chamadas git ficam como estão — a 1 ms cada, cachear custaria mais do que economiza.
- **#219 é fechada como `wontfix`**, com a decomposição registrada. Trocar o `jq` por um extrator de
  regex economizaria meio segundo uma vez por sessão ao preço da correção que a change anterior
  existiu para estabelecer.

## Capabilities

- **New Capabilities**: nenhuma.
- **Modified Capabilities**: `skills-catalog` — uma requisição ADDED sobre onde um custo por render
  pode ser cortado.

## Impact

- `skills/claude-statusline/references/statusline.sh` — bloco git da linha 2
- `skills/claude-statusline/SKILL.md` — as duas recomendações passam a descrever o que o script faz;
  o estado novo é declarado
- espelhos gerados por `./generate.sh`
- `openspec/specs/skills-catalog/spec.md` — via delta
- Fecha #216; fecha #219 como `wontfix`
