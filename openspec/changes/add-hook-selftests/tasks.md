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
        issue enumerou.
      - `README.md:258-260` e não `:255-257` como a issue cita: a frase é a mesma, deslocada três
        linhas por uma edição posterior ao grooming.

## 2. Selftest e guarda de payload nos dois hooks

- [ ] 2.1 `backlog-rite.py`: decisão extraída para `evaluate(payload) -> str | None`; leitura de
      stdin em `read_payload(stream) -> dict | None` com guarda `isinstance(payload, dict)`;
      `--selftest` lido de `sys.argv[1:]`; docstring declara o que o selftest não cobre (D1-D3)
- [ ] 2.2 `backlog-rite.py`: `fail\w*` no lado inglês da linha 47, ao lado de `falha` (D6)
- [ ] 2.3 `backlog-rite.py --selftest`: casos que disparam (pedido de mudança pt/en, cwd com
      `openspec/` em `tempfile` acrescenta `SPEC_RITE`, cwd sem ele não acrescenta, "por que o teste
      falha?" com a decisão de 2026-08-07 citada, "why does the build fail?"), casos mudos (slash
      command, "sem backlog", pergunta neutra, prompt vazio/ausente/não-string), payloads
      malformados (`[]`, `"x"`, vazio, `null`, `42`) via `read_payload`, asserção de forma da
      saída, uma linha OK/FAILED por caso, linha de resumo, exit code (D4, D5)
- [ ] 2.4 `verify-rite.py`: mesma extração — `evaluate`, `read_payload`, `--selftest` explícito,
      docstring com o limite do selftest (D1-D3)
- [ ] 2.5 `verify-rite.py --selftest`: casos que disparam ("isso é achismo", "where did you see
      that", "essa flag não existe", "that's not what I asked", slash command com correção —
      `verify-rite.py:78-79`), casos mudos (dispensa "pode chutar", "implementa o endpoint", prompt
      vazio/ausente), payloads malformados via `read_payload`, forma da saída, resumo, exit code (D7)
- [ ] 2.6 `.github/workflows/ci.yml`: dois steps novos logo após `Locale write-gate hook self-test`,
      um por hook, mesmo padrão de nome dos gates auto-testados (D8)
- [ ] 2.7 `README.md`, junto à frase "It stays silent for prompts already inside the rite…": uma
      frase dizendo que perguntas de diagnóstico contendo `erro`/`bug`/`falha` disparam e por quê

## 3. Simulation & Field Proof (MANDATORY)

- [ ] S.1 O artefato foi exercitado pelo caminho real — stdin do harness — com a saída observada
- [ ] S.2 Matriz de casos medida, em contagens
- [ ] S.3 O que escapou ou se comportou diferente do esperado

## 4. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado
- [ ] Q.2 Conteúdo de skill tocado em inglês
- [ ] Q.3 Gatilhos de descrição testáveis
- [ ] Q.4 Sem doutrina duplicada
- [ ] Q.5 Identificadores em inglês no que a change introduz

## 5. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-hook-selftests --strict` verde
- [ ] V.2 Descoberta do catálogo intacta: contagem de skills inalterada, sem órfão ou renomeado
- [ ] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo
- [ ] V.4 `openspec archive add-hook-selftests --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz
