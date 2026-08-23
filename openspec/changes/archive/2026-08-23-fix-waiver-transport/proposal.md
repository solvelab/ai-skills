# Change: Ler a dispensa do payload do evento, não de env que o CI ecoa

## Why

O gate entregue pelo `2026-08-23-add-spec-rite-gate` recebe o corpo do PR por variável de ambiente, e
o GitHub Actions imprime o bloco `env:` de todo passo `run:` no cabeçalho do passo. Medido no run
`32648727841`, job `97216916829`, passo *OpenSpec rite gate*:

```
##[group]Run bash scripts/validate-rite.sh
shell: /usr/bin/bash -e {0}
env:
  PR_BODY: Closes #89

Spec-rite: add-spec-rite-gate
...
```

O corpo inteiro do PR sai no log. Um gate virou canal de divulgação do que ele lê.

Neste repositório o dano é nulo — é público, e o corpo do PR já é visível a qualquer um. O que
importa é a forma, porque ela viaja: as duas skills de backlog são portáteis, `spec-rite.md`
documenta o mecanismo, e o mesmo desenho vai ser copiado para repositórios privados, onde o log do
Actions tem plateia diferente do PR.

## What Changes

- `scripts/validate-spec-rite.py` passa a ler o corpo do PR do arquivo apontado por
  `GITHUB_EVENT_PATH` — o payload completo do webhook, que para `pull_request` carrega
  `pull_request.body`. `PR_BODY` é rebaixado a **override explícito** para teste local e para o caso
  de o payload não trazer a chave.
- `.github/workflows/ci.yml` perde o bloco `env:` do passo do gate.
- O `--selftest` cobre o leitor novo: payload sintético lido, arquivo ausente tratado, precedência do
  override respeitada.
- **Nada da decisão muda.** As regras `S0`/`S1`/`S2`, a regex ancorada, a allowlist de release e a
  isenção de diff confinado a `openspec/` ficam idênticas. Só o transporte.

**Não é BREAKING.** A forma da linha de dispensa (`Spec-rite: none — <motivo>`) é a mesma, e quem
abre PR não muda nada no que escreve.

## Capabilities

### New Capabilities

_Nenhuma._ O gate já existe; o que muda é por onde ele lê.

### Modified Capabilities

- `skills-catalog`: *The rite gates evidence before it gates quality* — o parágrafo que já trata a
  dispensa como entrada não confiável ganha a segunda metade da mesma preocupação. Hoje ele governa
  o que o gate **faz com** o que lê (casar como texto, nunca executar); passa a governar também o que
  o gate **faz aparecer**: um gate não publica o conteúdo que lê num canal com plateia diferente da
  do próprio conteúdo. É a mesma regra vista do outro lado, não um requisito novo ao lado dela.

## Impact

- `scripts/validate-spec-rite.py`, `.github/workflows/ci.yml`.
- `openspec/specs/skills-catalog/spec.md`, após o archive.
- Nenhum skill e nenhum doc: verificado que nem `README.md` nem
  `skills/execute-backlog/references/spec-rite.md` nomeiam o transporte —
  `grep -n "PR_BODY" README.md skills/execute-backlog/references/spec-rite.md` não retorna nada.
  Essa neutralidade é propriedade a preservar, e vira critério de aceite.
- Consumidores do catálogo: nenhuma diferença. Quem abre PR: nenhuma diferença.
