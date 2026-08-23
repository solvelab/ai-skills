# Change: Exigir change OpenSpec no rito e fechar o passe vazio do gate

## Why

O rito deste repositório tem quatro camadas de enforcement e o OpenSpec está ausente ou opcional em
todas as quatro. A camada que deveria reprovar aprova por vacuidade: `scripts/validate-rite.sh`
itera `for dir in "$CHANGES_DIR"/*/`, pula `archive` com `continue`, e quando não existe change
ativa nenhuma o corpo do loop nunca executa — `fail` continua `0` e o script imprime `rite gate OK`.
`scripts/validate-rite-evidence.py:121` tem o mesmo comportamento: retorna `[]` sem change ativa,
logo `findings` vazio, logo `exit 0`.

O gate valida a **forma** de uma change que existe. Nada exige que ela exista.

A consequência já ocorreu duas vezes, e está no arquivo deste repositório: o PR #80 entregou
`scripts/validate-rite-evidence.py` e o PR #84 entregou quatro checks de frontmatter — ambos gates
bloqueantes novos no CI, ambos **sem proposta OpenSpec**, ambos verdes. O
`2026-08-15-record-shipped-gates` existe só para registrar retroativamente o que os dois deixaram
de registrar, e abre com *"ambos sem proposta OpenSpec"*.

A justificativa gravada na issue #79 — *"ajuste de gate existente, não capacidade nova"* — é um
julgamento discricionário, invisível, e desmentido pelo precedente
`2026-08-07-add-repo-hygiene-gates`, que tem exatamente a mesma forma e teve proposta completa. Um
rito cuja única defesa é o modelo lembrar de uma regra não é um rito; é uma intenção.

## What Changes

- **Camada 4 (gate)** — `scripts/validate-rite.sh` ganha a checagem que fecha o passe vazio: um
  diff que toca caminho fora de `openspec/` exige change ativa, archive novo no próprio diff, ou
  uma dispensa escrita `Spec-rite: none — <motivo>` no corpo do PR. A checagem ganha `--selftest`
  injetando um defeito por regra, como todo gate deste repositório.
  `.github/workflows/ci.yml` ganha `fetch-depth: 0` (hoje 1, sem base para diffar), `PR_BODY` no
  ambiente e o passo de self-test.
- **Camada 3 (`execute-backlog`)** — o gate de spec sai do reference e entra na espinha numerada:
  novo safety rail *Spec-before-code* e novo passo entre a re-análise e o plano. O plano
  apresentado para aprovação passa a carregar change-id, capabilities e a saída do `--strict`.
- **Camada 2 (`backlog`)** — a triagem de rito passa a existir e a ficar escrita na issue: novo
  ground rule, novo passo de workflow, nova seção obrigatória no `issue-template.md` e a chave
  `spec_rite` documentada em `backlog-config.md`.
- **Camada 1 (hook)** — `claude/global/hooks/backlog-rite.py` nomeia o rito de spec, e **só** onde
  ele existe: a frase extra é emitida apenas quando há `openspec/` no `cwd` do payload.
- **Doutrina** — `claude/global/personal-rules.md` passa a descrever a mesma política que o gate
  enforça, em vez de uma classificação discricionária que o gate não conhece.

**Não é BREAKING para consumidores do catálogo**: nenhum skill é adicionado, removido ou renomeado;
a composição e a descoberta por `npx` ficam idênticas. É breaking para o **fluxo de contribuição**
deste repositório, que passa a exigir artefato ou dispensa escrita em todo PR.

## Capabilities

### New Capabilities

_Nenhuma._ Todo o comportamento novo cai em requisitos que já existem sobre o rito e sobre as
skills de backlog.

### Modified Capabilities

- `skills-catalog`: *The development rite is enforced outside the model's discretion* ganha a perna
  spec-driven — o rito não termina no item de backlog, e o artefato de spec é exigido por um gate
  fora da discrição do modelo, com dispensa possível apenas por escrito.
- `skills-catalog`: *The backlog skills declare their place in one rite* passa a exigir que as duas
  metades declarem também o gate de spec entre elas, sem restatar o ciclo OpenSpec.
- `skills-catalog`: *The rite gates evidence before it gates quality* passa a exigir que o gate
  cubra a **ausência** de change, não só a forma de uma change presente — o passe vazio é o furo
  que este change fecha.

## Impact

- `scripts/validate-rite.sh`, `.github/workflows/ci.yml`.
- `skills/backlog/SKILL.md` + `references/issue-template.md` + `references/backlog-config.md`.
- `skills/execute-backlog/SKILL.md` + `references/execution-flow.md` + novo `references/spec-rite.md`.
- `claude/global/hooks/backlog-rite.py`, `claude/global/personal-rules.md`, `README.md`.
- Árvores geradas por `./generate.sh` (`claude/`, `codex/`, `cursor/`, `copilot/`,
  `plugins/workflow/`), porque as descrições dos dois skills mudam e o CI diffa a árvore gerada.
- Consumidores do catálogo: nenhuma diferença. Contribuidores deste repositório: todo PR passa a
  precisar de change ativa ou de dispensa escrita.
