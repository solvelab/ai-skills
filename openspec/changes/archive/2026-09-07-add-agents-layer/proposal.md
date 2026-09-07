# Change: Camada agents/ — fonte canônica, geração, gate e três agentes

## Why

O catálogo publica 38 skills, 10 plugins de domínio, 4 hooks e 8 validadores. Publica **zero
agentes**, e não por decisão: por omissão. Medido em `36091e7`:

- `find . -type d -name agents` fora de `.git/` -> vazio; `git log --all --name-only | grep '/agents/'`
  -> vazio. Nunca existiu em nenhum commit.
- `generate.sh:7-12` gera quatro árvores de wrapper mais `plugins/`. Nenhum alvo `agents/`.
- `README.md` define o que é uma skill e não define agente.

Desde `f6663f1` o critério de admissão existe: a skill `agent-delegation` separa onde uma regra mora
de onde um trabalho roda, e admite um subagente só quando os três testes valem todos. O que falta é o
lugar onde um agente admitido pode ser publicado — hoje ele seria um arquivo solto, invisível ao CI e
ausente dos plugins.

Enquanto isso o catálogo carrega três trabalhos que passam os três testes e rodam no loop principal,
queimando o contexto que o resto da tarefa precisa: a escada de pesquisa do `verify-before-claiming`,
a fase de análise do `bug-hunter`, e a auditoria de prosa de uma skill contra
`openspec/specs/skills-authoring/spec.md` — o que os checks C1–C13 explicitamente não sabem fazer.

## What Changes

- Cria `agents/<name>.md` na raiz como fonte canônica única, sem subdiretórios.
- Publica três agentes, cada um com a razão de admissão escrita contra os três testes de
  `agent-delegation`: `grounding-researcher`, `bug-hunter-analyst`, `skill-auditor`.
- `generate.sh` ganha o mapa `AGENT_GROUP` (agente -> grupo de plugin) com guard pré-escrita, e copia
  cada agente para `plugins/<group>/agents/`.
- A descrição publicada de cada plugin ganha um **parêntese separado** `(N agents: a, b)` ao lado do
  `(N skills: …)` já existente, e `scripts/validate-repo-hygiene.py` ganha o check irmão que o
  confere contra a árvore. Separado, e não dentro do parêntese atual, porque o `MEMBERSHIP_CLAIM` do
  H3 captura `[^)]*` e engoliria a segunda lista.
- `scripts/validate-agents.py` novo, com `scripts/selftest-validate-agents.py` que o gateia, e dois
  steps novos em `.github/workflows/ci.yml`.
- `README.md` ganha a seção *What is an agent?*, a linha `agents/` na árvore de estrutura e a
  declaração explícita de que agente é artefato **Claude-Code-only**.

**BREAKING para ninguém**: nenhuma skill muda de nome, categoria ou comportamento; a contagem
publicada `all 38` continua contando skills, e um agente nunca é uma skill do catálogo.

**Não muda**: as duas chamadas de `Explore` em `backlog` e `execute-backlog`; nenhum validador
determinístico é trocado por agente.

## Capabilities

### New Capabilities

- `agents-catalog`: composição e autoria da camada de agentes — a fonte canônica única e a lei de
  órfão, o limite Claude-Code-only e o que ele implica para as outras três árvores geradas, o
  frontmatter que todo agente carrega, a exigência de `tools` de menor privilégio e de contrato de
  saída, e a regra de que um agente publicado declara por escrito por que passa os três testes de
  `agent-delegation`.

### Modified Capabilities

- `skills-catalog`: MODIFIED *Catalog composition after the quality review* — a árvore ganha uma
  segunda classe de artefato publicado, então o requisito passa a dizer explicitamente que um agente
  **não** é uma skill do catálogo: `npx skills --list` continua achando exatamente as 38, e a
  contagem `all N` continua sendo de skills.

## Impact

- `plugins/workflow`, `plugins/testing` e `plugins/tooling` passam a publicar um agente cada; as
  outras sete não mudam.
- `scripts/validate-repo-hygiene.py` ganha um check; `.github/workflows/ci.yml` ganha dois steps.
- Codex, Cursor e Copilot **não** recebem wrapper de agente, e o README passa a dizer isso —
  a promessa multi-ferramenta é reduzida por escrito em vez de silenciosamente.
