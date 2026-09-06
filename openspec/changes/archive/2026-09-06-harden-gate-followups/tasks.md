## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `e7f5fe8` (topo de `master`, 2026-09-06):

      - `scripts/validate-spec-rite.py` — 399 linhas; `changed_paths()` em 167-170 (`git diff
        --name-only base...HEAD` + `splitlines()`); `requires_registration()` em 174-175 e
        `touched_changes()` em 193-195 comparam com `startswith`; `DEFECTS`/`SILENT` em 246-275;
        `selftest_reader()` em 297-332; KNOWN LIMIT em 23-29.
      - `scripts/validate-skill-version.py` — 469 linhas; `split_nul_paths()` em 162-165,
        `changed_paths()` com `-z` em 168-173, `_probe_quoted_path()` em 347-372,
        `_sibling_min_reason()` em 84-101 importa o spec-rite em tempo de carga; docstring 38-43
        explica `core.quotePath`.
      - `skills/code-locale/references/check-identifier-locale.py` — 916 linhas; KNOWN LIMIT 1-17 em
        26-76; `VENDOR_PARTS` em 386-389; `is_vendored()` em 393-394; `scan_path()` em 518-549
        (aplica `is_vendored` em 525); `scan_diff()` em 612-664 (não aplica); `SELFTEST_PATH_CLEAN`
        em 725-732; `selftest_paths()` em 760-794; `main()` em 828-910 (`is_vendored` em 878,
        `vendored` impresso em 906).
      - `skills/code-locale/SKILL.md` — `metadata.version: 1.4.2` (linha 17); linha *Verified
        against* em 31-37 cita "9 path cases silent" e "Probed on 2026-09-05".
      - `claude/global/hooks/locale-stop-gate.py:294-296` — `check.scan_diff(iter(...), allow,
        None)` e filtro `is_vendored` nos achados; `claude/global/hooks/locale-rite.py:258` —
        `check.is_vendored(path)`.
      - `scripts/selftest-validate-skills.py` — 136 linhas; `MUTATIONS` em 12-115 (27 entradas);
        laço em 117-134 com `copytree` em 123; C7 em 124-126 cria diretório; C11 em 129 cria
        arquivo.
      - `.github/workflows/ci.yml:70-79` — step *Version coherence*; `generate.sh:27-36` e
        `scripts/set-version.sh:13-16` — `SEMVER_RE` idêntico nos dois.
      - `README.md:443` — `r3f-*/SKILL.md  # React Three Fiber skills (10 topics)`;
        `scripts/validate-repo-hygiene.py:91-94` — declara esse `(10 topics)` como revisão apenas.
      - `openspec/specs/skills-catalog/spec.md` — *The repository itself is gated, not only its
        skills* e *The identifier-locale check reads the path it is given*, texto integral copiado
        para o delta.
      - `openspec/changes/archive/2026-09-04-close-ci-gate-holes/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md` — modelo de estilo; E.4 dele registra o follow-up do README.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      Cada buraco reproduzido antes de escrever, em `e7f5fe8` (2026-09-06):

      ```
      git ls-files | grep -cP '[^\x00-\x7F]'          -> 0   (o repo não tem caminho quotado hoje)
      bash make-quoted-clone.sh <worktree> quoted-clone   (clone; branch base com openspec/changes/probe-quoted/tasks.md;
                                                           branch work adiciona skills/x/references/café.md e
                                                           openspec/changes/probe-quoted/specs/café.md; core.quotePath=true)
      git diff --name-only base...HEAD
      -> "openspec/changes/probe-quoted/specs/caf\303\251.md"
      -> "skills/x/references/caf\303\251.md"
      git diff --name-only -z base...HEAD | tr '\0' '\n'
      -> openspec/changes/probe-quoted/specs/café.md
      -> skills/x/references/café.md
      SPEC_RITE_BASE=base PR_BODY="" python3 scripts/validate-spec-rite.py   (no clone, script de e7f5fe8)
      -> ::error::S3 unrelated change — this diff touches 2 path(s) outside openspec/ — "openspec/changes/probe-quoted/specs/caf\303\251.md", "skills/x/references/caf\303\251.md" — and 1 active change(s) exist (probe-quoted), but the diff touches none of their directories [...]
      -> spec-rite gate: 1 findings (base base, 2 changed path(s), 1 active change(s))   exit=1
      ```

      ```
      python3 skills/code-locale/references/check-identifier-locale.py --diff vendored.diff
          (--- /dev/null / +++ b/node_modules/servicos_pedido/calculo.js / +const usuario = 1; / +function calcularFrete() {})
      -> node_modules/servicos_pedido/calculo.js:1: usuario  [pt-noun: 'usuario']
      -> node_modules/servicos_pedido/calculo.js:2: calcularFrete  [pt-verb: 'calcular']
      -> findings: 2   exit=1
      ```

      ```
      bash timeit.sh "selftest-validate-skills BEFORE (e7f5fe8)" python3 scripts/selftest-validate-skills.py
      -> 27/27 defect classes detected
      -> selftest-validate-skills BEFORE (e7f5fe8) wall=49.1s rc=0
      python3 measure-cost.py <worktree>        (3 repetições de cada, no mesmo tree)
      -> files under source (incl. .git): 1375
      -> copytree x3: ['0.08s', '0.06s', '0.08s']  -> mean 0.07s
      -> validate-skills.py x3: ['1.71s', '1.74s', '1.69s']  -> mean 1.71s
      -> 27 copies ~ 1.9s ; 27 validator runs ~ 46.2s          (a premissa da issue — "a cópia é o custo" — não se sustenta)
      ```

      ```
      python3 extract-step.py .github/workflows/ci.yml "Version coherence" step-before-version-coherence.sh
      -> extracted step 2 'Version coherence (VERSION == plugin.json == marketplace.json)'
      bash make-version-fixture.sh vfix-bad 2.15.1dirtychange   (VERSION + plugin.json + marketplace.json iguais)
      bash run-step.sh vfix-bad step-before-version-coherence.sh
      -> Version 2.15.1dirtychange coherent across manifests.
      -> exit=0                                                  (o buraco 4, reproduzido)
      ```

      ```
      grep -n "10 topics" README.md      -> 443:│   └── r3f-*/SKILL.md   # React Three Fiber skills (10 topics)
      ls plugins/game/skills | wc -l     -> 12
      python3 scripts/validate-repo-hygiene.py   -> repo hygiene: 0 findings   (H2 não lê bloco de código, por desenho)
      ```

      ```
      git --version        -> git version 2.47.3
      python3 --version    -> Python 3.14.5
      openspec --version   -> 1.6.0
      ls skills | wc -l    -> 36
      openspec new change harden-gate-followups --schema skills-rite
      -> Created change 'harden-gate-followups' at openspec/changes/harden-gate-followups/   (só .openspec.yaml; artefatos escritos a partir de openspec/schemas/skills-rite/templates/)
      ```

- [x] E.3 O que não pôde ser probado

      - O comportamento do step *Version coherence* **no runner do GitHub** não é medido aqui: o
        shell do step é extraído literalmente do YAML e rodado com `bash -e` local; a run do PR desta
        change é a prova no runner (S.3).
      - A issue #172 fala em "24 mutation classes"; o arquivo em `e7f5fe8` tem 27 (`MUTATIONS` cresceu
        em #131, #153, #157, #165). A contagem que vale é a medida: 27/27.
      - O tempo do selftest é medido nesta máquina (WSL2); o número no CI difere, e só a **razão**
        antes/depois (e a decomposição cópia/validador) é transferível.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #172 pediu e nada além. Notados pelo caminho e **não** feitos, como
      follow-up:

      - `scripts/validate-repo-hygiene.py:91-94` cita `README.md:345 carries (10 topics)` como
        exemplo do que H2 não lê; depois desta change o exemplo não existe mais. O arquivo não está
        na lista deste item; atualizar a docstring é follow-up.
      - O custo real do selftest do validador são as 27 runs de `validate-skills.py` (46 s de 49 s);
        rodá-las em paralelo (`concurrent.futures`, uma cópia por worker) é a otimização que a
        medida justifica e que a issue não pediu — follow-up.
      - `claude/global/hooks/locale-stop-gate.py:296` filtra `is_vendored` nos achados por fora;
        com D2 o filtro fica redundante (o detector já não produz esses achados). Remover é do dono
        do hook, não deste item.
      - `validate-skill-version.py` poderia importar `split_nul_paths()` do spec-rite em vez de
        definir o seu (a direção de import que não fecha ciclo); não está na lista deste item.
      - `scripts/validate-repo-hygiene.py:252` e `scripts/validate-rite-evidence.py:353` também
        fazem `copytree` do repositório no selftest (uma vez cada, não por caso); fora de escopo.

## 2. Spec-rite lê o diff com `-z` (D1)

- [x] 2.1 `changed_paths()` roda `git diff --name-only -z` e separa por NUL com `split_nul_paths()`,
      duplicado de `validate-skill-version.py` com comentário nomeando o irmão e o motivo

      ```
      grep -n '"-z"\|def split_nul_paths\|Duplicated from validate-skill-version.py' scripts/validate-spec-rite.py
      -> 176:def split_nul_paths(out: str) -> list[str]:
      -> 180:    Duplicated from validate-skill-version.py rather than imported: that script loads THIS one at
      -> 190:    out = subprocess.run(["git", "-C", str(root), "diff", "--name-only", "-z", f"{base}...{head}"],
      ```

- [x] 2.2 Selftest: caso literal do helper (aspas, quebra de linha) e probe em repositório
      descartável com `core.quotePath=true` — caminho não-ASCII dentro de `openspec/changes/<id>/`
      registra o diff (`evaluate()` mudo)

      ```
      python3 scripts/validate-spec-rite.py --selftest
      -> PATHS  NUL-separated names are read verbatim, quotes and newlines included
      -> PATHS  a quoted path inside an active change registers the diff on a real repository
      -> 6/6 defect classes detected, 10/10 false-positive cases stayed silent, 6/6 reader cases correct, 2/2 path-reader cases correct   exit=0
      python3 probe-without-z.py <worktree>      (o mesmo probe com changed_paths() trocado pela versão de linha)
      -> new reader : True
      -> old reader : False | findings: ['S3 unrelated change: this diff touches 2']     (o probe reprova o leitor antigo)
      python3 scripts/validate-skill-version.py --selftest   (importa este script em tempo de carga)
      -> 7/7 defect classes detected, 11/11 false-positive cases stayed silent, 11/11 helper cases correct   exit=0
      ```

- [x] 2.3 Docstring: o parágrafo sobre `-z` e o que o modo de linha fazia com o caminho

      ```
      grep -n "Paths are read with\|The one plumbing probe" scripts/validate-spec-rite.py
      -> 29:below, not by the selftest. The one plumbing probe it does run is the path reader, below.
      -> 31:Paths are read with `git diff --name-only -z` and split on NUL, the way validate-skill-version.py
      ```

## 3. `scan_diff()` aplica `is_vendored()` (D2)

- [x] 3.1 `scan_diff()` pula o bloco inteiro de um `+++` vendored e devolve o caminho na lista
      `vendored` (parâmetro opcional); `main()` imprime na linha `skipped (vendored/...)` existente

      ```
      python3 skills/code-locale/references/check-identifier-locale.py --diff vendored.diff   (o mesmo diff de E.2)
      -> findings: 0
      ->   skipped (vendored/generated/minified): 1 file(s) — not this project's machine layer
      -> exit=0
      grep -n "vendored=vendored\|if is_vendored(Path(path)):" skills/code-locale/references/check-identifier-locale.py
      -> 654:            if is_vendored(Path(path)):
      -> 886:        findings.extend(scan_diff(stream, allow, english, vendored=vendored))
      ```

- [x] 3.2 Selftest: diff que adiciona `node_modules/servicos_pedido/calculo.js` com `const usuario`
      fica mudo e conta um pulado; contagem do `selftest OK` atualizada

      ```
      python3 skills/code-locale/references/check-identifier-locale.py --selftest
      -> CLEAN   path-clean/diff adds vendored file (skipped, counted)
      -> selftest OK: 7 content tiers fire, 16 clean cases stay silent, 6 path tiers fire, 10 path cases stay silent, 2 en-unknown tiers fire, 5 en-unknown cases stay silent   exit=0
      ```

- [x] 3.3 KNOWN LIMIT 12 diz o que o modo `--diff` pula (por caminho; `is_minified` não roda)

      ```
      sed -n 61,64p skills/code-locale/references/check-identifier-locale.py
      ->        A `+++` path in a vendored or generated tree (VENDOR_PARTS, `.min.`) is skipped whole in
      ->        --diff mode — path and added lines — and reported as skipped, the same exclusion file mode
      ->        applies. That decision is by PATH only: a diff carries no file body, so `is_minified` never
      ->        runs in this mode, and a generated file outside those trees is measured as written code.
      ```

- [x] 3.4 `code-locale` 1.4.2 → 1.4.3, linha *Verified against* re-probada; `./generate.sh` regenera
      os wrappers; `locale-rite.py --selftest` e `locale-stop-gate.py --selftest` verdes depois da
      edição

      ```
      grep -n "^  version:" skills/code-locale/SKILL.md claude/skills/code-locale/SKILL.md plugins/workflow/skills/code-locale/SKILL.md
      -> skills/code-locale/SKILL.md:17:  version: 1.4.3
      -> claude/skills/code-locale/SKILL.md:17:  version: 1.4.3
      -> plugins/workflow/skills/code-locale/SKILL.md:17:  version: 1.4.3
      bash generate.sh   -> Generated 10 category plugins in plugins/ (descriptions derived from the tree)
      diff -q skills/code-locale/references/check-identifier-locale.py plugins/workflow/skills/code-locale/references/check-identifier-locale.py   -> (idênticos)
      python3 claude/global/hooks/locale-rite.py --selftest
      -> selftest OK: 13 PostToolUse decisions, 12 PreToolUse decisions, inform mode, en-unknown, the allowlist, the legacy path, [...]   exit=0
      python3 claude/global/hooks/locale-stop-gate.py --selftest
      -> selftest OK: 26 decisions in temporary git repositories, 2 output shapes, 5 malformed payloads, plus the argv contract   exit=0
      ```

## 4. Selftest do validador em uma cópia (D3)

- [x] 4.1 Uma `copytree` por run; cada mutação guarda bytes (ou ausência), aplica, roda, restaura em
      `finally`; C7 remove o diretório, C11 remove o arquivo; cópia comparada byte a byte no fim

      ```
      grep -c "shutil.copytree(" scripts/selftest-validate-skills.py   -> 1
      grep -n "read_bytes\|write_bytes\|rmtree\|unlink\|filecmp.cmp" scripts/selftest-validate-skills.py
      -> 132:        original = target.read_bytes() if target is not None and target.exists() else None
      -> 142:                shutil.rmtree(ghost, ignore_errors=True)
      -> 144:                target.unlink(missing_ok=True)
      -> 146:                target.write_bytes(original)
      -> 158:        str(r) for r in src_files & dst_files if not filecmp.cmp(SRC / r, dst / r, shallow=False))
      python3 probe-leak.py <worktree>      (o mesmo script com `target.write_bytes(original)` trocado por `pass`)
      -> MISSED  C5 no version pin (date but no Probed on)          (+4 MISSED: as mutações de observability empilharam)
      -> LEAKED  copy byte-identical to the source after all mutations reverted: skills/assettoserver-ops/SKILL.md, skills/claude-statusline/SKILL.md, skills/conventional-commit/SKILL.md
      -> 22/27 defect classes detected                              (a checagem dispara; a reversão é o que isola)
      ```

- [x] 4.2 27/27 `CAUGHT`; cópia limpa depois do laço; tempo antes/depois registrado

      ```
      python3 scripts/selftest-validate-skills.py
      -> CLEAN   copy byte-identical to the source after all mutations reverted
      -> 27/27 defect classes detected   exit=0
      bash bench.sh <worktree>      (velho = e7f5fe8 via `git show`, novo = worktree; alternados, 3 rounds, máquina ociosa)
      -> round 1 OLD (e7f5fe8) wall=49.3s rc=0      round 1 NEW (worktree) wall=47.5s rc=0
      -> round 2 OLD (e7f5fe8) wall=49.2s rc=0      round 2 NEW (worktree) wall=46.5s rc=0
      -> round 3 OLD (e7f5fe8) wall=50.5s rc=0      round 3 NEW (worktree) wall=48.6s rc=0
      -> média OLD 49,7 s ; média NEW 47,5 s ; ganho ~2,2 s (4 %) — o que a cópia custava (E.2: 1,9 s); o resto é o validador
      ```

## 5. `VERSION` validado no step *Version coherence* (D4)

- [x] 5.1 `SEMVER_RE` (literal de `generate.sh:32`) aplicado a `VERSION` antes do laço dos
      manifests, `::error` nomeando o valor

      ```
      grep -n "SEMVER_RE" generate.sh scripts/set-version.sh .github/workflows/ci.yml
      -> generate.sh:32:SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'
      -> scripts/set-version.sh:15:SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'
      -> .github/workflows/ci.yml:78:          SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'
      -> .github/workflows/ci.yml:79:          if ! [[ "$VERSION" =~ $SEMVER_RE ]]; then
      ```

- [x] 5.2 Step extraído do YAML novo e rodado contra a fixture `2.15.1dirtychange` (reprova), contra
      `2.30.0` e `2.31.0-beta.1` (passam), contra vazio (reprova) e no worktree (passa)

      ```
      python3 extract-step.py .github/workflows/ci.yml "Version coherence" step-new-version-coherence.sh
      bash run-step.sh vfix-bad step-new-version-coherence.sh
      -> ::error::VERSION is '2.15.1dirtychange' — expected MAJOR.MINOR.PATCH with an optional -prerelease suffix (the regex generate.sh and set-version.sh apply).   exit=1
      bash run-step.sh vfix-empty step-new-version-coherence.sh
      -> ::error::VERSION is '' — expected MAJOR.MINOR.PATCH [...]   exit=1
      bash run-step.sh vfix-good step-new-version-coherence.sh   -> Version 2.30.0 coherent across manifests.   exit=0
      bash run-step.sh vfix-pre step-new-version-coherence.sh    -> Version 2.31.0-beta.1 coherent across manifests.   exit=0
      bash run-step.sh <worktree> step-new-version-coherence.sh  -> Version 2.30.0 coherent across manifests.   exit=0
      ```

## 6. README sem contagem na árvore (D5)

- [x] 6.1 `README.md:443` sem `(10 topics)`; `validate-repo-hygiene.py` verde

      ```
      grep -n "r3f-\*/SKILL.md" README.md   -> 443:│   └── r3f-*/SKILL.md   # React Three Fiber skills, one per topic
      grep -c "10 topics" README.md         -> 0
      python3 scripts/validate-repo-hygiene.py   -> repo hygiene: 0 findings   exit=0
      ```

## 7. Simulation & Field Proof (MANDATORY)

- [x] S.1 Cada gate exercitado pelo caminho real (o script como o CI o invoca, o step literal do
      `ci.yml`, o detector via `--diff`), antes e depois, com a saída observada registrada

      Tudo em `3b0f0ca` (2026-09-06), worktree limpo antes e depois (`git status --porcelain | wc -l
      -> 0` fora dos arquivos desta change). As reproduções que sujam árvore rodaram num **clone**
      (`quoted-clone`) e em fixtures no scratchpad.

      Buraco 1 — spec-rite pelo caminho do CI, no clone, antes e depois (o script copiado por cima):

      ```
      SPEC_RITE_BASE=base PR_BODY="" python3 scripts/validate-spec-rite.py   (e7f5fe8)
      -> ::error::S3 unrelated change — [...] "openspec/changes/probe-quoted/specs/caf\303\251.md" [...]   exit=1
      SPEC_RITE_BASE=base PR_BODY="" python3 scripts/validate-spec-rite.py   (95627a2)
      -> spec-rite gate: 0 findings (base base, 2 changed path(s), 1 active change(s))   exit=0
      ```

      No worktree, com o payload que o runner escreve (`{"pull_request":{"body":"Closes #172\n\nSpec-rite: harden-gate-followups\n"}}`):

      ```
      GITHUB_EVENT_PATH=event.json bash scripts/validate-rite.sh
      -> rite evidence gate: 0 findings
      -> spec-rite gate: 0 findings (base origin/master, 15 changed path(s), 1 active change(s))
      -> Totals: 3 passed, 0 failed (3 items)
      -> rite gate OK
      GITHUB_EVENT_PATH=event.json python3 scripts/validate-skill-version.py
      -> skill-version gate: 0 findings (base origin/master, 1 skill(s) changed, 1 with content changes)
      ```

      Buraco 2 — detector via `--diff`, o mesmo arquivo `vendored.diff`, antes (`findings: 2`, E.2) e
      depois (`findings: 0` + `skipped (vendored/generated/minified): 1 file(s)`, 3.1); os dois hooks
      que importam o detector, pelo próprio `--selftest` (3.4).

      Buraco 3 — selftest do validador pelo caminho do CI (`python3 scripts/selftest-validate-skills.py`):
      27/27 + `CLEAN copy byte-identical` (4.2); com a restauração neutralizada: `LEAKED` + 22/27 (4.1);
      bench alternado 3×3 (4.2).

      Buraco 4 — step literal (`yaml.safe_load` → `jobs.validate.steps[2].run`, `bash -e`): antes
      `exit=0` em `2.15.1dirtychange` (E.2); depois `exit=1` nomeando o valor, `exit=1` em vazio,
      `exit=0` em `2.30.0`, `2.31.0-beta.1` e no worktree (5.2).

      Buraco 5 — `grep -c "10 topics" README.md -> 0`; hygiene `0 findings` (6.1).

      O gate runner inteiro (`gates.sh`, os mesmos comandos do `ci.yml`) no worktree:

      ```
      PASS generate :: Generated 10 category plugins in plugins/ (descriptions derived from the tree)
      PASS version   PASS frontmatter
      PASS validate-skills :: skills checked: 36   findings: 0
      PASS selftest-validate-skills :: 27/27 defect classes detected
      PASS locale-detector :: selftest OK: 7 content tiers fire, 16 clean cases stay silent, 6 path tiers fire, 10 path cases stay silent, [...]
      PASS locale-rite   PASS backlog-rite-selftest   PASS verify-rite-selftest
      PASS scan-secrets :: no credentials found
      PASS scan-secrets-selftest :: 12/12 patterns fire on their sample, 3/3 context cases caught, 3/3 placeholder cases stayed silent
      PASS hygiene :: repo hygiene: 0 findings      PASS hygiene-selftest :: 4/4 defect classes detected
      PASS rite :: rite gate OK
      PASS rite-evidence-selftest :: 7/7 defect classes detected, 1/1 known escapes stayed silent
      PASS spec-rite-selftest :: 6/6 defect classes detected, 10/10 false-positive cases stayed silent, 6/6 reader cases correct, 2/2 path-reader cases correct
      PASS smoke :: smoke: 17/17 cases passed
      PASS plugin-validate :: ✔ Validation passed
      PASS openspec-strict harden-gate-followups :: Change 'harden-gate-followups' is valid
      ```

- [x] S.2 Matriz de casos medida, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | Tinha de disparar e disparou | 6/6 | spec-rite: probe com leitor antigo emite S3 (1); selftest do validador: restauração neutralizada → `LEAKED` (1); step: `2.15.1dirtychange` (1), vazio (1); detector antes do fix: 2 achados no hunk vendored contados como 1 (1); skill-version: 1.4.2→1.4.3 reconhecido como bump (1) |
      | Tinha de ficar mudo e ficou | 9/9 | spec-rite: clone quotado depois do fix (1), worktree pelo `validate-rite.sh` (1), probe do selftest (1); detector: hunk vendored depois do fix (1), caso do selftest (1); step: `2.30.0` (1), `2.31.0-beta.1` (1), worktree (1); hygiene no README novo (1) |
      | Versão antiga passou onde a nova falha / falhou onde a nova passa | 3/3 | step aceitou `2.15.1dirtychange`; detector mediu `node_modules/`; spec-rite reprovou o caminho quotado — cada um com a saída de `e7f5fe8` em E.2 |
      | Selftests do CI | 5/5 | spec-rite 6/6+10/10+6/6+2/2; skill-version 7/7+11/11+11/11; detector 7+16+6+10+2+5; validador 27/27; hooks locale-rite 25 e stop-gate 26 decisões |
      | Escape conhecido ficou mudo | 1/1 | `en-unknown` advisory em `filecmp`/`rmtree` (nomes da stdlib) no diff desta change: 3 avisos, `findings: 0`, exit 0 — comportamento declarado (KNOWN LIMIT 17) |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      - **A premissa do ponto 3 estava errada.** A issue diz que as 27 cópias são o custo; medido,
        são 1,9 s de 49,1 s. O ganho de parede é ~2,2 s (4 %), não uma ordem de grandeza. A cópia
        única fica pelo que compra de fato (churn, isolação provada por comparação byte a byte), e
        o custo real — 27 runs do validador — está em E.4 como follow-up. A primeira versão desta
        change rodava o validador uma 28ª vez como checagem de vazamento e ficou **mais lenta**
        (50,6 s); trocado por `filecmp`, que é a afirmação mais forte e custa milissegundos.
      - A restauração neutralizada não só disparou `LEAKED`: cinco casos C5 ficaram `MISSED`
        porque as mutações de `observability` empilharam — prova de que a reversão é o que isola,
        não só uma limpeza.
      - O step *Version coherence* rodou aqui com o bash do WSL, não com o do `ubuntu-latest`
        (E.3); `[[ =~ ]]` já roda em `generate.sh` no mesmo runner, um step antes.
      - O detector emite 3 avisos `en-unknown` em `filecmp`/`rmtree` no diff desta change —
        nomes da stdlib fora da lista de inglês; advisory por desenho, exit 0. Não adicionados a
        `programming-words.txt` por não estarem no escopo.
      - A issue cita "24 mutation classes"; são 27 em `e7f5fe8` (E.3).

## 8. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em `skills/code-locale/SKILL.md`: `PASS frontmatter` no gate runner
      (name == directory, `description: >-`, `author: solvelab`, `version: 1.4.3`, `category:
      process`, `license: MIT`, `compatibility` presente); wrappers regenerados idênticos (3.4)
- [x] Q.2 Conteúdo de skill tocado em inglês — a única edição em `SKILL.md` é a linha *Verified
      against* (data e contagem); docstring, comentários e KNOWN LIMIT do detector em inglês; os
      deltas de spec em inglês
- [x] Q.3 Gatilhos de descrição testáveis — a descrição não muda
- [x] Q.4 Sem doutrina duplicada: ver a tabela de Canonical Home em `design.md` (seis linhas, todas
      *already canonical*; `split_nul_paths()` é duplicata de código com o motivo, não de doutrina)
- [x] Q.5 Identificadores em inglês no que a change introduz (`split_nul_paths`, `vendored`,
      `original`, `ghost`, `leaked`, `SEMVER_RE`, labels de selftest)

      ```
      git diff -- scripts .github skills/code-locale/references | python3 skills/code-locale/references/check-identifier-locale.py --diff -
      -> findings: 0
      ->   en-unknown: 3 segment(s) not in the English word list — advisory — they do not fail this run   (filecmp ×2, rmtree)
      -> exit=0
      ```

## 9. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate harden-gate-followups --strict` verde

      ```
      openspec validate harden-gate-followups --strict   -> Change 'harden-gate-followups' is valid   (openspec 1.6.0)
      ```

- [x] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py` verde, 36 skills

      ```
      python3 scripts/validate-skills.py   -> skills checked: 36   findings: 0
      ls skills | wc -l                    -> 36
      ```

- [x] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo — a composição
      não muda; `README.md:443` é a única linha de docs tocada (6.1); a linha *Verified against* de
      `code-locale` reflete a contagem nova do selftest (3.4)
- [x] V.4 `openspec archive harden-gate-followups --yes` em PR separado, depois do merge


      ```
      openspec archive harden-gate-followups --yes
      -> Specs updated successfully.
      -> Change 'harden-gate-followups' archived as '2026-09-06-harden-gate-followups'.
      ```