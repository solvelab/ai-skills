## Context

O check tem quatro tiers, todos de mundo aberto: `non-ascii`, `pt-verb`, `pt-noun`, `pt-morphology`.
Os três últimos consultam listas de português. O KNOWN LIMIT 2 do próprio script já declara a
consequência — qualquer substantivo fora do léxico passa.

Medições feitas em 2026-08-26 sobre os identificadores reais deste repositório (58 arquivos com
perfil de língua, 961 segmentos distintos de comprimento ≥ 4):

| Fonte | Desconhecidos | Taxa |
|---|---|---|
| hunspell `en_US.dic` (79.013 entradas) | 333 | 34,7% |
| hunspell + desflexão ingênua | 126 | 13,1% |
| `words_alpha` de domínio público (369.652) | 99 | 10,3% |

Os 99 restantes não são falha do dicionário: são vocabulário de programação (`printf`, `startswith`,
`stdin`, `argparse`, `rglob`), compostos (`selftest`, `allowlist`, `frontmatter`) e nomes próprios
(`openspec`, `solvelab`, `fivem`, `ubuntu`).

## Goals / Non-Goals

**Goals**

- Inverter a direção da falha: o que o check não reconhece é reportado, não aprovado.
- Ruído baixo o bastante para ser lido — meta declarada: menos de 2% dos segmentos deste repositório
  após a lista de programação e a regra de composto.
- Nenhuma dependência nova, nenhuma rede em tempo de execução, nenhuma chamada a modelo.

**Non-Goals**

- Tornar `en-unknown` bloqueante por padrão. Essa decisão vem depois da medição em campo, em item
  próprio.
- Corrigir a fronteira que nenhuma das duas perguntas alcança: palavra que é português **e** inglês
  (`data`, `local`, `total`). Continua declarada no KNOWN LIMIT.
- Verificar ortografia de prosa. O tier lê identificador e segmento de caminho, como os existentes.

## Decisions

**D1 — Lista de domínio público embutida, não o dicionário do sistema.**
`/usr/share/hunspell/en_US.dic` não tem `read`, `input`, `context`, `math`, `detail`, `reset`,
`decode`, `struct` — verificado entrada a entrada. Um dicionário com buracos em palavra-base
transforma `read` em achado e mata a credibilidade do tier no primeiro uso. `dwyl/english-words` é
Unlicense (domínio público, compatível com MIT), contém as oito, e embutir remove a dependência de
ambiente: o mesmo resultado no CI, na máquina do mantenedor e no hook.

**D2 — Comprimida com `gzip`, não em texto puro.**
3,7 MB × 2 espelhos = 7,4 MB no repositório; comprimida são 2,2 MB. `gzip` é stdlib, então a promessa
`compatibility` do skill continua verdadeira. `scripts/validate-repo-hygiene.py` gata apenas bytecode
Python — lido no código do gate, `BYTECODE = re.compile(r"(^|/)__pycache__/|\.py[cod]$")` — então um
`.gz` de dados não é artefato compilado para esse gate.

**D3 — Duas listas separadas, não uma.**
Inglês natural e vocabulário de programação têm proveniências diferentes: uma é domínio público
importado, a outra é curada aqui. Misturar impede auditar qualquer uma das duas. `printf` não é
inglês; é vocabulário desta profissão, e o arquivo que o carrega diz isso.

**D4 — Regra de composto antes de reportar.**
Um segmento que se divide em duas palavras conhecidas é conhecido. Medido: resolve 13 de 13
compostos reais deste repositório. Sem ela, cada composto viraria entrada manual na lista curada, e a
lista curada viraria a mesma corrida de vocabulário aberto que esta change existe para acabar.

**D5 — Advisory por padrão, gating opcional.**
O repositório já usa esse desenho: `scripts/validate-rite-evidence.py` reporta densidade sem gatar,
com o motivo escrito. Um tier de mundo fechado que reprova no primeiro dia transforma toda árvore
legada em vermelho, e um gate que reprova tudo é desligado numa semana — o mesmo argumento que fez
`--diff` ser o modo de adoção do próprio check. `--gate-unknown` existe para quem já mediu o próprio
ruído.

**D6 — Precedência: um segmento produz no máximo um achado.**
Se um tier `pt-*` disparou, o `en-unknown` não repete. Confiança alta primeiro; o advisory é o que
sobra.

## Canonical Home & Cross-Links (MANDATORY)

| Regra transversal | Skill canônico (dono) | Ação nesta change |
|---|---|---|
| Fronteira prosa/máquina e a exceção de termo de domínio | `code-locale` | já canônico — a mudança é dentro do skill dono |
| Não afirmar sem probe | `verify-before-claiming` | link: as três taxas de ruído e os buracos do hunspell foram medidos, não estimados |
| Prova de que o artefato roda | rito `Simulation & Field Proof` | o grupo entregue no #100 é preenchido por esta change com a medição de campo |
| Rito backlog → PR | `execute-backlog` | link, sem restatement |

## Risks / Trade-offs

- **Ruído tornando o tier ilegível** → advisory por padrão; meta de <2% medida antes de fechar; a
  allowlist e as duas listas são as válvulas.
- **2,2 MB a mais no repositório** → comprimido, e o número está escrito aqui para quem revisar
  decidir com ele à vista.
- **Lista de domínio público conter lixo** (`words_alpha` inclui palavras obscuras) → isso favorece o
  falso negativo, não o falso positivo: uma palavra estranha a mais no dicionário só silencia o tier.
- **Palavra portuguesa que existe em inglês** (`data`, `local`) → não é alcançada por nenhuma das duas
  perguntas; declarado no KNOWN LIMIT, sem promessa em contrário.
- **Custo de carga na escrita** (o hook roda a cada `Write`) → carga preguiçosa: a lista só é
  descomprimida quando existe segmento candidato, e uma vez por execução.

## Migration Plan

Nenhuma. O tier é advisory, então nenhum pipeline existente muda de cor. Rollback: remover a flag e
os dois arquivos de dados; os tiers `pt-*` são independentes.

## Open Questions

- Nenhuma sobre o mecanismo: dicionário, licença, tamanho, ruído e regra de composto foram medidos
  antes de escrever. Fica em aberto **o número de campo em repositórios de terceiros** — este repo é
  o único medido, e é código deliberadamente inglês, então a taxa em base legada será outra. É essa
  medição que decide se o tier gradua para gating, em item separado.
