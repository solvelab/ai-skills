## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `d2918ed` (`docs(openspec): arquiva as duas changes de svg-animation`), topo de
      `master` em 2026-09-04:

      - `claude/global/hooks/backlog-rite.py` — 109 linhas; `CHANGE_SIGNALS` em 38-52 com a linha 47
        `fix|bug|erro|error|falha|quebr\w*|broken|` (sem par inglês para `falha`); `SKIP` em 55-60
        silencia slash command e dispensas; `has_spec_rite()` em 84-86 lê `payload["cwd"]` com
        fallback `os.getcwd()`; `main()` em 89-105 chama `payload.get("prompt")` na linha 95 sem
        guarda de tipo e sem ler `sys.argv`.
      - `claude/global/hooks/verify-rite.py` — 120 linhas; `GUESS_SIGNALS` em 54-76; `SKIP` em 80-86
        com o comentário de 78-79 ("this does NOT skip slash commands"); `main()` em 103-116 chama
        `payload.get("prompt")` na linha 109 sem guarda e sem `argv`.
      - `claude/global/hooks/locale-rite.py` — 260 linhas; o modelo: `evaluate()` em 155-173,
        `selftest()` em 176-241, `"--selftest" in sys.argv[1:]` em 245, `isinstance(payload, dict)`
        em 251.
      - `.github/workflows/ci.yml` — step `Locale write-gate hook self-test` em 93-94; os outros
        gates auto-testados em 87-91 e 113-117.
      - `README.md` — seção do hook de backlog em 225-260; a frase "It stays silent for prompts
        already inside the rite…" em 258-260 (a issue cita 255-257: drift de três linhas desde o
        grooming, mesma frase).
      - `openspec/changes/archive/2026-08-07-add-backlog-first-rite/design.md:31-32` e `:78-80` —
        a decisão do matcher generoso e do falso positivo aceito.
      - `openspec/specs/skills-catalog/spec.md:188-239` (*The development rite is enforced outside
        the model's discretion*) e `:457-486` (*The grounding rite is carried into context on
        correction*) — os dois requisitos que o delta modifica; `:579-585` (*A shipped enforcement
        script declares what escapes it*) e `openspec/specs/skills-authoring/spec.md:259-263` — as
        cláusulas de selftest que hoje só cobrem scripts de skill e de autoria.
      - `openspec/changes/archive/2026-08-30-fix-release-race/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md` — modelo de estilo da casa.
      - `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md`,
        `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py`,
        `scripts/validate-spec-rite.py` — o que os gates exigem de cada grupo.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      python3 --version
      -> Python 3.14.5
      openspec --version
      -> 1.6.0
      openspec list
      -> No active changes found.
      ```

      `--selftest` é hoje um no-op silencioso (o hook lê stdin vazio e sai 0):

      ```
      python3 claude/global/hooks/backlog-rite.py --selftest </dev/null; echo "selftest-before rc=$?"
      -> selftest-before rc=0        (nenhuma outra linha)
      ```

      Payload que não é objeto estoura nos dois hooks:

      ```
      echo '[]' | python3 claude/global/hooks/backlog-rite.py; echo "rc=$?"
      ->   File ".../backlog-rite.py", line 95, in main
      ->     prompt = payload.get("prompt") or ""
      -> AttributeError: 'list' object has no attribute 'get'
      -> rc=1
      echo '"x"' | python3 claude/global/hooks/verify-rite.py; echo "rc=$?"
      ->   File ".../verify-rite.py", line 109, in main
      -> AttributeError: 'str' object has no attribute 'get'
      -> rc=1
      printf '' | python3 claude/global/hooks/backlog-rite.py; echo "rc=$?"
      -> rc=0                        (JSONDecodeError já é capturado)
      ```

      Assimetria `falha`/`fail`, medida pelo stdin real (payload `{"prompt": …, "cwd": <repo>}`):

      ```
      por que o teste falha?      -> rc=0 chars=740 spec=1   (dispara, com a frase do spec-rite)
      why does the build fail?    -> rc=0 chars=0   spec=0   (mudo)
      ```

      Scaffold da change com o schema do repositório:

      ```
      openspec new change add-hook-selftests --schema skills-rite
      -> Created change 'add-hook-selftests' at openspec/changes/add-hook-selftests/
      -> Schema: skills-rite
      ```

- [x] E.3 O que não pôde ser probado

      Um item. A lista exata dos 8 prompts da simulação de 2026-09-04 não está gravada no
      `findings.md` que a originou (o arquivo registra só o resultado: "backlog-rite dispara em
      'por que o teste falha?'"). Os 8 prompts usados aqui foram reconstruídos a partir dos exemplos
      citados na issue #115 (os quatro de diagnóstico/pedido) e das três classes que o `SKIP`
      silencia mais uma pergunta neutra; a lista está escrita por extenso em S.1, para que a
      comparação antes/depois seja reproduzível mesmo que não coincida byte a byte com a original.

      O payload real do harness não foi capturado nesta sessão: o selftest alimenta só `prompt` e
      `cwd`, os únicos campos que os hooks leem, e isso fica declarado no docstring de cada hook
      (TR2). Que o harness ainda envie esses campos com esses nomes é uma premissa da doc pinada
      (`code.claude.com/docs/en/hooks`), não algo medido aqui.

- [x] E.4 Checagem de escopo

      A change faz só o que a issue #115 pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up:

      - `verify-rite.py` não está wired em `~/.claude/settings.json` desta máquina, enquanto o
        README mostra os dois hooks — configuração pessoal, fora da issue por decisão dela.
      - Um `prompt` presente mas não-string (`{"prompt": 42}`) estouraria em `SKIP.search` com
        `TypeError`; tratado como ausente por D2 do design, porque cai na mesma classe "payload
        malformado não derruba o turno" de FR2. Registrado aqui por ser um caso a mais do que a
        issue enumerou. A revisão achou o irmão dele — `{"cwd": 42}` estourava em `os.path.join` —
        e a guarda entrou pelo mesmo motivo (D2, commit `9c04572`).
      - Argumento desconhecido (`--self-test`) caía no caminho do stdin e saía 0 sem saída, o no-op
        verde de D3; os dois hooks passam a rejeitar com usage em stderr e exit 2 (D3, `9c04572`).
        O `locale-rite.py:245` carrega a mesma leitura por pertinência e fica como follow-up.
      - `fail\w*`, a forma pedida na issue, foi medida casando failover / failsafe / failure e
        estreitada para `fail(s|ed|ing)?` (D6, `c86a9ce`); a issue previa "exceto o sinal `fail`",
        e é só isso que muda.
      - `README.md:258-260` e não `:255-257` como a issue cita: a frase é a mesma, deslocada três
        linhas por uma edição posterior ao grooming.

## 2. Selftest e guarda de payload nos dois hooks

- [x] 2.1 `backlog-rite.py`: decisão extraída para `evaluate(payload) -> str | None`; leitura de
      stdin em `read_payload(stream) -> dict | None` com guarda `isinstance(payload, dict)`;
      `--selftest` lido de `sys.argv[1:]`; docstring declara o que o selftest não cobre (D1-D3).
      Commit `7804e62`. Depois da revisão, `9c04572`: `cwd` que não é string cai em `os.getcwd()`
      em vez de estourar, e argumento que não seja exatamente `--selftest` sai 2 com usage:

      ```
      printf '{"prompt": "implementa o endpoint", "cwd": 42}' | python3 claude/global/hooks/backlog-rite.py | cut -c1-40; echo "rc=$?"
      -> DEVELOPMENT RITE (backlog-first): this
      -> rc=0                        (antes de 9c04572: TypeError ... not int, rc=1)
      python3 claude/global/hooks/backlog-rite.py --self-test </dev/null; echo "rc=$?"
      -> usage: claude/global/hooks/backlog-rite.py [--selftest]
      -> rc=2                        (antes: rc=0, nenhuma saída)
      python3 claude/global/hooks/backlog-rite.py --selftest extra </dev/null; echo "rc=$?"
      -> usage: claude/global/hooks/backlog-rite.py [--selftest]
      -> rc=2                        (antes: rodava o selftest e ignorava o resto)
      ```
- [x] 2.2 `backlog-rite.py`: `fail(s|ed|ing)?` no lado inglês da linha 47, ao lado de `falha` (D6;
      `7804e62` entrou com `fail\w*`, `c86a9ce` estreitou depois de medir failover/failsafe/failure)

      ```
      git diff -U0 d2918ed...HEAD -- claude/global/hooks/backlog-rite.py | grep -E '^[-+].*falha\|'
      -> -    r"fix|bug|erro|error|falha|quebr\w*|broken|"
      -> +    r"fix|bug|erro|error|falha|fail(s|ed|ing)?|quebr\w*|broken|"
      ```

      Conjuntos medidos (`CHANGE_SIGNALS.search` importado do hook), que D6 registra em tabela:

      ```
      \bfalha\b        : 'o teste falha' True | 'o teste falhou' False | 'está falhando' False | 'falhas no deploy' False
      fail\w*          : fail/fails/failed/failing True | 'the failure domain' True | 'a failover cluster' True | 'a failsafe' True
      fail(s|ed|ing)?  : fail/fails/failed/failing True | 'the failure domain' False | 'a failover cluster' False | 'a failsafe' False
      ```

- [x] 2.3 `backlog-rite.py --selftest`: casos que disparam, casos mudos, payloads malformados via
      `read_payload`, asserção de forma, uma linha OK/FAILED por caso, resumo, exit code (D4, D5)

      Saída depois da rodada 2 da revisão (16 decisões: as 12 originais, "failing", "failover" e os
      dois casos do fallback de `cwd`), linhas de decisão completas, bloco dos malformados elidido:

      ```
      python3 claude/global/hooks/backlog-rite.py --selftest; echo "rc=$?"
      ->   OK      change request fires
      ->   OK      english change request fires
      ->   OK      cwd with openspec/ appends the spec sentence
      ->   OK      cwd without openspec/ omits the spec sentence
      ->   OK      diagnostic question containing 'falha' fires (accepted trade-off)
      ->   OK      english 'fail' (verb forms fail/fails/failed/failing) fires
      ->   OK      english 'failing' fires
      ->   OK      english noun 'failover' is silent
      ->   OK      slash command carrying a change word is silent
      ->   OK      waiver 'sem backlog' is silent
      ->   OK      neutral question is silent
      ->   OK      empty prompt is silent
      ->   OK      payload without prompt is silent
      ->   OK      prompt that is not a string is silent
      ->   OK      cwd that is not a string falls back to the process cwd (with openspec/)
      ->   OK      cwd that is not a string falls back to the process cwd (without openspec/)
      ->   OK      output shape is the reminder the harness reads
      ->   OK      malformed payload is ignored: json array
      ->   [...]                       (json string, empty stdin, json null, json number, not json)
      ->   OK      well-formed payload is read
      ->
      -> selftest OK: 16 decisions, 6 malformed payloads, plus the output shape
      -> rc=0
      ```

      Hermético de verdade (TR1), medido com `os.path.isdir` e `os.getcwd` instrumentados no módulo
      carregado por `importlib`, rodando `selftest()` do repositório. Antes desta rodada, o caso
      único `cwd: 42` (`spec_sentence=None`) fazia `isdir('<repo>/openspec')`; depois, nenhum
      `isdir` cai no cwd real, o `getcwd()` que o fallback vê é a fixture, e o cwd é restaurado:

      ```
      antes  -> rc 0 isdir on real cwd: ['<worktree>/openspec'] getcwd calls: 2
      depois -> rc 0 | isdir calls on real cwd: [] | isdir calls total: 10
      -> getcwd returned: ['REAL', 'REAL', 'fixture:with-rite', 'REAL', 'fixture:without-rite']
      -> cwd restored after selftest: True
      cd /tmp && python3 <worktree>/claude/global/hooks/backlog-rite.py --selftest | tail -1; echo "rc=$?"
      -> selftest OK: 16 decisions, 6 malformed payloads, plus the output shape
      -> rc=0
      ```

      (Os `REAL` são só o caminho: `previous = os.getcwd()` antes de cada `chdir`, e a consulta que
      `tempfile` faz ao escolher o diretório temporário — nada é lido dentro dele.)

      O selftest fica vermelho quando uma decisão regride — provado em cópias, cada uma com um
      defeito injetado:

      ```
      sed 's/|fail(s|ed|ing)?//' claude/global/hooks/backlog-rite.py > $SCR/backlog-rite-nofail.py
      python3 $SCR/backlog-rite-nofail.py --selftest | grep FAILED; echo "nofail rc=$?"
      ->   FAILED  english 'fail' (verb forms fail/fails/failed/failing) fires
      ->   FAILED  english 'failing' fires
      -> nofail rc=1
      sed 's/fail(s|ed|ing)?/fail\\w*/' claude/global/hooks/backlog-rite.py > $SCR/backlog-rite-wide.py
      python3 $SCR/backlog-rite-wide.py --selftest | grep FAILED; echo "wide rc=$?"
      ->   FAILED  english noun 'failover' is silent
      -> wide rc=1
      sed 's#r"(^\\s\*/\[a-z-\]+"#r"(^\\s*/NEVER"#' claude/global/hooks/backlog-rite.py > $SCR/backlog-rite-noslash.py
      python3 $SCR/backlog-rite-noslash.py --selftest | grep FAILED; echo "noslash rc=$?"
      ->   FAILED  slash command carrying a change word is silent
      -> noslash rc=1
      ```

      Sem a guarda de `cwd` (cópia com o `payload.get("cwd") or os.getcwd()` de `7804e62`), os casos
      do fallback não imprimem FAILED: estouram com `TypeError: expected str, bytes or os.PathLike
      object, not int` e rc=1 — vermelho do mesmo jeito, mas por traceback, não por asserção. Com um
      fallback que ignora o cwd do processo (cópia com `cwd = "/"` no lugar de `os.getcwd()`):

      ```
      python3 $SCR/backlog-rite-nofallback.py --selftest | grep FAILED; echo "nofallback rc=$?"
      ->   FAILED  cwd that is not a string falls back to the process cwd (with openspec/)
      -> nofallback rc=1
      ```

- [x] 2.4 `verify-rite.py`: mesma extração — `evaluate`, `read_payload`, `--selftest` explícito,
      docstring com o limite do selftest (D1-D3). Commit `7804e62`.
- [x] 2.5 `verify-rite.py --selftest`: casos que disparam (inclusive slash command com correção,
      `verify-rite.py:78-79`), casos mudos, payloads malformados, forma da saída, resumo, exit code
      (D7)

      ```
      python3 claude/global/hooks/verify-rite.py --selftest; echo "rc=$?"
      ->   OK      portuguese caught guess fires
      ->   OK      english demand for a source fires
      ->   [...]                       ('essa flag não existe', 'that's not what I asked')
      ->   OK      correction inside a slash command still fires
      ->   OK      waiver 'pode chutar' is silent
      ->   [...]                       (waiver 'from memory is fine')
      ->   OK      implementation request is silent
      ->   [...]                       (neutral question, empty prompt, no prompt, prompt not a string,
      ->                                output shape, 6 malformed payloads, well-formed payload)
      -> selftest OK: 12 decisions, 6 malformed payloads, plus the output shape
      -> rc=0
      ```

      Argumento desconhecido (`9c04572`):

      ```
      python3 claude/global/hooks/verify-rite.py --self-test </dev/null; echo "rc=$?"
      -> usage: claude/global/hooks/verify-rite.py [--selftest]
      -> rc=2                        (antes: rc=0, nenhuma saída)
      ```

      Vermelho quando a regra do slash command é "harmonizada" com o backlog-rite — cópia com
      `^\s*/[a-z-]+` acrescentado ao `SKIP`:

      ```
      python3 $SCR/verify-rite-broken.py --selftest; echo "broken rc=$?"
      ->   FAILED  correction inside a slash command still fires
      -> selftest FAILED: correction inside a slash command still fires
      -> broken rc=1
      ```

- [x] 2.6 `.github/workflows/ci.yml`: dois steps novos logo após `Locale write-gate hook self-test`,
      um por hook, mesmo padrão de nome dos gates auto-testados (D8). Commit `bb683b7`:

      ```
      git diff origin/master...HEAD -- .github/workflows/ci.yml
      -> +      - name: Backlog rite hook self-test (the shipped hook is itself gated)
      -> +        run: python3 claude/global/hooks/backlog-rite.py --selftest
      -> +      - name: Grounding rite hook self-test (the shipped hook is itself gated)
      -> +        run: python3 claude/global/hooks/verify-rite.py --selftest
      ```

- [x] 2.7 `README.md:258-264`, junto à frase "It stays silent for prompts already inside the
      rite…": uma frase dizendo que perguntas de diagnóstico contendo `erro`/`bug`/`falha`/`fail`
      disparam e por quê, citando o custo assimétrico e o selftest que fixa o caso. Commit `0381b1f`;
      `7cf89c7` troca "one paragraph of context" por "one line of context", a palavra da decisão
      citada (`2026-08-07-add-backlog-first-rite/design.md:31-32`) — o docstring do hook idem, em
      `c86a9ce`.

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi exercitado pelo caminho real — stdin do harness — com a saída observada

      Entrada: `printf '{"prompt": <json>, "cwd": "<repo>"}' | python3 claude/global/hooks/backlog-rite.py`,
      um processo por prompt. Unidade única em todo este grupo: `chars` = caracteres da saída
      capturada em shell (`out=$(...)`; `${#out}`), sem o newline final — `wc -c` daria 3 bytes a
      mais (743/503) pelos acentos e pelo newline. `spec` = ocorrências da frase do spec-rite.
      Os 8 prompts, **antes** (`d2918ed`) e **depois** (`c86a9ce`, mesmos números que em `7804e62`):

      ```
      implementa o endpoint de login               -> antes rc=0 chars=740 spec=1 | depois rc=0 chars=740 spec=1
      /backlog nova ideia                          -> antes rc=0 chars=0   spec=0 | depois rc=0 chars=0   spec=0
      faz isso sem backlog, corrige o typo         -> antes rc=0 chars=0   spec=0 | depois rc=0 chars=0   spec=0
      o que é um hook?                             -> antes rc=0 chars=0   spec=0 | depois rc=0 chars=0   spec=0
      por que o teste falha?                       -> antes rc=0 chars=740 spec=1 | depois rc=0 chars=740 spec=1
      why does the build fail?                     -> antes rc=0 chars=0   spec=0 | depois rc=0 chars=740 spec=1
      por que não implementa o endpoint de login?  -> antes rc=0 chars=740 spec=1 | depois rc=0 chars=740 spec=1
      como corrijo esse bug?                       -> antes rc=0 chars=740 spec=1 | depois rc=0 chars=740 spec=1
      ```

      Só "why does the build fail?" mudou, como a issue previu. A frase do spec-rite some quando o
      `cwd` não tem `openspec/`:

      ```
      printf '{"prompt": "implementa o endpoint", "cwd": "/tmp"}' | python3 claude/global/hooks/backlog-rite.py | grep -c 'spec-driven rite'
      -> 0            (500 chars: só o REMINDER)
      ```

      O lado inglês de `fail`, corpus da revisão, `cwd=/tmp`, **antes** (`d2918ed`) e **depois**
      (`c86a9ce`) — é o alargamento que D6 registra, e o que ficou de fora dele:

      ```
      why does the build fail?               -> antes rc=0 chars=0   | depois rc=0 chars=500
      the tests are failing                  -> antes rc=0 chars=0   | depois rc=0 chars=500
      the build failed again                 -> antes rc=0 chars=0   | depois rc=0 chars=500
      what is a failover cluster?            -> antes rc=0 chars=0   | depois rc=0 chars=0
      explain the failure domain concept     -> antes rc=0 chars=0   | depois rc=0 chars=0
      o que é um failsafe?                   -> antes rc=0 chars=0   | depois rc=0 chars=0
      o teste falhou ontem                   -> antes rc=0 chars=0   | depois rc=0 chars=0
      o deploy está falhando                 -> antes rc=0 chars=0   | depois rc=0 chars=0
      ```

      (Em `7804e62`, com `fail\w*`, os três de substantivo davam 500 — medido na revisão; é o que
      `c86a9ce` desfaz.) Slash command com sinal e `cwd` não-string, pelo mesmo caminho:

      ```
      /execute-backlog 12 implementa o endpoint   (cwd=<repo>)  -> rc=0 chars=0
      implementa o endpoint                       (cwd=42)      -> rc=0 chars=740 rodando do repo, 500 rodando de /tmp (fallback: os.getcwd())
      ```

      `verify-rite.py` pelo mesmo caminho (`{"prompt": <json>}`), antes e depois idênticos:

      ```
      isso é achismo                      -> rc=0 chars=883
      where did you see that              -> rc=0 chars=883
      pode chutar, de onde tirou isso?    -> rc=0 chars=0
      /backlog você inventou essa flag    -> rc=0 chars=883
      implementa o endpoint               -> rc=0 chars=0
      ```

      Payloads malformados, **antes** (traceback, E.2) e **depois**:

      ```
      echo '[]'  | python3 claude/global/hooks/backlog-rite.py; echo "rc=$?"   -> rc=0  (sem saída)
      echo '"x"' | python3 claude/global/hooks/backlog-rite.py; echo "rc=$?"   -> rc=0  (sem saída)
      printf ''  | python3 claude/global/hooks/backlog-rite.py; echo "rc=$?"   -> rc=0  (sem saída)
      echo null  | python3 claude/global/hooks/backlog-rite.py; echo "rc=$?"   -> rc=0  (sem saída)
      echo '[]'  | python3 claude/global/hooks/verify-rite.py;  echo "rc=$?"   -> rc=0  (sem saída)
      echo '"x"' | python3 claude/global/hooks/verify-rite.py;  echo "rc=$?"   -> rc=0  (sem saída)
      printf ''  | python3 claude/global/hooks/verify-rite.py;  echo "rc=$?"   -> rc=0  (sem saída)
      echo null  | python3 claude/global/hooks/verify-rite.py;  echo "rc=$?"   -> rc=0  (sem saída)
      ```

- [x] S.2 Matriz de casos medida, em contagens

      | Artefato | Expectativa | Casos | Resultado |
      |---|---|---|---|
      | backlog-rite (stdin, 8 prompts) | tinha de disparar e disparou | 5/5 | inclui o falso positivo aceito e "why does the build fail?" (novo) |
      | backlog-rite (stdin, 8 prompts) | tinha de ficar mudo e ficou | 3/3 | slash command, "sem backlog", pergunta neutra |
      | backlog-rite (stdin, corpus `fail`) | tinha de passar a disparar e passou | 3/3 | fail / failing / failed |
      | backlog-rite (stdin, corpus `fail`) | tinha de continuar mudo e continuou | 5/5 | failover, failure, failsafe, falhou, falhando |
      | backlog-rite (stdin) | payload malformado mudo, exit 0 | 4/4 | `[]`, `"x"`, vazio, `null` (antes: 2/4 estouravam) |
      | backlog-rite (stdin) | `cwd` não-string não estoura | 2/2 | `42`, `["/tmp"]` (antes: 2/2 estouravam) |
      | os dois hooks (argv) | argumento desconhecido sai 2 com usage | 4/4 | `--self-test`, `--selftest extra` × 2 hooks (antes: 4/4 saíam 0) |
      | backlog-rite `--selftest` | decisões OK | 16/16 + forma da saída + 6/6 malformados | rc=0 |
      | backlog-rite `--selftest` (cópias com defeito injetado) | tinha de ficar vermelho e ficou | 5/5 | sem `fail`, `fail\w*` de volta, slash SKIP apagado, sem guarda de cwd, fallback que ignora o cwd — rc=1 cada |
| backlog-rite `--selftest` (hermético, TR1) | nenhum `isdir` no cwd real; cwd restaurado; mesmo resultado de `/tmp` | 3/3 | instrumentado por `importlib` (2.3) |
      | verify-rite (stdin, 5 prompts) | tinha de disparar e disparou | 3/3 | inclui slash command com correção |
      | verify-rite (stdin, 5 prompts) | tinha de ficar mudo e ficou | 2/2 | dispensa, pedido de implementação |
      | verify-rite (stdin) | payload malformado mudo, exit 0 | 4/4 | `[]`, `"x"`, vazio, `null` (antes: 2/4 estouravam) |
      | verify-rite `--selftest` | decisões OK | 12/12 + forma da saída + 6/6 malformados | rc=0 |
      | verify-rite `--selftest` (cópia que silencia slash command) | tinha de ficar vermelho e ficou | 1/1 | rc=1 |
      | escape conhecido | ficou mudo | 1/1 | ver S.3 |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      Os 8 prompts dão o mesmo resultado antes e depois, exceto "why does the build fail?", que passa
      a disparar — como a issue previu. Duas coisas se comportaram diferente do escrito:

      - A forma pedida na issue, `fail\w*`, foi medida em `7804e62` disparando em "what is a failover
        cluster?", "explain the failure domain concept" e "o que é um failsafe?" (0 -> 500 chars cada,
        `cwd=/tmp`) — e o D6 original dizia que `\bfalha\b` casa "falhou"/"falhando", o que a mesma
        medição desmentiu. O sinal ficou `fail(s|ed|ing)?` (`c86a9ce`): fail / failing / failed
        disparam (0 -> 500), os substantivos e o português conjugado continuam em 0.
      - O caso "slash command is silent" original usava "/backlog nova ideia", sem palavra de mudança,
        e ficava verde com a regra de slash command apagada; o prompt agora carrega um sinal
        (`0ebe63e`), e a cópia sem a regra fica vermelha.
      - O caso `cwd: 42` da rodada 1 afirmava só "não estoura e dispara" e, medido com `isdir`
        instrumentado, lia `<repo>/openspec` pelo fallback — o docstring, D4 e TR1 diziam o
        contrário. Virou dois casos que movem o cwd do processo para cada fixture (`try/finally`) e
        afirmam a frase do spec-rite nos dois sentidos (2.3, D4).

      Um escape conhecido e mantido de propósito: "por que não implementa o endpoint de login?" é
      um pedido real com forma de pergunta, e dispara — por isso a exclusão por forma de pergunta
      não entra (design, Non-Goals). O que continua fora do alcance de qualquer selftest é o
      KNOWN LIMIT do `verify-rite.py`: ele dispara na correção, nunca no achismo em si; isso está
      declarado no docstring, não medido aqui.

      O que a simulação **não** prova: que o harness real ainda envie `prompt` e `cwd` com esses
      nomes — a entrada aqui foi construída à mão a partir da doc pinada (E.3).

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — **não se aplica**: esta change não toca
      nenhuma skill. O step `Skill frontmatter checks` de `.github/workflows/ci.yml:56` foi extraído
      (`yaml.safe_load` do workflow, corpo do `run:` para um arquivo) e rodado verbatim: nenhuma linha
      `::error`, `rc=0` (o step só imprime em falha)
- [x] Q.2 Conteúdo de skill tocado em inglês — **não se aplica** pelo mesmo motivo; o delta de spec,
      os docstrings dos hooks, os nomes dos casos do selftest e a frase do README estão em inglês,
      como o catálogo exige; proposal/design/tasks em português, como as changes da casa
- [x] Q.3 Gatilhos de descrição testáveis — **não se aplica**: nenhuma descrição de skill muda
- [x] Q.4 Sem doutrina duplicada: o selftest e o README **citam** a decisão de 2026-08-07 em vez de
      reescrevê-la; o docstring do verify-rite continua apontando para `verify-before-claiming`;
      ver a tabela de Canonical Home em `design.md`
- [x] Q.5 Identificadores em inglês no que a change introduz — `evaluate`, `read_payload`,
      `selftest`, `with_rite`, `without_rite`, `spec_sentence`, ids de step — conforme o glossário
      da issue #115 e `code-locale`:

      ```
      python3 skills/code-locale/references/check-identifier-locale.py claude/global/hooks/backlog-rite.py claude/global/hooks/verify-rite.py
      -> findings: 0
      ```

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-hook-selftests --strict` -> `Change 'add-hook-selftests' is valid`
- [x] V.2 Descoberta do catálogo intacta: `npx skills add . --list` -> `Found 35 skills`;
      `ls -d skills/*/ | wc -l` -> `35`; sem órfão ou renomeado
- [x] V.3 README / docs atualizados: `README.md:258-264` ganha a frase do falso positivo aceito
      (2.7); a composição do catálogo não muda
- [ ] V.4 `openspec archive add-hook-selftests --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz
