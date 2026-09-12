## Context

A skill decide *se* um documento é merecido e nunca decide *como ele se chama*, *o que mora dentro
dele* nem *em que idioma*. As três lacunas produzem o mesmo sintoma na frota do mantenedor: 11 de 39
repositórios com dois nomes para arquitetura, `docs/TECHNICAL.md` variando de 7 a 25 seções sob o
mesmo nome, 21 relatórios transitórios misturados à documentação permanente, zero requisitos e zero
ADRs (medições em `proposal.md`).

O que já existe e é reaproveitado em vez de reescrito:

- `references/check-doc-structure.py` — o padrão de detector deste catálogo: stdlib, `Finding`,
  `--list/--rules/--exclude/--selftest`, saída 1/0/2, bloco `KNOWN LIMIT` na docstring. O novo
  detector é irmão dele, não uma segunda arquitetura.
- `references/information-architecture.md` — o formato "regra + fonte publicada + medição +
  veredito (with validator | review-only)". As regras de layout entram nesse mesmo formato.
- As quatro necessidades do Diátaxis, que a skill já usa para separar páginas. O mapa apenas fixa
  um nome por necessidade em vez de deixar o nome para o autor.

## Goals / Non-Goals

**Goals:**

- Um conceito, um nome canônico, em inglês, válido em qualquer repositório.
- Um fato, um documento dono, uma forma fixa; em qualquer outro lugar, link.
- Requisito, decisão e relatório datado com casa própria.
- Documentação legível em inglês e em português, com uma fonte só e paridade verificável.
- Layout do repositório auditável por script, com destino nomeado para cada legado.

**Non-Goals:**

- Migrar os 39 repositórios da frota (item por workspace, depois desta publicação).
- Suporte a escopo por caminho em `.code-locale` (item próprio em `code-locale`).
- Traduzir por ferramenta externa; o espelho é escrito na mesma sessão que a fonte.
- Reabrir as sete regras de página (R1-R7), que continuam como estão.
- Gerador de site (MkDocs, Docusaurus), `llms.txt`, e o slot de recurso FiveM (`KEYBINDS.md`).

## Decisions

### D1 — O mapa é fechado por conceito, e o slot não ganho é uma linha, não um arquivo

A tabela *earned* some; entra um mapa slot → canônico → condição → legados. O risco óbvio é
reintroduzir o "documento para satisfazer a tabela" que a 3.0.0 removeu (a medição que o removeu
está em `openspec/changes/archive/2026-08-06-harden-documentation-skill/proposal.md`). A saída é que
a ausência passa a ser **declarada**: o índice `## Documentation` do README lista todos os slots, e
o não ganho aparece como `not applicable: <reason>`. O detector aceita a declaração e cobra a
ausência silenciosa. Um arquivo a menos, uma linha a mais, e o leitor sabe que a ausência foi
decidida em vez de esquecida.

### D2 — Arquitetura é `ARCHITECTURE.md`, operação é `OPERATIONS.md`

`TECHNICAL.md` (19 ocorrências) perde para `ARCHITECTURE.md` (12) porque é o termo da indústria
(arc42, C4, ADR) e porque "technical" não exclui nada: tudo em documentação de software é técnico,
e um nome que não exclui é um nome que atrai conteúdo alheio — que é exatamente o que a matriz de
posse precisa impedir. Decisão do mantenedor em 2026-09-12.

Operação recebe um nome que **nenhum** dos seis legados usa. `DEPLOYMENT.md` é o mais comum (6) e
descreve metade do slot: implantar. A outra metade — o que fazer quando quebra, quanto o serviço
pede de CPU e memória, quais portas e quais destinos de saída — foi parar em `INFRASTRUCTURE.md` (4)
e `RUNBOOK.md` (2) justamente porque não cabia sob um nome que só fala de implantação. Renomear 6
arquivos compra um nome que para de rachar; manter o mais comum preserva a racha medida.

### D3 — A posse é a regra que faltava, e ela é verificável pela forma

"One term per concept" governa a palavra; nada governava o lugar. A matriz fixa o dono e a forma:

| Fato | Dono | Forma fixa |
|---|---|---|
| o que é e por quê, em uma frase | `README.md` | prosa, acima de tudo |
| quick start | `README.md` | bloco de código, 3-5 comandos |
| variáveis de ambiente | `SETUP.md` | tabela `Variable · Type · Default · Required · Description` |
| endpoints | `API.md` (ou link para a spec gerada) | tabela `Method · Path · Auth · Description` |
| portas, CPU/memória, uid, egress | `OPERATIONS.md` | tabela `Resource · Value · Source` |
| requisitos, usuários, glossário | `REQUIREMENTS.md` | `FR-n`/`NFR-n` numerados + tabela de glossário |
| componentes, fluxos, trade-offs | `ARCHITECTURE.md` | diagrama em texto + prosa |
| decisões | `adr/NNNN-<slug>.md` | MADR: Context · Decision · Consequences |
| comandos de desenvolvimento | `README.md` | tabela `Command · What it does` |
| troubleshooting | `SETUP.md` | tabela `Symptom · Cause · Fix` |
| histórico | `CHANGELOG.md` | gerado por semantic-release |

A forma fixa não é estética: ela é o que torna a posse **detectável**. O detector não entende que
uma tabela fala de variáveis de ambiente; ele reconhece a linha de cabeçalho canônica
(`| Variable | Type | Default | Required | Description |`, e a versão pt-BR dela) fora do documento
dono. Duas consequências aceitas e escritas: uma tabela de env vars com colunas improvisadas escapa
(falso negativo), e o dono continua sendo o único lugar onde a linha canônica é legítima. A exceção
única é o quick start: o README pode repetir até 5 comandos do `SETUP.md`, porque é a repetição que
o leitor quer na primeira tela.

### D4 — Inglês é a fonte; o espelho é estrutura, não frescor de tradução

`docs/en/` é a fonte, `docs/pt-BR/` o espelho, ambos escritos no mesmo commit. Inglês na fonte
porque identificadores, rotas, chaves e comandos já são inglês (`code-locale`), então a fonte é o
documento em que nada precisa ser traduzido de volta; em conflito, o inglês vence.

Paridade (L6) mede o que um script pode medir sem julgar significado: o gêmeo existe, a contagem de
`##` bate, a numeração bate, e os blocos de código são **idênticos** byte a byte depois de normalizar
o fim de linha. O que L6 deliberadamente não mede é se a tradução está atualizada em conteúdo — isso
é julgamento sobre significado, e a lição de R5/R6 neste catálogo é que gate sobre significado
reprova documento correto e é desligado na primeira semana. Frescor de tradução fica **review-only**,
com esta frase como a medição que o classificou: o único sinal mecânico disponível seria "o gêmeo
mudou no mesmo commit", que a regra de commit único já cobre, e qualquer coisa além disso exigiria
comparar sentido entre dois idiomas.

`docs/reports/` fica fora do par: relatório datado é transitório, tem um leitor conhecido e traduzir
custa sem comprar nada. `AGENTS.md` e `CHANGELOG.md` também ficam em arquivo único — o primeiro é
lido por ferramenta, o segundo é gerado.

### D5 — O detector audita o repositório, o irmão audita a página

Sete regras novas, nomeadas L1-L7 para não colidirem com R1-R7:

| Regra | O que mede | Como |
|---|---|---|
| L1 | slot canônico presente ou declarado | procura o arquivo; se ausente, procura `not applicable` na seção `## Documentation` do README |
| L2 | legado com destino | nome legado do mapa presente → reporta o canônico de destino |
| L3 | `.md` solto na raiz | qualquer `.md` na raiz fora do conjunto canônico |
| L4 | relatório datado fora de casa | nome com `YYYY-MM-DD` ou marcador transitório fora de `docs/reports/` |
| L5 | nome de arquivo em português | palavra função portuguesa no nome do arquivo ou do diretório |
| L6 | paridade en/pt-BR | gêmeo ausente, contagem/numeração de `##` diferente, blocos de código diferentes |
| L7 | posse | linha de cabeçalho canônica de uma tabela possuída fora do documento dono |

L5 **não carrega lista de palavras nenhuma**. Probado em 2026-09-12: o irmão
`skills/code-locale/references/check-identifier-locale.py` já responde exatamente essa pergunta para
um caminho — `revalidacao-hermes.md` sai como `path-pt-morphology`, um veredito — e já carrega o
protocolo de dispensa (`.identifier-locale-allow`). L5 chama esse script e levanta os vereditos dele;
a camada advisory dele (`path-en-unknown`, que é o que `COMO-SUBIR.md` produz) fica de fora, porque
reprovar toda palavra desconhecida reprovaria nome de produto — e esse caso específico já é pego por
L2, que ainda diz para onde o arquivo vai. Quando o irmão não é encontrado, L5 se reporta **NOT RUN**
em vez de limpo: uma regra que responde "sem achados" porque o motor sumiu é pior que uma regra
ausente, porque é acreditada. Uma lista embutida de reserva foi descartada por isso mesmo — ela
responderia "limpo" com metade do vocabulário.

### D6 — O que cada regra não sabe fazer entra no `KNOWN LIMIT`, não em uma allowlist

Nenhuma allowlist entra antes da medição de falso positivo na frota. A ordem é: rodar nos
repositórios reais, contar achado confirmado e achado ruim por regra, e só então decidir entre
`--exclude` (do consumidor), ajuste da regra ou rebaixar para review-only. Uma regra que reprovar
documento correto acima do que R6 reprovou (7 em 10, que foi o que a rebaixou) não publica com gate.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Quais documentos um projeto ganha, como se chamam, o que mora em cada um | `documentation` | already canonical — o mapa e a matriz nascem aqui |
| Organização e navegabilidade de uma página (índice, célula, catálogo, alerta) | `documentation` | already canonical — R1-R7 seguem onde estão |
| Idioma da prosa × idioma da camada de máquina | `code-locale` | link — a skill de documentação linka; a exceção do espelho bilíngue é declarada lá em uma linha, sem restatement da doutrina |
| Pesquisar antes de afirmar, e relatar o que não se achou | `verify-before-claiming` | link — `## See also` |
| Onde mora a racional de mudança quando o repositório roda fluxo spec-driven | `openspec` | link — `REQUIREMENTS.md` indexa `openspec/specs/`, nunca copia |
| Formato de commit que gera o changelog | `conventional-commit` | link — `## See also` |
| Quanto código uma mudança deixa para trás | `lean-code` | link — o detector é stdlib e irmão do existente, não uma segunda arquitetura |

## Risks / Trade-offs

- **Mapa fixo reintroduz o documento decorativo.** Mitigado por D1: ausência declarada em vez de
  arquivo vazio, e o detector aceita a declaração.
- **Renomear `TECHNICAL.md` quebra link de entrada.** A regra de migração exige `git mv` mais
  atualização dos links no mesmo commit; L2 nomeia o destino para que a migração não seja adivinhada.
- **Bilíngue dobra o custo de escrita.** Aceito e medido na simulação (tempo e tokens por repositório
  registrados). O veredito escrito antes: se o custo por repositório passar do teto declarado no
  protocolo, o escopo bilíngue é reescrito antes de publicar, não silenciado.
- **L7 confunde tabela legítima com tabela possuída.** Só a linha de cabeçalho canônica dispara, e a
  taxa de falso positivo é medida antes de qualquer gate.
- **L5 depende de uma lista de palavras que vive em outra skill.** Limite conhecido, declarado na
  docstring; a lista embutida é mínima e o caminho preferido é o arquivo do irmão.
- **O detector de prosa do `code-locale` aponta a árvore espelho.** Nenhum repositório da frota
  declara `.code-locale` hoje (0 de 39), então o efeito é futuro; a skill nomeia o bloqueio e o item
  que o resolve em vez de desligar o gate.
