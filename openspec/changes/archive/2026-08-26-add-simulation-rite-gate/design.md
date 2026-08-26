## Context

Três gates leem o rito hoje, cada um com uma pergunta diferente, e cada um declara no próprio
cabeçalho o que não consegue fazer:

| Script | Pergunta |
|---|---|
| `scripts/validate-rite.sh` | os grupos obrigatórios existem, nas posições certas? |
| `scripts/validate-rite-evidence.py` | uma caixa marcada diz o que rodou, ou só uma conclusão? |
| `scripts/validate-spec-rite.py` | existe change alguma? |

Nenhum pergunta se o artefato foi executado. A leitura de `scripts/validate-rite.sh` (commit
`afa547e`, 2026-08-26) mostra que a restrição posicional é menor do que o texto do schema sugere: o
script fixa apenas o **primeiro** grupo (`Evidence & Sources`) e o **último** (`Validation &
Closure`); `Quality Gates` só precisa existir. Isso abre espaço para um quinto grupo sem tocar em
regra nenhuma das existentes.

`scripts/validate-rite-evidence.py` declara em KNOWN LIMIT 3: *"Only the four E kinds have rules. A
fifth `E.5` a change invents is counted in the density report and otherwise unchecked."* As caixas
novas herdam essa arquitetura em vez de inventar outra.

## Goals / Non-Goals

**Goals**

- Uma change que toca skill, hook ou script entregue não fecha sem registrar o artefato exercitado
  pelo caminho real, com saída observada e matriz medida.
- Uma change que não toca artefato de runtime fecha o grupo em uma linha, explicitamente.
- As regras novas provam **forma**, e dizem no próprio cabeçalho que não provam honestidade.

**Non-Goals**

- Rodar a simulação automaticamente. O que é gatado é o registro; um harness que executasse a
  simulação de cada skill é outro item, muito maior.
- Julgar se a saída registrada é real. O repositório já decidiu essa classe
  (`openspec/changes/archive/2026-08-07-add-verify-before-claiming/design.md`): CI só prova que o
  registro é bem-formado, e converter defeito óbvio em defeito certificado é pior que não checar.
- Mexer nas quatro caixas `E.` nem nas posições dos grupos existentes.
- Autorar suítes de `claude plugin eval` enquanto o comando não roda nesta conta.

## Decisions

**D1 — Grupo novo antes de Quality Gates, não dentro de Validation & Closure.**
`Validation & Closure` é o último grupo e trata de fechamento — validate estrito, catálogo íntegro,
archive. Simulação é trabalho de prova, não de fechamento, e precisa acontecer **antes** da revisão
adversarial de qualidade, porque é ela que costuma produzir o defeito que a revisão vai discutir.
Alternativa descartada: uma caixa `V.0` dentro do grupo de fechamento — ficaria sujeita à regra de
posição do último grupo e misturaria duas perguntas num grupo só.

**D2 — Três caixas com formas diferentes, não uma regra uniforme.**
`validate-rite-evidence.py` já mediu e rejeitou a regra uniforme: *"a uniform 'command -> output'
rule was measured first and rejected: it failed 14 of 20 historical boxes… all correct as written."*
As três caixas herdam isso:

| Caixa | Forma exigida |
|---|---|
| `S.1` | ponto de entrada em backticks **e** saída observada (seta `->`), ou declaração explícita de que não há artefato de runtime |
| `S.2` | números da matriz — pelo menos um par `n/n` |
| `S.3` | nomeia o que escapou, ou declara explicitamente que nada escapou |

**D3 — `S.1` aceita a saída explícita "não há artefato de runtime".**
Mesma válvula que `E.3` e `E.4` já usam (regex `NEGATIVE`). Sem ela, uma change de documentação pura
seria obrigada a inventar uma simulação — que é padding, o oposto do que o gate quer.

**D4 — O passo de validação de plugin no CI passa a bloquear, com versão pinada.**
Probado em 2026-08-26 com `claude 2.1.246`: `claude plugin validate . --strict` passa neste
repositório, e contra fixture controlado (plugin com `SKILL.md` sem `description`) reprova com
`✘ Validation failed (--strict treats warnings as errors)`. Ele **não** pega `name` divergente do
diretório — isso é do `scripts/validate-skills.py`; os dois se complementam. O pin existe porque o
passo hoje usa `@anthropic-ai/claude-code@latest`, e gate bloqueante em versão flutuante reprova
build por mudança de terceiro.

**D5 — `claude plugin eval` fica fora, registrado como o destino.**
O harness nativo é superior ao que qualquer gate deste repositório consegue fazer: ele roda o caso,
pontua com graders (`regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`) e, sob
`--ablation with-without`, compara o braço com plugin contra o braço sem — que é a única medição que
responde "a skill mudou o comportamento?". Está em early access e não roda nesta conta (medido). O
gate desta change é o que funciona hoje; quando o acesso abrir, `S.1` passa a poder citar
`claude plugin eval --json --threshold` como o ponto de entrada exercitado, sem alterar regra nenhuma.

## Canonical Home & Cross-Links (MANDATORY)

| Regra transversal | Skill canônico (dono) | Ação nesta change |
|---|---|---|
| Não afirmar sem probe; relatar o que não pôde ser probado | `verify-before-claiming` | link, sem restatement — o grupo novo é a forma executável da mesma doutrina, e o template aponta para o skill |
| Rito backlog → PR, plano antes de código | `execute-backlog` | já canônico: a simulação entra no plano e na evidência do PR **lá**, não é redescrita no schema |
| Teste adversarial de uma mudança recém-implementada | `bug-hunter` | link: a simulação prova que o artefato roda; quebrar de propósito continua sendo do `bug-hunter`, e o template referencia isso em vez de repetir |
| Fronteira prosa/máquina nos nomes novos (`S.1`, grupo, funções) | `code-locale` | já canônico — os identificadores novos são ingleses e vêm do Glossary do item |

## Risks / Trade-offs

- **Quinto grupo virar cerimônia** → as caixas exigem número e fragmento observado; e change sem
  runtime fecha em uma linha.
- **Padding: caixa preenchida com saída inventada passa** → declarado no KNOWN LIMIT, como o gate
  irmão já declara. Forma é o que script prova; conteúdo é o revisor.
- **Regra inaplicável a trabalho de julgamento** → `S.1` aceita a declaração explícita de ausência.
- **CI bloqueante quebrando por versão** → pin explícito, com a versão probada registrada.
- **Change ativa em voo pegando o gate novo** → o gate lê changes ativas no merge; não há outra
  aberta além desta.

## Migration Plan

Nenhuma migração. O gate lê apenas changes ativas; o arquivo histórico não é relitigado, como já vale
para os gates irmãos.

## Open Questions

- A semântica exata do `--threshold` do `claude plugin eval` (compara score por grader, pass_rate por
  caso ou agregado?) e o schema do `aggregate-result.json` **não** constam da referência embutida do
  produto. Não são afirmados em lugar nenhum desta change; ficam para o item de adoção, que só
  começa quando o comando puder ser executado e medido.
- O nome da variável de ambiente que habilita o early access em clientes sem flags server-side também
  não consta da referência. O caminho documentado para pedir enablement é `/feedback`.
