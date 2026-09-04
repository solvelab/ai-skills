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

- [ ] 2.1 O step falha quando `git status --porcelain` devolve qualquer linha depois de
      `bash generate.sh`, com `::error::` nomeando os arquivos `??` separadamente dos modificados
- [ ] 2.2 O caso antigo (arquivo rastreado modificado) continua falhando com a mensagem antiga

## 3. Spec-rite exige relevância (D2)

- [ ] 3.1 `NAMED_CHANGE` lê `Spec-rite: <id>` ancorado no começo da linha, sem casar `none`
- [ ] 3.2 `evaluate()` registra o diff só por caminho tocado, nome no corpo, archive no diff ou
      dispensa; caso contrário emite `S3 unrelated change` nomeando as changes ativas
- [ ] 3.3 Selftest: "active change present" sai de `SILENT` e entra em `DEFECTS`; `SILENT` ganha
      "active change touched in the diff", "active change named in the body" e "archive with an
      unrelated active change"; um id nomeado que não está ativo é achado
- [ ] 3.4 Docstring: regra `S3` listada ao lado de `S1`/`S2`; KNOWN LIMIT diz que relevância é por
      caminho e por nome, não por conteúdo

## 4. Secret scan ganha selftest e fecha o filtro (D3)

- [ ] 4.1 `PLACEHOLDER` aplicado só a `m.group(0)`; a janela de 40 caracteres anteriores sai
- [ ] 4.2 Padrões `github_pat_` e `sk-` em `PATTERNS`
- [ ] 4.3 `--selftest`: uma amostra montada em runtime por padrão, mais `test_token = <token>` e
      `<token>`; casos mudos (`xxx`, `<password>`, IP privado sem gatar); saída `n/n`
- [ ] 4.4 Docstring declara o modo e o que o selftest não prova (não lê o tree, não julga
      placeholders que a documentação inventar)
- [ ] 4.5 `ci.yml`: step *Secret scan self-test (the gate is itself gated)* logo depois de *Secret
      scan (working tree)*

## 5. Frontmatter greps escopados ao bloco (D4)

- [ ] 5.1 O step extrai o bloco com o `awk` literal de `generate.sh:29-31` uma vez por arquivo e todos
      os greps rodam sobre ele; o check de primeira linha fica

## 6. Privilégio mínimo e pins (D5)

- [ ] 6.1 `permissions: contents: read` no job `validate`; bloco do workflow intocado (serve o release)
- [ ] 6.2 `persist-credentials: false` no checkout do `validate`, com o motivo no comentário
- [ ] 6.3 `scripts/validate-rite.sh`: `npx -y @fission-ai/openspec@1.6.0` com comentário de bump

## 7. Higiene do workflow (D6)

- [ ] 7.1 `timeout-minutes: 15` nos dois jobs, com as medições no comentário
- [ ] 7.2 `outputs` do job `release` e step `check_release` removidos, com o motivo no commit

## 8. Escape dos 120 caracteres declarado e coberto (D7)

- [ ] 8.1 KNOWN LIMIT 7 em `validate-rite-evidence.py` nomeia o limite e o que ele deixa passar
- [ ] 8.2 `ESCAPES` no selftest com o caso E.3 de 130 caracteres sem gap; resultado esperado mudo;
      saída `n/n known escapes stayed silent`

## 9. Simulation & Field Proof (MANDATORY)

- [ ] S.1 Cada gate exercitado pelo caminho real (o step do CI ou o script como o CI o invoca), com
      a saída observada registrada
- [ ] S.2 Matriz de casos medida, em contagens
- [ ] S.3 O que escapou ou se comportou diferente do esperado

## 10. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — não se aplica: nenhuma skill é tocada
- [ ] Q.2 Conteúdo de skill tocado em inglês — não se aplica; os deltas de spec estão em inglês
- [ ] Q.3 Gatilhos de descrição testáveis — não se aplica: nenhuma descrição muda
- [ ] Q.4 Sem doutrina duplicada: ver a tabela de Canonical Home em `design.md`
- [ ] Q.5 Identificadores em inglês no que a change introduz — ids de step, nomes de função,
      labels de selftest, chaves de YAML (`code-locale`)

## 11. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate close-ci-gate-holes --strict` verde
- [ ] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py` verde, 35 skills
- [ ] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo — a composição
      não muda; o parágrafo do spec-rite no README é follow-up (E.4)
- [ ] V.4 `openspec archive close-ci-gate-holes --yes` em PR separado, depois do merge
