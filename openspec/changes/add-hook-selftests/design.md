## Context

Os três hooks de `claude/global/hooks/` compartilham o contrato "informa, nunca bloqueia, não
persiste nada", mas não a estrutura interna. Lidos em `d2918ed`:

- `locale-rite.py` (260 linhas): `evaluate(payload, check)` em 155-173, `selftest()` em 176-241 com
  lista de `(nome, deve_reportar, payload)`, uma linha `OK`/`FAILED` por caso, asserção da forma da
  saída em 226-235, linha de resumo em 240; `main()` em 244-256 lê `--selftest` de `sys.argv[1:]`
  (245) e guarda `isinstance(payload, dict)` (251). Step de CI em `ci.yml:93-94`.
- `backlog-rite.py` (109 linhas): `main()` em 89-105 faz tudo — `json.load`, `.get("prompt")`,
  `SKIP`, `CHANGE_SIGNALS`, `has_spec_rite`, `print`. Sem `argv`, sem guarda de tipo.
- `verify-rite.py` (120 linhas): `main()` em 103-116, mesma forma. Sem `argv`, sem guarda de tipo.

O `CHANGE_SIGNALS` do backlog-rite (linhas 38-52) é bilíngue por linha: cada verbo em pt-BR tem um
par em inglês. A linha 47 é a exceção: `fix|bug|erro|error|falha|quebr\w*|broken` — `falha` sem par
inglês. Medido por stdin: "por que o teste falha?" dispara e "why does the build fail?" fica mudo.

O falso positivo em perguntas de diagnóstico está registrado como decisão:
`openspec/changes/archive/2026-08-07-add-backlog-first-rite/design.md:31-32` ("A false positive
costs one line of context; a false negative costs traceability. The matcher is deliberately
generous.") e `:78-80` ("A generous matcher fires on pure questions containing 'erro'/'bug' →
accepted deliberately: the injected text says diagnosis is free").

## Goals / Non-Goals

**Goals:**

- `python3 <hook> --selftest` sai 0 com uma linha por caso e uma linha de resumo; qualquer regressão
  numa decisão fixada sai 1 e o CI fica vermelho.
- Payload que não é objeto JSON (`[]`, `"x"`, stdin vazio): saída vazia, exit 0, sem traceback.
- Comportamento para payloads válidos idêntico ao atual, exceto `fail(s|ed|ing)?` no lado inglês.
- O falso positivo aceito fica **fixado como caso que dispara**, com a decisão citada ao lado.

**Non-Goals:**

- Exclusão por forma de pergunta (`por que`, `why`, `?`). Reverte a decisão de 2026-08-07 e foi
  medida: silencia "por que não implementa o endpoint de login?" (pedido real) e não remove a classe
  que mira ("como corrijo esse bug?" continua disparando).
- Um selftest central em `scripts/`. O padrão da casa — `check-identifier-locale.py`,
  `locale-rite.py`, `validate-*.py` — é selftest no próprio arquivo, e o step de CI aponta para ele.
- Reproduzir o payload completo do harness. O selftest alimenta só os campos que o hook lê
  (`prompt`, `cwd`); isso fica declarado no docstring de cada hook (TR2 da issue).
- Wiring dos hooks em `~/.claude/settings.json` de qualquer máquina.

## Decisions

### D1 — A decisão vira `evaluate(payload) -> str | None`, e `main()` só faz I/O

Mesma divisão do `locale-rite.py:155`. A função recebe o dicionário já decodificado e devolve o texto
do lembrete ou `None`; `main()` lê stdin, guarda o tipo, chama `evaluate` e imprime. O selftest
chama `evaluate` diretamente — sem subprocess, sem tocar stdin/stdout — e por isso é hermético e
rápido.

Alternativa rejeitada: selftest por `subprocess.run([sys.executable, __file__], input=...)`. Cobre
`main()` de ponta a ponta, mas custa um processo por caso e não é o formato que o `locale-rite.py`
já estabeleceu. A cobertura de `main()` fica na simulação por stdin (`tasks.md`, grupo 3), que é o
caminho real do harness.

### D2 — A leitura do payload vira `read_payload(stream) -> dict | None`

O `isinstance(payload, dict)` do `locale-rite.py:251` fica dentro de `main()`, fora do alcance do
selftest. Aqui a leitura é extraída para uma função que recebe o stream, para que o selftest possa
alimentar `io.StringIO("[]")`, `io.StringIO('"x"')` e `io.StringIO("")` e afirmar `None` sem
subprocess. É o único ponto em que a forma diverge do `locale-rite.py`, e diverge para cobrir FR2
(payload malformado) no CI, não só na simulação.

Um `prompt` que existe mas não é string (`{"prompt": 42}`) é tratado como ausente pelo mesmo motivo:
`SKIP.search(42)` estouraria em `TypeError`, e o contrato do hook é nunca derrubar o turno.

O mesmo vale para o outro campo que o backlog-rite lê: `{"cwd": 42}` (ou lista, ou objeto) estourava
em `os.path.join` com `TypeError` e exit 1 — medido na revisão, depois da guarda do `prompt` ter
entrado sozinha. `has_spec_rite()` passa a aceitar só string não-vazia e cai em `os.getcwd()` no
resto. Os dois casos do selftest que cobrem esse fallback não leem o cwd de quem roda o teste (TR1):
movem o cwd do processo para uma das fixtures durante a chamada e o restauram em seguida — ver D4.

### D3 — `--selftest` é lido de `sys.argv[1:]`, nunca de stdin

Hoje `python3 backlog-rite.py --selftest` lê stdin, encontra vazio, sai 0 e não imprime nada. Um step
de CI escrito assim seria verde para sempre. O parse explícito é o que torna o step honesto, e o
selftest imprime uma linha por caso mais uma de resumo pelo mesmo motivo: um step que passa sem
nenhuma saída é indistinguível do no-op de hoje, e um leitor do log do CI precisa ver os casos.

Ler `--selftest` por pertinência (`"--selftest" in sys.argv[1:]`, a forma do `locale-rite.py:245`)
não fecha a porta: `--self-test` grafado errado num step cai no caminho do stdin, lê vazio e sai 0 —
o mesmo no-op verde, medido na revisão. Por isso `argv` é comparado por igualdade: exatamente
`["--selftest"]` roda o selftest, vazio lê stdin, qualquer outra coisa imprime o usage em stderr e
sai 2. O `locale-rite.py` carrega a fraqueza herdada e fica como follow-up, fora desta change.

### D4 — A fixture de `openspec/` vive em `tempfile.TemporaryDirectory()`

`has_spec_rite()` lê `payload["cwd"]` com fallback em `os.getcwd()`. O selftest cria dois diretórios
temporários — um com `openspec/` dentro, outro sem — e passa cada um como `cwd`. Os dois casos que
exercitam o fallback (`cwd: 42`) não podem passar a fixture pelo payload, então movem o cwd do
processo para ela com `os.chdir` num `try/finally` que restaura o anterior, e afirmam a frase do
spec-rite nos dois sentidos: presente com a fixture que tem `openspec/`, ausente com a outra. Um
fallback que ignorasse o cwd do processo, ou que sempre omitisse a frase, derruba um dos dois. A
revisão mediu a forma anterior desse caso (um só, sem `chdir`, `spec_sentence=None`) fazendo
`os.path.isdir(<cwd real>/openspec)` — o que a issue, este D4 e o docstring diziam não acontecer.

Alternativa rejeitada: um parâmetro `default_cwd` em `has_spec_rite()` só para o teste. Deixaria a
linha `os.getcwd()` real sem cobertura — o selftest provaria o parâmetro, não o fallback.

Assim o selftest nunca faz `stat` no cwd real, e o resultado é o mesmo rodando do repositório, de
`/tmp` ou do runner do CI (TR1 da issue). O que ele ainda lê do cwd real é só o **caminho** — a
string devolvida por `os.getcwd()` para restaurar depois, e a que `tempfile` consulta ao escolher o
diretório temporário — nunca o que existe dentro dele.

### D5 — O falso positivo aceito é um caso que **dispara**, com a decisão citada no comentário

"por que o teste falha?" entra na lista com `should_fire=True` e um comentário apontando para
`2026-08-07-add-backlog-first-rite/design.md:32` e `:78`. O selftest passa a ser onde a decisão fica
visível: quem tentar "corrigir" o falso positivo vê o caso quebrar e lê o porquê antes de mexer.

### D6 — `fail(s|ed|ing)?` entra no lado inglês da linha 47, medido e não `fail\w*`

A issue pediu `fail\w*` "para simetria com `falha`". Probado contra o regex antes de decidir
(`CHANGE_SIGNALS.search`, via `importlib` no próprio hook):

| Lado | Expressão | Casa | Não casa |
|---|---|---|---|
| pt-BR (já existia) | `\bfalha\b` | "o teste falha" | "falhou", "falhando", "falhas", "falhar", "falharam" |
| inglês, forma pedida | `fail\w*` | fail, fails, failed, failing, **failure, failover, failsafe** | — |
| inglês, forma adotada | `fail(s|ed|ing)?` | fail, fails, failed, failing | failure, failover, failsafe |

Duas alternativas fechavam a assimetria: estreitar o inglês ou alargar o português para `falh\w*`.
Fica o estreitamento, por dois motivos. FR3 da issue exige comportamento idêntico para todo payload
válido exceto o sinal `fail`, e alargar `falha` mudaria prompts em português ("o teste falhou
ontem" passaria a disparar) — fora do que a issue autorizou. E os três substantivos que `\w*`
arrasta (failure, failover, failsafe) são conceito, não pedido: "what is a failover cluster?"
disparando é custo de contexto sem contrapartida de rastreabilidade.

O lado inglês continua mais amplo que o português (quatro formas do verbo contra a palavra nua) —
de propósito e agora medido, coerente com a assimetria escolhida (falso positivo barato, falso
negativo caro). O selftest fixa os dois lados da decisão: "why does the build fail?" e "the tests
are failing" disparam; "what is a failover cluster?" fica mudo, e restaurar `fail\w*` deixa esse
caso vermelho.

### D7 — O verify-rite fixa que slash command **não** silencia

`verify-rite.py:78-79` diz por quê: "a correction typed inside a slash command still deserves the
reminder". É o oposto do backlog-rite, e um caso do selftest de cada hook fixa cada lado, para que
uma "harmonização" futura não apague a diferença sem ler o comentário.

### D8 — Dois steps em `ci.yml`, um por hook, ao lado do step do `locale-rite`

Um step por script segue o padrão das linhas 87-94 e 113-117: cada gate tem o próprio nome na lista
de checks do pull request, então uma regressão nomeia o hook sem abrir o log.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Um check embarcado carrega selftest e declara o que não cobre | `skills-catalog` (spec do repositório, *A shipped enforcement script declares what escapes it*) | already canonical — o delta estende a mesma cláusula aos dois hooks; nada é reescrito |
| Prova observada pelo caminho real antes de declarar entrega | `verify-before-claiming` | already canonical — citado no grupo de simulação de `tasks.md` |
| Rito backlog-first e o falso positivo aceito do matcher | `backlog` / `execute-backlog` (doutrina) + `2026-08-07-add-backlog-first-rite/design.md` (decisão) | already canonical — o selftest e o README **citam** a decisão, não a reescrevem |
| Rito anti-achismo e o limite conhecido do verify-rite | `verify-before-claiming` | already canonical — o docstring do hook já aponta para a skill |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — `evaluate`, `read_payload`, `selftest`, ids de step |

Nenhuma skill do catálogo é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **Refatorar `main()` muda a saída sem ninguém notar** → a asserção de forma do selftest afirma que
  o que dispara é uma string que começa pelo cabeçalho do lembrete (`DEVELOPMENT RITE` /
  `GROUNDING RITE`) e, no backlog-rite, que a frase do spec-rite está presente só com `openspec/`
  no cwd. A simulação por stdin (grupo 3) compara os 8 prompts antes e depois.
- **`fail(s|ed|ing)?` dispara em mais prompts em inglês** → aceito e registrado (D6) com o conjunto
  medido: três prompts do corpus passam a disparar (fail / failing / failed) e os de substantivo
  (failover, failure, failsafe) ficam mudos; o lado português não muda.
- **O selftest não reproduz o payload real do harness** → declarado no docstring de cada hook: só
  `prompt` e `cwd` são alimentados, que são os únicos campos lidos. O que um payload real prova e o
  selftest não é se o harness ainda manda esses campos com esses nomes — isso fica com a simulação
  e com a doc pinada (`code.claude.com/docs/en/hooks`).
- **Um payload malformado que não seja `[]`, `"x"` ou vazio** (por exemplo `null`, `42`) → `null` e
  `42` não são `dict` e caem na mesma guarda; fixados como casos do selftest junto com os três da
  issue.

## Open Questions

Nenhuma. As três lacunas que poderiam virar achismo — se `--selftest` hoje é ignorado, se um payload
`[]` estoura, e se "why does the build fail?" fica mudo — foram medidas por stdin antes de escrever,
e estão em `tasks.md` com comando e saída.
