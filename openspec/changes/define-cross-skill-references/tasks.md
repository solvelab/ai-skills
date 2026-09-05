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
        arquivo é copiado isolado; R5 fala só de `references/`, então fica como follow-up.
      - `verify-before-claiming/references/failure-catalog.md` cita `scripts/validate-rite.sh`,
        `openspec/specs/skills-authoring/spec.md` e `.github/workflows/ci.yml` deste repositório em
        crase — raízes que C12 declara não julgar (design D2). Converter para URL é follow-up.
      - `skills/backlog/references/backlog-config.md:32` cita `execute-backlog/references/board-sync.md`
        dentro de um fence YAML (comentário de config): fora do alcance de C12 por desenho, mas
        corrigido junto por ser texto deste item.
      - Pins `Verified against` como check: issue #131, fora deste item.

## 2. Validador: C11, C12, C13 e selftest (D2, D3, D4, D7)

- [ ] 2.1 `check_orphan_refs` (C11): BFS a partir de `SKILL.md` sobre links e inline paths fora de
      fences, só `*.md`, transitivo; docstring declara o que não cobre
- [ ] 2.2 `check_out_of_skill` (C12): `CATALOG_ONLY_ROOTS`, `<skill>/references/` sem prefixo, link
      `..` que sai de `skills/<x>/`; texto de link não é julgado; docstring declara as raízes não
      julgadas
- [ ] 2.3 `check_anti_trigger` (C13): `ANTI_TRIGGER_PHRASES` e `REDIRECT_WORDS` + nome de irmã,
      sobre a description parseada; skip declarado sem PyYAML
- [ ] 2.4 Docstring C1..C13; `main()` chama os três (C12 também em `references/*.md`)
- [ ] 2.5 Selftest: mutação por check (`C11` cria `references/orphan-probe.md`; `C12` anexa
      `bug-hunter/references/track-fivem-lua.md` em crase; `C13` substitui a description de
      `r3f-physics` por uma sem cláusula); o laço aceita mutação que cria arquivo

## 3. Conteúdo do catálogo (R1, R2, R4)

- [ ] 3.1 Caminhos cruzados reescritos como `skills/<skill>/references/<arquivo>` com a frase que
      nomeia a skill: `fivem-lua`, `openspec-drivezone`, `python-rest-api`, `assettoserver-csp-lua`
      (2), `assettoserver-plugin`, `backlog/references/backlog-config.md` (2, uma em fence),
      `backlog/references/issue-template.md`
- [ ] 3.2 `code-locale`: `claude/global/hooks/locale-rite.py` (2) vira URL do repositório
- [ ] 3.3 Cláusula de não-uso em `conventional-commit`, `r3f-geometry`, `r3f-physics`,
      `r3f-postprocessing`; redirecionamento em `python-rest-api` e `svg-animation`
- [ ] 3.4 Redirecionamentos recíprocos: `python-rest-api` ↔ `api-resilience-testing`,
      `r3f-animation` → `svg-animation`, `fivem-lua` → `assettoserver-csp-lua`
- [ ] 3.5 Toda description editada ≤ 1024 caracteres parseados e com as mesmas frases entre aspas de
      antes (tabela antes/depois); toda skill editada sobe patch em `metadata.version`

## 4. Wrappers Cursor/Copilot por URL (D5)

- [ ] 4.1 `generate.sh`: sed do Cursor reescreve `](references/` para a URL `blob/master/skills/<nome>/references/`;
      linha "Reference files live at <URL>" depois do frontmatter quando há `references/`; Copilot
      aponta `references/` para `tree/master/…`; `claude/`, `codex/`, `plugins/` intocados
- [ ] 4.2 `bash generate.sh` duas vezes: a segunda sem diff

## 5. README

- [ ] 5.1 Notas Cursor/Copilot do bloco de instalação dizem que `references/` resolve pela URL do
      repositório
- [ ] 5.2 Parágrafo do validador lista treze checks (C1-C13)

## 6. Simulation & Field Proof (MANDATORY)

- [ ] S.1 O validador exercitado pelo caminho real (`python3 scripts/validate-skills.py` como o CI
      o invoca) em `master`, no branch e em cópias com cada mutação; um `.mdc` e um
      `.instructions.md` regenerados abertos; `curl -sI` numa URL gerada
- [ ] S.2 Matriz de casos medida, em contagens
- [ ] S.3 O que escapou ou se comportou diferente do esperado

## 7. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado: name == diretório, description dobrada,
      author solvelab, semver, categoria no conjunto, license MIT, compatibility presente
- [ ] Q.2 Conteúdo de skill tocado em inglês
- [ ] Q.3 Gatilhos testáveis: cada cláusula nova nomeia a irmã com quem a skill competia e nenhuma
      frase entre aspas foi removida
- [ ] Q.4 Sem doutrina duplicada: tabela de Canonical Home em `design.md`
- [ ] Q.5 Identificadores em inglês no que a change introduz (`code-locale`)

## 8. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate define-cross-skill-references --strict` verde
- [ ] V.2 Descoberta do catálogo intacta: 35 skills, `validate-skills.py` sem achados nas skills deste
      item
- [ ] V.3 README / docs atualizados (grupo 5)
- [ ] V.4 `openspec archive define-cross-skill-references --yes` em PR separado, depois do merge
