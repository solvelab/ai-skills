# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `1122599` (master, base de `backlog/248-terse-response-skill`) em 2026-09-10:

      - Plugin caveman instalado, `~/.claude/plugins/cache/caveman/caveman/81536f57b330`:
        `skills/caveman/SKILL.md` inteiro (6698 B, sha256 `3edd6775…`), `.claude-plugin/plugin.json`
        (hooks `SessionStart` e `UserPromptSubmit`), `src/hooks/caveman-activate.js` (:1-80,
        :138-146, :257-345), `caveman-mode-tracker.js:169` (`execFileSync`),
        `cavecrew-model-overrides.js:24-40`, `LICENSE` (nota de escopo MIT/BSL), `package.json`
        (2.3.1); `~/.claude/plugins/installed_plugins.json` (gitCommitSha);
        `~/.claude/.caveman-active` (`full`); `~/.claude/settings.json:197,211-214`;
        `~/.claude/settings.local.json:8-9`; `~/.claude/hooks/` (só `memory-autopush.sh`).
      - `skills/lean-code/SKILL.md:1-45` (frontmatter, linha *Not version-bound*, mapa de
        references); `skills/agent-delegation/SKILL.md:27`.
      - `claude/global/personal-rules.md:64-72` (bloco *Lean Code*) e os outros blocos.
      - `generate.sh:74-79` (`group_of`: `git|process` -> `workflow`), `:170-227`, `:252-263`,
        `:275-330`.
      - `README.md:51`, `:59`, `:113`, `:697-709`, `:1017-1086`.
      - `scripts/validate-skills.py` (C1–C13, docstring :6-19; `check_anti_trigger` :588;
        `check_meta` :401; `check_limits` :445), `scripts/validate-repo-hygiene.py:196-249` (H3).
      - `openspec/specs/skills-authoring/spec.md:11-76` (requisito *Single canonical home per
        rule* inteiro, copiado no delta antes da extensão); `openspec/specs/skills-catalog/spec.md:10-25`
        (composição não é contagem congelada).
      - `openspec/changes/archive/2026-09-07-add-tdd-skill/{proposal.md,tasks.md,specs/*}` como
        precedente de skill ADDED.
      - `research/i-have-adhd/run.py` (`skill_for`, `condition_prompt`, `main`) e `results.md`
        (seção *Verbosity*).
- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      `claude --version` -> `2.1.268 (Claude Code)` (subiu de 2.1.267 durante o #246)

      `grep -n -E 'fetch\(|https?://|child_process|execSync|spawn' src/hooks/*.js` (no cache do
      caveman) -> só `caveman-mode-tracker.js:8:const { execFileSync } = require('child_process');`

      `cat ~/.claude/.caveman-active` -> `full`

      `openspec new change add-terse-response-skill --schema skills-rite` -> `Created change …`;
      `openspec validate add-terse-response-skill --strict` -> `Change 'add-terse-response-skill' is valid`

      `python3 -c "import yaml; …len(description)"` -> `1017` (limite 1024; a primeira versão deu
      `C10 … 1178 chars`)

      `python3 scripts/validate-skills.py` -> `skills checked: 39   findings: 0` (após corrigir
      C10 e dois caminhos inline em `upstream.md` para URLs, C1/C12)

      `./generate.sh` -> `Generated wrappers for 39 skills` / `Generated 11 category plugins`;
      `plugins/workflow/.claude-plugin/plugin.json` passa a listar `terse-response`.

      Sonda de carga do `CLAUDE.md` de rascunho com `@` (sentinela `BENCH-SENTINEL: terse-sim`,
      Haiku): sem `--setting-sources` -> `BENCH-SENTINEL: terse-sim DONE`; com
      `--setting-sources user` -> saída vazia (o flag desliga a memória de usuário). O caminho
      real da simulação é sem o flag.

      `python3 research/i-have-adhd/run.py --probe --mode prompt` (Haiku) -> `probe prompt:
      PASSED  $0.1272`.
- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      (a) ~~**Se um bloco-resumo no `personal-rules.md` segura o registro.**~~ **FECHADA em
      2026-09-10, com correção (design.md D2, emenda).** Não segura: mesma pergunta em Haiku, só
      o bloco -> 1030 chars de prosa com títulos; com a skill inteira incluída por `@` -> 813
      (Haiku) e 855 (Fable, artigos caídos). O bloco termina em
      `@../../skills/terse-response/SKILL.md`.

      (b) ~~**Se `@` aninhado com caminho relativo resolve a partir do arquivo que o contém.**~~
      **FECHADA pela simulação**: `CLAUDE.md` de rascunho -> `@/home/…/claude/global/personal-rules.md`
      -> `@../../skills/terse-response/SKILL.md`; a resposta do Fable saiu tersa (S.1).

      (c) **Deriva em sessões longas sem o tracker por prompt.** Não probada: a simulação é de
      um turno. Fica como follow-up (E.4); não afirmada como resolvida.
- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Um desvio, aprovado pelo desenho e registrado como emenda em `design.md` D2: o bloco
      always-on inclui a skill inteira por `@` em vez de resumi-la (medido: o resumo não segura o
      registro). Follow-ups anotados e **não** feitos:

      - Deriva do registro em sessões longas (o tracker por prompt do caveman existia para isso):
        medir com uma conversa multi-turno antes de decidir se precisa de algo além do bloco.
      - Gate de não-regressão no modelo diário (aqui rodou em Haiku, $0.85 por passada; no Fable
        seriam ~$6 por passada — fora do teto de $3 deste item).
      - O `CLAUDE.md` do repositório (`.claude/`) não inclui o bloco: quem clona sem o
        `personal-rules.md` do mantenedor não recebe o registro — é opt-in por desenho.

      Nada em `.github/workflows/`, `scripts/`, outros `skills/` ou `~/.claude` foi tocado.

## 2. A skill

- [x] 2.1 `skills/terse-response/SKILL.md`: frontmatter uniforme (`process`, `1.0.0`, MIT,
      compatibility, `Verified against` sem dependência de versão), doutrina de um nível só, o que
      nunca cai, frase de saída, auto-clareza, fronteiras; prosa em inglês; sem seção *Usage*
- [x] 2.2 `skills/terse-response/references/upstream.md`: PIN (commit, sha256, licença), o que
      entrou, o que ficou de fora e por quê, e o checklist de remoção do plugin

## 3. Casa canônica e always-on

- [x] 3.1 Bloco `## Terse Response` em `claude/global/personal-rules.md`, com link para a skill
- [x] 3.2 Mapa canônico de `openspec/specs/skills-authoring` ganha a entrada (delta MODIFIED)

## 4. Catálogo

- [x] 4.1 `generate.sh` sem diff pendente; `plugins/workflow` embarca a skill; descrição do plugin
      regenerada
- [x] 4.2 `README.md`: tabela de plugins, tabela de skills, contagem

## 5. Medição (gate de não-regressão, pré-declarado)

- [x] 5.1 `research/i-have-adhd/run.py` ganha `--candidate-skill <path>` (o candidato deixa de ser
      fixo no vendor); selftest cobre o flag
- [x] 5.2 Matriz Haiku, modo `prompt`, 14 casos × 3 condições × n=1, teto $3, sem juiz; razão
      pareada de caracteres candidate/comparator registrada em `research/i-have-adhd/results.md`
      (seção datada) e o veredito lido pelo limiar de D4

      Passada 1 (`terse-01`, $0.85): razão pareada 1.22, candidato mais curto em 2 de 12 pares —
      **REWRITE**: a skill descrevia o registro em prosa plena e o modelo não o imitava. Reescrita
      com as regras no próprio registro. Passada 2 (`terse-02`, $0.85 incl. a parte perdida numa
      morte por memória e retomada pela chave): razão pareada **0.92**, candidato mais curto em 7 de
      12 pares, mediana de caracteres 213 vs caveman 292 vs sem skill 472 — **PASS**.
      `research/i-have-adhd/results/terse-0{1,2}-export.json`; seção datada em `results.md`.

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      Caminho real: `CLAUDE_CONFIG_DIR` de rascunho (sem plugin, sem settings) cujo `CLAUDE.md` é
      `@/home/…/ai-skills/claude/global/personal-rules.md`, que termina em
      `@../../skills/terse-response/SKILL.md`; `claude --print --output-format json
      --no-session-persistence --model claude-fable-5-1 --tools "" "Why does my React component
      re-render every time when I pass an inline object as a prop?"`

      -> `Inline object gets new reference every parent render. React compares props by
      \`Object.is\`, not by value. \`{a: 1} !== {a: 1}\`, so memoized child sees "changed" prop and
      re-renders.` (1032 chars, artigos caídos, $0.14)

      Mesma sessão de rascunho, prompt prefixado com `normal mode.` -> `Terse mode off. Answering
      in normal prose from here on.` seguido de 1591 chars de prosa normal ($0.15).

      Sentinela de carga (`BENCH-SENTINEL: terse-sim` no `CLAUDE.md` de rascunho, Haiku) ->
      `BENCH-SENTINEL: terse-sim DONE`.
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      **Tinham de disparar e dispararam**: memória do `CLAUDE.md` com `@` aninhado relativo 1/1
      (sentinela); registro terso pelo caminho real no Fable 2/2 (skill v1 e v2); frase de saída
      1/1; `validate-skills.py` C1–C13 39/39 skills `findings: 0` após 3 correções (C10, C1, C12);
      gate de não-regressão 1/1 na segunda passada (12 pares limpos, razão 0.92); selftest do
      harness 58/58 com e sem `--candidate-skill`.
      **Tinham de ficar quietos e ficaram**: hook events 0/9 na sonda; nenhum arquivo executável
      em `skills/terse-response` (`find -type f` -> 2 `.md`); `git diff` fora de
      `skills/terse-response`, `claude/global/personal-rules.md`, `README.md`, wrappers gerados,
      `research/i-have-adhd/` e `openspec/` vazio.
      **Escapes conhecidos que ficaram quietos**: `--setting-sources user` desliga a memória de
      usuário (a simulação não o usa); um turno só, deriva não medida.
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      Duas coisas: (1) o bloco-resumo não segurou o registro (E.3 a, D2 emendado); (2) a primeira
      versão da skill, escrita em prosa plena, reprovou no gate (razão 1.22) — o modelo imita a
      forma do texto que lê, não só o que ele manda; reescrita no próprio registro, 0.92. Uma
      passada da matriz foi morta pelo guarda de memória da máquina e retomada pela chave sem
      perda de linhas.

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

      Q.1 frontmatter: `name: terse-response` == diretório, description folded 1017 chars,
      `author: solvelab`, `version: 1.0.0`, `category: process`, `license: MIT`, `compatibility`
      presente; linha *Not version-bound* (C5). Q.2 prosa em inglês (`check-identifier-locale.py`
      -> `findings: 0`). Q.3 gatilhos: "terse mode", "be brief", "less tokens", "caveman mode",
      "modo terso", "fala menos", "resposta curta"; "Do NOT use for" aponta `documentation`,
      `conventional-commit`, `lean-code` (C13). Q.4 o bloco em `personal-rules.md` não restata:
      inclui a skill por `@`; o mapa canônico ganhou a entrada. Q.5 os exemplos de código são
      `jsx`/`sql` genéricos com identificadores em inglês.

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate <id> --strict` green — `Change 'add-terse-response-skill' is valid`; `validate-rite.sh` -> `rite gate OK`
- [x] V.2 Catalog discovery intact: `npx skills add <repo> --list` finds every skill, expected count,
      no orphan/renamed leftovers — `generate.sh` -> `Generated wrappers for 39 skills`;
      `validate-skills.py` -> `skills checked: 39   findings: 0`; `validate-repo-hygiene.py` ->
      `0 findings` (H3: `plugins/workflow` lista `terse-response`)
- [x] V.3 README / docs updated where the change alters catalog composition or usage — `README.md:59` (tabela de plugins), linha nova em *Process & git*, contagem 38 -> 39 (`:51`, `:113`)
- [ ] V.4 `openspec archive <id> --yes` after all groups above are `[x]`
