# Design — agrupar plugins por domínio de projeto

## Context

`generate.sh:57-62` deriva o grupo de `metadata.category`, com `git` e `process` colapsando em
`workflow` e o resto sendo identidade. `plugins/<group>/skills/` sai daí, e as descrições publicadas
são derivadas da árvore e conferidas por `scripts/validate-repo-hygiene.py` (H3, e H4 desde a camada
de agentes).

O conjunto controlado de categorias é imposto em `.github/workflows/ci.yml:98` e documentado em
`openspec/specs/skills-authoring` (*Uniform frontmatter metadata*), que tem um cenário exigindo que os
dois sejam atualizados na mesma change.

O que quebrou isso não foi um erro de digitação: categoria é sobre o assunto, instalação é sobre o
domínio. A diferença só ficou visível quando o catálogo passou a ser instalado como plugin, porque
`skillOverrides` — que absorvia a diferença — não vale para skill de plugin.

## Goals / Non-Goals

**Goals:**

- Uma regra escrita que decide o grupo, para que a próxima skill caia no lugar certo por critério.
- Nenhum grupo obrigando o consumidor a carregar domínio que ele não instalou.
- A quebra declarada, com tabela de migração onde o consumidor a lê.

**Non-Goals:**

- Criar, remover ou reescrever skill.
- Mexer nos grupos que já não misturam domínio.
- Um plugin por skill. A regra tem que dizer quando **não** dividir.
- Resolver a limitação do Claude Code (não dá para desligar skill de plugin). Não é nossa para
  resolver; é a restrição sob a qual o agrupamento passa a ser projetado.

## Decisions

**D1 — A regra é "domínio de projeto", com um teste operacional.** Duas skills compartilham grupo
somente se um projeto que quer uma quer a outra. O teste não é taxonômico ("as duas são de jogo"),
é de instalação: existe repositório que instala uma e não a outra? Se existe e é comum, são grupos
diferentes. É o que separa `assettoserver-*` de `r3f-*`, e o que mantém as 10 `r3f-*` juntas.

**D2 — Corrige a categoria, não o mapa.** A alternativa era manter as categorias e escrever um mapa
explícito skill -> grupo em `generate.sh`. Recusada: criaria duas fontes de verdade sobre a mesma
coisa, e a causa é a categoria estar errada. `metadata.category` é onde a informação pertence e é
onde o CI já a valida. (A camada de agentes usa mapa em `generate.sh` por motivo oposto: o
frontmatter de agente é uma whitelist do harness e não aceita campo extra.)

**D3 — `game` mantém o nome.** Com AssettoServer fora, o grupo fica com as 10 skills de React Three Fiber, e os dois
repositórios que o instalam são web managers com three.js — `r3f` descreveria melhor. O rename foi
recusado depois de separar as duas metades do custo: **o conteúdo errado é o defeito; o nome é o que
quebra config.** Renomear faria todo `enabledPlugins` que nomeia `ai-skills-game` parar de casar em
silêncio, inclusive o de consumidores que este repositório não conhece, e a única coisa comprada
seria precisão de nome. O defeito é corrigido sem pagar isso.

**D4 — Quebra de conteúdo declarada, sem grupo-alias.** Nenhum plugin some e nenhum
`enabledPlugins` para de casar, mas quem instalou `ai-skills-game` pelas duas skills de AssettoServer
deixa de recebê-las. Isso é quebra, mesmo sem sumir nome, e é silenciosa se ninguém disser — então
carrega rodapé `BREAKING CHANGE` e tabela de migração no `README.md` e no `CHANGELOG.md`. A opção de
manter as skills antigas duplicadas em `game` por uma janela foi recusada: seriam duas cópias da
mesma skill em dois grupos, que H3 e H4 teriam de policiar, contra a lei de fonte canônica única.

**D5 — `assettoserver-ops` sai de `devops`.** Ele é o passageiro que 30 repositórios carregam sem
usar. `devops` fica com Helm e Kubernetes, que é o que aqueles 30 de fato querem.

**D6 — O gate desta mudança é a própria árvore.** Não há detector novo: `H3`/`H4` já comparam a
descrição publicada com `plugins/<g>/`, o CI já valida a categoria contra o conjunto controlado, e o
gate de sync reprova wrapper fora do commit. O que falta é a **regra escrita**, que vira requisito de
`skills-catalog` — e o critério de aceite é a lista de skills de cada grupo, medida, não opinada.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Composição do catálogo publicado e o que cada plugin publica | `skills-catalog` | already canonical — ganha o requisito da regra de agrupamento |
| Conjunto controlado de `metadata.category` | `skills-authoring` | already canonical — MODIFIED, troca `game` por `r3f` e `assettoserver` |
| Operação de servidor AssettoServer, plugin C#, script CSP Lua | `assettoserver-ops`, `assettoserver-plugin`, `assettoserver-csp-lua` | already canonical — as três só mudam de grupo, o conteúdo não é tocado |
| Convenções de React Three Fiber | as 10 skills `r3f-*` | already canonical — só mudam de grupo |
| Qual artefato uma regra vira, e quando delegar | `agent-delegation` | link — esta change não cria artefato novo: usa o gate que já existe (D6) |
| Volume de código | `lean-code` | link — a alternativa recusada em D2 e o alias recusado em D4 são as duas aplicações da escada aqui |

## Risks / Trade-offs

- **Quebrar `enabledPlugins` de quem já instalou.** É o risco central e é aceito de propósito (D4),
  com tabela de migração em dois lugares e release major. O workspace do mantenedor, com 31
  repositórios, é atualizado no mesmo movimento.
- **Multiplicar grupos até virar um plugin por skill.** Mitigado por D1: o teste é de instalação e
  exige um caso real, não uma intuição taxonômica.
- **Alguém ter instalado `ai-skills-game` pelas skills de AssettoServer e não notar que sumiram.** É
  o risco que sobra depois de D3, e é o motivo de D4 exigir o rodapé `BREAKING CHANGE` e a tabela:
  sem nome quebrado, a perda é silenciosa e só a nota de release a torna visível.
- **A categoria virar duas fontes de verdade se o mapa também mudar.** Evitado por D2: só a
  categoria muda; `group_of()` continua identidade fora de `git|process`.
