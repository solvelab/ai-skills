# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `d10969c` (master, base de `backlog/205-harden-agent-validator`) em 2026-09-07:

      - `scripts/validate-agents.py` inteiro — `add()`, `split()`, `check_file()`, `check_layout()` e
        `main()`, incluindo o `return` antecipado quando `agents/` não existe e os cinco blocos
        `if X is not None:`.
      - `scripts/selftest-validate-agents.py` inteiro — `GOOD`, `build()`, `run()`, `drop()`,
        `replace()`, a lista `CASES` e as duas asserções positivas do final.
      - `openspec/specs/agents-catalog/spec.md` — os dois requisitos tocados, copiados por completo no
        delta antes de serem modificados.
      - `.github/workflows/ci.yml` — os dois steps de agente, para confirmar que nenhum precisa mudar.
      - `agents/*.md` (os três) e `plugins/*/agents/*.md` (as três cópias geradas).
      - `generate.sh` — a linha que copia o agente, `cp --no-preserve=mode`, que é o que torna a
        comparação de conteúdo do A7 válida byte a byte.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      O relatório que originou o item é a saída do agente `ai-skills:bug-hunter-analyst` despachado
      contra `scripts/validate-agents.py` numa sessão headless em 2026-09-07. Oito ataques, cada um
      com `WHERE:` em `path:line` e `CONFIDENCE:`; seis linhas em *TRIED AND FOUND NOTHING* com a
      razão de cada uma não ter produzido nada.

      Estado antes da correção: `python3 scripts/selftest-validate-agents.py` -> `22/22 cases passed`
      — ou seja, o selftest existente aprovava um validador com dois falsos verdes.

      Depois: `python3 scripts/selftest-validate-agents.py` -> `33/33 cases passed`;
      `python3 scripts/validate-agents.py` -> `agents checked: 3   findings: 0`.

      `openspec new change harden-agent-validator --schema skills-rite` -> `Schema: skills-rite`;
      `openspec validate harden-agent-validator --strict` -> `Change 'harden-agent-validator' is valid`.

      `cmp -s agents/<n>.md plugins/<g>/agents/<n>.md` para os três -> idênticos, o que confirma a
      premissa do D5.

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Duas lacunas, nenhuma preenchida com substituto plausível:

      (a) **O ataque 4 (bomba de expansão YAML) nunca foi executado.** O próprio relatório o marcou
      `CONFIDENCE: plausible` e disse que não executou payload. Esta change **também não** executa: ela
      remove a classe recusando âncora e alias, e o caso de selftest prova que um alias é recusado —
      não que uma bomba teria estourado a máquina. A afirmação que fica é "âncora é recusada", não
      "a bomba era explorável".

      (b) **Se algum consumidor usa âncora YAML legitimamente no frontmatter de um agente.** Os três
      publicados não usam, e o formato documentado pelo harness não a menciona. Não há como saber de
      agentes fora deste repositório; a mensagem do achado é onde essa exceção seria discutida.

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      **Escopo levantado, e registrado:** a issue #205 foi escrita descrevendo **seis** achados,
      porque eu tinha lido só a cauda do relatório ao abri-la. São **oito**, e os dois que faltavam
      são os graves (falso verde por null explícito; `agents/` ausente pulando a checagem de órfão).
      O levantamento está comentado na issue e os critérios de aceite passaram a cobrir os oito.
      Levantar veredito não pede permissão; baixar pediria.

      Follow-ups anotados e **não** feitos:

      - As seis linhas de *TRIED AND FOUND NOTHING* (CRLF, alias recursivo em `tools`, normalização
        Unicode no stem, frontmatter vazio degenerado, dois órfãos do mesmo stem, corrida de
        filesystem) ficam registradas como já examinadas e **não** viram teste.
      - O relatório observou que o frontmatter vazio degenerado (`---\n---\n`) é rotulado pelo check
        errado — reprova, mas como "sem frontmatter" em vez de "frontmatter vazio". Não é falso verde
        e não foi tocado.
      - Nada em `agents/`, `skills/`, `generate.sh`, `.github/workflows/` ou `README.md` foi alterado.

## 2. Os dois falsos verdes

- [x] 2.1 Presença passa a ser valor: campo obrigatório com null explícito reprova, e A2–A5 deixam de
      ser puláveis (ataque 1)
      `meta.get(field) is None` no lugar de `field not in meta`, e a mensagem distingue ausente de
      declarado-sem-valor. Selftest: `name declared with no value`, `tools declared as an explicit
      null` e `description declared as null`, os três reprovando em A1.

- [x] 2.2 `check_layout()` roda mesmo sem `agents/`, e o `return` antecipado sai de `main()` (ataque 2)

      `main()` deixa de retornar quando `agents/` não existe; `check_layout()` roda sempre e trata a
      ausência como o estado que ela própria reprova. Asserção positiva no selftest: com o diretório
      canônico apagado e uma cópia gerada presente, o A7 dispara.

## 3. As entradas que derrubavam a execução

- [x] 3.1 Diretório com sufixo `.md` é do A7, e `check_file` não reporta o mesmo defeito duas vezes (ataque 3)
      `check_file` retorna cedo em diretório, com o comentário dizendo que o A7 é o dono — antes o
      mesmo defeito produzia dois achados. Selftest: `a directory named like an agent file` -> A7.

- [x] 3.2 Arquivo ilegível e symlink pendurado viram achado nomeado; os demais agentes continuam sendo checados (ataque 6)
      `except (UnicodeDecodeError, FileNotFoundError, PermissionError, OSError)` vira achado que
      nomeia o caminho. O guard de diretório é `is_dir()` e **não** `is_file()` de propósito:
      `is_file()` também recusa symlink pendurado, que precisa virar achado. Selftest:
      `bytes that are not UTF-8` e `a dangling symlink`, os dois em A1.

- [x] 3.3 A saída é sanitizada em `add()`, para que um surrogate solto vire achado legível (ataque 5)
      `_printable()` na fronteira de `add()`. Selftest: `a lone surrogate in name` -> A2, e a regra
      anti-traceback prova que a execução completa.

- [x] 3.4 Âncora e alias YAML recusados por loader próprio, removendo a classe (ataque 4)

      `_NoAliasLoader(yaml.SafeLoader)` recusa `AliasEvent` com mensagem própria. Selftest:
      `a YAML anchor and alias in the frontmatter` -> A1.

## 4. As duas regras que faltavam

- [x] 4.1 A7 compara conteúdo além do nome: cópia gerada divergente é achado (ataque 7)
      A7 compara `read_bytes()` da fonte com o da cópia. Premissa conferida: `cmp -s` entre os três
      agentes e suas cópias em `plugins/*/agents/` -> idênticos. Selftest:
      `a generated copy that drifted from its source` -> A7.

- [x] 4.2 Qualquer espaço em branco depois dos `##` é aceito, e a decisão está escrita (ataque 8)

      `^#{2,}\s+When to invoke\s*$`. Decisão escrita no D6 e no comentário do próprio regex.
      Asserção positiva no selftest: cabeçalho com tabulação é **aceito**.

## 5. Selftest

- [x] 5.1 Um caso por defeito corrigido, cada um declarando o check que deve provocar
      Nove casos novos na lista `CASES`, cada um declarando o check que deve provocar — e um defeito
      pego pelo check errado continua reprovando, que é a lei que o arquivo já aplicava.

- [x] 5.2 Traceback passa a reprovar em **todos** os casos, não só nos que se esperava que quebrassem
      `Traceback (most recent call last)` na saída reprova em qualquer caso, com rótulo `CRASH`. É a
      generalização do que os ataques 3, 5 e 6 tinham em comum.

- [x] 5.3 Duas asserções positivas: o cabeçalho com tabulação é aceito; o diretório canônico ausente
      **não** silencia a checagem de órfão

      Cabeçalho com tabulação aceito, e diretório canônico ausente não silenciando o A7.

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      O caminho real destes dois scripts é serem rodados — pelo autor e pelos dois steps do CI. Os
      dois falsos verdes foram exercitados numa árvore descartável, para medir o **antes documentado**
      contra o depois observado.

      **Ataque 1, campo obrigatório com null explícito.** Um agente com os cinco campos declarados sem
      valor. Antes, pelo caminho de código lido: `findings: 0`, aprovação limpa. Observado agora:

          agents checked: 1   findings: 5
          nulls
             [A1 frontmatter] missing `name` — required for every agent (declared with no value, which states nothing)
             … idem description, model, color, tools
          exit=1

      **Ataque 2, diretório canônico ausente com cópia publicada.** Antes:
      `agents/ not found — nothing to check.` e exit 0. Observado agora:

          agents checked: 0   findings: 1
          ghost
             [A7 layout] plugins/testing/agents/ghost.md has no source at agents/ghost.md — regenerate with ./generate.sh, or delete it
          exit=1

      **Contra a árvore real**: `python3 scripts/validate-agents.py` ->
      `agents checked: 3   findings: 0` — o gate ficou mais estrito e os três agentes publicados já o
      cumpriam, sem edição.

      **Selftest**: `python3 scripts/selftest-validate-agents.py` -> `33/33 cases passed`, contra
      `22/22` antes desta change. Os 22 antigos continuam passando.

- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      - Ataques que tinham de deixar de passar e deixaram: **8/8** — os dois falsos verdes medidos
        ponta a ponta acima, e os outros seis cobertos por caso de selftest que declara o check dono.
      - Casos de selftest que tinham de reprovar e reprovaram: **20/20** antigos + **9/9** novos.
      - Casos que tinham de **passar** e passaram: **4/4** — o agente conforme, a cópia gerada com
        fonte, o cabeçalho com tabulação, e o repositório sem agentes (zero achados porque a checagem
        rodou, não porque foi pulada).
      - Defeito pego pelo check errado: **0** — continua sendo reprovação, e nenhum caso caiu nela.
      - Traceback em qualquer caso: **0/33**, agora medido em todos e não só onde se esperava.
      - Cópias geradas conferidas byte a byte contra a fonte: **3/3** idênticas, que é a premissa do
        A7 novo.

      Escapes conhecidos que continuaram em silêncio, de propósito: as seis linhas de *TRIED AND FOUND
      NOTHING* do relatório não viraram teste e estão nomeadas em E.4; e o frontmatter vazio
      degenerado continua rotulado pelo check errado — reprova, mas como "sem frontmatter". Não é
      falso verde, e não foi tocado.

- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      Três coisas, nenhuma silenciada:

      (a) **O escopo do item estava errado quando eu o abri: seis achados, e são oito.** Eu tinha lido
      só a cauda da saída do agente. Os dois que faltavam eram os graves — os únicos dois falsos
      verdes do conjunto. Levantado, comentado na issue e coberto pelos critérios. Está aqui e em E.4
      porque é a segunda vez nesta sequência que um número meu não bateu com a fonte.

      (b) **A primeira correção do ataque 3 produzia dois achados para um defeito.** Guardar
      `check_file` e deixar o A7 também reportar fazia um diretório `ghost.md/` aparecer duas vezes.
      Corrigido antes do commit: `check_file` retorna cedo em diretório e o A7 é o dono. E o guard é
      `is_dir()` e não `is_file()` de propósito — `is_file()` recusa symlink pendurado, que precisa
      virar achado.

      (c) **A bomba de expansão YAML nunca foi executada, nem antes nem agora.** O relatório a marcou
      `plausible` e disse que não executou payload; esta change remove a classe recusando âncora, e o
      caso de selftest prova que um alias é recusado — **não** que a bomba era explorável. A afirmação
      que fica é essa, e está em E.3(a).

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
      Nenhuma `SKILL.md` foi tocada: esta change mexe em dois scripts. `validate-skills.py` ->
      `skills checked: 38   findings: 0`.

- [x] Q.2 All touched skill content in English (catalog locale)
      Os dois scripts em inglês, comentários incluídos; a prosa desta change e do PR em português.

- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
      Nenhuma `description` foi tocada — nem de skill nem de agente. `validate-agents.py` ->
      `agents checked: 3   findings: 0`, com o gate mais estrito.

- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
      Nada restatado: a metodologia adversarial que produziu os achados é linkada a `bug-hunter`, e a
      regra de menor privilégio é de `agent-delegation` — o achado do `tools: ~` é uma violação dela
      passando pelo gate, não uma regra nova escrita aqui.

- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

      Identificadores em inglês nos dois scripts (`code-locale`). C9 rodou sobre as 38 skills sem
      achados.

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate harden-agent-validator --strict` green
      `openspec validate harden-agent-validator --strict` -> `Change 'harden-agent-validator' is
      valid`; `bash scripts/validate-rite.sh` -> `rite gate OK`.

- [x] V.2 Catalog discovery intact: 38 skills, 3 agentes, sem órfão e sem cópia divergente
      38 skills, 3 agentes. `validate-agents.py` 0 achados com o gate endurecido;
      `validate-repo-hygiene.py` -> `repo hygiene: 0 findings`; `./generate.sh` não move nenhuma cópia
      de agente.

- [x] V.3 README / docs updated where the change alters catalog composition or usage
      Nada a atualizar: a composição do catálogo não muda e o `README` já descreve o gate sem
      enumerar os checks. O que mudou é o rigor do validador, documentado no cabeçalho dele.

- [x] V.4 `openspec archive harden-agent-validator --yes` after all groups above are `[x]`
