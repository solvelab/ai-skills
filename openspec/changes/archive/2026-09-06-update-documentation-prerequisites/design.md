## Context

A `documentation` foi endurecida em `2026-08-06-harden-documentation-skill` por medição, não por
revisão, e a decisão `D3` daquele change escolheu a checabilidade como regra central: o braço revisado
escreveu 131 afirmações checáveis contra 84 do controle. A `D7` mandou os esqueletos para
`references/`, porque são lidos na hora de gerar e não na hora de escolher.

Este change ataca o que aquela medição não cobriu: o **bloco de pré-requisitos** de um guia de
instalação. A evidência de campo é `solvelab/feldt`, documentado com esta skill e com duas guardas de
documentação em CI — ou seja, um caso onde a skill foi seguida e o buraco ficou mesmo assim.

## Goals / Non-Goals

**Goals**

- Que a regra de colher fatos alcance a superfície de implantação, e não pare na porta do compose.
- Que pré-requisito sondável carregue o valor que aprova, não só o comando.
- Que o destino de saída seja categoria de primeira classe.
- Que o catálogo ganhe o requisito autoral que o caso ensinou, sem duplicar doutrina.

**Non-Goals**

- Não prescrever números de hardware na skill. O requisito *Prescribed numbers carry the rule that
  produces them* pede a regra, e a regra aqui é "leia do manifesto do projeto documentado".
- Não escrever validador para o requisito novo. Ver `D3` abaixo.
- Não consertar o feldt neste change. Ele é a prova, e a prova não se edita.
- Não adotar o esqueleto do Good Docs como layout de arquivo — a `D2` do change de endurecimento já
  decidiu que o `README`/`SETUP`/`TECHNICAL` fica.

## Decisions

**D1 — A superfície de implantação entra na lista de fontes, não numa regra nova.** A linha
*Extract the facts* já enumera fonte por tipo de fato, e a porta do compose já está lá. Recursos,
armazenamento, identidade e modo de filesystem são o mesmo tipo de fato lido do mesmo tipo de
arquivo; separá-los numa regra própria criaria duas casas para uma doutrina só, contra o requisito
*Single canonical home per rule*.

**D2 — O valor que aprova é regra do `SKILL.md`, a lista de categorias é esqueleto do
`references/`.** Pela `D7` do change de endurecimento: o que decide *se* e *por quê* fica na
política, o que decide *o formato* fica no esqueleto. A lista de dez categorias é formato.

**D3 — O requisito autoral novo entra sem validador, e isso é declarado.** Detectar "verificação sem
critério de aprovação" exigiria decidir, sobre prosa, se um trecho de saída esperada é um critério.
`# Esperado: um bloco JSON` e `# Esperado: v1.29 ou maior` têm a mesma forma e significados opostos.
Um detector aqui produziria falso positivo, e o cenário *Partial coverage is declared, not implied*
do `skills-authoring` manda declarar a condição e o que escapa dela em vez de presumir conformidade.
A revisão é humana, e está escrito.

**D4 — Egress é categoria própria, e não um subcaso de "rede".** Nenhuma das cinco fontes externas
consultadas nomeia egress como pré-requisito: K3s, Grafana, Good Docs, Elastic ECK e Portainer
documentam entrada, armazenamento, permissões e versões. A categoria é contribuição própria, paga por
um defeito medido, e por isso entra com o defeito escrito ao lado — a doutrina deste repositório não
aceita linha sem evidência.

**D5 — A tabela de diagnóstico entra como forma prescrita.** O contra-modelo veio do próprio feldt:
`deploy/standalone/README.md` §1 mede alcançabilidade e separa `qualquer HTTP`, `http=000` lento
(firewall filtrando em silêncio) e `http=000` instantâneo (RST) — três leituras do mesmo comando com
**remédios opostos**. Uma linha de "esperado" não consegue dizer isso; uma tabela consegue.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| De onde se lê cada tipo de fato ao documentar | `documentation` | already canonical — a lista de fontes ganha a superfície de implantação |
| O que um bloco de pré-requisitos precisa cobrir | `documentation/references/templates.md` | establish here (new) — esqueleto, pela `D7` |
| Pré-requisito carrega o valor que aprova | `documentation` | establish here (new) |
| Egress como pré-requisito documentado | `documentation` | establish here (new) |
| Como pesquisar um fato antes de afirmá-lo, e o relatório quando não se acha | `verify-before-claiming` | link (already canonical) — não repetir a escada aqui |
| O que o serviço faz em runtime quando a dependência está fora | `backend-resilience` | link (already canonical) — este change documenta o pré-requisito, não o comportamento |
| Verificação prescrita diz o que aprova | `openspec/specs/skills-authoring` | spec delta, não conteúdo de skill |

## Risks / Trade-offs

- [A lista de dez categorias vira formulário que alguém preenche com "N/A"] → cada categoria entra com
  a fonte externa que a pede, e o esqueleto diz que categoria que não se aplica sai da lista em vez de
  virar linha vazia — a mesma regra que a skill já aplica à tabela de decisão de documentos.
- [O requisito autoral nasce sem enforcement e vira letra morta] → aceito e declarado na `D3`, com a
  razão medida. A alternativa era um detector com falso positivo, que este repositório já mediu ser
  pior: teste que reprova sem defeito é desligado.
- [A `documentation` incha e perde a densidade que o `harden-documentation-skill` conquistou] → o
  `SKILL.md` recebe três regras curtas; a lista vai para `references/`, que é onde o esqueleto mora e
  onde o custo é lido só na hora de gerar.
- [O egress é específico demais e não generaliza para software sem rede] → o esqueleto marca a
  categoria como condicional ("quando o produto chama algo de fora"), na mesma forma condicional que
  a tabela de decisão de documentos já usa.

## Open Questions

- Se a varredura registrada em E.4 achar outras skills prescrevendo verificação sem critério, elas
  entram uma a uma ou numa varredura só? A `D1` do change de endurecimento preferiu a decisão por
  caso; a resposta fica para o item que a varredura abrir.
