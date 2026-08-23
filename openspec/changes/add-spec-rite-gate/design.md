## Context

O rito backlog-first deste repositório é enforçado em quatro camadas, e o OpenSpec só aparece de
verdade em nenhuma delas. Medido no HEAD `c275a38`, em 2026-08-23:

```
$ grep -rn -i "openspec" skills/backlog | wc -l
0
$ grep -rn -i "openspec" skills/execute-backlog | wc -l
5
$ grep -c -i "openspec" claude/global/hooks/backlog-rite.py
0
```

As cinco ocorrências em `execute-backlog` são todas exemplo dentro de um mecanismo genérico de
descoberta (`references/execution-flow.md:54`, `SKILL.md:89`,
`references/acceptance-tracking.md:13`), nunca um passo da espinha numerada.

A camada 4 é a única que sobreviveria a um contribuidor sem os hooks locais, e ela aprova por
vacuidade:

```
$ ls openspec/changes/
archive
$ sed -n '20,26p' scripts/validate-rite.sh
for dir in "$CHANGES_DIR"/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  [ "$name" = "archive" ] && continue
```

Sem change ativa, o corpo do loop nunca roda. `scripts/validate-rite-evidence.py:121` faz o mesmo
por outro caminho — `if not base.exists(): return []`, e a lista de `tasks.md` ativos sai vazia.

## Goals / Non-Goals

**Goals:**

- Um PR que toque `skills/**` sem change OpenSpec e sem dispensa escrita não fica verde.
- A decisão de dispensar vira uma linha escrita, revisável, em vez de um julgamento interno do
  modelo.
- As três camadas acima do CI nomeiam o rito de spec explicitamente, e a de baixo o exige.
- O rito continua portátil: as duas skills rodam também nos repositórios DriveZone, com rito e
  schema próprios.

**Non-Goals:**

- Reescrever a doutrina vanilla de `skills/openspec/SKILL.md` §*When a proposal is required*. Ela
  descreve o OpenSpec; a política de rigor é do repositório.
- Mexer em `skills/openspec-drivezone/`.
- Remediar os desvios equivalentes nos repositórios DriveZone — rito próprio, item próprio lá.
- Arquivar este change no mesmo PR. O precedente é PR separado (`#78`, `#74`).
- Provar que a change é honesta. O gate prova que ela existe; a revisão julga o conteúdo.

## Decisions

**Fail-closed com dispensa escrita, e não "proposta sempre, sem exceção".** A escolha do mantenedor
foi gate duro. Gate duro literal não é implementável: o CLI 1.6.0 exige ≥1 delta de spec por change
e `skills/openspec/SKILL.md:36-38` registra que `skip_specs` foi probado e não tem efeito. Um typo
forçaria inventar requisito — que a doutrina do próprio repositório proíbe (*"A near-duplicate
ADDED requirement is the wrong answer: it splits the doctrine"*). A forma que preserva a intenção é
inverter o default: o artefato é exigido, e a única saída é uma linha escrita que o CI lê e o
revisor vê. Nada escapa por julgamento silencioso, que era o alvo.

**A política mora no repositório, não na skill.** `backlog` e `execute-backlog` são portáteis e
rodam em repositórios com ritos diferentes. Hardcodar "proposta obrigatória" nelas exportaria a
política deste repositório para todos. A chave `spec_rite.policy` em `backlog.yml` resolve isso, e o
default sem chave, com `openspec/` presente, é `required` — a ausência de decisão não vira permissão.

**Upgrade automático, downgrade com o usuário.** O modo de falha medido nas issues #79 e #84 foi o
downgrade silencioso: o item nasce sem exigir artefato, e a implementação cresce sem que ninguém
revisite. Subir o veredito (dispensa → artefato) não tira nada de ninguém e é automático. Descer
(artefato → dispensa) é exatamente o movimento que produziu a deriva, e para.

**A dispensa vive no corpo do PR, não em label nem em arquivo.** Label não carrega motivo. Arquivo
no repositório vira lixo permanente por uma decisão de um PR só. O corpo do PR é onde o revisor já
está olhando, e o `github.event.pull_request.body` chega ao script sem API extra.

**A dispensa é entrada não confiável.** Ela é escrita por quem abre o PR, inclusive de um fork. O
script casa por regex ancorada e nunca interpola em comando — a alternativa (avaliar a linha, ou
passá-la a um shell) daria execução arbitrária a um contribuidor externo.

**`fetch-depth: 0` é pré-requisito, não detalhe.** `.github/workflows/ci.yml:28` usa
`actions/checkout@v5` sem `with:`, ou seja profundidade 1: não existe base para `git diff`. Sem essa
mudança a checagem nova não tem o que ler, e a forma de falha seria a pior possível — um gate que
não consegue medir e por isso passa.

**A checagem só roda em `pull_request`.** Em `push` para `master` o merge já aconteceu; reprovar ali
não protege nada e quebraria os commits de release do semantic-release.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Ciclo OpenSpec (explore → propose → validate --strict → apply → archive), formato de proposal/delta/tasks, quando uma proposta é exigida na doutrina vanilla | `openspec` | já canônica — `backlog` e `execute-backlog` carregam o **gate** e linkam; nenhuma delas restata o ciclo |
| Variante de schema forkado com gates obrigatórios | `openspec-drivezone` | já canônica — citada como precedente de fork, não reescrita |
| Rito backlog-first (todo change vira item antes da primeira edição) | `claude/global/personal-rules.md` → `backlog` / `execute-backlog` | já canônica — este change acrescenta a perna de spec, não redefine o rito |
| Anti-chute: não afirmar nem agir sobre fato não verificado; o downgrade silencioso da #79 é uma instância | `verify-before-claiming` | já canônica — `execute-backlog` linka no novo rail, sem restatar a escada de pesquisa |
| Camada de máquina em inglês (chaves de config, marcador do PR, nomes de arquivo) | `code-locale` | já canônica — o Glossary da issue #89 é a fonte dos nomes novos |
| Rito adversarial de teste do que foi implementado | `bug-hunter` | já canônica — o `--selftest` do gate segue o padrão dos gates irmãos, sem restatar a metodologia |

## Risks / Trade-offs

- **PR de fork escreve a dispensa** → a dispensa é dado, não instrução: regex ancorada, sem
  execução, sem interpolação. O revisor continua sendo quem julga o motivo.
- **Falso positivo nos commits do semantic-release** (`chore(release): … [skip ci]`) → allowlist de
  `VERSION`, `CHANGELOG.md` e `.claude-plugin/*.json`, mais a restrição a evento `pull_request`.
- **O gate reprovar o PR que o introduz** → este PR carrega change ativa, logo passa. Verificado
  antes de abrir.
- **Atrito virar burla** → a dispensa existe justamente para o caso legítimo. Se ela começar a
  aparecer em todo PR, o sintoma fica visível no histórico dos PRs, que era o objetivo.
- **`fetch-depth: 0` deixa o checkout mais lento** → o repositório é pequeno (histórico de meses,
  sem binários grandes); o custo é de segundos e é o preço de conseguir diffar.
- **O gate provar existência e ser lido como prova de qualidade** → o cabeçalho `KNOWN LIMIT` do
  script declara explicitamente que existência não é honestidade, no mesmo lugar onde já declara que
  forma não é verdade.

## Open Questions

- O payload de `UserPromptSubmit` carrega a chave `cwd`? A implementação probou o payload real antes
  de escrever; o fallback `os.getcwd()` cobre o caso de não carregar. Registrado em `E.2`.
