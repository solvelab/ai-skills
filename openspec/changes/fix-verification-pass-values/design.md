## Context

O requisito *A prescribed verification states what passes* entrou em `2026-09-06-update-documentation-prerequisites`
pago por um defeito de campo. A change de origem declarou, na `D3`, que ele entra **sem validador**,
porque separar critério de descrição de forma sobre prosa é julgamento que um detector erra nos dois
sentidos — medido: 3 falsos positivos em 4 marcações.

Este change é a primeira aplicação do requisito ao próprio catálogo, e a varredura que ele exigia.

## Goals / Non-Goals

**Goals**

- Fechar as duas violações que a varredura confirmou.
- Que a saída prometida pelo `claude-statusline` seja **medida**, não plausível.
- Que o requisito aprenda o que a varredura ensinou: exemplo é prescrição.

**Non-Goals**

- Não reabrir a decisão do validador. A `D3` mediu e decidiu.
- Não julgar as 67 linhas de prosa uma a uma — a amostra está declarada.
- Não reescrever a seção `## Verify` além das duas frases.

## Decisions

**D1 — A saída entra medida, e a medição é registrada.** Escrever "a saída deve ser mais ou menos
assim" repetiria o defeito num nível acima: uma promessa que o leitor também não consegue conferir. A
saída vem de rodar `skills/claude-statusline/references/statusline.sh` com o JSON que o próprio
documento já traz, e o comando fica no grupo de evidência.

**D2 — "Cleanly" vira segmentos nomeados.** O caso vazio foi medido: a linha de tokens
(`📝 … ↑ In … ♻️ … ↓ Out …`) desaparece inteira, o segmento de rate limit sai da linha do contexto, a
duração some do cabeçalho, e `thinking` inverte. Isso se olha; "cleanly" não.

**D3 — O delta é MODIFIED, não ADDED.** O requisito já existe e está certo; o que faltava era dizer
que ele vale dentro de **exemplo**, e que ausência não é valor. Criar requisito novo para isso daria
duas casas para uma regra só, contra *Single canonical home per rule*.

**D4 — A cobertura parcial entra escrita, com os números.** Nove linhas de saída esperada julgadas
uma a uma; 67 linhas de prosa em 17 skills, das quais 2 skills amostradas. O cenário *Partial coverage
is declared, not implied* pede exatamente isso, e um número honesto de piso vale mais que um censo
alegado.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Verificação prescrita diz o que aprova | `openspec/specs/skills-authoring` | already canonical — o requisito ganha um cenário, não muda de casa |
| Como um guia de instalação escreve saída esperada | `documentation/references/templates.md` | already canonical — só o exemplo é corrigido, a regra fica |
| O conteúdo da seção `## Verify` de uma status line | `claude-statusline` | already canonical |
| Medir antes de afirmar, e relatar o que não deu para medir | `verify-before-claiming` | link (already canonical) — não repetir a escada aqui |

## Risks / Trade-offs

- [A saída medida envelhece quando o script mudar] → é o mesmo contrato de qualquer exemplo do
  catálogo, e o requisito *Prescribed numbers carry the rule that produces them* já obriga a nomear o
  comando que a produz — quem mexer no script tem como remedir em uma linha.
- [A saída colada carregar dado da máquina] → o JSON de entrada é o do próprio documento, sem caminho
  real além de `/tmp`; `scan-secrets.py` roda no CI como rede de baixo.
- [A varredura amostrada esconder um terceiro caso] → aceito e declarado com número; o custo de
  julgar 67 linhas de prosa agora é maior que o de abrir item quando um terceiro aparecer.

## Open Questions

- Nenhuma.
