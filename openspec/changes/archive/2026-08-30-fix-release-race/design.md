## Context

`.github/workflows/ci.yml` tem dois jobs. `validate` (linhas 25-130) roda em todo evento;
`release` (linhas 132-191) roda só em `push` para `master` (linha 135) e executa
`npx semantic-release` (linha 174) sob `.releaserc.json`, cujo `branches` é `["master"]`.

As runs de `master` são serializadas por `concurrency.group: ci-${{ github.ref }}` com
`cancel-in-progress: false` (linhas 19-21): duas entram em fila, nenhuma é cancelada.

Num evento `push`, `actions/checkout` sem `ref` explícito faz checkout de `github.sha` — o commit
que disparou aquela run. Como a fila pode segurar a run do commit A enquanto o commit B já entrou em
`master`, o job de A trabalha sobre um HEAD atrasado.

O que o semantic-release faz nessa situação, lido em `semantic-release@25.0.9`:

- `package/index.js:88` chama `verifyAuth`, que é `git push --dry-run --no-verify -- <url> HEAD:master`
  (`package/lib/git.js:209-216`). Com HEAD atrasado o push seria non-fast-forward e o comando falha.
- No `catch`, `package/index.js:90` chama `isBranchUpToDate`, que compara `getGitHead()` com o SHA
  de `git ls-remote --heads -- <url> master` (`package/lib/git.js:296-303`). Diferentes.
- `package/index.js:91-94` loga `The local branch master is behind the remote one, therefore a new
  version won't be published.` e faz `return false`.
- Esse `false` percorre `package/cli.js:55`, que devolve `0`. O processo sai com sucesso.

Ou seja: a decisão de não publicar chega ao Actions indistinguível de "não havia nada a publicar".

## Goals / Non-Goals

**Goals:**

- Um commit que entra em `master` e merece release recebe uma, independentemente de quão perto o
  merge seguinte cair.
- Uma run que não consegue publicar por estar atrás do remoto fica **vermelha**, não verde.
- O caso legítimo de "nada a publicar" continua verde.

**Non-Goals:**

- Mudar as regras de release (`releaseRules`, plugins, política de versão) em `.releaserc.json`.
- Trocar o semantic-release por outra ferramenta, ou introduzir tag manual.
- Mexer nos gates do job `validate`.
- Emitir tag retroativa: `v2.15.0` já cobre `4875a6c`.

## Decisions

### D1 — O job `release` faz checkout do topo de `master`, não do SHA que disparou a run

`ref: master` no `actions/checkout` do job `release`. `fetch-depth: 0` continua, porque o
semantic-release precisa do histórico e das tags.

Por que isso é seguro aqui e não seria em qualquer repositório: as runs de `master` já são
serializadas por `concurrency` (linhas 19-21). A run de A só executa o job de release quando nenhuma
outra run de `master` está em curso; ela pega o topo, publica o que for devido de A **e** de B, e a
run de B em seguida encontra nada a publicar e termina verde.

Consequência aceita: o commit sobre o qual o release roda pode ser mais novo do que o commit que o
`validate` desta run examinou. Cada um desses commits passou pelo `validate` no próprio pull request
— `master` é protegido e não recebe push direto além do commit de release, que carrega `[skip ci]`.
Essa razão vai escrita como comentário no workflow, seguindo a convenção do arquivo de explicar
inline toda decisão de CI não óbvia (linhas 30-31, 120-125, 167-168).

### D2 — Não trocar `cancel-in-progress` para `true`

Cancelar a run anterior parece resolver a corrida, mas descarta justamente a run que carregava a
publicação. Com `false` + D1 a fila vira uma garantia: cada run pega o topo do momento em que roda.

### D3 — A recusa vira falha visível, via a linha que o próprio semantic-release emite

O step `Run semantic-release` grava a saída num arquivo e um step seguinte falha o job quando
encontra `is behind the remote one` nela. A âncora é a string do log, não o exit code, porque o exit
code é `0` por desenho (`package/cli.js:55`) e não distingue os dois casos.

Depois de D1 essa condição deixa de ser esperada: a guarda é um **tripwire**, não um caminho de
rotina. Ela existe porque a falha que ela cobre já aconteceu uma vez em silêncio, e porque D1 depende
de uma premissa (a serialização por `concurrency`) que uma edição futura do workflow pode remover sem
perceber.

### D4 — O ponto cego fica declarado dentro do step

A guarda casa uma única string emitida por uma versão específica do semantic-release. Se o upstream
reescrever a mensagem, ela para de disparar e nada avisa. Isso vai escrito no próprio step, como o
repositório já faz nos checks de `scripts/` — cada um declara o que não cobre
(`openspec/specs/skills-catalog/spec.md:487`, cenário *"The uncovered part is declared, not implied"*).

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Um check declara o que não cobre | `skills-catalog` (spec do repositório) + `verify-before-claiming` | already canonical — o workflow só aplica a regra, sem reescrevê-la |
| Prova observada, não esperada, antes de declarar entrega | `verify-before-claiming` | already canonical — citado no grupo de simulação de `tasks.md` |
| Fallback e degradação de dependência externa | `backend-resilience` | não se aplica: nada aqui chama dependência de runtime; a guarda é de pipeline |

Nenhuma skill do catálogo é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **O release roda sobre um commit que o `validate` desta run não examinou.** Mitigação: cada commit
  passou pelo `validate` no próprio PR; `master` é protegido. Registrado como comentário no workflow.
- **O tripwire de D3 pode ficar mudo se o upstream mudar a mensagem.** Mitigação: a versão do
  semantic-release já é pinada na instalação (linha 169, `semantic-release@25`), e o ponto cego fica
  declarado no step (D4).
- **O tripwire pode ficar vermelho num caso benigno** — uma run atrasada cuja publicação outra run
  já fez. Depois de D1 essa combinação não deveria ocorrer; se ocorrer, ela indica que a premissa da
  serialização caiu, que é exatamente o que se quer ver em vermelho.
- **Não há como ensaiar o caminho de publicação sem empurrar para `master`.** Mitigação: o tripwire
  é exercitado contra o log real da run 32959050372 e contra um log de push só de `docs`; o `ref`
  é comprovado no merge desta própria change, cuja run é registrada no pull request.

## Open Questions

Nenhuma. Os dois pontos que poderiam ter virado achismo — o texto exato da mensagem e o código de
saída do processo — foram lidos no pacote publicado, e estão registrados em `tasks.md` com comando e
saída.
