## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `80ee53c` (`docs(openspec): arquiva as changes add-skill-version-gate e
      define-cross-skill-references`), topo de `master` em 2026-09-05:

      - `claude/global/hooks/locale-rite.py` — 285 linhas; `CHECK_PATH` em 63 (import do detector por
        caminho, `parents[3]`); `evaluate()` em 164-182; `selftest()` em 185-259 com a lista
        `(nome, deve_reportar, payload)`, a asserção de forma e o caso de argv por `subprocess`;
        `main()` em 262-284 com `args == ["--selftest"]` (264) e `isinstance(payload, dict)` (276).
      - `claude/global/hooks/backlog-rite.py`, `claude/global/hooks/verify-rite.py` — o mesmo
        contrato de argv e de payload malformado (#115).
      - `skills/code-locale/references/check-identifier-locale.py` — `scan_diff()` em 612-666 (tier
        de caminho só após `--- /dev/null`, 633-641; linhas `+` agrupadas em run); `load_allowlist()`
        em 401-412; `is_vendored()` em 393 e `VENDOR_PARTS` em 386-389; `project_relative()` em
        473-486 ("root=None means the caller already handed a project-relative path (diff mode
        does)"); `advisory_for()` em 499-516 (`english is None` → sem tier `en-unknown`);
        `Finding.render()` em 252-267 e `PathFinding` em 269-296; `main()` em 828-880 — só o modo
        de caminhos aplica `is_vendored`.
      - `.github/workflows/ci.yml` — step `Locale write-gate hook self-test` em 146-147; os steps dos
        hooks irmãos em 149-153.
      - `README.md` — seção dos hooks em 235-346: `### Enforcing the rite (optional hook)` (235),
        snippet `UserPromptSubmit` (252-271), `### The grounding rite` (283), `### The locale rite`
        (306; "third hook" em 308), snippet `PostToolUse` com `"matcher": "Write|Edit"` (314-330,
        319), citação final (343-346).
      - `openspec/specs/skills-catalog/spec.md:781-822` — *The code-locale rite is enforced at the
        moment of the write*, o requisito que este delta complementa (ADDED, não MODIFIED);
        `:700` — *A shipped enforcement script declares what escapes it*.
      - `openspec/changes/archive/2026-09-04-add-hook-selftests/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md` — modelo de estilo da casa.
      - `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md`,
        `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py`,
        `scripts/validate-spec-rite.py:1-80`, `scripts/validate-skill-version.py:1-60` — o que os
        gates exigem.
      - `~/.claude/settings.json` (fora do repositório, lido para o snippet): `Stop` já carrega
        `memory-autopush.sh` (`async: true`); `PostToolUse` com matcher
        `Write|Edit|MultiEdit|NotebookEdit`; nenhum `PreToolUse` para as ferramentas de escrita.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      python3 --version                -> Python 3.14.5
      openspec --version               -> 1.6.0
      openspec list                    -> No active changes found.
      claude --version                 -> 2.1.261 (Claude Code)
      readlink -f $(which claude)      -> /home/diegops/.local/share/claude/versions/2.1.261
      file $(readlink -f $(which claude)) | cut -c1-80 -> ELF 64-bit LSB executable, x86-64  (grep precisa de -a)
      ```

      A forma da saída de Stop, no bundle (TR1). Entrada:

      ```
      grep -a -o -E '.{200}stop_hook_active.{300}' $B | head -5
      -> xoe=m(()=>be().and(c({hook_event_name:C("Stop"),stop_hook_active:P(),last_assistant_message:s().optional()[...]
      -> zoe=m(()=>be().and(c({hook_event_name:C("SubagentStop"),stop_hook_active:P(),agent_id:s(),agent_transcript_path:s(),agent_type:s()[...]
      -> [...]hook_event_name:"Stop",stop_hook_active:o,last_assistant_message:B,...q}[...]
      grep -a -c stop_hook_active $B   -> 5
      ```

      Leitura da resposta (o que decide "topo vs. aninhado"):

      ```
      grep -a -o -E 'function eg\(e\)\{.{500}' $B
      -> function eg(e){if("decision"in e&&e.decision==="block")return!0;if("continue"in e&&e.continue===!1)return!0;
      -> let t="hookSpecificOutput"in e?e.hookSpecificOutput:void 0;return t!==void 0&&typeof t==="object"&&t!==null
      -> &&"permissionDecision"in t&&(t.permissionDecision==="deny"||t.permissionDecision==="ask")}
      grep -a -o -E '.{900}return\{answer:\{\.\.\.o\.continue' $B
      -> [...]f=o.decision==="approve"?void 0:X5(r,"reason",o.reason),y=X5(r,"systemMessage",o.systemMessage),
      -> E=o.hookSpecificOutput,[...]x=v?PKr(r,E,t):void 0;return{answer:{...o.continue===!1&&{continue:!1},
      -> [...]...o.decision==="block"&&{decision:"block"},...y!==void 0&&{systemMessage:y},...f!==void 0&&{reason:f},
      -> ...x!==void 0&&{hookSpecificOutput:x}}
      grep -a -o -E 'function LU\(e,t,r\)\{.{400}' $B
      -> function LU(e,t,r){let o=X5(e,"additionalContext",r.additionalContext);return{hookEventName:t,...o!==void 0&&{additionalContext:o}}}
      -> [...]case"SubagentStop":return LU(e,"SubagentStop",t)   (e "Stop" pelo mesmo LU)
      grep -a -o -E '(AKr|RKr)=\{[^}]{0,400}\}' $B
      -> AKr={reason:2000,stopReason:2000,systemMessage:4000,additionalContext:8000,permissionDecisionReason:2000}
      -> RKr={reason:20,stopReason:20,systemMessage:20,additionalContext:j8t,permissionDecisionReason:20}
      grep -a -o -E '.{200}CLAUDE_CODE_STOP_HOOK_BLOCK_CAP.{100}' $B
      -> [...]let Od=a.CLAUDE_CODE_STOP_HOOK_BLOCK_CAP??8;if(Od>0&&Pc>Od)return[...]
      -> [...]For Stop/SubagentStop hooks, check stop_hook_active in the input and return success while it's true.
      ```

      Conclusão medida, não lida: `decision`/`reason`/`systemMessage` são lidos do **topo**;
      `hookSpecificOutput` de Stop só devolve `additionalContext` (qualquer outra chave aninhada é
      descartada sem erro); `reason` cabe em 2000 e `systemMessage` em 4000; a guarda de loop do
      bundle é 8 bloqueios seguidos. A doc (code.claude.com/docs/en/hooks) é a segunda fonte.

      Git, no repositório de sondagem (`scratchpad/probe138`, `probe-unborn.sh`):

      ```
      git ls-files --others --exclude-standard            -> sub/blob.bin  sub/servico_cliente.py
      git diff --no-index --no-color /dev/null sub/servico_cliente.py; echo rc=$?
      -> diff --git a/sub/servico_cliente.py b/sub/servico_cliente.py
      -> new file mode 100644
      -> --- /dev/null
      -> +++ b/sub/servico_cliente.py
      -> @@ -0,0 +1,2 @@
      -> +def buscar_cliente(id_usuario):
      -> rc=1                          (1 = "há diferença", não erro)
      git diff --no-index --no-color /dev/null sub/blob.bin
      -> Binary files /dev/null and b/sub/blob.bin differ     (sem +++, sem linhas +)
      git diff HEAD --no-color   (repo sem commit)
      -> fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree.   rc=128
      git rev-parse --verify -q HEAD                       -> rc=1
      git hash-object -t tree /dev/null                    -> 4b825dc642cb6eb9a060e54bf8d69288fbee4904
      git diff 4b825dc… --no-color | head -5               -> diff --git a/a.py b/a.py / new file mode / --- /dev/null / +++ b/a.py
      cd /tmp && git rev-parse --show-toplevel             -> fatal: not a git repository [...]   rc=128
      ```

      O detector, importado por caminho (`importlib`), em `80ee53c`:

      ```
      import: 12.7 ms | load_english: 109.1 ms, 369786 words
      scan_diff(<diff de servico_cliente.py>, set(), None)
      -> 4 [('servico_cliente.py', 0, 'servico_cliente', 'path-pt-noun', False), ('servico_cliente.py', 1, 'buscar_cliente', 'pt-verb', False),
      ->    ('servico_cliente.py', 1, 'id_usuario', 'pt-noun', False), ('servico_cliente.py', 2, 'id_usuario', 'pt-noun', False)]
      ```

      Scaffold da change com o schema do repositório:

      ```
      openspec new change add-locale-stop-gate --schema skills-rite
      -> Created change 'add-locale-stop-gate' at openspec/changes/add-locale-stop-gate/
      -> Schema: skills-rite
      ```

- [x] E.3 O que não pôde ser probado

      Dois itens. (1) O harness real disparando o hook num Stop de sessão: o wiring em
      `~/.claude/settings.json` é configuração pessoal fora do PR, e esta execução roda como subagente
      isolado — o payload que a simulação alimenta é construído à mão a partir do schema lido no
      bundle (`hook_event_name`, `stop_hook_active`, `cwd`, `session_id`, `transcript_path`), não
      capturado de uma sessão. (2) Que o bundle **entregue** o `reason` ao modelo como texto do turno
      seguinte: o grep mostra que `reason` é lido e guardado (`X5(r,"reason",o.reason)`) e que
      `decision:"block"` impede o encerramento (`eg`), mas o caminho do `reason` até a mensagem que o
      modelo lê não foi seguido no minificado além disso; a doc pinada diz que ele é "fed back to the
      model". Nenhum dos dois vira afirmação no docstring além do que o grep mostra.

- [x] E.4 Checagem de escopo

      A change faz só o que a issue #138 pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up:

      - `scan_diff` não aplica `is_vendored` (`check-identifier-locale.py:612-666` vs. o `main()` em
        828-880 que só o aplica ao modo de caminhos): o hook filtra os achados depois do scan (D5);
        mover o filtro para dentro do detector é edição em `skills/**`, fora do que este item possui.
      - `git diff --no-index` de um binário emite `+++`-menos "Binary files … differ": o hook pula
        binários antes de chamar o git (NUL nos primeiros 8 KiB), e um nome de binário em português
        fica declarado como limite, não medido.
      - O README ainda diz `"matcher": "Write|Edit"` (319) enquanto o `settings.json` real usa
        `Write|Edit|MultiEdit|NotebookEdit`: a seção dos hooks é reescrita aqui com o matcher
        completo, por ser o que a issue pede para o snippet; nenhuma outra seção do README é tocada.
      - Um caminho não rastreado com nome em português mas conteúdo vazio (`touch relatorio.py`):
        `git diff --no-index /dev/null` de um arquivo vazio não emite `+++`; o tier de caminho não
        dispara. Declarado como limite; não corrigido aqui.

## 2. Hook `locale-stop-gate.py`

- [ ] 2.1 Forma dos irmãos: `evaluate(payload, check, env, max_lines) -> dict | None` pura; `main()`
      só faz I/O; `args == ["--selftest"]` roda o selftest, vazio lê stdin, qualquer outro argumento
      imprime usage em stderr e sai 2; payload que não é objeto JSON → exit 0 sem saída (D1, D9)
- [ ] 2.2 Diff não commitado do topo do work tree: base `HEAD` ou árvore vazia; `git diff <base>
      --no-color`; não rastreados por `ls-files --others --exclude-standard` + `diff --no-index
      /dev/null <path>`; binários pulados; `timeout=5` por chamada; `MAX_DIFF_LINES` declarado e dito
      no motivo (D2-D4)
- [ ] 2.3 Decisão: `scan_diff` com o allowlist do topo e `english=None`; achados vendored filtrados;
      gating + `stop_hook_active` falso + modo ≠ `inform` → `{"decision": "block", "reason": …}` no
      topo, ≤ 2000; `stop_hook_active` verdadeiro → `{"systemMessage": …}` ≤ 4000; senão `None`
      (D1, D5-D8)
- [ ] 2.4 Docstring: por que Stop; a forma da saída com versão e trecho do bundle; KNOWN LIMIT
      (commit no mesmo turno, repo fora do cwd, `SubagentStop`, rename puro, binário, git lento);
      wiring; sem atribuição a IA
- [ ] 2.5 `--selftest` num repositório git em `tempfile`: novo não rastreado em pt → bloqueia;
      rastreado editado com identificador pt → bloqueia; edição limpa → mudo; cwd fora de git → mudo;
      `stop_hook_active: true` → sem bloqueio + `systemMessage`; `LOCALE_RITE_MODE=inform` → mudo;
      renomeado/`locale-ok:` → mudo; teto de linhas dito no motivo; forma da saída; malformados e
      argumento desconhecido pelo entry point real (D9)
- [ ] 2.6 Tempo medido neste repositório: diff vazio (< 1 s) e diff de 500 linhas
- [ ] 2.7 `.github/workflows/ci.yml`: step `Locale stop-gate hook self-test` logo após o step do
      `locale-rite`
- [ ] 2.8 `README.md`, seção dos hooks: snippet completo (`UserPromptSubmit`, `PreToolUse`,
      `PostToolUse` com `Write|Edit|MultiEdit|NotebookEdit` e `LOCALE_RITE_MODE=inform`, `Stop`),
      parágrafo do gate de Stop, tabela "qual camada pega o quê" (write tools → PreToolUse deny;
      Bash/heredoc/sed → Stop; outros assistentes e humanos → kit da issue #139)

## 3. Simulation & Field Proof (MANDATORY)

- [ ] S.1 O artefato foi exercitado pelo caminho real — payloads de Stop no formato do schema do
      bundle (`session_id`, `transcript_path`, `cwd`, `hook_event_name`, `stop_hook_active`) por
      stdin do entry point real, contra um repositório de rascunho com um arquivo em português gravado
      por heredoc, e depois renomeado; stdout, exit e tempos registrados
- [ ] S.2 Matriz de casos medida, em contagens
- [ ] S.3 O que escapou ou se comportou diferente do esperado

## 4. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — esta change não toca nenhuma skill; o step
      de frontmatter roda mesmo assim
- [ ] Q.2 Conteúdo de skill tocado em inglês — não se aplica; o delta de spec, o docstring, os nomes
      dos casos e o README em inglês; proposal/design/tasks em português, como as changes da casa
- [ ] Q.3 Gatilhos de descrição testáveis — não se aplica: nenhuma descrição de skill muda
- [ ] Q.4 Sem doutrina duplicada: o motivo do bloqueio cita as saídas e aponta para `code-locale`;
      o README aponta para #137 e #139 em vez de descrever o que eles implementam; tabela de
      Canonical Home em `design.md`
- [ ] Q.5 Identificadores em inglês no que a change introduz; detector rodado sobre o hook novo

## 5. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-locale-stop-gate --strict` green
- [ ] V.2 Descoberta do catálogo intacta: contagem de skills igual antes e depois; sem órfão ou
      renomeado
- [ ] V.3 README / docs atualizados: seção dos hooks com o bloco `Stop` e a tabela
- [ ] V.4 `openspec archive add-locale-stop-gate --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz
