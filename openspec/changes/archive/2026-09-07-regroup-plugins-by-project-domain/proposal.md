# Change: Agrupar plugins por domínio de projeto

## Why

O grupo de plugin é derivado de `metadata.category` (`generate.sh:57-62`), e a categoria descreve o
**assunto da skill**. Quem instala, instala por **domínio de projeto**. Enquanto skill era diretório
solto a diferença era absorvida por `skillOverrides`; como plugin, não é: a documentação do Claude
Code diz que *"Plugin skills are not affected by `skillOverrides` — manage those through `/plugin`
instead"*, e `claude plugin disable` opera no plugin inteiro.

Medido em 2026-09-07, configurando um workspace real de 31 repositórios:

- **30 repositórios habilitam `ai-skills-devops`** e nenhum tem qualquer coisa de Assetto Corsa. São
  APIs FastAPI, web managers React, workers de ML e um bot de Kubernetes. Todos precisam de
  `helm-migration` e `k8s-tune-resources` de verdade — têm `helm/` e `k8s/` — e nenhum consegue
  recusar `assettoserver-ops`.
- **2 repositórios habilitam `ai-skills-game`** por causa das 10 skills de R3F e recebem junto
  `assettoserver-plugin` e `assettoserver-csp-lua`.
- Quem trabalha em AssettoServer quer três skills que hoje moram em **dois grupos diferentes**, e
  instalar os dois arrasta 10 skills de R3F e 2 de Kubernetes: **~1.950 tok** always-on sem como
  desligar.

O `README.md` já diz *"dumping all 38 skills into every project is noise, not help"*. A mesma frase
vale dentro de um grupo que mistura dois domínios.

## What Changes

- **Regra escrita**: o grupo é o domínio de projeto que o instala. Duas skills compartilham grupo
  somente se um projeto que quer uma quer a outra.
- Grupo novo **`assettoserver`**: `assettoserver-ops`, `assettoserver-plugin`, `assettoserver-csp-lua`.
- **`game` fica com as 10 skills `r3f-*`** e mantém o nome. Renomeá-lo para `r3f` descreveria melhor
  o conteúdo e foi **recusado**: o nome é o que quebra config, e precisão de nome não paga o custo de
  fazer todo `enabledPlugins` existente parar de casar em silêncio.
- **`devops` fica com** `helm-migration` e `k8s-tune-resources`.
- O conjunto controlado de `metadata.category` ganha `assettoserver`, atualizado em
  `.github/workflows/ci.yml` **e** em `openspec/specs/skills-authoring` na mesma change, como o
  cenário *The documented set matches the enforced set* exige.
- `GROUP_THEME` de `generate.sh` ganha o tema de `assettoserver`; os de `game` e `devops` perdem a
  menção ao domínio que saiu.
- `.claude-plugin/marketplace.json` ganha a entrada nova; `README.md` (tabela de plugins e a nota do
  bloco r3f) e o `CHANGELOG` de migração.

**BREAKING em conteúdo, não em nome**: nenhum plugin deixa de existir e nenhum `enabledPlugins` para
de casar. Mas quem instalou `ai-skills-game` pelas skills de AssettoServer, ou `ai-skills-devops` por
`assettoserver-ops`, deixa de recebê-las — silenciosamente, se ninguém disser. Por isso o commit
carrega rodapé `BREAKING CHANGE` e a tabela de migração vai no README e no CHANGELOG.

**Não muda**: nenhuma skill é criada, removida ou reescrita; `workflow`, `testing`, `tooling`,
`backend`, `fivem`, `nui`, `frontend` e `docs` ficam intactos; os agentes não se movem.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `skills-catalog`: ADDED *Plugin groups are project domains, not skill subjects* — a regra de
  agrupamento, o que ela proíbe (um grupo que obriga o consumidor a carregar domínio que ele não
  instalou), o que fazer quando uma skill serve dois domínios, e a exigência de declarar a migração
  quando um grupo publicado é renomeado ou dividido.
- `skills-authoring`: MODIFIED *Uniform frontmatter metadata* — o conjunto controlado de
  `metadata.category` passa a listar `r3f` e `assettoserver` no lugar de `game`.

## Impact

- Plugins publicados vão de 10 para 11: `ai-skills-assettoserver` nasce, nenhum some.
- **Três** skills mudam `metadata.category` e sobem `metadata.version`
  (`scripts/validate-skill-version.py`): `assettoserver-ops` (de `devops`), `assettoserver-plugin` e
  `assettoserver-csp-lua` (de `game`). As 10 `r3f-*` não são tocadas.
- `plugins/assettoserver/` passa a existir; `plugins/game/` e `plugins/devops/` encolhem.
- Release **major**: o commit carrega rodapé `BREAKING CHANGE`.
