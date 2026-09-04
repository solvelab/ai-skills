## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `d2918ed` (topo de `master` em 2026-09-04, worktree da issue #114):

      - `generate.sh` — 201 linhas; `GROUP_DESC` em 150-161, `group_of` em 163-168, cópia dos
        skills em 170-178, `VERSION_STR` em 180 (`tr -d '[:space:]' ... || echo 0.0.0`), heredoc
        do `plugin.json` em 185-195 com o fallback `:-Skill group ${group}` na 190.
      - `scripts/set-version.sh` — 29 linhas; regex sem âncora final na 13
        (`^[0-9]+\.[0-9]+\.[0-9]+`), `sed` da versão nos dois JSON em 18-19, `bash generate.sh`
        na 22, coerência em 25-27.
      - `scripts/validate-repo-hygiene.py` — 147 linhas; `COUNT_FILES` na 30, `COUNT_CLAIM`
        (`\ball (\d+)\b`) na 31, H1 em 50-61, H2 em 64-84, `DEFECTS` em 109-110, `selftest` em
        113-132.
      - `.claude-plugin/marketplace.json` — 79 linhas; `"version": "2.16.0"` na 9, bundle
        `ai-skills` com `source: "./"` e `all 35 skills` na 15, `game` "(12 topics)" na 45.
      - `.claude-plugin/plugin.json` — 22 linhas; `"version": "2.16.0"` na 4, description com
        "React Three Fiber (10 topics)" na 5.
      - `plugins/game/.claude-plugin/plugin.json` — description "React Three Fiber skills (10 topics)".
      - `README.md` — 50-55 (parágrafo dos plugins, `all 35` na 55), 345 (`(10 topics)` dentro do
        bloco ``` aberto na 329), 504-509 (tabela Frontend), 537-548 (tabela Game com
        `svg-animation` na primeira linha e o cabeçalho "10 topics").
      - `skills/svg-animation/SKILL.md:18` — `category: frontend`.
      - `.releaserc.json` — `prepareCmd: bash scripts/set-version.sh ${nextRelease.version}`;
        assets incluem `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugins/**`.
      - `.github/workflows/ci.yml` — 25-129 (job `validate`): *Wrappers in sync* em 36-43 roda
        `generate.sh` antes de *Version coherence* em 45-54; hygiene em 99-103; plugin validate
        pinado em `2.1.246` na 129. Lido e **não editado** (fora do escopo desta execução).
      - `openspec/specs/skills-catalog/spec.md:487-524` — requisito *The repository itself is
        gated, not only its skills*, copiado integralmente no delta.
      - `openspec/config.yaml` — `schema: skills-rite`.
      - `openspec/changes/archive/2026-08-30-fix-release-race/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md` — modelo de estilo da casa.

- [x] E.2 Ferramentas e comportamentos externos probados contra a versão instalada

      ```
      openspec --version
      -> 1.6.0
      python3 --version
      -> Python 3.14.5
      claude --version
      -> 2.1.260 (Claude Code)
      ```

      ```
      openspec new change derive-plugin-descriptions --schema skills-rite
      -> Created change 'derive-plugin-descriptions' at openspec/changes/derive-plugin-descriptions/
      -> Schema: skills-rite
      ```

      Regex ancorada em `[[ =~ ]]` (bash 5.2.37), guardada em variável:

      ```
      probe.sh   # SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'
      -> ACCEPT '2.16.0'
      -> ACCEPT '1.2.3-rc.1'
      -> REJECT '1.2.3garbage'
      -> REJECT '2.15.1dirtychange'
      -> REJECT ''
      -> REJECT '1.2'
      ```

      Chave ausente em array associativo sob `set -u`, e `[[ -v ]]`:

      ```
      probe.sh   # declare -A T=([a]=x); [[ -v T[zz] ]]; echo "${T[zz]}"
      -> -v unset: no
      -> line 12: T[zz]: unbound variable
      -> unset key under -u -> exit 1
      ```

      Fidelidade do round-trip JSON que D3 usa para reescrever os dois manifestos da raiz:

      ```
      python3 probe_json.py   # json.dumps(json.loads(raw), indent=2, ensure_ascii=False) + "\n" == raw ?
      -> .claude-plugin/marketplace.json identical
      -> .claude-plugin/plugin.json identical
      ```

      Ordem determinística dos nomes de um grupo:

      ```
      ls -1 plugins/game/skills | LC_ALL=C sort | paste -sd, - | sed 's/,/, /g'
      -> assettoserver-csp-lua, assettoserver-plugin, r3f-animation, r3f-assets, r3f-fundamentals, r3f-geometry, r3f-interaction, r3f-lighting, r3f-materials, r3f-physics, r3f-postprocessing, r3f-shaders
      ```

      Contagens nuas no README e a posição da linha 345 dentro de um bloco de código:

      ```
      grep -nE "\([0-9]+ (topics|skills)|[0-9]+ topics|all [0-9]+" README.md
      -> 55:`ai-skills` bundle for whoever really wants all 35.
      -> 82:`ai-skills-game`, ...) — dumping all 35 skills into every project is noise, not help.
      -> 345:│   └── r3f-*/SKILL.md                        # React Three Fiber skills (10 topics)
      -> 537:### Game (React Three Fiber — 10 topics)
      awk 'NR<=345 && /^```/ {print NR": "$0}' README.md | tail -4
      -> 256: ```
      -> 292: ```jsonc
      -> 310: ```
      -> 329: ```
      ```

      Gates de base antes de qualquer edição:

      ```
      python3 scripts/validate-repo-hygiene.py --selftest
      -> 2/2 defect classes detected
      claude plugin validate . --strict
      -> ✔ Validation passed
      ```

- [x] E.3 O que não pôde ser probado

      Um ponto: **como a UI do `/plugin` renderiza uma description longa** (a de `workflow` terá 7
      nomes, a de `game` 12, a raiz 10 temas). Não há comando local que renderize a listagem do
      marketplace sem instalar o plugin numa sessão interativa; `claude plugin validate --strict`
      não impõe limite de tamanho (medido na simulação, S.1). Fica registrado como limite conhecido
      em `design.md`, não como fato.

- [x] E.4 Checagem de escopo

      A change faz só o que a proposta pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up:

      - `.github/workflows/ci.yml:47` continua sem a regex ancorada (a issue pedia; o orquestrador
        desta execução vetou editar o workflow). Cobertura transitiva via o step *Wrappers in sync*.
      - A tabela de `README.md:50-55` que nomeia as skills por plugin é prosa escrita à mão; gerar
        esse bloco a partir da mesma fonte (marcadores + `generate.sh`) fecharia a última deriva.
      - `README.md:345` (`r3f-*/SKILL.md # ... (10 topics)`) está dentro de um bloco de código e
        fora das linhas desta change; é verdadeiro hoje (10 diretórios `r3f-*`) e review-only.
      - `install.sh`/`update.sh` — issue própria.

## 2. Gerador: tema à mão, nomes e contagem da árvore

- [ ] 2.1 `GROUP_DESC` vira `GROUP_THEME`, uma frase por grupo sem nomes nem contagens (D1)
- [ ] 2.2 A description de `plugins/<g>/.claude-plugin/plugin.json` é montada como
      `"<tema> (<N> skills: <nomes em LC_ALL=C sort>)"` a partir de `plugins/<g>/skills/` (D1)
- [ ] 2.3 O fallback `:-Skill group` some: grupo sem tema derruba o gerador nomeando o grupo (D1)
- [ ] 2.4 `generate.sh` reescreve as `description` das entradas do `marketplace.json` (por plugin e
      bundle) e a do `plugin.json` raiz por round-trip JSON, sem tocar `version`; entrada sem grupo
      ou grupo sem entrada derruba o gerador (D3)

## 3. Guarda de `VERSION`

- [ ] 3.1 `generate.sh` valida `VERSION` com `SEMVER_RE` logo após checar `skills/`, antes de gravar
      qualquer arquivo; sem `|| echo 0.0.0` (D2)
- [ ] 3.2 `scripts/set-version.sh:13` usa a mesma regex literal (D2)

## 4. Gate: H3 pertencimento e contagem nua

- [ ] 4.1 `check_plugin_membership` (H3) compara o parêntese de cada `plugins/<g>/.claude-plugin/plugin.json`
      e da entrada `source: ./plugins/<g>` do `marketplace.json` com `plugins/<g>/skills/`,
      nomeando arquivo, grupo, sobrando e faltando (D4)
- [ ] 4.2 H2 ganha `UNSCOPED_COUNT_CLAIM` para `(N topics)`/`(N skills)` sem lista, fora de blocos
      de código; `.claude-plugin/plugin.json` entra em `COUNT_FILES` (D4)
- [ ] 4.3 Um defeito injetado por check novo em `DEFECTS`; o docstring de cada check declara o que
      não cobre (tema não verificado semanticamente, README prosa review-only, fences) (D4)

## 5. README

- [ ] 5.1 Linha de `svg-animation` sai da tabela Game e entra na tabela Frontend (D5)
- [ ] 5.2 Cabeçalho Game sem "10 topics"; o parágrafo nomeia o que `ai-skills-game` embarca (D5)
- [ ] 5.3 `README.md:50-55` nomeia as skills de cada plugin (D5)

## 6. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 7. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [ ] Q.2 All touched skill content in English (catalog locale)
- [ ] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [ ] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [ ] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

## 8. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate derive-plugin-descriptions --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive derive-plugin-descriptions --yes` after all groups above are `[x]`
