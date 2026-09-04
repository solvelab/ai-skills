## Context

O `.github/workflows/ci.yml` (231 linhas em `d2918ed`) tem dois jobs. `validate` (linhas 25-131)
roda em todo evento e encadeia treze steps; `release` (133-231) roda só em `push` para `master`. As
permissões são declaradas uma vez, no nível do workflow (linhas 14-17: `contents: write`,
`issues: write`, `pull-requests: write`), e os dois jobs as herdam. Nenhum job declara
`timeout-minutes`.

Os quatro scripts que este change toca declaram cada um, no cabeçalho, o que não cobrem — a
convenção do repositório. Os buracos medidos na issue #117 estão todos **fora** dessas declarações:
são coisas que o gate diz medir e não mede.

O que foi lido para decidir, no commit `d2918ed` (2026-09-04):

- `generate.sh:29-31` — a função `frontmatter()` extrai o bloco entre os dois `---` com
  `awk 'NR==1 && $0=="---"{inFM=1; print; next} inFM && $0=="---"{print; exit} inFM{print}'`.
  Os greps do CI não a usam; varrem o arquivo inteiro.
- `scripts/validate-spec-rite.py:171-196` — `evaluate()` retorna sem achado quando `changes` (a lista
  de diretórios ativos) não está vazia. A lista vem de `active_changes()`, que lê o filesystem, não o
  diff. `SILENT[2]` (`:210`) fixa esse comportamento como correto.
- `scripts/scan-secrets.py:55-64` — `find()` descarta o match quando `PLACEHOLDER` casa no token
  **ou** nos 40 caracteres anteriores. `PLACEHOLDER` inclui `test` e `<`.
- `scripts/validate-rite-evidence.py:157-161` e `:197-200` — E.3, E.4 e S.3 passam com `NEGATIVE`
  **ou** `len(body) > 120`. O KNOWN LIMIT (`:36-51`) tem seis itens; nenhum menciona o comprimento.
- `scripts/validate-rite.sh:78-82` — usa `openspec` do PATH quando existe; no CI cai em
  `npx -y @fission-ai/openspec@latest`. `npm view @fission-ai/openspec version` -> `1.12.0`; a versão
  instalada e probada localmente é `1.6.0`.

## Goals / Non-Goals

**Goals**

- Cada um dos sete buracos fecha, ou fica escrito como limite conhecido **dentro do check**.
- Todo gate Python alterado mantém ou ganha `--selftest` verde, com um defeito injetado por regra.
- O job `Validate` roda com o mínimo de privilégio e versões pinadas.
- O fluxo de arquivar não quebra: um PR que só toca `openspec/changes/archive/` continua passando.

**Non-Goals**

- Proteção de branch e Dependabot (issues de decisão, fora deste item).
- Pinar actions por SHA (mudança de política de manutenção; follow-up).
- Tornar o spec-rite capaz de julgar se a change é honesta — continua provando relevância por caminho
  e por nome, não por conteúdo.
- Tocar qualquer outro step de `ci.yml` (itens paralelos adicionam steps depois de outros selftests).
- Atualizar `README.md`: o parágrafo que descreve o spec-rite (linhas 731-739) fica um passo atrás
  do script; registrado como follow-up em `tasks.md` E.4.

## Decisions

### D1 — O step de wrappers lê `git status --porcelain`, não só `git diff`

`git diff --exit-code` compara índice com árvore de trabalho e nunca vê arquivo `??`. Depois de
`bash generate.sh`, o step passa a falhar quando `git status --porcelain` devolve qualquer linha, e
imprime as linhas `??` separadamente, com o nome de cada arquivo, antes do `git diff --stat` dos
rastreados. Uma única checagem cobriria os dois casos, mas a mensagem do caso antigo ("out of sync,
run ./generate.sh") continua correta e vale manter distinta da nova ("generated file untracked, add
it").

Alternativa rejeitada: `git add -A && git diff --cached --exit-code`. Funciona, mas muda o índice do
runner e esconde a distinção entre "modificado" e "novo" que a mensagem quer nomear.

### D2 — Relevância do spec-rite por caminho ou por nome, nunca por existência

`evaluate()` ganha uma regra: com `offenders` não vazio e sem arquivo em `archive/`, o diff está
registrado só se **(a)** algum caminho começa com `openspec/changes/<id>/` para `<id>` ativo, ou
**(b)** o corpo do PR carrega uma linha `Spec-rite: <id>` com `<id>` ativo. A linha é lida com o
mesmo cuidado da dispensa: âncora no começo da linha, casada como texto, nunca interpolada.

Quando existem changes ativas mas nenhuma satisfaz (a) ou (b), o achado é novo — `S3 unrelated
change` — e nomeia as changes ativas encontradas e as duas formas de ligar o diff a uma delas. `S1`
continua sendo o caso "nenhuma change existe". A separação importa para o selftest: `SILENT[2]`
("active change present") passa a ser um `DEFECT`, e os casos mudos ganham "change tocada no diff" e
"change nomeada no corpo".

Por que (a) basta: o PR que só marca caixas em `tasks.md` toca `openspec/changes/<id>/tasks.md`, e
portanto registra-se sozinho — é exatamente o PR legítimo que o risco da issue temia reprovar.

Por que (b) existe: um PR de correção pequena, aberto contra uma change já em andamento em outro
branch, não toca o diretório dela. A linha `Spec-rite: <id>` já é a que `execute-backlog` manda
escrever no corpo (`skills/execute-backlog/references/spec-rite.md:83`); o gate só passa a lê-la.

`archived_in_diff` fica intocado: TR2 da issue exige que o PR de archive continue passando, e ele
toca só `openspec/`, então nem chega à regra nova.

KNOWN LIMIT atualizado: relevância é por caminho e por nome, não por conteúdo. Um tick qualquer em
`tasks.md` de uma change ativa liga qualquer diff a ela; a revisão continua sendo quem julga.

### D3 — `PLACEHOLDER` só no token; selftest gera as credenciais em runtime

`find()` passa a testar `PLACEHOLDER` só em `m.group(0)`. A janela de 40 caracteres anteriores foi
medida no tree atual antes de remover: zero matches dependem só dela (`tasks.md` E.2), então a
mudança não cria falso positivo no repositório de hoje.

O selftest injeta uma amostra por padrão em `PATTERNS`, mais uma precedida de `test_token = ` e uma
entre `<` e `>`, e afirma que a classe é detectada; e injeta casos que devem ficar mudos (token com
`xxx`, senha `<password>` numa connection string, IP privado reportado sem gatar). As amostras são
**montadas** em runtime (`"ghp_" + fill(36)`), nunca literais: o próprio `scan-secrets.py` está no
tree que o scan do CI lê, e um token literal no arquivo reprovaria o build por design.

Padrões novos: `github_pat_[A-Za-z0-9_]{22,}` (PAT fine-grained) e `sk-[A-Za-z0-9_\-]{20,}` (chaves
`sk-…`, `sk-proj-…`, `sk-ant-…`). Ambos probados contra o tree atual sem match (`tasks.md` E.2).

### D4 — Greps de frontmatter sobre o bloco extraído com o `awk` de `generate.sh`

O step extrai o bloco uma vez por arquivo, com o **mesmo** `awk` de `generate.sh:29-31` (copiado
literalmente, para que os dois leiam a mesma coisa), e todos os greps rodam sobre esse texto via
here-string. O check de primeira linha (`head -1 | grep '^---$'`) fica como está: é ele que garante
que o `awk` tem por onde começar.

Alternativa rejeitada: chamar `source generate.sh` para reutilizar a função. `generate.sh` tem
`set -euo pipefail` e efeitos colaterais no topo; importar só a função exigiria refatorar um arquivo
fora deste item.

### D5 — Privilégio mínimo no job, não no workflow

`permissions: contents: read` vai no job `validate`, não no nível do workflow: o job `release`
precisa de `contents: write` (tag, commit de release) e o bloco do workflow continua servindo a ele.
Um bloco de permissões no job substitui o do workflow por inteiro — todo escopo não listado vira
`none` — então `Validate` fica só com leitura. Nenhum step de `Validate` escreve no repositório ou
usa `GITHUB_TOKEN` (lidos um a um em `tasks.md` E.1). `persist-credentials: false` remove o token do
`.git/config` depois do fetch; o fetch em si ainda usa o token, o que é tudo de que o checkout precisa.

`openspec` pinado em `1.6.0` porque é a versão probada aqui (`openspec --version` -> `1.6.0`) e a que
o cabeçalho de `validate-rite.sh` já cita. O comentário de bump repete a regra do step do
`claude-code`: sobe deliberadamente, depois de rodar local.

### D6 — Timeout nos dois jobs; `outputs` e `check_release` removidos

`timeout-minutes: 15` nos dois jobs. Medido: `Validate` levou 57s (run 33463864134) e 5m38s (run
33843366162); `Semantic Release` 29s. O teto é generoso o bastante para uma run lenta de `npx` e
curto o bastante para não segurar a fila de `master` (serializada por `concurrency`) por horas.

`outputs.new_release`/`outputs.version` e o step `check_release` são removidos, não ligados a um
consumidor: `grep -rn "check_release\|new_release\|needs: \[release\]"` fora de `ci.yml` devolve
vazio, o semantic-release já imprime `Published release X` no log, e o step escrevia
`new_release=false` tanto para "nada a publicar" quanto para "não consegui publicar" — a
ambiguidade que a change `fix-release-race` (E.4) já tinha notado. O step `Get previous tag`
(`prev_tag`), cujo único leitor era `check_release`, **não** está na lista de steps deste item e fica
como está; registrado como follow-up.

### D7 — O escape dos 120 caracteres é declarado e coberto, não fechado

Fechar o escape exigiria decidir o que é "nomear um gap" por regex, o que é o mesmo problema que o
KNOWN LIMIT 1 já rejeitou: CI só prova forma. A decisão é declarar o escape como KNOWN LIMIT 7 e
adicionar ao selftest uma lista `ESCAPES` com um caso explícito — E.3 com 130 caracteres de
enchimento sem gap nomeado — cujo resultado esperado é **silêncio**. O selftest passa a imprimir
`n/n known escapes stayed silent`, o mesmo formato que `S.2` já pede.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Um check declara dentro de si o que não cobre | `skills-catalog` (spec do repositório) + `verify-before-claiming` | already canonical — os quatro scripts só estendem o próprio KNOWN LIMIT |
| Um gate carrega selftest com um defeito injetado por regra | `skills-authoring` (*Authoring rules are machine-enforced*) | already canonical — `scan-secrets.py` passa a cumprir a regra; nenhum texto é copiado |
| A linha `Spec-rite: <id>` no corpo do PR | `execute-backlog` (`references/spec-rite.md`) | already canonical — o gate passa a ler a linha que a skill já manda escrever; a skill não muda |
| Prova observada, não esperada, antes de declarar entrega | `verify-before-claiming` | already canonical — citado no grupo de simulação de `tasks.md` |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — ids de step, nomes de função e labels de selftest em inglês |

Nenhuma skill do catálogo é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **`contents: read` pode quebrar um step de `Validate` que escreva.** → Nenhum escreve hoje (E.1
  lista os treze); confirmado na run do PR, registrada em `tasks.md` S.1 quando existir.
- **A relevância do spec-rite pode reprovar um PR legítimo.** → Os dois PRs legítimos previsíveis
  passam por desenho: "só tick de tasks" toca a change (D2-a); "correção pequena contra change em
  andamento" nomeia a change (D2-b). O PR de archive nem chega à regra.
- **`git status --porcelain` no CI pode ver lixo que não é de `generate.sh`.** → O step é o primeiro
  depois do checkout, e `.gitignore` já cobre `__pycache__`/`*.py[cod]`. Se um step futuro deixar
  arquivo antes dele, a mensagem nomeia o arquivo, o que é o comportamento desejado.
- **`PLACEHOLDER` só no token pode criar falso positivo em docs que escrevem `example` antes de um
  token real-shaped.** → Medido zero no tree atual; e um token real-shaped em docs é exatamente o que
  o cenário *An example credential is written so it cannot be mistaken for one* proíbe.
- **`sk-` é prefixo curto.** → Exige 20+ caracteres de classe estreita depois do hífen e `\b` antes;
  probado sem match no tree atual.
- **`timeout-minutes: 15` pode matar uma run legítima muito lenta.** → 15 min é 2,7x a pior run
  medida; uma run acima disso é sinal de `npx` travado, que hoje segura a fila até o default de 360 min.

## Open Questions

Nenhuma. Os pontos que poderiam virar achismo — o valor de `persist-credentials` no log, a versão
publicada do `openspec`, a existência de consumidor dos `outputs`, o efeito da janela de 40
caracteres no tree atual — foram medidos e estão em `tasks.md` com comando e saída.
