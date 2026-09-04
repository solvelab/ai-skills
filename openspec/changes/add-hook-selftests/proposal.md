# Change: Dar selftest e gate de CI aos hooks backlog-rite e verify-rite

## Why

Três hooks vivem em `claude/global/hooks/`. `locale-rite.py` carrega `--selftest` — uma função
`evaluate()` isolada de stdin/stdout, uma lista de casos que devem disparar e ficar mudos, uma
asserção da forma da saída — e um step próprio em `.github/workflows/ci.yml:93-94`.
`backlog-rite.py` e `verify-rite.py` não têm nem um nem outro. Pior: `--selftest` hoje é aceito em
silêncio por ambos, porque nenhum dos dois lê `sys.argv`, então um step de CI escrito antes do modo
existir seria um no-op verde.

Medido em `d2918ed` (2026-09-04):

```
python3 claude/global/hooks/backlog-rite.py --selftest </dev/null; echo rc=$?
-> rc=0            (sem saída: o flag é ignorado e o hook leu stdin vazio)
```

Os dois hooks também estouram com traceback e exit 1 num payload JSON que não é objeto —
`backlog-rite.py:95` e `verify-rite.py:109` chamam `.get()` no que quer que `json.load` devolva:

```
echo '[]' | python3 claude/global/hooks/backlog-rite.py
-> AttributeError: 'list' object has no attribute 'get'
-> rc=1
```

`locale-rite.py:251` guarda esse caso com `isinstance(payload, dict)` e o selftest cobre.

Qualquer edição na lista de sinais — que o README convida o leitor a fazer — só é medida à mão. Um
falso positivo já conhecido e **aceito** (perguntas de diagnóstico contendo `erro`/`bug`/`falha`
disparam: `openspec/changes/archive/2026-08-07-add-backlog-first-rite/design.md:32` e `:78`) não
está fixado em lugar nenhum, então uma "correção" bem-intencionada poderia revertê-lo sem que nada
avisasse.

## What Changes

- `backlog-rite.py` e `verify-rite.py` ganham o mesmo formato do `locale-rite.py`: a decisão vira
  uma função pura `evaluate(payload) -> str | None`; `--selftest` é lido explicitamente de
  `sys.argv[1:]`; um payload que não é objeto JSON é ignorado (saída vazia, exit 0).
- Cada selftest fixa os casos que o design de cada hook já assume — inclusive o falso positivo
  aceito do backlog-rite, gravado como caso que **dispara**, e o fato de o verify-rite **não**
  silenciar em slash command (`verify-rite.py:78-79`).
- O lado inglês do sinal em `backlog-rite.py:47` ganha `fail\w*`, simétrico ao `falha` que já
  existe: "por que o teste falha?" dispara hoje e "why does the build fail?" fica mudo.
- Dois steps novos em `ci.yml`, logo após o step do `locale-rite`, rodam os dois selftests.
- `README.md` ganha uma frase, junto à lista do que silencia o hook, dizendo que perguntas contendo
  `erro`/`bug`/`falha` disparam e por quê.

## Capabilities

### Modified Capabilities

- `skills-catalog`: os requisitos *The development rite is enforced outside the model's discretion*
  e *The grounding rite is carried into context on correction* ganham a cláusula de que o artefato
  embarcado carrega um selftest exercitado pelo CI do repositório e ignora um payload que não é
  objeto, com o cenário correspondente. Hoje a cláusula de selftest existe para scripts de autoria
  (`skills-authoring/spec.md:259-263`) e para checks embarcados em skill
  (`skills-catalog/spec.md:579-585`), mas não para os hooks — lacuna de convenção da casa, não
  promessa quebrada: 5 dos 6 gates do CI são auto-testados.

## Impact

- `claude/global/hooks/backlog-rite.py`, `claude/global/hooks/verify-rite.py` — refatoração de
  `main()` mais o modo `--selftest`; comportamento para payloads válidos idêntico ao atual, exceto o
  sinal `fail` em inglês.
- `.github/workflows/ci.yml` — dois steps de `Validate`.
- `README.md` — uma frase na seção do hook de backlog.
- Nenhuma skill do catálogo muda: nenhum `SKILL.md` é tocado e a composição do catálogo (contagem,
  descoberta via `npx`) fica idêntica. Quem já tem os hooks wired em `~/.claude/settings.json` não
  precisa mudar nada: a linha de comando é a mesma.

Fora de escopo, por decisão registrada na issue #115: exclusão por forma de pergunta (reverte a
decisão de 2026-08-07 e foi medida silenciando pedidos reais), um `scripts/selftest-hooks.py`
central (o padrão da casa é selftest no próprio arquivo) e o wiring dos hooks na máquina do
mantenedor.
