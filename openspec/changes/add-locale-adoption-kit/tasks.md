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

      Probado no review de 2026-09-05, antes de editar (a hipótese "roda em qualquer bash" tinha sido
      testada só em 5.2). Imagens `bash:3.2` e `bash:4.3` estão nesta máquina (`docker images`):

      ```
      docker run --rm bash:3.2 bash -c 'set -u; EXTRA_ARGS=(); args=("${EXTRA_ARGS[@]}"); echo ok'
      -> bash: EXTRA_ARGS[@]: unbound variable          rc=127
      docker run --rm bash:3.2 bash -c 'set -u; EXTRA_ARGS=(); args=(${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}); echo "fixed ok n=${#args[@]}"'
      -> fixed ok n=0                                   rc=0
      docker run --rm bash:3.2 sh -c 'apk add --no-cache git python3 >/dev/null && git --version && python3 --version'
      -> git version 2.49.1 / Python 3.12.14            (o container consegue rodar o hook inteiro)
      git -c diff.external=<sh que sai 0> diff --cached --no-color | wc -c   -> 0
      git diff --cached --no-color   (após git mv orders.py relatorio.py)
      -> diff --git a/orders.py b/relatorio.py / similarity index 100% / rename from orders.py / rename to relatorio.py
      git -c diff.mnemonicPrefix=true diff --cached --no-color | grep '^+++'   -> +++ i/relatorio.txt
      git diff --cached --no-color --src-prefix=a/ --dst-prefix=b/ | grep '^+++'   -> +++ b/relatorio.txt
      PYTHONIOENCODING=utf-8:surrogateescape python3 <detector> --diff - < latin1.diff   -> findings: 1  (sem a variável: UnicodeDecodeError)
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

      Terceiro item, do review: o shell padrão de um `run:` (`bash -e {0}`) e o de `shell: bash`
      (`bash --noprofile --norc -eo pipefail {0}`) vêm da página *workflow syntax* do GitHub, não de
      um runner probado — por isso o `set -o pipefail` é explícito no bloco, e o efeito foi medido
      localmente com `bash -e -c` (S.1).

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
      - Ensinar o detector a medir o caminho num header `rename to` (hoje só em `--- /dev/null`,
        `check-identifier-locale.py:632-646`; o KNOWN LIMIT 12 diz "a rename appears as an add", o
        que só é verdade com `--no-renames`). O kit contorna com o flag nos dois artefatos (D7);
        a edição no detector fica fora desta issue.
      - `PYTHONIOENCODING` aparece como `en-unknown` consultivo quando o detector lê o próprio hook
        e o `ci-step.md` — é o nome da variável do Python; uma linha em `programming-words.txt`
        resolveria, fora desta issue.

## 2. Hook de pre-commit

- [x] 2.1 `skills/code-locale/references/pre-commit-locale.sh` (217 linhas; commit `79a171b`, corrigido
      no review em `4c82e0a`): cabeçalho com instalação (`cp` para `.git/hooks/pre-commit` ou
      `core.hooksPath`), ordem de localização do detector (D2) com *THE PIN* restrito ao modo
      download, pin `v2.21.0` + sha256 e a frase de bump, a lista do que não cobre (`--no-verify`,
      extensões fora de `EXT_LANG`, conteúdo existente, renames relidos como add, exit 1 sem
      `findings:`, tier consultivo no modo download); corpo que roda `git diff --cached --no-color
      --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ | PYTHONIOENCODING=utf-8:surrogateescape
      python3 <detector> --diff -` (D7) com expansões seguras para bash 3.2 (D8) e sai 1 com os
      achados mais o rodapé das três saídas (D4); `python3` ausente recusa (D3)

      ```
      grep -c "" skills/code-locale/references/pre-commit-locale.sh   -> 217
      grep -n "^LOCALE_CHECK_TAG=\|^LOCALE_CHECK_SHA256=\|^args=\|rc=70" skills/code-locale/references/pre-commit-locale.sh
      -> 106:LOCALE_CHECK_TAG="${LOCALE_CHECK_TAG:-v2.21.0}"
      -> 107:LOCALE_CHECK_SHA256="${LOCALE_CHECK_SHA256:-4e72af47225d6259f6b69db638af6db6c586c7ee6800e401941e08c223413ff2}"
      -> 181:args=(${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"})
      -> 194:  rc=70
      grep -n "no-renames --src-prefix" skills/code-locale/references/pre-commit-locale.sh
      -> 6:#   git diff --cached --no-color --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ \
      -> 187:output="$(git diff --cached --no-color --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ \
      grep -n "^# Dependencies" skills/code-locale/references/pre-commit-locale.sh   -> 99:# Dependencies: bash 3.2+ [...]
      ```

- [x] 2.2 `bash -n` limpo; o detector sobre o próprio hook (`.sh` está em `EXT_LANG`) reporta
      `findings: 0`; `shellcheck` não está instalado (E.2) e por isso não foi rodado

      ```
      bash -n skills/code-locale/references/pre-commit-locale.sh; echo "bash-n rc=$?"
      -> bash-n rc=0
      python3 skills/code-locale/references/check-identifier-locale.py skills/code-locale/references/pre-commit-locale.sh
      -> pre-commit-locale.sh:188: PYTHONIOENCODING  [en-unknown: 'PYTHONIOENCODING']   advisory (nome da variável do Python, E.4)
      -> findings: 0
      -> rc=0
      ```

## 3. Step de CI

- [x] 3.1 `skills/code-locale/references/ci-step.md` (136 linhas; commit `f4b8bd0`, corrigido no review):
      job copiável (`pull_request`, `permissions: contents: read`, `checkout@v5` com `fetch-depth: 0`
      e `persist-credentials: false`, `curl -fsSL` na tag `v2.21.0` + `sha256sum -c`, `run:` com
      `set -o pipefail` e `git diff --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/
      origin/${{ github.base_ref }}...HEAD | python3 check-identifier-locale.py --diff -` sob
      `PYTHONIOENCODING=utf-8:surrogateescape`); o pin, o `fetch-depth`, o gatilho, o `pipefail`, os
      quatro flags e o handler explicados (D5, D7); o que o step não cobre, com o trade-off do
      `--no-renames`

      ```
      grep -n "fetch-depth\|sha256sum -c\|github.base_ref\|AI_SKILLS_TAG: \|pipefail$\|PYTHONIOENCODING:" skills/code-locale/references/ci-step.md
      -> 25:          fetch-depth: 0
      -> 30:          AI_SKILLS_TAG: v2.21.0
      -> 35:          echo "${CHECK_SHA256}  check-identifier-locale.py" | sha256sum -c -
      -> 39:          PYTHONIOENCODING: utf-8:surrogateescape
      -> 41:          set -o pipefail
      -> 42:          git diff --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ origin/${{ github.base_ref }}...HEAD \
      ```

- [x] 3.2 O bloco `yaml` parseia (C3 via `validate-skills.py`, e à parte)

      ```
      python3 -c "import re,yaml; ... yaml.safe_load_all(block)"   (sobre o fence yaml de ci-step.md)
      -> yaml ok; jobs: ['identifier-locale'] steps: 3 on: {'pull_request': None}
      (após o review) steps[2]['env'] -> {'PYTHONIOENCODING': 'utf-8:surrogateescape'}; steps[2]['run'] começa com "set -o pipefail"
      python3 scripts/validate-skills.py
      -> skills checked: 35   findings: 0
      ```

## 4. Seção da skill e wrappers

- [x] 4.1 `skills/code-locale/SKILL.md` (commit `9060d47`): seção *Wire it in one minute* com os
      dois links relativos e a tabela de três camadas (hook de sessão / pre-commit / CI: o que pega,
      o que deixa passar); item novo no índice de `references/`; `metadata.version` `1.3.1 → 1.4.0`;
      description intacta (mesmos gatilhos, 996 chars ≤ 1024)

      ```
      python3 -c "import yaml; ... print(len(d['description']), len(d['compatibility']), d['metadata']['version'])"
      -> description chars: 996 compat chars: 490 version: 1.4.0
      git diff 80ee53c HEAD -- skills/code-locale/SKILL.md | grep -c '^[-+].*description'
      -> 0            (nenhuma linha da description mudou)
      ```

- [x] 4.2 `bash generate.sh` duas vezes; a segunda sem diff; os dois arquivos novos aparecem em
      `plugins/workflow/skills/code-locale/references/`

      ```
      bash generate.sh; git status --porcelain --untracked-files=all
      ->  M claude/skills/code-locale/SKILL.md
      ->  M cursor/rules/code-locale.mdc
      ->  M plugins/workflow/skills/code-locale/SKILL.md
      ->  M skills/code-locale/SKILL.md
      -> ?? plugins/workflow/skills/code-locale/references/ci-step.md
      -> ?? plugins/workflow/skills/code-locale/references/pre-commit-locale.sh
      -> ?? skills/code-locale/references/ci-step.md
      -> ?? skills/code-locale/references/pre-commit-locale.sh
      bash generate.sh; git status --porcelain --untracked-files=all | wc -l
      -> 8            (os mesmos 8 caminhos: a segunda rodada não muda nada)
      cmp skills/code-locale/references/pre-commit-locale.sh plugins/workflow/skills/code-locale/references/pre-commit-locale.sh
      -> plugins hook mirror identical
      grep -c "blob/master/skills/code-locale/references/pre-commit-locale.sh" cursor/rules/code-locale.mdc
      -> 1            (o Cursor reescreve o link relativo para a URL do repositório)
      (após o review) bash generate.sh; cmp skills/.../pre-commit-locale.sh plugins/workflow/skills/code-locale/references/pre-commit-locale.sh
      -> plugins hook mirror identical; plugins ci-step mirror identical
      ```

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi exercitado pelo caminho real. **Entry point 1**: `git commit` num
      repositório git de rascunho (`$SCR/kit-probe`, `git init -b main`) com o hook copiado para
      `.git/hooks/pre-commit` (`cp` + `chmod +x`, como o cabeçalho instrui). Nesta máquina
      `~/ai-skills` existe, então o caso base roda no modo clone (tiers completos):

      ```
      printf 'def calcular_total(itens):\n    return sum(itens)\n' > orders.py; git add orders.py; git commit -q -m "add orders"; echo "commit rc=$?"
      -> orders.py:1: calcular_total  [pt-verb: 'calcular']
      ->     machine layer must be English (code-locale). If this name is correct as written, add a reason:
      ->       # locale-ok: <why this term has no faithful English name>
      -> orders.py:1: itens  [en-unknown: 'itens']   [...]  advisory: this finding does not fail the run
      -> findings: 1
      -> pre-commit-locale: refused: the staged diff adds a non-English name to the machine layer (code-locale).
      -> pre-commit-locale:   waive one line:   # locale-ok: <why this term has no faithful English name>   (on the line, or the one above)
      -> pre-commit-locale:   waive a path:     add it to .identifier-locale-allow (one path or segment per line)
      -> pre-commit-locale:   bypass:           git commit --no-verify   — the deliberate exit; CI measures it anyway
      -> commit rc=1
      -> fatal: your current branch 'main' does not have any commits yet     (git log: 0 commits — nada entrou)
      printf '# locale-ok: probe\ndef calcular_total(itens):\n    return sum(itens)\n' > orders.py; git add orders.py; git commit -q -m "add orders"; echo "commit rc=$?"
      -> orders.py:3: itens  [en-unknown: 'itens']   [...]  advisory
      -> findings: 0
      -> commit rc=0
      ```

      Os demais casos do hook foram disparados por `$SCR/sim_cases.py` — um driver que só monta o
      ambiente por caso (`HOME`, `AI_SKILLS_HOME`, `LOCALE_CHECK*`, `PATH`) e chama o mesmo
      `git commit`; o sandbox desta sessão recusa `HOME=... git` direto no shell. Saída completa em
      `$SCR/sim_output.txt`; fragmentos:

      ```
      [3] HOME=<vazio> AI_SKILLS_HOME=/nonexistent git commit   (customers.py: def buscar_cliente)
      -> pre-commit-locale: downloading the detector once, pinned at v2.21.0: https://raw.githubusercontent.com/solvelab/ai-skills/v2.21.0/skills/code-locale/references/[...]
      -> pre-commit-locale: advisory English tier off: english-words.txt.gz is not beside .git/locale-check/v2.21.0/check-identifier-locale.py (gating tiers unaffected)
      -> customers.py:1: buscar_cliente  [pt-verb: 'buscar']
      -> findings: 1
      -> pre-commit-locale: refused: [...]   rc=1
      -> cached detector: .git/locale-check/v2.21.0/check-identifier-locale.py sha256=4e72af47…3ff2 matches_pin=True
      [3b] mesmo comando de novo            -> sem a linha "downloading" (cache), buscar_cliente, rc=1
      [4] LOCALE_CHECK_SHA256=deadbeef      -> digest mismatch for the detector at tag v2.21.0 / expected deadbeef / got 4e72af47…3ff2 / could not locate [...]  rc=1
      [4b] LOCALE_CHECK_TAG=v0.0.0-nope LOCALE_CHECK_SHA256=skip
                                           -> curl: (22) The requested URL returned error: 404 / download failed (is v0.0.0-nope a published tag [...])  rc=1
      [5] LOCALE_CHECK=$SCR/standalone/check-identifier-locale.py
                                           -> advisory English tier off [...] / buscar_cliente / refused  rc=1
      [6] LOCALE_CHECK=/nonexistent/check.py -> LOCALE_CHECK is set but is not a file: /nonexistent/check.py / could not locate  rc=1
      [7] PATH=<dir sem python3>            -> python3 not found on PATH — the detector needs Python 3.9+, and a gate that cannot measure must not approve / bypass, if you mean it: git commit --no-verify  rc=1
      [8] git commit --no-verify (buscar_cliente)  -> rc=0   (escape conhecido e nomeado)
      [9] git commit --allow-empty          -> rc=0, sem saída
      [10] totals.py: def compute_total(items)  -> rc=0, sem saída
      [11] relatorio.txt (fora de EXT_LANG) -> relatorio.txt: relatorio  [path-pt-noun: 'relatorio'] / A file name carries no inline waiver — grandfather the path [...] .identifier-locale-allow / refused  rc=1
      [12] .identifier-locale-allow com relatorio.txt  -> rc=0
      ```

      **Entry point 2** — o step de CI. `act` não está instalado (E.3); rodado o **mesmo texto dos
      dois blocos `run:`** de `ci-step.md` sob `bash -e -c`, num clone do repositório de rascunho
      (`git clone kit-probe kit-probe-ci`, então `origin/main` existe) com `origin/main` no lugar de
      `origin/${{ github.base_ref }}`, num branch `feature/pt` que adiciona `shipping.py` com
      `def calcular_frete(order)` (commitado com `--no-verify`, como um autor que dribla o hook):

      ```
      [CI-1] curl -fsSL -o check-identifier-locale.py "https://raw.githubusercontent.com/solvelab/ai-skills/v2.21.0/[...]" && echo "4e72af47…3ff2  check-identifier-locale.py" | sha256sum -c -
      -> check-identifier-locale.py: OK          rc=0
      [CI-2] git diff origin/main...HEAD | python3 check-identifier-locale.py --diff - --no-english   (feature/pt)
      -> shipping.py:1: calcular_frete  [pt-verb: 'calcular']
      -> findings: 1                              rc=1
      [CI-3] mesmo comando em feature/en (def compute_shipping(order))
      -> findings: 0                              rc=0
      [CI-4] fetch com CHECK_SHA256 errado
      -> check-identifier-locale.py: FAILED / sha256sum: WARNING: 1 computed checksum did NOT match   rc=1
      ```

      `bash -n` e o detector sobre o hook: 2.2. `shellcheck`: ausente nesta máquina, não rodado.

      **Após o review (2026-09-05)** — os nove achados foram reproduzidos contra o hook original e
      re-medidos contra o corrigido, todos pelo `git commit` real com o hook em `.git/hooks/pre-commit`
      e `LOCALE_CHECK` apontando para o detector do worktree (`$SCR/repro139.py <hook> <detector>
      before|after`; saída em `$SCR/repro139-{before,after}.txt`). Antes: `cases: 10  as expected: 3
      unexpected: 7`. Depois:

      ```
      [F3] git -c diff.external=<sh que sai 0> commit   (customers.py: def buscar_cliente)
      -> antes: rc=0, commits=1 (aprovado sem medir)        depois: buscar_cliente [pt-verb] / refused  rc=1
      [F4a] git mv orders.py relatorio.py; git commit
      -> antes: rc=0, commits=2                             depois: relatorio.py: relatorio [path-pt-noun] / refused  rc=1
      [F4b] git mv base.py cadastro.py + uma linha; git commit
      -> antes: rc=0                                         depois: cadastro.py: cadastro [path-pt-noun]  rc=1
      [F4c] relatorio.py (def calcular_total) -> git mv report.py; git commit   (o trade-off de D7)
      -> antes: rc=0 (mudo)                                  depois: report.py:1: calcular_total [pt-verb]  rc=1
      [F5a] legacy.py latin-1 já commitado + "count = 1"; git commit
      -> antes: UnicodeDecodeError [...] refused: the staged diff adds a non-English name  rc=1
      -> depois: rc=0, commits=2, sem saída
      [F5b] legacy.py latin-1 + "def buscar_cliente(x):"; git commit
      -> depois: legacy.py:3: buscar_cliente [pt-verb] / findings: 1 / refused  rc=1  (sem traceback)
      [F5c] LOCALE_CHECK=crash.py (raise RuntimeError) sobre código inglês
      -> antes: RuntimeError: boom / refused: the staged diff adds a non-English name [...]  rc=1
      -> depois: RuntimeError: boom / the detector itself failed (exit 70, no findings: line); nothing was measured  rc=1
      [F6] diff.mnemonicPrefix=true + .identifier-locale-allow com relatorio.txt; git commit
      -> antes: i/relatorio.txt: relatorio [path-pt-noun] / refused  rc=1     depois: rc=0, commits=1
      cases: 10  as expected: 10  unexpected: 0
      ```

      **Entry point 3** — o hook inteiro em bash 3.2 e 4.3 (`docker run --rm -v $SCR/b32-kit:/kit:ro
      -v $SCR/b32-run.sh:/run.sh:ro bash:3.2 sh /run.sh`: `apk add git python3`, `git init`, `cp` do
      hook para `.git/hooks/pre-commit`, dois `git commit`; saída em `$SCR/b32-{before,after}.txt`):

      ```
      [B-3.2 antes]  .git/hooks/pre-commit: line 154: EXTRA_ARGS[@]: unbound variable / english commit rc=1  commits=0 / pt commit rc=1  commits=0
      [B-3.2 depois] GNU bash, version 3.2.57(1)-release / english commit rc=0  commits=1 / customers.py:1: buscar_cliente [pt-verb] / refused / pt commit rc=1  commits=1
      [B-4.3 depois] GNU bash, version 4.3.48(1)-release / english commit rc=0  commits=1 / [...] refused / pt commit rc=1  commits=1
      ```

      A matriz original de 16 casos foi re-rodada num repositório novo contra o hook corrigido
      (`$SCR/sim139_full.py`, saída em `$SCR/sim139_full_output.txt`): `cases: 18  as expected: 18
      unexpected: 0` (os 16 mais os dois manuais de S.1, agora no driver). E o bloco `run:` do
      `ci-step.md` foi relido do próprio arquivo (fence `yaml` parseado, `origin/main` no lugar de
      `origin/${{ github.base_ref }}`, `env` do step aplicado) e rodado sob `bash -e -c` num clone com
      quatro branches (`$SCR/ci139.py`, saída em `$SCR/ci139-out.txt`):

      ```
      [CI-pt]      feature/pt  (def calcular_frete)          -> shipping.py:1: calcular_frete [pt-verb] / findings: 1   rc=1
      [CI-en]      feature/en  (def compute_shipping)        -> findings: 0   rc=0
      [CI-rename]  feature/rename-pt (git mv orders.py relatorio.py) -> relatorio.py: relatorio [path-pt-noun] / findings: 1   rc=1
      [CI-latin1]  feature/latin1 (linha inglesa num .py latin-1)    -> findings: 0   rc=0
      [CI-nobase]  origin/release/9...HEAD (base ausente)    -> fatal: ambiguous argument [...] / findings: 0   rc=128  (antes do pipefail: rc=0, verde)
      [CI-depth1]  clone --depth 1                           -> fatal: ambiguous argument 'origin/main...HEAD' / findings: 0   rc=128
      cases: 8  as expected: 8  unexpected: 0     (com CI-1 fetch OK e CI-4 digest errado FAILED)
      ```

- [x] S.2 Matriz de casos medida, em contagens. Primeira entrega: `sim_cases.py` -> `cases: 16  as
      expected: 16  unexpected: 0`, mais os dois casos manuais de S.1. Após o review, sobre o hook
      corrigido: `sim139_full.py` -> `cases: 18  as expected: 18  unexpected: 0`; `repro139.py after`
      -> `cases: 10  as expected: 10  unexpected: 0`; `ci139.py` -> `cases: 8  as expected: 8
      unexpected: 0`; bash 3.2 e 4.3 -> 2/2 commits ingleses aceitos, 2/2 commits `buscar_cliente`
      recusados

      | Artefato | Expectativa | Casos | Resultado |
      |---|---|---|---|
      | hook (`git commit`, modo clone) | tinha de recusar e recusou | 1/1 | `calcular_total`, rc=1, 0 commits |
      | hook (modo clone) | tinha de aceitar e aceitou | 1/1 | `# locale-ok: probe`, rc=0 |
      | hook (modo download, `HOME` vazio) | tinha de baixar uma vez, conferir sha e recusar | 2/2 | [3] download + `matches_pin=True`; [3b] cache, sem download |
      | hook (pin) | tinha de recusar sem medir | 2/2 | [4] sha errado; [4b] tag inexistente (404) |
      | hook (`LOCALE_CHECK`) | caminho explícito mede; caminho inválido recusa | 2/2 | [5] rc=1 com achado; [6] rc=1 nomeando a variável |
      | hook (sem `python3`) | tinha de recusar e recusou | 1/1 | [7] rc=1, nomeia o `--no-verify` |
      | hook | tinha de ficar mudo e ficou | 3/3 | [9] commit vazio; [10] `compute_total`; [12] allowlist |
      | hook (fora de `EXT_LANG`) | caminho medido, conteúdo pulado | 1/1 | [11] `relatorio.txt` recusado pelo nome |
      | hook | escape conhecido ficou mudo | 1/1 | [8] `--no-verify`, rc=0 — ver S.3 |
      | step de CI (`run:` verbatim, `origin/main`) | fetch + digest OK; PR com achado falha; PR limpo passa; digest errado falha | 4/4 | CI-1 rc=0; CI-2 rc=1; CI-3 rc=0; CI-4 rc=1 |
      | hook (config git do repo/usuário) — review | `diff.external`, rename puro, rename+edit tinham de recusar | 3/3 | F3, F4a, F4b rc=1 (antes: 3/3 aprovados, rc=0) |
      | hook (allowlist sob `mnemonicPrefix`) — review | tinha de aceitar | 1/1 | F6 rc=0 (antes: recusado) |
      | hook (latin-1) — review | linha inglesa aceita; `buscar_cliente` recusado como achado | 2/2 | F5a rc=0; F5b rc=1 sem traceback |
      | hook (detector que crasha) — review | recusa como falha do detector, não como achado | 1/1 | F5c "detector itself failed (exit 70 [...])" |
      | hook (trade-off `--no-renames`) — review | rename de legado com conteúdo PT encontra o gate | 1/1 | F4c rc=1, `calcular_total` no conteúdo — declarado em D7 |
      | hook em bash 3.2 / 4.3 (container) — review | inglês aceito, PT recusado | 4/4 | 2 imagens × 2 commits (antes: 0/4 — `unbound variable`) |
      | step de CI — review | rename para PT falha; latin-1 passa; base ausente e `--depth 1` falham em vez de aprovar | 4/4 | rc=1; rc=0; rc=128; rc=128 (antes: base ausente rc=0, verde) |
      | `bash -n` | limpo | 1/1 | rc=0 |
      | `shellcheck` | — | 0/0 | não instalado; declarado |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      Um escape conhecido e mantido de propósito: `git commit --no-verify` com `buscar_cliente`
      passa ([8], rc=0). É o bypass **nomeado** no cabeçalho e no rodapé do hook, e é exatamente o
      que o step de CI pegou em CI-2 — o mesmo commit driblado, medido no clone. Nada se comportou
      diferente do escrito no design; três observações que não são defeitos, registradas para o
      revisor:

      - No modo clone, um commit aceito **com** achados consultivos imprime a saída inteira do
        detector (inclusive `findings: 0`) — decisão D4: linhas `advisory` merecem os olhos do
        autor. Um commit sem nenhum achado fica mudo ([9], [10]).
      - Quando o digest falha ([4]), a última linha antes do bypass é a genérica "could not locate
        the identifier-locale detector"; a razão específica ("digest mismatch … expected … got …")
        está três linhas acima. Aceito: a mensagem específica vem primeiro.
      - O que a simulação **não** prova: que o runner do Actions resolve `github.base_ref` e faz o
        checkout do merge commit com `fetch-depth: 0` — `origin/main` foi o substituto (E.3), e a
        premissa vem do `ci.yml` deste repositório, que já depende dos dois. Nem que o shell padrão
        do runner é `bash -e {0}` sem `pipefail` — vem da doc (E.3); por isso o `set -o pipefail`
        está escrito no bloco, e não confiado ao `shell:`.

      O que o review de 2026-09-05 mostrou que **tinha** escapado da primeira simulação, e que agora
      está medido acima (S.1, F3-F6, B-3.2, CI-nobase): sete comportamentos fora do desenhado,
      todos reproduzidos antes da edição e re-medidos depois. Um comportamento novo, deliberado e
      declarado (D7, cabeçalhos): com `--no-renames`, renomear um arquivo legado cujo conteúdo ainda
      tem nomes em português encontra o gate (F4c) — antes passava mudo. O escape `--no-verify`
      permanece e continua nomeado.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em `skills/code-locale/SKILL.md`: name == diretório, description
      folded, author solvelab, semver `1.4.0`, category `process`, license MIT, compatibility —
      `gates.sh` -> `PASS frontmatter` (o mesmo loop do step *Skill frontmatter checks*);
      `agentskills validate skills/code-locale/` -> `Valid skill: skills/code-locale`
- [x] Q.2 Conteúdo tocado em inglês (catalog locale): `SKILL.md`, `pre-commit-locale.sh`,
      `ci-step.md` — sem comentário em português; `grep -nP '[àáâãéêíóôõúç…]'` sobre os dois
      arquivos novos -> nenhuma linha (rc=1); as únicas palavras portuguesas são os fixtures
      (`calcular_total`, `relatorio`) citados como exemplo do que o gate recusa
- [x] Q.3 Gatilhos da description testáveis e sem colisão — a description não muda
      (`git diff 80ee53c HEAD -- skills/code-locale/SKILL.md | grep -c '^[-+].*description'` -> 0);
      996 chars; o "Do NOT use for" permanece
- [x] Q.4 Sem doutrina duplicada: a seção nova e os dois arquivos apontam para *Reviewing a diff*,
      para `references/migration.md` e para o docstring do detector em vez de reescrever os tiers
      ou as saídas (tabela de Canonical Home em `design.md`); nenhum tier é reimplementado
      (`grep -c "pt-verb\|pt-noun" pre-commit-locale.sh` -> 1, a linha do cabeçalho que os nomeia)
- [x] Q.5 Identificadores em inglês no que a change introduz (`LOCALE_CHECK`, `LOCALE_CHECK_TAG`,
      `LOCALE_CHECK_SHA256`, `EXTRA_ARGS`, `locate_check`, `verify_digest`, `refuse`, `log`,
      `identifier-locale` como id de job e step):

      ```
      python3 skills/code-locale/references/check-identifier-locale.py skills/code-locale/references/pre-commit-locale.sh
      -> findings: 0
      python3 skills/code-locale/references/check-identifier-locale.py --markdown-fences skills/code-locale/references/ci-step.md skills/code-locale/SKILL.md
      -> findings: 0   (cada um)
      ```

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-locale-adoption-kit --strict` -> `Change 'add-locale-adoption-kit' is valid`
- [x] V.2 Descoberta do catálogo intacta: `npx -y skills add . --list` -> `Found 35 skills`;
      `ls -d skills/*/ | wc -l` -> `35`; `validate-skills.py` -> `skills checked: 35   findings: 0`
      (sem órfão: C11 não reporta os dois arquivos novos, ambos linkados do `SKILL.md`)
- [x] V.3 README / docs atualizados onde a composição ou o uso mudam — a composição não muda; o uso
      novo está documentado na própria skill (seção *Wire it in one minute*); `README.md` fora do
      escopo por decisão da issue #139 e não tocado
- [ ] V.4 `openspec archive add-locale-adoption-kit --yes` after all groups above are `[x]` — PR
      separado, como o repositório já faz
