## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `d2918ed` (topo de `master`, 2026-09-04):

      - `.github/workflows/ci.yml` — 231 linhas; `permissions` do workflow em 14-17
        (`contents: write`, `issues: write`, `pull-requests: write`); job `validate` em 25-131 com
        treze steps, nenhum escreve no repositório nem lê `GITHUB_TOKEN` (Checkout, Wrappers,
        Version coherence, Frontmatter, Content checks, Validator self-test, Locale detector
        self-test, Locale hook self-test, Secret scan, Repo hygiene, Hygiene self-test, OpenSpec
        rite gate, Evidence self-test, Spec-rite self-test, Plugin validation); step *Wrappers in
        sync* em 38-45 usa `git diff --exit-code --quiet`; *Skill frontmatter checks* em 62-84 com
        `grep -q '^name:' "$f"` sobre o arquivo inteiro; job `release` em 133-231, `outputs` em
        139-141, step `check_release` em 216-231; nenhum `timeout-minutes` em nenhum job.
      - `generate.sh:29-31` — função `frontmatter()`:
        `awk 'NR==1 && $0=="---"{inFM=1; print; next} inFM && $0=="---"{print; exit} inFM{print}'`.
      - `scripts/validate-spec-rite.py` — 338 linhas; `evaluate()` em 171-196 retorna sem achado
        quando `changes` não está vazio (`:176`); `SILENT[2]` = `("active change present", ...)` em
        `:210`; `WAIVER` em 64-67 ancorado no começo da linha; KNOWN LIMIT em 19-23.
      - `scripts/scan-secrets.py` — 132 linhas; `PATTERNS` em 26-43 (sem `github_pat_` nem `sk-`);
        `PLACEHOLDER` em 48-49 inclui `test` e `<`; `find()` em 55-64 aplica o filtro em
        `m.group(0)` e em `body[m.start()-40:m.start()]` (`:59-60`); `main()` não trata `--selftest`.
      - `scripts/validate-rite-evidence.py` — 360 linhas; `_shape_ok()` E.3/E.4 em 157-161 com
        `len(body) > 120`; `_simulation_shape_ok()` S.3 em 197-200 com o mesmo limite; KNOWN LIMIT
        1-6 em 36-51, nenhum cita o comprimento; `DEFECTS` em 318-324.
      - `scripts/validate-rite.sh` — 88 linhas; `openspec` do PATH ou
        `npx -y @fission-ai/openspec@latest` em 78-82.
      - `.gitignore` — `__pycache__/` e `*.py[cod]`; `.releaserc.json` — assets do
        `@semantic-release/git`, nenhum plugin lê output de job.
      - `openspec/specs/skills-catalog/spec.md:345-486` (*The rite gates evidence before it gates
        quality*) e `:487-524` (*The repository itself is gated, not only its skills*);
        `openspec/specs/skills-authoring/spec.md` (*The catalog carries no credentials*).
      - `openspec/changes/archive/2026-08-30-fix-release-race/{proposal,design,tasks}.md` — modelo
        de estilo; E.4 dele já registra `check_release` como ambíguo.
      - `skills/execute-backlog/references/spec-rite.md:83-84` — as duas formas da linha
        `Spec-rite:` que o corpo do PR carrega.
      - `README.md:731-739` — parágrafo que descreve o spec-rite (fica um passo atrás; ver E.4).

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      Cada buraco reproduzido antes de escrever, em `d2918ed` (2026-09-04):

      ```
      python3 -c "...; m.evaluate(['skills/backlog/SKILL.md'], ['unrelated-change'], ''); print(m.findings)"
      -> unrelated active change, no Spec-rite line -> []
      ```

      ```
      python3 -c "...; m.find('test_token = ghp_' + <36 chars>, 'x', h); print(h)"
      -> after test -> {}
      -> after < -> {}
      -> github_pat_ -> {}
      -> sk- -> {}
      python3 scripts/scan-secrets.py --selftest
      -> scanned 635 files (working tree)   (flag ignorada: o script não tem esse modo)
      ```

      ```
      python3 -c "...; pad='Checked everything carefully and thoroughly, '*4; print(len(pad), m._shape_ok('E.3', pad), m._shape_ok('E.4', pad), m._simulation_shape_ok('S.3', pad))"
      -> 180 (True, '') (True, '') (True, '')
      ```

      ```
      grep -q '^name:' <fixture SKILL.md sem name no frontmatter, com ```yaml name: fm-probe no corpo>
      -> whole-file grep: name FOUND (hole 4 reproduced)
      awk '<frontmatter() de generate.sh:29-31>' <fixture> | grep -q '^name:'
      -> frontmatter-scoped: Missing name
      ```

      ```
      gh run view --job 99719547987 -R solvelab/ai-skills --log | grep -iE "persist-credentials|fetch-depth"
      -> Validate  fetch-depth: 0
      -> Validate  persist-credentials: true
      ```

      ```
      gh run view 33463864134 --json jobs --jq '.jobs[] | "\(.name) \(.startedAt) \(.completedAt)"'
      -> Validate 2026-09-01T02:47:44Z 2026-09-01T02:48:41Z      (57s)
      gh run view 33843366162 --json jobs --jq ...
      -> Validate 2026-09-04T06:11:49Z 2026-09-04T06:17:27Z      (5m38s)
      -> Semantic Release 2026-09-04T06:17:31Z 2026-09-04T06:18:00Z   (29s)
      ```

      ```
      grep -rn "check_release\|new_release\|needs.release\|needs: \[release\]" .github .releaserc.json README.md scripts | grep -v "workflows/ci.yml"
      -> (vazio) grep exit=1
      ```

      ```
      grep -n "timeout-minutes\|persist-credentials\|permissions:\|contents:" .github/workflows/ci.yml
      -> 14:permissions:
      -> 15:  contents: write
      ```

      Medidas que sustentam as decisões do design:

      ```
      python3 - <<'EOF'   # quantos matches do tree atual só a janela de 40 chars silencia
      ... if not PLACEHOLDER.search(token) and PLACEHOLDER.search(before): suppressed[name]+=1
      EOF
      -> {}
      ```

      ```
      grep -rnE "sk-[A-Za-z0-9_-]{20,}|github_pat_[A-Za-z0-9_]{20,}" --include='*.md' --include='*.py' ... .
      -> (vazio) exit=0
      ```

      ```
      openspec --version                                  -> 1.6.0
      npx -y @fission-ai/openspec@1.6.0 --version         -> 1.6.0
      npm view @fission-ai/openspec version               -> 1.12.0   (o @latest de hoje)
      python3 --version                                   -> Python 3.14.5
      ls skills | wc -l                                   -> 35
      openspec new change close-ci-gate-holes --schema skills-rite
      -> Created change 'close-ci-gate-holes' at openspec/changes/close-ci-gate-holes/  (só .openspec.yaml; artefatos escritos a partir de openspec/schemas/skills-rite/templates/)
      openspec validate close-ci-gate-holes --strict      -> Change 'close-ci-gate-holes' is valid
      ```

- [x] E.3 O que não pôde ser probado

      - O efeito de `permissions: contents: read` + `persist-credentials: false` **na run real do
        CI** não pode ser medido localmente: é medido na run do PR desta change, e o resultado entra
        em S.1 quando existir. Até lá, a afirmação "nenhum step de Validate escreve" é leitura dos
        treze steps (E.1), não observação de run.
      - O `awk` do GitHub runner (`ubuntu-latest`, mawk ou gawk) não foi probado; o mesmo programa
        `awk` já roda em `generate.sh` no mesmo runner a cada build, então a sintaxe está coberta pelo
        step anterior.
      - A janela de 40 caracteres foi medida como irrelevante **no tree de hoje**; um tree futuro
        pode ter um match que só ela silenciava, e aí o scan reprova nomeando o arquivo — que é o
        comportamento desejado, não um gap.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #117 pediu e nada além. Notados pelo caminho e **não** feitos, como
      follow-up:

      - `README.md:731-739` descreve o spec-rite como "carry an active change" — depois desta change
        a regra é relevância (tocar ou nomear a change). `README.md` não está entre os arquivos deste
        item; corrigir o parágrafo é follow-up.
      - O step `Get previous tag` (`prev_tag`) do job de release fica sem leitor depois da remoção de
        `check_release`; não está na lista de steps deste item e fica como está.
      - Pinar actions por SHA (`actions/checkout@v5` etc.) — fora de escopo pela issue.
      - O `openspec` do PATH local continua sendo o que roda em `validate-rite.sh` quando existe; o
        pin só governa o caminho `npx` (o do CI). Alinhar os dois exigiria exigir versão exata do
        binário local, decisão de manutenção fora deste item.

## 2. Wrappers in sync vê arquivo não rastreado (D1)

- [x] 2.1 O step falha quando `git status --porcelain` devolve qualquer linha depois de
      `bash generate.sh`, com `::error::` nomeando os arquivos `??` separadamente dos modificados

      Medido em cópia independente do worktree (`42591ee`, 2026-09-04): shell do step extraído
      literalmente de `ci.yml` (`yaml.safe_load` -> `jobs.validate.steps[1].run`) e rodado com
      `bash -e`, como o runner faz. Detalhe em S.1.

      ```
      bash -e step-new-wrappers-in-sync-with-skills.sh   # após commitar skills/backlog/references/zz.md
      -> ::error::generate.sh produced files that are not tracked. Add them and commit:
      -> ?? plugins/workflow/skills/backlog/references/zz.md
      -> exit=1
      ```

- [x] 2.2 O caso antigo (arquivo rastreado modificado) continua falhando com a mensagem antiga

      ```
      echo "stale line" >> plugins/workflow/skills/backlog/SKILL.md && git commit -qam "probe: stale wrapper"
      bash -e step-new-wrappers-in-sync-with-skills.sh
      -> ::error::Generated wrappers are out of sync. Run ./generate.sh and commit the result.
      ->  plugins/workflow/skills/backlog/SKILL.md | 1 -
      -> exit=1
      ```

## 3. Spec-rite exige relevância (D2)

- [x] 3.1 `NAMED_CHANGE` lê `Spec-rite: <id>` ancorado no começo da linha, sem casar `none`

      ```
      python3 -c "...; print(m.named_changes('Spec-rite: none — reason'))"          -> []
      python3 -c "...; print(m.named_changes('see Spec-rite: close-ci-gate-holes mid-line'))"  -> []
      python3 -c "...; print(m.named_changes('- Spec-rite: close-ci-gate-holes'))"   -> ['close-ci-gate-holes']
      ```

- [x] 3.2 `evaluate()` registra o diff só por caminho tocado, nome no corpo, archive no diff ou
      dispensa; caso contrário emite `S3 unrelated change` nomeando as changes ativas

      `evaluate()` importado de `scripts/validate-spec-rite.py` em `42591ee` e chamado com entradas
      sintéticas (`annotate = False`); o mesmo primeiro caso contra a versão de `d2918ed`:

      ```
      evaluate(['skills/backlog/SKILL.md'], ['close-ci-gate-holes'], '')
      -> findings=['S3 unrelated change: this diff touches 1 path(s) outside openspec/ — skills/backlog/SKILL.md — and 1 active change(s) exist (close-ci-gate-holes), but the diff touches none of their directories and the pull request body names none of them. [...]']
      evaluate(mesmo diff, mesma change, 'Closes #117\n\nSpec-rite: close-ci-gate-holes\n')
      -> findings=[]
      evaluate(['openspec/changes/archive/2026-09-04-x/tasks.md', 'README.md'], ['close-ci-gate-holes'], '')
      -> findings=[]
      evaluate(['scripts/x.py', 'openspec/changes/close-ci-gate-holes/tasks.md'], ['close-ci-gate-holes'], '')
      -> findings=[]
      evaluate(['skills/backlog/SKILL.md'], ['close-ci-gate-holes'], 'Spec-rite: fix-release-race')
      -> findings=['S3 unrelated change: [...]; the body names fix-release-race, which is not an active change. [...]']
      master (d2918ed) evaluate(['skills/backlog/SKILL.md'], ['close-ci-gate-holes'], '')
      -> []                                              (o buraco 2, reproduzido na versão antiga)
      ```

- [x] 3.3 Selftest: "active change present" sai de `SILENT` e entra em `DEFECTS`; `SILENT` ganha
      "active change touched in the diff", "active change named in the body" e "archive with an
      unrelated active change"; um id nomeado que não está ativo é achado

      ```
      python3 scripts/validate-spec-rite.py --selftest
      -> CAUGHT  S3 unrelated change: ''
      -> CAUGHT  S3 unrelated change: 'Spec-rite: some-archived-change'
      -> CAUGHT  S3 unrelated change: 'see the Spec-rite: add-spec-rite-gate line elsewhere'
      -> SILENT  active change touched in the diff
      -> SILENT  active change named in the body
      -> SILENT  archived with an unrelated active change
      -> 6/6 defect classes detected, 10/10 false-positive cases stayed silent, 6/6 reader cases correct
      -> exit=0
      ```

- [x] 3.4 Docstring: regra `S3` listada ao lado de `S1`/`S2`; KNOWN LIMIT diz que relevância é por
      caminho e por nome, não por conteúdo

      ```
      grep -n "S3 \|KNOWN LIMIT" scripts/validate-spec-rite.py
      -> 18:  S3 the change it carries is ITS change: the diff touches openspec/changes/<id>/ of an active
      -> 23:KNOWN LIMIT: this proves that a change EXISTS and is LINKED to the diff — by path or by name, never
      ```

## 4. Secret scan ganha selftest e fecha o filtro (D3)

- [x] 4.1 `PLACEHOLDER` aplicado só a `m.group(0)`; a janela de 40 caracteres anteriores sai

      `find()` de `d2918ed` e de `42591ee` chamados sobre o mesmo corpo (tokens montados em runtime):

      ```
      test_token = <ghp_…36>      master=[]  new=['GitHub token']
      <ghp_…36> entre < >         master=[]  new=['GitHub token']
      ghp_ + 'x'*36               master=[]  new=[]          (placeholder no próprio token: mudo)
      postgres://app:<password>@  master=[]  new=[]
      ```

- [x] 4.2 Padrões `github_pat_` e `sk-` em `PATTERNS`

      ```
      github_pat_ + 30 chars      master=[]  new=['GitHub fine-grained token']
      sk- + 24 chars              master=[]  new=['sk- API key']
      PATTERNS master: 10 new: 12 added: ['GitHub fine-grained token', 'sk- API key']
      ```

- [x] 4.3 `--selftest`: uma amostra montada em runtime por padrão, mais `test_token = <token>` e
      `<token>`; casos mudos (`xxx`, `<password>`, IP privado sem gatar); saída `n/n`

      ```
      python3 scripts/scan-secrets.py --selftest
      -> CAUGHT  token after the word test
      -> CAUGHT  token between angle brackets
      -> SILENT  token that is itself a placeholder
      -> SILENT  connection string with a <password> placeholder
      -> REPORTED  private IPv4 is reported, never a credential
      -> 12/12 patterns fire on their sample, 3/3 context cases caught, 3/3 placeholder cases stayed silent
      -> exit=0
      ```

- [x] 4.4 Docstring declara o modo e o que o selftest não prova (não lê o tree, não julga
      placeholders que a documentação inventar)

      ```
      grep -n "selftest\|MATCHED TOKEN ONLY\|KNOWN LIMIT" scripts/scan-secrets.py | head -3
      -> 13:  --selftest    inject one credential per pattern and assert each class is reported. Gates
      -> 22:The placeholder filter applies to the MATCHED TOKEN ONLY. It used to also read the forty
      -> 26:KNOWN LIMIT: the selftest proves each pattern fires on its own sample and stays silent on the
      ```

- [x] 4.5 `ci.yml`: step *Secret scan self-test (the gate is itself gated)* logo depois de *Secret
      scan (working tree)*

      ```
      python3 -c "import yaml; print([s['name'] for s in yaml.safe_load(open('.github/workflows/ci.yml'))['jobs']['validate']['steps']])"
      -> [..., 'Secret scan (working tree)', 'Secret scan self-test (the gate is itself gated)', 'Repo hygiene (compiled artifacts, published counts)', ...]
      bash -e step-new-secret-scan-self-test.sh   (run: do step, literal)
      -> 12/12 patterns fire on their sample, 3/3 context cases caught, 3/3 placeholder cases stayed silent   exit=0
      ```

## 5. Frontmatter greps escopados ao bloco (D4)

- [x] 5.1 O step extrai o bloco com o `awk` literal de `generate.sh:29-31` uma vez por arquivo e todos
      os greps rodam sobre ele; o check de primeira linha fica

      Fixture `skills/fm-probe/SKILL.md` na cópia: frontmatter completo **sem** `name:`, corpo com um
      bloco ```yaml contendo `name: fm-probe`. Shell dos dois steps extraído literalmente:

      ```
      bash -e step-master-skill-frontmatter-checks.sh   (d2918ed)
      -> exit=0, 0 linhas ::error, nenhuma linha nomeia fm-probe        (buraco 4 reproduzido)
      bash -e step-new-skill-frontmatter-checks.sh      (42591ee)
      -> ::error file=skills/fm-probe/SKILL.md::Missing name
      -> ::error file=skills/fm-probe/SKILL.md::name '' != directory 'fm-probe'
      -> exit=1
      bash -e step-new-skill-frontmatter-checks.sh      (worktree, 35 skills reais)
      -> exit=0
      ```

## 6. Privilégio mínimo e pins (D5)

- [x] 6.1 `permissions: contents: read` no job `validate`; bloco do workflow intocado (serve o release)

      ```
      python3 -c "import yaml; d=yaml.safe_load(open('.github/workflows/ci.yml')); print(d['permissions'], d['jobs']['validate']['permissions'])"
      -> {'contents': 'write', 'issues': 'write', 'pull-requests': 'write'} {'contents': 'read'}
      ```

      O efeito na run real (nenhum step de `Validate` precisando de escrita) só se mede na run do PR;
      ver E.3 e S.3.

- [x] 6.2 `persist-credentials: false` no checkout do `validate`, com o motivo no comentário

      ```
      python3 -c "...; print(d['jobs']['validate']['steps'][0]['with'])"
      -> {'fetch-depth': 0, 'persist-credentials': False}
      grep -n "persist-credentials" .github/workflows/ci.yml
      -> 41:        # persist-credentials: false — the token is needed for the fetch and for nothing after it.
      -> 47:          persist-credentials: false
      ```

- [x] 6.3 `scripts/validate-rite.sh`: `npx -y @fission-ai/openspec@1.6.0` com comentário de bump

      ```
      grep -n "openspec@" scripts/validate-rite.sh
      -> 81:# `npx -y @fission-ai/openspec@<new> validate --all --strict` locally, then change the version here
      -> 87:  npx -y @fission-ai/openspec@1.6.0 validate --all --strict || fail=1
      npx -y @fission-ai/openspec@1.6.0 --version   -> 1.6.0   exit=0
      ```

## 7. Higiene do workflow (D6)

- [x] 7.1 `timeout-minutes: 15` nos dois jobs, com as medições no comentário

      ```
      python3 -c "...; print(d['jobs']['validate']['timeout-minutes'], d['jobs']['release']['timeout-minutes'])"
      -> 15 15
      grep -n "timeout-minutes\|Measured" .github/workflows/ci.yml
      -> 34:    # Measured 57s (run 33463864134) to 5m38s (run 33843366162). Without a ceiling a hung `npx`
      -> 36:    timeout-minutes: 15
      -> 171:    # Measured 29s (run 33843366162); the ceiling exists for a hung npm install, not for the work.
      -> 172:    timeout-minutes: 15
      ```

- [x] 7.2 `outputs` do job `release` e step `check_release` removidos, com o motivo no commit

      ```
      python3 -c "...; print(d['jobs']['release'].get('outputs'), [s.get('id') for s in d['jobs']['release']['steps']])"
      -> None [None, 'prev_tag', None, None, None, None, None]        (em d2918ed: outputs com 2 chaves e id 'check_release' no fim)
      grep -c "check_release\|new_release\|outputs:" .github/workflows/ci.yml   -> 0
      git log -1 --format=%b 42591ee | grep -c "check_release"                -> 1
      ```

## 8. Escape dos 120 caracteres declarado e coberto (D7)

- [x] 8.1 KNOWN LIMIT 7 em `validate-rite-evidence.py` nomeia o limite e o que ele deixa passar

      ```
      sed -n 52,56p scripts/validate-rite-evidence.py
      ->   7. E.3, E.4 and S.3 accept any body longer than 120 characters as "names a gap / a follow-up /
      ->      an escape", with no negative word required. [...] What it lets through: 121 characters of padding that name nothing.
      ```

- [x] 8.2 `ESCAPES` no selftest com o caso E.3 de 130 caracteres sem gap; resultado esperado mudo;
      saída `n/n known escapes stayed silent`

      ```
      python3 scripts/validate-rite-evidence.py --selftest
      -> ESCAPED R1 evidence shape: E.3 padded past 120 characters names no gap   (silent, as KNOWN LIMIT 7 declares)
      -> 7/7 defect classes detected, 1/1 known escapes stayed silent
      -> exit=0
      ```

## 9. Simulation & Field Proof (MANDATORY)

- [x] S.1 Cada gate exercitado pelo caminho real (o step do CI ou o script como o CI o invoca), com
      a saída observada registrada

      Tudo em `42591ee` (2026-09-04). Os steps de `ci.yml` foram extraídos com `yaml.safe_load`
      (`jobs.validate.steps[*].run`, das duas versões: `d2918ed` e `42591ee`) para arquivos
      `step-<versão>-<nome>.sh` e rodados com `bash -e`, o shell padrão de um `run:` no runner.
      As reproduções que sujam a árvore rodaram numa **cópia** independente do worktree (`cp -r`
      seguido de troca do ponteiro `.git` por um clone do mesmo HEAD, porque o `.git` de um worktree
      é um ponteiro para o índice do worktree real); o worktree ficou limpo o tempo todo
      (`git status --porcelain | wc -l -> 0` antes e depois).

      Buraco 1 — wrappers (cópia):

      ```
      bash generate.sh; git status --porcelain --untracked-files=all | wc -l      -> 0   (baseline)
      printf '# zz probe\n' > skills/backlog/references/zz.md; git add; git commit -qm "probe: add reference"
      bash -e step-master-wrappers-in-sync-with-skills.sh   (d2918ed)
      -> Generated 10 category plugins in plugins/
      -> exit=0                                            (o buraco: passou)
      git status --porcelain --untracked-files=all
      -> ?? plugins/workflow/skills/backlog/references/zz.md
      bash -e step-new-wrappers-in-sync-with-skills.sh      (42591ee)
      -> ::error::generate.sh produced files that are not tracked. Add them and commit:
      -> ?? plugins/workflow/skills/backlog/references/zz.md
      -> exit=1
      ```

      Skill nova inteira (`skills/zz-probe/SKILL.md` commitada) continua falhando nas duas versões,
      e a nova nomeia os cinco arquivos gerados:

      ```
      bash -e step-master-wrappers-in-sync-with-skills.sh -> exit=1  ::error::Generated wrappers are out of sync. [...]
      bash -e step-new-wrappers-in-sync-with-skills.sh    -> exit=1  5 linhas `??` (claude/, codex/, copilot/, cursor/, plugins/tooling/) + as duas ::error::
      ```

      Buraco 2 — spec-rite: `evaluate()` com diff de `skills/` e change ativa alheia -> achado `S3`;
      com `Spec-rite: close-ci-gate-holes` no corpo -> mudo; diff só de archive -> mudo (saídas em
      3.2). Pelo caminho do CI, no worktree, com o payload que o runner escreve:

      ```
      printf '{"pull_request":{"body":"Closes #117\n\nSpec-rite: close-ci-gate-holes\n"}}' > event.json
      GITHUB_EVENT_PATH=event.json bash scripts/validate-rite.sh
      -> rite evidence gate: 0 findings
      -> spec-rite gate: 0 findings (base origin/master, 11 changed path(s), 1 active change(s))
      -> Totals: 3 passed, 0 failed (3 items)
      -> rite gate OK
      PR_BODY="" python3 scripts/validate-spec-rite.py        (sem a linha: registra-se por caminho, D2-a)
      -> spec-rite gate: 0 findings (base origin/master, 11 changed path(s), 1 active change(s))
      ```

      Buraco 3 — scan-secrets: `find()` das duas versões sobre `test_token = ghp_…` (4.1) e o
      selftest pelo step literal (4.5). Scan real do tree pelo step literal:

      ```
      bash -e step-new-secret-scan.sh   -> no credentials found   exit=0
      ```

      Buraco 4 — frontmatter: fixture com `name:` só em bloco de código (5.1): `d2918ed` exit=0 sem
      nenhum `::error`; `42591ee` exit=1 com `Missing name`.

      Buracos 5 e 6 — YAML de `ci.yml` parseado com `yaml.safe_load` nas duas versões:

      ```
      d2918ed: validate.permissions=None validate.timeout-minutes=None release.timeout-minutes=None
               release.outputs={'new_release': '${{ steps.check_release.outputs.new_release }}', 'version': ...}
               validate checkout with={'fetch-depth': 0}
      42591ee: validate.permissions={'contents': 'read'} validate.timeout-minutes=15 release.timeout-minutes=15
               release.outputs=None  validate checkout with={'fetch-depth': 0, 'persist-credentials': False}
      ```

      Buraco 7 — evidence gate: selftest pelo step literal, com o escape declarado:

      ```
      bash -e step-new-rite-evidence-self-test.sh
      -> ESCAPED R1 evidence shape: E.3 padded past 120 characters names no gap   (silent, as KNOWN LIMIT 7 declares)
      -> 7/7 defect classes detected, 1/1 known escapes stayed silent   exit=0
      ```

      Os steps de `Validate` que este item toca, todos literais, no worktree:

      ```
      step-new-wrappers-in-sync-with-skills  exit=0 :: Generated 10 category plugins in plugins/
      step-new-version-coherence             exit=0 :: Version 2.16.0 coherent across manifests.
      step-new-skill-frontmatter-checks      exit=0
      step-new-secret-scan                   exit=0 :: no credentials found
      step-new-secret-scan-self-test         exit=0 :: 12/12 patterns fire on their sample, 3/3 context cases caught, 3/3 placeholder cases stayed silent
      step-new-rite-evidence-self-test       exit=0 :: 7/7 defect classes detected, 1/1 known escapes stayed silent
      step-new-spec-rite-self-test           exit=0 :: 6/6 defect classes detected, 10/10 false-positive cases stayed silent, 6/6 reader cases correct
      git status --porcelain --untracked-files=all | wc -l   -> 0
      ```

- [x] S.2 Matriz de casos medida, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | Tinha de disparar e disparou | 9/9 | wrappers: ref nova (1), skill nova (1), wrapper stale (1); spec-rite `S3`: change alheia (1), id não ativo (1); scan-secrets: `test_token =` (1), `< >` (1); frontmatter: fixture (1); evidence: 7/7 do selftest contados como 1 |
      | Tinha de ficar mudo e ficou | 8/8 | wrappers: tree limpo (1); spec-rite: nomeada no corpo (1), archive+README (1), tick em tasks.md (1), branch real por caminho (1); scan-secrets: `ghp_xxx…` (1), `<password>` (1); frontmatter: 35 skills reais (1) |
      | Versão antiga passou onde a nova falha | 4/4 | wrappers ref nova, spec-rite change alheia, scan-secrets após `test`, frontmatter em bloco de código — cada um com `exit=0`/`[]` em `d2918ed` |
      | Escape conhecido ficou mudo | 1/1 | E.3 com 130 caracteres sem gap (`ESCAPED … silent`) |
      | Selftests do CI | 3/3 | spec-rite 6/6+10/10+6/6; scan-secrets 12/12+3/3+3/3; evidence 7/7+1/1 |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      - `permissions: contents: read` e `persist-credentials: false` **não** foram exercitados pelo
        caminho real: o efeito só existe no runner do GitHub. Localmente o que se prova é o YAML
        (6.1, 6.2) e a leitura dos steps (E.1: nenhum escreve). A prova é a run do PR desta change:
        `Validate` verde com `persist-credentials: false` no log do checkout. Até ela, é gap.
      - `timeout-minutes` idem: só o YAML é provável localmente.
      - O `awk` do step de frontmatter rodou aqui com o awk do WSL, não com o do `ubuntu-latest`
        (E.3); o mesmo programa já roda em `generate.sh` no mesmo runner.
      - A fixture do buraco 4 dispara **dois** achados na versão nova (`Missing name` e
        `name '' != directory`), não um: o segundo grep lê o mesmo bloco vazio. Esperado era um;
        o segundo é redundante mas correto, e fica.
      - Escape declarado e medido: E.3/E.4/S.3 com mais de 120 caracteres sem gap nomeado passam
        (KNOWN LIMIT 7, `1/1 known escapes stayed silent`). A relevância do spec-rite é por caminho
        e por nome: um tick qualquer em `tasks.md` de uma change ativa registra qualquer diff (KNOWN
        LIMIT do script). Nenhum dos dois é fechado por esta change, por desenho (D2, D7).

## 10. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — não se aplica: nenhuma skill é tocada
      (`git diff --name-only origin/master...HEAD | grep -c '^skills/'` -> 0)
- [x] Q.2 Conteúdo de skill tocado em inglês — não se aplica; os deltas de spec estão em inglês
- [x] Q.3 Gatilhos de descrição testáveis — não se aplica: nenhuma descrição muda
- [x] Q.4 Sem doutrina duplicada: ver a tabela de Canonical Home em `design.md` (cinco linhas, todas
      *already canonical*; nenhuma skill editada)
- [x] Q.5 Identificadores em inglês no que a change introduz — ids de step, nomes de função,
      labels de selftest, chaves de YAML (`code-locale`)

      ```
      git diff origin/master...HEAD -- .github scripts | python3 skills/code-locale/references/check-identifier-locale.py --diff -
      -> findings: 0   exit=0
      ```

## 11. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate close-ci-gate-holes --strict` verde

      ```
      openspec validate close-ci-gate-holes --strict   -> Change 'close-ci-gate-holes' is valid   (openspec 1.6.0)
      ```

- [x] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py` verde, 35 skills

      ```
      python3 scripts/validate-skills.py   -> skills checked: 35   findings: 0
      ls skills | wc -l                    -> 35
      ```

- [x] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo — a composição
      não muda; o parágrafo do spec-rite no README é follow-up (E.4)
- [ ] V.4 `openspec archive close-ci-gate-holes --yes` em PR separado, depois do merge
