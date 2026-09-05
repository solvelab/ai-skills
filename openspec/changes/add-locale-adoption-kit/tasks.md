## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `80ee53c` (`docs(openspec): arquiva as changes add-skill-version-gate e
      define-cross-skill-references`), topo de `master` em 2026-09-05:

      - `skills/code-locale/SKILL.md` — 211 linhas; `metadata.version: 1.3.1` na linha 17; a frase
        "a shipped detector a repository can wire into CI" em 33-34; *Reviewing a diff* em 121-146
        (o exemplo `git diff origin/main... | python3 references/check-identifier-locale.py --diff -`
        na 125); *Catching it at the write* em 176-193; *See also* em 201-210.
      - `skills/code-locale/references/check-identifier-locale.py` — 45,6 KB; `ALLOWLIST_FILE` na
        linha 98, `WAIVER_RE` na 99, `EXT_LANG` em 211-216, `load_english()` em 414-445 (resolve as
        listas por `Path(__file__).resolve().parent` e não falha quando faltam), `--no-english` em
        841 e 849; docstring 1-90 com *WHY --diff IS THE DEFAULT ADOPTION MODE* e os 17 KNOWN LIMITs.
      - `skills/code-locale/references/migration.md:16` — "Wire this into pre-commit and CI".
      - `claude/global/hooks/locale-rite.py` — `CHECK_PATH` por `parents[3]`, `WRITE_TOOLS`,
        `written_text()`: a camada de sessão mede só o texto escrito pela ferramenta.
      - `README.md:306-347` — seção *The locale rite*: `PostToolUse` para `Write|Edit`, snippet do
        `settings.json`, "informs, never blocks".
      - `.github/workflows/ci.yml` — step *Skill content checks* (C9 via `validate-skills.py`),
        *Identifier-locale detector self-test*, o checkout com `fetch-depth: 0` e
        `persist-credentials: false` e o comentário que os justifica; job `validate` com
        `permissions: contents: read`.
      - `scripts/validate-skills.py` — C1 (`check_refs`, 77-135: links e inline `references/...`
        resolvidos contra o diretório da skill), C3 (`check_blocks`, 136-166: fences `bash` com `<`,
        `$(` ou `${` são pulados; fences `yaml` passam por `yaml.safe_load_all`), C10 (300-357,
        `description` ≤ 1024 no valor parseado), C11 (358-417: só `*.md` sob `references/` é
        julgado como órfão; `.sh` é "loaded by the markdown that names them"), C12 (419-492), C13.
      - `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py` (1-140),
        `scripts/validate-spec-rite.py` e `scripts/validate-skill-version.py` (1-60, `resolve_base`
        em 120-127) — o que os gates exigem e como resolvem a base fora do CI.
      - `generate.sh:140-200` — Cursor reescreve `](references/` para a URL do repositório;
        `plugins/` copia `references/` inteira (`ls plugins/workflow/skills/code-locale/references/`
        -> 8 arquivos, os mesmos de `skills/`).
      - `openspec/specs/skills-catalog/spec.md:647-698` — o requisito *Code locale has a canonical
        home* que o delta modifica (copiado por inteiro); `:700-725` *A shipped enforcement script
        declares what escapes it*.
      - `openspec/changes/archive/2026-09-04-add-hook-selftests/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md`; `2026-09-05-add-skill-version-gate/{proposal,design}.md` —
        modelo de estilo da casa.
      - `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md` e `schema.yaml`.
      - Issue #139 (`gh issue view 139 --json body`): escopo, FR1-FR3, TR1-TR3, os quatro critérios
        de aceite, o glossário (`pre-commit-locale.sh`, `ci-step.md`), o veredito
        `add-locale-adoption-kit`.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      python3 --version                -> Python 3.14.5
      /usr/bin/git --version           -> git version 2.47.3
      dpkg -s bash | grep ^Version     -> Version: 5.2.37-2+b9
      openspec --version               -> 1.6.0
      cat VERSION                      -> 2.21.0
      git tag --list 'v*' --sort=-v:refname | head -1   -> v2.21.0
      which shellcheck                 -> shellcheck not found
      which act                        -> act not found
      ```

      O detector em `--diff` sobre um fixture (arquivo novo, `def calcular_total(itens)`), pelo
      caminho e por stdin `-`:

      ```
      python3 skills/code-locale/references/check-identifier-locale.py --diff fixtures/pt.diff; echo rc=$?
      -> orders.py:1: calcular_total  [pt-verb: 'calcular']
      ->     machine layer must be English (code-locale). If this name is correct as written, add a reason:
      ->       # locale-ok: <why this term has no faithful English name>
      ->     or grandfather it in .identifier-locale-allow:
      ->       calcular_total
      -> orders.py:1: itens  [en-unknown: 'itens']   [...] advisory: this finding does not fail the run
      -> findings: 1
      -> rc=1
      python3 ... --diff - < fixtures/pt.diff          -> findings: 1  rc=1   (saída idêntica)
      python3 ... --diff fixtures/en.diff              -> findings: 0  rc=0   (def compute_total(items))
      ```

      O detector copiado **sozinho** para um diretório vazio (o que um `curl` do arquivo único dá):

      ```
      cp skills/code-locale/references/check-identifier-locale.py $SCR/standalone/ && python3 $SCR/standalone/check-identifier-locale.py --diff fixtures/pt.diff
      -> orders.py:1: calcular_total  [pt-verb: 'calcular']
      -> orders.py: orders  [path-en-unknown: 'orders']   (novo: a lista inglesa não está ao lado)
      -> findings: 1
      ->   en-unknown: 3 segment(s) not in the English word list — advisory
      -> rc=1
      ```

      A raw URL na tag responde, e o detector é byte a byte o mesmo da tag e do HEAD:

      ```
      curl -sI https://raw.githubusercontent.com/solvelab/ai-skills/v2.21.0/skills/code-locale/references/check-identifier-locale.py | head -1
      -> HTTP/2 200
      /usr/bin/git show v2.21.0:skills/code-locale/references/check-identifier-locale.py | sha256sum
      -> 4e72af47225d6259f6b69db638af6db6c586c7ee6800e401941e08c223413ff2  -
      sha256sum skills/code-locale/references/check-identifier-locale.py
      -> 4e72af47225d6259f6b69db638af6db6c586c7ee6800e401941e08c223413ff2
      /usr/bin/git diff --stat v2.21.0 HEAD -- skills/code-locale/references/{check-identifier-locale.py,english-words.txt.gz,programming-words.txt,not-english.txt}
      -> (vazio) diff-rc=0
      ```

      Scaffold da change com o schema do repositório:

      ```
      openspec new change add-locale-adoption-kit --schema skills-rite
      -> Created change 'add-locale-adoption-kit' at openspec/changes/add-locale-adoption-kit/
      -> Schema: skills-rite
      openspec validate add-locale-adoption-kit --strict
      -> Change 'add-locale-adoption-kit' is valid
      ```

- [x] E.3 O que não pôde ser probado

      Dois itens. `shellcheck` e `act` não estão instalados nesta máquina (`which` acima), então o
      hook é verificado com `bash -n` e o step de CI é validado rodando o **mesmo comando** do bloco
      `run:` num clone local com `origin/main` no lugar de `origin/${{ github.base_ref }}` — a
      simulação (S.1) declara isso por extenso, como o critério de aceite da issue pede. O que essa
      substituição não prova: que o runner resolve `github.base_ref` e faz o checkout do merge
      commit do PR com `fetch-depth: 0` — isso vem da doc do Actions e do precedente do `ci.yml`
      deste repositório, que já depende dos dois.

      A versão do bash foi lida do pacote (`dpkg -s bash`), não de `bash --version`: o sandbox desta
      sessão recusa invocar `bash` com argumentos computados. Mesmo pacote, mesma versão.

- [x] E.4 Checagem de escopo

      A change faz só o que a issue #139 pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up:

      - O detector copiado sozinho não falha sem as listas de palavras, mas reporta todo segmento
        como `en-unknown` (E.2). O kit contorna com `--no-english` no modo download e documenta; um
        aviso do próprio detector quando `english-words.txt.gz` não está ao lado seria uma edição no
        detector, fora desta issue.
      - `SKILL.md:125` exemplifica `git diff origin/main...` sem `...HEAD`; forma válida, mas o step
        de CI usa a forma com `HEAD` explícito. Não harmonizado: a seção nova aponta para a doutrina,
        não a reescreve.
      - `README.md:558` (linha do índice de `code-locale`) diz "any project can wire into pre-commit"
        e continuaria verdadeiro; a issue exclui `README.md` do escopo e nada foi tocado lá.
      - Uma opção `--git-hooks <repo>` no `install.sh` — rejeitada na própria issue.

## 2. Hook de pre-commit

- [ ] 2.1 `skills/code-locale/references/pre-commit-locale.sh`: cabeçalho com instalação (`cp` para
      `.git/hooks/pre-commit` ou `core.hooksPath`), ordem de localização do detector (D2), pin
      `v2.21.0` + sha256 e a frase de bump, a lista do que não cobre (`--no-verify`, extensões fora
      de `EXT_LANG`, conteúdo existente, tier consultivo no modo download); corpo que roda
      `git diff --cached --no-color | python3 <detector> --diff -` e sai 1 com os achados mais o
      rodapé das três saídas (D4); `python3` ausente recusa (D3)
- [ ] 2.2 `bash -n` limpo; o detector sobre o próprio hook (`.sh` está em `EXT_LANG`) reporta
      `findings: 0`

## 3. Step de CI

- [ ] 3.1 `skills/code-locale/references/ci-step.md`: job copiável (`pull_request`,
      `permissions: contents: read`, `checkout@v5` com `fetch-depth: 0` e
      `persist-credentials: false`, `curl -fsSL` na tag `v2.21.0` + `sha256sum -c`,
      `git diff origin/${{ github.base_ref }}...HEAD | python3 check-identifier-locale.py --diff -`);
      o pin, o `fetch-depth`, o gatilho e o `pipefail` explicados (D5); o que o step não cobre
- [ ] 3.2 O bloco `yaml` parseia (C3 via `validate-skills.py`)

## 4. Seção da skill e wrappers

- [ ] 4.1 `skills/code-locale/SKILL.md`: seção *Wire it in one minute* com os dois links relativos
      e a tabela de três camadas (hook de sessão / pre-commit / CI: o que pega, o que deixa passar);
      `metadata.version` `1.3.1 → 1.4.0`; description intacta (mesmos gatilhos, ≤ 1024 chars)
- [ ] 4.2 `bash generate.sh` duas vezes; a segunda sem diff; os dois arquivos novos aparecem em
      `plugins/workflow/skills/code-locale/references/`

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 O artefato foi exercitado pelo caminho real: hook instalado em `.git/hooks/pre-commit` de
      um repositório git de rascunho, `git commit` recusado com o achado, aceito com `# locale-ok:`;
      o comando do step de CI rodado sobre um clone com `origin/main` (declarado em E.3); `bash -n`;
      `shellcheck` ausente e dito
- [ ] S.2 Matriz de casos medida, em contagens
- [ ] S.3 O que escapou ou se comportou diferente do esperado — ou declaração de que nada escapou

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em `skills/code-locale/SKILL.md`: name == diretório, description
      folded, author solvelab, semver `1.4.0`, category `process`, license MIT, compatibility
- [ ] Q.2 Conteúdo tocado em inglês (catalog locale): `SKILL.md`, `pre-commit-locale.sh`,
      `ci-step.md` — sem comentário em português
- [ ] Q.3 Gatilhos da description testáveis e sem colisão — a description não muda
- [ ] Q.4 Sem doutrina duplicada: a seção nova e os dois arquivos apontam para *Reviewing a diff* e
      para o docstring do detector (tabela de Canonical Home em `design.md`)
- [ ] Q.5 Identificadores em inglês no que a change introduz (`LOCALE_CHECK`, `LOCALE_CHECK_TAG`,
      `LOCALE_CHECK_SHA256`, funções e ids de step); o detector sobre os arquivos novos

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-locale-adoption-kit --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage — a composição
      não muda; `README.md` fora do escopo por decisão da issue
- [ ] V.4 `openspec archive add-locale-adoption-kit --yes` after all groups above are `[x]` — PR
      separado, como o repositório já faz
