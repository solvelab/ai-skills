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
      - `scripts/validate-skills.py` — C3 (127-168), C8 (319-333, `META_HEADING`), C10 (335-391),
        C11 (393-452), C12 (454-526), C13 (528-578, `ANTI_TRIGGER_PHRASES`, `REDIRECT_WORDS`).
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

      Ausência de doutrina e de marcadores, medidas em `f11ba7a`:

      ```
      grep -rniE "yagni|less code|smallest change|speculative|over-engineer|dead code|tech debt" skills/ claude/global/personal-rules.md | wc -l
      -> 0
      grep -rnE '(#|//|--) ?lean: ' --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist . | wc -l
      -> 0
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
      ```

- [x] E.3 O que não pôde ser probado nesta parte

      Três itens, todos pagos ou interativos, todos do mantenedor (parte B):

      - **O efeito da skill.** Nenhuma célula `claude -p` rodou nesta worktree (regra do item:
        nenhuma célula paga por subagente). O arm `skill` não tem número; `SKILL.md` e README não
        carregam nenhum; `## What the baseline measured` cita só o baseline e nomeia
        `research/lean-code/results.md` como o lugar do número.
      - **Se a description roteia numa sessão real.** A simulação lexical de S.1 mede se o sinal
        léxico existe (6 prompts contra as 36 descriptions); o roteador real é o modelo. A sessão
        interativa com a skill instalada (prompt com armadilha de over-build + bug de dois callers)
        é critério de aceite da issue e fica com o mantenedor.
      - **Se `skillOverrides.lean-code = "on"` carrega a skill na célula.** Repousa nos valores
        lidos do binário 2.1.261 pelo item #145 (KNOWN LIMIT 4 do harness); a sonda com `--tools ""`
        não vê skills. O preflight novo só garante que o symlink existe e que o bloco está no
        `CLAUDE.md` da célula.

      O `--claude-block` foi provado pelo `--selftest` (arm sintético, casos presente/ausente) e pelo
      `--prepare-arms` real contra um `--arms-root` de rascunho — nunca por uma célula.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #146 pediu, menos a parte paga, entregue como comandos exatos.
      Notados pelo caminho e **não** feitos, ficam como follow-up:

      - Estreitar a description se a simulação real mostrar que ela rouba prompts de irmãos ou
        nunca dispara — decisão da issue: medir em S.2 antes de estreitar.
      - Kit de adoção do ledger por repositório (pre-commit/CI para `lean:` sem `->`) — excluído
        pela própria issue.
      - `_diff.patch` das células lista `__pycache__/*.pyc` (observado no baseline-defects.md):
        cosmético, fora desta issue.
      - O `## Rules` verbatim mantém "Fewest files possible"; o catálogo tem skills que exigem
        arquivos por camada (`python-rest-api`). Não harmonizado: a regra é "shortest working diff
        **once you understand the problem**" e o texto de deferência já manda o layout do stack
        vencer; um choque real seria um item novo.
      - `research/lean-code/results.md` não muda nesta parte: só a matriz do mantenedor escreve
        nele.

## 2. Skill `lean-code`

- [ ] 2.1 `skills/lean-code/SKILL.md` v1.0.0: frontmatter uniforme, description ≤ 1024 parseada
      com gatilhos EN+PT e cláusula de não-uso nomeando `verify-before-claiming`, `bug-hunter`,
      `documentation` e o `/simplify` nativo; compatibility ≤ 500; seções na ordem do design (D7);
      escada, causa raiz, regras e carve-outs verbatim (D3); nenhuma seção *How to use* / *When to
      use* (C8); todo bloco de código parseia (C3)
- [ ] 2.2 `references/platform-native.md` aparado (sem Swift, debounce com `lean:`, nota de lookup),
      `references/simplification-ledger.md`, `references/review-examples.md`,
      `references/upstream.md` (aviso MIT integral, mapa, proveniência por regra, números do upstream
      com condições); todas linkadas do `SKILL.md` (C11); caminhos cruzados na forma
      `skills/<skill>/references/<file>` (C12)

## 3. Irmãos, gerador, README, regras pessoais

- [ ] 3.1 Uma linha *See also* + bump patch em `verify-before-claiming` (1.1.1), `bug-hunter`
      (2.2.5), `code-locale` (1.4.2), `log-event-collector` (1.1.2)
- [ ] 3.2 `generate.sh` `GROUP_THEME[workflow]` + "and the lean-code doctrine"; `README.md`: membro
      em `ai-skills-workflow`, linha em *Process & git*, `all 35` → `all 36`, "the 36 that `git
      archive HEAD` ships"; `bash generate.sh` duas vezes, a segunda sem diff
- [ ] 3.3 `claude/global/personal-rules.md`: `## Lean Code (the best code is the code never written)`
      depois de *Code Locale*, oito linhas, fecho com o link para a skill; o mesmo bloco sem heading
      em `research/lean-code/arms-block.md`

## 4. Harness: o arm da skill

- [ ] 4.1 `run.py --prepare-arms --claude-block <file>`: arm `skill` = sentinela + bloco no
      `claude-snippet.md`, `baseline` = só a sentinela; `claude_block_sha256` em `arm.json`;
      preflight exige presente no `skill` e ausente no `baseline`; casos novos no `--selftest`;
      `protocol.md` e `research/lean-code/README.md` registram a opção; nenhum arquivo de
      `results/` muda

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 O artefato foi exercitado pelo caminho real (parte offline): a description contra os 6
      prompts pela simulação lexical (`research/lean-code/route-sim.py`); o grep do ledger no repo
      e num arquivo com dois marcadores; `agentskills validate skills/lean-code`
- [ ] S.2 Matriz de casos como contagens: intended-top n/6 na simulação lexical (3 lean + 3
      não-lean); ledger 0 no repo, 2 marcadores / 1 `no-trigger` no arquivo; selftest do harness
      N/N com os casos novos
- [ ] S.3 O que escapou ou se comportou diferente do esperado, nomeado
- [ ] S.4 **(mantenedor)** Matriz `--arms skill` n=3 × 9 tarefas no mesmo `claude --version` e
      modelo do baseline; `--report <baseline> <skill>`; veredito pelo protocolo registrado em
      `research/lean-code/results.md` **antes** de qualquer número entrar em README ou `SKILL.md`
- [ ] S.5 **(mantenedor)** Lente nos 3 diffs (`49c44d0`, `69aaf73`, `b1f527f`): achados por tag,
      `net:` 3/3, precisão ≥ 0,7 com as 5 regras de FP do protocolo
- [ ] S.6 **(mantenedor)** Sessão interativa real com a skill instalada: um prompt com armadilha de
      over-build e um bug de dois callers; saída observada registrada

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [ ] Q.2 All touched skill content in English (catalog locale)
- [ ] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [ ] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [ ] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-lean-code-doctrine --strict` green
- [ ] V.2 Catalog discovery intact: `scripts/validate-skills.py` (36 skills), `validate-repo-hygiene.py`
      com `all 36`, `validate-rite.sh`, `validate-skill-version.py`, `scan-secrets.py`, `agentskills
      validate`, `run.py --selftest` verdes; `generate.sh` sem diff
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive add-lean-code-doctrine --yes` after all groups above are `[x]`
