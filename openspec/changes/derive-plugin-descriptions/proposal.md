# Change: Derivar as descrições dos plugins da árvore de skills

## Why

Três artefatos publicados descrevem à mão o que cada plugin do marketplace embarca, e os três já
discordam entre si e da árvore. Medido em `d2918ed` contra `plugins/*/skills/`:

| Grupo | `generate.sh:150-161` diz | `marketplace.json` diz | A árvore tem |
|---|---|---|---|
| `game` | "React Three Fiber skills (10 topics)" | "(12 topics)" (linha 45) | 12 |
| `workflow` | 5 nomes | 4 temas | 7 (faltam `backlog`, `execute-backlog`) |
| `backend` | 2 nomes | 2 temas | 4 (faltam `observability`, `log-event-collector`) |
| `frontend` | `react-api-client` | 1 tema | + `svg-animation` |
| `devops` | `helm-migration` | 1 tema | + `k8s-tune-resources`, `assettoserver-ops` |

O `.claude-plugin/plugin.json` raiz (linha 5) ainda diz "React Three Fiber (10 topics)". O
`README.md:537` intitula a tabela "Game (React Three Fiber — 10 topics)" e lista `svg-animation`
(categoria `frontend`, `skills/svg-animation/SKILL.md:18`) como primeira das 11 linhas dela; a
tabela Frontend (`README.md:504-509`) não a tem.

Nada falha quando uma skill entra num grupo: `generate.sh:190` tem o fallback
`:-Skill group ${group}`, que daria a uma categoria nova uma descrição placeholder sem aviso, e o
gate `validate-repo-hygiene.py` H2 casa só a forma `all N` (`scripts/validate-repo-hygiene.py:31`),
então "(10 topics)" nunca esteve no alcance de gate nenhum.

Por fim, `generate.sh:180` lê `VERSION` com `tr -d '[:space:]'` sem validar a forma, e
`set-version.sh:13` usa uma regex sem âncora final — `2.15.1dirtychange` passa nas duas e chega aos
10 `plugin.json` gerados.

## What Changes

- `generate.sh`: `GROUP_DESC` vira `GROUP_THEME` (só o tema, sem nomes nem contagens). A descrição
  publicada de cada plugin passa a ser `"<tema> (<N> skills: <nomes ordenados>)"`, com `N` e os
  nomes lidos de `plugins/<g>/skills/` no momento da geração. O fallback `:-Skill group` some: um
  grupo sem tema derruba o gerador com mensagem que nomeia o grupo e a skill, **antes de gravar
  qualquer arquivo** — a categoria de cada `skills/*/SKILL.md` é lida contra `GROUP_THEME` logo
  depois da guarda de `VERSION`, antes do primeiro `mkdir` e do `rm -rf plugins/`.
- `generate.sh` passa a reescrever também as `description` das entradas por plugin de
  `.claude-plugin/marketplace.json` (inclusive a do bundle `ai-skills`, que publica `all N skills`)
  e a `description` do `.claude-plugin/plugin.json` raiz, derivada do conjunto de temas. Os campos
  `version` desses dois arquivos continuam sendo escritos só por `scripts/set-version.sh`; a
  reescrita é idempotente (segunda run sem diff) e preserva o formato que o `sed` de
  `set-version.sh:18-19` casa.
- `generate.sh` valida `VERSION` com a regex ancorada
  `^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$` antes de gravar qualquer arquivo; `set-version.sh:13`
  usa a mesma regex.
- `scripts/validate-repo-hygiene.py` ganha o check `H3 plugin description membership`: em cada
  `plugins/<g>/.claude-plugin/plugin.json` e na entrada correspondente do `marketplace.json`, o
  conjunto de nomes no parêntese é igual ao conjunto de diretórios em `plugins/<g>/skills/`, e a
  contagem confere. H2 ganha um segundo padrão que reprova uma contagem nua `(N topics)` /
  `(N skills)` fora de blocos de código. Um defeito injetado por check novo no `--selftest`; o que
  cada check não cobre (o texto do tema) fica declarado dentro dele.
- `README.md`: a linha de `svg-animation` sai da tabela Game e entra na tabela Frontend; o
  cabeçalho Game deixa de dizer "10 topics" e o parágrafo nomeia o que o plugin `game` de fato
  embarca; `README.md:50-55` vira uma tabela que nomeia as skills de cada plugin, e o parágrafo
  que a introduz diz que ela é mantida à mão (só a descrição publicada vem do gerador).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `skills-catalog`:
  - ADDED *Published plugin descriptions are derived from the tree* — a lista e a contagem de skills
    de cada plugin publicado vêm da árvore na geração, sobrando à mão só o tema; um grupo sem tema
    e uma versão inválida derrubam o gerador antes de gravar.
  - MODIFIED *The repository itself is gated, not only its skills* — ganha o cenário de uma
    descrição publicada que discorda da árvore (nome sobrando, faltando, ou contagem nua) falhar o
    build, nomeando arquivo, grupo e diferença.

## Impact

- `generate.sh` — tema por grupo, derivação, guarda de `VERSION`, reescrita das descrições de
  `.claude-plugin/marketplace.json` e `.claude-plugin/plugin.json`.
- `scripts/set-version.sh:13` — regex ancorada, idêntica à do gerador.
- `scripts/validate-repo-hygiene.py` — H3, padrão de contagem nua em H2, dois defeitos no selftest.
- `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `plugins/*/.claude-plugin/plugin.json`
  — conteúdo regenerado (só `description`; `name`, `source` e `version` intocados).
- `README.md` — linhas 50-55 e as tabelas Frontend e Game.
- Nenhuma skill do catálogo muda: nenhum `SKILL.md` é tocado e a composição (35 skills, descoberta
  via `npx`) fica idêntica. O que muda para o consumidor é o texto que o `/plugin` mostra para cada
  plugin, agora com a lista completa de skills.
- Fora desta change, por decisão do orquestrador da execução: `.github/workflows/ci.yml:47`
  (a issue pedia a mesma regex lá; a cobertura fica transitiva, porque o step *Wrappers in sync*
  roda `generate.sh` antes) e `install.sh`/`update.sh` (issue própria).
