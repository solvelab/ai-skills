# Change: Exigir prova de que o artefato foi exercitado antes de fechar o rito

## Why

O rito pergunta hoje o que foi lido, o que foi probado, se o frontmatter está uniforme e se a
validação estrita está verde. Todas essas respostas podem ser verdadeiras sem que o artefato tenha
sido **executado uma única vez** pelo caminho que o usuário percorre.

Medido em 2026-08-26, executando a issue #95 (PR #96): `--selftest` do detector verde, CI verde — e
a simulação end-to-end pelo harness real ainda achou dois defeitos:

```
tmp-sim/order_service/shipping_cost.py:1: valor_pedido   <- linha errada; :1 é o offset do fragmento
tmp-sim/order_service/shipping_cost.py:3: valor_pedido   <- depois da correção, a linha do arquivo
```

e o alcance da dispensa inline (a própria linha e a seguinte) não estava escrito em lugar nenhum —
erro cometido duas vezes dentro da própria change, uma no docstring e outra num fixture. Nenhum dos
dois seria visto por qualquer gate existente.

O mantenedor estabeleceu a regra em 2026-08-26: nenhuma melhoria de skill é aceita sem simulação
prévia usando a própria skill. Regra que vive só na conversa morre com a sessão — é o mesmo argumento
que já tirou o rito de backlog e o rito de grounding da prosa e os colocou em artefato de enforcement.

## What Changes

- Novo grupo obrigatório `Simulation & Field Proof (MANDATORY)` no template do schema, posicionado
  imediatamente antes de `Quality Gates (MANDATORY)`, com as caixas `S.1`, `S.2` e `S.3`.
- `scripts/validate-rite.sh` passa a exigir o grupo estruturalmente, como já faz com os outros três.
- `scripts/validate-rite-evidence.py` ganha regras de forma por caixa para `S.1`–`S.3`, no mesmo
  desenho por tipo que as caixas `E.` já usam, e três casos novos de `--selftest`.
- `openspec/schemas/skills-rite/schema.yaml` descreve o quinto gate ao lado dos quatro.
- `skills/execute-backlog`: a simulação entra no plano apresentado para aprovação e na evidência do PR.
- `.github/workflows/ci.yml`: o passo de validação de plugin **passa a bloquear**. Hoje ele está
  desligado duas vezes — `continue-on-error: true` e `|| true` — e nunca reprovou build nenhum.
  Junto vai o pin da versão, porque gate bloqueante em `@latest` quebra no calendário de release
  alheio.

**Não é BREAKING** para consumidores do catálogo: nenhum skill entra, sai ou muda de nome. É breaking
para quem tem change ativa neste repositório, e não há nenhuma além desta.

## Capabilities

### New Capabilities

_Nenhuma._ Nenhum skill novo entra no catálogo.

### Modified Capabilities

- `skills-catalog`: uma requirement ADICIONADA — o rito passa a gatar prova de execução, ao lado da
  requirement existente `The rite gates evidence before it gates quality`. A distinção entre as duas
  é o que justifica ser requirement nova e não emenda da antiga: aquela governa o que foi **lido e
  probado** antes de escrever; esta governa o que foi **executado** antes de declarar entregue.

## Impact

- `openspec/schemas/skills-rite/schema.yaml`, `openspec/schemas/skills-rite/templates/tasks.md`,
  `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py`,
  `skills/execute-backlog/SKILL.md` (+ `references/`), `.github/workflows/ci.yml`, `README.md`.
- `openspec/specs/skills-catalog/spec.md`, depois do archive.
- Espelhos gerados por `./generate.sh`.
- Quem abre change neste repositório passa a preencher mais um grupo; quem toca só documentação fecha
  o grupo em uma linha, declarando que não há artefato de runtime.

## Fora desta change, e por quê

`claude plugin eval` é o lar definitivo desta camada: casos em `evals/<caso>/prompt.md` com graders
`regex`, `tool_used`, `tool_order`, `file_exists`, `llm` e `baseline`, e um braço `--ablation
with-without` que mede se a skill **muda o comportamento** em vez de apenas carregar. Medido em
2026-08-26 com `claude 2.1.246`:

```
$ claude plugin eval .
`plugin eval` is currently in early access
```

Não roda nesta conta. Escrever suíte que não pode ser executada seria entregar artefato não
verificado — exatamente o que esta change existe para proibir. A adoção vira item próprio quando o
acesso abrir, e sua primeira entrega é uma suíte **rodada**, não escrita.
