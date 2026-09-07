# Change: a skill documentation passa a cumprir as próprias regras de organização

## Why

A #184 publicou sete regras de organização em
`skills/documentation/references/information-architecture.md` e o detector que as mede em
`skills/documentation/references/check-doc-structure.py`. Rodado contra a própria skill, o detector
reprova três dos quatro arquivos dela:

```
python3 skills/documentation/references/check-doc-structure.py skills/documentation/
-> findings: 7 in 4 file(s); rules run: R1,R2,R3,R4,R6,R7
```

R1 (índice acima de 100 linhas) em `SKILL.md` (229), `references/examples.md` (291) e
`references/templates.md` (407); R2 (célula de tabela acima de 120 caracteres) em `SKILL.md:56`
(145) e em `references/templates.md:241,243,247` (206, 172, 172). O `information-architecture.md`,
escrito pela #184, sai com `findings: 0` — a régua passa, o resto da skill não.

Uma skill que publica regra e não a cumpre não é regra: é preferência com fonte anexada. E o custo é
concreto — `templates.md` é o arquivo que o modelo **imita** ao gerar documentação, então uma célula
de 206 caracteres ali vira célula de 206 caracteres no repositório de quem consome.

## What Changes

- `skills/documentation/SKILL.md` — ganha `## Contents` cobrindo as onze seções; a célula longa de
  `:56` encolhe e a lista de nomes de arquivo desce para a seção `## AGENTS.md`, que já existe.
- `skills/documentation/references/examples.md` — ganha `## Contents` com as três seções reais.
- `skills/documentation/references/templates.md` — ganha `## Contents` com as cinco seções reais; a
  tabela de categorias de pré-requisito perde a coluna de fontes, que vira lista logo abaixo.
- `metadata.version` da `documentation` sobe.

As âncoras dos índices são geradas por `anchor_of()` do próprio detector, não escritas à mão.

**Não muda**: `information-architecture.md`, `check-doc-structure.py`, nenhuma outra skill.

## Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED *A published checkable rule holds on the skill that publishes it* — o
  requisito que este item aplica a si mesmo. Quando o catálogo publica uma regra de organização
  junto com o detector que a mede, a skill que publica ambos passa nesse detector, e a exceção é
  escrita, nunca silenciosa. Três cenários.

## Impact

- Três arquivos de `skills/documentation/` e a versão da skill; wrappers regenerados por
  `generate.sh`.
- Nenhuma regra e nenhum detector alterado: a medição da #184 continua comparável.
- O catálogo inteiro tem 241 achados em 142 arquivos (`R1` 80, `R2` 142, `R6` 19), medido em
  `bd8254b`. Este item fecha 7 deles. Os 234 restantes são item próprio, não este.
