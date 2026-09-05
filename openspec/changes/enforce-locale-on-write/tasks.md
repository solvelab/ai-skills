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

- [ ] 2.1 `locale-rite.py`: `evaluate()` lê `hook_event_name`; em `PreToolUse` um achado gating
      devolve `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
      "permissionDecisionReason": ...}}`; só advisory ou evento ausente/outro caem no envelope
      consultivo de hoje (D1, D4)
- [ ] 2.2 `deny_reason()`: cabeçalho, uma linha por achado deduplicado por `(path, token)`, `+N more`,
      contagem de advisory, as três saídas literais no fim; `REASON_CAP = 2000` e `REASON_LINE_CAP =
      20` medidos, com corte no hook preservando o rabo (D3, D7)
- [ ] 2.3 `LOCALE_RITE_MODE=inform`: `evaluate(payload, check, mode=None)` com default do ambiente;
      `inform` nunca nega; qualquer outro valor é o modo padrão (D5)
- [ ] 2.4 `first_line_of()` ancora no `old_string` em `PreToolUse` para `Edit` (D6)
- [ ] 2.5 Selftest: casos de `PreToolUse` (nega por identificador, nega por caminho, `locale-ok:`
      silencia, allowlist num cwd temporário silencia, `inform` não nega e o `PostToolUse` do mesmo
      payload informa, só `en-unknown` não nega, payload malformado mudo), forma e caps do envelope de
      negação com 30 achados, variável de ambiente pelo caminho real (subprocess), os 12 casos de
      `PostToolUse` inalterados
- [ ] 2.6 Docstring: modos, probe do `permissionDecision` ao lado do do `additionalContext` (versão,
      comando, fragmento, os dois caps), bloco de wiring com os **dois** eventos, KNOWN LIMIT das
      escritas via Bash (issue #138)
- [ ] 2.7 `personal-rules.md`, seção *Code Locale*: uma ou duas frases dizendo que a escrita é negada
      pelo hook e onde estão as saídas; estrutura da seção mantida

## 3. Simulation & Field Proof (MANDATORY)

- [ ] S.1 O artefato exercitado pelo caminho real (`python3 claude/global/hooks/locale-rite.py` lendo
      stdin) com payloads na forma do bundle, para os dois eventos; comando e fragmento observado
      registrados; a corrida na sessão com o hook wired é o passo de aceite do mantenedor
- [ ] S.2 Matriz de casos em contagens: o que tinha de negar e negou, o que tinha de ficar mudo e
      ficou, o que tinha de informar e informou, escapes conhecidos que ficaram mudos
- [ ] S.3 O que escapou ou se comportou diferente do esperado — ou a declaração de que nada escapou

## 4. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — não se aplica se nenhuma skill for tocada;
      o step do CI é rodado mesmo assim e o resultado registrado
- [ ] Q.2 Conteúdo de skill tocado em inglês — idem; docstring, nomes de caso e delta de spec em
      inglês, proposal/design/tasks em português como as changes da casa
- [ ] Q.3 Gatilhos de descrição testáveis — não se aplica se nenhuma descrição de skill muda
- [ ] Q.4 Sem doutrina duplicada: o motivo da negação **nomeia** as dispensas e aponta para
      `code-locale`; ver a tabela de Canonical Home em `design.md`
- [ ] Q.5 Identificadores em inglês no que a change introduz, medidos com o check do repositório

## 5. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate enforce-locale-on-write --strict` verde
- [ ] V.2 Descoberta do catálogo intacta: `npx skills add . --list` acha todas as skills, contagem
      esperada, sem órfão ou renomeado
- [ ] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo — a composição
      não muda; `personal-rules.md` ganha a frase (2.7); o `README.md` é de outro item
- [ ] V.4 `openspec archive enforce-locale-on-write --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz
