## Context

Lido em `e7f5fe8` (2026-09-06):

- `generate.sh:84-90` — o comentário que justifica `REPO_BLOB_URL`/`REPO_TREE_URL`: os wrappers Cursor
  e Copilot são os dois outputs que o README manda **copiar** para o projeto, então um caminho
  relativo à árvore morre ao sair do checkout. `generate.sh:189` aplica isso ao Cursor via `sed` sobre
  `](references/`; `generate.sh:199` aplica ao `references/` do Copilot; `generate.sh:196` escreve o
  link do `SKILL.md` ainda relativo.
- `install.sh:173-187` — `if [ -d "$INSTALL_DIR" ]` → bloco de pull (176-183); `else` → `git clone`.
  O bloco de pull só roda quando o clone existe. `install.sh:23-24` e `update.sh:20-21`: os dois rodam
  por `curl | bash` (README linhas 113-119 e 162), onde `${BASH_SOURCE[0]}` não aponta para nada útil.
- `update.sh:46-49` — exige `$INSTALL_DIR/.git`; `56-69` — `--force` faz `reset --hard`, senão o bloco
  de pull (61-68), idêntico ao de `install.sh` linha a linha.
- `scripts/smoke-install-scripts.sh` — 17 casos; o caso 13 (`update.sh` divergido) e o 14
  (`install.sh` divergido) afirmam cada um a **presença** das frases, nunca a igualdade entre os dois;
  o fixture clona de um bare construído a partir do `HEAD` do checkout (linha 103), então o que o
  clone carrega é o que está commitado.
- `openspec/specs/skills-authoring/spec.md:639-698` — o requisito modificado; `:655-656` é a regra
  que cobre só `references/`.
- `openspec/specs/skills-catalog/spec.md:1266-1339` — *Distribution scripts refuse what they cannot
  honor*; o cenário *A diverged clone is refused with the recovery hint, by both scripts* já pede a
  mesma mensagem nos dois scripts.

## Goals / Non-Goals

**Goals**

- Um `copilot/instructions/<name>.instructions.md` copiado sozinho resolve o link do `SKILL.md`.
- O bloco de pull existe uma vez; a igualdade da mensagem é medida, não presumida.
- Os 17 casos do smoke test continuam verdes sem alteração de expectativa.

**Non-Goals**

- Mudar o que o Copilot ou o Cursor carregam (fora de escopo pela issue): só o link.
- Tocar `codex/skills/<name>/AGENTS.md` (`@../../skills/…` é um include lido no lugar, não copiado).
- Tocar `README.md` (não está entre os arquivos do item; follow-up em `tasks.md` E.4).
- Unificar o resto de `install.sh`/`update.sh` (checagem de `git`, cabeçalhos): a issue pede o bloco de
  pull.

## Decisions

### D1 — O link do `SKILL.md` no Copilot usa `REPO_BLOB_URL`, a mesma variável do `references/`

Uma linha: `[SKILL.md](${REPO_BLOB_URL}/skills/${name}/SKILL.md)`. A forma `blob/master` é a que
`validate-skills.py` (`REPO_URL_PREFIX`, C12) já recomenda e a que o Cursor já usa para arquivos;
`tree/master` fica para diretórios (`references/`). Probado: `curl -sI` da URL de `backlog` → `HTTP/2
200` (E.2).

Alternativa rejeitada: a URL da tag corrente (`blob/v2.30.0/…`), que a issue menciona ("na tag
corrente"). `generate.sh` roda no release **antes** da tag existir (o `chore(release)` regenera os
wrappers e só depois o semantic-release cria `vX.Y.Z`), então a URL apontaria para uma tag que ainda
não existe no momento em que é escrita, e `references/` já é `master` — misturar as duas formas no
mesmo arquivo seria pior que manter uma.

### D2 — O arquivo compartilhado é lido do clone que vai ser sincronizado, não da pasta do script

Os dois scripts rodam por `curl | bash`; nesse modo não há diretório do script. Mas o bloco de pull
só executa sobre um clone existente em `$INSTALL_DIR` — `install.sh` entra nele por
`[ -d "$INSTALL_DIR" ]`, `update.sh` exige `$INSTALL_DIR/.git` — e esse clone carrega `scripts/`.
Logo `$INSTALL_DIR/scripts/lib/git-sync.sh` é o único caminho que os dois conhecem em todo modo de
invocação, e é o mesmo arquivo nos dois. Na primeira instalação (sem clone) o bloco nem é necessário:
o `git clone` não tem o que fazer fast-forward.

Alternativas rejeitadas:

- **Here-doc / função inline nos dois scripts** — é a duplicação de hoje com outro nome; uma correção
  num não chega ao outro, exatamente o defeito medido em #113.
- **Ler de `$(dirname "${BASH_SOURCE[0]}")` quando existe, senão do clone** — dois caminhos de carga,
  duas versões possíveis do mesmo bloco numa só execução (o checkout de onde o script foi chamado
  contra o clone em `~/ai-skills`); o smoke test passaria a exercitar um arquivo que o usuário por
  `curl` nunca lê.
- **Bootstrap por `git show origin/master:scripts/lib/git-sync.sh` quando o arquivo falta** — executa
  conteúdo de `origin` **antes** de o guard de fast-forward decidir se o clone pode receber `origin`,
  e a população que precisa disso é transitória (clones entre esta versão e o primeiro update).

### D3 — Clone sem o arquivo: recusa com a dica de usar o updater que o clone carrega

Um clone instalado antes desta versão não tem `scripts/lib/git-sync.sh`. Nos dois scripts, o caminho
de pull checa `[ -f "$SYNC_LIB" ]` antes do `source` e, faltando, imprime a própria mensagem
(nomeando o arquivo e o motivo) com a recuperação `cd ~/ai-skills && ./update.sh` — o `update.sh`
antigo, presente nesse clone, ainda carrega o bloco inline, faz o fast-forward e traz o arquivo. Sem
o guard, `source` de arquivo inexistente morre sob `set -e` com o `No such file or directory` do
bash, sem dica — o caso "erro cru" que o requisito de `skills-catalog` proíbe.

O guard é a única linha de comportamento que fica em dois lugares (uma checagem de arquivo e uma
mensagem de duas linhas). O que a issue pede que exista uma vez — o pull, a mensagem de divergência,
a dica de `--force`, o detalhe do git — está só em `pull_ff_only`.

`update.sh --force` não carrega o arquivo: o `reset --hard` não passa pelo bloco de pull, e um clone
antigo precisa continuar podendo ser resetado.

### D4 — O smoke test mede a igualdade byte a byte, entre as saídas reais dos dois scripts

Os casos 13 e 14 já produzem as duas saídas sobre o mesmo clone divergido. O caso novo recorta de
cada uma o bloco de `Fast-forward failed` até a linha `git:` (três linhas) e afirma `test "$a" =
"$b"` mais o tamanho do bloco (três linhas, para que dois recortes vazios não passem por iguais).
Nenhum novo estado de fixture: reutiliza as saídas capturadas, e imprime os dois blocos quando
diverge. Um segundo caso apaga `scripts/lib/git-sync.sh` do clone e afirma que `install.sh` e
`update.sh` (sem `--force`) recusam com a dica de D3 e sem tocar o `HEAD`.

O cabeçalho do smoke test passa a declarar que o arquivo compartilhado é lido do clone — isto é, do
`HEAD` commitado, como já vale para `generate.sh` no caso 9 — e não da árvore de trabalho.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Um wrapper copiado sozinho referencia por URL do repositório | `skills-authoring` (spec, *Cross-skill references resolve in every install form*) | already canonical — o delta estende a regra ao link do `SKILL.md`; `generate.sh` só a implementa |
| Os scripts de distribuição recusam com mensagem própria, e os dois dão a mesma dica | `skills-catalog` (spec, *Distribution scripts refuse what they cannot honor*) | already canonical — o arquivo compartilhado é implementação; o smoke test mede o cenário existente |
| Um check declara o que não cobre | `skills-catalog` + `verify-before-claiming` | already canonical — cabeçalhos de `install.sh`, `update.sh`, `git-sync.sh` e do smoke test só estendem o próprio KNOWN LIMIT |
| Reusar antes de escrever; sem abstração especulativa | `lean-code` | already canonical — uma função, um arquivo, sem camada de "lib" genérica além do que os dois scripts usam |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — `pull_ff_only`, `SYNC_LIB`, `git-sync.sh`, nomes dos casos |

Nenhuma skill do catálogo é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **Re-run de `install.sh` ou `update.sh` por `curl` sobre um clone anterior a esta versão passa a
  recusar** (hoje faz o pull). → Mensagem própria com a recuperação de uma linha (D3); o `update.sh`
  do próprio clone continua funcionando; população transitória. Medido no smoke test (caso 16).
- **O smoke test exercita o `git-sync.sh` do `HEAD`, não o da árvore de trabalho.** → Já é assim
  para `generate.sh` (caso 9, header do smoke); declarado no cabeçalho; uma edição não commitada no
  arquivo é invisível ao smoke até o commit — o CI roda sobre commits, então o gate não perde nada.
- **A URL `blob/master` aponta para o `SKILL.md` mais novo, não para a versão que gerou o wrapper.**
  → Mesma escolha já feita para `references/` em #121; o wrapper Copilot é um ponteiro de uma linha,
  não conteúdo inlined, e o README diz que `install.sh`/`update.sh` seguem `master` (linha 195).
- **`source` de um arquivo do clone executa o que o clone carrega.** → É o mesmo nível de confiança
  de `bash "$INSTALL_DIR/generate.sh"`, que `update.sh:85` já executa do mesmo clone.

## Open Questions

Nenhuma. O que poderia virar achismo — se o bloco de pull roda sem clone (não roda), se a URL
responde (200), se os dois scripts rodam por `curl` (README 113-119 e 162) — foi lido ou probado e
está em `tasks.md` com comando e saída.
