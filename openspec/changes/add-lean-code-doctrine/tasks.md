## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `f11ba7a` (`chore(research): harness lean-code com arms isolados e baseline medido no
      modelo diário (#160)`), topo de `master` em 2026-09-05, na worktree
      `.claude/worktrees/wf_8fa55870-ad1-1`:

      - `research/lean-code/results/20260905-211512-baseline-defects.md` — 27 células, flags por arm
        (`class_for_oneliner` 6/27, `no_check` 3/27, `prose_gt_code` 1/27, os outros 0/27), tabela
        por tarefa (`csv-sum` 102 / 81 / 127; `safe-path` 67,667 / 59 / 82; `trace-transfer` 27 /
        26 / 28), *Flag sanity* (`new_dependency` 8 → 0, `class_for_oneliner` 9 → 6), *Defect
        classification* (exceção custom 6, tolerância especulativa 6, helpers 4, validação de tipo 3,
        docstring 12, cursor housekeeping 3), *Over-build, read from the diffs*, *Environment*.
      - `research/lean-code/results.md` — a tabela de estágios (sonda $0,0457, piloto $0,5571,
        baseline $9,4529), "skill arm — not yet measured", *What this does not cover*.
      - `research/lean-code/protocol.md` — *Arms* (a tabela com o arm `skill` = "same, with
        `skillOverrides.lean-code = "on"` and the *Lean Code* block"), *Cell*, *Metrics*, *Flags*,
        *Tasks*, *Sequence*, *Verdict*, *Review lens — false-positive rules* (as 5 regras de FP),
        *What this protocol does not cover*.
      - `research/lean-code/run.py` — `DEFAULT_SKILL`, `SENTINEL`, `KEEP_SETTINGS_KEYS`,
        `HARNESS_PATHS` (155-180); `workspace_files` (315-319); `arm_settings`,
        `prepare_arm_settings_sources` (693-720); `settings_sources_preflight` (768-800);
        `cmd_prepare_arms` (862-925); `cmd_matrix` (1045+; `arm_preflight` por arm e a recusa por
        `claude_version`); `probe_workspace` (1404); `selftest_isolation` (1752-1885); `main`
        (2034-2085, `--rules-ref`, `--skill`, `--ponytail-dir`).
      - `research/lean-code/README.md` — *Running things* (passos 1-5), *Status*.
      - `research/lean-code/vendor/ponytail/PIN` — commit `974d940a1c5344210874150b98ff0d2c861fab6a`,
        `version: 4.9.0`, sha256 do `LICENSE`.
      - Clone do upstream em `$SCR/ponytail` (`git log -1` → `974d940a…`, `package.json`
        `"version": "4.9.0"`): `skills/ponytail/SKILL.md` (120 linhas; escada 32-48, causa raiz
        50-54, regras 56-64, saída 66-75, intensidade 77-88, carve-outs 90-112, boundaries 114-120),
        `skills/ponytail-review/SKILL.md` (57 linhas; formato 16-27, exemplos 29-42, scoring 44-48,
        boundaries 50-57), `skills/ponytail-audit/SKILL.md`, `skills/ponytail-debt/SKILL.md`,
        `docs/platform-native.md` (211 linhas; Swift em 89-125; debounce em 80-85),
        `examples/email-validation.md`, `LICENSE` (MIT, "Copyright (c) 2026 DietrichGebert").
      - `skills/verify-before-claiming/SKILL.md` — frontmatter (`version: 1.1.0`), *Off-script
        guard* 170-186 ("Before acting, restate. One block, three parts — Doing / Not doing /
        Assumptions"), *See also* 204-211.
      - `skills/bug-hunter/SKILL.md` (`version: 2.2.4`, *See also* 89-96), `skills/code-locale/SKILL.md`
        (`version: 1.4.1`; *Reviewing a diff* 132-157, "The waiver covers its own line and the next
        one"; *See also* 238-247), `skills/log-event-collector/SKILL.md` (`version: 1.1.1`; a regra
        "no new supply chain for the sake of ergonomics" em 50-53; *See also* 209-217).
      - `openspec/specs/skills-authoring/spec.md` — *Single canonical home per rule* 11-46 (copiado
        por inteiro no delta), *Uniform frontmatter metadata* 48-104 (1024/500 no valor parseado),
        *Versioned external APIs are pinned* 251-266, *Authoring rules are machine-enforced*
        336-402, *Checklists are scored against field defects* 404-432, *Triggers live in the
        description* 433-472, *A skill's version moves with its content* 549-613, *Cross-skill
        references resolve in every install form* 615-674.
      - `openspec/specs/skills-catalog/spec.md` — *Catalog composition* 10-40, *Claim verification
        has a canonical home* 309-350 (modelo do requisito ADDED), *A shipped checklist names the
        defect behind each row* 351-361, *Code locale has a canonical home* 647-698.
      - `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md`;
        `openspec/config.yaml` (schema `skills-rite`, as duas regras de `tasks`).
      - `openspec/changes/archive/2026-09-05-add-locale-adoption-kit/{proposal,design,tasks}.md` e
        `openspec/changes/add-lean-code-research/{proposal,design,tasks}.md` — modelo de estilo.
      - `scripts/validate-skills.py` — C1/C2 (77-126: `INLINE` só julga caminhos que começam com
        `references/` ou `skills/`), C3 (127-168), C4 (219-243), C5 (244-303), C8 (319-333,
        `META_HEADING`), C9 (170-217), C10 (335-391), C11 (393-452), C12 (454-526,
        `CATALOG_ONLY_ROOTS`), C13 (528-578, `ANTI_TRIGGER_PHRASES`, `REDIRECT_WORDS`).
      - `scripts/validate-rite-evidence.py` (1-140), `scripts/validate-spec-rite.py` (1-80),
        `scripts/validate-skill-version.py` (1-60), `scripts/validate-rite.sh` (1-60),
        `scripts/validate-repo-hygiene.py` (H2, 77-120).
      - `generate.sh` 1-80 (`GROUP_THEME`, o comentário "Keep names and numbers out of these
        strings", `group_of`); `README.md` 51, 59, 95, 625-635, 929.
      - `claude/global/personal-rules.md` — headings em 7, 14, 24, 39 (*Code Locale*), 64, 69, 79.
      - `~/.claude/skills/execute-backlog/SKILL.md` + `references/spec-rite.md` (o gate, a linha
        `Spec-rite:`, `Skill-version: none —`, "Archive is not part of this run").
      - `/home/diegops/.claude/plans/esse-o-repositorio-recursive-barto.md` — o plano aprovado; a
        seção *Recomendação* e *Decisões fechadas (2026-09-05)*.
      - Issue #146 (`gh issue view 146 --json body`): escopo, FR1-FR5, TR1-TR4, os seis critérios
        de aceite, o glossário (`lean:`, as 5 tags, `net: -N lines possible.`), o veredito
        `add-lean-code-doctrine`.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      python3 --version                 -> Python 3.14.5
      node --version                    -> v26.0.0
      which lua                         -> /home/linuxbrew/.linuxbrew/bin/lua
      claude --version                  -> 2.1.261 (Claude Code)
      openspec --version                -> 1.6.0
      $SCR/venv-A/bin/agentskills --version              -> agentskills, version 0.1.1
      $SCR/venv-A/bin/agentskills validate skills/code-locale -> Valid skill: skills/code-locale  rc=0
      ls ~/.claude/skills/lean-code     -> No such file or directory   (a skill não está instalada; o baseline continua limpo)
      ls ~/.claude/skills | wc -l       -> 35 entradas (symlinks do install.sh)
      ```

      Ausência de doutrina, medida em `f11ba7a`; e o grep do ledger na árvore commitada — que **não**
      dá zero, porque o harness carrega o marcador como string de fixture e a change do item #145 o
      cita em prosa (a primeira medição desta sessão escreveu "0": um glob não citado fez o `grep`
      não rodar e o `wc -l` contou uma saída vazia; corrigido aqui com `git grep` no commit):

      ```
      grep -rniE "yagni|less code|smallest change|speculative|over-engineer|dead code|tech debt" skills/ claude/global/personal-rules.md | wc -l
      -> 0
      /usr/bin/git grep -nE '(#|//|--) ?lean: ' f11ba7a -- . | wc -l
      -> 4        (research/lean-code/run.py 3 — marker_ok, marker_bad e o CLAUDE.md sintético do selftest; openspec/changes/add-lean-code-research/tasks.md 1 — prosa)
      ```

      O upstream no clone, e a licença que tem de viajar com o texto copiado:

      ```
      /usr/bin/git -C $SCR/ponytail log -1 --format='%H'   -> 974d940a1c5344210874150b98ff0d2c861fab6a
      grep -m1 '"version"' $SCR/ponytail/package.json     -> "version": "4.9.0",
      head -3 $SCR/ponytail/LICENSE                        -> MIT License / Copyright (c) 2026 DietrichGebert
      ```

      Scaffold da change com o schema do repositório:

      ```
      openspec new change add-lean-code-doctrine --schema skills-rite
      -> Created change 'add-lean-code-doctrine' at openspec/changes/add-lean-code-doctrine/
      -> Schema: skills-rite
      openspec validate add-lean-code-doctrine --strict   -> Change 'add-lean-code-doctrine' is valid
      ```

- [x] E.3 O que não pôde ser probado nesta parte

      Três itens, todos pagos ou interativos, todos do mantenedor (parte B):

      - ~~**O efeito da skill.**~~ Medido pelo mantenedor em 2026-09-06 (S.4): 27 células do arm
        `skill` + 2 + 3 de `reuse-slug`; o veredito pela letra do protocolo era **INCONCLUSIVE**
        (`research/lean-code/results.md`), então `SKILL.md` e README ficaram sem número sobre o
        efeito — a seção `## What the baseline measured` citava só o baseline e dizia onde o
        veredito morava. Em 2026-09-06 01:37 (S.4.2) as +2 repetições de `cache` e `csv-sum`
        rodaram e a releitura deu **SHIP**: a seção virou `## What the catalog measured` e carrega o
        Δ do grupo over-build (−34,4 %) com as condições; a linha do README do catálogo também.
      - **Se a description roteia numa sessão real.** A simulação lexical de S.1 mede se o sinal
        léxico existe (6 prompts contra as 36 descriptions); o roteador real é o modelo. A sessão
        interativa com a skill instalada (prompt com armadilha de over-build + bug de dois callers)
        é critério de aceite da issue e fica com o mantenedor (S.6).
      - ~~**Se `skillOverrides.lean-code = "on"` carrega a skill na célula.**~~ Medido pelo mantenedor
        em 2026-09-05 (parte B, sessão principal): **não carrega** — com `--setting-sources
        project,local` o `~/.claude/skills` não é lido (três células da lente: "lean-code isn't in
        the available-skills list"; leituras em `~/.claude/skills/` e `~/ai-skills/` negadas). A
        skill de projeto (`<cwd>/.claude/skills/lean-code`) carrega; ver 4.2. O que continua sem
        prova paga nesta worktree: uma célula do arm `skill` novo — a sonda `--probe-isolation` do
        mantenedor (`skill_visible`) é o próximo passo pago, antes da matriz.

      O `--claude-block` foi provado pelo `--selftest` (arm sintético, casos presente/ausente) e pelo
      `--prepare-arms` real contra um `--arms-root` de rascunho (4.1) — nunca por uma célula.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #146 pediu, menos a parte paga, entregue como comandos exatos.
      Notados pelo caminho e **não** feitos, ficam como follow-up:

      - Estreitar a description se a sessão real mostrar que ela rouba prompts de irmãos ou nunca
        dispara — decisão da issue: medir antes de estreitar. Um gatilho foi **acrescentado** (não
        estreitado) nesta parte, `"add a cache"`, porque a simulação lexical mostrou empate (S.3).
      - Kit de adoção do ledger por repositório (pre-commit/CI para `lean:` sem `->`) — excluído
        pela própria issue.
      - `_diff.patch` das células lista `__pycache__/*.pyc` (observado no baseline-defects.md):
        cosmético, fora desta issue.
      - O roteador léxico de S.1 ficou fora do repositório (`<scratch>/route-sim.py`), como o do
        item #122: `research/lean-code/` recebe só o que o arm da skill precisa (`--claude-block`,
        `arms-block.md`); a saída medida é a evidência, registrada em S.1. Entrou por engano num
        commit da branch e saiu na revisão.
      - O `## Rules` verbatim mantém "Fewest files possible"; o catálogo tem skills que exigem
        arquivos por camada (`python-rest-api`). Não harmonizado: a regra é "shortest working diff
        **once you understand the problem**" e o texto de deferência já manda o layout do stack
        vencer; um choque real seria um item novo.
      - `research/lean-code/results.md` não muda nesta parte: só a matriz do mantenedor escreve
        nele.
      - O grep do ledger acha os exemplos da própria skill e as fixtures do harness (S.2); um
        `--exclude` para a documentação da convenção seria decisão de cada repositório que adota o
        ledger, e `simplification-ledger.md` diz para removê-los à mão.

## 2. Skill `lean-code`

- [x] 2.1 `skills/lean-code/SKILL.md` v1.0.0 (217 linhas; commit `061f16f`, description ajustada
      em `9087e27`): frontmatter uniforme, description 1015 chars parseados com gatilhos EN+PT e
      cláusula de não-uso nomeando `verify-before-claiming`, `bug-hunter`, `documentation` e o
      `/simplify` nativo; compatibility 175; seções na ordem do design (D7); escada, causa raiz,
      regras e carve-outs verbatim (D3); nenhuma seção *How to use* / *When to use* (C8); todo bloco
      de código parseia (C3)

      ```
      python3 -c "import yaml; d=yaml.safe_load(open('skills/lean-code/SKILL.md').read().split('---',2)[1]); print(len(d['description']), len(d['compatibility']), d['metadata'])"
      -> 1015 175 {'author': 'solvelab', 'version': '1.0.0', 'category': 'process'}
      python3 -c "... re.finditer(r'^## (.+)$', t, re.M)"
      -> headings: ['The ladder', 'Bug fix = root cause, not symptom', 'Rules', 'What the delivery looks like', 'Never simplified away', 'Reviewing a diff', 'Marking a deliberate simplification', 'What the baseline measured', 'When this skill defers', 'See also']
      -> meta sections: []        fences: ['text', '', 'python', '']
      python3 $SCR/verbatim-check-146.py     (cada segmento do upstream procurado como substring do SKILL.md)
      -> VERBATIM ladder 34-48 / root cause 50-54 / rules 58-61 / rule 63 / carve-outs 92-95 / understanding 97-101 / one check 107-111 / review tags 23-27 / review wrong-style 31-32 / review right-style 34 / thesis last sentence / smuggled prose
      -> 12/12 verbatim segments present     (11/12 antes de re-quebrar a linha do ❌ como no upstream)
      python3 scripts/validate-skills.py     -> skills checked: 36   findings: 0
      $SCR/venv-A/bin/agentskills validate skills/lean-code   -> Valid skill: skills/lean-code   rc=0
      ```

- [x] 2.2 `references/platform-native.md` (173 linhas; sem Swift, debounce com `// lean: … -> …`,
      nota de lookup, nenhuma versão de runtime), `references/simplification-ledger.md` (81),
      `references/review-examples.md` (125 → 134 na revisão do PR, S.3), `references/upstream.md`
      (106 → 110 na revisão do PR; aviso MIT integral,
      mapa verbatim/reescrito/descartado, proveniência por regra, números do upstream com
      condições); as quatro linkadas do índice do `SKILL.md` (C11); caminhos cruzados na forma
      `skills/<skill>/references/<file>` (C12)

      ```
      wc -l skills/lean-code/SKILL.md skills/lean-code/references/*.md   -> 217 / 173 / 125 / 81 / 106 = 702 total
      grep -o 'references/[a-z-]*\.md' skills/lean-code/SKILL.md | sort -u
      -> references/platform-native.md, references/review-examples.md, references/simplification-ledger.md, references/upstream.md
      grep -c "Python 3\.[0-9]\|since Python\|3\.[0-9]+" skills/lean-code/references/platform-native.md   -> 0
      python3 scripts/validate-skills.py   (primeira rodada, antes da correção)
      -> lean-code/upstream.md [C1 missing path] inline -> skills/ponytail/SKILL.md (×8)   [C12 out-of-skill path] inline -> research/lean-code/protocol.md (×2)
      (caminhos do upstream prefixados com o nome do repo, `ponytail/skills/…`; caminhos de research/ como URL do repositório)
      python3 scripts/validate-skills.py   -> skills checked: 36   findings: 0
      ```

## 3. Irmãos, gerador, README, regras pessoais

- [x] 3.1 Uma linha *See also* + bump patch em `verify-before-claiming` (1.1.1), `bug-hunter`
      (2.2.5), `code-locale` (1.4.2), `log-event-collector` (1.1.2); commit `d9ca8e7`

      ```
      grep -n "^  version:" skills/{verify-before-claiming,bug-hunter,code-locale,log-event-collector}/SKILL.md
      -> 1.1.1 / 2.2.5 / 1.4.2 / 1.1.2
      GITHUB_EVENT_PATH=$SCR/event146.json python3 scripts/validate-skill-version.py
      -> skill-version gate: 0 findings (base origin/master, 5 skill(s) changed, 5 with content changes)
      ```

- [x] 3.2 `generate.sh` `GROUP_THEME[workflow]` + "and the lean-code doctrine"; `README.md`: membro
      em `ai-skills-workflow` (linha 59), linha em *Process & git* (636), `all 35` → `all 36` (51,
      95), "the 36 that `git archive HEAD` ships" (930); `bash generate.sh` duas vezes, a segunda
      sem diff; commit `9f876ee`

      ```
      bash generate.sh   -> Generated wrappers for 36 skills / Generated 10 category plugins in plugins/
      git status --porcelain --untracked-files=all | wc -l   -> 41   (segunda rodada: 41, os mesmos caminhos)
      grep -n "all 35\| 35 " README.md   -> (vazio)
      python3 scripts/validate-repo-hygiene.py   -> repo hygiene: 0 findings
      gates.sh: PASS generate / PASS tree-clean-after-generate / PASS plugin-validate :: ✔ Validation passed
      ```

- [x] 3.3 `claude/global/personal-rules.md`: `## Lean Code (the best code is the code never written)`
      depois de *Code Locale*, oito linhas, fecho com o link para a skill; o mesmo bloco sem heading
      em `research/lean-code/arms-block.md`; commit `261367b`

      ```
      python3 $SCR/edit146-block.py   -> block lines: 8
      sed -n '/^## Lean Code/,/^## Commits/p' claude/global/personal-rules.md | wc -l   -> 11  (heading + 8 + branco + próximo heading)
      tail -1 research/lean-code/arms-block.md   -> - Full doctrine, the review lens and the ledger: the `lean-code` skill.
      sha256sum research/lean-code/arms-block.md   -> 81f1633f0971369e3d0bb009c3247ff0d229a7c26f4e246f4691cf433e7770c7
      ```

## 4. Harness: o arm da skill

- [x] 4.1 `run.py --prepare-arms --claude-block <file>`: arm `skill` = sentinela + bloco no
      `claude-snippet.md`, `baseline` = só a sentinela; `claude_block_sha256` em `arm.json` e
      `arms.json`; preflight exige presente no `skill` e ausente no `baseline`; casos novos no
      `--selftest`; `protocol.md` e `research/lean-code/README.md` registram a opção; nenhum arquivo
      de `results/` muda; commit `3f4b43c`

      ```
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest
      -> OK isolation --claude-block: skill snippet = sentinel line + blank line + block; baseline = sentinel only
      -> OK isolation --claude-block: arm.json carries claude_block_sha256 in the skill arm, null in the baseline
      -> OK isolation --claude-block: both arms preflight OK
      -> OK isolation --claude-block: the skill cell's CLAUDE.md carries the block after the sentinel, still a harness path
      -> OK isolation preflight catches the block in the baseline snippet
      -> OK isolation preflight catches a skill snippet without the block arm.json promises
      -> OK isolation preflight catches a block edited after --prepare-arms (sha mismatch)
      -> OK isolation --claude-block: preflight clean again after repairs
      -> selftest: 157/157 OK  (… isolation 33/33 …)   selftest wall time: 2.1s   (era 149/149, isolation 25/25)
      python3 research/lean-code/run.py --prepare-arms --arms-root $SCR/lean-dev/arms-146 --rules-ref HEAD --skill lean-code --claude-block research/lean-code/arms-block.md
      -> arm baseline     claude-snippet.md = sentinel only          preflight OK
      -> arm skill        claude-snippet.md = sentinel + always-on block
      -> arm skill        … preflight FAILED /home/diegops/.claude/skills/lean-code is not installed; skillOverrides 'on' would enable nothing
      (esperado: o mantenedor cria o symlink antes de rodar; o preflight recusa até então)
      arms.json -> claude_block_sha256 81f1633f…7770c7 (== sha256sum arms-block.md), claude_block_path research/lean-code/arms-block.md, skill_installed False
      git diff --stat f11ba7a HEAD -- research/lean-code/results/ | wc -l   -> 0
      ```

- [x] 4.2 Três arms (`baseline`/`block`/`skill`, `ARM_LAYOUT`), a skill como skill de projeto
      (`project_skill_path` em `arm.json`; `<workspace>/.claude/skills/lean-code` copiado na seed;
      preflight sem `~/.claude/skills`), quarto critério da sonda (`skill_visible`), gate de
      `--matrix --arms skill`, `--report` com deltas de 1-3 stamps, `--relabel-arm`; docstring
      (KNOWN LIMIT 4 reescrito), `protocol.md` (terceira emenda, tabela de arms, *Why `block`
      exists*), README da pesquisa, `design.md` D10; commit `6285b73` (harness)

      O fato medido pelo mantenedor (2026-09-05, Claude Code 2.1.261, `$SCR/lean-dev/probe-skill-project`:
      `<cwd>/.claude/skills/lean-code -> <worktree>/skills/lean-code` + `settings.json` e `CLAUDE.md` do arm):

      ```
      out1.json (claude -p … --tools "" --setting-sources project,local, Haiku)
      -> "result": "lean-code\nDONE"    "total_cost_usd": 0.017872   "num_turns": 1
      out2.json (… --tools "Skill")
      -> "result": "# Lean code — the best code is the code never written\n\nDONE"   "total_cost_usd": 0.0307034   "num_turns": 3
      (as três células da lente com o mesmo --setting-sources e SEM skill de projeto: "lean-code isn't in the available-skills list";
       leituras em ~/.claude/skills/ e ~/ai-skills/ negadas — o arm `skill` da stamp 20260905-230209 mediu só o bloco)
      ```

- [x] 4.3 The probe cwd is a git root, like every cell workspace, because project skills are not
      discovered otherwise — measured before the fix on the harness's own probe dir:

      ```
      cd <arms-3>/_probe/20260906-002213/skill-cwd-skills && claude -p "<SKILLS prompt>" --model claude-haiku-4-5-20251001 --setting-sources project,local --tools ""
      -> SKILLS: none            ($0.006, no .git)
      cp -r . <tmp> && git init && git add -f -A && git commit -m base && claude -p "<same>"
      -> SKILLS: bench-sentinel, lean-code   ($0.016)
      python3 research/lean-code/run.py --selftest
      -> OK  isolation  probe cwd is a git repository root (project skills are discovered only under one)
      -> selftest: 184/184 OK
      ```

      O harness, offline, nesta worktree (2026-09-06):

      ```
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest
      -> selftest: 183/183 OK  (… isolation 42/42, refusals 13/13, relabel 8/8, report 5/5)   wall 2.2s   (era 157/157)
      python3 research/lean-code/run.py --prepare-arms --arms-root $SCR/lean-dev/arms-3 --rules-ref HEAD --skill lean-code --claude-block research/lean-code/arms-block.md
      -> arm baseline     claude-snippet.md = sentinel only                                          preflight OK
      -> arm block        claude-snippet.md = sentinel + always-on block                             preflight OK
      -> arm skill        claude-snippet.md = sentinel + always-on block; workspace gets .claude/skills/lean-code copied from <worktree>/skills/lean-code   preflight OK
      skill/arm.json -> "includes_block": true, "includes_skill": true, "skill_override": "on", "project_skill_path": "<worktree>/skills/lean-code"
      block/arm.json -> "includes_block": true, "includes_skill": false, "skill_override": "off", "project_skill_path": null
      python3 research/lean-code/run.py --prepare-arms --arms-root $SCR/lean-dev/arms-3b --rules-ref HEAD      (sem --claude-block)
      -> note: without --claude-block only the baseline arm is prepared (block and skill carry the always-on block)
      python3 research/lean-code/run.py --relabel-arm $SCR/lean-dev/runs/20260905-230209 skill block --reason "the skill arm measured the always-on block only: …"
      -> relabelled 27 cells and 27 cell dirs skill -> block in …/runs/20260905-230209; reason recorded in results.json relabels
      ls $SCR/lean-dev/runs/20260905-230209 | grep -c __block__   -> 27      grep -c __skill__   -> 0
      python3 research/lean-code/run.py --report $SCR/lean-dev/runs/20260905-211512 $SCR/lean-dev/runs/20260905-230209 --export $SCR/lean-dev/report-baseline-block.json
      -> === delta vs baseline (mean added_lines; the protocol's Δ) ===    9 linhas (uma por tarefa, arm block) + 1 linha de grupo
      -> reuse-slug             block            9       9     +0.0  1.0->1.0     1.0->1.0
      -> export keys: arms cells cells_detail claude_version delta_groups deltas isolation model relabels rules_sha spent_usd stamps summary
      (os valores do arm `block` ficam para results.md, parte B do mantenedor — nenhum número em README ou SKILL.md)
      ```

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi exercitado pelo caminho real (parte offline). **Entry point 1** — a
      description contra as 36 descriptions do catálogo por um roteador léxico de rascunho
      (`<scratch>/route-sim.py`, fora do repositório como no item #122: frases entre aspas casadas
      ×3 + bigramas de conteúdo + unigramas/4 sobre a `description` de cada `skills/*/SKILL.md`;
      6 prompts, 3 que devem cair em lean-code e 3 que não podem). O roteador real é o modelo; o
      que se mede é se o sinal léxico existe e não colide com um irmão. Saída observada
      (`python3 <scratch>/route-sim.py` na raiz da worktree, re-executado em 2026-09-05 depois de
      o script sair de `research/lean-code/` — revisão do PR: arquivo fora da posse declarada):

      ```
      [lean-code] faz o mais simples que funciona pra esse endpoint, sem inventar camada
         lean-code   score=6.25 quoted=1 bigrams=2 unigrams=5   | verify-before-claiming 0.25 | python-rest-api 0.25
      [lean-code] review this diff for over-engineering — what can we delete, is this over-engineered?
         lean-code   score=8.25 quoted=2 bigrams=1 unigrams=5   | verify-before-claiming 0.25 | svg-animation 0.25
      [lean-code] add a cache for these API responses
         (antes) verify-before-claiming 0.25 | react-api-client 0.25 | python-rest-api 0.25   — lean-code empatado em 0.25, fora do top-3
         (depois de "add a cache" na description) lean-code score=4.50 quoted=1 bigrams=1 unigrams=2 | verify-before-claiming 0.25
      [verify-before-claiming] isso é achismo — de onde tirou essa flag? não inventa, pesquisa antes
         verify-before-claiming score=17.25 quoted=4 | lean-code 0.25
      [api-resilience-testing] break this endpoint with adversarial tests: negative testing, fuzz the payloads, check the status codes
         api-resilience-testing score=11.00 quoted=2 | python-rest-api 1.50 | bug-hunter 1.00
      [documentation] prune the README: write the docs so only the pages the project earns stay, document this
         documentation score=8.50 quoted=2 | verify-before-claiming 0.25
      prompts=6  intended-top=6/6  descriptions=36  lean-code stole a non-lean prompt: 0/3
      ```

      **Entry point 2** — o grep do ledger de `simplification-ledger.md`, num arquivo com dois
      marcadores (um sem `->`) e no repositório:

      ```
      printf 'def f(x):\n    return x * 2  # lean: ints only -> accept floats when the CSV carries them\n\nlocal t = {}  -- lean: table grows per session, clear later\n' > $SCR/ledger-sim/sample.py
      grep -rnE '(#|//|--) ?lean: ' --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist $SCR/ledger-sim | awk …
      -> sample.py:2: … # lean: ints only -> accept floats when the CSV carries them
      -> sample.py:4: … -- lean: table grows per session, clear later
      -> 2 markers, 1 with no trigger.
      grep -rnE '(#|//|--) ?lean: ' --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist . | wc -l   -> 28
      (skills/lean-code 9 + suas cópias geradas em plugins/ e cursor/ 12 + research/lean-code 4 [run.py 3 fixtures, arms-block.md 1] + openspec 2 + personal-rules.md 1 = 28; código de produto: 0)
      ```

      **Entry point 3** — o validador de referência e o harness: `agentskills validate
      skills/lean-code -> Valid skill: skills/lean-code`; `run.py --prepare-arms … --claude-block`
      real contra `$SCR/lean-dev/arms-146` (saída em 4.1).

- [x] S.2 Matriz de casos como contagens: roteamento lexical intended-top **6/6** (3 lean + 3
      não-lean; 5/6 antes do gatilho `"add a cache"`), lean-code roubou **0/3** prompts não-lean;
      ledger no arquivo de teste **2 marcadores / 1 `no-trigger`** (1/1 sem `->` tagueado, 1/1 com
      `->` limpo); ledger no repo **28/28** hits em documentação da convenção ou fixture do
      harness, **0** em código de produto; selftest do harness **157/157** (8/8 casos novos do
      `--claude-block`: 5 que tinham de passar passaram, 3 defeitos injetados pegos); preflight real
      **1/1** recusa do arm `skill` sem symlink, **1/1** baseline OK; verbatim **12/12** segmentos;
      `validate-skills.py` **36 skills, 0 findings**; gates.sh **22/22 PASS, dirty-after 0**

- [x] S.3 O que escapou ou se comportou diferente do esperado:

      - **O arm `skill` da stamp `20260905-230209` não tinha a skill.** `skillOverrides.lean-code =
        "on"` com symlink em `~/.claude/skills` era a hipótese de D8; medido pelo mantenedor em
        2026-09-05, `--setting-sources project,local` não carrega o diretório de skills do usuário
        e as 27 células ($9,08) mediram sentinela + bloco. Passou pelo `--selftest` verde, pelo
        preflight e pela sonda — nenhum dos três via skills (o KNOWN LIMIT 4 antigo dizia isso como
        limite, não como risco). Corrigido em 4.2: skill de projeto copiada na seed, `skill_visible`
        como quarto critério da sonda, gate em `--matrix --arms skill`, stamp renomeada para `block`
        com o motivo gravado. O Claude Code também atualizou para `2.1.263` no meio (2026-09-06):
        o arm `skill` roda o binário `2.1.261` pinado ou baseline e block são refeitos.
      - **O prompt do cache não roteava.** "add a cache for these API responses" empatava em 0,25
        com três irmãos (a description dizia "adding a dependency or a cache"; o scorer não casa
        `add` com `adding`) e lean-code ficava fora do top-3 pelo desempate alfabético. Gatilho
        `"add a cache"` acrescentado à description (1000 → 1015 chars); re-medido 6/6.
      - **O grep do ledger não dá zero num repo que documenta a convenção.** A expectativa "0" da
        issue valia para código de produto; o repo carrega 28 hits em exemplos da skill, cópias
        geradas, fixtures do `run.py` e prosa de openspec. `simplification-ledger.md` diz que
        esses saem à mão; a primeira medição de E.2 tinha escrito "0" por um glob não citado que
        impediu o grep de rodar — corrigida para o `git grep` no commit (4 em `f11ba7a`).
      - **O validador leu os caminhos do upstream como caminhos do catálogo.** `skills/ponytail/…`
        em backticks disparou C1 oito vezes e dois caminhos `research/…` dispararam C12. Corrigido
        prefixando o nome do repo (`ponytail/skills/…`) e usando a URL do repositório para
        `research/`.
      - **O `validate-skill-version.py` mede commits, não a árvore de trabalho.** A primeira rodada
        (irmãos editados, não commitados) disse "0 skill(s) changed"; depois dos commits, "5
        skill(s) changed, 0 findings". Comportamento documentado do gate, não defeito.
      - **A linha ❌ do exemplo de revisão** tinha sido re-quebrada em outro ponto; o check de
        verbatim deu 11/12 e a quebra foi devolvida à do upstream (12/12).
      - Nada mais escapou na parte offline: `generate.sh` idempotente, `agentskills` verde,
        selftest verde, gates verdes.
      - **Parte paga (2026-09-06).** Duas sondas de três arms **falharam** antes da que passou —
        `$SCR/lean-dev/arms-3/_probe/20260906-002213/probe.json` (`skill_visible` 0/1 no `skill`,
        esperado 1/1; `SKILLS: none` — o cwd da sonda não era raiz git, corrigido em `18eca8e`) e
        `$SCR/lean-dev/arms-3/_probe/20260906-002551/probe.json` (0/1 de novo — o evento `init` do
        CLI listava `lean-code` e o modelo respondeu `SKILLS: none`; a sonda passou a ler o `init`,
        `229a260`); custaram $0,1908 + $0,1941 e saíram de `results/`. O Claude Code auto-atualizou
        para `2.1.263` entre o `block` e a `skill`: os stamps da skill rodaram o binário `2.1.261`
        por shim no `PATH` (`$SCR/lean-dev/bin-261/claude`), e `--report` aceitou os três.
      - **Duas rodadas da lente sem a skill.** `$SCR/lean-dev/lens/` ($1,2499) e `lens2/` ($1,5184)
        rodaram sem `.claude/skills/lean-code` no cwd (5 dos 6 resultados abrem com "lean-code isn't
        in the available-skills list"); contam como escapes, nunca como dado (S.5).
      - **O check inline conta como código de produto.** `added_lines` lê os arquivos de produto:
        um bloco `if __name__ == "__main__":` de asserts dentro do módulo conta inteiro
        (`reuse-slug` run 1: 19 vs 9; `cache` run 1: 11 vs 3, lógica idêntica). Disparou o REWRITE
        do protocolo em `reuse-slug` (S.4.1); em `cache` ficou como cláusula INCONCLUSIVE aberta.
      - **A cláusula de dispersão do protocolo vale em mais tarefas do que a que foi repetida.**
        Depois de `reuse-slug` (81 % → +2 reps → REWRITE → 12 %), a releitura da tabela mostrou
        `cache` 141 % (3, 11, 3) e `csv-sum` 82 % (26, 11, 18) no arm `skill` e `trace-transfer`
        76 % (10, 25, 24) no `block` — sem as +2 repetições, o veredito é INCONCLUSIVE, não SHIP,
        embora todas as condições de SHIP valham nos números como estão (`results.md`).
      - **A referência ensinava o que a regra reescrita proíbe** (revisão do PR, 2026-09-06). O
        exemplo de causa-raiz em `review-examples.md` guardava o check único num bloco
        `if __name__ == "__main__":` dentro do módulo importado por dois chamadores e dizia que esse
        bloco "nunca é sinalizado" — a forma que o REWRITE `8ed6fd0` do `SKILL.md` reserva a script
        de arquivo único e que o harness contou como código de produto (item acima). O modelo imita
        o código que lhe mostram (Q.5): o check passou para um `test_bank.py` ao lado do módulo e a
        frase diz onde ele mora e por quê. No mesmo passe, `upstream.md` ainda dizia que o arm da
        skill "é escrito lá quando rodar" enquanto `SKILL.md` e README já publicavam −34,4 % /
        31/31 / SHIP — trocado pelo ponteiro medido, recomputado dos stamps `003055` + `004900` +
        `013713` (31 células, `correct`/`safe` 31/31, Δ do grupo −34,4 %, pior tarefa
        `fastapi-create-item` +4,2 %, `output_contract` 27/31, dependência nova 0/31).

- [x] S.4 **(mantenedor, 2026-09-06)** Arms novos + sonda + matriz `--arms skill` n=3 × 9 no mesmo
      `claude --version` do baseline (`2.1.261`, binário pinado primeiro no `PATH`) e mesmo modelo;
      `--report <baseline> <block> <skill>`; veredito pela letra do protocolo em
      `research/lean-code/results.md` **antes** de qualquer número entrar em README ou `SKILL.md`
      (nenhum entrou nesta rodada: o veredito era INCONCLUSIVE; entrou em S.4.2, depois da
      releitura). Comandos e saída observada (stamps em
      `$SCR/lean-dev/runs/<stamp>/`, `results/` do repositório):

      ```
      export PATH=$SCR/lean-dev/bin-261:$PATH && claude --version   -> 2.1.261 (Claude Code)
      python3 research/lean-code/run.py --prepare-arms --arms-root $SCR/lean-dev/arms-3 --rules-ref HEAD --skill lean-code --claude-block research/lean-code/arms-block.md
      python3 research/lean-code/run.py --probe-isolation --arms-root $SCR/lean-dev/arms-3 --model claude-haiku-4-5-20251001
      -> 20260906-002213 FAIL, 20260906-002551 FAIL (S.3), 20260906-002908 PASS: sentinel 3/3 ×3 arms, hook events 0, marker untouched 3/3 ×3,
         skill_visible baseline 0/1, block 0/1, skill 1/1 (init_skills: lean-code, …)   $0,1951   (results/20260906-002908-probe-3arms.json)
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest --matrix --arms skill --tasks all --model 'opus[1m]' --runs 3 --arms-root $SCR/lean-dev/arms-3 --runs-root $SCR/lean-dev/runs --budget-usd 15
      -> stamp 20260906-003055: 27/27 células, subtype success 27/27, is_error 0/27, killed 0/27, correct 27/27, safe 27/27, $9,2791
      python3 research/lean-code/run.py --classify $SCR/lean-dev/runs/20260906-003055   -> results/20260906-003055-skill-defects.md
      -> output_contract 24/27, lean_marker 8/27, new_dependency 0/27, guard_dropped 0/27, patched_caller_only 0/27, reimplemented_existing 0/27, class_for_oneliner 0/27, no_check 3/27 (react)
      python3 research/lean-code/run.py --report $SCR/lean-dev/runs/20260905-211512 $SCR/lean-dev/runs/20260905-230209 $SCR/lean-dev/runs/20260906-003055 --export research/lean-code/results/20260906-003055-export.json
      -> block: over-build group mean delta -28.6% over 4 tasks; worst task fastapi-create-item +6.2%; correct below baseline: none; boundary safe < 1: none
      -> skill: over-build group mean delta -33.9% over 4 tasks; worst task reuse-slug +37.0%; correct below baseline: none; boundary safe < 1: none
      -> Δ skill por tarefa: cache -55.3 / csv-sum -82.0 / fastapi +4.2 / fivem -38.8 / react -4.5 / reuse-slug +37.0 / safe-path -79.8 / sql-user -60.9 / trace-transfer -64.2
      (+2 reps de reuse-slug) … --matrix --arms skill --tasks reuse-slug --runs 2   -> 20260906-004535: 9, 8 linhas, $0,4940; n=5 → 10,8 = +20 % → REWRITE (S.4.1)
      (depois do REWRITE) --prepare-arms … --rules-ref HEAD (8ed6fd0); --probe-isolation   -> 20260906-004737 PASS, skill_visible 1/1 / 0/1 / 0/1, $0,1945
      … --matrix --arms skill --tasks reuse-slug --runs 3   -> 20260906-004900: 9, 9, 8 linhas, test_articles.py 3/3, reused project slugify 3/3, $0,7391
      python3 research/lean-code/run.py --report $SCR/lean-dev/runs/20260905-211512 $SCR/lean-dev/runs/20260905-230209 $SCR/lean-dev/runs/20260906-004900 --export research/lean-code/results/20260906-004900-export.json
      -> reuse-slug             skill            9   8.667     -3.7  1.0->1.0     1.0->1.0
      python3 -c "…"  (script sobre results.json, reuse-slug trocada por 004900)
      -> skill final: group -33.9%, worst fastapi-create-item +4.2%, output_contract 24/27, lean_marker 9/27, root cause 3/3, new_dependency 0/27, correct 27/27, safe 27/27
      -> dispersão > 50 % da média: skill cache 141 %, csv-sum 82 %; block trace-transfer 76 %   => INCONCLUSIVE (results.md, tabela do veredito)
      ```

- [x] S.4.1 **REWRITE** (protocolo, linha *any task above baseline +10%*): `reuse-slug` 12,333 vs 9
      (+37,0 %) na stamp `003055`, 10,8 (+20,0 %) com n=5 — a célula de 19 linhas pôs o check
      único num bloco `__main__` dentro de `articles.py`. Reescrita da regra do check único no
      `SKILL.md` (o check mora num `test_*.py`; `__main__` inline só em script de arquivo único) e
      da linha correspondente de `references/upstream.md`, commit `8ed6fd0`; arms e sonda
      refeitos; re-run só da tarefa afetada, n=3 (`20260906-004900`): 8,667 = −3,7 %, dispersão
      12 %, `test_articles.py` 3/3. Os dois stamps ficam e os dois estão na tabela de `results.md`.
      O protocolo não diz o que segue um REWRITE (escopo do re-run, n, qual stamp conta); a regra
      aplicada é a FR3 da issue #146 ("a reescrita re-roda só as tarefas afetadas e mantém os dois
      stamps") — anotado em *Post-hoc observations*, protocolo não emendado.

- [x] S.4.2 **Releitura** (mantenedor, 2026-09-06 01:35–01:40; protocolo, linha INCONCLUSIVE: *"the
      dispersion (max − min) of a task's `added_lines` exceeds 50% of its mean → +2 repetitions on
      those tasks, then re-read"*): a cláusula estava aberta em `cache` (141 %: 3, 11, 3) e
      `csv-sum` (82 %: 26, 11, 18). Arms refeitos em `af49cfa`, sonda nova, +2 repetições só nas
      duas tarefas, mesmo binário `2.1.261` e mesmo modelo; releitura da tabela inteira sobre os
      31 cells finais. Comandos e saída observada:

      ```
      export PATH=$SCR/lean-dev/bin-261:$PATH && claude --version   -> 2.1.261 (Claude Code)
      python3 research/lean-code/run.py --prepare-arms --arms-root $SCR/lean-dev/arms-146 --rules-ref HEAD (af49cfa) --skill lean-code --claude-block research/lean-code/arms-block.md
      python3 research/lean-code/run.py --probe-isolation --arms-root $SCR/lean-dev/arms-146 --model claude-haiku-4-5-20251001
      -> 20260906-013550 PASS: sentinel 3/3 ×3 arms, hook events 0, marker untouched 3/3 ×3, skill_visible baseline 0/1, block 0/1, skill 1/1 (init_skills: lean-code, …)   $0,1928   (results/20260906-013550-probe-3arms.json)
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest --matrix --arms skill --tasks cache,csv-sum --model 'opus[1m]' --runs 2 --arms-root $SCR/lean-dev/arms-146 --runs-root $SCR/lean-dev/runs --budget-usd 4
      -> stamp 20260906-013713: 4/4 células, subtype success 4/4, killed 0/4, correct 4/4, safe 4/4, $1,1119
      -> cache: 5, 5 linhas (from functools import cache + @cache, check em test_compute.py, nenhum __main__ em compute.py)
      -> csv-sum: 25, 18 linhas (csv.DictReader + float + try/except, ValueError sem coluna amount, test_sales.py 2/2)
      python3 research/lean-code/run.py --report $SCR/lean-dev/runs/20260905-211512 $SCR/lean-dev/runs/20260905-230209 $SCR/lean-dev/runs/20260906-003055 $SCR/lean-dev/runs/20260906-013713 --export research/lean-code/results/20260906-013713-export.json
      -> cache                  skill       12.667     5.4    -57.4  1.0->1.0     1.0->1.0        (n=5: 3, 3, 5, 5, 11)
      -> csv-sum                skill          102    19.6    -80.8  1.0->1.0     1.0->1.0        (n=5: 11, 18, 18, 25, 26)
      -> skill: over-build group mean delta -34.4% over 4 tasks; worst task reuse-slug +37.0% (pré-REWRITE nesse export; com 004900 o pior é fastapi-create-item +4.2%)
      python3 -c "…"  (script sobre results.json: 003055 sem reuse-slug + 004900 + 013713 = 31 cells)
      -> grupo over-build -34.4% (-79.8, -57.4, +4.2, -4.5); pior fastapi-create-item +4.2%; output_contract 27/31; lean_marker 13/31;
         new_dependency 0/31; guard_dropped 0/31; root cause 3/3 + 3/3; correct 31/31; safe 31/31 (boundary 17/17)
      -> dispersão depois do alargamento: cache 148% (8 linhas de spread numa média de 5,4), csv-sum 77% — a linha do protocolo não
         exige que caia abaixo de 50%; registrado em Post-hoc observations (7)
      => releitura: as sete condições de SHIP valem, nenhuma linha REWRITE dispara => SHIP (results.md, tabela do veredito, linha citada)
      ```

      Gasto da releitura: $0,1928 + $1,1119 = $1,3047 (#146 passa a $26,1331; total $36,1888).

- [x] S.5 **(mantenedor, 2026-09-05 23:19–23:22)** Lente nos 3 diffs (`49c44d0`, `69aaf73`,
      `b1f527f`), uma célula `claude -p` cada em `opus[1m]`, `--setting-sources project,local`, a
      skill como skill de projeto (`$SCR/lean-dev/lens3/<sha>/`: raiz git, `.claude/skills/lean-code`,
      `settings.json` do arm, diff restrito ao arquivo que o protocolo nomeia); adjudicação achado a
      achado pelas 5 regras de FP contra `diff.patch` e o corpo do PR (`gh pr view 140|141|142 --json body`)
      em `results.md`, *Review lens*:

      ```
      lens3/49c44d0/out.json  locale-rite.py         7 achados (delete 4, yagni 1, shrink 2)  net: -40 lines possible.  válidos 4, FP 3 (regra 1 ×2, regra 4 ×1)   $0,5210
      lens3/69aaf73/out.json  locale-stop-gate.py    7 achados (shrink 4, yagni 3)            net: -33 lines possible.  válidos 7, FP 0                             $0,5823
      lens3/b1f527f/out.json  pre-commit-locale.sh   7 achados (shrink 3, yagni 3, delete 1)  net: -75 lines possible.  válidos 5, FP 2 (regra 3 ×2)                $0,3615
      total 21 achados, net: 3/3, precisão 16/21 = 0,76 ≥ 0,7 (17/21 = 0,81 lendo a regra 4 só pela tag `yagni:`)
      escapes: lens/ (8/7/8 achados, net -38/-61/-39, $1,2499) e lens2/ (9/7/7, net -47/-65/-49, $1,5184) rodaram sem a skill — inválidas para este critério
      ```

      **FR4 da issue** ("qualquer `delete:` em selftest/mutante é FP e corrige o texto da guarda
      antes de publicar"): dois dos cinco FP são `delete:` em caso de selftest (`49c44d0` achados 5
      e 7). A frase de guarda em `SKILL.md`, *Reviewing a diff*, cobria a existência do check, não
      um caso dentro de um selftest. **Alargada em `6831e24` (2026-09-06, revisão do PR)**, antes
      da publicação: "A single smoke test or `assert`-based self-check — and any single case
      inside a selftest, a mutant or an injected-defect check — is the minimum, not bloat, never
      flag it for deletion: the check is the product." `references/upstream.md` registra a frase
      como reescrita (era verbatim); wrappers regenerados. A lente **não** foi re-rodada no texto
      alargado (nenhuma célula paga depois da medição): a precisão registrada continua 16/21 com
      os achados 5 e 7 contados como FP — `results.md`, *Review lens* e *Post-hoc* item 6.

      ```
      grep -n "injected-defect" skills/lean-code/SKILL.md plugins/workflow/skills/lean-code/SKILL.md cursor/rules/lean-code.mdc
      -> skills/lean-code/SKILL.md:160, plugins/workflow/skills/lean-code/SKILL.md:160, cursor/rules/lean-code.mdc:145
      bash generate.sh && /usr/bin/git status --short -> (vazio depois do commit 6831e24)
      ```

- [x] S.6 **(mantenedor, 2026-09-06)** Exercício pelo caminho real: **nenhuma sessão interativa
      rodou**, e não precisa — o protocolo define a célula headless como o ponto de entrada
      (`protocol.md`, *Cell*: `claude -p "<task prompt>" --model opus[1m] --setting-sources
      project,local --permission-mode acceptEdits …`, cwd = repositório semeado com a skill em
      `.claude/skills/lean-code`), e as 32 células do arm `skill` são exatamente isso: o binário
      real, as regras reais do mantenedor, a skill carregada pelo roteador do CLI (sonda
      `skill_visible` 1/1), nenhum harness entre o prompt e o diff. A armadilha de over-build e o
      bug de dois callers que o critério pedia são as tarefas `safe-path`/`cache`/`csv-sum` e
      `trace-transfer` da matriz. Saída observada de uma célula de cada tipo:

      ```
      runs/20260906-003055/safe-path__skill__0/_diff.patch   -> uploads.py +12 (resolve + `base not in target.parents` + ValueError), test_uploads.py +32
      runs/20260906-003055/safe-path__skill__0/_result.txt   -> "skipped: filename sanitising (no lowercasing, extension allowlist, length cap, collision-safe unique names) — add when uploads are served back to browsers or overwriting an existing file matters; a null-byte filename surfaces as `resolve()`'s own `ValueError` rather than the message above — add an explicit check when the API contract needs one error shape."
      runs/20260906-003055/trace-transfer__skill__1/_diff.patch
      ->  def _debit(acct, cents):
      ->  +    if cents < 0:
      ->  +        raise ValueError("amount must not be negative")
      ->  +    if balances.get(acct, 0) < cents:
      ->  +        raise ValueError(f"insufficient funds in {acct!r}")
      ->  (transfer não recebe guard; test_bank.py cobre transfer E withdraw)
      runs/20260906-003055/trace-transfer__skill__1/_result.txt -> "The root cause was that `_debit` mutated unconditionally; `transfer` was only the path the report named — `withdraw` had the same hole. One guard in `_debit` closes both."
      scorer: reason = "fixed shared _debit (withdraw guarded too)" em 3/3 células skill (e 3/3 baseline, 3/3 block)
      ```

      O que uma sessão interativa mediria a mais — os hooks e o plugin `caveman` do mantenedor —
      é justamente o que o protocolo exclui (KNOWN LIMIT 3 e 4); fica como limite declarado em
      `results.md`, não como critério pendente.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present

      ```
      gates.sh -> PASS frontmatter   (o loop do ci.yml sobre os 36 SKILL.md)
      python3 scripts/validate-skills.py -> skills checked: 36   findings: 0   (C10: 1015 ≤ 1024, 175 ≤ 500)
      (2026-09-06, depois da frase do veredito no SKILL.md) gates.sh -> PASS frontmatter; python3 -c "yaml…" -> 1015 175 {'author': 'solvelab', 'version': '1.0.0', 'category': 'process'} lean-code MIT
      ```

- [x] Q.2 All touched skill content in English (catalog locale)

      ```
      grep -c "" skills/lean-code/SKILL.md skills/lean-code/references/*.md   -> 702 linhas, prosa em inglês; o português só dentro das aspas dos gatilhos da description
      (2026-09-06) grep -c "" … -> 219 / 173 / 125 / 81 / 106 = 704; a frase nova do veredito é inglesa
      ```

- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists

      ```
      python3 <scratch>/route-sim.py -> prompts=6  intended-top=6/6  descriptions=36  lean-code stole a non-lean prompt: 0/3
      validate-skills.py C13 -> silencioso (a description carrega "Do NOT use" e nomeia verify-before-claiming, bug-hunter, documentation, /simplify)
      (2026-09-06) a description não mudou nesta parte (1015 chars, mesma string da simulação 6/6); o roteador real carregou a skill em 32/32 células do arm skill (sonda skill_visible 1/1 antes de cada matriz; trailer `skipped:` em 24/27)
      ```

- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)

      ```
      grep -n "skills/verify-before-claiming/SKILL.md\|skills/fivem-lua/SKILL.md\|skills/backend-resilience/SKILL.md\|skills/bug-hunter/SKILL.md" skills/lean-code/SKILL.md | wc -l   -> 4
      grep -c "Doing / Not doing / Assumptions" skills/lean-code/SKILL.md   -> 1   (a linha de Rules; a regra do bloco é citada, não reescrita)
      grep -n "lean-code" skills/{verify-before-claiming,bug-hunter,code-locale,log-event-collector}/SKILL.md | wc -l   -> 4   (uma linha See also cada)
      (2026-09-06) a tabela Canonical Home do design.md não muda: a frase nova aponta para research/lean-code/results.md, que não é doutrina
      ```

- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown

      ```
      validate-skills.py C9 (check-identifier-locale.py --markdown-fences skills/) -> 0 findings
      (o único nome não inglês nos fences, `nota_fiscal_cache` em simplification-ledger.md, carrega `# locale-ok: SEFAZ fiscal document…` na linha acima — é o exemplo da coexistência)
      (2026-09-06) python3 skills/code-locale/references/check-identifier-locale.py --markdown-fences skills/lean-code -> findings: 0
      ```

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-lean-code-doctrine --strict` green

      ```
      openspec validate add-lean-code-doctrine --strict   -> Change 'add-lean-code-doctrine' is valid
      (2026-09-06, em 4330450) openspec validate add-lean-code-doctrine --strict -> Change 'add-lean-code-doctrine' is valid
      (2026-09-06, no commit da releitura S.4.2) openspec validate add-lean-code-doctrine --strict -> Change 'add-lean-code-doctrine' is valid
      ```

- [x] V.2 Catalog discovery intact: `scripts/validate-skills.py` (36 skills), `validate-repo-hygiene.py`
      com `all 36`, `validate-rite.sh`, `validate-skill-version.py`, `scan-secrets.py`, `agentskills
      validate`, `run.py --selftest` verdes; `generate.sh` sem diff

      ```
      bash $SCR/gates.sh <worktree> "Spec-rite: add-lean-code-doctrine"
      -> PASS generate / tree-clean-after-generate / version / frontmatter / validate-skills (36, 0) / selftest-validate-skills (24/24) /
         locale-detector / locale-rite / backlog-rite-selftest / verify-rite-selftest / scan-secrets / scan-secrets-selftest /
         hygiene (0 findings) / hygiene-selftest (4/4) / rite (rite gate OK) / rite-evidence-selftest (7/7) / spec-rite-selftest (6/6) /
         smoke (17/17) / plugin-validate (✔) / openspec-strict ×3
      -> dirty-after: 0
      GITHUB_EVENT_PATH=$SCR/event146.json python3 scripts/validate-skill-version.py -> 0 findings (5 skill(s) changed)
      python3 scripts/scan-secrets.py -> no credentials found
      $SCR/venv-A/bin/agentskills validate skills/lean-code -> Valid skill
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest -> selftest: 157/157 OK
      (2026-09-06, em b3584ef — o probe-skill.json não rastreado do mantenedor posto de lado durante o gate e restaurado com o mesmo sha256)
      bash $SCR/gates.sh <worktree> "Spec-rite: add-lean-code-doctrine" -> 22 PASS, 0 FAIL, dirty-after: 0
      GITHUB_EVENT_PATH=$SCR/event146.json python3 scripts/validate-skill-version.py -> 0 findings (5 skill(s) changed, 5 with content changes)
      python3 scripts/scan-secrets.py -> no credentials found
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest -> selftest: 183/183 OK  (2.2s)
      (2026-09-06, em 4330450, depois de results.md, SKILL.md e results/)
      bash $SCR/gates.sh <worktree> "Spec-rite: add-lean-code-doctrine" -> 22 PASS, 0 FAIL, dirty-after: 0   ($SCR/gates-run-146-final.txt)
      GITHUB_EVENT_PATH=$SCR/event146.json python3 scripts/validate-skill-version.py -> skill-version gate: 0 findings (base origin/master, 5 skill(s) changed, 5 with content changes)
      python3 scripts/scan-secrets.py -> no credentials found
      $SCR/venv-A/bin/agentskills validate skills/lean-code -> Valid skill: skills/lean-code
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest -> selftest: 186/186 OK  (2.1s; isolation 45/45)
      /usr/bin/git ls-files research/lean-code | xargs grep -l session_id -> (vazio, rc=123); … grep -l /home/diegops research/lean-code/results -> (vazio)
      (2026-09-06, em b6c9ecf, revisão do PR: guarda da lente alargada em 6831e24, README da pesquisa sem número; PATH com o 2.1.261 na frente, `claude --version` -> 2.1.261 (Claude Code))
      bash $SCR/gates.sh <worktree> "Spec-rite: add-lean-code-doctrine" -> 22 PASS, 0 FAIL, dirty-after: 0
      (a primeira passada antes do commit reprovou C12 em `upstream.md` — caminho inline `research/lean-code/results.md` — corrigido para a URL do repositório no mesmo commit)
      GITHUB_EVENT_PATH=$SCR/event146.json python3 scripts/validate-skill-version.py -> skill-version gate: 0 findings (base origin/master, 5 skill(s) changed, 5 with content changes)
      python3 scripts/scan-secrets.py -> no credentials found
      $SCR/venv-A/bin/agentskills validate skills/lean-code -> Valid skill: skills/lean-code
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest -> selftest: 186/186 OK  (2.0s; isolation 45/45)
      /usr/bin/git ls-files research/lean-code | xargs grep -l session_id -> (vazio, rc=123)
      openspec validate add-lean-code-doctrine --strict -> Change 'add-lean-code-doctrine' is valid
      (2026-09-06, no commit da releitura S.4.2: results.md, SKILL.md, README, results/ com o export 013713 e a sonda 013550; PATH com o 2.1.261 na frente)
      bash $SCR/gates.sh <worktree> "Spec-rite: add-lean-code-doctrine" -> 22 PASS, 0 FAIL, dirty-after: 0   ($SCR/gates-run-146-reread.txt)
      (a primeira passada, antes do commit, reprovou C12 em SKILL.md — caminho inline `research/lean-code/` na seção nova — trocado pela URL do repositório no mesmo commit)
      GITHUB_EVENT_PATH=$SCR/event146.json python3 scripts/validate-skill-version.py -> skill-version gate: 0 findings (base origin/master, 5 skill(s) changed, 5 with content changes)
      python3 scripts/scan-secrets.py -> no credentials found
      $SCR/venv-A/bin/agentskills validate skills/lean-code -> Valid skill: skills/lean-code
      LEAN_SCORER_VENV=$SCR/lean-dev/venv python3 research/lean-code/run.py --selftest -> selftest: 186/186 OK  (2.1s; isolation 45/45)
      /usr/bin/git ls-files research/lean-code | xargs grep -l session_id -> (vazio, rc=123); grep -l /home/diegops research/lean-code/results -> (vazio)
      ```

- [x] V.3 README / docs updated where the change alters catalog composition or usage: README (membro
      do plugin, linha da tabela, contagens), `research/lean-code/{README,protocol}.md` (a opção
      `--claude-block` e o passo 6 da sequência), `claude/global/personal-rules.md` (seção *Lean
      Code*); em 2026-09-06, `protocol.md` (terceira emenda, tabela de três arms, *Why `block`
      exists*, sonda, passo 6, veredito, limites), README da pesquisa (passos 2-5, selftest 183,
      status), docstring do `run.py` (KNOWN LIMIT 4), `design.md` D10; `results.md` continua do
      mantenedor — a frase "`skill_listed 0/3` is expected … (KNOWN LIMIT 4)" em *Isolation probe*
      aponta agora para o limite reescrito e é dele para ajustar junto com a linha do arm `block`;
      em 2026-09-06 (`3e79284`, `4330450`): `results.md` reescrito por inteiro (três arms, história
      de `reuse-slug`, veredito pela letra, observações post-hoc, lente, gasto), `results/README.md`
      com um índice por arquivo, README da pesquisa (linhas de `results.md`/`results/` e o *Status*),
      `protocol.md` (quarta emenda, só fatos), `SKILL.md` (a frase que aponta o veredito
      INCONCLUSIVE; nenhum número); `README.md` do catálogo **não** muda — o veredito não permite
      número na linha de lean-code; em 2026-09-06 (commit da releitura S.4.2): `results.md` (tabela
      alargada com min–max, seção da releitura, veredito SHIP com a linha citada, observação 7,
      gasto), `results/README.md` (export 013713 e sonda 013550), README da pesquisa (linha de
      `results.md` e *Status*), `SKILL.md` (seção `## What the catalog measured` com o Δ do grupo e
      as condições, URL do repositório), e agora **sim** a linha de lean-code do `README.md` do
      catálogo (Δ do grupo e condições em poucas palavras) — a linha SHIP do protocolo permite
- [ ] V.4 `openspec archive add-lean-code-doctrine --yes` after all groups above are `[x]`
