# Change: Tornar a publicação de versão imune à corrida entre merges

## Why

O job `Semantic Release` do `.github/workflows/ci.yml` publica a versão do catálogo a partir do
commit que **disparou** a run, não do topo de `master`. Quando dois pull requests entram em `master`
em janela curta, a run enfileirada do primeiro commit faz checkout de um SHA que já está atrás do
remoto, e o semantic-release desiste — em silêncio, com o job **verde**.

Medido na run 32959050372 (commit `4875a6c`, PR #102, um `feat`):

```
[semantic-release] › ℹ  The local branch master is behind the remote one, therefore a new version won't be published.
```

O mecanismo, lido no pacote instalado (`semantic-release@25.0.9`, `package/index.js:87-96`):
`verifyAuth` roda `git push --dry-run --no-verify -- <url> HEAD:master`, que falha porque o push
seria non-fast-forward; no `catch`, `isBranchUpToDate` compara o HEAD local com o SHA que
`git ls-remote --heads` devolve, vê a diferença, loga a linha acima e faz `return false`. Esse
`false` não vira erro: `package/cli.js:55` devolve `0`, e o job termina **success**.

Naquele dia o resultado ainda foi correto — o PR #103 entrou segundos depois e a run dele publicou
`v2.15.0` cobrindo os dois commits. A publicação sobreviveu por sorte, não por desenho. O release
some quando a run posterior não publica: o `Validate` dela falha, o push posterior carrega
`[skip ci]` (o próprio commit de release carrega), ou ela perde a mesma corrida para um terceiro
merge.

## What Changes

- O job `release` passa a operar sobre o **topo do branch de release**, não sobre o commit que
  disparou a run.
- A condição "não publiquei porque meu checkout estava atrás" deixa de terminar verde: vira falha
  explícita do job, com a linha do log que a comprova.
- O caso legítimo "não havia nada para publicar" (push só de `docs`/`chore`) continua verde.
- O que a guarda **não** cobre fica escrito dentro do próprio workflow, seguindo a convenção do
  repositório de um check declarar o próprio ponto cego.

## Capabilities

### Modified Capabilities

- `skills-catalog`: ganha o requisito de que a automação de publicação do próprio repositório não
  dependa do intervalo entre merges, e de que uma publicação pulada seja visível. Hoje a capability
  já governa o CI do próprio repositório em *"The repository itself is gated, not only its skills"*,
  mas só sobre os gates de `Validate` — nada diz sobre o job que publica.

## Impact

- `.github/workflows/ci.yml` — job `Semantic Release`: o checkout e a verificação pós-execução.
- Nenhuma skill do catálogo muda: nenhum `SKILL.md` é tocado, e a composição do catálogo
  (contagem, descoberta via `npx`) fica idêntica.
- Consumidores do catálogo não veem mudança de comportamento; o que muda é a garantia de que a tag
  e a release do GitHub saem quando são devidas.
