## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `4ef1f3f` (`docs(openspec): arquiva as changes harden-gate-followups e
      extend-install-form-links (#178)`), topo de `master` em 2026-09-06:

      - `skills/code-locale/references/check-identifier-locale.py` — 942 linhas; KNOWN LIMIT 7 em
        42-47 (prosa retirada antes da análise); `COMMENT_SYNTAX` 203-213; `EXT_LANG` 215-220;
        `strip_prose()` 302-354; `is_vendored()` 397; `load_allowlist()` 405-415;
        `project_relative()` 477; `scan_text()` 556-589 (waiver na linha ou na anterior);
        `scan_diff()` 616-685; selftest 689-854; `main()` 858-937.
      - `skills/code-locale/references/programming-words.txt` (regras de linha 7-16) e
        `references/english-words.SOURCE.md` — forma dos arquivos de dados e da procedência.
      - `claude/global/hooks/locale-rite.py` — 655 linhas; `CHECK_PATH` 128; `written_text()`
        196-206; `first_line_of()` 209-228; `waiver_above()` 231-247; `findings_for()` 250-273;
        `deny_reason()` 308-335 (18 linhas por construção); `evaluate()` 350-388; selftest 391-628.
      - `claude/global/hooks/locale-stop-gate.py` — 653 linhas; `uncommitted_diff()` 233-288;
        `gating_findings()` 291-296; `evaluate()` 324-365; `_repo()` 391-399; selftest 407-626.
      - `skills/code-locale/references/pre-commit-locale.sh` — `locate_check()`, a linha do diff
        staged, o `case "$rc"` e a regra da linha `findings:`.
      - `skills/code-locale/references/ci-step.md` — o job, o pin por tag e o `sha256sum -c`.
      - `skills/code-locale/SKILL.md` — frontmatter (`version: 1.4.3`, description 996 chars),
        seções *The two layers*, *Reviewing a diff*, *Catching it at the write*, *Wire it in one
        minute*.
      - `openspec/specs/skills-catalog/spec.md:662-751`, `:846-961`, `:1406-1490` — os três
        requisitos modificados, com todos os cenários copiados no delta.
      - `openspec/config.yaml`, `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md`,
        `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py` (regras E.1-E.4, S.1-S.3),
        `scripts/validate-skill-version.py`, `scripts/validate-skills.py` (C1, C11), `generate.sh`.
      - `openspec/changes/archive/2026-09-05-enforce-locale-on-write/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md`; `openspec/changes/archive/2026-09-04-close-ci-gate-holes/` —
        forma da casa.
      - `README.md:235-420` — a seção dos hooks e a tabela *Which layer catches what*.
      - `.github/workflows/ci.yml:130-175` — os steps de selftest, onde o novo entra.
      - Corpus de calibração (somente leitura):
        `/mnt/d/DOCUMENTS/Documents/Project/WSL/mvp/editaudiotomovie/omnivoice-tts/server_addons`
        (`inference.py`, `schemas.py`, `server_app.py`, `voices.py`, `tests/*.py`), lido em
        2026-09-06.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      python3 --version                                   -> Python 3.14.5
      openspec --version                                  -> 1.6.0
      openspec new change add-prose-locale-gate --schema skills-rite
                                                          -> Created change 'add-prose-locale-gate' at openspec/changes/add-prose-locale-gate/
                                                          -> Schema: skills-rite
      python3 skills/code-locale/references/check-identifier-locale.py --selftest | tail -1
                                                          -> selftest OK: 7 content tiers fire, 16 clean cases stay silent, 6 path tiers fire, 10 path cases stay silent, 2 en-unknown tiers fire, 5 en-unknown cases stay silent
      which agentskills                                   -> (não instalado no PATH desta máquina)
      uvx --from skills-ref==0.1.1 agentskills --help     -> Usage: agentskills [OPTIONS] COMMAND [ARGS]...   (a mesma versão que o ci.yml pina)
      grep -h -n '^\s*#' server_addons/*.py | head        -> "# OmniVoice has a closed set of inline non-verbal tags that the tokenizer" [...]   (comentários em inglês, como a issue mediu)
      ```

- [x] E.3 O que não pôde ser probado

      Um item: o hook disparado pelo harness numa sessão real (`claude -p`) com um repositório
      temporário declarando `prose: pt-BR`. Este item roda num subagente, que não dispara o hook da
      sessão; a simulação alimenta os hooks por stdin com payloads na forma que o bundle 2.1.261
      declara (a mesma forma probada pela change `enforce-locale-on-write`), e a corrida real fica
      escrita em S.2 com o comando exato, para a sessão principal executar antes do merge.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #179 pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up: (1) medir strings de UI e mensagens de log — decisão registrada como KNOWN LIMIT,
      não como pendência; (2) um `--fix` que traduza — a regra de Grounding proíbe inventar
      tradução; (3) `scan_diff()` do irmão aceitar um scanner por parâmetro em vez de o detector de
      prosa ter o próprio leitor de diff — o de prosa precisa de `.md` e não precisa do tier de
      caminho, então o leitor próprio (≈40 linhas) custa menos que generalizar o do irmão; (4) o
      catálogo declarar a própria prosa — repositório misto, fica de fora por decisão da issue.

## 2. Detector de prosa, listas de palavras e tokenizador compartilhado

- [x] 2.1 `check-identifier-locale.py`: `split_prose(line, lang, state) -> (code, state, fragments)`
      com `kind` em `comment|docstring|string`; `strip_prose()` vira wrapper fino; selftest do irmão
      verde sem edição (D2). Commit `3de5bfe`.

      ```
      (old = HEAD~ strip_prose, new = split_prose wrapper, sobre todos os .py/.js/.lua/.sh/.yml do catálogo + server_addons)
      -> lines compared: 53887 in 157 files, differences: 0
      python3 skills/code-locale/references/check-identifier-locale.py --selftest | tail -1
      -> selftest OK: 7 content tiers fire, 16 clean cases stay silent, 6 path tiers fire, 10 path cases stay silent, 2 en-unknown tiers fire, 5 en-unknown cases stay silent
      ```

- [x] 2.2 `check-prose-locale.py`: importa o irmão por caminho; declaração (`.code-locale`,
      `find_declaration`, `load_declaration`, exit 2 em valor inválido); extração de
      comentários/docstrings por blocos (D3) e de parágrafos de `.md` fora de fences e frontmatter;
      limpeza e classificação (D4); waivers e allowlist; `--explain`, `--report`, `--diff -`,
      `--stdin --lang --path`, `--prose`, `--root`; KNOWN LIMIT no cabeçalho (D5). Commit `3de5bfe`.

      ```
      printf '# compute the total for the order and apply the discount\ntotal = 0\n' | python3 skills/code-locale/references/check-prose-locale.py --stdin --lang py --path orders/x.py --prose pt-BR; echo rc=$?
      -> orders/x.py:1: [gating] comment reads as en, repo prose is pt: "compute the total for the order and apply the discount"
      ->     translate it to Portuguese, or waive with a reason: `locale-ok: <reason>` on the line or the line above; or list the path in .identifier-locale-allow
      -> findings: 1
      -> rc=1
      python3 skills/code-locale/references/check-prose-locale.py --explain .        (no catálogo, sem declaração)
      -> prose locale: no .code-locale found walking up from <wt> up to <wt> (the repository root) — the prose direction is silent: 0 findings, exit 0. Declare it with a file `.code-locale` at the repository root holding `prose: pt-BR` (or pt, en, en-US).
      -> findings: 0
      ```

- [x] 2.3 `prose-words-pt.txt` (164 palavras), `prose-words-en.txt` (170), interseção vazia
      afirmada no carregamento e no selftest, e `prose-words.SOURCE.md`. Commit `3de5bfe`.

      ```
      grep -cv '^#\|^$' skills/code-locale/references/prose-words-pt.txt skills/code-locale/references/prose-words-en.txt
      -> prose-words-pt.txt:164   prose-words-en.txt:170   (interseção: [] — o selftest afirma; `do` foi removido do PT por ser inglês)
      ```

- [x] 2.4 `--selftest` com os casos de FR5 da issue: declaração ausente, PT correto, EN gating em
      comentário e em docstring, fragmento curto pulado, trecho entre aspas ignorado, linha técnica
      pulada, `.md` inglês só consultivo, waiver na linha e na linha acima, caminho na allowlist,
      `--diff` com caminho vendored pulado, `--prose` override, declaração inválida exit 2,
      interseção vazia, direção inversa (`prose: en`, comentário português -> gating). Commit `3de5bfe`.

      ```
      python3 skills/code-locale/references/check-prose-locale.py --selftest | tail -1
      -> selftest OK: 31 cases — the word lists, both directions, the skips, the waivers, the allowlist, Markdown, --diff, and the declaration through the real entry point
      ```

## 3. Hooks

- [x] 3.1 `locale-rite.py`: localiza a declaração subindo do arquivo escrito; `PreToolUse` nega
      comentário/docstring gating com as três saídas; `PostToolUse` avisa; selftest com diretório
      temporário com e sem `.code-locale`, todos os casos existentes mantidos (D6). Commit `561c855`.

      ```
      python3 claude/global/hooks/locale-rite.py --selftest | tail -1
      -> selftest OK: 13 PostToolUse decisions, 12 PreToolUse decisions, inform mode, en-unknown, the allowlist, the legacy path, the waiver above the fragment, both envelopes, the environment, the argv contract and 17 prose decisions with and without .code-locale
      ```

- [x] 3.2 `locale-stop-gate.py`: mede o diff com o detector de prosa quando a raiz declara; bloqueia
      em gating, `systemMessage` em `.md`; guarda de `stop_hook_active` mantida; selftest com
      repositório temporário com e sem `.code-locale`, todos os casos existentes mantidos (D6).
      Commit `561c855`.

      ```
      python3 claude/global/hooks/locale-stop-gate.py --selftest | tail -1
      -> selftest OK: 38 decisions in temporary git repositories (the prose direction with and without .code-locale included), 2 output shapes, 5 malformed payloads, plus the argv contract
      ```

## 4. Kit, skill e wiring do repositório

- [x] 4.1 `pre-commit-locale.sh` roda o detector de prosa sobre o diff staged quando
      `$(git rev-parse --show-toplevel)/.code-locale` existe; `ci-step.md` documenta o step extra
      e a declaração (D8). Commit `77820e9`. Exercitado num repositório temporário com o hook
      copiado para `.git/hooks/pre-commit` e `LOCALE_CHECK` apontando para o detector da worktree:

      ```
      commit 1: `prose: pt-BR`, orders/total.py com "# compute the total for the order and apply the discount"
      -> findings: 1
      -> pre-commit-locale: refused: the staged diff adds a comment or docstring that is not in the prose language .code-locale declares (code-locale).
      -> pre-commit-locale:   translate it, or waive one line:   # locale-ok: <reason>   (on the comment's line, or the one above)
      -> commits=0
      commit 2: o mesmo arquivo com "# calcula o total do pedido e aplica o desconto"      -> commits=1
      commit 3: `prose: klingon`
      -> error: <repo>/.code-locale:1: prose: 'klingon' is not a language this check knows — accepted values: pt-BR, pt, en, en-US
      -> pre-commit-locale: .code-locale could not be read (see above); fix the declaration — a gate that cannot read its own declaration must not approve
      -> commits=1
      commit 4: sem .code-locale, comentário inglês                                        -> commits=2
      bash -n skills/code-locale/references/pre-commit-locale.sh                            -> ok
      ```

- [x] 4.2 `ci.yml`: step `Prose-locale detector self-test` ao lado do de identificadores; README:
      linhas dos hooks e da tabela *Which layer catches what* mencionam a direção de prosa. Commit
      `77820e9`.

      ```
      grep -n 'Prose-locale detector self-test' .github/workflows/ci.yml   -> 156:      - name: Prose-locale detector self-test (the shipped script is itself gated)
      grep -c 'code-locale' README.md                                      -> 12
      ```

- [x] 4.3 `SKILL.md` do `code-locale`: seção *Prose follows the repository* (declaração, o que é
      medido, o que escapa, as saídas, por que o catálogo não declara); `metadata.version` 1.4.3 ->
      1.5.0; description 996/1024 sem edição; `bash generate.sh` e wrappers commitados. Commit
      `77820e9`.

      ```
      grep -n '^## Prose follows the repository\|^  version:' skills/code-locale/SKILL.md   -> 17:  version: 1.5.0 / 193:## Prose follows the repository
      python3 scripts/validate-skills.py | tail -1                                          -> skills checked: 36   findings: 0   (um C12 corrigido antes do commit: `claude/` inline virou "skill and hook trees")
      bash generate.sh                                                                      -> Generated wrappers for 36 skills [...] Generated 10 category plugins
      ```

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 Os artefatos exercitados pelo caminho real — os quatro selftests (saídas em 2.1, 2.4, 3.1,
      3.2), o detector por stdin (2.2), o pre-commit num repositório temporário (4.1), e os dois
      hooks por stdin com os payloads da issue (FR2, FR3), na forma que o bundle 2.1.261 declara,
      num diretório temporário com `.git` e `prose: pt-BR`:

      ```
      {PreToolUse, Write, orders/total.py, "# compute the total for the order and apply the discount\ndef total(x): ..."} | python3 claude/global/hooks/locale-rite.py
      -> {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "CODE-LOCALE: write denied — 1 comment or docstring not in the repository's prose language (pt, declared in .code-locale; code-locale skill). Translate, or waive with a reason:\n  orders/total.py:1: comment reads as en, repo prose is pt: \"compute the total for the order and apply the discount\"\nExits: (1) [...] (prose) the same `locale-ok: <reason>` on the comment's own line or the line above [...] (3) export LOCALE_RITE_MODE=inform [...]"}}
      -> rc=0
      {PreToolUse, Write, mesmo caminho, "# calcula o total do pedido e aplica o desconto ..."}      -> 0 bytes (mudo; a escrita cai)
      {PreToolUse, Write, mesmo caminho, "# TODO: fix lru_cache ..."}                                -> 0 bytes (curto/técnico: pulado)
      {PostToolUse, Write, NOTES.md, "This paragraph explains how the order total is computed for the customer."}
      -> {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "CODE-LOCALE (advisory): the write that just landed carries prose that reads as a language other than the one .code-locale declares [...]\n\nNOTES.md:1: [advisory] paragraph reads as en, repo prose is pt: \"This paragraph [...]
      git init no mesmo diretório; orders/total.py com o comentário inglês via printf; {Stop, stop_hook_active: false} | python3 claude/global/hooks/locale-stop-gate.py
      -> {"decision": "block", "reason": "CODE-LOCALE (stop gate): the turn is ending with uncommitted changes that carry a comment or docstring not in the prose language .code-locale declares [...]\n\norders/total.py:1: [gating] comment reads as en, repo prose is pt: \"compute the t[...]
      ```

      O que esta simulação **não** prova: o hook disparado pelo harness numa sessão real — é S.2.
- [ ] S.2 Corrida na sessão real do mantenedor (não executável por este subagente — E.3): num
      repositório temporário declarando `pt-BR`, o harness nega o `Write` com comentário inglês,
      grava o comentário português e só avisa no `.md`. Comando exato, a rodar da sessão principal
      com os hooks wired em `~/.claude/settings.json`:

      ```
      T=$(mktemp -d) && cd "$T" && git init -q && printf 'prose: pt-BR\n' > .code-locale && \
      claude -p --permission-mode acceptEdits --model sonnet \
        'Do exactly these three tool calls and nothing else, in order, then stop: (1) Write the file orders/total.py with the content "# compute the total for the order and apply the discount\ndef total(x):\n    return x\n"; (2) Write the file orders/order_total.py with the content "# calcula o total do pedido e aplica o desconto\ndef total(x):\n    return x\n"; (3) Write the file NOTES.md with the content "This paragraph explains how the order total is computed for the customer.\n". Report which calls were denied and quote the denial reason.' ; \
      ls -R "$T" ; cat "$T"/orders/*.py 2>/dev/null
      ```

      Esperado: (1) negado com `CODE-LOCALE: write denied — ... comment reads as en, repo prose is
      pt` e as saídas no motivo, `orders/total.py` ausente; (2) gravado, `orders/order_total.py`
      existe com o comentário português; (3) gravado, com `[advisory] paragraph reads as en` no
      contexto do PostToolUse (o modelo relata o aviso, não uma negação). Registrar a saída
      observada aqui e ticar.
- [x] S.3 Calibração (TR3, FR4), medida em `3de5bfe` com os limiares da issue (`MIN_WORDS=4`,
      `WRONG_MIN=2`, `STRONG_MIN=3`, `CODE_SHARE=0.5`), mantidos porque a precisão ficou acima da
      barra sem estreitar:

      | Corpus | Declaração | Gating | Consultivo | Pulados (short / code / unknown / waived) | Medidos na língua declarada | Strings (não medidas) | Arquivos pulados | Precisão adjudicada |
      |---|---|---|---|---|---|---|---|---|
      | `omnivoice-tts/server_addons` (8 `.py`, somente leitura) | `--prose pt-BR` | **42** (24 comentários, 18 docstrings: inference.py 26, voices.py 5, server_app.py 4, test_generate_kwargs.py 4, test_sanitize_text.py 2, schemas.py 1) | 7 | 7 / 1 / 10 / 0 | 6 | 419 | vendored 2 (`__pycache__`) | **42/42 = 1,00** — cada um dos 42 lido: todos são comentários ou docstrings inteiramente em inglês; nenhum falso positivo, nada excluído |
      | catálogo `skills/` + `claude/` | `--prose en` | **0** | 0 | 54 / 73 / 121 / 13 | 1336 | 2367 | no-profile 6, vendored 20 | n/a (esperado 0, obtido 0) |
      | `openspec/changes/archive` (81 changes) | `--prose pt-BR` | **0** | 1713 | 76 / 108 / 119 / 28 | 1540 | 0 | vendored 5 | n/a (esperado 0 gating, obtido 0) |

      ```
      python3 skills/code-locale/references/check-prose-locale.py --prose pt-BR --report /mnt/d/.../omnivoice-tts/server_addons; echo rc=$?
      -> findings: 42 / advisory: 7 / skipped fragments: code 1, short 7, unknown 10 / skipped files: vendored 2 / measured: 6 / strings: 419 / rc=1
      python3 skills/code-locale/references/check-prose-locale.py --prose en --report skills claude; echo rc=$?
      -> findings: 0 / skipped fragments: code 73, short 54, unknown 121, waived 13 / skipped files: no-profile 6, vendored 20 / measured: 1336 / strings: 2367 / rc=0
      python3 skills/code-locale/references/check-prose-locale.py --prose pt-BR --report openspec/changes/archive; echo rc=$?
      -> findings: 0 / advisory: 1713 / skipped fragments: code 108, short 76, unknown 119, waived 28 / measured: 1540 / rc=0
      ```

      O que se comportou diferente do esperado, e o que ficou de fora:

      - Os 1713 consultivos do archive não são falsos positivos: 958 vêm dos `specs/*/spec.md` das
        changes (o delta de spec é inglês por regra do repositório) e 755 de
        `proposal/design/tasks.md` de changes que **foram escritas em inglês** (51 em 2026-07, 632 em
        2026-08, 69 em 2026-09 — amostra de 25 e os 69 de setembro lidos: parágrafos ingleses,
        comentários HTML do template, checkboxes do template). A tier consultiva de `.md` mede o que
        está lá; o archive é misto, e é por isso que o catálogo não declara.
      - Um caso de selftest foi corrigido antes da calibração, não por ela: `# see 'the order total'
        in the docs` sobra com 4 palavras depois da limpeza (`see in the docs`) e é gating —
        correto, porque é inglês; a fixture passou a ter 3 palavras para provar o `skipped:short`.
      - Dois defeitos achados pelo selftest antes de qualquer calibração: `do` estava na lista PT
        (é inglês; removido) e um bloco `/*` aberto numa linha vazia era tratado como run de
        comentários e não como bloco (corrigido em `fragments_from_code`, que agora só junta linhas
        de comentário quando nenhum bloco abre na linha).
      - O que escapa, por desenho e declarado no cabeçalho: 419 strings em `server_addons` (log e
        erros, em inglês) não são medidas; 10 fragmentos `unknown` (só substantivos) não são
        aprovados nem reprovados. Recall parcial: dos 78 comentários ingleses que a issue contou
        linha a linha, o detector reporta 42 achados porque junta runs e blocos (um achado por
        docstring) e pula os curtos — a contagem é por fragmento, não por linha.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme no `SKILL.md` tocado (`code-locale`): name == diretório, description
      dobrada, `metadata.author solvelab`, `metadata.version 1.5.0`, categoria `process`, MIT,
      compatibility presente (490 chars) — `PASS frontmatter` no runner de gates;
      `uvx --from skills-ref==0.1.1 agentskills validate skills/code-locale` -> `Valid skill: skills/code-locale`
- [x] Q.2 Conteúdo de skill tocado em inglês: SKILL.md, detector, listas, SOURCE, kit, docstrings e
      nomes de caso do selftest; proposal/design/tasks em português, como as changes da casa. O
      próprio detector sob `--prose en` sobre `skills/` -> 0 gating (S.3)
- [x] Q.3 Gatilhos de descrição testáveis — a description não muda (996/1024, medida); "prose
      follows the repository's working language" já é gatilho da skill, e a seção nova é o corpo
      dele
- [x] Q.4 Sem doutrina duplicada: hooks, kit e README **nomeiam** `.code-locale` e as saídas e
      apontam para a seção da skill; `COMMENT_SYNTAX`, `EXT_LANG`, `WAIVER_RE`, `load_allowlist`,
      `is_vendored`, `project_relative` importados do irmão por caminho (design, Canonical Home);
      `grep -c 'COMMENT_SYNTAX = ' skills/code-locale/references/*.py` -> só o irmão define
- [x] Q.5 Identificadores em inglês no que a change introduz — `split_prose`, `MIN_WORDS`,
      `WRONG_MIN`, `STRONG_MIN`, `CODE_SHARE`, `ProseFinding`, `find_declaration`,
      `load_declaration`, `resolve_declaration`, `DECLARATION_FILE`, `MARKDOWN_SUFFIXES`,
      `prose_findings_for`, `declared_prose`, `advisory_message`:

      ```
      python3 skills/code-locale/references/check-identifier-locale.py skills/code-locale/references/check-prose-locale.py claude/global/hooks/locale-rite.py claude/global/hooks/locale-stop-gate.py
      -> findings: 0     (sem en-unknown; `MARKDOWN_EXTS` foi renomeado para `MARKDOWN_SUFFIXES` quando o hook wired apontou `EXTS` na primeira escrita)
      ```

## 7. Validation & Closure (MANDATORY)

- [x] V.1 Rodado em `77820e9`: `openspec validate add-prose-locale-gate --strict` ->
      `Change 'add-prose-locale-gate' is valid`; runner de gates (`gates.sh`, os steps de Validate
      do `ci.yml`) -> 20 linhas `PASS` (`PASS rite :: rite gate OK`, `PASS locale-rite`, `PASS
      locale-detector`, `PASS plugin-validate`, `PASS openspec-strict add-prose-locale-gate`) e
      `dirty-after: 0`; `GITHUB_EVENT_PATH=<body com Spec-rite: add-prose-locale-gate>
      SKILL_VERSION_BASE=master python3 scripts/validate-skill-version.py` -> `skill-version gate: 0
      findings (base origin/master, 1 skill(s) changed, 1 with content changes)`;
      `python3 scripts/validate-spec-rite.py` -> `spec-rite gate: 0 findings (base origin/master, 27
      changed path(s), 1 active change(s))`; `agentskills validate skills/code-locale` -> `Valid skill`
- [x] V.2 Descoberta do catálogo intacta: `ls -d skills/*/ | wc -l` -> 36; `validate-skills.py` ->
      `skills checked: 36   findings: 0`; `generate.sh` -> `Generated wrappers for 36 skills`
- [x] V.3 README / docs: seção dos hooks e tabela *Which layer catches what* mencionam a direção de
      prosa; `ci-step.md` documenta o step extra e a declaração; SKILL.md ganha a seção; wrappers
      regenerados e commitados (`77820e9`)
- [ ] V.4 `openspec archive add-prose-locale-gate --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz
