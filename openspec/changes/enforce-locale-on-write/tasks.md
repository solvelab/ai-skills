## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `80ee53c` (`docs(openspec): arquiva as changes add-skill-version-gate e
      define-cross-skill-references (#136)`), topo de `master` em 2026-09-05:

      - `claude/global/hooks/locale-rite.py` — 260 linhas; `CONTEXT_CAP = 8000` em 71;
        `written_text()` em 107-117; `first_line_of()` em 120-134 localiza o `new_string` no arquivo
        já gravado; `findings_for()` em 137-152; `report()` em 155-172 monta sempre `hookEventName:
        "PostToolUse"`; `evaluate()` em 175-193 não lê `hook_event_name`; `selftest()` em 196-259 com
        12 casos, asserção de forma e o subprocess do argv; `main()` em 262-282.
      - `skills/code-locale/references/check-identifier-locale.py` — `ALLOWLIST_FILE` em 98,
        `WAIVER_RE` em 99, `Finding`/`PathFinding` em 245-292 (`path`, `line`, `token`, `segment`,
        `tier`, `advisory`), `load_allowlist()` em 401-411 sobe do `start` até achar o arquivo,
        `scan_text()` em 552-585 aceita o waiver na própria linha ou na anterior.
      - `claude/global/personal-rules.md:39-55` — a seção *Code Locale*, a única que este item toca.
      - `openspec/specs/skills-catalog/spec.md:781-822` — o requisito *The code-locale rite is
        enforced at the moment of the write*, copiado por inteiro no delta; `:700-724` e `:726-779`
        os dois requisitos vizinhos do check.
      - `README.md:306-335` — a seção do hook (lida para não a editar: outro item a documenta).
      - `openspec/changes/archive/2026-09-04-add-hook-selftests/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md` — modelo de estilo da casa.
      - `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md`,
        `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py`,
        `scripts/validate-spec-rite.py`, `scripts/validate-skill-version.py`,
        `.github/workflows/ci.yml` — o que os gates exigem.
      - `~/.claude/skills/execute-backlog/SKILL.md`, `references/spec-rite.md`,
        `references/acceptance-tracking.md`, `~/.claude/skills/conventional-commit/SKILL.md`.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      python3 --version                -> Python 3.14.5
      openspec --version               -> 1.6.0
      openspec list                    -> No active changes found.
      which claude                     -> /home/diegops/.local/bin/claude
      readlink -f $(which claude)      -> /home/diegops/.local/share/claude/versions/2.1.261
      claude --version                 -> 2.1.261 (Claude Code)
      file <bundle>                    -> ELF 64-bit LSB executable, x86-64 [...]
      ```

      O bundle é um ELF único e o `grep` da máquina é `ugrep`, que recusa o padrão com contexto
      ("exceeds complexity limits"); os fragmentos abaixo vieram de `re.finditer` em Python sobre os
      bytes do arquivo (`scratchpad/probe.py`), contagem de ocorrências e contexto de ±220 bytes:

      ```
      permissionDecision          -> 93 ocorrências;   permissionDecisionReason -> 31;   hookEventName -> 96
      schema PreToolUse           -> c({hookEventName:C("PreToolUse"),permissionDecision:boe().optional(),
                                       permissionDecisionReason:s().optional(),updatedInput:pe(s(),se()).optional(),
                                       additionalContext:s().optional()})
      caps (caracteres)           -> AKr={reason:2000,stopReason:2000,systemMessage:4000,additionalContext:8000,
                                       permissionDecisionReason:2000}
      caps (linhas)               -> j8t=200,RKr={reason:20,stopReason:20,systemMessage:20,additionalContext:j8t,
                                       permissionDecisionReason:20}
      X5                          -> function X5(e,t,r){if(typeof r!=="string")return;let{text:o,truncated:d}=Phn(r,AKr[t],RKr[t]);
      normalização PreToolUse     -> let o=t.permissionDecision==="deny"||t.permissionDecision==="ask"; [...]
                                       let d=o?X5(e,"permissionDecisionReason",t.permissionDecisionReason):void 0,
                                       f=X5(e,"additionalContext",t.additionalContext);return{hookEventName:"PreToolUse",
                                       ...o&&{permissionDecision:t.permissionDecision},...d!==void 0&&{permissionDecisionReason:d},
                                       ...f!==void 0&&{additionalContext:f}}
      mismatch de evento          -> function PKr(e,t,r){if(t.hookEventName!==r){Ik(e,"hookSpecificOutput_event_mismatch",!0);return}
      payload de entrada          -> c({hook_event_name:C("PreToolUse"),tool_name:s(),tool_input:se(),tool_use_id:s()})
                                       sobre be=c({session_id:s(),transcript_path:s(),cwd:s(),...})
      additionalContext em Pre    -> yield{type:"additionalContext",message:{message:fn({type:"hook_additional_context",
                                       content:q.additionalContexts,hookName:`PreToolUse:${t.name}`,...,hookEvent:"PreToolUse"})}}
      ```

      Comportamento atual do hook no payload da issue (o arquivo já estaria gravado):

      ```
      printf '{"hook_event_name":"PostToolUse","tool_name":"Write","cwd":"/tmp/x","tool_input":{"file_path":"/tmp/x/servico_pedido.py","content":"def calcular_total(preco):\n    return preco\n"}}' | python3 claude/global/hooks/locale-rite.py; echo "rc=$?"
      -> {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "CODE-LOCALE: the write that just landed [...]
      -> "systemMessage": "code-locale: 4 non-English names in the last write"}
      -> rc=0
      ```

      Scaffold da change com o schema do repositório:

      ```
      openspec new change enforce-locale-on-write --schema skills-rite
      -> Created change 'enforce-locale-on-write' at openspec/changes/enforce-locale-on-write/
      -> Schema: skills-rite
      ```

- [x] E.3 O que não pôde ser probado

      Dois itens. (1) O hook real disparado pelo harness numa sessão com o bloco `PreToolUse` wired:
      este item roda num subagente, que não pode disparar o hook da sessão; a simulação alimenta o hook
      por stdin com payloads na forma que o bundle declara (E.2), e a corrida na sessão do mantenedor
      é o passo de aceite — o primeiro critério da issue fica `manual`. (2) A doc pública
      (code.claude.com/docs/en/hooks) não foi aberta nesta sessão; o texto da doc que o próprio bundle
      embute ("`permissionDecision` - "allow", "deny", or "ask" (PreToolUse only)") foi lido no ELF, e o
      bundle instalado é a fonte preferida por decisão da issue (TR1).

- [x] E.4 Checagem de escopo

      A change faz só o que a issue #137 pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up:

      - O `additionalContext` também tem cap de **linhas** (200), não registrado no docstring até
        aqui; o `report()` do `PostToolUse` só corta por caracteres. O harness corta o fim e cada
        achado é autocontido; registrado no docstring, comportamento do `PostToolUse` intocado.
      - O bundle aceita `updatedInput` em `PreToolUse` (reescrever o input da ferramenta). Renomear por
        conta do hook seria inventar uma tradução; fora, por Grounding (design, Non-Goals).
      - `README.md:306-335` mostra o matcher `Write|Edit` e só o bloco `PostToolUse`; a seção é de
        outro item, que documenta o wiring de todos os hooks — não tocado aqui.
      - Escritas via Bash continuam passando; é a issue #138 (gate de Stop), declarada como KNOWN
        LIMIT no docstring.

## 2. Envelope de negação em PreToolUse, modo inform, selftest e docstring

- [x] 2.1 `locale-rite.py`: `evaluate()` (linha 312) lê `hook_event_name`; em `PreToolUse` um achado
      gating devolve o envelope de `deny()` (300) com `hookEventName: "PreToolUse"`; só advisory, ou
      evento ausente/outro, cai em `report()` (244), intocado (D1, D4). Commit `bcfbc30`.

      ```
      printf '{"session_id":"sim","transcript_path":"/tmp/t.jsonl","cwd":"<X>","hook_event_name":"PreToolUse","tool_name":"Write","tool_use_id":"toolu_sim","tool_input":{"file_path":"<X>/servico_pedido.py","content":"def calcular_total(preco):\n    return preco\n"}}' | python3 claude/global/hooks/locale-rite.py
      -> {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "CODE-LOCALE: write denied — 3 non-English names [...]"}}
      -> rc=0        (o mesmo payload com "hook_event_name":"PostToolUse" -> additionalContext, "code-locale: 4 non-English names in the last write")
      ```

- [x] 2.2 `deny_reason()` (270): `DENY_HEADER` (153), uma linha por `(path, token)` via
      `finding_line()` (263), `+N more`, contagem de advisory, `EXITS` (161) no fim; `REASON_CAP =
      2000` e `REASON_LINE_CAP = 20` (127-128), `REASON_MAX_FINDINGS = 12` (130) (D3, D7)

      Motivo observado no exemplo da issue — `preco` em duas linhas do conteúdo vira uma:

      ```
      CODE-LOCALE: write denied — 3 non-English names in the machine layer. Identifiers, file and directory names are English (code-locale skill); comments, docstrings and strings keep the repository's language. Rename, or waive with a reason:
        servico_pedido.py: servico_pedido  [path-pt-noun: 'servico']
        servico_pedido.py:1: calcular_total  [pt-verb: 'calcular']
        servico_pedido.py:1: preco  [pt-noun: 'preco']
      Exits: (1) `# locale-ok: <reason>` on the line above the name (identifiers only — a file name has nowhere to carry it);
        (2) list the name or the path in .identifier-locale-allow (the only waiver for a file name);
        (3) export LOCALE_RITE_MODE=inform to make this hook advisory for the whole session.
      -> lines=7 chars=712
      ```

      Com 30 achados gating + 1 advisory (caso do selftest): `<= 2000` chars, `<= 20` linhas,
      `preco_0` uma vez, `(+18 more`, `(+1 unrecognised word, advisory`, termina em `EXITS[-1]`
      -> `OK      denial envelope: PreToolUse shape, <= 2000 chars, <= 20 lines, three exits last`.

- [x] 2.3 `LOCALE_RITE_MODE=inform`: `MODE_ENV`/`MODE_INFORM` (135-136), `current_mode()` (182),
      `evaluate(payload, check, mode=None)` com default do ambiente; `inform` nunca nega; qualquer
      outro valor é o modo padrão (D5)

      ```
      (mesmo payload de 2.1) | LOCALE_RITE_MODE=inform python3 claude/global/hooks/locale-rite.py     -> rc=0 chars=0   (mudo; o PostToolUse do mesmo payload -> ADVISORY chars=1608)
      (mesmo payload de 2.1) | LOCALE_RITE_MODE=informar python3 claude/global/hooks/locale-rite.py   -> rc=0 DENY chars=846   (grafia errada = modo padrão)
      ```

- [x] 2.4 `first_line_of(path, anchor)` (200): em `PreToolUse` com `Edit` a âncora é o `old_string`
      (D6); `Write` e `PostToolUse` como antes

      ```
      printf 'a = 1\nb = 2\n' > <X>/edit_target.py
      PreToolUse Edit {"old_string":"b = 2","new_string":"usuario_count = 2"} | python3 claude/global/hooks/locale-rite.py
      -> "  edit_target.py:2: usuario_count  [pt-noun: 'usuario']"      (linha 2, onde o old_string está; antes seria 1)
      ```

- [x] 2.5 Selftest (353): 13 decisões de `PostToolUse` (as 12 originais sem `hook_event_name` +
      uma nomeada), 12 de `PreToolUse`, `inform` nos dois eventos, `en-unknown` sozinho (o token é
      afirmado advisory-only antes, para o caso não passar numa escrita limpa), allowlist em
      `tempfile.TemporaryDirectory()`, envelope de negação com 30 achados, deduplicação, variável de
      ambiente por subprocess com `env`, argv

      ```
      python3 claude/global/hooks/locale-rite.py --selftest; echo "rc=$?"
      ->   OK      portuguese path reported
      ->   [...]                       (as 12 decisões originais, inalteradas)
      ->   OK      PostToolUse by name is the advisory envelope
      ->   OK      output shape is the field the harness reads (PostToolUse)
      ->   OK      PreToolUse denies a portuguese identifier
      ->   OK      PreToolUse denies a portuguese path
      ->   OK      PreToolUse denies an Edit whose new_string is portuguese
      ->   OK      PreToolUse allows the same name with locale-ok on the line above
      ->   OK      PreToolUse allows a clean write
      ->   OK      PreToolUse in inform mode never denies
      ->   OK      PreToolUse with a misspelt mode still denies
      ->   OK      PreToolUse ignores another tool
      ->   OK      PreToolUse ignores a payload without file_path
      ->   OK      PreToolUse ignores a tool_input that is not an object
      ->   OK      PreToolUse ignores a file_path that is not a string
      ->   OK      PreToolUse with a cwd that is not a string still denies
      ->   OK      inform mode: PostToolUse still carries the advisory
      ->   OK      en-unknown alone: PreToolUse silent, PostToolUse advisory
      ->   OK      PreToolUse allows a name listed in .identifier-locale-allow of the cwd
      ->   OK      denial envelope: PreToolUse shape, <= 2000 chars, <= 20 lines, three exits last
      ->   OK      denial reason names each distinct token once
      ->   OK      LOCALE_RITE_MODE=inform read from the environment through stdin
      ->   OK      unknown flag prints usage and exits 2
      ->
      -> selftest OK: 13 PostToolUse decisions, 12 PreToolUse decisions, inform mode, en-unknown, the allowlist, both envelopes, the environment and the argv contract
      -> rc=0
      ```

- [x] 2.6 Docstring (`locale-rite.py:1-106`): modos, o bloco "WHY `hookSpecificOutput.permissionDecision`
      AND NOT `exit 2`" com versão (2.1.261), comando (`re.finditer` sobre o ELF) e fragmentos
      (schema, normalização, `AKr`/`RKr`, mismatch), ao lado do probe do `additionalContext`; wiring
      com os **dois** eventos; KNOWN LIMIT das escritas via Bash (issue #138)

      ```
      grep -c -E "PreToolUse|PostToolUse" claude/global/hooks/locale-rite.py   -> 52
      grep -n "KNOWN LIMIT" claude/global/hooks/locale-rite.py                  -> 73:KNOWN LIMIT
      ```

- [x] 2.7 `personal-rules.md`, seção *Code Locale*: um bullet novo (`claude/global/personal-rules.md:55-59`,
      commit `cbeec33`) dizendo que o hook **nega** a escrita em `PreToolUse`, nomeando as três saídas
      e o limite (Bash, #138); a estrutura da seção (bullets + link final para `code-locale`) mantida

      ```
      git diff -U0 80ee53c...HEAD -- claude/global/personal-rules.md | grep -E '^@@'   -> @@ -54,0 +55,5 @@ field keys.
      ```

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato exercitado pelo caminho real — `python3 claude/global/hooks/locale-rite.py` lendo
      um payload por stdin, na forma que o bundle 2.1.261 declara (`session_id`, `transcript_path`,
      `cwd`, `hook_event_name`, `tool_name`, `tool_use_id`, `tool_input`, e `tool_response` no
      PostToolUse), 23 payloads, cada um num processo próprio (`scratchpad/sim.py`, 2026-09-05):

      ```
      python3 scratchpad/sim.py
      -> OK     1 Pre Write pt path+identifiers (issue example)            rc=0 DENY     chars=846 stderr=0
      -> OK     2 Pre Write pt identifier only                             rc=0 DENY     chars=727 stderr=0
      -> OK     3 Pre Write pt path only                                   rc=0 DENY     chars=745 stderr=0
      -> OK     4 Pre Edit pt new_string (anchor old_string, line 2)       rc=0 DENY     chars=726 stderr=0
      -> OK     5 Pre Write locale-ok on the line above                    rc=0 silent   chars=0 stderr=0
      -> OK     6 Pre Write name in .identifier-locale-allow of cwd        rc=0 silent   chars=0 stderr=0
      -> OK     7 Pre Write pt, LOCALE_RITE_MODE=inform                    rc=0 silent   chars=0 stderr=0
      -> OK     8 Post Write pt (advisory, as before)                      rc=0 ADVISORY chars=1608 stderr=0
      -> OK     9 Post Write pt, LOCALE_RITE_MODE=inform                   rc=0 ADVISORY chars=1608 stderr=0
      -> OK     10 Pre Write en-unknown only                               rc=0 silent   chars=0 stderr=0
      -> OK     11 Post Write en-unknown only                              rc=0 ADVISORY chars=726 stderr=0
      -> OK     12 Pre Write clean                                         rc=0 silent   chars=0 stderr=0
      -> OK     13 Post Write clean                                        rc=0 silent   chars=0 stderr=0
      -> OK     14 Pre MultiEdit pt                                        rc=0 DENY     chars=719 stderr=0
      -> OK     15 Pre NotebookEdit pt notebook_path                       rc=0 DENY     chars=728 stderr=0
      -> OK     16 Pre Bash writing pt (KNOWN LIMIT, must stay silent)     rc=0 silent   chars=0 stderr=0
      -> OK     17 Pre Write without file_path                             rc=0 silent   chars=0 stderr=0
      -> OK     18 malformed: json array                                   rc=0 silent   chars=0 stderr=0
      -> OK     19 malformed: json string                                  rc=0 silent   chars=0 stderr=0
      -> OK     20 malformed: empty stdin                                  rc=0 silent   chars=0 stderr=0
      -> OK     21 Pre tool_input not an object                            rc=0 silent   chars=0 stderr=0
      -> OK     22 Pre Write pt, LOCALE_RITE_MODE=informar (typo)          rc=0 DENY     chars=846 stderr=0
      -> OK     23 no hook_event_name, pt (pre-#137 payload)               rc=0 ADVISORY chars=1608 stderr=0
      -> mismatches: 0/23
      -> files in the write target after all runs: ['edit_target.py']        (só a fixture do caso 4: o hook não grava nada)
      ```

      O envelope do caso 1 e a linha do caso 4 estão em 2.1, 2.2 e 2.4. O que esta simulação **não**
      prova: o hook disparado pelo harness numa sessão com o bloco `PreToolUse` wired — um subagente
      não dispara o hook da sessão. A corrida na sessão do mantenedor (Write de `servico_pedido.py`
      negado, arquivo ausente, depois com `locale-ok:` e com `LOCALE_RITE_MODE=inform`, contando as
      tentativas até a saída) é o passo de aceite; o snippet de `settings.json` vai no resultado.

- [x] S.2 Matriz de casos em contagens, medida em S.1 e no selftest:

      | Grupo | O que tinha de acontecer | Contagem | Nota |
      |---|---|---|---|
      | stdin, PreToolUse | tinha de negar e negou | 7/7 | casos 1-4, 14, 15, 22: caminho, identificador, Edit, MultiEdit, NotebookEdit, grafia errada do modo |
      | stdin, PreToolUse | tinha de ficar mudo e ficou | 8/8 | casos 5-7, 10, 12, 17, 21 e 16: locale-ok, allowlist, inform, en-unknown, limpo, sem file_path, tool_input inválido, Bash |
      | stdin, PostToolUse | tinha de informar e informou | 4/4 | casos 8, 9, 11, 23 (o caso 9 com inform é idêntico ao 8: 1608 chars) |
      | stdin, PostToolUse | tinha de ficar mudo e ficou | 1/1 | caso 13 |
      | stdin, malformado | mudo, exit 0, sem stderr | 3/3 | casos 18-20 |
      | stdin, escape conhecido | ficou mudo | 1/1 | caso 16: Bash escrevendo `preco` (KNOWN LIMIT, issue #138) — contado também na linha dos mudos |
      | `--selftest` | decisões OK | 13/13 PostToolUse + 12/12 PreToolUse + 7/7 asserções (forma Post, inform Post, en-unknown, allowlist, envelope, deduplicação, ambiente) + 1/1 argv | rc=0 |
      | runner de gates | steps PASS | 19/19 PASS | ver V.1 |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      Nada escapou na matriz: 0/23 desvios em S.1. Duas coisas foram diferentes do planejado antes de
      medir, e estão registradas:

      - O bundle honra `additionalContext` em `PreToolUse` (E.2). A opção de emitir o `en-unknown`
        antes da escrita existe e **não** foi usada (D4): com os dois blocos wired o aviso chegaria
        duas vezes por escrita. A decisão é por duplicação, não por limite do harness.
      - O cap de `permissionDecisionReason` é duplo — 2000 caracteres **e** 20 linhas — e o
        `additionalContext` também tem cap de 200 linhas, não registrado antes. O motivo da negação
        foi desenhado para 18 linhas por construção (D3); o `render()` do check (5 linhas por achado)
        estouraria o cap de linhas com 4 achados e o harness cortaria justamente as saídas.

      O escape conhecido e mantido: um arquivo escrito por Bash (caso 16) passa em silêncio — issue
      #138. E o que continua fora do alcance da simulação por stdin é o disparo pelo harness real,
      declarado em E.3 e S.1 como passo de aceite do mantenedor.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — **não se aplica**: esta change não toca
      nenhuma skill (`git diff --stat 80ee53c...HEAD` -> `locale-rite.py`, `personal-rules.md`,
      `openspec/changes/enforce-locale-on-write/**`). O step de frontmatter do CI foi rodado mesmo
      assim pelo runner de gates: `PASS frontmatter`; `PASS validate-skills :: skills checked: 35
      findings: 0`
- [x] Q.2 Conteúdo de skill tocado em inglês — **não se aplica** pelo mesmo motivo; o docstring, os
      nomes dos casos do selftest, o motivo da negação e o delta de spec estão em inglês, como o
      catálogo exige; proposal/design/tasks em português, como as changes da casa; o bullet novo de
      `personal-rules.md` em inglês, como o resto do arquivo
- [x] Q.3 Gatilhos de descrição testáveis — **não se aplica**: nenhuma descrição de skill muda
- [x] Q.4 Sem doutrina duplicada: o motivo da negação **nomeia** as dispensas (`locale-ok:`,
      `.identifier-locale-allow`, `LOCALE_RITE_MODE=inform`) e aponta para `code-locale`; o bullet de
      `personal-rules.md` aponta para o hook e para a issue #138 sem reescrever o check; ver a tabela
      de Canonical Home em `design.md`
- [x] Q.5 Identificadores em inglês no que a change introduz — `REASON_CAP`, `REASON_LINE_CAP`,
      `REASON_MAX_FINDINGS`, `MODE_ENV`, `MODE_INFORM`, `PRE_EVENT`, `POST_EVENT`, `current_mode`,
      `split_findings`, `finding_line`, `deny_reason`, `deny`, `distinct_ok` — e o glossário da issue
      (`LOCALE_RITE_MODE`, `permissionDecision`):

      ```
      python3 skills/code-locale/references/check-identifier-locale.py claude/global/hooks/locale-rite.py
      -> findings: 0
      -> rc=0
      ```

      O próprio hook, wired em PostToolUse nesta sessão, apontou `dedup_ok  [en-unknown: 'dedup']`
      na primeira escrita do selftest; renomeado para `distinct_ok` antes do commit.

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate enforce-locale-on-write --strict` -> `Change 'enforce-locale-on-write' is valid`;
      `bash scripts/validate-rite.sh` (com `GITHUB_EVENT_PATH` apontando para um body com
      `Spec-rite: enforce-locale-on-write`) -> `rite evidence gate: 0 findings` [...] `rite gate OK`;
      `python3 scripts/validate-skill-version.py` (mesmo event, `SKILL_VERSION_BASE=master`) ->
      `skill-version gate: 0 findings (base origin/master, 0 skill(s) changed, 0 with content changes)`
- [x] V.2 Descoberta do catálogo intacta: `npx -y skills add . --list` -> `Found 35 skills`;
      `ls -d skills/*/ | wc -l` -> `35`; sem órfão ou renomeado
- [x] V.3 README / docs atualizados: a composição do catálogo não muda; `personal-rules.md` ganha o
      bullet (2.7); a seção dos hooks do `README.md:306-335` é de outro item, que documenta o wiring
      de todos os hooks, e não foi tocada aqui por decisão da issue
- [ ] V.4 `openspec archive enforce-locale-on-write --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz
