# Change: Medir o `metadata.version` por skill com um gate e uma dispensa escrita

## Why

`README.md:194` (e de novo em `:864`) promete um contrato por skill: "Each skill also carries its
own `metadata.version` … bump it when that skill's behavior changes. Repo version = the collection;
skill version = the individual contract." Nada mede a segunda metade da frase. O step *Skill
frontmatter checks* de `.github/workflows/ci.yml` verifica presença e formato semver do campo; o
requisito *Uniform frontmatter metadata* de `openspec/specs/skills-authoring/spec.md` exige o campo,
não o bump.

Medido na issue #119 (`git log` por skill, sem `chore(release)`): 20 skills cujo último commit de
conteúdo não mexeu em `metadata.version`; no histórico inteiro, 49 de 165 pares (commit, skill) com
edição de conteúdo ficaram sem bump, 42 deles vindos de 4 varreduras catálogo-inteiro. Um só commit,
`cf767ee`, tocou 13 skills e bumpou zero (a décima terceira, `code-locale`, nasceu ali). Regra
escrita e não medida é o estado que a doutrina deste repositório rejeita — a mesma assimetria que
levou o spec-rite a exigir dispensa por linha escrita com motivo (issue #117).

A decisão registrada na issue em 2026-09-05 é a **Opção A**: gate com dispensa escrita. A Opção B
(rebaixar o campo a informativo) apagaria a promessa em vez de honrá-la.

## What Changes

- `scripts/validate-skill-version.py`, novo, no molde de `scripts/validate-spec-rite.py`: mesma
  resolução de base (`GITHUB_BASE_REF`, `origin/master`, `origin/main`), mesmo leitor do corpo do PR
  (`GITHUB_EVENT_PATH`, com `PR_BODY` como override deliberado), mesmo `--selftest` com `DEFECTS` e
  `SILENT`, mesmo skip impresso em evento que não é `pull_request`. Regra: para cada `skills/<x>/`
  com qualquer caminho alterado contra a base — ignorando um diff cuja única mudança na skill é a
  linha `  version:` — o `metadata.version` do `SKILL.md` em HEAD tem de ser semver-maior que na
  base, **ou** o corpo do PR carrega uma linha `Skill-version: none — <motivo>` (motivo com o mesmo
  tamanho mínimo da dispensa do spec-rite). Skill nova (sem `SKILL.md` na base) passa. Árvores
  geradas (`claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`) nunca contam. Versão que **desce**
  é achado sempre, dispensa ou não.
- Dois steps novos em `ci.yml`, logo depois de *Spec-rite self-test*: o gate e o seu `--selftest`.
- `README.md`: as duas frases que enunciam a regra passam a dizer que o bump é medido pelo gate e
  nomeiam a linha de dispensa.
- `skills/execute-backlog/references/spec-rite.md`, seção *In the PR body*: a linha `Skill-version`
  ao lado da linha `Spec-rite`, em um parágrafo curto. `metadata.version` de `execute-backlog` sobe
  um patch, e os wrappers são regenerados.
- Delta em `skills-authoring`: requisito novo *A skill's version moves with its content*.

Não é **BREAKING** para consumidores do catálogo: nenhum skill entra, sai ou muda de nome, e nenhum
consumidor lê `metadata.version` (`generate.sh`, `install.sh`, `update.sh`, `set-version.sh` e o
`marketplace.json` usam só o `VERSION` do repositório). É mais restritivo para quem abre PR neste
repositório: editar `skills/<x>/` sem bump e sem a linha passa a reprovar.

## Capabilities

### New Capabilities

_Nenhuma._ Nenhum skill novo entra no catálogo.

### Modified Capabilities

- `skills-authoring`: ganha o requisito *A skill's version moves with its content* — a regra do
  README passa a ser medida por um gate diff-based, com dispensa escrita PR-wide, isenção para skill
  nova e para diff só em árvore gerada, e skip declarado fora de `pull_request`. *Uniform
  frontmatter metadata* não muda: ele exige o campo; o requisito novo exige o movimento.

## Impact

- `scripts/validate-skill-version.py` (novo); `.github/workflows/ci.yml` (dois steps).
- `README.md:194` e `:864`.
- `skills/execute-backlog/SKILL.md` (só `metadata.version`, 1.8.0 → 1.8.1) e
  `skills/execute-backlog/references/spec-rite.md` (um parágrafo); espelhos regenerados por
  `./generate.sh` em `claude/skills/execute-backlog/` e `plugins/workflow/skills/execute-backlog/`.
- Nenhuma outra skill é tocada; a composição do catálogo (35 skills, descoberta via `npx`) fica
  idêntica.
- Quem abre PR neste repositório: ~1 em 5 PRs de skill carrega uma linha `Skill-version: none —
  <motivo>` (custo aceito na decisão da issue); uma varredura catálogo-inteiro carrega uma linha só.
