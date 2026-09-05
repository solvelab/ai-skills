## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `bfc400d` (topo de `master`, 2026-09-05):

      - `scripts/validate-skills.py` — 411 linhas; docstring C1..C10 em 1-16; `check_refs` em `:75`
        com o filtro `s.startswith("references/") or s.startswith("skills/")` em `:97` (um caminho
        `bug-hunter/references/x.md` nunca é julgado); `check_limits` em `:309` parseando a
        description com PyYAML; `main()` em 365-407, `references/*.md` percorrido com `glob` (sem
        recursão); `INLINE`, `LINK`, `FENCE`, `PLACEHOLDER` em 36-49.
      - `scripts/selftest-validate-skills.py` — 72 linhas; `MUTATIONS` em 13-59 como
        `label: (relpath, mutate[, (expect, fragment)])`; `p.write_text(mutate(p.read_text()))` em
        `:65` (exige arquivo existente); `relpath is None` reservado ao caso C7.
      - `generate.sh` — 314 linhas; sed do Cursor em 171-173
        (`s#\]\(references/#](../../skills/${name}/references/#g`); wrapper Copilot em 176-185 (dois
        links relativos `../../skills/${name}/…`); `claude/` em 141-151 (caminho `~/ai-skills/…`),
        `codex/` em 153-159 (`@../../skills/…`), `plugins/` em 199-212 (`cp -r` da skill inteira).
      - `install.sh:105-114` — `setup_cursor`/`setup_copilot` mandam copiar os arquivos isolados.
      - `README.md:125-148` (bloco de instalação manual; Cursor em 144-145, Copilot em 147-148),
        `:425-431` (tabela de formas), `:774-784` (parágrafo "runs nine checks", que lista C1-C9 e
        já está um check atrás de C10).
      - `openspec/specs/skills-authoring/spec.md` — 478 linhas; *Authoring rules are
        machine-enforced* em 281-332 (copiado inteiro no delta); *Triggers live in the description*
        em 363-402, cenário *Every skill states where it does not apply* em 385-389.
      - `openspec/changes/archive/2026-09-04-close-ci-gate-holes/{proposal,design,tasks}.md` e
        `specs/skills-authoring/spec.md` — modelo de estilo do rito.
      - Linhas com caminho cruzado: `skills/fivem-lua/SKILL.md:154`,
        `skills/openspec-drivezone/SKILL.md:85`, `skills/python-rest-api/SKILL.md:329`,
        `skills/assettoserver-csp-lua/SKILL.md:124,201`, `skills/assettoserver-plugin/SKILL.md:277`,
        `skills/backlog/references/backlog-config.md:32` (em fence) e `:91`,
        `skills/backlog/references/issue-template.md:65`,
        `skills/execute-backlog/references/board-sync.md:5,45` (outro item),
        `skills/code-locale/SKILL.md:25,179` (`claude/global/hooks/locale-rite.py`).
      - Frontmatter (name, description, version) das 14 skills que este item edita; versões lidas:
        fivem-lua 1.3.1, openspec-drivezone 2.1.2, python-rest-api 1.4.1, assettoserver-csp-lua
        1.1.0, assettoserver-plugin 1.3.1, backlog 1.5.0, code-locale 1.3.0, conventional-commit
        1.3.0, r3f-geometry 1.2.0, r3f-physics 1.2.0, r3f-postprocessing 1.2.0, svg-animation 1.1.1,
        r3f-animation 1.2.0, api-resilience-testing 1.3.0.
      - `skills/svg-animation/SKILL.md:26-28,103-112` e `references/platform.md:5`,
        `references/regimes/articulated-body.md:27` — `research/svg-animation` já é URL com texto de
        link; a tabela de regimes cita os 10 arquivos em crase.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      openspec --version                                   -> 1.6.0
      python3 --version                                    -> Python 3.14.5
      openspec list                                        -> No active changes found.
      openspec new change define-cross-skill-references --schema skills-rite
      -> Created change 'define-cross-skill-references' at openspec/changes/define-cross-skill-references/
      ```

      Contagem em `master` (`bfc400d`) com o validador estendido (cópia em scratchpad, mesma
      `ROOT = Path.cwd()`), antes de qualquer edição fora de `openspec/`:

      ```
      python3 <scratchpad>/validate-skills.py
      -> skills checked: 35   findings: 18
      ->   C12 out-of-skill path  12
      ->   C13 anti-trigger clause 6
      -> [...] fivem-lua [C12] inline -> bug-hunter/references/track-fivem-lua.md: cross-skill path without the skills/ prefix [...]
      -> [...] code-locale [C12] inline -> claude/global/hooks/locale-rite.py: exists only in a clone of this repository [...]
      -> [...] r3f-geometry [C13] description names no boundary [...]
      exit=1
      ```

      C11 em `master`: zero órfãos em 29 skills com `references/` (BFS sobre links + inline paths,
      fora de fences), medido pelo mesmo protótipo.

      Descriptions parseadas (PyYAML) em `master`: 16 sem "Do NOT use"/"do not use"; dessas, 10
      redirecionam nomeando uma irmã sem crase e 6 não (`conventional-commit`, `python-rest-api`,
      `r3f-geometry`, `r3f-physics`, `r3f-postprocessing`, `svg-animation`); maior description
      `verify-before-claiming` 1012, `assettoserver-csp-lua` 1003, `backlog` 1000, `svg-animation` 998.

      ```
      curl -sI https://github.com/solvelab/ai-skills/blob/master/skills/backlog/references/gh-projects.md | head -1
      -> HTTP/2 200
      curl -sI https://github.com/solvelab/ai-skills/tree/master/skills/backlog/references/ | head -1
      -> HTTP/2 200
      grep -c "references/" cursor/rules/*.mdc | grep -v ":0$" | wc -l          -> 30
      grep -l "\](\.\./\.\./skills" cursor/rules/*.mdc | wc -l                  -> 10
      grep -l "\`references/" cursor/rules/*.mdc | wc -l                        -> 19
      grep -c "references/" copilot/instructions/*.instructions.md | grep -v ":0$" | wc -l   -> 29
      ls skills | wc -l                                                          -> 35
      ```

- [x] E.3 O que não pôde ser probado

      - O comportamento do Cursor e do Copilot diante de uma URL num `.mdc`/`.instructions.md`
        (se o agente a segue ou só a mostra ao humano) não é probável nesta máquina: nenhum dos dois
        está instalado. O que se prova é que a URL responde 200 e que o caminho relativo anterior não
        resolvia fora da árvore. Gap declarado; a decisão R5 é da issue.
      - Roteamento real das seis descriptions editadas (se a cláusula nova muda a escolha do modelo
        num prompt ambíguo) não é medido aqui: C13 prova presença da frase, não o efeito. Q.3 revisa
        colisão à mão.
      - `npx skills add` não foi executado de fato contra o branch (rede + instalação num agente
        externo); a forma de instalação (cópia de `skills/<nome>/`) vem do `README.md:44-46` e do
        comportamento já medido em V.2 de changes anteriores.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #121 e a decisão registrada pedem. Notados e **não** feitos:

      - `skills/execute-backlog/references/board-sync.md:5,45` — dois caminhos `backlog/references/…`
        sem prefixo; pertencem ao item paralelo dono de `execute-backlog/**`. Fica como achado C12
        aberto (S.3) até aquele item corrigir (duas linhas + bump patch).
      - Link `[SKILL.md](../../skills/<nome>/SKILL.md)` do wrapper Copilot também morre quando o
        arquivo é copiado isolado; R5 fala só de `references/`, então fica como follow-up (o README
        passa a dizer que esse link ainda espera o clone).
      - `verify-before-claiming/references/failure-catalog.md` cita `scripts/validate-rite.sh`,
        `openspec/specs/skills-authoring/spec.md` e `.github/workflows/ci.yml` deste repositório em
        crase — raízes que C12 declara não julgar (design D2). Converter para URL é follow-up.
      - `skills/backlog/references/backlog-config.md:32` cita `execute-backlog/references/board-sync.md`
        dentro de um fence YAML (comentário de config): fora do alcance de C12 por desenho, mas
        corrigido junto por ser texto deste item.
      - Pins `Verified against` como check: issue #131, fora deste item.

## 2. Validador: C11, C12, C13 e selftest (D2, D3, D4, D7)

- [x] 2.1 `check_orphan_refs` (C11): BFS a partir de `SKILL.md` sobre links e inline paths fora de
      fences, só `*.md`, transitivo; docstring declara o que não cobre

      ```
      grep -n "^def check_orphan_refs\|^def _cited_files" scripts/validate-skills.py
      -> 355:def _cited_files(skill_dir: Path, path: Path, text: str) -> set[Path]:
      -> 381:def check_orphan_refs(skill: str, skill_dir: Path) -> None:
      python3 scripts/validate-skills.py | grep -c "C11"      -> 0     (29 skills com references/, 0 órfãos)
      ```

- [x] 2.2 `check_out_of_skill` (C12): `CATALOG_ONLY_ROOTS`, `<skill>/references/` sem prefixo, link
      `..` que sai de `skills/<x>/`; texto de link não é julgado; docstring declara as raízes não
      julgadas

      ```
      grep -n "^CATALOG_ONLY_ROOTS\|^def check_out_of_skill" scripts/validate-skills.py
      -> 418:CATALOG_ONLY_ROOTS = ("research/", "claude/", "codex/", "cursor/", "copilot/", "plugins/")
      -> 422:def check_out_of_skill(skill: str, path: Path, text: str) -> None:
      ```

      Em `master` (cópia via `git archive bfc400d`), pelo caminho do CI:
      `python3 scripts/validate-skills.py -> C12 out-of-skill path  12` (S.1 tem a lista).

- [x] 2.3 `check_anti_trigger` (C13): `ANTI_TRIGGER_PHRASES` e `REDIRECT_WORDS` + nome de irmã,
      sobre a description parseada; skip declarado sem PyYAML

      ```
      grep -n "^ANTI_TRIGGER_PHRASES\|^REDIRECT_WORDS\|^def check_anti_trigger" scripts/validate-skills.py
      -> 487:ANTI_TRIGGER_PHRASES = ("Do NOT use", "do not use", "Not for", "that is `")
      -> 488:REDIRECT_WORDS = ("that is", "use", "see", "in", "to", "instead of")
      -> 491:def check_anti_trigger(skill: str, text: str) -> None:
      ```

      Em `master`: `C13 anti-trigger clause 6` — `conventional-commit`, `python-rest-api`,
      `r3f-geometry`, `r3f-physics`, `r3f-postprocessing`, `svg-animation`; as 10 descriptions que
      redirecionam sem crase ("see fivem-lua", "live in r3f-fundamentals", "use openspec-drivezone",
      "that is fivem-nui-react") ficaram mudas.

- [x] 2.4 Docstring C1..C13; `main()` chama os três (C12 também em `references/*.md`)

      ```
      grep -n "^  C1[0-3]" scripts/validate-skills.py
      -> 14:  C10 frontmatter limits [...]
      -> 15:  C11 orphan reference                      (every references/**/*.md is reachable from SKILL.md)
      -> 16:  C12 out-of-skill path                     (a path that resolves only in a full checkout of this repo)
      -> 17:  C13 anti-trigger clause                   (the description says where the skill does NOT apply)
      ```

- [x] 2.5 Selftest: mutação por check (`C11` cria `references/orphan-probe.md`; `C12` anexa
      `bug-hunter/references/track-fivem-lua.md` em crase; `C13` substitui a description de
      `r3f-physics` por uma sem cláusula); o laço aceita mutação que cria arquivo

      ```
      python3 scripts/selftest-validate-skills.py
      -> [...]
      ->   CAUGHT  C11 orphan reference
      ->   CAUGHT  C12 out-of-skill path
      ->   CAUGHT  C13 anti-trigger clause
      -> 18/18 defect classes detected
      exit=0
      ```

## 3. Conteúdo do catálogo (R1, R2, R4)

- [x] 3.1 Caminhos cruzados reescritos como `skills/<skill>/references/<arquivo>` com a frase que
      nomeia a skill: `fivem-lua`, `openspec-drivezone`, `python-rest-api`, `assettoserver-csp-lua`
      (2), `assettoserver-plugin`, `backlog/references/backlog-config.md` (2, uma em fence),
      `backlog/references/issue-template.md`

      ```
      grep -rn "\`bug-hunter/references\|\`execute-backlog/references" skills --include=SKILL.md --include=*.md | grep -v "^skills/execute-backlog/"
      -> (vazio)
      grep -rn "skills/bug-hunter/references/track-" skills/fivem-lua skills/openspec-drivezone skills/python-rest-api skills/assettoserver-csp-lua skills/assettoserver-plugin | wc -l
      -> 7      (fivem-lua 1, openspec-drivezone 2, python-rest-api 1, assettoserver-csp-lua 2, assettoserver-plugin 1)
      python3 scripts/validate-skills.py | grep -c "C1 missing path"     -> 0   (os seis caminhos existem)
      ```

- [x] 3.2 `code-locale`: `claude/global/hooks/locale-rite.py` (2) vira URL do repositório

      `skills/code-locale/SKILL.md:25` (compatibility, ≤ 500 chars: a URL vai para o corpo) e `:179`
      (link `https://github.com/solvelab/ai-skills/blob/master/claude/global/hooks/locale-rite.py`).
      Primeira tentativa deixou `compatibility` em 621 chars e C10 reprovou (`compatibility is 621
      chars, limit 500`); reescrita para 490.

- [x] 3.3 Cláusula de não-uso em `conventional-commit`, `r3f-geometry`, `r3f-physics`,
      `r3f-postprocessing`; redirecionamento em `python-rest-api` e `svg-animation`

      `python3 scripts/validate-skills.py | grep -c "C13"` -> `0` (era 6 em `master`).
      `svg-animation`: "a hand-off to the r3f-* skills for 3D" -> "a hand-off to `r3f-animation` for
      3D" (a família não nomeia skill; a irmã nomeada é a que ganha o redirecionamento recíproco).

- [x] 3.4 Redirecionamentos recíprocos: `python-rest-api` ↔ `api-resilience-testing`,
      `r3f-animation` → `svg-animation`, `fivem-lua` → `assettoserver-csp-lua`

      ```
      grep -c "that is \`api-resilience-testing\`" skills/python-rest-api/SKILL.md       -> 1
      grep -c "that is \`python-rest-api\`" skills/api-resilience-testing/SKILL.md       -> 1
      grep -c "that is \`svg-animation\`" skills/r3f-animation/SKILL.md                  -> 1
      grep -c "that is \`assettoserver-csp-lua\`" skills/fivem-lua/SKILL.md              -> 1
      ```

- [x] 3.5 Toda description editada ≤ 1024 caracteres parseados e com as mesmas frases entre aspas de
      antes (tabela antes/depois); toda skill editada sobe patch em `metadata.version`

      `desc_compare.py <árvore bfc400d> <branch>` (PyYAML, `len()` do valor parseado, frases
      `"…"` extraídas por regex e comparadas em ordem):

      | skill | antes | depois | frases entre aspas | ≤ 1024 |
      |---|---|---|---|---|
      | conventional-commit | 472 | 616 | 0/0 iguais | sim |
      | r3f-geometry | 186 | 300 | 0/0 iguais | sim |
      | r3f-physics | 238 | 388 | 0/0 iguais | sim |
      | r3f-postprocessing | 270 | 433 | 0/0 iguais | sim |
      | python-rest-api | 885 | 977 | 0/0 iguais | sim |
      | svg-animation | 998 | 997 | 6/6 iguais | sim |
      | api-resilience-testing | 735 | 828 | 6/6 iguais | sim |
      | r3f-animation | 333 | 400 | 0/0 iguais | sim |
      | fivem-lua | 520 | 613 | 0/0 iguais | sim |

      Versões depois (`q1_frontmatter.py`): fivem-lua 1.3.2, openspec-drivezone 2.1.3,
      python-rest-api 1.4.2, assettoserver-csp-lua 1.1.1, assettoserver-plugin 1.3.2, backlog 1.5.1,
      code-locale 1.3.1, conventional-commit 1.3.1, r3f-geometry 1.2.1, r3f-physics 1.2.1,
      r3f-postprocessing 1.2.1, svg-animation 1.1.2, r3f-animation 1.2.1, api-resilience-testing 1.3.1.

## 4. Wrappers Cursor/Copilot por URL (D5)

- [x] 4.1 `generate.sh`: sed do Cursor reescreve `](references/` para a URL `blob/master/skills/<nome>/references/`;
      linha "Reference files … live at <URL>" depois do frontmatter quando há `references/`; Copilot
      aponta `references/` para `tree/master/…`; `claude/`, `codex/`, `plugins/` intocados

      ```
      grep -n "REPO_BLOB_URL=\|REPO_TREE_URL=" generate.sh
      -> 89:REPO_BLOB_URL="https://github.com/solvelab/ai-skills/blob/master"
      -> 90:REPO_TREE_URL="https://github.com/solvelab/ai-skills/tree/master"
      bash generate.sh   (sobre a árvore com o conteúdo já commitado em ccca1c2)
      git status --porcelain | wc -l                                  -> 60   (29 cursor + 29 copilot + generate.sh + README.md)
      git status --porcelain | grep -c "^ M claude/\|^ M codex/\|^ M plugins/"   -> 0
      grep -l "^Reference files (" cursor/rules/*.mdc | wc -l          -> 29
      grep -l "tree/master/skills/.*/references/" copilot/instructions/*.md | wc -l   -> 29
      grep -rl "\.\./\.\./skills" cursor/rules | wc -l                 -> 0    (era 10)
      grep -l "\](../../skills" copilot/instructions/*.md | wc -l      -> 35   (o link SKILL.md; follow-up, E.4)
      ```

- [x] 4.2 `bash generate.sh` duas vezes: a segunda sem diff

      Antes do commit: `bash generate.sh` -> `git status --porcelain --untracked-files=all | wc -l`
      -> `109`; segunda execução -> `109`, `git diff --stat | tail -1` -> `109 files changed`
      (mesmo conjunto). Depois de tudo commitado, no gate runner:
      `PASS generate :: Generated 10 category plugins in plugins/` e `PASS tree-clean-after-generate`,
      `dirty-after: 0`.

## 5. README

- [x] 5.1 Notas Cursor/Copilot do bloco de instalação dizem que `references/` resolve pela URL do
      repositório

      ```
      grep -n "references/ links resolve through the repository URL\|references/ resolve through the same repository URL" README.md
      -> 145:# (each .mdc is self-contained; its references/ links resolve through the repository URL,
      -> 150:# (references/ resolve through the same repository URL; the SKILL.md link still expects the clone)
      ```

- [x] 5.2 Parágrafo do validador lista treze checks (C1-C13)

      ```
      grep -n "runs thirteen checks\|(C11)\|(C12)\|(C13)" README.md
      -> 778:[`scripts/validate-skills.py`](scripts/validate-skills.py) runs thirteen checks over every
      -> 785:`references/**/*.md` is reachable from its `SKILL.md` (C11), no path resolves only in a full checkout
      -> 787:outside `skills/` as a repository URL (C12), and every description says where the skill does *not*
      -> 788:apply (C13). [...]
      ```

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 O validador exercitado pelo caminho real (`python3 scripts/validate-skills.py` como o CI
      o invoca) em `master`, no branch e em cópias com cada mutação; um `.mdc` e um
      `.instructions.md` regenerados abertos; `curl -sI` numa URL gerada

      **`master`** — árvore de `bfc400d` exportada com `git archive` para o scratchpad, o validador
      do branch rodado de dentro dela (`cwd` = a cópia), 2026-09-05:

      ```
      python3 scripts/validate-skills.py
      -> skills checked: 35   findings: 18
      ->   C12 out-of-skill path  12
      ->   C13 anti-trigger clause 6
      -> assettoserver-csp-lua  [C12] inline -> bug-hunter/references/track-dotnet-plugin.md [...]  (x2)
      -> assettoserver-plugin   [C12] inline -> bug-hunter/references/track-dotnet-plugin.md [...]
      -> backlog/backlog-config.md [C12] inline -> execute-backlog/references/spec-rite.md [...]
      -> code-locale            [C12] inline -> claude/global/hooks/locale-rite.py: exists only in a clone [...]  (x2)
      -> execute-backlog/board-sync.md [C12] inline -> backlog/references/backlog-config.md [...]; inline -> backlog/references/gh-projects.md [...]
      -> fivem-lua              [C12] inline -> bug-hunter/references/track-fivem-lua.md [...]
      -> openspec-drivezone     [C12] inline -> bug-hunter/references/track-fivem-lua.md [...]; track-python-pytest.md [...]
      -> python-rest-api        [C12] inline -> bug-hunter/references/track-python-pytest.md [...]
      -> conventional-commit, python-rest-api, r3f-geometry, r3f-physics, r3f-postprocessing, svg-animation  [C13] description names no boundary [...]
      exit=1
      ```

      Por check em `master`: C11 0, C12 12, C13 6.

      **Branch** (`e116c18`), pelo mesmo comando:

      ```
      python3 scripts/validate-skills.py
      -> skills checked: 35   findings: 2
      ->   C12 out-of-skill path  2
      -> execute-backlog/board-sync.md
      ->    [C12 out-of-skill path] inline -> backlog/references/backlog-config.md: cross-skill path without the skills/ prefix [...]
      ->    [C12 out-of-skill path] inline -> backlog/references/gh-projects.md: cross-skill path without the skills/ prefix [...]
      exit=1
      ```

      Os dois restantes são o diretório do outro item (E.4, S.3). Nas skills deste item: 0.

      **Cópias com uma mutação cada** (`simulate_mutations.py`: `copytree` do branch para um
      diretório temporário, uma edição, `python3 scripts/validate-skills.py` com `cwd` na cópia; as
      duas linhas de `execute-backlog` aparecem em todas e foram omitidas abaixo):

      ```
      C11 orphan-probe.md sem link em r3f-geometry
      -> findings: 3  [C11 orphan reference] references/orphan-probe.md is linked from neither SKILL.md nor a reachable reference
      C11 controle: arquivo já linkado                              -> findings: 2  (mudo)
      C12 `bug-hunter/references/track-fivem-lua.md` em fivem-lua
      -> findings: 3  [C12 out-of-skill path] inline -> bug-hunter/references/track-fivem-lua.md: cross-skill path without the skills/ prefix — write skills/bug-hunter/refe[...]
      C12 `research/svg-animation/verify-motion.mjs` em svg-animation
      -> findings: 3  [C12 out-of-skill path] inline -> research/svg-animation/verify-motion.mjs: exists only in a clone of this repository — use https://github.com/solvela[...]
      C12 link ../../research/notes.md a partir de backlog/references/gh-projects.md
      -> findings: 4  [C12 out-of-skill path] link -> ../../research/notes.md: resolves outside skills/backlog/   (+ C1 missing path, o arquivo não existe)
      C12 controle: `skills/bug-hunter/references/track-fivem-lua.md` (forma canônica)   -> findings: 2  (mudo)
      C12 controle: `docs/SETUP.md` (raiz não julgada, declarada)                       -> findings: 2  (mudo)
      C13 description de r3f-physics sem cláusula
      -> findings: 3  [C13 anti-trigger clause] description names no boundary: add a "Do NOT use for … (that is `<skill>`)" clause or a redirect [...]
      C13 controle: "For tweens see r3f-animation" (sem crase)                          -> findings: 2  (mudo)
      C13 escape declarado: "Use when working in fivem-lua projects too"               -> findings: 2  (mudo, como o KNOWN LIMIT diz)
      ```

      **Wrappers regenerados**, abertos:

      ```
      sed -n 5,10p cursor/rules/backlog.mdc
      -> ---
      ->
      -> Reference files (`references/…` below) live at https://github.com/solvelab/ai-skills/tree/master/skills/backlog/references/
      ->
      -> # Backlog — idea → structured GitHub Project item
      grep -n "references/" cursor/rules/r3f-geometry.mdc | head -2
      -> 7:Reference files (`references/…` below) live at https://github.com/solvelab/ai-skills/tree/master/skills/r3f-geometry/references/
      -> 23:| [Built-in Geometries](https://github.com/solvelab/ai-skills/blob/master/skills/r3f-geometry/references/built-in-geometries.md) | [...]
      cat copilot/instructions/backlog.instructions.md
      -> # backlog
      -> Follow the instructions in [SKILL.md](../../skills/backlog/SKILL.md)
      -> Reference files: [references/](https://github.com/solvelab/ai-skills/tree/master/skills/backlog/references/)
      grep -o "https://github.com/solvelab/ai-skills/blob/master/skills/r3f-geometry/references/[a-z-]*\.md" cursor/rules/r3f-geometry.mdc | head -1 | xargs curl -sI | head -1
      -> HTTP/2 200
      grep -o "https://github.com/solvelab/ai-skills/tree/master/skills/backlog/references/" copilot/instructions/backlog.instructions.md | head -1 | xargs curl -sI | head -1
      -> HTTP/2 200
      ```

      Gate runner (todos os steps de `ci.yml` mais os novos), na árvore commitada:
      `PASS` em generate, tree-clean, version, frontmatter, selftest-validate-skills (18/18),
      locale-detector, locale-rite, backlog-rite, verify-rite, scan-secrets (+selftest), hygiene
      (+selftest), rite, rite-evidence-selftest, spec-rite-selftest, smoke (17/17), plugin-validate,
      openspec-strict; `FAIL validate-skills (rc=1)` só pelas duas linhas de `execute-backlog`;
      `dirty-after: 0`.

- [x] S.2 Matriz de casos medida, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | Tinha de disparar e disparou | 5/5 | C11 órfão (1); C12 caminho cruzado sem prefixo (1), raiz `research/` (1), link `..` fora da skill (1); C13 description sem cláusula (1) |
      | Tinha de ficar mudo e ficou | 5/5 | C11 arquivo linkado (1); C12 forma canônica `skills/<outra>/references/` (1), raiz não julgada `docs/` (1); C13 redirecionamento sem crase (1); URLs `https://…/research/…` já presentes em `svg-animation` (1, no baseline) |
      | Escape conhecido ficou mudo | 1/1 | C13 "working in fivem-lua" numa frase-gatilho (KNOWN LIMIT do check) |
      | Achados de `master` corrigidos | 16/18 | 10 C12 + 6 C13 nas skills deste item; 2 C12 restantes em `execute-backlog` (outro item) |
      | Selftest do CI | 18/18 | 15 classes anteriores + C11, C12, C13 |
      | Wrappers | 29/29 + 29/29 | `.mdc` com linha de URL e links reescritos; `.instructions.md` com `references/` por URL; 0 caminhos `../../skills` restantes em `cursor/` |
      | `generate.sh` idempotente | 2/2 | segunda execução sem diff; `dirty-after: 0` |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      - **Dois achados C12 permanecem no branch**, em `skills/execute-backlog/references/board-sync.md:5`
        (`backlog/references/gh-projects.md`) e `:45` (`backlog/references/backlog-config.md`). O
        diretório é de outro item em paralelo e não foi editado (design D6). O step
        *Skill content checks* do CI reprova até a correção — duas linhas
        (`skills/backlog/references/…` + a frase nomeando `backlog`) e bump patch de `execute-backlog`.
      - A mutação "link `../../research/notes.md`" disparou **dois** achados, não um: C12 (resolve
        fora da skill) e C1 (o arquivo não existe). Esperado era C12; o C1 é correto e independente.
      - Primeira versão da correção em `code-locale` levou `compatibility` a 621 caracteres e C10
        reprovou; a URL foi movida para o corpo (`:179`) e `compatibility` ficou em 490.
      - Escape declarado e medido: uma frase-gatilho "in <irmã>" passa C13 (KNOWN LIMIT); caminhos
        sob `openspec/`, `scripts/`, `docs/`, `.github/` não são julgados por C12 (D2), então
        `verify-before-claiming/references/failure-catalog.md` continua citando três arquivos deste
        repositório em crase (E.4).
      - O comportamento do Cursor/Copilot ao encontrar a URL não foi observado (E.3): o que se mediu
        foi a forma do arquivo e o `200` da URL.

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado: name == diretório, description dobrada,
      author solvelab, semver, categoria no conjunto, license MIT, compatibility presente

      `q1_frontmatter.py` (PyYAML) sobre as 14 skills editadas -> `uniform=True` em 14/14, todas
      com `description` ≤ 1024 e `compatibility` ≤ 500; o laço de frontmatter do CI (gate runner)
      -> `PASS frontmatter`.

- [x] Q.2 Conteúdo de skill tocado em inglês — as frases novas ("Do NOT use for …", "the file
      `skills/…` in the `bug-hunter` skill") e a linha dos wrappers estão em inglês; os deltas de
      spec em inglês; o rito (proposal/design/tasks) em português, como o repositório

- [x] Q.3 Gatilhos testáveis: cada cláusula nova nomeia a irmã com quem a skill competia e nenhuma
      frase entre aspas foi removida — tabela em 3.5 (6/6 e 6/6 frases iguais em `svg-animation`
      e `api-resilience-testing`; as demais não tinham frases entre aspas). Pares fechados:
      `python-rest-api` ↔ `api-resilience-testing` ("review an endpoint": o primeiro redireciona
      "test, break or audit an existing endpoint", o segundo "the service's own layout, envelope and
      handlers"); `r3f-animation` → `svg-animation` (2D/SVG/CSS); `fivem-lua` →
      `assettoserver-csp-lua` (CSP Lua on an Assetto Corsa server); `svg-animation` →
      `r3f-animation` (3D). Novas cláusulas: `conventional-commit` → `code-locale`, `backlog`;
      `r3f-geometry` → `r3f-materials`, `r3f-physics`; `r3f-physics` → `r3f-animation`,
      `r3f-geometry`; `r3f-postprocessing` → `r3f-materials`, `r3f-interaction`.

- [x] Q.4 Sem doutrina duplicada: tabela de Canonical Home em `design.md` (sete linhas; a regra de
      referência cruzada muda para o spec, os `track-*.md` continuam só em `bug-hunter`, nada é
      copiado entre skills)

- [x] Q.5 Identificadores em inglês no que a change introduz (`code-locale`)

      ```
      git diff -- skills scripts generate.sh README.md > work.diff
      python3 skills/code-locale/references/check-identifier-locale.py --diff work.diff
      -> findings: 0
      -> en-unknown: 1 segment(s) not in the English word list — advisory — they do not fail this run
      ```

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate define-cross-skill-references --strict` verde

      ```
      openspec validate define-cross-skill-references --strict   -> Change 'define-cross-skill-references' is valid   (openspec 1.6.0)
      ```

- [x] V.2 Descoberta do catálogo intacta: 35 skills, `validate-skills.py` sem achados nas skills deste
      item

      ```
      ls skills | wc -l                        -> 35
      python3 scripts/validate-skills.py       -> skills checked: 35   findings: 2   (ambos em execute-backlog/board-sync.md, S.3)
      claude plugin validate . --strict        -> ✔ Validation passed
      ```

- [x] V.3 README / docs atualizados (grupo 5) — bloco de instalação e parágrafo do validador
- [ ] V.4 `openspec archive define-cross-skill-references --yes` em PR separado, depois do merge
