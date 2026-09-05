# Change: Kit de adoção do code-locale por repositório — pre-commit e step de CI

## Why

A regra "a camada de máquina é inglês" só é medida onde há um harness com o `settings.json` desta
máquina: `claude/global/hooks/locale-rite.py` roda em `PostToolUse` de sessões Claude Code. Codex,
Cursor e Copilot recebem o texto da skill e nenhum gate; um commit escrito à mão não encontra nada.
A skill `code-locale` diz que o detector "pode ser wired em pre-commit e CI" (`SKILL.md:33-34`,
`references/migration.md:16`, docstring do detector, linha 10) e o único exemplo real é o step C9
do `ci.yml` **deste** repositório — que roda `scripts/validate-skills.py`, não um comando copiável.

Medido em 2026-09-05 (issue #139) nos projetos do mantenedor disponíveis nesta máquina:
`server_addons` (8 `.py`) sem workflow nem `.identifier-locale-allow` — 0 achados gating, 114
palavras `en-unknown` consultivas. O gate existe por ferramenta, não por repositório.

## What Changes

- `skills/code-locale/references/pre-commit-locale.sh`, novo: hook `pre-commit` em bash + python3.
  Localiza o detector — `$LOCALE_CHECK`, depois `$AI_SKILLS_HOME` ou `~/ai-skills`, depois download
  pinado por tag (`v2.21.0`, o `VERSION` atual) com sha256 conferido em python3 e cache em
  `$(git rev-parse --git-dir)/locale-check/` — e roda
  `git diff --cached --no-color --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ |
  PYTHONIOENCODING=utf-8:surrogateescape python3 <detector> --diff -` (a forma do diff fixada contra
  a configuração git do usuário; bash 3.2+). Sai 1 com os achados e nomeia as três
  saídas: `# locale-ok: <motivo>`, `.identifier-locale-allow`, `git commit --no-verify`. O cabeçalho
  declara instalação (`cp` para `.git/hooks/pre-commit` ou `core.hooksPath`) e o que **não** cobre.
- `skills/code-locale/references/ci-step.md`, novo: um job de GitHub Actions copiável — `checkout`
  com `fetch-depth: 0`, `curl -fsSL` do detector na tag com `sha256sum -c`, e um `run:` com
  `set -o pipefail` e `git diff <os mesmos flags> origin/${{ github.base_ref }}...HEAD | python3
  check-identifier-locale.py --diff -` — com o pin, o `fetch-depth`, o `pipefail` e o gatilho
  `pull_request` explicados.
- `skills/code-locale/SKILL.md`: seção *Wire it in one minute* apontando os dois arquivos e uma
  tabela de três camadas (hook de sessão, pre-commit, CI) dizendo o que cada uma pega e o que deixa
  passar. `metadata.version` `1.3.1 → 1.4.0`; wrappers regenerados por `./generate.sh`.

Fora de escopo, por decisão da issue: opção `--git-hooks` no `install.sh`, publicar o detector como
pacote, wiring automático nos repositórios do mantenedor.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `skills-catalog`: o requisito *Code locale has a canonical home* ganha a cláusula de que a skill
  canônica embarca o meio de adoção por repositório — um hook de pre-commit e um step de CI
  copiáveis, pinados por tag — e não só o detector, com o cenário *A repository adopts the gate
  without the assistant*.

## Impact

- Skill afetada: `code-locale` (dois arquivos novos em `references/`, uma seção no `SKILL.md`, bump
  minor). Nenhuma skill é adicionada, removida ou renomeada: a composição do catálogo (35) e a
  descoberta via `npx` não mudam.
- Wrappers gerados de `code-locale` em `claude/`, `codex/`, `cursor/`, `copilot/` e
  `plugins/workflow/` (a árvore de `plugins/` copia `references/` inteira, então os dois arquivos
  novos aparecem lá).
- Nada em `hooks/`, `README.md`, `ci.yml` ou `install.sh` muda.
