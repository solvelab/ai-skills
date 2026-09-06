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

- [ ] 3.1 `scripts/lib/git-sync.sh` com `pull_ff_only <dir>`: o pull `--ff-only` com
      `advice.diverging=false`, a mensagem de divergência, a dica de `--force` e o `git:` indentado —
      texto byte a byte igual ao que os dois scripts imprimiam
- [ ] 3.2 `install.sh` (re-run sobre clone) e `update.sh` (sem `--force`) carregam
      `$INSTALL_DIR/scripts/lib/git-sync.sh` e chamam `pull_ff_only "$INSTALL_DIR" || exit 1`;
      arquivo ausente → recusa própria com `cd ~/ai-skills && ./update.sh`; cabeçalhos atualizados
- [ ] 3.3 `diff` das mensagens de divergência entre `install.sh` e `update.sh` vazio (o bloco literal
      não existe mais em nenhum dos dois)

## 4. Smoke test (D4)

- [ ] 4.1 Caso novo: o bloco `Fast-forward failed … git:` recortado das saídas dos casos 13 e 14 é
      byte a byte igual e tem três linhas
- [ ] 4.2 Caso novo: clone sem `scripts/lib/git-sync.sh` → `install.sh` e `update.sh` recusam com a
      dica, `HEAD` intocado; fixture restaurada
- [ ] 4.3 Os 17 casos anteriores continuam verdes com as mesmas expectativas; cabeçalho declara que o
      arquivo compartilhado é lido do clone (`HEAD`), não da árvore de trabalho

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 O artefato foi exercitado pelo caminho real — `bash scripts/smoke-install-scripts.sh`, como
      o CI o invoca — com a saída observada registrada; um wrapper Copilot regenerado citado; a linha
      de status do `curl`
- [ ] S.2 Matriz de casos medida, em contagens: o que tinha de disparar e disparou, o que tinha de
      ficar mudo e ficou, escapes conhecidos que ficaram mudos
- [ ] S.3 O que escapou ou se comportou diferente do esperado é nomeado aqui — ou fica dito que nada
      escapou

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — não se aplica se nenhuma skill for tocada
      (medir com `git diff --name-only master...HEAD | grep -c '^skills/'`)
- [ ] Q.2 Conteúdo de skill tocado em inglês — não se aplica; o delta de spec e os cabeçalhos dos
      scripts são em inglês
- [ ] Q.3 Gatilhos de descrição testáveis — não se aplica: nenhuma descrição muda
- [ ] Q.4 Sem doutrina duplicada: ver a tabela de Canonical Home em `design.md`; nenhuma skill editada
- [ ] Q.5 Identificadores em inglês no que a change introduz — `pull_ff_only`, `SYNC_LIB`,
      `git-sync.sh`, nomes dos casos do smoke (`code-locale`), medido com o detector sobre o diff

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate extend-install-form-links --strict` verde e `scripts/validate-rite.sh`
      verde com `Spec-rite: extend-install-form-links`
- [ ] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py` verde, 36 skills
- [ ] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo — a composição
      não muda; a nota do README (linha 150) é follow-up (E.4)
- [ ] V.4 `openspec archive extend-install-form-links --yes` em PR separado, depois do merge
