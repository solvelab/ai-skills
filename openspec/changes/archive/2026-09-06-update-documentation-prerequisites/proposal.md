# Change: Pré-requisito colhido do manifesto, com valor que aprova e com egress

## Why

A `documentation` manda extrair fatos em vez de inventá-los e nomeia as fontes
(`skills/documentation/SKILL.md:36-37`): env var do módulo de config, endpoint do router, comando do
manifest, **porta do compose**. E manda verificar cada passo
(`skills/documentation/references/templates.md:223-224`): "the command that confirms it worked and
the output it should print".

As duas regras param cedo, e o custo foi medido em `solvelab/feldt` — um serviço documentado com esta
skill, com sete páginas e duas guardas de documentação em CI.

**A lista de fontes não alcança a superfície de implantação.** O `docs/SETUP.md` §1 do feldt lista
quatro pré-requisitos. O `deploy/feldt.yaml`, dois diretórios ao lado, carrega `cpu: 50m`/`200m`
(`:155`,`:158`), `memory: 128Mi`/`256Mi` (`:156`,`:159`), `storage: 1Gi` (`:39`), `nodePort: 30080` e
`30081` (`:63`,`:88`), `runAsUser`/`fsGroup: 65532` (`:113-114`) e `readOnlyRootFilesystem: true`
(`:162`). Nenhum chegou ao §1. A regra cobre porta do compose e para ali, então requests, limits,
tamanho de volume, uid e modo de filesystem não têm fonte nomeada — e o que não tem fonte é composto
de memória.

**Verificação sem valor de aprovação.** O mesmo §1 traz `kubectl version --output=json | head -5` com
"Esperado: um bloco JSON com clientVersion e serverVersion". Isso prova que o `kubectl` fala com *um*
cluster; não diz qual versão passa. `grep -rniE 'kubernetes 1\.|kubectl 1\.|versão mínima|minimum
version'` no repositório inteiro do feldt devolve zero linhas. A regra do `templates.md` pede "the
output it should print", e a saída que esse comando imprime **é** um bloco JSON — imprimir não é
aprovar.

**Egress não é pré-requisito em lugar nenhum.** Nenhuma das nove páginas do feldt declara que o
cluster precisa alcançar `api.telegram.org`, `chat.googleapis.com` ou a URL de webhook. Porta de
entrada se documenta; destino de saída não. O agravante é o sintoma: o feldt é um dead man's switch,
e egress bloqueado produz silêncio — o estado que o produto existe para distinguir de saúde.

## What Changes

- `skills/documentation/SKILL.md`: a linha *Extract the facts* passa a nomear o manifesto de
  implantação como fonte de recursos, armazenamento, portas, identidade e modo de filesystem; regra
  nova de que pré-requisito sondável carrega o comando **e o valor que aprova**; regra nova de que
  destino de saída é pré-requisito, com a razão de a falha dele ser silenciosa.
- `skills/documentation/references/templates.md`: as convenções do `docs/SETUP.md` ganham a lista de
  categorias de pré-requisito, cada uma com a fonte externa que a pede, e a forma de tabela de
  diagnóstico para sintoma único com remédios opostos.
- `metadata.version` da `documentation`: `3.0.3` -> `3.1.0`; árvores geradas regeneradas.
- Delta em `skills-authoring`: requisito ADDED *A prescribed verification states what passes*,
  generalizando o segundo defeito para todo o catálogo.

## Deliberately not done

- **Consertar o `docs/SETUP.md` do feldt.** Ele é a evidência de campo deste item; consertá-lo aqui
  confundiria a prova com o conserto. Item próprio, no repositório dele.
- **Validador para o requisito autoral novo.** Um detector de "verificação sem critério" sobre prosa
  produziria falso positivo, que é o defeito que este repositório mais rejeita. A ausência é
  declarada no `design.md`, conforme o cenário *Partial coverage is declared, not implied*.
- **Números concretos de hardware na skill.** O requisito *Prescribed numbers carry the rule that
  produces them* proíbe: o número certo é do projeto documentado, e a skill entrega a regra que o
  produz.
- **Varredura do catálogo por violações do requisito novo.** Achado registrado em E.4, não entrega
  deste item.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skills-authoring`: ADDED requirement — uma skill que prescreve um passo de verificação SHALL dizer
  o valor que aprova, e não só o comando e a saída que ele imprime. Uma verificação sem critério de
  aprovação não verifica; ela tranquiliza, que é pior que não verificar.

## Impact

- `skills/documentation/SKILL.md` e `skills/documentation/references/templates.md` — as duas skills
  afetadas são uma só; nenhuma outra skill do catálogo muda.
- `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/` — regenerados por `generate.sh`.
- Consumidores: projetos documentados com esta skill passam a receber pré-requisito colhido do
  manifesto e com valor de aprovação. Não muda a composição do catálogo, então a descoberta por
  `npx` fica intacta e nenhuma contagem publicada se move.
