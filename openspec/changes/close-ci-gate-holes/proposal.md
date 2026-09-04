# Change: Fechar os buracos medidos nos gates do CI

## Why

A auditoria de 2026-09-04 (issue #117) reproduziu, em cópia do repositório, sete formas de um pull
request passar verde no `.github/workflows/ci.yml` sem ter feito o que o gate diz medir:

1. **Wrappers in sync** usa `git diff --exit-code`, que ignora arquivo não rastreado. Um
   `references/*.md` novo commitado gera um arquivo `??` em `plugins/` e o step passa.
2. **Spec-rite** (`scripts/validate-spec-rite.py:176`) aprova qualquer diff desde que **alguma**
   change ativa exista, mesmo sem relação; o selftest fixa isso como caso mudo (`:210`).
3. **scan-secrets** não tem `--selftest`; o filtro `PLACEHOLDER` é aplicado aos 40 caracteres
   anteriores ao token (`:59-60`), então `test_token = ghp_…` e `<ghp_…>` ficam mudos; não cobre
   `github_pat_` nem `sk-`.
4. **Frontmatter greps** varrem o arquivo inteiro: `name:` dentro de um bloco ```yaml satisfaz o check.
5. **Permissões e pins**: o job `Validate` herda `contents: write` do workflow e o checkout persiste o
   token (`persist-credentials: true` no log da run 33463864134); `openspec` roda `@latest`
   (`scripts/validate-rite.sh:81`) enquanto o `claude-code` é pinado.
6. **Higiene**: nenhum `timeout-minutes` (Validate variou de 57s a 5m38s entre as runs 33463864134 e
   33843366162); `outputs`/step `check_release` não têm consumidor.
7. **validate-rite-evidence.py** (`:159`, `:198`): E.3/E.4/S.3 aceitam qualquer texto acima de 120
   caracteres, e o limite não está declarado no KNOWN LIMIT.

Cada uma está fora das declarações de "o que não cobre" que este repositório exige de cada check
(`openspec/specs/skills-catalog/spec.md`, cenário *The uncovered part is declared, not implied*).

## What Changes

- O step de wrappers falha também quando `git status --porcelain` não está vazio depois de
  `generate.sh`, nomeando os arquivos não rastreados.
- `validate-spec-rite.py` exige **relevância**: o diff toca `openspec/changes/<id>/` de uma change
  ativa, ou o corpo do PR nomeia `Spec-rite: <id>` de uma change ativa, ou o diff arquiva uma change,
  ou carrega a dispensa escrita. O selftest ganha "change ativa não relacionada" como achado.
- `scan-secrets.py` ganha `--selftest` (uma credencial injetada por padrão, inclusive uma precedida de
  `test` e uma de `<`), aplica `PLACEHOLDER` só ao token casado, cobre `github_pat_` e `sk-`, e o
  selftest entra no CI logo depois do scan.
- Os greps de frontmatter passam a olhar só o bloco entre os dois `---`, extraído com o mesmo `awk`
  de `generate.sh:29-31`.
- O job `Validate` roda com `permissions: contents: read`, checkout com `persist-credentials: false`;
  `@fission-ai/openspec@1.6.0` pinado em `validate-rite.sh` com comentário de bump.
- `timeout-minutes` nos dois jobs; `outputs` e `check_release` do job de release removidos por não
  terem consumidor.
- `validate-rite-evidence.py` declara o escape dos 120 caracteres no KNOWN LIMIT e o cobre com caso
  de selftest explícito (esperado mudo).

Nenhuma dessas mudanças é **BREAKING** para consumidores do catálogo: nenhum skill entra, sai ou
muda de nome. É mais restritiva para quem abre PR neste repositório: um diff fora de `openspec/` com
uma change ativa alheia e sem linha `Spec-rite:` passa a reprovar.

## Capabilities

### New Capabilities

_Nenhuma._ Nenhum skill novo entra no catálogo.

### Modified Capabilities

- `skills-catalog`: *The repository itself is gated, not only its skills* ganha três classes que
  escapavam — arquivo gerado não rastreado, change ativa sem relação com o diff, campo de frontmatter
  fora do bloco de frontmatter — e passa a exigir privilégio mínimo, versões pinadas e timeout no job
  que gata. *The rite gates evidence before it gates quality* passa a exigir que o escape de
  comprimento das caixas de gap seja declarado no próprio script e coberto por caso de selftest.
- `skills-authoring`: *The catalog carries no credentials* ganha o selftest do scanner, o escopo do
  filtro de placeholder (só o token casado) e as duas classes novas de token.

## Impact

- `.github/workflows/ci.yml` — bloco de permissões do job `Validate`, checkout, steps *Wrappers in
  sync* e *Skill frontmatter checks*, um step novo de selftest do scanner, `timeout-minutes` nos dois
  jobs, `outputs` e step `check_release` removidos.
- `scripts/validate-rite.sh` — pin do `openspec`.
- `scripts/validate-spec-rite.py`, `scripts/scan-secrets.py`, `scripts/validate-rite-evidence.py`.
- Nenhum `SKILL.md` é tocado; a composição do catálogo (35 skills, descoberta via `npx`) fica
  idêntica. Espelhos gerados por `./generate.sh` não mudam.
- Quem abre PR neste repositório: uma change ativa alheia deixa de servir de registro. O PR que só
  marca caixas em `tasks.md` toca o diretório da change e continua passando; o PR que só arquiva
  continua passando via `archived_in_diff`.
