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

      Relidos em `11c416d` (topo do branch antes da rodada de revisão, 2026-09-05):

      - `claude/global/hooks/locale-stop-gate.py` — `run_git()` 151-158 sem flag de forma;
        `uncommitted_diff()` 169-217 (`diff <base> --no-color` em 198, `diff --no-index --no-color`
        em 212; `is_binary` antes do git, vendored só depois do scan); `evaluate()` 253-286 — o
        `if not findings: return None` em 282 descartava `truncated`; `_fixture_env()` 295-304 com
        `GIT_CONFIG_GLOBAL=os.devnull` (toda decisão provada só sob config em branco).
      - `skills/code-locale/references/check-identifier-locale.py:638-643` — `scan_diff` guarda o
        caminho do `+++` com as aspas que o git imprime; `EXT_LANG.get(Path(path).suffix.lower())`
        com sufixo `.py"` → `None`, e as linhas `+` não são lidas.
      - `claude/global/hooks/locale-rite.py` neste branch —
        `grep -n 'LOCALE_RITE_MODE\|PreToolUse\|permissionDecision'` → nada, rc=1: não há caminho de
        PreToolUse aqui.
      - Worktree irmão da issue #137 (`.claude/worktrees/wf_3d89aff2-ea2-1`, `17fc01f`, não mergeado,
        só leitura) — `locale-rite.py:84,90` `"matcher": "Write|Edit|MultiEdit|NotebookEdit"`; `:135`
        `MODE_ENV = "LOCALE_RITE_MODE"`; `:306` `"permissionDecision": "deny"`. O wiring que o README
        descreve bate com o código da #137, lido e não presumido.
      - `README.md:352-354, 362-363, 402` (em `11c416d`) — afirmavam a negação em PreToolUse como
        fato presente.

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

      Rodada de revisão — o `~/.gitconfig` do usuário e a forma do diff (git 2.47.3; repositório de
      sondagem `scratchpad/repro138`, `shipping.py` rastreado editado por
      `sed -i 's/order_id/id_pedido/g'`; hook em `11c416d`, antes da correção):

      ```
      GIT_CONFIG_GLOBAL=<[diff] external = /bin/true>   git diff HEAD --no-color | wc -l     -> 0
      mesmo gitconfig, payload de Stop | locale-stop-gate.py                                -> rc=0 chars=0
      GIT_CONFIG_GLOBAL=/dev/null (controle, mesma árvore)                                  -> rc=0 chars=856 keys=decision,reason
      GIT_CONFIG_GLOBAL=<[diff] mnemonicPrefix = true>  git diff HEAD --no-color | sed -n 3,4p -> --- c/shipping.py / +++ w/shipping.py
      mesmo gitconfig, hook                        -> reason: `w/shipping.py:1: id_pedido  [pt-noun: 'pedido']`
      git diff --no-index --no-color /dev/null 'serviço.py'   (core.quotePath padrão)
      -> diff --git "a/servi\303\247o.py" "b/servi\303\247o.py"             hook -> rc=0 chars=0
      git -c core.quotePath=false diff --no-index --no-color /dev/null 'serviço.py'
      -> diff --git a/serviço.py b/serviço.py
      rastreado relatório.py editado: git diff HEAD --no-color | sed -n 3,4p
      -> --- "a/relat\303\263rio.py" / +++ "b/relat\303\263rio.py"           hook -> rc=0 chars=0
      GIT_CONFIG_GLOBAL=<noprefix + external + mnemonicPrefix + relative + color.ui=always>:
        git diff HEAD | sed -n 1,4p                                                         -> (vazio)
        git -c core.quotePath=false diff --no-ext-diff --no-textconv --no-color --src-prefix=a/ --dst-prefix=b/ HEAD | sed -n 1,4p
        -> diff --git a/shipping.py b/shipping.py / index 0c0b18e..fa663ce 100644 / --- a/shipping.py / +++ b/shipping.py
      GIT_EXTERNAL_DIFF=true git diff --no-color HEAD | wc -l -> 0;   com --no-ext-diff -> 8
      .gitattributes `*.py diff=pyx` + -c diff.pyx.command=true: | wc -l -> 0;   com --no-ext-diff -> 8
      .gitattributes + -c 'diff.pyx.textconv=tr a-z A-Z <'  -> -DEF COMPUTE_SHIPPING(ORDER_ID): / +DEF COMPUTE_SHIPPING(ID_PEDIDO):
        com --no-textconv                                    -> -def compute_shipping(order_id): / +def compute_shipping(id_pedido):
      git -c diff.relative=true diff --no-relative --no-color HEAD | wc -l -> 8      (flag aceita no 2.47.3)
      git -c core.quotePath=false diff --no-index /dev/null 'we"ird.py' | sed -n 4p -> --- /dev/null  (o `+++` segue citado: limite)
      ```

      O teto (`scratchpad/repro138b`, hook em `11c416d`; `servico_cliente.py` em português em todos os
      casos, ordenando depois do conteúdo limpo):

      ```
      controle: só servico_cliente.py                               -> rc=0 ms=43   chars=1742 (bloqueia)
      A: aaa_generated.py, 5000 linhas `value_i = i`, não rastreado  -> rc=0 ms=121  chars=0
      B: 5000 linhas anexadas ao shipping.py rastreado               -> rc=0 ms=124  chars=0
      C: build/gen.py 5000 linhas, não ignorado                      -> rc=0 ms=135  chars=0
      H: 1500 arquivos vazios em build/                              -> rc=0 ms=1721 chars=0
      git diff --no-index --no-color /dev/null build/f1.py (vazio)   -> diff --git / new file mode / index 0000000..e69de29   rc=1  (3 linhas, sem +++)
      detector em memória, scan_diff: 4000 linhas limpas -> 83 ms; 20000 -> 442 ms
      ```

      O `locale-rite.py` deste branch num payload de PreToolUse, e o que o bundle faz com a resposta:

      ```
      printf '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"/tmp/servico.py","content":"def buscar_cliente(id_usuario):..."}}' | python3 claude/global/hooks/locale-rite.py
      -> {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "CODE-LOCALE: the write that just landed [...]   rc=0
      grep -a -o -E 'function PKr\(e,t,r\)\{.{80}' $B
      -> function PKr(e,t,r){if(t.hookEventName!==r){Ik(e,"hookSpecificOutput_event_mismatch",!0);return}swit
      grep -a -c hookSpecificOutput_event_mismatch $B   -> 2
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
        `index`, rc=1); o tier de caminho não dispara. Declarado como limite; agora o arquivo vazio é
        pulado antes do git (não consome teto nem processo), com o mesmo efeito no nome.
      - O detector guarda as aspas do `+++` (`scan_diff`, 638-643): com `core.quotePath` padrão um
        caminho não ASCII vira `"b/relat\303\263rio.py"` e o sufixo `.py"` não casa linguagem. O hook
        contorna com `-c core.quotePath=false`; desfazer as aspas e o octal dentro do detector é
        edição em `skills/**` — anotado para a issue #139, cujo kit lê diffs de outros produtores.
      - Um caminho com aspas duplas, barra invertida ou caractere de controle continua citado pelo
        git mesmo com `quotePath=false` (medido: `'we"ird.py'` → `+++` citado) e não é medido.
        Declarado no docstring; não corrigido aqui.
      - Falso positivo do modo `--diff` do detector, observado no próprio hook: rodado contra este
        worktree com o docstring editado e ainda não commitado, o gate bloqueou por `relatório` e
        `relatorio` nas linhas 59, 92 e 96 do docstring (`rc=0 chars=1548 keys=decision,reason`) —
        o run de linhas `+` começa dentro do docstring, não carrega o `"""` de abertura e é lido como
        código; no arquivo inteiro o mesmo detector devolve `findings: 0`. Mesma família da issue
        #85; o bloqueio dura enquanto a edição está não commitada. Detector-side (`skills/**`):
        follow-up, não corrigido aqui.

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
      /dev/null`; toda chamada como `git --no-pager -c core.quotePath=false`, e os dois diffs com
      `--no-ext-diff --no-textconv --no-color --no-relative --src-prefix=a/ --dst-prefix=b/`
      (D10); não rastreados por `ls-files --others --exclude-standard -z` + `diff --no-index
      /dev/null <path>`, pulando ANTES do git o que o detector chama de vendored, o arquivo vazio e o
      binário (NUL nos primeiros 8 KiB); `timeout=5` por chamada; `MAX_DIFF_LINES = 4000` e o teto
      dito sempre (D2-D4). Commits `a3d56fd` e `e8c1f1d`:

      ```
      grep -n 'GIT_PIN = \|DIFF_FLAGS = \|\*GIT_PIN\|\*DIFF_FLAGS\|vendored(Path(rel))\|st_size == 0' claude/global/hooks/locale-stop-gate.py
      -> 153:GIT_PIN = ["--no-pager", "-c", "core.quotePath=false"]
      -> 154:DIFF_FLAGS = ["--no-ext-diff", "--no-textconv", "--no-color", "--no-relative",
      -> 214:        run = subprocess.run(["git", *GIT_PIN, *args], cwd=cwd, env=env, capture_output=True,
      -> 225:        if path.stat().st_size == 0:
      -> 267:    tracked = run_git(["diff", *DIFF_FLAGS, base], root, env)
      -> 279:        if vendored is not None and vendored(Path(rel)):
      -> 283:        added = run_git(["diff", *DIFF_FLAGS, "--no-index", "/dev/null", rel], root, env)
      ```

      Provado pelo selftest (2.5): "cwd in a subdirectory still measures the whole work tree",
      "repository without a commit measures staged files", "binary untracked file is skipped",
      "ignored path never enters the diff", "diff over the cap still blocks" + "truncation is stated
      in the reason", "diff.external, mnemonicPrefix, relative and color.ui do not silence the gate",
      "untracked file with a non-ASCII name is measured", "tracked file with a non-ASCII name edited
      in place is measured", "unignored vendored and empty files do not eat the cap" — todos `OK`; e
      pelo entry point real em S.1 (gitconfig ligado, `GIT_EXTERNAL_DIFF`, `serviço.py`,
      `relatório.py`).

- [x] 2.3 Decisão: `scan_diff` com `load_allowlist(<topo>)` e `english=None`; achados `advisory` e
      `is_vendored` filtrados; gating + `stop_hook_active` falso + modo ≠ `inform` →
      `{"decision": "block", "reason": …}` no topo, ≤ 2000; `stop_hook_active` verdadeiro →
      `{"systemMessage": …}` ≤ 4000; sem achado e teto atingido → bloqueio único com
      `UNMEASURED_REASON` (a cauda NÃO foi medida, como medir) e `UNMEASURED_MESSAGE` no Stop
      seguinte (D4, revisado); senão `None` (D1, D5-D8). Commits `a3d56fd` e `e8c1f1d`. Forma medida
      pelo entry point real (S.1):

      ```
      heredoc pt, stop_hook_active=false                 -> rc=0 chars=1742 keys=decision,reason
      mesmo tree, stop_hook_active=true                  -> rc=0 chars=371  keys=systemMessage
      500 linhas pt                                       -> rc=0 chars=2084 keys=decision,reason   (reason no cap de 2000; JSON escapa o resto)
      5000 linhas limpas antes de servico_cliente.py     -> rc=0 chars=770  keys=decision,reason   "the uncommitted diff is longer than 4000 lines [...] NOT measured"
      mesmo tree, stop_hook_active=true                  -> rc=0 chars=358  keys=systemMessage     "longer than 4000 lines; the part past the cap was NOT measured"
      ```

- [x] 2.4 Docstring: por que Stop; a forma da saída com versão (`2.1.261`) e os trechos do bundle
      (`eg`, `PMe`, `LU`, `AKr`, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`); por que a forma do diff é fixada
      contra o gitconfig (com as medições da revisão); por que o teto nunca passa mudo; KNOWN LIMIT
      (commit no mesmo turno, repo fora do cwd, `SubagentStop`, rename puro, binário e vazio pulados,
      nome com aspas/controle, git lento, consultivo); `LOCALE_RITE_MODE` como a variável que a #137
      dá ao gate de escrita — este hook é o único leitor até ela entrar; wiring; sem atribuição a IA.
      Commits `a3d56fd` e `e8c1f1d`:

      ```
      grep -n '^WHY \|^KNOWN LIMIT' claude/global/hooks/locale-stop-gate.py
      -> 10:WHY A STOP HOOK WHEN A WRITE HOOK ALREADY EXISTS
      -> 19:WHY `{"decision": "block", "reason": ...}` AT THE TOP LEVEL AND NOTHING NESTED
      -> 45:WHY THE DIFF SHAPE IS PINNED AGAINST THE USER'S GIT CONFIG
      -> 64:WHY A TRUNCATED DIFF IS NEVER A SILENT PASS
      -> 77:WHY `stop_hook_active` NEVER BLOCKS TWICE
      -> 83:KNOWN LIMIT — what this hook does NOT see
      grep -c 'KNOWN LIMIT\|2.1.261\|stop_hook_active' claude/global/hooks/locale-stop-gate.py   -> 14
      grep -i -c 'co-authored\|generated with\|claude fable\|anthropic' claude/global/hooks/locale-stop-gate.py   -> 0
      ```

- [x] 2.5 `--selftest` em repositórios git criados em `tempfile` (D9), com a fixture de gitconfig
      de D10. Commits `a3d56fd` e `e8c1f1d`:

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
      ->   OK      clean diff over the cap blocks once and says the tail was not measured
      ->   OK      clean diff over the cap on the second stop reports and does not block  ->  message
      ->   OK      clean lines ahead of a portuguese file never make it a silent pass  ->  block
      ->   OK      unignored vendored and empty files do not eat the cap ahead of a portuguese file  ->  block
      ->   OK      the portuguese file is measured with no truncation note (cap untouched)
      ->   OK      diff.external, mnemonicPrefix, relative and color.ui do not silence the gate  ->  block
      ->   OK      the finding names the repository path, not w/ or a bare one
      ->   OK      untracked file with a non-ASCII name is measured, name and content  ->  block
      ->   OK      the non-ASCII path is reported unquoted, with its identifiers
      ->   OK      tracked file with a non-ASCII name edited in place is measured  ->  block
      ->   OK      cwd outside a git work tree is silent  ->  silent
      ->   OK      block shape is top-level decision/reason within the cap, findings and exits named
      ->   OK      second-stop shape is systemMessage only, within the cap
      ->   OK      malformed payload is silent, exit 0: json array
      ->   [...]                       (json string, empty stdin, json null, not json)
      ->   OK      unknown flag prints usage and exits 2
      ->   OK      --selftest with an extra argument exits 2
      -> selftest OK: 26 decisions in temporary git repositories, 2 output shapes, 5 malformed payloads, plus the argv contract
      -> rc=0
      ```

      Duas fixtures da rodada de revisão também não mediam nada na primeira escrita e foram corrigidas
      antes de `e8c1f1d`: o repositório da fixture de gitconfig chamava-se `gitconfig`, o mesmo nome
      do arquivo (`NotADirectoryError`); e os 60 arquivos vazios estavam em `build/`, onde o pulo de
      vendored os engolia antes do pulo de tamanho — o mutante "vazio não pulado" ficava verde. Foram
      para `orders/`. `diff.noprefix` saiu da fixture de propósito: sobrepõe o `mnemonicPrefix` e
      deixava verde o mutante sem `--src-prefix/--dst-prefix` (D10).

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

      Mutantes da rodada de revisão (`scratchpad/negative-138b.py`, um fix removido por cópia, hook
      em `e8c1f1d`):

      ```
      control                    rc=0 FAILED=0
      no-ext-diff                rc=1 FAILED=5 :: diff.external, mnemonicPrefix, relative and color.ui do not silence the gate -> silent | the finding names the repository path [...]
      no-prefix-pin              rc=1 FAILED=1 :: the finding names the repository path, not w/ or a bare one
      no-quotepath               rc=1 FAILED=2 :: the non-ASCII path is reported unquoted [...] | tracked file with a non-ASCII name edited in place is measured -> silent
      vendored-after-scan        rc=1 FAILED=1 :: the portuguese file is measured with no truncation note (cap untouched)
      empty-not-skipped          rc=1 FAILED=1 :: the portuguese file is measured with no truncation note (cap untouched)
      silent-clean-truncation    rc=1 FAILED=3 :: clean diff over the cap blocks once and says the tail was not measured | [...] second stop [...] -> silent
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

      Depois de `e8c1f1d` (`scratchpad/sim138b`, mesmo método):

      ```
      heredoc pt (bloqueia)                                         -> rc=0 ms=46  chars=1742
      renomeado+traduzido                                           -> rc=0 ms=42  chars=0
      gitconfig external+mnemonic+quotePath+color, sed no rastreado -> rc=0 ms=44  chars=856
      untracked serviço.py                                          -> rc=0 ms=50  chars=1731
      5000 linhas limpas antes do arquivo pt (bloqueio "not measured") -> rc=0 ms=125 chars=770
      build/gen.py 5000 linhas não ignorado + arquivo pt            -> rc=0 ms=43  chars=1742   (antes: 135 ms e mudo)
      1500 arquivos vazios em gen/ + arquivo pt                     -> rc=0 ms=60  chars=1742   (antes, em build/: 1721 ms e mudo)
      tree limpa / cwd fora de git                                  -> rc=0 ms=42 / 45 chars=0
      este worktree, 3 runs                                         -> rc=0 ms=60 / 60 / 67
      ```

      Todos abaixo de 1 s (FR4); `load_english` (109 ms medido em E.2) fica de fora por D5.

- [x] 2.7 `.github/workflows/ci.yml`: step `Locale stop-gate hook self-test` logo após o step do
      `locale-rite`. Commit `44a6597`:

      ```
      git diff 80ee53c...HEAD -- .github/workflows/ci.yml | grep '^+' | grep -v '^+ *#'
      -> +      - name: Locale stop-gate hook self-test (the shipped hook is itself gated)
      -> +        run: python3 claude/global/hooks/locale-stop-gate.py --selftest
      ```

      `9dd5e83` só muda o comentário do step, para nomear o que o selftest passou a cobrir:

      ```
      git diff 11c416d...HEAD -- .github/workflows/ci.yml | grep '^[+-] '
      -> -        # Stop (stop_hook_active) reports without blocking. Needs only python3 and git.
      -> +        # Stop (stop_hook_active) reports without blocking, a ~/.gitconfig with diff.external or
      -> +        # mnemonicPrefix does not silence it, a non-ASCII file name is measured, and a diff over the
      -> +        # cap is never a silent pass. Needs only python3 and git.
      ```

- [x] 2.8 `README.md`, seção dos hooks (235-425 depois da edição), commits `1627bf8` e `71e9a66`:
      snippet completo com `UserPromptSubmit` (backlog-rite, verify-rite), `PostToolUse` com matcher
      `Write|Edit|MultiEdit|NotebookEdit`, o bloco `PreToolUse` **comentado** com a razão (chega com a
      #137; neste branch `locale-rite.py` responde a um payload de PreToolUse com o envelope de
      PostToolUse, que o bundle descarta como `hookSpecificOutput_event_mismatch` — E.2), a menção a
      `LOCALE_RITE_MODE=inform`, `Stop` (locale-stop-gate); parágrafo do gate de escrita dizendo "hoje
      PostToolUse informa; com a #137 PreToolUse nega"; parágrafo do gate de Stop com a forma probada
      no bundle, o `stop_hook_active`, a forma fixada contra o `~/.gitconfig` e o teto que bloqueia
      uma vez quando a parte medida está limpa; tabela "Which layer catches what" com a primeira
      linha em dois tempos:

      ```
      grep -n '^### \|^| ' README.md | grep -i 'enforcing\|grounding\|locale rite\|What wrote\|Write. /\|Bash —\|another assistant'
      -> 235:### Enforcing the rite (optional hooks)
      -> 324:### The grounding rite (anti-achismo)
      -> 347:### The locale rite, at the write (English machine layer, measured on the tool call)
      -> 372:### The locale rite, at the end of the turn (the Stop gate)
      -> 415:| What wrote the name | Layer that catches it | Effect |
      -> 417:| `Write` / `Edit` / `MultiEdit` / `NotebookEdit` | `locale-rite.py` — on `PostToolUse` today; on `PreToolUse` once #137 merges | today the finding is **context** after the write; with #137 the write is **denied** and nothing reaches the disk |
      -> 418:| Bash — heredoc, `sed -i`, a script, a generator | `locale-stop-gate.py` on `Stop` | the **turn does not end** until the diff is clean or waived |
      -> 419:| another assistant (Codex, Cursor, Copilot), or a human commit | the per-repository kit of the [`code-locale`](skills/code-locale/) skill — pre-commit hook and CI step (issue #139) | the **commit or the pull request** fails |
      grep -n 'Arrives with issue #137\|// "PreToolUse"' README.md
      -> 265:    // Arrives with issue #137 (locale-rite.py learns PreToolUse and LOCALE_RITE_MODE there). Wire
      -> 268:    // "PreToolUse": [
      ```

      O `PreToolUse` que nega é entregue pela issue #137 em paralelo; o README descreve o wiring, diz
      quando ele passa a valer e aponta para a issue em vez de descrever a implementação dela (Q.4).
      O matcher e o nome da variável foram conferidos no código da #137 (E.1), não presumidos.

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

      Rodada de revisão, hook em `e8c1f1d` (`scratchpad/sim138b`, mesmo payload, mesmo método):

      ```
      heredoc pt                                                  -> rc=0 ms=46 chars=1742 keys=decision,reason  servico_cliente.py: servico_cliente [path-pt-noun] | :1: buscar_cliente [pt-verb] | :1: id_usuario [pt-noun]
      mesmo tree, stop_hook_active=true                           -> rc=0 ms=43 chars=371  keys=systemMessage
      mv + sed (renomeado e traduzido)                            -> rc=0 ms=42 chars=0
      sed -i 's/order_id/id_pedido/g' shipping.py                 -> rc=0 ms=44 chars=856  shipping.py:1: id_pedido  [pt-noun: 'pedido']
      mesma árvore, GIT_CONFIG_GLOBAL=<external+mnemonicPrefix+relative+quotePath+color.ui=always>
                                                                  -> rc=0 ms=44 chars=856  shipping.py:1: id_pedido      (antes: chars=0 / w/shipping.py)
      mesma árvore, + GIT_EXTERNAL_DIFF=true no ambiente          -> rc=0 ms=46 chars=856  shipping.py:1: id_pedido
      untracked serviço.py com PT_SOURCE                          -> rc=0 ms=50 chars=1731 serviço.py: serviço [path-non-ascii: 'serviço'] | serviço.py:1: buscar_cliente   (antes: chars=0)
      rastreado relatório.py editado com id_pedido                -> rc=0 ms=50 chars=862  relatório.py:1: id_pedido  [pt-noun: 'pedido']            (antes: chars=0)
      5000 linhas limpas não rastreadas antes de servico_cliente.py -> rc=0 ms=125 chars=770 keys=decision,reason  "the uncommitted diff is longer than 4000 lines [...] NOT measured"   (antes: chars=0)
      mesmo tree, stop_hook_active=true                           -> rc=0 ms=128 chars=358 keys=systemMessage  "longer than 4000 lines; the part past the cap was NOT measured"
      5000 linhas anexadas ao shipping.py rastreado + arquivo pt  -> rc=0 ms=128 chars=770  (bloqueio "not measured"; antes: chars=0)
      build/gen.py 5000 linhas não ignorado + arquivo pt          -> rc=0 ms=43  chars=1742 servico_cliente.py [...]   (vendored pulado antes do git; antes: chars=0)
      1500 arquivos vazios em gen/ (não vendored) + arquivo pt    -> rc=0 ms=60  chars=1742 servico_cliente.py [...]   (vazios pulados; antes, em build/: 1721 ms e chars=0)
      5000 linhas limpas e nada em pt                             -> rc=0 ms=146 chars=770  (bloqueio único "not measured"; depois systemMessage)
      tree limpa / cwd fora de git                                -> rc=0 ms=42 / 45 chars=0
      este worktree com o docstring do hook editado e não commitado, 3 runs -> rc=0 ms=60 / 60 / 67 chars=1548  relatório [non-ascii] ×2, relatorio [pt-noun] — o falso positivo de E.4 (S.3)
      ```

- [x] S.2 Matriz de casos medida, em contagens

      | Artefato | Expectativa | Casos | Resultado |
      |---|---|---|---|
      | entry point real (stdin, repo de rascunho) | tinha de bloquear e bloqueou | 3/3 | heredoc pt, rastreado editado por sed, 500 linhas pt |
      | entry point real (stdin) | tinha de ficar mudo e ficou | 4/4 | renomeado+traduzido, modo inform, fora de git, tree limpa |
      | entry point real (stdin) | `stop_hook_active` → mensagem sem bloqueio | 1/1 | keys=systemMessage |
      | entry point real (stdin), rodada de revisão | os cinco achados da revisão reproduzidos no hook de `11c416d` | 5/5 | diff.external mudo; mnemonicPrefix → `w/`; quotePath esconde `serviço.py`/`relatório.py`; teto mudo em A/B/C/H; README afirmava PreToolUse presente |
      | entry point real (stdin), hook em `e8c1f1d` | tinha de bloquear e bloqueou | 9/9 | gitconfig ligado, `GIT_EXTERNAL_DIFF`, `serviço.py`, `relatório.py`, 5000 limpas + pt (×2), `build/` + pt, 1500 vazios + pt, 5000 limpas sem pt |
      | entry point real (stdin), hook em `e8c1f1d` | `stop_hook_active` no teto limpo → mensagem sem bloqueio | 2/2 | keys=systemMessage, "NOT measured" |
      | entry point real (stdin), hook em `e8c1f1d` | tinha de ficar mudo e ficou | 3/3 | renomeado+traduzido, tree limpa, fora de git |
      | entry point real (stdin) | payload malformado mudo, exit 0 | 5/5 | `[]`, `"x"`, vazio, `null`, `{oops` |
      | entry point real (argv) | argumento desconhecido sai 2 com usage | 1/1 | `--bogus` |
      | entry point real (tempo) | abaixo de 1 s | 10/10 | 41-75 ms, inclusive neste repositório |
      | `--selftest` | decisões OK | 26/26 + 2/2 formas + 6/6 asserções de conteúdo + 5/5 malformados + 2/2 argv | rc=0 (`selftest OK: 26 decisions [...]`) |
      | `--selftest` (cópias com defeito injetado, 1ª rodada) | tinha de ficar vermelho e ficou | 5/5 | nested-output, blocks-twice, ignores-inform, silent-truncation, skips-untracked — rc=1 cada |
      | `--selftest` (cópias com defeito injetado, revisão) | tinha de ficar vermelho e ficou | 6/6 | no-ext-diff, no-prefix-pin, no-quotepath, vendored-after-scan, empty-not-skipped, silent-clean-truncation — rc=1 cada |
      | `--selftest` (cópia de controle) | tinha de ficar verde e ficou | 2/2 | rc=0 nas duas rodadas |
      | escapes conhecidos | ficaram mudos, como declarado | 2/2 | binário em pt pulado; vendored em pt filtrado (ver S.3) |
      | escape observado e não corrigido aqui | detector lê run `+` iniciado dentro de docstring como código | 1/1 | o próprio hook, editado e não commitado, bloqueia por `relatório` no docstring (E.4, S.3) |

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

      Rodada de revisão — cinco achados, todos reproduzidos antes de tocar o código (E.2) e nenhum
      disputado:

      - `diff.external` no `~/.gitconfig` deixava o hook mudo; `diff.mnemonicPrefix` reportava
        `w/shipping.py`; `core.quotePath` (padrão) escondia `serviço.py` e `relatório.py` atrás das
        aspas — nome e conteúdo não medidos. Causa comum: o diff era montado na forma que o config do
        usuário quisesse. Corrigido fixando a forma por flag em toda chamada (D10); a fixture padrão do
        selftest (`GIT_CONFIG_GLOBAL=/dev/null`) provava as decisões só sob config em branco, e agora
        há uma fixture com as opções ligadas.
      - O teto passava mudo quando conteúdo limpo/vendored/vazio ordenava antes do arquivo em
        português (A/B/C/H em E.2): a nota de truncamento só existia colada a um motivo, e
        `if not findings: return None` descartava `truncated`. Corrigido em dois pontos (D4): vendored
        e vazios pulados antes do git; sem achado e teto atingido → bloqueio único dizendo que a cauda
        não foi medida, `systemMessage` no Stop seguinte.
      - O README afirmava a negação em PreToolUse como fato presente, e neste branch `locale-rite.py`
        não tem esse caminho (E.1/E.2). Corrigido no texto: bloco comentado no snippet, parágrafo e
        tabela em dois tempos, docstring reconciliado (linha do `LOCALE_RITE_MODE`).

      Duas fixtures da revisão precisaram de segunda escrita (2.5): nome do repositório colidindo com o
      arquivo de gitconfig, e vazios dentro de `build/` (engolidos pelo pulo de vendored antes de
      testar o pulo de tamanho). O critério continua o mesmo da primeira rodada: um caso que passa com
      o mecanismo desligado não prova o mecanismo — por isso cada fix novo tem um mutante vermelho.

      Escape novo, observado e **não** corrigido aqui: com o docstring do hook editado e não commitado,
      o gate rodado contra este worktree bloqueia por `relatório`/`relatorio` (linhas 59, 92 e 96 do
      docstring) — o run de linhas `+` começa dentro do docstring e o detector o lê como código; no
      arquivo inteiro devolve `findings: 0`. É limite do modo `--diff` do detector (família da #85),
      dura enquanto a edição está não commitada, e é `skills/**` — anotado em E.4.

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
      `MAX_DIFF_LINES`, `GIT_TIMEOUT`, `REASON_CAP`, `SYSTEM_MESSAGE_CAP`, `STOP_EVENTS`, `MODE_VAR`,
      e da revisão `GIT_PIN`, `DIFF_FLAGS`, `is_measurable`, `UNMEASURED_REASON`, `UNMEASURED_MESSAGE`;
      o nome do arquivo vem do glossário da issue (`locale-stop-gate.py`):

      ```
      python3 skills/code-locale/references/check-identifier-locale.py claude/global/hooks/locale-stop-gate.py   (em e8c1f1d)
      -> findings: 0
      ```

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-locale-stop-gate --strict` -> `Change 'add-locale-stop-gate' is valid`;
      `bash scripts/validate-rite.sh` -> `rite evidence gate: 0 findings` / `spec-rite gate: 0
      findings` / `Totals: 3 passed, 0 failed (3 items)` / `rite gate OK`. Rerodados depois da rodada
      de revisão (`71e9a66` + este tasks.md): `Change 'add-locale-stop-gate' is valid`; `Totals: 3
      passed, 0 failed (3 items)` / `rite gate OK`; runner dos gates (`scratchpad/gates.sh`, os steps
      de Validate do `ci.yml`) só `PASS` — `locale-detector`, `locale-rite`, `backlog-rite-selftest`,
      `verify-rite-selftest`, `scan-secrets`, `hygiene`, `rite`, `rite-evidence-selftest`,
      `spec-rite-selftest`, `smoke: 17/17`, `plugin-validate`, `openspec-strict add-locale-stop-gate`;
      `GITHUB_EVENT_PATH=<body com "Spec-rite: add-locale-stop-gate"> python3 scripts/validate-skill-version.py`
      -> `skill-version gate: 0 findings (base origin/master, 0 skill(s) changed, 0 with content changes)`
      rc=0
- [x] V.2 Descoberta do catálogo intacta: `ls -d skills/*/ | wc -l` -> `35` antes e depois (nenhum
      `skills/**` tocado — `git diff --stat 80ee53c...HEAD` lista 8 arquivos, nenhum sob `skills/`;
      depois da revisão: `git diff --name-only 80ee53c...HEAD | grep -c '^skills/'` -> `0`);
      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`;
      `claude plugin validate . --strict` -> `✔ Validation passed`; `bash generate.sh` deixa a árvore
      limpa (`PASS tree-clean-after-generate`). `npx skills add . --list` não foi rodado nesta execução
      (subagente isolado, sem rede garantida); a contagem local e o validador de hygiene, que mede as
      contagens publicadas, cobrem o que ele mediria.
- [x] V.3 README / docs atualizados: `README.md:235-425` reescrita com o snippet completo (bloco
      `PreToolUse` comentado até a #137), o parágrafo do gate de Stop com a forma fixada e o teto, e a
      tabela em dois tempos (2.8, `71e9a66`); a composição do catálogo não muda
- [x] V.4 `openspec archive add-locale-stop-gate --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz


      ```
      openspec archive add-locale-stop-gate --yes
      -> Specs updated successfully.
      -> Change 'add-locale-stop-gate' archived as '2026-09-05-add-locale-stop-gate'.
      ```