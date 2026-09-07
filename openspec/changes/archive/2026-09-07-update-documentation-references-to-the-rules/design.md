# Design — a documentation cumpre as próprias regras

## Context

A #184 entregou a régua e o detector. Este item é o consumidor da régua se acertando. O detector é
autoridade: ele apaga as cercas antes de rodar as regras (`scan()` chama `strip_fences`), então os
`##` dentro dos blocos ```` ```markdown ```` dos exemplos não contam. As seções reais são onze em
`SKILL.md`, três em `examples.md` e cinco em `templates.md` — não as 21 e 25 que uma leitura sem o
`strip_fences` sugere.

## Goals / Non-Goals

**Goals:**

- `check-doc-structure.py skills/documentation/` sai com `findings: 0`.
- Nada de prosa se perde: o que sai de uma célula tem para onde ir.
- Os índices continuam corretos depois de qualquer edição, porque as âncoras vêm do detector.

**Non-Goals:**

- Mexer nas sete regras ou no detector.
- Corrigir qualquer outra skill do catálogo.
- Reduzir o número de achados por exclusão (`--exclude`) em vez de correção.

## Decisions

**D1 — Índice com âncoras geradas, nunca escritas à mão.**
`anchor_of()` do detector é a única fonte: ele tira crases, resolve links, remove tudo que não é
palavra/espaço/hífen e troca espaço por hífen. `AGENTS.md — the repo's instructions for coding
agents` vira `#agentsmd--the-repos-instructions-for-coding-agents`, com hífen duplo porque o
travessão some e os dois espaços ficam. Escrever isso à mão é como o índice apodrece.

**D2 — A célula longa de `SKILL.md:56` encolhe e o conteúdo desce.**
A célula lista quatro nomes de arquivo de instrução de agente. A condição vira uma frase curta e os
quatro nomes passam a viver na seção `## AGENTS.md`, que já existe e é onde um leitor os procura.
Encurtar apagando os nomes seria cumprir R2 destruindo o conteúdo, que é o que FR2 proíbe.

**D3 — A tabela de pré-requisitos perde a coluna de fontes.**
As três células longas de `templates.md` estão todas na coluna *Documented as a prerequisite by*,
que carrega citação com URL. A tabela fica `Category | Covers` — que é o que o leitor consulta ao
escrever um SETUP — e as fontes viram uma lista logo abaixo, uma linha por categoria. Resolve os
três achados de uma vez, e a tabela volta a caber na tela.

**D4 — O delta existe porque o strict o exige, e diz algo verdadeiro.**
Probado: `openspec validate --strict` recusa uma change sem delta
(`Ensure change has deltas in specs/`). O item deixava a pergunta aberta; a resposta é que um change
só de tarefas não valida neste schema. O requisito acrescentado é a lição deste item e não uma
formalidade: uma regra publicada com detector vale primeiro para quem a publicou.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| As sete regras de organização e o detector que as mede | `documentation` (`references/information-architecture.md`) | already canonical — este item as aplica, não as reescreve |
| Uma regra publicada com detector vale para quem a publicou | `skills-authoring` (ADDED aqui) | move — o requisito passa a existir na spec |
| Prosa em documentação: uma página, um propósito | `documentation` | already canonical |
| Não afirmar o que não foi probado | `verify-before-claiming` | link — o grupo Evidence cita, não restata |
| Simulação pelo caminho real antes de considerar entregue | `execute-backlog` e o grupo S do schema | already canonical |

## Risks / Trade-offs

- **Reescrever `templates.md` muda o que o modelo imita.** É o ponto do item e também o risco. O
  detector confere a forma; a continência (contagem de palavras antes e depois, mais leitura do
  diff) confere que nada sumiu.
- **Índice em arquivo de referência vira mais uma lista para apodrecer.** R1 é exatamente a regra
  que o detector cobre, então uma seção nova sem entrada no índice é acusada na próxima execução.
- **Tirar a coluna de fontes pode enfraquecer a rastreabilidade.** Mitigado por D3: a lista abaixo
  mantém cada fonte ligada à sua categoria pelo nome, e os links continuam clicáveis.
