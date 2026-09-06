## Context

Os cinco pontos vêm de grupos E.4 já arquivados — cada um foi visto por quem fechava outra change,
anotado como follow-up e deixado. Nenhum é um gate novo; todos são um gate existente medindo menos
do que diz (1, 2, 4), pagando mais do que precisa (3) ou publicando um número que ninguém confere
(5). Lido em `e7f5fe8` (2026-09-06):

- `scripts/validate-spec-rite.py:167-170` — `changed_paths()` roda `git diff --name-only
  base...HEAD` e faz `splitlines()`. `requires_registration()` (`:174`) e `touched_changes()`
  (`:193`) comparam com `startswith("openspec/")` — um caminho quotado começa com `"`.
- `scripts/validate-skill-version.py:162-173` — `split_nul_paths()` + `changed_paths()` com `-z`,
  e `_probe_quoted_path()` (`:347-372`) commitando `skills/probe/references/café.md` num repositório
  descartável com `core.quotePath=true`. O módulo importa `validate-spec-rite.py` em tempo de carga
  (`_sibling_min_reason()`, `:84-101`) para `MIN_REASON`.
- `skills/code-locale/references/check-identifier-locale.py:612-664` — `scan_diff()` lê `--- `,
  `+++ `, `@@` e `+`; chama `scan_path()` só para arquivo adicionado; `lang` vem da extensão. `main()`
  (`:878-880`) aplica `is_vendored()` e acumula em `vendored`, impresso em `:906`. O hook
  `locale-stop-gate.py:294-296` chama `check.scan_diff(iter(...), allow, None)` e filtra
  `is_vendored` por fora nos achados.
- `scripts/selftest-validate-skills.py:117-134` — laço `for check, entry in MUTATIONS` com
  `tempfile.TemporaryDirectory()` + `shutil.copytree(SRC, dst, ignore=(".git", "node_modules"))`
  por iteração; 27 entradas em `MUTATIONS`; C7 cria um diretório, C11 cria um arquivo, os outros
  reescrevem um arquivo existente com `read_text()`/`write_text()`.
- `.github/workflows/ci.yml:70-79` — step *Version coherence*: `VERSION="$(tr -d '[:space:]' <
  VERSION)"` e `grep -q "\"version\": \"$VERSION\""` nos dois manifests.
- `generate.sh:27-36` e `scripts/set-version.sh:13-16` — `SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'`
  com o comentário "the two readers must agree on what a version is".
- `README.md:443` — `│   └── r3f-*/SKILL.md  # React Three Fiber skills (10 topics)` dentro do
  bloco ```text da árvore; `scripts/validate-repo-hygiene.py:91-94` declara esse `(10 topics)`
  como fora do alcance de H2 por estar em bloco de código.

## Goals / Non-Goals

**Goals**

- Os dois leitores de diff do repositório (`validate-spec-rite.py`, `validate-skill-version.py`)
  leem caminhos da mesma forma, e cada um prova isso no próprio selftest.
- `scan_diff()` e `scan_path()` concordam sobre o que é vendored, e o pulo é contado, não silenciado.
- O selftest do validador roda numa cópia só, com os 27 casos ainda detectados e o tempo medido.
- O CI recusa um `VERSION` que `generate.sh` também recusaria, antes de comparar manifests.
- Nenhum número solto na árvore do README.

**Non-Goals**

- Trocar a arquitetura dos gates ou adicionar checks novos (fora de escopo pela issue).
- Extrair um módulo compartilhado `scripts/_git_paths.py` (ver D1).
- Editar `validate-skill-version.py`, os hooks de locale ou `validate-repo-hygiene.py`: não estão
  na lista de arquivos deste item. A docstring do hygiene que cita `README.md:345 (10 topics)` fica
  um passo atrás — follow-up em `tasks.md` E.4.
- Fazer o selftest do validador rodar em paralelo ou em `git worktree`: uma cópia com reversão já
  remove o custo dominante (D3); paralelizar é otimização sem medida que a justifique.

## Decisions

### D1 — `split_nul_paths()` duplicado no spec-rite, não importado nem extraído

`validate-skill-version.py` carrega `validate-spec-rite.py` em tempo de import para ler
`MIN_REASON`. Importar na direção contrária fecharia um ciclo em tempo de carga (o spec-rite
executaria o irmão, que executa o spec-rite). Um terceiro módulo `scripts/_git_paths.py` resolveria
o ciclo, mas exigiria `sys.path` nos dois `--selftest` e criaria um arquivo para duas linhas de
código. O helper é `out.split("\0")` com filtro de vazios; a duplicata carrega um comentário que
nomeia o irmão e o motivo, e cada script prova a própria leitura com um probe em repositório
descartável — é o probe, não a origem do código, que impede as duas cópias de divergirem.

O probe do spec-rite difere do irmão no que prova: o caminho quotado fica **dentro de
`openspec/changes/<id>/`** de uma change ativa, e a asserção é `evaluate()` mudo — o diff se
registra pelo caminho que o git quotaria. O caso literal em `split_nul_paths()` (aspas, quebra de
linha) fica ao lado, como no irmão.

### D2 — `scan_diff()` pula o bloco vendored inteiro e devolve o caminho numa lista

No `+++ `, depois de resolver `path`, `is_vendored(Path(path))` decide: se vendored, `lang = None`
(nenhuma linha `+` entra em `run`), o path tier não roda, e o caminho vai para `vendored` — um
parâmetro opcional `vendored: list | None = None` que `main()` passa e os hooks não precisam passar
(`locale-stop-gate.py:294` chama com três posicionais e continua válido). `main()` imprime a lista
na linha `skipped (vendored/generated/minified)` que já existe para o modo de arquivos, com o mesmo
texto: "not this project's machine layer".

Alternativa rejeitada: filtrar `is_vendored` nos achados depois de `scan_diff()` (o que o hook de
Stop faz por fora). Filtrar depois ainda tokeniza o arquivo — um `dist/bundle.js` de 5 000 linhas é
lido inteiro para jogar fora — e não conta o pulo, que é o que KNOWN LIMIT 10 exige para arquivo sem
perfil de linguagem: reportado como pulado, nunca como aprovado.

A exclusão é por **caminho** (`VENDOR_PARTS`, `.min.`); `is_minified()` lê o corpo do arquivo, que
em modo diff não existe, e não entra — KNOWN LIMIT 12 diz isso.

### D3 — Uma cópia por run; mutação aplicada e desfeita em `finally`

`shutil.copytree` do repositório (35 skills, cinco árvores geradas) é o custo dominante: 27 cópias
em 49,1 s. A cópia passa a ser feita uma vez fora do laço; para cada mutação o laço guarda o
estado original do alvo — `read_bytes()` se existe, `None` se não — aplica a mutação com o mesmo
`read_text()`/`write_text()` de antes, roda o validador, e em `finally` restaura os bytes ou remove
o arquivo criado (C11) ou o diretório criado (C7, `shutil.rmtree`). Restaurar **bytes**, não texto:
`read_text()` normaliza `\r\n` e uma restauração por texto deixaria a cópia diferente da origem
para a mutação seguinte.

A ordem das mutações não muda e cada uma continua vendo a cópia limpa — a asserção `CAUGHT` de cada
caso é a mesma de antes. O que muda é a garantia: antes a isolação vinha de uma cópia nova; agora
vem da reversão, e um `finally` que não restaure deixaria a mutação anterior vazando para a
seguinte. A prova é que os 27 casos continuam `CAUGHT` **e** que o validador na cópia depois do
laço fica limpo (nenhuma mutação sobrou) — S.1.

### D4 — A regex do `generate.sh` no step, antes da comparação

O step ganha `SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'` — o mesmo literal de
`generate.sh:32` e `set-version.sh:15`, copiado e não importado, pelo mesmo motivo que os greps de
frontmatter copiaram o `awk` (D4 de `close-ci-gate-holes`): `generate.sh` tem `set -euo pipefail`
e efeitos colaterais no topo. `[[ "$VERSION" =~ $SEMVER_RE ]] || { echo "::error::VERSION is
'$VERSION' — ..."; exit 1; }` vem **antes** do laço dos manifests: um valor malformado que os três
arquivos compartilham (o caso medido, `2.15.1dirtychange`) passaria na comparação e tem de reprovar
antes dela.

### D5 — O comentário da árvore diz o que é, não quantos são

`(10 topics)` vira `one skill per topic`. Um número no README fora de bloco de código é gatado por
H2; dentro de bloco de código é revisão apenas, e a revisão o deixou errado por dois releases. A
alternativa — mover a linha para fora do bloco para que H2 a leia — quebraria a árvore ilustrativa;
tirar o número é a forma que não pode envelhecer.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Um gate lê o diff do jeito que o git escreve caminhos (`-z`, NUL) | `skills-catalog` (spec do repositório) | already canonical — o requisito ganha a frase; os dois scripts só a cumprem |
| Um check declara dentro de si o que não cobre (KNOWN LIMIT) | `skills-catalog` + `verify-before-claiming` | already canonical — KNOWN LIMIT 12 do detector e a docstring do spec-rite só estendem o próprio texto |
| Vendored/generated não é camada de máquina do projeto | `code-locale` | already canonical — `scan_diff()` passa a aplicar a exclusão que `scan_path()` e `main()` já aplicam; nenhum texto novo de doutrina |
| Um gate carrega selftest com um defeito injetado por regra | `skills-authoring` (*Authoring rules are machine-enforced*) | already canonical — os dois selftests ganham um caso cada; nenhum texto copiado |
| Prova observada, não esperada, antes de declarar entrega | `verify-before-claiming` | already canonical — citado no grupo de simulação de `tasks.md` |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — `split_nul_paths`, `vendored`, `original`, labels de selftest em inglês |

Uma skill é editada (`code-locale`: versão e linha *Verified against*); nenhuma doutrina é
restatada.

## Risks / Trade-offs

- **A duplicata de `split_nul_paths()` pode divergir do irmão.** → Cada script tem um probe em
  repositório real com `core.quotePath=true`; uma divergência que importe (voltar a `splitlines()`)
  reprova o selftest de quem a fizer.
- **Pular vendored em `scan_diff()` pode esconder um achado legítimo em `build/` ou `dist/` de um
  projeto que commita esses diretórios.** → É a mesma regra que o modo de arquivos já aplica a esses
  caminhos há meses (`VENDOR_PARTS`), e o pulo é contado na saída; um projeto que quer medir `dist/`
  já não conseguia pelo modo de arquivos.
- **A reversão por bytes pode falhar no meio e contaminar o caso seguinte.** → `finally` restaura
  mesmo quando `subprocess.run` levanta; e S.1 roda o validador na cópia depois do laço para provar
  que ficou limpa.
- **A regex pode recusar um `VERSION` que o semantic-release escreve.** → O semantic-release escreve
  `X.Y.Z` puro (histórico: `2.30.0`, `2.15.1`); pré-release `-beta.1` passa pelo sufixo opcional. É
  a regex que `generate.sh` já aplica no mesmo job, um step antes.
- **Remover `(10 topics)` perde informação.** → O número estava errado; o que a linha tem de dizer é
  que os `r3f-*` são um por tópico, e diz.

## Open Questions

Nenhuma. Os pontos que poderiam virar achismo — se o caminho quotado reprova mesmo, quanto custa a
cópia, se o step aceita `2.15.1dirtychange`, se o hook de Stop ainda passa — foram medidos e estão em
`tasks.md` com comando e saída.
