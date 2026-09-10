# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `fef050d` (master, base de `backlog/246-i-have-adhd-research`) em 2026-09-10:

      - Clone de `ayghri/i-have-adhd` em `ff690b6` (scratchpad): `skills/i-have-adhd/SKILL.md`
        inteiro; `scripts/run_evals.py` (`_neutral_cwd` :31, `_condition_prompt` :205-216,
        `_parse_response` :219-243, `run_evaluations` :245-340, `_build_parser` :343-371,
        `main` :374-405, guard :407); `scripts/judge.py` (`invoke_judge` :171-201,
        `_judge_group` :204-228, `_build_parser` :231-252, `main` :255-330, guard :333);
        `evals/{README,RESULTS,rubric}.md`, `evals/cases.jsonl` (14 casos),
        `evals/runners.example.json`; `hooks/hooks.json`, `hooks/always-on.sh`; `AGENTS.md`;
        `.claude-plugin/{plugin,marketplace}.json`; `.github/workflows/plugin-load-check.yml`
        e `cursor-skill-sync.yml`; issue #61 do upstream (via `gh issue view`).
      - Plugin caveman instalado (`~/.claude/plugins/cache/caveman/caveman/81536f57b330`):
        `.claude-plugin/plugin.json` (hooks `SessionStart` e `UserPromptSubmit`),
        `src/hooks/caveman-activate.js` (:1-80, :257-345 — injeta o SKILL.md filtrado pelo nível),
        `skills/caveman/SKILL.md`, `LICENSE` (nota de escopo), `package.json` (2.3.1);
        `~/.claude/plugins/installed_plugins.json` (gitCommitSha); `~/.claude/.caveman-active`
        (`full`); `~/.claude/settings.json:85` (`model`), `:224` (`effortLevel`).
      - `research/lean-code/run.py`: `outside_repo` (:292), `claude_version` (:305),
        `now_stamp` (:315), `run_process` (:1143-1160), `probe_command` (:1683-1694),
        `parse_stream` (:1697-1740), `strip_export` (:1391-1409); `research/lean-code/protocol.md`
        (cabeçalho :1-30, `## Arms`); `research/lean-code/README.md`; `research/lean-code/vendor/ponytail/PIN`.
      - `research/tdd/run.py` (`lean()` :100-121, `selftest_contract` :687-716, `main` :915-961),
        `research/tdd/PIN`, `research/tdd/README.md` (linha de status :84-93).
      - `openspec/specs/skills-catalog/spec.md:1208-1310` — o requisito *A published cost claim
        carries re-runnable backing* inteiro, copiado por completo no delta antes da extensão;
        `openspec/specs/skills-authoring/spec.md` (:157-183, :212-241, :816-840, :671, :722).
      - `openspec/changes/archive/2026-09-06-add-tdd-research/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md`; `openspec/schemas/skills-rite/templates/*.md`;
        `openspec/config.yaml`; `scripts/validate-rite.sh` (:1-40).
      - `.github/workflows/ci.yml:225-247`; `.github/backlog.yml`; `generate.sh` (via Explore);
        `skills/code-locale/references/check-identifier-locale.py` (:105, :117, :456-464).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      `claude --version` -> `2.1.267 (Claude Code)`

      `claude --help | grep -E -o -- '--(setting-sources|tools|max-budget-usd|disable-slash-commands|no-session-persistence|output-format|model|append-system-prompt|print)\b' | sort -u`
      -> as nove flags do runner do upstream, uma por linha

      `claude --help | grep -A3 -- '--plugin-dir '` -> `Load a plugin from a directory or .zip
      for this session only; a folder of plugins loads each child (repeatable: ...)`

      `claude --help | grep -A2 -- '--include-hook-events'` -> `Include all hook lifecycle events
      in the output stream (only works with --output-format=stream-json)`

      `python3 --version` -> `Python 3.14.5`; `node --version` -> `v26.0.0`

      No clone do upstream: `python3 scripts/run_evals.py validate` -> `Evaluation cases are
      valid.`; `python3 scripts/run_evals.py plan --trials 3 --include-comparator | wc -l` -> 126;
      `python3 -m unittest discover -s tests` -> `OK`

      `openspec new change add-i-have-adhd-research --schema skills-rite` -> `Created change
      'add-i-have-adhd-research' at openspec/changes/add-i-have-adhd-research/` / `Schema: skills-rite`

      `openspec validate add-i-have-adhd-research --strict` -> `Change 'add-i-have-adhd-research' is valid`

      `gh repo view ayghri/i-have-adhd --json stargazerCount,licenseInfo,pushedAt` ->
      `34612`, `MIT License`, `2026-09-10T00:47:20Z`

      `python3 research/i-have-adhd/run.py --selftest` -> `vendor 2/2  upstream 2/2  contract 14/14
      counters 5/5  verdict 18/18  stripper 3/3  preflight 10/10  selftest 54/54`

      `run.py --probe` (Haiku) -> `probe prompt: PASSED  $0.1278` / `probe plugin: PASSED
      $0.1429`; no stream do `plugin/candidate`: `system hook_response SessionStart:startup ...
      out: ADHD MODE ACTIVE (always-on). The ruleset below applies to every response.`; no do
      `plugin/comparator`: `CAVEMAN MODE ACTIVE — level: full` e `UserPromptSubmit ...
      additionalContext: CAVEMAN MODE ACTIVE (full) — session ruleset applies.`; `system/init`
      `plugins: [{'name': 'i-have-adhd', ... 'version': '0.3.0'}]` e `[{'name': 'caveman', ...}]`;
      no baseline `plugins: []`.

      Cinco primeiras células no modelo diário (`fable-01-prompt`): `cost_usd` 0.0895–0.1479,
      `cache_read_input_tokens` 0, `cache_creation_input_tokens` 4417–6834 (a base da emenda de
      orçamento do `protocol.md`).
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      (a) ~~**Se `--plugin-dir` dispara `SessionStart` numa sessão `--print` com
      `--setting-sources ""` e `CLAUDE_CONFIG_DIR` de rascunho.**~~ **FECHADA em 2026-09-10 pela
      sonda**: dispara, 3/3 nas duas condições tratadas, e o `hook_response` carrega o texto
      injetado (E.2). O `UserPromptSubmit` do caveman também dispara — fato que o protocolo e o
      docstring do `run.py` diziam ao contrário; corrigido por emenda datada, sem tocar limiar.

      (b) ~~**Se a cópia de `.credentials.json` no `CLAUDE_CONFIG_DIR` de rascunho autentica.**~~
      **FECHADA pela sonda e pelo piloto**: 18 + 12 chamadas autenticadas, `total_cost_usd` presente.

      (d) ~~**Se sete cópias de `.credentials.json` sobrevivem a uma sessão longa.**~~ **FECHADA
      em 2026-09-10, com correção.** Não sobrevivem: às 02:28 a sessão interativa do mantenedor
      renovou o token OAuth (o refresh token rotaciona) e às 09:23 toda célula nos diretórios
      de rascunho falhou com `Failed to authenticate: OAuth session expired and could not be
      refreshed`, enquanto o mesmo comando no `~/.claude` real respondia `DONE`. Correção:
      `link_credentials` (symlink para o arquivo vivo) e `--refresh-credentials`; preflight do
      selftest ajustado.

      (e) ~~**Se a conta suporta 252 células + 84 juízes numa janela.**~~ **FECHADA pela
      matriz.** Não suporta: às 01:01 as duas matrizes passaram a receber `You've hit your
      session limit · resets 4:20am (America/Sao_Paulo)` (`terminal_reason: api_error`,
      `total_cost_usd: 0`) — 19 células do `prompt` e 60 do `plugin` marcadas FAIL e retomadas
      às 09:30 pela chave de resumo. A conta é assinatura (`subscriptionType: max`); o
      `total_cost_usd` que o CLI reporta é custo estimado, e o teto do item é lido sobre ele.

      (c) **O preço do modelo diário não era conhecido.** Não foi substituído por estimativa: o
      protocolo dizia que o teto decide. Medido nas cinco primeiras células ($0.129/célula, cache
      recriado por processo) e resolvido pelo mantenedor subindo o teto para $55 (emenda no
      `protocol.md`, seção *Cell*).
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Desvios aprovados pelo mantenedor durante a execução, todos registrados como emendas datadas
      no `protocol.md` (fatos e orçamento, nenhum limiar): teto $40 → 55 → 70 → 78 e parada em
      $66.64; timeout de célula 300 → 900 s; cap por chamada $4; credenciais por symlink;
      `--budget-usd` por invocação. Follow-ups anotados e **não** feitos:

      - Julgar o modo `plugin` (42 grupos, ≈ $8) se o mantenedor quiser o veredito combinado.
      - Medir com ferramentas ligadas (caso agêntico) — o artefato de tool-call em texto domina
        os blockers e não é propriedade de nenhuma das skills.
      - Juiz de outra família como controle.
      - Gate de CI "plugin carrega de verdade" (fora deste item desde o grooming).
      - Contabilizar o custo de tentativas mortas por timeout (hoje um piso, não o total).

      Nada em `skills/`, `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`, `generate.sh`,
      `README.md` da raiz ou `.github/workflows/` foi tocado.

## 2. Vendor e proveniência

- [x] 2.1 `research/i-have-adhd/vendor/i-have-adhd/` com `scripts/run_evals.py`, `scripts/judge.py`,
      `evals/cases.jsonl`, `evals/rubric.md`, os testes que passam aqui, `.claude-plugin/plugin.json`,
      `hooks/`, `skills/i-have-adhd/SKILL.md`, `LICENSE`, sem modificação; `PIN` com commit, data e
      sha256 por arquivo
- [x] 2.2 `research/i-have-adhd/vendor/caveman/` com `skills/caveman/SKILL.md`, `LICENSE` (parte MIT)
      e `PIN` com versão, commit instalado e sha256 do que o hook carrega
- [x] 2.3 `research/i-have-adhd/PIN` com o blob de `research/lean-code/run.py` lido e a lista de
      símbolos importados

## 3. Protocolo congelado

- [x] 3.1 `research/i-have-adhd/protocol.md` com o cabeçalho de congelamento: sha base, data, e a
      frase de que os vereditos foram escritos antes de qualquer célula paga
- [x] 3.2 Seções `## Conditions` e `## Injection modes`: o que cada célula vê em cada modo, o
      comando literal do runner, e como o hook entra
- [x] 3.3 Seção `## Metrics per response`: as cinco do juiz, `blocker`, `output_tokens`,
      `forbidden_phrase_hits` com a lista literal de frases
- [x] 3.4 Seção `## Verdict (written before the number)`: ADOPT / NO-CLAIM / REJECT com limiares
      numéricos e a regra do `partial-success`
- [x] 3.5 Seção do que a medição **não** cobre: chat sem ferramentas, juiz da mesma família, três
      trials, caveman medido pelo que o hook injeta

## 4. Harness

- [x] 4.1 `research/i-have-adhd/run.py` carrega `run_evals` e `judge` do vendor e a camada de
      processo e sonda de `research/lean-code/run.py` por `importlib`; nada copiado
- [x] 4.2 `--prepare-conditions`: um `CLAUDE_CONFIG_DIR` de rascunho por condição fora do
      repositório, o flag `.i-have-adhd-always` no candidato, `conditions.json` com os caminhos e
      hashes; recusa uma raiz dentro do repositório
- [x] 4.3 `--probe`: uma chamada por condição e modo com `stream-json --include-hook-events`;
      passa só com hook 3/3 nas condições tratadas e 0/3 no baseline (modo `plugin`) e 0/3 em
      todas (modo `prompt`); grava `probe.json`
- [x] 4.4 `--matrix`: laço próprio de células (D2), resumível pela chave do upstream, comando de
      cada célula gravado antes de rodar, teto `--budget-usd`; recusa sem `--selftest` verde na
      mesma invocação e sem sonda passada para o modo pedido
- [x] 4.5 `--judge`: chama o `judge.py` do upstream com o runner do juiz e as três condições, um
      arquivo por modo
- [x] 4.6 `--report --export`: tabelas por dimensão e por caso, blockers, `output_tokens`,
      `forbidden_phrase_hits`, gasto; recusa agregar stamps com `claude --version`, modelo ou sha
      da rubrica diferentes; export sem `session_id`, texto de resposta ou caminho de HOME
- [x] 4.7 `--selftest` (offline): hashes do vendor contra os `PIN`, testes do upstream, contrato
      dos símbolos importados, contador de frases com defeito injetado, tabela de veredito sobre
      notas sintéticas, stripper de export, preflight das condições

## 5. Medição

- [x] 5.1 Piloto Haiku n=1 em dois casos, ambos os modos (nunca reportado)

      Stamps `20260909-222611-prompt` e `20260909-222653-plugin`: 6 células cada, 0 falhas,
      $0.1204 + $0.1049; juiz Haiku $0.0606 + $0.0523, 4/4 grupos julgados; `--report --export`
      produziu as tabelas e o export sem `session_id` nem texto de resposta. Números não
      reportados, por protocolo.
- [x] 5.2 Sonda nos dois modos; a lacuna do `--plugin-dir` em `-p` fechada com o que o stream mostrou

      Sonda `20260909-222459` (Haiku, $0.2707): modo `prompt` hook events 0/0/0 nas três
      condições; modo `plugin` `SessionStart` 3/3 em `candidate` (`hook_response` com
      `ADHD MODE ACTIVE (always-on)…`) e 3/3 em `comparator` (`CAVEMAN MODE ACTIVE — level: full…`
      mais o `UserPromptSubmit` do tracker), 0/3 em `baseline`; `.caveman-active` só no
      comparador. `results/20260909-222459-probe.json`.
- [ ] 5.3 Matriz no modelo diário, 14 casos × 3 condições × 3 trials, modos `prompt` e `plugin`,
      dentro do `--budget-usd`

      **Parcial.** `prompt`: 126/126 linhas, $28.62. `plugin`: 101/126 (34/34/33 por condição),
      $29.36, parada pelo mantenedor quando o gasto passou do que a pergunta valia. Quatro
      células em loop de tool-call ($3.34 antes do cap por chamada, depois $4.25, $4.34, $4.44 —
      uma com 64.000 tokens de saída) contadas como falha. Não ticada: o modo `plugin` não fechou.
- [ ] 5.4 Juiz cego nos dois arquivos de respostas

      **Parcial.** `prompt`: 42/42 grupos, 126 linhas de nota, $8.06. `plugin`: 0 grupos — o
      mantenedor parou o gasto antes do juiz. Não ticada.
- [x] 5.5 `results.md` com as tabelas, o veredito citado verbatim do protocolo e conferido condição
      por condição, a seção de gasto e a do que não cobre; `README.md` com a linha de status

      Veredito **NO-CLAIM** pela tabela: `prompt` Δ +0.018 < +0.2 e 4 blockers do candidato fora
      de `agent-owned-edit`; `plugin` não julgado. `results/fable-01-export.json` sem `session_id`,
      sem texto de resposta, sem caminho de HOME (checado por grep no export).

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      O artefato executável é `research/i-have-adhd/run.py`; o caminho real é a matriz paga no
      modelo diário com o plugin carregado por `--plugin-dir`.

      `python3 research/i-have-adhd/run.py --selftest --matrix --mode plugin --model claude-fable-5-1
      --trials 3 --stamp fable-01 --conditions-root <scratch>/conds --runs-root <scratch>/runs --budget-usd 22`
      -> `selftest 54/54` -> `matrix fable-01 mode=plugin model=claude-fable-5-1: 14 cases x 3
      conditions x 3 trials, 0 done, budget $22.00` -> `candidate  trial 1: agent-owned-edit
      out_tokens=9746 hits=0 $0.6266 attempts=3 killed=2`

      `run.py --judge <scratch>/runs/fable-01-prompt --conditions-root <scratch>/conds` ->
      `judged direct-answer/trial 1` … `Reported judge cost: $1.4626` -> `judge fable-01-prompt:
      rc=0 judge_cost=$8.0591`

      `run.py --report <prompt> <plugin> --export research/i-have-adhd/results/fable-01-export.json`
      -> `## verdict, by the letter of protocol.md: **NO-CLAIM**` -> `wrote research/i-have-adhd/results/fable-01-export.json`
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      **Tinham de disparar e dispararam**: selftest 56/56 (7 grupos, defeito injetado por
      instrumento); sonda `plugin` `SessionStart` 6/6 nas condições tratadas com o texto das regras
      no `hook_response`, flag `.caveman-active` 1/1 no comparador; juiz 42/42 grupos do `prompt`
      pareados e cegos; cap por chamada disparou 3/3 nas células em loop depois de existir;
      resumo por chave retomou 100% das células perdidas por limite de sessão (2 vezes).
      **Tinham de ficar quietos e ficaram**: hook 0/9 no modo `prompt` e 0/3 no baseline do
      `plugin`; `.caveman-active` 0/5 fora do comparador; export sem `session_id`/texto/HOME 1/1;
      `--matrix` sem selftest ou sem sonda recusou 2/2 (probado à mão).
      **Escapes conhecidos que ficaram quietos**: tentativas mortas por timeout antes do fix não
      deixaram custo registrado (piso declarado); o cap por chamada não existia na primeira célula
      em loop ($3.34 contados só depois).
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      Cinco coisas se comportaram diferente do esperado, todas registradas em `results.md` e nas
      emendas do `protocol.md`: (1) o custo por célula no Fable ($0.13–0.17, cache recriado por
      processo) e o do juiz ($0.19/grupo) — a projeção subiu de $40 para $78 e o mantenedor parou
      em $66.64; (2) células em loop de tool-call escrito como texto, até 64.000 tokens de saída,
      quatro vezes; (3) o `UserPromptSubmit` do caveman dispara em `--print`; (4) cópias de
      credenciais ficam inválidas quando o token rotaciona; (5) o limite de sessão da assinatura
      parou as matrizes duas vezes. O modo `plugin` ficou sem juiz por decisão do mantenedor.

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [x] Q.2 All touched skill content in English (catalog locale)
- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`).
      Provenance: maintainer field report 2026-08-14 (issue #76) — Portuguese identifiers and route
      paths shipped in target repos through this rite. Regression gate on the exemplar: the model
      imitates the code it is shown

      Q.1–Q.5: nenhum `SKILL.md` do catálogo foi tocado (`git diff --stat master -- skills/` vazio);
      os `SKILL.md` sob `vendor/` são cópias byte a byte de terceiros, com PIN, fora do que
      `generate.sh` publica, e não seguem o frontmatter do catálogo por definição. Q.4: a tabela
      Canonical Home do `design.md` liga cada regra à sua casa e este diretório não restata
      nenhuma. Q.5: identificadores do `run.py` em inglês (`check-identifier-locale.py` ->
      `findings: 0`).

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate <id> --strict` green — `Change 'add-i-have-adhd-research' is valid`
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers — nada em `skills/`; `scripts/validate-skills.py` e
      `validate-repo-hygiene.py` verdes na branch
- [x] V.3 README / docs updated where the change alters catalog composition or usage — a composição do catálogo não muda; `research/i-have-adhd/README.md` carrega a linha de status
- [x] V.4 `openspec archive <id> --yes` after all groups above are `[x]` — arquivada por ordem do
      mantenedor em 2026-09-10 com 5.3 e 5.4 parciais (gasto parado em $66.64; lacunas escritas
      nelas e no PR #247), antes do merge do PR, por decisão dele
