# Design — skill tdd

## Context

`research/tdd/` (#182) mediu uma doutrina de ordem de teste e devolveu duas coisas que este item tem
de honrar ao mesmo tempo: um efeito de comportamento total e sem sobreposição entre os arms, e um
veredito **NO-CLAIM** que proíbe publicar qualquer número. A skill nasce, portanto, pela disciplina
— e muda o desenho: sem número, o que sustenta a skill é a clareza da regra e a exatidão das
fronteiras com as skills vizinhas.

O mapa canônico de `openspec/specs/skills-authoring/spec.md:11-21` já atribui *adversarial
methodology* a `bug-hunter` e o volume de código, incluindo *the one runnable check*, a `lean-code`.
Nenhuma entrada cobre **quando** o teste é escrito. É essa a lacuna, e é estreita de propósito.

## Goals / Non-Goals

**Goals:**

- Uma casa canônica para a ordem do teste, que não repita nem contradiga `bug-hunter` nem `lean-code`.
- Uma skill que não carregue número, e que diga onde a medição vive e o que ela não estabeleceu.
- Cross-links recíprocos que deixem a fronteira temporal explícita: `tdd` antes da mudança,
  `lean-code` no piso, `bug-hunter` depois.
- Um track pytest concreto, porque doutrina sem mecânica vira slogan.

**Non-Goals:**

- Inverter a ordem default de `skills/execute-backlog/SKILL.md`.
- Tracks para outros stacks.
- Qualquer número — de `order`, `red`, custo, células ou taxa.
- Reabrir a medição de #182.

## Decisions

**D1 — A skill é opt-in e o fluxo publicado não muda.**
`execute-backlog` continua com passo 7 Implement, passo 8 Tests. O passo 8 ganha **uma linha** que
aponta `tdd` para quem roda o ciclo. Inverter o default seria mudar o comportamento de todo item de
backlog com base numa medição que não mostrou ganho de correção — exatamente o que o veredito não
autoriza. O requisito de `skills-catalog` fixa isso, para que uma revisão futura não leia a skill
como mandato.

**D2 — O núcleo é `research/tdd/arms-block.md`, e a skill é superconjunto verificado.**
O que foi medido são aquelas linhas, não a `SKILL.md`. A skill pode acrescentar frontmatter,
triggers, o track e a seção de quando o ciclo não se aplica; não pode dizer nada que contradiga o
bloco. A conferência é linha a linha e está no `tasks.md`, não no julgamento de quem escreve.

**D3 — Nenhum número, e a ausência é declarada.**
A linha NO-CLAIM do protocolo é literal: *no number appears in any README or SKILL.md*. Vale para
`order` e `red`, que foram os números bons. A skill nomeia `research/tdd/` como o registro e diz o
que ele estabeleceu (a disciplina muda o comportamento) e o que não estabeleceu (ganho de correção,
por falta de folga no baseline). O `Verified against` diz isso explicitamente, para que a ausência
de número se leia como decisão e não como esquecimento. O critério de aceite é um `grep`, não uma
impressão.

**D4 — A fronteira com `bug-hunter` é temporal, não de método.**
`tdd` governa o que se escreve **antes**; `bug-hunter` o que se faz **depois**. Sem essa linha, as
duas descrições colidiriam no gatilho "adversarial test" e o gate Q.3 cobraria. Cada uma nomeia a
outra na `description`, e o requisito de `skills-authoring` ganha o cenário desse par.

**D5 — O piso de uma checagem continua de `lean-code`.**
`tdd` não redefine quanto teste existe; diz quando o teste é escrito. A seção *quando o ciclo não se
aplica* linka o piso em vez de repeti-lo, e diz que TDD não é licença para suíte inflada — que é
onde as duas doutrinas poderiam brigar.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Ordem do teste: o teste falhando antes do código, o que o torna legítimo, quando o ciclo não se aplica | `tdd` (esta change) | **move** — o mapa canônico de `skills-authoring` ganha a entrada |
| Metodologia adversarial, quebrar o que já foi escrito | `bug-hunter` | link — `tdd` nomeia a fronteira temporal e não repete o método |
| Piso de uma checagem executável atrás de lógica não trivial; volume de código | `lean-code` | link — `tdd` linka o piso e não o redefine |
| Ordem dos passos na execução de um item de backlog | `execute-backlog` | link — o passo 8 ganha uma linha opt-in; a ordem default fica |
| Stack de teste em Python (fixtures, markers, golden, fuzz) | `python-rest-api` | link — o track pytest de `tdd` aponta a mecânica de lá em vez de repetir |
| Checklist negativo de REST | `api-resilience-testing` | link — `Do NOT use for` na description |
| Claim publicado carrega backing re-executável; método e alcance | `skills-catalog` | already canonical — esta change **usa** a regra, sob NO-CLAIM |
| Método de medição de ganho de comportamento | `research/tdd/protocol.md` e `research/lean-code/protocol.md` | already canonical — não são skills, não são publicados |
| Não afirmar o que não foi probado | `verify-before-claiming` | link — o grupo Evidence cita, não restata |

## Risks / Trade-offs

- **A skill ser lida como mandato e inverter o rito na prática.** Mitigado por D1, pelo requisito de
  `skills-catalog` e pela redação do passo 8.
- **Colisão de triggers com `bug-hunter`.** Mitigado por D4 e cobrado pelo gate Q.3.
- **Um número escapar para a `SKILL.md` ou o README.** Mitigado por D3 e por um critério de aceite
  que é um comando, não uma leitura.
- **A skill crescer além do que foi medido.** Mitigado por D2: o bloco é o núcleo, a conferência é
  linha a linha.
- **Uma medição futura contradizer a skill.** É o desenho: `research/tdd/results.md` já nomeia o
  follow-up (tarefas com folga em `green`), e a skill não afirma ganho que precise ser defendido.
