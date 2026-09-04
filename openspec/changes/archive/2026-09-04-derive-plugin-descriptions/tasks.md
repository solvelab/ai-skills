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
      - A tabela de `README.md:50-55` que nomeia as skills por plugin é prosa escrita à mão (o
        parágrafo que a introduz diz isso desde a revisão 2; antes atribuía a tabela ao gerador);
        gerar esse bloco a partir da mesma fonte (marcadores + `generate.sh`) fecharia a última deriva.
      - `README.md:345` (`r3f-*/SKILL.md # ... (10 topics)`) está dentro de um bloco de código e
        fora das linhas desta change; é verdadeiro hoje (10 diretórios `r3f-*`) e review-only.
      - `install.sh`/`update.sh` — issue própria.
      - Um grupo **com** tema mas sem entrada no `marketplace.json` ainda derruba o gerador depois
        de gravar os wrappers e `plugins/<g>/` (D3 roda depois do loop; medido em S.3). O spec só
        promete atomicidade para `VERSION` e para o tema (fechado na revisão 2); ler o
        `marketplace.json` antes do primeiro `mkdir` fecharia também este caminho.

## 2. Gerador: tema à mão, nomes e contagem da árvore

- [x] 2.1 `GROUP_DESC` vira `GROUP_THEME`, uma frase por grupo sem nomes nem contagens (D1)

      ```
      grep -nE 'declare -A GROUP_THEME' generate.sh; grep -c GROUP_DESC generate.sh
      -> 42:declare -A GROUP_THEME=(
      -> 0
      sed -n '/declare -A GROUP_THEME/,/^)/p' generate.sh | grep -cE '\[[a-z]+\]=".*[0-9]'
      -> 0    (nenhum tema carrega dígito)
      ```

- [x] 2.2 A description de `plugins/<g>/.claude-plugin/plugin.json` é montada como
      `"<tema> (<N> skills: <nomes em LC_ALL=C sort>)"` a partir de `plugins/<g>/skills/` (D1)

      ```
      grep -n 'LC_ALL=C sort' generate.sh
      -> 225:  names="$(ls -1 "$PLUGINS_OUT/$group/skills" | LC_ALL=C sort | paste -sd, - | sed 's/,/, /g')"
      python3 -c "import json;print(json.load(open('plugins/game/.claude-plugin/plugin.json'))['description'])"
      -> React Three Fiber and AssettoServer game-dev conventions (12 skills: assettoserver-csp-lua, assettoserver-plugin, r3f-animation, r3f-assets, r3f-fundamentals, r3f-geometry, r3f-interaction, r3f-lighting, r3f-materials, r3f-physics, r3f-postprocessing, r3f-shaders)
      python3 -c "import json;print(json.load(open('plugins/docs/.claude-plugin/plugin.json'))['description'])"
      -> Three-tier project documentation generation (1 skill: documentation)
      ```

      Uma skill que muda de categoria move nos três artefatos (FR2), medido na cópia de
      simulação com `skills/svg-animation/SKILL.md:18` trocado de `frontend` para `game`:

      ```
      bash generate.sh; git status --porcelain | grep plugin.json
      ->  M .claude-plugin/marketplace.json
      ->  M plugins/frontend/.claude-plugin/plugin.json
      ->  M plugins/game/.claude-plugin/plugin.json
      git diff -U0 | grep -E '^[-+] ' | cut -c1-120
      -> -      "description": "React Three Fiber and AssettoServer game-dev conventions (12 skills: assettoserver-csp-lua, [...]
      -> +      "description": "React Three Fiber and AssettoServer game-dev conventions (13 skills: assettoserver-csp-lua, [...]
      -> -      "description": "React SPA API-client conventions and physically-grounded SVG/CSS animation (2 skills: react-api-client, svg-animation)",
      -> +      "description": "React SPA API-client conventions and physically-grounded SVG/CSS animation (1 skill: react-api-client)",
      -> [...]  (as mesmas duas trocas nos plugin.json de frontend e game)
      python3 scripts/validate-repo-hygiene.py | tail -1
      -> repo hygiene: 0 findings
      ```

- [x] 2.3 O fallback `:-Skill group` some: grupo sem tema derruba o gerador nomeando o grupo, antes
      de gravar qualquer arquivo (D1)

      ```
      grep -n ':-Skill group' generate.sh
      -> 217:# `:-Skill group <g>` fallback would have published a placeholder for a new category without a   (só o comentário)
      grep -n -- '-v GROUP_THEME' generate.sh
      -> 74:  [[ -v GROUP_THEME[$group] ]] || {      (pré-checagem sobre skills/*/SKILL.md, antes do mkdir da 80)
      -> 221:  [[ -v GROUP_THEME[$group] ]] || {     (segunda guarda em group_description)
      grep -nE '^category_of|^rm -rf' generate.sh
      -> 62:category_of() {
      -> 203:rm -rf "$PLUGINS_OUT"
      ```

      Na cópia de simulação (`git archive` do worktree + `git init`), `skills/zz-probe/` com
      `category: newcat` commitado como base. Revisão 2, com a checagem antes do primeiro write:

      ```
      bash generate.sh; echo rc=$?; echo "porcelain: $(git status --porcelain | wc -l)"
      -> ❌ generate.sh: no GROUP_THEME for plugin group 'newcat' (from zz-probe/SKILL.md) — add its theme to GROUP_THEME in generate.sh. Nothing was written.
      -> rc=1
      -> porcelain: 0
      find plugins codex/AGENTS.md -newer generate.sh | wc -l
      -> 0        (nada gravado depois da cópia do gerador)
      ```

      Na primeira versão da change a mesma prova dava `porcelain` 10 (`M codex/AGENTS.md`, quatro
      `D plugins/*/.claude-plugin/plugin.json`, cinco `??`): a saída está guardada em S.3.

- [x] 2.4 `generate.sh` reescreve as `description` das entradas do `marketplace.json` (por plugin e
      bundle) e a do `plugin.json` raiz por round-trip JSON, sem tocar `version`; entrada sem grupo
      ou grupo sem entrada derruba o gerador (D3)

      ```
      grep -nE '^python3 - |def marketplace|def root_manifest|if out != raw' generate.sh
      -> 258:python3 - "$SCRIPT_DIR" "$generated" "$plugin_count" "${group_args[@]}" <<'PY'
      -> 274:    if out != raw:
      -> 278:def marketplace(data: dict) -> None:
      -> 300:def root_manifest(data: dict) -> None:
      python3 -c "import json;d=json.load(open('.claude-plugin/marketplace.json'));print(d['plugins'][0]['description']);print(d['metadata']['version'])"
      -> FULL bundle (all 35 skills). Prefer the per-domain plugins — enable only what fits the project.
      -> 2.16.0
      python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['description'][:120])"
      -> Reusable AI skills for coding assistants — all 35 skills across 10 per-domain plugins: backend: Backend service conventi
      ```

      Os dois sentidos da falha, na cópia de simulação:

      ```
      # tema declarado para newcat, sem entrada no marketplace
      bash generate.sh; echo rc=$?
      -> ❌ generate.sh: plugin group(s) with no marketplace entry: newcat — add the entry to .claude-plugin/marketplace.json.
      -> rc=1
      # entrada ai-skills-ghost com source ./plugins/ghost, sem grupo na árvore
      bash generate.sh; echo rc=$?
      -> ❌ generate.sh: marketplace entry 'ai-skills-ghost' points at './plugins/ghost', which is not a plugin group in plugins/.
      -> rc=1
      # com tema E entrada, o gerador aceita e publica a description derivada
      bash generate.sh | tail -1
      -> Generated 11 category plugins in plugins/ (descriptions derived from the tree)
      -> ['Probe theme (1 skill: zz-probe)']
      ```

## 3. Guarda de `VERSION`

- [x] 3.1 `generate.sh` valida `VERSION` com `SEMVER_RE` logo após checar `skills/`, antes de gravar
      qualquer arquivo; sem `|| echo 0.0.0` (D2)

      ```
      grep -nE '^\[ -d "\$SKILLS"|SEMVER_RE=|=~ \$SEMVER_RE|^mkdir -p' generate.sh
      -> 24:[ -d "$SKILLS" ] || { echo "❌ skills/ directory not found."; exit 1; }
      -> 30:SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'
      -> 32:[[ "$VERSION_STR" =~ $SEMVER_RE ]] || {
      -> 80:mkdir -p "$CURSOR_OUT" "$COPILOT_OUT"
      grep -c 'echo 0.0.0' generate.sh
      -> 0
      ```

      Entre a 32 e a 80 só há declarações (`GROUP_THEME`, `group_of`, `category_of`) e a
      pré-checagem de tema (2.3), que lê `skills/*/SKILL.md` e não grava nada:

      ```
      sed -n '33,79p' generate.sh | grep -vE '^\s*#' | grep -E '(^|[^&])>[^&]|\bmkdir\b|\brm\b|\bcp\b' | wc -l
      -> 0        (o único `>` fora de comentário é o `>&2` da mensagem de erro)
      ```

      Com mtime de três saídas medido antes e depois (`plugins/game/.claude-plugin/plugin.json`,
      `codex/AGENTS.md`, `claude/skills/backlog/SKILL.md`):

      ```
      echo 1.2.3garbage > VERSION; bash generate.sh; echo rc=$?
      -> ❌ VERSION is '1.2.3garbage' — expected MAJOR.MINOR.PATCH with an optional -prerelease suffix. Nothing was written.
      -> rc=1
      diff mtimes-before.txt mtimes-after.txt && echo "mtimes unchanged: no file written"
      -> mtimes unchanged: no file written
      git status --porcelain
      ->  M VERSION          (só o que o teste escreveu; restaurado com git checkout -- VERSION)
      ```

      Arquivo ausente e pré-release, na cópia de simulação:

      ```
      rm VERSION; bash generate.sh; echo rc=$?
      -> ❌ VERSION is '' — expected MAJOR.MINOR.PATCH with an optional -prerelease suffix. Nothing was written.
      -> rc=1
      echo 3.0.0-rc.1 > VERSION; bash generate.sh | tail -1; grep -c '"version": "3.0.0-rc.1"' plugins/game/.claude-plugin/plugin.json
      -> Generated 10 category plugins in plugins/ (descriptions derived from the tree)
      -> 1
      ```

- [x] 3.2 `scripts/set-version.sh:13` usa a mesma regex literal (D2)

      ```
      grep -n "SEMVER_RE='" generate.sh scripts/set-version.sh
      -> generate.sh:30:SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'
      -> scripts/set-version.sh:15:SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'
      bash scripts/set-version.sh 1.2.3garbage; echo rc=$?; cat VERSION
      -> ❌ Usage: scripts/set-version.sh <X.Y.Z[-prerelease]> (got '1.2.3garbage')
      -> rc=1
      -> 2.16.0
      ```

## 4. Gate: H3 pertencimento e contagem nua

- [x] 4.1 `check_plugin_membership` (H3) compara o parêntese de cada `plugins/<g>/.claude-plugin/plugin.json`
      e da entrada `source: ./plugins/<g>` do `marketplace.json` com `plugins/<g>/skills/`,
      nomeando arquivo, grupo, sobrando e faltando (D4)

      ```
      grep -nE '^MEMBERSHIP_CLAIM|^def check_plugin_membership|^CHECKS' scripts/validate-repo-hygiene.py
      -> 42:MEMBERSHIP_CLAIM = re.compile(r"\((\d+) skills?: ([^)]*)\)")
      -> 153:def check_plugin_membership(root: Path) -> None:
      -> 202:CHECKS = (check_no_bytecode, check_counts, check_plugin_membership)
      ```

      Defeitos injetados no worktree e restaurados com `git checkout --` em seguida:

      ```
      # plugins/backend/.claude-plugin/plugin.json sem log-event-collector no parêntese
      python3 scripts/validate-repo-hygiene.py; echo rc=$?
      ->   H3 plugin description membership: plugins/backend/.claude-plugin/plugin.json (backend) names 3 skills but plugins/backend/skills/ has 4 — in excess: none; missing: ['log-event-collector']; regenerate with ./generate.sh
      ->   H3 plugin description membership: plugins/backend/.claude-plugin/plugin.json (backend) says 4 skills but lists 3 names; regenerate with ./generate.sh
      -> repo hygiene: 2 findings
      -> rc=1
      # marketplace.json, entrada ai-skills-fivem com fivem-nui-react no lugar de fivem-lua
      python3 scripts/validate-repo-hygiene.py; echo rc=$?
      ->   H3 plugin description membership: .claude-plugin/marketplace.json entry `ai-skills-fivem` (fivem) names 2 skills but plugins/fivem/skills/ has 2 — in excess: ['fivem-nui-react']; missing: ['fivem-lua']; regenerate with ./generate.sh
      -> rc=1
      ```

- [x] 4.2 H2 ganha `UNSCOPED_COUNT_CLAIM` para `(N topics)`/`(N skills)` sem lista, fora de blocos
      de código; `.claude-plugin/plugin.json` entra em `COUNT_FILES` (D4)

      ```
      grep -nE '^COUNT_FILES|^UNSCOPED_COUNT_CLAIM|in_fence = not' scripts/validate-repo-hygiene.py
      -> 33:COUNT_FILES = ("README.md", ".claude-plugin/marketplace.json", ".claude-plugin/plugin.json")
      -> 39:UNSCOPED_COUNT_CLAIM = re.compile(r"(?<!all )\b(\d+) (?:topics|skills)\)")
      -> 107:                in_fence = not in_fence
      # .claude-plugin/plugin.json com "(10 topics)" injetado
      python3 scripts/validate-repo-hygiene.py; echo rc=$?
      ->   H2 unscoped count: .claude-plugin/plugin.json:5 publishes `10 topics)` with no member list — nothing in the tree can confirm it; write `all N` (catalog total) or `(N skills: <names>)` (group membership, checked by H3)
      -> rc=1
      # README.md:548 reescrito como "### Game (React Three Fiber — 10 topics)"
      python3 scripts/validate-repo-hygiene.py; echo rc=$?
      ->   H2 unscoped count: README.md:548 publishes `10 topics)` with no member list [...]
      -> rc=1
      # README.md:355 ("r3f-*/SKILL.md  # React Three Fiber skills (10 topics)") dentro do bloco ``` aberto na 339
      python3 scripts/validate-repo-hygiene.py
      -> repo hygiene: 0 findings     (mudo, como D4 pede)
      ```

- [x] 4.3 Um defeito injetado por check novo em `DEFECTS`; o docstring de cada check declara o que
      não cobre (tema não verificado semanticamente, README prosa review-only, fences) (D4)

      ```
      grep -nE '^DEFECTS|_defect_unscoped_count\)|_defect_membership\)|KNOWN LIMIT' scripts/validate-repo-hygiene.py
      -> 66:    KNOWN LIMIT: covers the bytecode classes .gitignore names [...]
      -> 86:    KNOWN LIMIT: both patterns run over exactly the files in COUNT_FILES [...]
      -> 161:    KNOWN LIMIT: the theme — the text before the parenthetical — is not read at all. [...]
      -> 240:DEFECTS = (("H1 tracked bytecode", _defect_bytecode),
      -> 242:           ("H2 unscoped count", _defect_unscoped_count),
      -> 243:           ("H3 plugin description membership", _defect_membership))
      python3 scripts/validate-repo-hygiene.py --selftest
      ->   CAUGHT  H1 tracked bytecode
      ->   CAUGHT  H2 stale count
      ->   CAUGHT  H2 unscoped count
      ->   CAUGHT  H3 plugin description membership
      -> 4/4 defect classes detected
      ```

## 5. README

- [x] 5.1 Linha de `svg-animation` sai da tabela Game e entra na tabela Frontend (D5)

      ```
      grep -nE '^### (Frontend|Game)|^\| \*\*svg-animation\*\*' README.md | cut -c1-60
      -> 517:### Frontend
      -> 523:| **svg-animation** | "a toucan flying", "a tree in a li
      -> 551:### Game (React Three Fiber)
      grep -c '^| \*\*svg-animation\*\*' README.md
      -> 1      (uma linha só, entre 517 e 525 = tabela Frontend; nenhuma sob 551)
      ```

      Numeração de `349a0ce`: o parágrafo de 5.3 ganhou três linhas na revisão 2, então as
      referências a `README.md:548` e `:355` em 4.1, 4.2 e S.2 (medidas em `5bff578`) hoje são
      `:551` e `:358`.

- [x] 5.2 Cabeçalho Game sem "10 topics"; o parágrafo nomeia o que `ai-skills-game` embarca (D5)

      ```
      sed -n '551p;558,559p' README.md
      -> ### Game (React Three Fiber)
      -> The `ai-skills-game` plugin bundles every skill in this table plus `assettoserver-plugin` and
      -> `assettoserver-csp-lua` from the AssettoServer table above (`assettoserver-ops` ships with
      grep -nE '[0-9]+ topics' README.md
      -> 358:│   └── r3f-*/SKILL.md                        # React Three Fiber skills (10 topics)   (dentro de bloco de código, review-only; E.4)
      ```

- [x] 5.3 `README.md:50-55` nomeia as skills de cada plugin (D5)

      ```
      sed -n '54,64p' README.md | cut -c1-80
      -> | Plugin | Ships |
      -> |---|---|
      -> | `ai-skills-workflow` | `backlog`, `code-locale`, `conventional-commit`, `execute-b
      -> | `ai-skills-backend` | `backend-resilience`, `log-event-collector`, `observability`
      -> [...]
      -> | `ai-skills-tooling` | `claude-statusline` |
      ```

      A tabela é prosa e não é comparada com a árvore por H3 (limite declarado em
      `scripts/validate-repo-hygiene.py:161-170`); medido em S.3. O parágrafo que a introduz diz
      isso (revisão 2 — antes dizia que `generate.sh` "deriva as duas", e o gerador nunca leu nem
      escreveu o README):

      ```
      grep -n README generate.sh; echo rc=$?
      -> rc=1
      sed -n '51,55p' README.md | cut -c1-100
      -> full `ai-skills` bundle for whoever really wants all 35. What each plugin ships. The published
      -> description of each plugin is derived by `generate.sh` from `plugins/<group>/skills/` and checked
      -> against that tree by `scripts/validate-repo-hygiene.py` (H3); this table is **hand-maintained** and
      -> mirrors it — no gate compares it with the tree (H3's declared KNOWN LIMIT), so review it when a sk
      -> changes category:
      ```

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 O gerador, o script de versão e o gate foram exercitados pelo caminho real, com a saída
      observada

      No worktree (`5bff578`), duas gerações seguidas:

      ```
      bash generate.sh; echo rc=$?; bash generate.sh; echo rc=$?; git status --porcelain | wc -l
      -> Generated wrappers for 35 skills:
      -> Generated 10 category plugins in plugins/ (descriptions derived from the tree)
      -> rc=0
      -> [...]  (segunda run, mesma saída)
      -> rc=0
      -> 0
      ```

      Os dois steps do `ci.yml` que esta change alcança, rodados literalmente:

      ```
      bash generate.sh; git diff --exit-code --quiet; echo rc=$?
      -> rc=0
      VERSION="$(tr -d '[:space:]' < VERSION)"; for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json; do grep -q "\"version\": \"$VERSION\"" "$f" || exit 1; done; echo "Version $VERSION coherent across manifests."
      -> Version 2.16.0 coherent across manifests.
      ```

      `VERSION` inválido, antes de qualquer escrita (3.1), e `set-version.sh` recusando o mesmo
      valor (3.2): saídas acima. Gate com defeito injetado nos dois arquivos e nas duas formas de
      contagem nua (4.1, 4.2): saídas acima.

      Validador do vendor, na versão instalada e na pinada pelo `ci.yml:129`:

      ```
      claude plugin validate . --strict
      -> ✔ Validation passed          (claude 2.1.260)
      npx -y @anthropic-ai/claude-code@2.1.246 plugin validate . --strict
      -> ✔ Validation passed
      ```

      **Ordem no release** (Risks de `design.md`), numa cópia do worktree em
      `scratchpad/wt3-copy` com `.git` próprio (`git init` + commit base), nunca no worktree:

      ```
      bash scripts/set-version.sh 9.9.9; echo rc=$?
      -> ✅ Version set: 2.16.0 → 9.9.9
      -> rc=0
      git status --porcelain
      ->  M .claude-plugin/marketplace.json
      ->  M .claude-plugin/plugin.json
      ->  M VERSION
      ->  M plugins/backend/.claude-plugin/plugin.json
      -> [...]  (os 10 plugins/*/.claude-plugin/plugin.json; 13 linhas ao todo)
      grep -l '"version": "9.9.9"' plugins/*/.claude-plugin/plugin.json .claude-plugin/plugin.json .claude-plugin/marketplace.json | wc -l
      -> 12
      git add -A; git commit -q -m v999; bash generate.sh >/dev/null; git status --porcelain | wc -l
      -> 0        (sem segundo diff)
      ```

      E a versão não entra na derivação: as 11 `description` do `marketplace.json` em `9.9.9`
      (cópia) são idênticas às de `2.16.0` (worktree):

      ```
      python3 -c "... da==db ..."
      -> scratch version: 9.9.9 worktree version: 2.16.0
      -> descriptions identical across versions: True 11
      ```

      Grupo novo sem tema, tema sem entrada, entrada sem grupo, `VERSION` ausente, pré-release e
      mudança de categoria: saídas em 2.2, 2.3, 2.4 e 3.1, todas na mesma cópia.

- [x] S.2 Matriz de casos, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | Tinha de disparar e disparou | **11/11** | `VERSION` `1.2.3garbage` (gerador, exit 1, mtimes intactos); `VERSION` ausente (exit 1); `set-version.sh 1.2.3garbage` (exit 1, `VERSION` intacto); grupo sem tema (exit 1, nomeia `newcat` e `zz-probe/SKILL.md`, porcelain 0 — revisão 2); tema sem entrada no marketplace (exit 1, nomeia `newcat`); entrada `ai-skills-ghost` sem grupo (exit 1); H3 `plugin.json` sem `log-event-collector` (2 findings, nomeia arquivo, grupo, faltando); H3 entrada `ai-skills-fivem` com `fivem-nui-react` (nomeia sobrando e faltando); H2 `(10 topics)` no `plugin.json` raiz; H2 `(… — 10 topics)` no cabeçalho `README.md:548`; `--selftest` 4/4 |
      | Tinha de mudar e mudou | **1/1** | `svg-animation` `frontend → game`: `marketplace.json` (2 entradas), `plugins/frontend` e `plugins/game` reescritos com `1 skill`/`13 skills`, hygiene 0 findings sobre a árvore movida |
      | Tinha de ficar mudo e ficou | **8/8** | segunda `generate.sh` (porcelain 0); `set-version.sh 9.9.9` + `generate.sh` (sem segundo diff, 12 arquivos em 9.9.9); pré-release `3.0.0-rc.1` aceito; hygiene no worktree (0 findings); `README.md:355` dentro de fence (0 findings); `claude plugin validate --strict` em 2.1.260 e em 2.1.246; `Wrappers in sync` e `Version coherence` do `ci.yml` literais |
      | Escape conhecido ficou mudo | **2/2** | tema errado (`[fivem]="Kubernetes cluster tuning…"`): publicado e hygiene 0 findings; `README.md:63` tabela de plugins com `helm-migration` em `ai-skills-docs`: hygiene 0 findings |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      Dois escapes, os dois declarados dentro do check (`scripts/validate-repo-hygiene.py:161-170`,
      D4) e agora medidos:

      ```
      # cópia: tema do grupo fivem trocado para "Kubernetes cluster tuning"
      bash generate.sh; python3 -c "...plugins/fivem...['description']"; python3 scripts/validate-repo-hygiene.py | tail -1
      -> Kubernetes cluster tuning and Lua-side resilience patterns (2 skills: fivem-fallback, fivem-lua)
      -> repo hygiene: 0 findings
      # cópia: README.md tabela Plugin | Ships, ai-skills-docs com `helm-migration` a mais
      python3 scripts/validate-repo-hygiene.py | tail -1
      -> repo hygiene: 0 findings
      ```

      O tema (texto antes do parêntese) não é verificado semanticamente; a tabela
      `README.md:54-64` é prosa review-only (follow-up em E.4: gerá-la da mesma fonte).

      Um ponto **não medido**: como a UI do `/plugin` renderiza as descrições longas. Tamanhos
      publicados: `game` 264 chars, `workflow` 236, raiz (`.claude-plugin/plugin.json`) 941.
      `claude plugin validate --strict` (2.1.260 e 2.1.246) não impõe limite — os dois passaram
      com esses tamanhos — mas nenhum comando local renderiza a listagem do marketplace sem
      sessão interativa (E.3). Fica como limite conhecido.

      Uma diferença de comportamento, medida na primeira versão da change e **fechada na revisão
      2**: um grupo sem tema derrubava o gerador **no meio do loop** de `plugins/`, não antes de
      gravar. `rm -rf plugins/` já tinha rodado, os wrappers já estavam gravados, e os `plugin.json`
      dos grupos que vêm depois do grupo órfão na ordem alfabética ainda não tinham sido recriados.
      Medido na cópia, com `skills/zz-probe/` (`category: newcat`) commitado como base, no gerador
      de `5bff578`:

      ```
      bash generate.sh; echo rc=$?; git status --porcelain
      -> ❌ generate.sh: no GROUP_THEME for plugin group 'newcat' — add its theme to GROUP_THEME in generate.sh.
      -> rc=1
      ->  M codex/AGENTS.md
      ->  D plugins/nui/.claude-plugin/plugin.json
      ->  D plugins/testing/.claude-plugin/plugin.json
      ->  D plugins/tooling/.claude-plugin/plugin.json
      ->  D plugins/workflow/.claude-plugin/plugin.json
      -> ?? claude/skills/zz-probe/
      -> [...]  (codex/, copilot/, cursor/ e plugins/newcat/ novos)
      ```

      O spec prometia "antes de gravar qualquer arquivo" para os dois casos e o código só cumpria
      para `VERSION` (finding da revisão 2). A checagem de tema foi movida para logo depois da
      guarda de `VERSION`, sobre `skills/*/SKILL.md`, antes do primeiro `mkdir` e do `rm -rf`
      (`generate.sh:66-78`); a mesma prova, na mesma cópia, com o gerador revisado:

      ```
      bash generate.sh; echo rc=$?; echo "porcelain: $(git status --porcelain | wc -l)"
      -> ❌ generate.sh: no GROUP_THEME for plugin group 'newcat' (from zz-probe/SKILL.md) — add its theme to GROUP_THEME in generate.sh. Nothing was written.
      -> rc=1
      -> porcelain: 0
      ```

      O que **continua** não atômico, medido na mesma cópia e fora do que o spec promete: tema
      declarado para `newcat` mas sem entrada no `marketplace.json` derruba o gerador em D3, depois
      do loop, com os wrappers e `plugins/newcat/` já gravados (os `plugin.json` dos outros grupos
      já foram recriados, então não há `D`):

      ```
      bash generate.sh; echo rc=$?; git status --porcelain | grep -v '^ M generate.sh'
      -> ❌ generate.sh: plugin group(s) with no marketplace entry: newcat — add the entry to .claude-plugin/marketplace.json.
      -> rc=1
      ->  M codex/AGENTS.md
      -> ?? claude/skills/zz-probe/
      -> [...]  (codex/, copilot/, cursor/ e plugins/newcat/ novos)
      ```

      Fica como follow-up em E.4. Nada mais escapou nem se comportou de forma diferente.

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — **não se aplica**: esta change não toca
      nenhuma skill (`git diff --name-only master...HEAD | grep -c SKILL.md` → `0`); o step
      *Skill frontmatter checks* roda verde no runner de gates (`PASS frontmatter`)
- [x] Q.2 Conteúdo de skill tocado em inglês — **não se aplica** pelo mesmo motivo; o delta de spec
      desta change está em inglês, como o catálogo exige
- [x] Q.3 Gatilhos de descrição testáveis — **não se aplica**: nenhuma descrição de skill muda; as
      descrições que mudam são as dos plugins, e o que elas afirmam (nomes e contagem) é o que H3
      verifica
- [x] Q.4 Sem doutrina duplicada: a regra "um check declara o que não cobre" é aplicada dentro de H2
      e H3 (`KNOWN LIMIT` em `scripts/validate-repo-hygiene.py:86,161`) e não reescrita; ver a
      tabela de Canonical Home em `design.md`
- [x] Q.5 Identificadores em inglês no que a change introduz — `GROUP_THEME`, `SEMVER_RE`,
      `group_description`, `check_plugin_membership`, `UNSCOPED_COUNT_CLAIM`, `MEMBERSHIP_CLAIM` —
      conforme o glossário da issue #114 e `code-locale`; `PASS locale-detector` no runner

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate derive-plugin-descriptions --strict` verde

      ```
      openspec validate derive-plugin-descriptions --strict
      -> Change 'derive-plugin-descriptions' is valid
      ```

- [x] V.2 Descoberta do catálogo intacta

      ```
      npx -y skills add <worktree> --list > skills-list.txt; grep -E '^│    [a-z0-9-]+$' skills-list.txt | sed 's/^│ *//' | sort > list-names.txt; wc -l < list-names.txt
      -> 35
      ls -1 skills | sort > tree-names.txt; diff list-names.txt tree-names.txt && echo "list == skills/ tree"
      -> list == skills/ tree
      ```

- [x] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo: a
      composição não muda (35 skills, mesmos grupos); o que muda é o texto publicado por plugin, e o
      README foi ajustado nas linhas da proposta (5.1-5.3)
- [x] V.4 `openspec archive derive-plugin-descriptions --yes` depois que todos os grupos acima estiverem `[x]`


      ```
      openspec archive derive-plugin-descriptions --yes
      -> Specs updated successfully.
      -> Change 'derive-plugin-descriptions' archived as '2026-09-04-derive-plugin-descriptions'.
      ```