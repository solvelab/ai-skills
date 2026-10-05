## 1. Evidence & Sources (MANDATORY)

<!-- Always the FIRST group: probe before you write. Record the COMMAND and a fragment of its
     RAW OUTPUT, never a conclusion — a row a reviewer can re-run in two seconds is the only kind
     worth writing. A claim with no evidence is a guess: drop the claim, or go get the evidence.
     Doctrine: the verify-before-claiming skill.

     Shape each box owes, gated by scripts/validate-rite-evidence.py once ticked:
       E.1  a repo-relative path AND the commit sha or date it was read at
       E.2  at least one `command` -> a fragment of its output
       E.3  names the gap, or states explicitly that there is none
       E.4  lists a follow-up, or states explicitly that there is none
     The gate cannot tell a real output from an invented one — that is still the reviewer's job. -->

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em 2026-10-04 em `solvelab/ai-skills` no commit `6fbda3a` (`chore(release): 3.5.1`,
      topo de `origin/master`), numa extração `git archive origin/master` — nunca na árvore de
      trabalho de `~/ai-skills`, que está em `1abce62`:
      - `claude/global/hooks/backlog-rite.py` — 273 linhas; docstring `:8-12` e `:43-50`; `SPEC_RITE`
        `:99-103`; `SPEC_RITE_DIR` `:107`; `has_spec_rite` `:110-116`; `evaluate` `:132-142`;
        fixtures do selftest `:161-165`; casos `:169-213`; resumo `:249`.
      - `claude/global/hooks/locale-rite.py` — 937 linhas; docstring da prosa `:82-99`; `CHECK_PATH`
        `:155`; `declared_prose` `:267-282`; `prose_findings_for` `:285-307` (`:300-302`);
        `findings_for` `:373-396` (`:383-384`, `:390`); `evaluate` `:503-545` (`:520-522`); selftest
        `:548-911` (`cwd` fixo `:553`, allowlist `:674-682`, legado `:687-722`, prosa `:735-847`,
        `SKIP` `:839-847`).
      - `claude/global/hooks/locale-stop-gate.py` — 853 linhas; docstring `:4`, KNOWN LIMIT `:94-121`
        (`:99`, `:111-114`), fiação `:123-131`; `MAX_DIFF_LINES` `:158`; `GIT_TIMEOUT` `:160`;
        `UNMEASURED_REASON` `:206-214`; `FOOTER` `:220-224`; `prose_findings` `:256-273`; `brief`
        `:280-286`; `run_git` `:289-296`; `uncommitted_diff` `:311-366` (`:318-321`);
        `gating_findings` `:369-374`; `block_reason` `:389-393`; `evaluate` `:422-467`;
        `_fixture_env` `:476-485`; `_repo` `:493-501`; casos `:546-547` e `:769-774`.
      - `skills/code-locale/references/check-identifier-locale.py` — `PathFinding.render` `:287-302`;
        `EXT_LANG` `:218-223` (sem `.md`, sem `.rs`); `load_allowlist` `:456-466`; `project_relative`
        `:528-541`; `scan_path` `:573-604`; `scan_diff` `:715-717`; CLI `:929`, `:953`.
      - `skills/code-locale/references/check-prose-locale.py` — `find_declaration` `:167-181`;
        `ProseFinding.render` `:451-458`; `path_allowlisted` `:473-476`.
      - `skills/backlog/SKILL.md` — `version: 1.5.2` (`:17`), compatibility `:21-22`, passo 2
        `:76-83`, passo 6 `:93-104`; `skills/backlog/references/backlog-config.md` (`:5-12`,
        `:49-67`, `:69-92`); `skills/backlog/references/issue-template.md` (`:51-65`, `:94-97`).
      - `skills/execute-backlog/SKILL.md` — `version: 1.9.0` (`:17`), rail 10 `:77-83`, passo 5
        `:105-109`, passo 6 `:110-115`; `skills/execute-backlog/references/spec-rite.md` (`:11-27`,
        `:46-61`, `:97-103`); `skills/execute-backlog/references/execution-flow.md` (plano `:17-32`,
        branch `:83-90`).
      - `openspec/specs/skills-catalog/spec.md` — os quatro requisitos copiados inteiros no delta:
        `:200-268` (6 cenários), `:270-319` (5), `:907-1052` (14), `:1568-1684` (11).
      - `openspec/config.yaml`, `openspec/schemas/skills-rite/schema.yaml` (`:89-102`, `:247-286`),
        `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md`,
        `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py`,
        `scripts/validate-spec-rite.py` (`:60`, `:128-141`, `:448-474`),
        `scripts/validate-skill-version.py` (`:1-40`), `scripts/validate-skills.py` (C1-C13).
      - `openspec/changes/archive/2026-09-05-add-locale-stop-gate/design.md:62` e
        `openspec/changes/archive/2026-08-23-add-spec-rite-gate/proposal.md:40` — as decisões que o
        design revê; `openspec/changes/archive/2026-09-06-add-prose-locale-gate/` e
        `openspec/changes/archive/2026-09-25-update-doc-structure-checker-blind-spots/` — forma da casa.
      - `README.md` `:322-332`, `:376-394`, `:396-438`; `.github/workflows/ci.yml` `:49-68`
        (wrappers), `:181-193` (selftests dos hooks), `:216-240` (gates do rito e de versão);
        `.releaserc.json`; `update.sh` `:1-12`; `generate.sh`.

      Fora do repositório, somente leitura, em 2026-10-04: `~/.claude/settings.json` (`:121`, `:142`,
      `:148`, `:170`, `:214-215`, `:285-288`); `~/.claude/plugins/installed_plugins.json`;
      `~/.claude/plugins/known_marketplaces.json`; o workspace do Mantis —
      `backlog.yml` (`:15-23`, `:50-53`), `mantis-computer/.github/backlog.yml` (`:40-44`),
      `mantis-computer/openspec/config.yaml` (`schema: spec-driven`), `mantis-computer` em `9b4c587`;
      a CLI instalada `@fission-ai/openspec` 1.6.0 — `dist/core/planning-home.js` (`:37-38`) e
      `dist/core/root-selection.js` (`:170-184`, `:224-258`).

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      ```
      git -C ~/ai-skills rev-parse origin/master master
        -> 6fbda3a30aafde1fcba58a2e3bb221ea387db595
        -> 1abce620887dea45e0abc6e700d238e4e4677935
      git -C ~/ai-skills ls-remote origin refs/heads/master
        -> 6fbda3a30aafde1fcba58a2e3bb221ea387db595	refs/heads/master
      git -C ~/ai-skills diff --quiet 1abce62 origin/master -- openspec/specs/skills-catalog/spec.md claude/global/hooks skills/backlog skills/execute-backlog skills/code-locale README.md scripts generate.sh openspec/schemas; echo "cited-paths diff rc=$?"
        -> cited-paths diff rc=0
      python3 --version            -> Python 3.14.5
      git --version                -> git version 2.47.3
      openspec --version           -> 1.6.0
      claude --version             -> 2.1.289 (Claude Code)
      openspec list --help         -> Options: --specs | --changes | --sort <order> | --json | --store <id> | -h, --help
      openspec validate --help     -> Usage: openspec validate [options] [item-name] / --all --changes --specs --type <type> --strict --json --concurrency <n> --no-interactive --store <id>
      openspec new change update-rite-repo-discovery --schema skills-rite
        -> Created change 'update-rite-repo-discovery' at openspec/changes/update-rite-repo-discovery/
        -> Schema: skills-rite
      claude --help | grep -n -A3 -E -- '--setting-sources|^  --settings|--bare'
        -> 225:  --setting-sources <sources>  Comma-separated list of setting sources / to load (user, project, local).
        -> 227:  --settings <file-or-json>    Path to a settings JSON file or a JSON / string to load additional settings from
        -> 41:   --bare                       Minimal mode: skip hooks (those defined / in settings and by installed plugins; ...
      claude --help | grep -E -- '--plugin-dir'
        -> --plugin-dir <path>  Load a plugin from a directory or .zip
      claude plugin --help | grep -n -A2 -E '^  update'
        -> 53:  update [options] <plugin>  Update a plugin to the latest version / (restart required to apply)
      claude plugin marketplace --help | grep -E 'update'
        -> update [options] [name]  Update marketplace(s) from their source - updates
      (cd <raiz do workspace do Mantis> && git rev-parse --show-toplevel; echo rc=$?)
        -> fatal: not a git repository (or any parent up to mount point /mnt)
        -> rc=128
      python3 -c 'import tempfile; print(tempfile.gettempdir())'   -> /tmp
      git -C /tmp rev-parse --show-toplevel   -> fatal: not a git repository (or any parent up to mount point /)
      ```

      Gates do repositório na cópia de `6fbda3a` com esta change commitada num branch (base
      `origin/master` apontando para a extração):

      ```
      python3 scripts/validate-skills.py | tail -1       -> skills checked: 40   findings: 0
      python3 scripts/validate-skill-version.py          -> skill-version gate: 0 findings (base origin/master, 0 skill(s) changed, 0 with content changes)
      python3 scripts/validate-repo-hygiene.py | tail -1 -> repo hygiene: 0 findings
      python3 scripts/scan-secrets.py | tail -1          -> no credentials found
      python3 skills/code-locale/references/check-identifier-locale.py --markdown-fences skills/backlog skills/execute-backlog | tail -2
        -> findings: 0
        -> en-unknown: 5 segment(s) not in the English word list — advisory — they do not fail this run
      python3 scripts/validate-rite-evidence.py --selftest | tail -1 -> 7/7 defect classes detected, 1/1 known escapes stayed silent
      python3 scripts/validate-spec-rite.py --selftest | tail -1     -> 6/6 defect classes detected, 10/10 false-positive cases stayed silent, 6/6 reader cases correct, 2/2 path-reader cases correct
      openspec archive update-rite-repo-discovery --yes  (numa cópia descartável)
        -> ~ 4 modified / Totals: + 0, ~ 4, - 0, → 0 / Change 'update-rite-repo-discovery' archived as '2026-10-04-update-rite-repo-discovery'.
        -> openspec validate --all --strict: Totals: 3 passed, 0 failed (3 items)
      ```

      Selftests de base, nos hooks de `6fbda3a`:

      ```
      python3 claude/global/hooks/backlog-rite.py --selftest | tail -1
        -> selftest OK: 16 decisions, 6 malformed payloads, plus the output shape
      python3 claude/global/hooks/locale-rite.py --selftest | tail -1
        -> selftest OK: 13 PostToolUse decisions, 12 PreToolUse decisions, inform mode, en-unknown, the allowlist, the legacy path, the waiver above the fragment, both envelopes, the environment, the argv contract and 21 prose decisions with and without .code-locale
      python3 claude/global/hooks/locale-stop-gate.py --selftest | tail -1
        -> selftest OK: 41 decisions in temporary git repositories (the prose direction with and without .code-locale included), 2 output shapes, 5 malformed payloads, plus the argv contract
      ```

      O Problem da issue, re-medido no workspace do Mantis com os hooks de `6fbda3a` (script
      `probe-261.sh`, 33 linhas, sha1 `da3908da84c4cdbed2983750618392693f94ef3c`, carregado na íntegra
      no corpo do PR; payloads por stdin; `GIT_OPTIONAL_LOCKS=0`; nada escrito). A mesma saída saiu
      duas vezes, na cópia do rascunho e na cópia da revisão:

      ```
      bash probe-261.sh <extração de 6fbda3a>
      ### cwd = <workspace root>
      backlog-rite spec sentence: absent
      [ -d openspec ]: not found
      openspec list: No active changes found.
      openspec list --specs: No specs found.
      stop gate: rc=0 bytes=0 decision=silent
      git rev-parse --show-toplevel: fatal: not a git repository (or any parent up to mount point /mnt)
      write gate (Write mantis-computer/crates/core/src/servicos/x.rs): deny ["  mantis-computer/crates/core/src/servicos/x.rs: servicos  [path-pt-noun: 'servicos']"]
      ### cwd = mantis-computer
      backlog-rite spec sentence: present
      [ -d openspec ]: found
      openspec list: No active changes found.
      openspec list --specs: Specs:   avatar-overlay     requirements 10   diagnostics        requirements 4
      stop gate: rc=0 bytes=0 decision=silent
      git rev-parse --show-toplevel: /mnt/d/DOCUMENTS/Documents/Project/WSL/mvp/mantis/mantis-computer
      write gate (Write mantis-computer/crates/core/src/servicos/x.rs): deny ["  crates/core/src/servicos/x.rs: servicos  [path-pt-noun: 'servicos']"]
      ### cwd = mantis-computer/src-tauri
      backlog-rite spec sentence: absent
      [ -d openspec ]: not found
      openspec list: No active changes found.
      openspec list --specs: Specs:   avatar-overlay     requirements 10   diagnostics        requirements 4
      stop gate: rc=0 bytes=0 decision=silent
      git rev-parse --show-toplevel: /mnt/d/DOCUMENTS/Documents/Project/WSL/mvp/mantis/mantis-computer
      write gate (Write mantis-computer/crates/core/src/servicos/x.rs): silent
      ```

      Fixtures herméticas (script `fixtures-261.py`, 131 linhas, sha1
      `b33bafa6dfea0cea7d04d2fff4892979cdf82c3a`, carregado na íntegra no corpo do PR; git com config em
      branco e `GIT_CEILING_DIRECTORIES` no diretório das fixtures), mesmos hooks. Montagem, lida no
      script: `br-ws/with-spec/` tem `.git` e `openspec/`; `br-worktree/.git` é ARQUIVO, com
      `openspec/` na raiz; `lw-ws/child/.identifier-locale-allow` lista `servicos`. A mesma saída saiu
      nas duas cópias (a linha de `br-repo` cortada aqui no começo da frase):

      ```
      python3 fixtures-261.py <extração de 6fbda3a> <diretório das fixtures>
      backlog-rite   cwd=br-repo                -> rc=0 sentence present
      backlog-rite   cwd=br-repo/src/deep       -> rc=0 sentence absent
      backlog-rite   cwd=br-ws                  -> rc=0 sentence absent
      backlog-rite   cwd=br-ws-none             -> rc=0 sentence absent
      backlog-rite   cwd=br-worktree/pkg        -> rc=0 sentence absent
      write-gate     cwd=lw-ws                  -> rc=0 deny ["child/servicos/x.py: servicos  [path-pt-noun: 'servicos']"]
      write-gate     cwd=lw-ws/child            -> rc=0 silent
      write-gate     cwd=lw-sub/src-tauri       -> rc=0 silent
      write-gate     cwd=lw-sub                 -> rc=0 deny ["crates/core/src/servicos/x.rs: servicos  [path-pt-noun: 'servicos']"]
      stop-gate      cwd=ls-ws                  -> rc=0 silent
      stop-gate      cwd=ls-ws/child            -> rc=0 block ["servico_cliente.py: servico_cliente  [path-pt-noun: 'servico']", '      servico_cliente.py']
      stop-gate      cwd=ls-ws/child/orders     -> rc=0 block ["servico_cliente.py: servico_cliente  [path-pt-noun: 'servico']", '      servico_cliente.py']
      stop-gate      cwd=ls-ws/no-repo          -> rc=0 silent
      ```

      Qual forma de entrada a allowlist de um filho aceita (`servico_cliente.py` com conteúdo inglês,
      allowlist excluída via `.git/info/exclude`, `cwd` no filho; `ws/child` é um repositório com um
      commit e `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CEILING_DIRECTORIES=<base>`):

      ```
      cd <base>/ws/child && echo .identifier-locale-allow >> .git/info/exclude
      printf 'def find_customer(user_id):\n    return user_id\n' > servico_cliente.py
      for entry in child/servico_cliente.py servico_cliente.py; do printf '%s\n' "$entry" > .identifier-locale-allow
        printf '{"hook_event_name":"Stop","stop_hook_active":false,"cwd":"%s"}' "$PWD" | python3 <6fbda3a>/claude/global/hooks/locale-stop-gate.py | python3 -c '...decision or silent...'; done
        -> child/servico_cliente.py -> block
        -> servico_cliente.py -> silent
      ```

      Custo do Stop gate inteiro (processo + git), 3 corridas cada, com
      `python3 time_stop.py <hook> <cwd>` (um `subprocess.run` do hook com o payload de Stop por stdin,
      cronometrado com `time.monotonic()`; em 9p com `GIT_OPTIONAL_LOCKS=0`):

      ```
      mantis-computer (9p, /mnt/d, diff limpo)         -> 0.82s 0.74s 0.78s last=silent
      mantis-computer (9p, outra série, mesmo laço)    -> 0.69s 0.71s 0.65s last=silent
      raiz do workspace do Mantis (9p, não é repo)     -> 0.10s 0.09s 0.11s last=silent
      cópia da revisão (tmpfs, diff limpo)             -> 0.09s 0.10s 0.12s last=silent
      fixture ls-ws/child (tmpfs, 1 arquivo PT)        -> 0.11s 0.14s 0.13s last=block
      ```

      Onde a CLI do `openspec` acha o workflow, e o que cada regra de detecção responde quando um
      pacote carrega `openspec/` abaixo de uma raiz git que não carrega (`mono` com `git init`,
      `mono/packages/app/openspec/{specs,changes/archive,config.yaml}`):

      ```
      grep -n -A2 'export function findRepoPlanningRootSync' <prefixo npm>/@fission-ai/openspec/dist/core/planning-home.js
        -> 37:export function findRepoPlanningRootSync(startPath = process.cwd()) {
        -> 38-    return findNearestAncestor(startPath, (dirPath) => pathExistsAsDirectory(path.join(dirPath, 'openspec')));
      (cd <dir> && openspec list --json) | python3 -c '...r=json.load(sys.stdin)["root"]; print(r["source"], r["path"])'
        -> <workspace root> -> implicit /mnt/d/DOCUMENTS/Documents/Project/WSL/mvp/mantis
        -> /mantis-computer -> nearest /mnt/d/DOCUMENTS/Documents/Project/WSL/mvp/mantis/mantis-computer
        -> /mantis-computer/src-tauri -> nearest /mnt/d/DOCUMENTS/Documents/Project/WSL/mvp/mantis/mantis-computer
      root="$(git rev-parse --show-toplevel)"   # de cada <dir>, com GIT_CEILING_DIRECTORIES=<base>
        -> mono/packages/app: [ -d openspec ]=found | draft [ -d "$root/openspec" ]=not found | openspec list --json root=nearest mono/packages/app
        -> mono/packages/app/src: [ -d openspec ]=not found | draft [ -d "$root/openspec" ]=not found | openspec list --json root=nearest mono/packages/app
      printf '{"prompt":"implementa o endpoint de login","cwd":"%s"}' <dir> | python3 <6fbda3a>/claude/global/hooks/backlog-rite.py
        -> mono/packages/app -> spec sentence present
        -> mono/packages/app/src -> spec sentence absent
      ```

      Um `.git` arquivo para um gitdir inexistente, visto pelo git (o Stop gate); a subida de D1 o chama
      de raiz (declarado em D5):

      ```
      cd <fixtures>/br-worktree/pkg && cat ../.git && git rev-parse --show-toplevel; echo "rc=$?"
        -> gitdir: /nowhere/.git/worktrees/x
        -> fatal: not a git repository: /nowhere/.git/worktrees/x
        -> rc=128
      ```

      Pastas desta máquina que TR2 já chama de raiz de workspace:

      ```
      ls -d ~/*/.git ~/.[!.]*/.git
        -> /home/diegops/.oh-my-zsh/.git/
        -> /home/diegops/ai-skills/.git/
      ```

      Fiação e cache (somente leitura):

      ```
      grep -n 'ai-skills/claude/global/hooks\|"timeout"' ~/.claude/settings.json
        -> 121: "command": "python3 /home/diegops/ai-skills/claude/global/hooks/locale-rite.py",
        -> 142: "command": "python3 /home/diegops/ai-skills/claude/global/hooks/backlog-rite.py",
        -> 148: "command": "python3 /home/diegops/ai-skills/claude/global/hooks/verify-rite.py",
        -> 170: "command": "python3 /home/diegops/ai-skills/claude/global/hooks/locale-rite.py",
        -> 214: "command": "python3 /home/diegops/ai-skills/claude/global/hooks/locale-stop-gate.py",
        -> 215: "timeout": 30
      git -C ~/ai-skills worktree list              -> /home/diegops/ai-skills  1abce62 [master]
      git -C ~/ai-skills status --porcelain | wc -l -> 0
      python3 -c '...installed_plugins.json: plugins["ai-skills-workflow@ai-skills"], scope user -> version, installPath'
        -> 3.4.0 /home/diegops/.claude/plugins/cache/ai-skills/ai-skills-workflow/3.4.0
      grep -n -A3 '"ai-skills"' ~/.claude/plugins/known_marketplaces.json
        -> 10:  "ai-skills": {
        -> 12-      "source": "github",
        -> 13-      "repo": "solvelab/ai-skills"
      for s in backlog execute-backlog; do diff -rq <cache 3.4.0>/skills/$s <6fbda3a>/skills/$s; echo "diff -rq $s rc=$?"; done
        -> diff -rq backlog rc=0
        -> diff -rq execute-backlog rc=0
      grep -rn -- '-d openspec' . (fora do archive)
        -> skills/execute-backlog/references/spec-rite.md:14 | skills/backlog/SKILL.md:96 | plugins/workflow/skills/execute-backlog/references/spec-rite.md:14 | plugins/workflow/skills/backlog/SKILL.md:96 | cursor/rules/backlog.mdc:81
      ```

      Precedentes de versão e de archive (`git log`/`git show` em `~/ai-skills`, somente leitura):

      ```
      git log -1 --format='%h %s' e738120   -> e738120 ✨ skill(backlog): grava o veredito de spec na issue, em vez de calar
      git show e738120:skills/backlog/SKILL.md | grep -m1 '^  version:'   ->   version: 1.4.0
      git show e738120~1:skills/backlog/SKILL.md | grep -m1 '^  version:' ->   version: 1.3.0
      git show 6e43a90:skills/documentation/SKILL.md | grep -m1 '^  version:'   ->   version: 4.1.0
      git show 6e43a90~1:skills/documentation/SKILL.md | grep -m1 '^  version:' ->   version: 4.0.0
      git log origin/master --format='%h %s' -40 | grep -i arquiva
        -> 1abce62 🗃️ chore(openspec): arquiva a change da sprite-animation (#254) (#256)
        -> f0a2530 🗃️ chore(openspec): arquiva a change do mapa de documentos (#251) (#253)
        -> c59b1f9 🗃️ chore(openspec): arquiva a change do #248 (#250)
        -> fef050d 🗃️ chore(openspec): arquiva as changes do #238 e do #239 (#245)
        -> 28d0c80 🗃️ chore(openspec): arquiva a change do #232 e dá veredito às duas caixas (#237)
        -> 4a865a2 🗃️ chore(openspec): arquiva as changes do #225 e do #228 (#234)
        -> 432342f 🗃️ chore(openspec): arquiva update-bug-hunter-generation-and-scoring (#226)
      ```

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Oito lacunas, as primeiras duas também em design.md *Open Questions*: (1) o que o harness faz
      quando um hook de `Stop` passa do timeout da fiação; (2) se `--settings`, `--setting-sources
      project,local` e `--plugin-dir` se combinam como a corrida pelo harness precisa — lido só no
      `--help` do 2.1.289; (3) os hooks novos pelo harness — eles ainda não existem; (4) o critério do
      `/backlog` rodado da raiz do Mantis, que precisa do texto novo da skill; (5) gates do CI não
      rodados aqui: `agentskills validate` (binário não instalado; `uvx` existe em `~/.local/bin` e
      não foi exercitado), `npx @anthropic-ai/claude-code@2.1.246 plugin validate . --strict` e
      `scripts/smoke-install-scripts.sh`;
      (6) a linha `add-avatar-overlay 40/44 tasks` da tabela da issue não se reproduz — a change foi
      arquivada em `mantis-computer` (`9b4c587`); a subida da CLI foi re-medida com `openspec list
      --specs`; (7) uma série anterior do custo do Stop gate em `mantis-computer` (1,11-2,12 s) não tem
      comando registrado e não se reproduziu nas duas séries de E.2 (0,65-0,82 s): o custo em 9p varia
      de uma corrida para outra, e nenhum número de uma série só é tomado como o custo; (8) o
      comportamento do Stop gate quando o prazo acaba no meio dos arquivos não rastreados de um filho
      só existe depois da implementação (tarefa 2.6).

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Notados e **não** feitos, ficam como follow-up: (1) `skills/code-locale/SKILL.md:35-36` cita
      contagens velhas de selftest (17 decisões de prosa e 38 do Stop gate, contra 21 e 41 medidas) e
      esta change as deixa mais velhas — corrigir exige bump do `code-locale`; (2) #260, a raiz do
      `scripts/validate-spec-rite.py`; (3) depois do merge, o comentário de `backlog.yml:50-53` e o
      `CLAUDE.md` da raiz do workspace do Mantis, que cabem ao workspace; (4) `load_allowlist`
      subindo acima da fronteira do repositório, fora de escopo pela issue; (5) os hooks lerem
      `workspace.repos`, registrado como `# lean:` com gatilho; (6) o `~/.claude/CLAUDE.md` do
      mantenedor diz que o marketplace é o diretório local `~/ai-skills`, mas a config aponta para
      `github` `solvelab/ai-skills` com cache em 3.4.0 — configuração pessoal, fora do rito; (7) excluir
      diretórios ocultos (`~/.oh-my-zsh`) da definição de workspace dos hooks — decisão do usuário,
      registrada em design.md *Risks*, não feita aqui.

## 2. Hooks

- [ ] 2.1 `backlog-rite.py`: `find_repo_root` (subida até a primeira `.git`, diretório ou arquivo, sem
      git), `child_repos` (filhos diretos com `.git`, em ordem de nome), `WORKSPACE_SPEC_RITE`, e os
      quatro ramos de D3 — o primeiro olha `openspec/` em cada nível do `cwd` até a raiz, o mais
      próximo vale; docstring (`:8-12`, `:43-50`) diz onde o workflow é procurado
- [ ] 2.2 `backlog-rite.py --selftest`: `.git` nas fixtures `with-rite` e `without-rite` (os 16 casos
      mantêm nome e resultado); casos novos — subpasta de repo com `openspec/` na raiz (frase), subpasta
      de repo sem (sem frase), subpasta que carrega `openspec/` abaixo de uma raiz que não carrega
      (frase, como hoje), raiz de workspace com um filho que tem `openspec/` (frase nomeando só
      esse filho), raiz de workspace sem esse filho (sem frase), `.git` arquivo (frase), repo aninhado
      (a primeira `.git` vence), diretório fora de repo com `openspec/` (frase); os que precisam de "fora
      de qualquer repositório" imprimem `SKIP` com o motivo quando o `TMPDIR` está dentro de um
      repositório
- [ ] 2.3 `locale-rite.py`: `write_root` serve `findings_for` e `prose_findings_for` (D4);
      `declared_prose` sem mudança; docstring diz de qual repositório saem a allowlist e o caminho
- [ ] 2.4 `locale-rite.py --selftest`: `.git` nas fixtures da allowlist e do legado (rótulo da
      allowlist: "of the written file's repository"); casos novos — `cwd` numa subpasta e `Write` em
      `crates/core/src/servicos/x.rs` do mesmo repo (`deny`, `path-pt-noun` em `servicos`, caminho
      relativo à raiz), `cwd` na raiz de workspace e `Write` num filho cuja allowlist lista o nome
      (mudo nos dois eventos), o mesmo sem a entrada (`deny` com o caminho relativo ao filho), `.git`
      arquivo, arquivo fora de qualquer repo (allowlist do `cwd`, com `SKIP` guardado)
- [ ] 2.5 `locale-stop-gate.py`: `rev-parse` `None` continua mudo, código de saída diferente de zero
      lista `child_repos` (o repositório que o git não abre fica no KNOWN LIMIT, D5); cada filho por
      `uncommitted_diff`, `gating_findings` e `prose_findings` na raiz dele; achados prefixados por
      `<filho>/` no motivo e em `brief`, dica da allowlist relativa ao filho, e o `FOOTER` diz que a
      entrada da allowlist (inclusive a de um achado de prosa) é o caminho sem o prefixo;
      `MAX_DIFF_LINES` compartilhado; `TIME_BUDGET` (prazo único, chamadas git com
      `min(GIT_TIMEOUT, restante)`, nenhuma chamada nova com o prazo esgotado, e a chamada encurtada
      pelo prazo distinguível da que estourou `GIT_TIMEOUT`); filho não alcançado ou interrompido no
      meio declarado não medido, nunca pulado; `FOOTER` e `UNMEASURED_REASON` reescritos (D5);
      docstring: KNOWN LIMIT `:99`, `:111-114`, custo medido por repositório e quantos filhos cabem no
      prazo
- [ ] 2.6 `locale-stop-gate.py --selftest`: os 41 casos sem mudança; casos novos na raiz de um
      workspace de fixture — arquivo não rastreado em português num filho (`block` com
      `<filho>/servico_cliente.py`), um arquivo cujo único achado é o nome com a linha que o motivo
      imprime acrescentada à allowlist do filho (mudo; com `<filho>/...` na allowlist, continua
      `block`), allowlist de um filho não fala pelo outro, `.code-locale` de um filho não fala pelo outro,
      filhos limpos (mudo), teto de linhas estourado entre filhos (diz o que não foi medido), prazo
      esgotado antes de um filho e no meio dos arquivos não rastreados de um filho (bloqueia uma vez,
      mensagem no Stop seguinte, nunca um filho parcial dado como medido), diretório filho sem `.git`
      ignorado

## 3. Skills, README e cópias geradas

- [ ] 3.1 `skills/backlog/SKILL.md` passo 6: detecção onde o workflow vive para o repositório alvo
      (em modo repo, o `openspec/` mais próximo do `cwd` até a raiz git — D6; em modo workspace, a raiz
      de cada repositório afetado), `openspec list` com esse diretório como diretório de trabalho;
      `references/backlog-config.md`: precedência de `spec_rite` por repositório afetado — por chave
      (um `.github/backlog.yml` sem `spec_rite` cai no do workspace), dita ao lado da precedência por
      arquivo de `:10-12`, que vale para o resto da config;
      `references/issue-template.md`: um veredito por repositório afetado que roda o workflow;
      `metadata.version` 1.5.2 -> 1.6.0
- [ ] 3.2 `skills/execute-backlog/references/spec-rite.md`: *Detect the rite* com a mesma regra de
      3.1, comandos com esse diretório como diretório de trabalho, *Policy comes from the repo* com a
      precedência por repositório afetado (link para `backlog-config.md`); passo 5 do `SKILL.md`: a
      cláusula de workspace que FR4 pede (D6); `metadata.version` 1.9.0 -> 1.10.0
- [ ] 3.3 `README.md` `:326`, `:403-404`, `:430-434`: onde o workflow é procurado, os filhos do
      workspace no Stop gate, "under a second" e a lista do que escapa
- [ ] 3.4 `bash generate.sh` e commit de tudo que `git status --porcelain --untracked-files=all`
      mostrar (`plugins/`, `claude/skills/`, `cursor/rules/`, `codex/`, `copilot/`)

## 4. Simulation & Field Proof (MANDATORY)

<!-- Second-to-last but one: proof that the artifact was RUN, before the quality review discusses it.
     Reading, probing, uniform frontmatter and a green strict validation can all hold while the
     artifact was never executed once — measured on 2026-08-26 (issue #95), where a green selftest
     and a green CI still shipped two defects that only an end-to-end run surfaced.

     Exercise the artifact through the path its USER takes — the hook fired by the harness, the CLI
     invoked as documented, the skill loaded in a session — and record what you OBSERVED, never what
     you expected. Breaking it on purpose afterwards is a different job: the bug-hunter skill.
     The doctrine behind "observed, not recalled" is verify-before-claiming.

     Shape each box owes, gated by scripts/validate-rite-evidence.py once ticked:
       S.1  an `entry point` -> a fragment of the OBSERVED output; or an explicit statement that the
            change touches no runtime artifact
       S.2  the case matrix as counts (n/n): what had to fire and did, what had to stay silent and
            did, which known escapes stayed silent
       S.3  names what escaped or misbehaved, or states explicitly that nothing did
     The gate cannot tell a real observation from an invented one — that is still the reviewer's job. -->

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 5. Quality Gates (MANDATORY)

<!-- Adversarial review of the skills touched — not happy-path. Every skill added or edited
     by this change gets checked against the skills-authoring spec. Keep this group second-to-last. -->

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

## 6. Validation & Closure (MANDATORY)

<!-- Always the last group. "Done" is verifiable, not an opinion. -->

- [ ] V.1 `openspec validate update-rite-repo-discovery --strict` green
- [ ] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive update-rite-repo-discovery --yes` after all groups above are `[x]` — PR
      separado, como o repositório já faz
