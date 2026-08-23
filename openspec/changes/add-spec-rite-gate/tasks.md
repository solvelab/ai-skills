## 1. Evidence & Sources (MANDATORY)

<!-- Sempre o PRIMEIRO grupo: prove antes de escrever. Registre o COMANDO e um fragmento da SAÍDA
     CRUA, nunca uma conclusão. Doutrina: skill verify-before-claiming. -->

- [x] E.1 Todo caminho local que este change usa foi ABERTO e lido em `c275a38` em 2026-08-23, não
      recordado: `scripts/validate-rite.sh` (o loop `for dir in "$CHANGES_DIR"/*/` e o
      `[ "$name" = "archive" ] && continue` das linhas 20-23), `scripts/validate-rite-evidence.py`
      (`active_task_files` e as regras de shape `_shape_ok`), `.github/workflows/ci.yml` (o passo
      *Checkout* sem `with:` e o passo *OpenSpec rite gate*), `skills/backlog/SKILL.md`,
      `skills/backlog/references/issue-template.md`, `skills/backlog/references/backlog-config.md`,
      `skills/execute-backlog/SKILL.md`, `skills/execute-backlog/references/execution-flow.md`,
      `skills/execute-backlog/references/acceptance-tracking.md`,
      `skills/execute-backlog/references/board-sync.md`,
      `skills/execute-backlog/references/validation-matrix.md`,
      `claude/global/hooks/backlog-rite.py`, `claude/global/personal-rules.md`,
      `skills/openspec/SKILL.md`, `openspec/config.yaml`,
      `openspec/schemas/skills-rite/schema.yaml`, `openspec/schemas/skills-rite/templates/tasks.md`,
      `openspec/specs/skills-catalog/spec.md`, `generate.sh` e
      `openspec/changes/archive/2026-08-15-record-shipped-gates/proposal.md`
- [x] E.2 Ferramentas e comportamentos probados nesta máquina em 2026-08-23:
      `openspec --version` -> `1.6.0`;
      `openspec schema which skills-rite` -> `Source: project` / `Path: /home/diegops/ai-skills/openspec/schemas/skills-rite`;
      `openspec templates` -> `Schema: spec-driven` (o default do CLI **não** herda o
      `schema: skills-rite` do `openspec/config.yaml`; só `openspec templates --schema skills-rite`
      resolve o fork — por isso o change foi criado com `openspec new change ... --schema skills-rite`);
      `ls openspec/changes/` -> `archive` (única entrada, o que torna o loop do gate vazio);
      `grep -rn -i "openspec" skills/backlog | wc -l` -> `0`;
      `gh auth status` -> `Token scopes: 'admin:org', ..., 'project', 'repo', 'workflow', ...`;
      docs oficiais de hooks (code.claude.com/docs/en/hooks, lidas em 2026-08-23) -> `cwd` é campo
      comum de entrada de **todo** hook event, ao lado de `session_id`, `transcript_path`,
      `permission_mode` e `hook_event_name`;
      `echo '{"prompt":"corrige o bug X","cwd":"/tmp"}' | python3 claude/global/hooks/backlog-rite.py`
      -> saída termina em `...ask before coding.` (sem a frase de spec), e o mesmo prompt com
      `"cwd":"$PWD"` -> `... This repo runs a spec-driven rite (openspec/): ...`;
      `python3 scripts/validate-spec-rite.py --selftest` ->
      `3/3 defect classes detected, 6/6 false-positive cases stayed silent`
- [x] E.3 A única lacuna aberta na proposta — se o payload de `UserPromptSubmit` carrega `cwd` —
      foi fechada pelas docs oficiais em 2026-08-23: `cwd` é campo comum de todo hook event. O
      fallback `os.getcwd()` ficou no código como defesa, não como suposição. Nenhuma outra lacuna
      em aberto: o que o `--selftest` do gate novo não cobre (o encanamento de git que alimenta a
      função de decisão) está declarado no `KNOWN LIMIT` do próprio script, não escondido.
- [x] E.4 Follow-ups listados, não executados aqui: (a) `openspec templates` sem `--schema` ignorar o
      `openspec/config.yaml` é um comportamento do CLI 1.6.0 que merece item próprio (documentar ou
      reportar upstream); (b) os desvios equivalentes nos repositórios DriveZone ganham item em cada
      um, com rito próprio; (c) o archive deste change é PR separado, conforme o precedente `#78`/`#74`

## 2. Camada 4 — o gate de CI deixa de aprovar por vacuidade

- [x] 2.1 `scripts/validate-rite.sh`: nova checagem antes do loop atual — diff que toca caminho fora
      de `openspec/` exige change ativa, diretório novo sob `openspec/changes/archive/` no próprio
      diff, ou a linha `Spec-rite: none — <motivo>` em `PR_BODY`
- [x] 2.2 Allowlist dos caminhos escritos só pela automação de release (`VERSION`, `CHANGELOG.md`,
      `.claude-plugin/*.json`) e restrição a evento `pull_request`
- [x] 2.3 `PR_BODY` tratado como entrada não confiável: regex ancorada, sem execução, sem
      interpolação em comando
- [x] 2.4 `scripts/validate-rite.sh --selftest` injetando um defeito por regra nova, no padrão dos
      gates irmãos deste repositório
- [x] 2.5 Cabeçalho `KNOWN LIMIT` estendido: existência de change não é honestidade de change
- [x] 2.6 `.github/workflows/ci.yml`: `fetch-depth: 0` no checkout, `PR_BODY` no ambiente do passo do
      gate, e passo de self-test do gate

## 3. Camada 3 — `execute-backlog` põe o gate de spec na espinha numerada

- [x] 3.1 Novo safety rail *Spec-before-code* em `skills/execute-backlog/SKILL.md`
- [x] 3.2 Novo passo numerado de spec-rite entre *Context re-analysis* e *Implementation plan*, e o
      plano passando a carregar change-id, capabilities e a saída do `--strict`
- [x] 3.3 Novo `skills/execute-backlog/references/spec-rite.md`: detecção, descoberta do schema,
      tabela de veredito, protocolo de upgrade/downgrade, timing do archive
- [x] 3.4 `references/execution-flow.md` deixa de tratar OpenSpec como exemplo e aponta para o novo
      reference; passo de PR passa a carregar a linha `Spec-rite:`
- [x] 3.5 `metadata.version` de `execute-backlog` bumpada e a descrição refletindo o gate novo

## 4. Camada 2 — `backlog` passa a produzir o veredito por escrito

- [x] 4.1 Novo ground rule de spec-rite em `skills/backlog/SKILL.md`, linkando `openspec` sem
      restatar o ciclo
- [x] 4.2 Novo passo de triagem no workflow, antes do Draft, e o veredito entrando no preview
- [x] 4.3 Seção de spec-rite em `references/issue-template.md`, obrigatória quando há `openspec/`
- [x] 4.4 Chave `spec_rite` (`tool`, `policy`) documentada em `references/backlog-config.md`, com o
      default fail-closed
- [x] 4.5 `metadata.version` de `backlog` bumpada e a descrição refletindo a triagem nova

## 5. Camada 1 — o hook nomeia o rito de spec onde ele existe

- [x] 5.1 Probar o payload real de `UserPromptSubmit` e registrar o resultado em `E.3`
- [x] 5.2 Frase condicional na `REMINDER`, emitida só quando há `openspec/` no diretório do payload
- [x] 5.3 Docstring do hook atualizada para descrever a condicional

## 6. Doutrina, docs e árvore gerada

- [ ] 6.1 `claude/global/personal-rules.md` descrevendo a mesma política que o gate enforça
- [ ] 6.2 `README.md`: seção do hook e quickstart de backlog refletindo o gate de spec
- [ ] 6.3 `./generate.sh` re-rodado e o resultado commitado (`claude/`, `codex/`, `cursor/`,
      `copilot/`, `plugins/workflow/`)

## 7. Quality Gates (MANDATORY)

<!-- Revisão adversarial dos skills tocados — não happy-path. -->

- [ ] Q.1 Frontmatter uniforme em cada `SKILL.md` tocado: `name` == diretório, description folded,
      `metadata.author solvelab`, `metadata.version` semver, category no conjunto controlado,
      `license MIT`, `compatibility` presente
- [ ] Q.2 Todo conteúdo de skill tocado em inglês (locale do catálogo)
- [ ] Q.3 Triggers de description testáveis: as frases que roteiam para `backlog` e
      `execute-backlog` não colidem entre si nem com `openspec` / `openspec-drivezone`; fronteira
      "Do NOT use for" presente
- [ ] Q.4 Zero doutrina duplicada: o ciclo OpenSpec continua morando em `skills/openspec/` e as duas
      skills de backlog linkam, conforme a tabela Canonical Home do `design.md`
- [ ] Q.5 Todo exemplo de código nos skills tocados usa identificadores, rotas, chaves e nomes de
      evento em inglês; termo mantido em outra língua carrega o motivo inline (`code-locale`)

## 8. Validation & Closure (MANDATORY)

<!-- Sempre o último grupo. "Pronto" é verificável, não é opinião. -->

- [ ] V.1 `openspec validate add-spec-rite-gate --strict` verde
- [ ] V.2 `bash scripts/validate-rite.sh` verde neste branch (que carrega change ativa) e
      `bash scripts/validate-rite.sh --selftest` verde
- [ ] V.3 `bash generate.sh && git diff --exit-code` limpo; `python3 scripts/validate-skills.py`,
      `python3 scripts/selftest-validate-skills.py` e `python3 scripts/validate-repo-hygiene.py`
      verdes
- [ ] V.4 README / docs atualizados onde o change altera o fluxo de contribuição
- [ ] V.5 `openspec archive add-spec-rite-gate --yes` — **após o merge**, em PR separado, conforme o
      precedente `#78`/`#74`
