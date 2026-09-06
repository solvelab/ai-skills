## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `e7f5fe8` (topo de `master`, 2026-09-06):

      - `generate.sh:84-90` — comentário e as duas variáveis `REPO_BLOB_URL`/`REPO_TREE_URL`;
        `:142-206` — o laço por skill; `:189` — `sed` do Cursor sobre `](references/`; `:192-200` —
        bloco `# --- GitHub Copilot ---`, com `:196` escrevendo
        `[SKILL.md](../../skills/${name}/SKILL.md)` e `:199` já usando `${REPO_TREE_URL}` para
        `references/`; `:168` — Codex `@../../skills/${name}/SKILL.md` (include lido no lugar, fora
        deste item).
      - `install.sh` — 216 linhas; `:23-24` "the README runs this script via `curl | bash`";
        `:173-187` — `if [ -d "$INSTALL_DIR" ]` → pull (`:178-183`), `else` → `git clone`; o bloco de
        pull só roda sobre clone existente.
      - `update.sh` — 104 linhas; `:20-21` mesma nota de `curl | bash`; `:46-49` exige
        `$INSTALL_DIR/.git`; `:56-69` — `--force` → `reset --hard`, senão o bloco de pull
        (`:63-68`), idêntico ao de `install.sh:178-183` linha a linha.
      - `scripts/smoke-install-scripts.sh` — 310 linhas, 17 casos; `:103` clona de um bare feito do
        `HEAD`; `:265-291` — casos 13 (`update.sh` divergido) e 14 (`install.sh` divergido), cada um
        com `want_out` das frases, nenhum comparando as duas saídas; `:302-310` matriz.
      - `scripts/` — sem subdiretório `lib/` (`ls scripts/lib` → *No such file or directory*).
      - `scripts/validate-skills.py:488-534` — `CATALOG_ONLY_ROOTS` inclui `copilot/`;
        `REPO_URL_PREFIX = "https://github.com/solvelab/ai-skills/"` e a recomendação
        `blob/master/<path>` (C12); nenhum check lê o conteúdo de `copilot/instructions/`.
      - `.github/workflows/ci.yml:175-179` — step *Distribution scripts smoke test* roda
        `bash scripts/smoke-install-scripts.sh`.
      - `README.md:113-119` (`curl … install.sh | bash`, `bash -s -- --tool …`), `:150-151` (nota
        *"the SKILL.md link still expects the clone"* + `cp … .github/instructions/`), `:162-171`
        (`curl … update.sh | bash`, `cd ~/ai-skills && ./update.sh [--force]`), `:195` (`install.sh`
        / `update.sh` seguem *Latest `master`*).
      - `openspec/specs/skills-authoring/spec.md:639-698` — requisito modificado; `:655-656` a regra
        só de `references/`; `:679-684` cenário *Cursor or Copilot copy*.
      - `openspec/specs/skills-catalog/spec.md:1266-1339` — *Distribution scripts refuse what they
        cannot honor*; cenário *A diverged clone is refused with the recovery hint, by both scripts*.
      - `openspec/changes/archive/2026-09-05-define-cross-skill-references/proposal.md` (R5 só
        converteu `references/`), `…/2026-09-04-harden-distribution-scripts/tasks.md:100-110` (E.4:
        "não há de onde carregar um arquivo comum"), `…/2026-09-04-close-ci-gate-holes/*` (modelo).
      - `openspec/schemas/skills-rite/{schema.yaml,templates/*.md}`, `openspec/config.yaml`.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      openspec --version   -> 1.6.0
      gh --version         -> gh version 2.98.0 (2026-08-20)
      git --version        -> git version 2.47.3
      ls skills | wc -l    -> 36
      ls copilot/instructions | wc -l -> 36
      grep -c '\.\./\.\./skills' copilot/instructions/*.md | awk -F: '{s+=$2} END {print s}'   -> 36
      cat copilot/instructions/backlog.instructions.md
      -> Follow the instructions in [SKILL.md](../../skills/backlog/SKILL.md)
      -> Reference files: [references/](https://github.com/solvelab/ai-skills/tree/master/skills/backlog/references/)
      ```

      ```
      curl -sI https://github.com/solvelab/ai-skills/blob/master/skills/backlog/SKILL.md | head -1
      -> HTTP/2 200
      -> date: Sun, 06 Sep 2026 05:41:59 GMT   x-github-request-id: A7DD:D301E:1863940:1D3030E:6A9CFD27
      ```

      ```
      bash scripts/smoke-install-scripts.sh          (baseline, e7f5fe8, antes de qualquer edição)
      -> smoke: origin=… head=e7f5fe8 skills=36
      -> smoke: 17/17 cases passed — refusals that had to fire: 6/6, paths that had to succeed: 11/11
      ```

      ```
      bash -c 'set -u; echo "BASH_SOURCE=[${BASH_SOURCE[0]:-}] dollar0=[$0]"'
      -> BASH_SOURCE=[] dollar0=[bash]        (script que não vem de arquivo: sem diretório do script)
      ```

      ```
      openspec new change extend-install-form-links --schema skills-rite
      -> Created change 'extend-install-form-links' at openspec/changes/extend-install-form-links/
      -> (só .openspec.yaml; artefatos escritos a partir de openspec/schemas/skills-rite/templates/)
      openspec validate extend-install-form-links --strict
      -> Change 'extend-install-form-links' is valid
      ```

- [x] E.3 O que não pôde ser probado

      - `curl … | bash` de verdade (README 113-119, 162) não foi executado: o sandbox desta sessão
        recusa `bash` lendo script de stdin. O análogo probado é `bash -c` (E.2): `BASH_SOURCE[0]`
        vazio quando o script não vem de arquivo, que é o que sustenta D2 (ler o arquivo compartilhado
        do clone, não da pasta do script). O smoke test roda `bash "$ROOT/install.sh"`, por arquivo.
      - O comportamento sobre um clone **realmente** anterior a esta versão (instalado de uma release
        publicada) não foi medido; o smoke test simula o estado apagando `scripts/lib/git-sync.sh` do
        clone (caso 16), que é observacionalmente o mesmo para o guard de D3.
      - O que o GitHub Copilot faz ao seguir uma URL num `.instructions.md` não foi observado; a
        issue fixa o escopo em "só o link", e o cenário do spec afirma que a URL resolve (200), não o
        que o assistente faz com ela.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #173 pediu e nada além. Notados pelo caminho e **não** feitos, como
      follow-up:

      - `README.md:150` — a nota *"(references/ resolve through the same repository URL; the SKILL.md
        link still expects the clone)"* fica desatualizada depois desta change; `README.md` não está
        entre os arquivos do item. A árvore em `README.md:466-472` e a tabela de `scripts/` em `:490`
        também não citam `scripts/lib/git-sync.sh`.
      - `generate.sh:10-11` e `:84-88` (cabeçalho e comentário fora do bloco do Copilot) ainda dizem
        que só `references/` aponta para o repositório; o item entrega só o bloco do Copilot.
      - `codex/skills/<name>/AGENTS.md` usa `@../../skills/…` — include lido no lugar, não copiado; a
        issue não o cita.
      - `install.sh` e `update.sh` ainda duplicam a checagem de `git` instalado e o guard de D3
        (quatro linhas); a issue pede o bloco de pull.

## 2. generate.sh — link do SKILL.md por URL no wrapper Copilot (D1)

- [x] 2.1 `generate.sh:199` escreve `[SKILL.md](${REPO_BLOB_URL}/skills/${name}/SKILL.md)`; os 36
      wrappers regenerados; segundo `bash generate.sh` sem diff; nenhum outro wrapper muda

      ```
      bash generate.sh   -> Generated wrappers for 36 skills: … Generated 10 category plugins in plugins/
      git status --porcelain --untracked-files=all | <dir> | uniq -c   -> 36 copilot/instructions, 1 generate.sh
      bash generate.sh (2ª vez); git status --porcelain --untracked-files=all | wc -l   -> 37   (mesmos 37; nada novo)
      git diff --stat | tail -1   -> 37 files changed, 40 insertions(+), 37 deletions(-)
      ```

- [x] 2.2 `grep -c '\.\./\.\./skills' copilot/instructions/*.md` → 0 em todos; `curl -sI` de um link
      regenerado → 200

      ```
      grep -c '\.\./\.\./skills' copilot/instructions/*.md | grep -vc ':0$'   -> 0   (36 arquivos, todos :0)
      cat copilot/instructions/backlog.instructions.md
      -> # backlog
      -> Follow the instructions in [SKILL.md](https://github.com/solvelab/ai-skills/blob/master/skills/backlog/SKILL.md)
      -> Reference files: [references/](https://github.com/solvelab/ai-skills/tree/master/skills/backlog/references/)
      curl -sI https://github.com/solvelab/ai-skills/blob/master/skills/execute-backlog/SKILL.md | head -1   -> HTTP/2 200
      ```

## 3. Bloco de pull compartilhado (D2, D3)

- [x] 3.1 `scripts/lib/git-sync.sh` com `pull_ff_only <dir>`: o pull `--ff-only` com
      `advice.diverging=false`, a mensagem de divergência, a dica de `--force` e o `git:` indentado —
      texto byte a byte igual ao que os dois scripts imprimiam

      Em `fac8b54` (2026-09-06); os casos 13 e 14 do smoke continuam afirmando as mesmas frases
      (`Fast-forward failed`, `./update.sh --force`, `git: fatal: Not possible to fast-forward`,
      sem `hint:`, mensagem própria antes do `fatal:`) e passam sem alteração de expectativa:

      ```
      grep -n 'Fast-forward failed\|update.sh --force\|git: %s' install.sh update.sh scripts/lib/git-sync.sh
      -> scripts/lib/git-sync.sh:27:        echo "  ❌ Fast-forward failed — local changes diverge from origin."
      -> scripts/lib/git-sync.sh:28:        echo "     Re-run with --force to discard them: cd ~/ai-skills && ./update.sh --force"
      -> scripts/lib/git-sync.sh:29:        [ -z "$pull_err" ] || printf '     git: %s\n' "$pull_err"
      -> update.sh:7 e :87 — só o texto de uso e a dica da regeneração pulada, não o bloco de pull
      bash -n install.sh && bash -n update.sh && bash -n scripts/lib/git-sync.sh   -> syntax ok
      ```

- [x] 3.2 `install.sh` (re-run sobre clone) e `update.sh` (sem `--force`) carregam
      `$INSTALL_DIR/scripts/lib/git-sync.sh` e chamam `pull_ff_only "$INSTALL_DIR" || exit 1`;
      arquivo ausente → recusa própria com `cd ~/ai-skills && ./update.sh`; cabeçalhos atualizados

      ```
      sed -n '/SYNC_LIB=/,/pull_ff_only/p' install.sh > a; … update.sh > b; diff a b
      -> loader blocks identical (diff empty), 8 lines
      bash scripts/smoke-install-scripts.sh   (fac8b54)
      -> PASS  [refuse] install + update: clone without scripts/lib/git-sync.sh (exit 1 with hint)
      ```

- [x] 3.3 `diff` das mensagens de divergência entre `install.sh` e `update.sh` vazio (o bloco literal
      não existe mais em nenhum dos dois)

      ```
      grep -c 'Fast-forward failed' install.sh update.sh scripts/lib/git-sync.sh
      -> install.sh:0   update.sh:0   scripts/lib/git-sync.sh:1
      bash scripts/smoke-install-scripts.sh
      -> PASS  [refuse] install + update: divergence message byte-identical from both scripts
      ```

## 4. Smoke test (D4)

- [x] 4.1 Caso novo: o bloco `Fast-forward failed … git:` recortado das saídas dos casos 13 e 14 é
      byte a byte igual e tem três linhas

      Caso 14b (`scripts/smoke-install-scripts.sh`, depois do caso 14): `divergence_block()` =
      `sed -n '/Fast-forward failed/,/^     git: /p'` sobre `UPDATE_DIVERGED_OUT` e
      `INSTALL_DIVERGED_OUT`; três `want`: 3 linhas em cada, `test "$a" = "$b"`. Provado que reprova:
      `install.sh` mutado na árvore de trabalho (sem o guard do arquivo e com um bloco próprio de
      divergência com outra dica) e o smoke rodado de novo:

      ```
      bash scripts/smoke-install-scripts.sh   (install.sh mutado, não commitado)
      -> FAIL  [refuse] install + update: divergence message byte-identical from both scripts
      ->         - install.sh block is three lines (message, hint, git detail)
      ->         - the two blocks are byte-identical
      -> smoke: 17/19 cases passed — refusals that had to fire: 6/8, paths that had to succeed: 11/11
      cp install.sh.bak install.sh; git status --porcelain | wc -l   -> 0
      ```

- [x] 4.2 Caso novo: clone sem `scripts/lib/git-sync.sh` → `install.sh` e `update.sh` recusam com a
      dica, `HEAD` intocado; fixture restaurada

      Caso 16 (depois do caso 15): `rm "$INSTALL/scripts/lib/git-sync.sh"`, os dois scripts com
      `want_rc 1`, `want_out "scripts/lib/git-sync.sh not found"`, `want_out "cd ~/ai-skills &&
      ./update.sh"`, `want_no_out "No such file or directory"`, `HEAD` igual antes/depois; restaurado
      com `git checkout -- scripts/lib/git-sync.sh`. Na mesma rodada mutada de 4.1 (guard removido):

      ```
      -> FAIL  [refuse] install + update: clone without scripts/lib/git-sync.sh (exit 1 with hint)
      ->         - output lacks: scripts/lib/git-sync.sh not found
      ->         - output lacks: cd ~/ai-skills && ./update.sh
      ->         - output must not contain: No such file or directory
      ```

- [x] 4.3 Os 17 casos anteriores continuam verdes com as mesmas expectativas; cabeçalho declara que o
      arquivo compartilhado é lido do clone (`HEAD`), não da árvore de trabalho

      Nenhum `want*` dos casos 1-15 foi editado (diff do arquivo: cabeçalho, duas capturas de `$OUT`,
      os casos 14b e 16). Baseline em `e7f5fe8`: 17/17 (E.2); em `fac8b54`:

      ```
      bash scripts/smoke-install-scripts.sh
      -> smoke: origin=… head=fac8b54 skills=36
      -> PASS ×19
      -> smoke: 19/19 cases passed — refusals that had to fire: 8/8, paths that had to succeed: 11/11
      sed -n 27,31p scripts/smoke-install-scripts.sh
      -> # output, which the "Wrappers in sync" CI step guarantees for the same HEAD. The shared pull block
      -> # (scripts/lib/git-sync.sh) is read by both scripts from the CLONE, i.e. from this checkout's HEAD:
      ```

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi exercitado pelo caminho real — `bash scripts/smoke-install-scripts.sh`, como
      o CI o invoca — com a saída observada registrada; um wrapper Copilot regenerado citado; a linha
      de status do `curl`

      Tudo em `fac8b54` (2026-09-06), no worktree, tree limpo antes e depois (`git status --porcelain
      | wc -l -> 0`). O smoke test é o ponto de entrada que `.github/workflows/ci.yml:179` invoca:

      ```
      bash scripts/smoke-install-scripts.sh
      -> smoke: origin=/tmp/ai-skills-smoke.hRHQ1t/origin.git head=fac8b54 skills=36
      -> PASS  [accept] install: default (claude symlinks)
      -> PASS  [accept] install: idempotent re-run (0 linked / 36 up to date)
      -> … (casos 3-13 PASS, texto idêntico ao baseline de e7f5fe8)
      -> PASS  [refuse] update: diverged, no --force (exit 1 with hint)
      -> PASS  [refuse] install: re-run over a diverged clone (exit 1 with hint)
      -> PASS  [refuse] install + update: divergence message byte-identical from both scripts
      -> PASS  [accept] update: diverged, --force (reset to origin)
      -> PASS  [refuse] install + update: clone without scripts/lib/git-sync.sh (exit 1 with hint)
      -> smoke: 19/19 cases passed — refusals that had to fire: 8/8, paths that had to succeed: 11/11
      ```

      O caso 2 (re-run idempotente) e o 14 (re-run divergido) são `install.sh` carregando
      `pull_ff_only` do clone; o 9-11 e o 13 são `update.sh` fazendo o mesmo — nenhum deles mudou de
      expectativa.

      Wrapper regenerado, pelo caminho do usuário (`cat` do arquivo que o README manda copiar):

      ```
      cat copilot/instructions/backlog.instructions.md
      -> # backlog
      ->
      -> Follow the instructions in [SKILL.md](https://github.com/solvelab/ai-skills/blob/master/skills/backlog/SKILL.md)
      ->
      -> Reference files: [references/](https://github.com/solvelab/ai-skills/tree/master/skills/backlog/references/)
      curl -sI https://github.com/solvelab/ai-skills/blob/master/skills/execute-backlog/SKILL.md | head -1
      -> HTTP/2 200
      ```

      O runner completo (`generate.sh` + tree limpo, versão, frontmatter, validate-skills e selftest,
      detectores de locale e hooks, scan-secrets e selftest, higiene e selftest, rite com
      `Spec-rite: extend-install-form-links`, evidence/spec-rite selftests, smoke, plugin validate,
      `openspec validate --strict`): 20 linhas `PASS`, `dirty-after: 0`.

- [x] S.2 Matriz de casos medida, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | Tinha de disparar e disparou | 8/8 | recusas do smoke em `fac8b54`: `--tool bogus` (1), `--tool` sem valor (1), bogus sobre clone (1), generate.sh falhando (1), update divergido (1), install divergido (1), mensagem byte-idêntica (1), clone sem `git-sync.sh` (1) |
      | Tinha de ficar mudo e ficou | 11/11 | caminhos de sucesso do smoke (install ×5, update ×6), idênticos ao baseline 11/11 de `e7f5fe8` |
      | Versão antiga passou onde a nova falha | 2/2 | `install.sh` mutado (bloco próprio de divergência, sem guard do arquivo): 17/19, os dois casos novos `FAIL` e só eles |
      | Link relativo restante | 0/36 | `grep -c '\.\./\.\./skills' copilot/instructions/*.md` → todos `:0` |
      | URL responde | 2/2 | `backlog` (E.2) e `execute-backlog` (2.2): `HTTP/2 200` |
      | Escape conhecido ficou mudo | 1/1 | o guard de D3 existe em dois lugares (loader de 8 linhas idêntico nos dois scripts, medido em 3.2); nenhum caso do smoke compara os dois loaders — o caso 16 prova cada um separadamente |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      - Na rodada mutada (4.1), o caso 14b reprovou com **duas** asserções, não uma: o `install.sh`
        mutado imprimiu o bloco do `pull_ff_only` (stdout) **e** o bloco próprio, então o recorte do
        `sed` devolveu seis linhas e "three lines" caiu junto com "byte-identical". Esperado era só a
        segunda; a primeira é redundante mas correta, e fica — é o guard contra dois recortes vazios.
      - `curl … | bash` real não foi executado (E.3); o análogo `bash -c` mostra `BASH_SOURCE`
        vazio, que é o fato que D2 usa. O CI roda o smoke por arquivo, como aqui.
      - Um clone anterior a esta versão re-executando `install.sh`/`update.sh` por `curl` passa a
        ser recusado com a dica (caso 16), onde antes fazia o pull — mudança de comportamento fora
        dos 17 casos medidos, declarada em `design.md` D3 e Risks, transitória por construção.
      - O loader de D3 (checagem `[ -f ]` + duas linhas de mensagem) fica duplicado nos dois
        scripts, por necessidade: não há de onde carregar o guard que verifica se há de onde carregar.
        É a única duplicação que a change deixa; registrada em E.4.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — **não se aplica**: nenhuma skill é tocada
      (`git diff --name-only master...HEAD` → 36 `copilot/instructions/*`, `generate.sh`,
      `install.sh`, `update.sh`, `scripts/lib/git-sync.sh`, `scripts/smoke-install-scripts.sh` e os
      cinco arquivos da change; nenhum caminho sob `skills/`); o gate de versão confirma:
      `validate-skill-version.py` → `0 findings (base origin/master, 0 skill(s) changed, 0 with
      content changes)`
- [x] Q.2 Conteúdo de skill tocado em inglês — não se aplica; o delta de spec, `git-sync.sh` e os
      cabeçalhos dos scripts estão em inglês, como o catálogo exige
- [x] Q.3 Gatilhos de descrição testáveis — não se aplica: nenhuma descrição de skill muda
- [x] Q.4 Sem doutrina duplicada: ver a tabela de Canonical Home em `design.md` (cinco linhas, todas
      *already canonical*); nenhuma skill editada; o texto da mensagem de divergência existe uma vez
      (3.3)
- [x] Q.5 Identificadores em inglês no que a change introduz — `pull_ff_only`, `pull_err`, `SYNC_LIB`,
      `git-sync.sh`, `divergence_block`, `UPDATE_DIVERGED_OUT`/`INSTALL_DIVERGED_OUT`,
      `UPDATE_MSG`/`INSTALL_MSG`, nomes dos casos (`code-locale`)

      ```
      git diff master...HEAD -- install.sh update.sh scripts generate.sh > diff173.patch   (215 linhas)
      python3 skills/code-locale/references/check-identifier-locale.py --diff - < diff173.patch
      -> findings: 0
      ```

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate extend-install-form-links --strict` verde e `scripts/validate-rite.sh`
      verde com `Spec-rite: extend-install-form-links`

      ```
      openspec validate extend-install-form-links --strict   -> Change 'extend-install-form-links' is valid   (openspec 1.6.0)
      printf '{"pull_request":{"body":"Closes #173\n\nSpec-rite: extend-install-form-links\n"}}' > event173.json
      GITHUB_EVENT_PATH=event173.json bash scripts/validate-rite.sh
      -> Totals: 3 passed, 0 failed (3 items)
      -> rite gate OK
      ```

- [x] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py` verde, 36 skills

      ```
      python3 scripts/validate-skills.py   -> skills checked: 36   findings: 0
      ls skills | wc -l                    -> 36
      python3 scripts/validate-repo-hygiene.py   -> repo hygiene: 0 findings
      claude plugin validate . --strict          -> ✔ Validation passed
      ```

- [x] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo — a composição
      não muda; `README.md` não está entre os arquivos do item, e a nota da linha 150 (*"the SKILL.md
      link still expects the clone"*) fica desatualizada: follow-up registrado em E.4 e como *Known
      gap* no PR
- [ ] V.4 `openspec archive extend-install-form-links --yes` em PR separado, depois do merge
