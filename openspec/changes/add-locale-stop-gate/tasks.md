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
        `git diff --no-index /dev/null` de um arquivo vazio não emite `+++` (medido: só `diff --git` e
        `index`, rc=1); o tier de caminho não dispara. Declarado como limite; não corrigido aqui.

## 2. Hook `locale-stop-gate.py`

- [x] 2.1 Forma dos irmãos: `evaluate(payload, check, env, max_lines) -> dict | None` pura; `main()`
      só faz I/O; `args == ["--selftest"]` roda o selftest, vazio lê stdin, qualquer outro argumento
      imprime usage em stderr e sai 2; payload que não é objeto JSON → exit 0 sem saída (D1, D9).
      Commit `a3d56fd`:

      ```
      python3 claude/global/hooks/locale-stop-gate.py --bogus </dev/null; echo "rc=$?"
      -> usage: [...]/claude/global/hooks/locale-stop-gate.py [--selftest]
      -> rc=2
      for p in '[]' '"x"' '' 'null' '{oops'; do printf '%s' "$p" | python3 claude/global/hooks/locale-stop-gate.py; echo "rc=$? chars=..."; done
      -> payload=[]    rc=0 chars=0
      -> payload="x"   rc=0 chars=0
      -> payload=''    rc=0 chars=0
      -> payload=null  rc=0 chars=0
      -> payload={oops rc=0 chars=0
      ```

- [x] 2.2 Diff não commitado do topo do work tree: `rev-parse --show-toplevel` decide se há repo e de
      onde medir; base `HEAD` se `rev-parse --verify -q HEAD` responde, senão `hash-object -t tree
      /dev/null`; `git diff <base> --no-color`; não rastreados por `ls-files --others
      --exclude-standard -z` + `diff --no-index --no-color /dev/null <path>`; NUL nos primeiros 8 KiB
      pula o arquivo; `timeout=5` por chamada; `MAX_DIFF_LINES = 4000` e o teto dito no motivo
      (D2-D4). Commit `a3d56fd`. Provado pelo selftest (2.5): "cwd in a subdirectory still measures
      the whole work tree", "repository without a commit measures staged files", "binary untracked
      file is skipped", "ignored path never enters the diff", "diff over the cap still blocks" +
      "truncation is stated in the reason" — todos `OK`.

- [x] 2.3 Decisão: `scan_diff` com `load_allowlist(<topo>)` e `english=None`; achados `advisory` e
      `is_vendored` filtrados; gating + `stop_hook_active` falso + modo ≠ `inform` →
      `{"decision": "block", "reason": …}` no topo, ≤ 2000; `stop_hook_active` verdadeiro →
      `{"systemMessage": …}` ≤ 4000; senão `None` (D1, D5-D8). Commit `a3d56fd`; `1627bf8` não toca o
      hook. Forma medida pelo entry point real (S.1):

      ```
      heredoc pt, stop_hook_active=false -> rc=0 chars=1742 keys=decision,reason
      mesmo tree, stop_hook_active=true  -> rc=0 chars=371  keys=systemMessage
      500 linhas pt                       -> rc=0 chars=2084 keys=decision,reason   (reason no cap de 2000; JSON escapa o resto)
      ```

- [x] 2.4 Docstring: por que Stop; a forma da saída com versão (`2.1.261`) e os trechos do bundle
      (`eg`, `PMe`, `LU`, `AKr`, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`); KNOWN LIMIT (commit no mesmo
      turno, repo fora do cwd, `SubagentStop`, rename puro, binário, arquivo vazio, git lento,
      consultivo); wiring; sem atribuição a IA:

      ```
      grep -c 'KNOWN LIMIT\|2.1.261\|stop_hook_active' claude/global/hooks/locale-stop-gate.py   -> 12
      grep -i -c 'co-authored\|generated with\|claude fable\|anthropic' claude/global/hooks/locale-stop-gate.py   -> 0
      ```

- [x] 2.5 `--selftest` em repositórios git criados em `tempfile` (D9). Commit `a3d56fd`:

      ```
      python3 claude/global/hooks/locale-stop-gate.py --selftest; echo "rc=$?"
      ->   OK      untracked portuguese file blocks the stop  ->  block
      ->   OK      second stop (stop_hook_active) reports and does not block  ->  message
      ->   OK      LOCALE_RITE_MODE=inform is silent  ->  silent
      ->   OK      SubagentStop payload is evaluated too  ->  block
      ->   OK      another event name is silent  ->  silent
      ->   OK      payload without cwd is silent  ->  silent
      ->   OK      cwd in a subdirectory still measures the whole work tree  ->  block
      ->   OK      renamed and translated, the stop is allowed  ->  silent
      ->   OK      tracked file edited with a portuguese identifier blocks  ->  block
      ->   OK      clean edit is silent  ->  silent
      ->   OK      locale-ok waiver on the line above is silent  ->  silent
      ->   OK      deleted tracked file is silent  ->  silent
      ->   OK      binary untracked file is skipped (declared limit)  ->  silent
      ->   OK      vendored untracked path is silent  ->  silent
      ->   OK      ignored path never enters the diff  ->  silent
      ->   OK      token in the repository allowlist is silent  ->  silent
      ->   OK      allowlist covers only what it names  ->  block
      ->   OK      repository without a commit measures staged files  ->  block
      ->   OK      diff over the cap still blocks  ->  block
      ->   OK      truncation is stated in the reason
      ->   OK      cwd outside a git work tree is silent  ->  silent
      ->   OK      block shape is top-level decision/reason within the cap, findings and exits named
      ->   OK      second-stop shape is systemMessage only, within the cap
      ->   OK      malformed payload is silent, exit 0: json array
      ->   [...]                       (json string, empty stdin, json null, not json)
      ->   OK      unknown flag prints usage and exits 2
      ->   OK      --selftest with an extra argument exits 2
      -> selftest OK: 20 decisions in temporary git repositories, 2 output shapes, 5 malformed payloads, plus the argv contract
      -> rc=0
      ```

      Duas fixtures da primeira rodada não mediam nada e foram corrigidas antes do commit: `valor_{i}`
      (o caso do teto) — `valor` está em `ENGLISH_COLLISIONS`, o caso saía `silent`; e `boleto_id` (o
      caso do allowlist) — `boleto` está em `DOMAIN_KEEP`, o caso passava sem ler o allowlist. Viraram
      `pedido_{i}` e `fatura_id`/`cobranca_total`, e o caso "allowlist covers only what it names"
      entrou para provar que o allowlist foi lido e não é um passe geral.

      O selftest fica vermelho quando uma decisão regride — cópias com um defeito injetado cada
      (`scratchpad/negative-138.sh`, `CHECK_PATH` reescrito para o absoluto):

      ```
      nested-output   (decision/reason dentro de hookSpecificOutput)   -> FAILED block shape + 7 casos "-> other"   rc=1
      blocks-twice    (ignora stop_hook_active)                          -> FAILED second stop ... -> block          rc=1
      ignores-inform  (LOCALE_RITE_MODE não lido)                        -> FAILED LOCALE_RITE_MODE=inform is silent rc=1
      silent-truncation (nota de truncamento removida)                   -> FAILED truncation is stated in the reason rc=1
      skips-untracked (ls-files ignorado)                                -> FAILED untracked portuguese file blocks + 8  rc=1
      control (só CHECK_PATH reescrito)                                  -> selftest OK: 20 decisions [...]            rc=0
      ```

- [x] 2.6 Tempo medido pelo entry point real (`date +%s%N` em volta do `python3`, payload por stdin),
      commit `a3d56fd`:

      ```
      repo de rascunho, tree limpa (diff vazio)        -> rc=0 ms=44 chars=0
      repo de rascunho, cwd fora de git                -> rc=0 ms=41 chars=0
      repo de rascunho, heredoc pt (bloqueia)          -> rc=0 ms=47 chars=1742
      repo de rascunho, 500 linhas pt (bloqueia)       -> rc=0 ms=55 chars=2084
      este repositório (worktree), tree limpa, 3 runs  -> rc=0 ms=67 / 63 / 64 chars=0
      ```

      Todos abaixo de 1 s (FR4); `load_english` (109 ms medido em E.2) fica de fora por D5.

- [x] 2.7 `.github/workflows/ci.yml`: step `Locale stop-gate hook self-test` logo após o step do
      `locale-rite`. Commit `44a6597`:

      ```
      git diff 80ee53c...HEAD -- .github/workflows/ci.yml | grep '^+' | grep -v '^+ *#'
      -> +      - name: Locale stop-gate hook self-test (the shipped hook is itself gated)
      -> +        run: python3 claude/global/hooks/locale-stop-gate.py --selftest
      ```

- [x] 2.8 `README.md`, seção dos hooks (235-410 depois da edição), commit `1627bf8`: snippet completo
      com `UserPromptSubmit` (backlog-rite, verify-rite), `PreToolUse` e `PostToolUse` com matcher
      `Write|Edit|MultiEdit|NotebookEdit` e a menção a `LOCALE_RITE_MODE=inform`, `Stop`
      (locale-stop-gate); parágrafo do gate de Stop com a forma probada no bundle e o
      `stop_hook_active`; tabela "Which layer catches what":

      ```
      grep -n '^### \|^| ' README.md | grep -i 'enforcing\|grounding\|locale rite\|What wrote\|Write. /\|Bash —\|another assistant'
      -> 235:### Enforcing the rite (optional hooks)
      -> 321:### The grounding rite (anti-achismo)
      -> 344:### The locale rite, at the write (English machine layer, measured on the tool call)
      -> 366:### The locale rite, at the end of the turn (the Stop gate)
      -> 400:| What wrote the name | Layer that catches it | Effect |
      -> 402:| `Write` / `Edit` / `MultiEdit` / `NotebookEdit` | `locale-rite.py` on `PreToolUse` (#137) | the write is **denied**; nothing reaches the disk |
      -> 403:| Bash — heredoc, `sed -i`, a script, a generator | `locale-stop-gate.py` on `Stop` | the **turn does not end** until the diff is clean or waived |
      -> 404:| another assistant (Codex, Cursor, Copilot), or a human commit | the per-repository kit of the [`code-locale`](skills/code-locale/) skill — pre-commit hook and CI step (issue #139) | the **commit or the pull request** fails |
      ```

      O `PreToolUse` que nega é entregue pela issue #137 em paralelo; o README descreve o wiring e
      aponta para a issue em vez de descrever a implementação dela (Q.4).

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi exercitado pelo caminho real — payloads de Stop no formato do schema do
      bundle, por stdin do entry point real, contra um repositório de rascunho
      (`scratchpad/sim-138.sh`, commit `a3d56fd` do hook)

      Payload, construído do schema lido em E.2:
      `{"session_id":"sim-138","transcript_path":"<S>/transcript.jsonl","cwd":"<repo>","permission_mode":"default","hook_event_name":"Stop","stop_hook_active":false}`.
      Repositório: `git init -b main`, `shipping.py` limpo commitado. Depois, **exatamente o heredoc
      da issue**, sem ferramenta de escrita:

      ```
      cat > servico_cliente.py <<'EOF'
      def buscar_cliente(id_usuario):
          return id_usuario
      EOF
      payload | python3 claude/global/hooks/locale-stop-gate.py
      -> rc=0  ms=47  chars=1742  keys=decision,reason
      -> CODE-LOCALE (stop gate): the turn is ending with uncommitted changes that carry a non-English name in the machine layer. [...]
      -> servico_cliente.py: servico_cliente  [path-pt-noun: 'servico']
      -> servico_cliente.py:1: buscar_cliente  [pt-verb: 'buscar']
      -> [...] id_usuario ×2, Exits: `# locale-ok: <reason>` [...] `.identifier-locale-allow` [...] `LOCALE_RITE_MODE=inform` [...]
      mesmo tree, "stop_hook_active":true
      -> rc=0  ms=42  chars=371  keys=systemMessage
      -> code-locale: the turn is ending with 4 non-English names still uncommitted (second Stop — not blocking again; rename or waive before committing):
      ->   servico_cliente.py: servico_cliente  [path-pt-noun]
      ->   servico_cliente.py:1: buscar_cliente  [pt-verb]
      ->   [...]
      mv servico_cliente.py customer_service.py; sed -i 's/buscar_cliente/find_customer/; s/id_usuario/user_id/g' customer_service.py
      -> rc=0  ms=43  chars=0                                     (FR2: renomeado, o turno encerra)
      sed -i 's/order_id/id_pedido/g' shipping.py                 (rastreado editado por sed)
      -> rc=0  ms=42  chars=856  keys=decision,reason
      -> shipping.py:1: id_pedido  [pt-noun: 'pedido']
      LOCALE_RITE_MODE=inform, com servico_cliente.py de volta   -> rc=0 chars=0
      cwd fora de git (<S>/nowhere, com servico.py em pt dentro) -> rc=0  ms=41  chars=0
      tree limpa                                                  -> rc=0  ms=44  chars=0
      500 linhas pt (lista_pedidos.py)                            -> rc=0  ms=55  chars=2084  keys=decision,reason
      malformados [] "x" '' null {oops                            -> rc=0 chars=0 ×5
      --bogus                                                     -> usage: [...] [--selftest]   rc=2
      este worktree, tree limpa, 3 runs                           -> rc=0 ms=67 / 63 / 64 chars=0
      ```

- [x] S.2 Matriz de casos medida, em contagens

      | Artefato | Expectativa | Casos | Resultado |
      |---|---|---|---|
      | entry point real (stdin, repo de rascunho) | tinha de bloquear e bloqueou | 3/3 | heredoc pt, rastreado editado por sed, 500 linhas pt |
      | entry point real (stdin) | tinha de ficar mudo e ficou | 4/4 | renomeado+traduzido, modo inform, fora de git, tree limpa |
      | entry point real (stdin) | `stop_hook_active` → mensagem sem bloqueio | 1/1 | keys=systemMessage |
      | entry point real (stdin) | payload malformado mudo, exit 0 | 5/5 | `[]`, `"x"`, vazio, `null`, `{oops` |
      | entry point real (argv) | argumento desconhecido sai 2 com usage | 1/1 | `--bogus` |
      | entry point real (tempo) | abaixo de 1 s | 10/10 | 41-75 ms, inclusive neste repositório |
      | `--selftest` | decisões OK | 20/20 + 2/2 formas + 5/5 malformados + 2/2 argv | rc=0 |
      | `--selftest` (cópias com defeito injetado) | tinha de ficar vermelho e ficou | 5/5 | nested-output, blocks-twice, ignores-inform, silent-truncation, skips-untracked — rc=1 cada |
      | `--selftest` (cópia de controle) | tinha de ficar verde e ficou | 1/1 | rc=0 |
      | escapes conhecidos | ficaram mudos, como declarado | 2/2 | binário em pt pulado; vendored em pt filtrado (ver S.3) |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      Três coisas se comportaram diferente do escrito na primeira rodada, nenhuma no hook entregue:

      - Duas fixtures do selftest não mediam nada (`valor_{i}` é colisão com inglês; `boleto` está em
        `DOMAIN_KEEP`) — o caso do teto saía `silent` e o do allowlist passava sem ler o allowlist.
        Corrigidas antes de `a3d56fd` (2.5). Lição registrada: um caso que "passa" com o mecanismo
        desligado não prova o mecanismo; por isso entrou o caso "allowlist covers only what it names".
      - O passo de rename da simulação usava `git mv -k` num arquivo não rastreado: `-k` engole o erro
        e sai 0, o `||` nunca rodou, e o caso "renomeado" continuou bloqueando porque o arquivo em
        português seguia lá. Defeito do script de simulação, trocado por `mv`; rerodado, `chars=0`.
      - A `systemMessage` do segundo Stop imprimia `servico_cliente.py:0` para o achado de caminho
        (`PathFinding` carrega `line=0`); passou a imprimir só o caminho. Cosmético, dentro de
        `a3d56fd`.

      Escapes conhecidos e mantidos de propósito, todos declarados no docstring: um binário com nome em
      português (`relatorio.bin`) é pulado e o nome não é medido; um arquivo **vazio** não rastreado
      não recebe `+++` do git e o nome não é medido (probado em E.2/E.4); um arquivo em português
      movido sem edição é rename para o git e não dispara; um `git` que estoura `timeout=5` deixa o
      hook mudo. O que a simulação **não** prova: o harness real disparando o hook num Stop de sessão
      e entregando o `reason` ao modelo — o wiring é configuração pessoal fora do PR e esta execução
      roda como subagente isolado (E.3); o payload foi construído do schema do bundle, não capturado.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — **não se aplica**: esta change não toca
      nenhuma skill. O step de frontmatter rodou mesmo assim pelo runner de gates: `PASS frontmatter`;
      `python3 scripts/validate-skills.py -> skills checked: 35   findings: 0`
- [x] Q.2 Conteúdo de skill tocado em inglês — **não se aplica** pelo mesmo motivo; o delta de spec, o
      docstring, os nomes dos casos do selftest, o step de CI e a seção do README estão em inglês, como
      o catálogo exige; proposal/design/tasks em português, como as changes da casa
- [x] Q.3 Gatilhos de descrição testáveis — **não se aplica**: nenhuma descrição de skill muda
- [x] Q.4 Sem doutrina duplicada: o motivo do bloqueio lista as três saídas e aponta para a skill
      `code-locale` ("Doctrine: the code-locale skill") em vez de reescrever a regra; o README descreve
      o **wiring** do PreToolUse e aponta para #137, e aponta para #139 na terceira linha da tabela em
      vez de descrever o kit; tabela de Canonical Home em `design.md`
- [x] Q.5 Identificadores em inglês no que a change introduz — `evaluate`, `run_git`, `is_binary`,
      `uncommitted_diff`, `gating_findings`, `capped`, `block_reason`, `remaining_message`,
      `MAX_DIFF_LINES`, `GIT_TIMEOUT`, `REASON_CAP`, `SYSTEM_MESSAGE_CAP`, `STOP_EVENTS`, `MODE_VAR`;
      o nome do arquivo vem do glossário da issue (`locale-stop-gate.py`):

      ```
      python3 skills/code-locale/references/check-identifier-locale.py claude/global/hooks/locale-stop-gate.py
      -> findings: 0
      ```

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-locale-stop-gate --strict` -> `Change 'add-locale-stop-gate' is valid`;
      `bash scripts/validate-rite.sh` -> `rite evidence gate: 0 findings` / `spec-rite gate: 0
      findings` / `Totals: 3 passed, 0 failed (3 items)` / `rite gate OK`
- [x] V.2 Descoberta do catálogo intacta: `ls -d skills/*/ | wc -l` -> `35` antes e depois (nenhum
      `skills/**` tocado — `git diff --stat 80ee53c...HEAD` lista 8 arquivos, nenhum sob `skills/`);
      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`;
      `claude plugin validate . --strict` -> `✔ Validation passed`; `bash generate.sh` deixa a árvore
      limpa (`PASS tree-clean-after-generate`). `npx skills add . --list` não foi rodado nesta execução
      (subagente isolado, sem rede garantida); a contagem local e o validador de hygiene, que mede as
      contagens publicadas, cobrem o que ele mediria.
- [x] V.3 README / docs atualizados: `README.md:235-410` reescrita com o snippet completo, o parágrafo
      do gate de Stop e a tabela (2.8); a composição do catálogo não muda
- [ ] V.4 `openspec archive add-locale-stop-gate --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz
