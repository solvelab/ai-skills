# Change: Definir o que uma skill instalada sozinha pode referenciar

## Why

A auditoria de 2026-09-04 (issue #117) deixou quatro achados que compartilham uma pergunta de
desenho que o spec não respondia: **o que uma skill pode referenciar quando é instalada sozinha** —
por symlink, por `npx skills add` (que copia só `skills/<nome>/`), por plugin de grupo (que copia as
skills de um grupo) ou por cópia isolada de um wrapper Cursor/Copilot. A issue #121 registrou a
decisão (regras R1–R5) e derivou os gates; esta change escreve a regra no spec e a implementa.

O que a árvore de `master` (`bfc400d`, 2026-09-05) tem hoje, medido com o validador estendido:

1. **Doze caminhos cruzados mortos** (`C12`): `bug-hunter/references/track-*.md` sem o prefixo
   `skills/` em `fivem-lua`, `openspec-drivezone`, `python-rest-api`, `assettoserver-csp-lua` (2),
   `assettoserver-plugin`; `execute-backlog/references/spec-rite.md` em
   `backlog/references/backlog-config.md`; `backlog/references/*.md` (2) em
   `execute-backlog/references/board-sync.md`; e `claude/global/hooks/locale-rite.py` (2) em
   `code-locale`, que só existe num clone. `check_refs` (C1) só julga `references/` e `skills/`,
   então nenhum deles reprovava.
2. **Seis descriptions sem cláusula de não-uso** (`C13`): `conventional-commit`, `python-rest-api`,
   `r3f-geometry`, `r3f-physics`, `r3f-postprocessing`, `svg-animation`. O cenário *Every skill
   states where it does not apply* existe no spec desde #96 e nenhum check o media.
3. **Wrappers copiados sem a árvore**: 30 de 35 `cursor/rules/*.mdc` e todo
   `copilot/instructions/*.md` apontam `references/` por `../../skills/<nome>/references/`, e o
   README (linhas 144-148) manda copiar esses arquivos isolados para o projeto.
4. **Referência órfã sem gate** (`C11`): o caso `svg-animation/references/objects/`, corrigido em
   #128, não tinha check que o impedisse de voltar. Hoje a contagem é zero; o gate existe para que
   continue zero.

Pares que competem pelo mesmo prompt, medidos na auditoria e sem redirecionamento recíproco:
`python-rest-api` ↔ `api-resilience-testing` ("review an endpoint"), `r3f-animation` → `svg-animation`
(2D/SVG), `fivem-lua` → `assettoserver-csp-lua` (CSP Lua).

## What Changes

- **Spec**: `skills-authoring` ganha o requisito *Cross-skill references resolve in every install
  form* (R1–R5 da issue, um cenário por forma de instalação) e *Authoring rules are machine-enforced*
  ganha o cenário que gata C11–C13 pelo selftest.
- **Validador** (`scripts/validate-skills.py`): três checks novos, cada um declarando o que não
  cobre — `C11 orphan reference` (todo `references/**/*.md` alcançável a partir do `SKILL.md`,
  transitivo), `C12 out-of-skill path` (raiz só-do-catálogo como `research/` e `claude/`, caminho
  `<outra-skill>/references/` sem prefixo `skills/`, caminho relativo — link ou crase — que sai de
  `skills/<x>/`; corre sobre `SKILL.md` e todo `*.md` sob `references/`, recursivamente), `C13
  anti-trigger clause` (lista literal de frases + redirecionamento a uma skill irmã nomeada). Docstring
  C1..C13. `scripts/selftest-validate-skills.py` ganha uma mutação por check.
- **Conteúdo**: cada achado C12/C13 acima é corrigido no catálogo — caminho cruzado vira
  `skills/<skill>/references/<arquivo>` mais a frase que nomeia a skill; `claude/global/hooks/…` vira
  URL do repositório; as seis descriptions ganham cláusula "Do NOT use for … (that is `<skill>`)" ou
  redirecionamento, mantendo cada frase-gatilho entre aspas e ficando ≤ 1024 caracteres (C10 já é
  gate); os três pares medidos ganham redirecionamento recíproco. Toda skill editada sobe patch.
  Exceção: os dois achados em `skills/execute-backlog/references/board-sync.md` pertencem a outro
  item em paralelo e ficam registrados como gap, não editados aqui.
- **Wrappers** (`generate.sh`): nos wrappers Cursor e Copilot os links para `references/` passam a
  ser `https://github.com/solvelab/ai-skills/blob/master/skills/<nome>/references/<arquivo>`
  (Copilot: `tree/master/…/references/`). `claude/`, `codex/` e `plugins/` não mudam.
- **README**: as notas de instalação Cursor/Copilot dizem que `references/` resolve pela URL do
  repositório; o parágrafo do validador lista treze checks.

Nenhuma skill entra, sai ou muda de nome: a composição do catálogo (35 skills) fica idêntica, então
nada aqui é **BREAKING** para consumidores do `npx skills add`. É mais restritivo para quem edita uma
skill: um caminho `<outra>/references/…`, um arquivo órfão em `references/` ou uma description sem
cláusula de não-uso passam a reprovar o CI.

## Capabilities

### New Capabilities

_Nenhuma._ Nenhum skill novo entra no catálogo.

### Modified Capabilities

- `skills-authoring`: requisito novo *Cross-skill references resolve in every install form* (forma
  canônica `skills/<skill>/references/<arquivo>` + frase nomeando a skill; caminho fora de `skills/`
  como URL; todo `references/**/*.md` alcançável; wrappers Cursor/Copilot por URL), com um cenário
  por forma de instalação. *Authoring rules are machine-enforced* ganha o cenário em que o selftest
  injeta um órfão, um caminho cruzado sem prefixo e uma description sem cláusula, e um validador mudo
  em qualquer dos três reprova.

## Impact

- `scripts/validate-skills.py` (C11, C12, C13 + docstring), `scripts/selftest-validate-skills.py`
  (três mutações; o laço passa a aceitar mutação que cria arquivo).
- `generate.sh` (sed do Cursor em ~:173 e bloco do Copilot em ~:176-185) e, por regeneração,
  `cursor/rules/*.mdc` (30 arquivos com `references/`) e `copilot/instructions/*.instructions.md`
  (30 arquivos). `claude/`, `codex/`, `plugins/` regenerados sem diff de comportamento.
- Skills editadas (todas com bump patch): `fivem-lua`, `openspec-drivezone`, `python-rest-api`,
  `assettoserver-csp-lua`, `assettoserver-plugin`, `backlog` (references), `code-locale`,
  `conventional-commit`, `r3f-geometry`, `r3f-physics`, `r3f-postprocessing`, `svg-animation`,
  `r3f-animation`, `api-resilience-testing`. Cada uma é espelhada em `plugins/<grupo>/skills/` e nos
  quatro wrappers.
- `README.md`: notas de instalação Cursor/Copilot (seção Install) e o parágrafo "runs nine checks".
- **Não** tocado: `skills/execute-backlog/**` (outro item; dois achados C12 ficam abertos e nomeados
  em `tasks.md` S.3), `skills/bug-hunter/**`, `install.sh`, `.github/workflows/ci.yml`.
