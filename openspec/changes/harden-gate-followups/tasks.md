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
        antes/depois é transferível.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #172 pediu e nada além. Notados pelo caminho e **não** feitos, como
      follow-up:

      - `scripts/validate-repo-hygiene.py:91-94` cita `README.md:345 carries (10 topics)` como
        exemplo do que H2 não lê; depois desta change o exemplo não existe mais. O arquivo não está
        na lista deste item; atualizar a docstring é follow-up.
      - `claude/global/hooks/locale-stop-gate.py:296` filtra `is_vendored` nos achados por fora;
        com D2 o filtro fica redundante (o detector já não produz esses achados). Remover é do dono
        do hook, não deste item.
      - `validate-skill-version.py` poderia importar `split_nul_paths()` do spec-rite em vez de
        definir o seu (a direção de import que não fecha ciclo); não está na lista deste item.
      - `scripts/validate-repo-hygiene.py:252` e `scripts/validate-rite-evidence.py:353` também
        fazem `copytree` do repositório no selftest (uma vez cada, não por caso); fora de escopo.

## 2. Spec-rite lê o diff com `-z` (D1)

- [ ] 2.1 `changed_paths()` roda `git diff --name-only -z` e separa por NUL com `split_nul_paths()`,
      duplicado de `validate-skill-version.py` com comentário nomeando o irmão e o motivo
- [ ] 2.2 Selftest: caso literal do helper (aspas, quebra de linha) e probe em repositório
      descartável com `core.quotePath=true` — caminho não-ASCII dentro de `openspec/changes/<id>/`
      registra o diff (`evaluate()` mudo)
- [ ] 2.3 Docstring: o parágrafo sobre `-z` e o que o modo de linha fazia com o caminho

## 3. `scan_diff()` aplica `is_vendored()` (D2)

- [ ] 3.1 `scan_diff()` pula o bloco inteiro de um `+++` vendored e devolve o caminho na lista
      `vendored` (parâmetro opcional); `main()` imprime na linha `skipped (vendored/...)` existente
- [ ] 3.2 Selftest: diff que adiciona `node_modules/servicos_pedido/calculo.js` com `const usuario`
      fica mudo e conta um pulado; contagem do `selftest OK` atualizada
- [ ] 3.3 KNOWN LIMIT 12 diz o que o modo `--diff` pula (por caminho; `is_minified` não roda)
- [ ] 3.4 `code-locale` 1.4.2 → 1.4.3, linha *Verified against* re-probada; `./generate.sh` regenera
      os wrappers; `locale-rite.py --selftest` e `locale-stop-gate.py --selftest` verdes depois da
      edição

## 4. Selftest do validador em uma cópia (D3)

- [ ] 4.1 Uma `copytree` por run; cada mutação guarda bytes (ou ausência), aplica, roda, restaura em
      `finally`; C7 remove o diretório, C11 remove o arquivo
- [ ] 4.2 27/27 `CAUGHT`; validador limpo na cópia depois do laço; tempo antes/depois registrado

## 5. `VERSION` validado no step *Version coherence* (D4)

- [ ] 5.1 `SEMVER_RE` (literal de `generate.sh:32`) aplicado a `VERSION` antes do laço dos
      manifests, `::error` nomeando o valor
- [ ] 5.2 Step extraído do YAML novo e rodado contra a fixture `2.15.1dirtychange` (reprova), contra
      uma fixture `2.30.0` e `2.31.0-beta.1` (passam) e no worktree (passa)

## 6. README sem contagem na árvore (D5)

- [ ] 6.1 `README.md:443` sem `(10 topics)`; `validate-repo-hygiene.py` verde

## 7. Simulation & Field Proof (MANDATORY)

- [ ] S.1 Cada gate exercitado pelo caminho real (o script como o CI o invoca, o step literal do
      `ci.yml`, o detector via `--diff`), antes e depois, com a saída observada registrada
- [ ] S.2 Matriz de casos medida, em contagens
- [ ] S.3 O que escapou ou se comportou diferente do esperado

## 8. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado (`code-locale`): name == directory,
      description folded, author solvelab, semver, category no conjunto, license MIT, compatibility
- [ ] Q.2 Conteúdo de skill tocado em inglês (catalog locale)
- [ ] Q.3 Gatilhos de descrição testáveis — a descrição não muda
- [ ] Q.4 Sem doutrina duplicada: ver a tabela de Canonical Home em `design.md`
- [ ] Q.5 Identificadores em inglês no que a change introduz (`code-locale`)

## 9. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate harden-gate-followups --strict` verde
- [ ] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py` verde, 35 skills
- [ ] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo
- [ ] V.4 `openspec archive harden-gate-followups --yes` em PR separado, depois do merge
