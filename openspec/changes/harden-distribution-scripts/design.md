## Context

`install.sh` (185 linhas em `d2918ed`) clona `~/ai-skills` ou faz `git pull` quando o diretório já
existe (linhas 146-152), e só depois entra no `case "$TOOL"` (158-181) que rejeita um valor
desconhecido. `--tool` lê `$2` direto (108) sob `set -u`.

`update.sh` (70 linhas) faz `fetch`, depois `reset --hard` (com `--force`) ou `pull --ff-only`
(47-51), e em seguida `bash generate.sh >/dev/null && echo "  ✅ Wrappers regenerated."` (59).

`generate.sh` lê `VERSION` e `skills/*/SKILL.md` e reescreve `claude/skills/`, `codex/skills/`,
`cursor/rules/`, `copilot/instructions/` e `plugins/` — este último com `rm -rf` e o valor de
`VERSION` gravado em cada `plugins/<group>/.claude-plugin/plugin.json`. Ou seja: as **entradas** do
gerador são `VERSION` e `skills/`; tudo o mais é saída.

`README.md:145` roda `update.sh` via `curl | bash`; `README.md:216` manda o usuário editar
`claude/global/personal-rules.md` no clone. Os dois fatos limitam o desenho: não há stdin para
perguntar nada, e a árvore do usuário pode estar legitimamente suja fora das entradas do gerador.

## Goals / Non-Goals

**Goals:**

- Um `update.sh` sobre `VERSION` ou `skills/` editados faz o pull, não regenera, diz o que está
  sujo e como limpar, e sai 0 sem tocar nenhum `plugin.json`.
- Uma falha do `generate.sh` durante o update é visível: exit ≠ 0 com a saída do erro.
- `install.sh` re-executado sobre um clone divergente falha com a mesma mensagem e dica de
  `update.sh`, em vez do `fatal:` cru do git.
- `install.sh --tool bogus` e `install.sh --tool` falham antes de qualquer `git clone`/`git pull`,
  listando os valores suportados.
- Um teste de fumaça sem rede, em `HOME` temporário, prova cada um desses comportamentos e roda no CI.

**Non-Goals:**

- Guarda de semver ou qualquer edição em `generate.sh` — pertence à issue que reescreve o bloco dos
  `plugin.json`.
- Prompt interativo em `--force`.
- Bloquear o update quando a árvore está suja fora de `VERSION`/`skills/`: o README documenta essa
  edição.
- Fazer `install.sh` delegar o re-run a `update.sh`.

## Decisions

### D1 — A guarda olha as entradas do gerador, não a árvore inteira

`git status --porcelain --untracked-files=no -- VERSION skills/`. Probado em `d2918ed` com
`VERSION` editado, `skills/untracked.txt` criado e `README.md` editado: o filtro devolve só
` M VERSION`. Uma edição em `claude/global/personal-rules.md` — o uso do `README.md:216` — não
aparece, e a regeneração segue normal, porque a saída do gerador não depende dela.

Por que **pular** a regeneração e não abortar o update: o pull é a parte útil para o usuário e não
é ela que corrompe nada; o dano medido na issue vem só do `generate.sh` rodando sobre `VERSION`
sujo. Pular com mensagem preserva o pull e elimina o dano.

### D2 — O que a guarda não vê fica escrito no cabeçalho do script

`--untracked-files=no` ignora arquivos novos (`skills/nova-skill/SKILL.md` não commitado não bloqueia
a regeneração, e o gerador vai criar wrappers para ele); o pathspec ignora edições fora de
`VERSION`/`skills/`. Os dois pontos cegos vão no cabeçalho de `update.sh`, seguindo a regra que o
catálogo já impõe aos checks de `scripts/` (*"The uncovered part is declared, not implied"*,
`openspec/specs/skills-catalog/spec.md:487`).

### D3 — A falha do gerador sai do `&&`

`bash generate.sh` passa a rodar como comando próprio, com a saída capturada e impressa só em caso
de falha. Sob `set -e`, um comando que falha à esquerda de `&&` não aborta o script — probado:
`f >/dev/null && echo ok; echo after` imprime `after` e sai 0. O `if`/`else` explícito devolve o
exit code e a saída do erro.

### D4 — `install.sh` valida `--tool` no parse, com `${2:-}`

A lista de valores suportados vira uma variável única (`SUPPORTED_TOOLS`) usada pela validação,
pela mensagem de erro e pelo `--help`, para que as três não divirjam. A validação roda logo depois
do loop de argumentos, antes de `command -v git` e do clone. `--tool` sem valor cai em `${2:-}`
vazio e produz erro de uso, não `unbound variable`.

### D5 — Os dois scripts dão a mesma mensagem de divergência, com o detalhe do git indentado

`git -c advice.diverging=false pull --ff-only --quiet` com stderr capturado. Na falha, o script
imprime a própria mensagem e a dica (`cd ~/ai-skills && ./update.sh --force`), e só então o stderr
do git, indentado, como detalhe. O `advice.diverging=false` suprime as nove linhas de `hint:` que o
git 2.47.3 emite antes do `fatal:`; o `fatal:` fica, porque num erro de rede ele é a única
informação útil, e indentado sob a mensagem própria não é mais "cru".

### D6 — O teste de fumaça clona de um bare local construído a partir do HEAD

`scripts/smoke-install-scripts.sh` cria `origin.git` com `git init --bare`, aponta `HEAD` para
`refs/heads/master` explicitamente (não depende de `init.defaultBranch`, que num `HOME` vazio já é
`master` — probado — mas no runner pode não ser) e faz `git push <bare> HEAD:refs/heads/master` a
partir do checkout. Isso funciona tanto num branch local quanto no HEAD destacado que o
`actions/checkout` produz num `pull_request`. `install.sh` ganha `AI_SKILLS_REPO_URL` como override
do `REPO_URL`, documentado no cabeçalho; sem a variável o comportamento é o de hoje. A alternativa
— `sed` sobre o script antes de testá-lo — testaria outro script.

Cada caso roda com `HOME=<tmp>/home-<caso>` exportado só para aquele processo; `~/.claude`,
`~/.codex` e a rede não são tocados. Os commits de "upstream" e "local" usam
`-c user.name -c user.email`, porque o `HOME` falso não tem `.gitconfig`.

### D7 — O teste imprime a matriz como contagens

Cada caso termina em `PASS`/`FAIL` com o motivo, e o resumo final separa "tinha de recusar e
recusou" de "tinha de passar e passou", em `n/n`, que é o formato que o grupo de simulação do rito
pede.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Um check declara o que não cobre | `skills-catalog` (spec do repositório) + `verify-before-claiming` | already canonical — os cabeçalhos dos scripts só aplicam a regra |
| Prova observada, não esperada, antes de declarar entrega | `verify-before-claiming` | already canonical — citado no grupo de simulação de `tasks.md` |
| Identificadores, nomes de arquivo e chaves em inglês | `code-locale` | already canonical — `smoke-install-scripts.sh`, `AI_SKILLS_REPO_URL`, `SUPPORTED_TOOLS` seguem o glossário da issue #113 |
| Fallback e degradação de dependência externa | `backend-resilience` | não se aplica: nada aqui chama dependência de runtime; as guardas são de estado local |

Nenhuma skill do catálogo é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **Pular a regeneração pode passar despercebido** num `update.sh` rodado via `curl | bash` sem
  olhar a saída. Mitigação: a mensagem lista os arquivos sujos e o comando que limpa; o resumo
  final do script continua imprimindo a versão, e a regeneração volta no próximo update limpo.
- **Um `skills/` com arquivo novo não rastreado regenera mesmo assim** (D2). Aceito: o resultado é
  um wrapper a mais, não um arquivo rastreado corrompido; e está declarado no cabeçalho.
- **O teste de fumaça depende de `git push` local para um bare** e de `generate.sh` rodando dentro
  do clone. Se o `generate.sh` do HEAD estiver quebrado, o caso "update limpo" falha — o que é
  correto, porque o step *Wrappers in sync* já teria falhado antes.
- **`AI_SKILLS_REPO_URL` é uma superfície nova em `install.sh`.** Aceito: sem a variável nada
  muda, e ela está documentada no cabeçalho como o gancho do teste.

## Open Questions

Nenhuma. Os pontos que poderiam virar achismo — o texto do `fatal:` do git, o comportamento do
`&&` sob `set -e`, o `unbound variable`, o filtro do `--porcelain` — foram probados e estão em
`tasks.md` com comando e saída.
