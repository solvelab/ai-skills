# Design — camada agents/

## Context

O critério de admissão foi publicado em `f6663f1` (skill `agent-delegation`). Falta o lugar onde um
agente admitido é publicado, gerado e conferido.

Fatos medidos nos plugins oficiais da Anthropic instalados nesta máquina, lidos em 2026-09-07 em
`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/`:

- `feature-dev/`, `pr-review-toolkit/` e `plugin-dev/` carregam `agents/*.md` na raiz do plugin, e
  os três `.claude-plugin/plugin.json` **não** têm chave `agents` — a descoberta é por convenção de
  diretório.
- `plugin-dev/skills/agent-development/SKILL.md` fixa o frontmatter (`name`, `description`, `model`,
  `color` obrigatórios; `tools` opcional), os limites (`name` 3–50, `description` 10–5000, corpo
  20–10000), a seção *When to invoke* no corpo, e o efeito de subdiretório sobre o namespace.

## Goals / Non-Goals

**Goals:**

- Uma fonte canônica única para agentes, com a mesma lei de órfão que as skills já têm.
- Geração para os plugins, conferida por um gate estrutural, não por revisão.
- Três agentes que ganham existência pelos três testes, com a razão escrita.
- A redução da promessa multi-ferramenta declarada por escrito.

**Non-Goals:**

- Wrapper de agente para Codex, Cursor ou Copilot: as três ferramentas não têm o conceito, e
  fabricar equivalente seria inventar comportamento.
- Um quarto agente. A lista é fechada nesta change; outro é outro item.
- Trocar qualquer validador determinístico por agente.
- Medir ganho de contexto da delegação. Nenhuma alegação de ganho é feita.

## Decisions

**D1 — `agents/` na raiz, imposto pela ferramenta.** O bundle FULL é `source: "./"` em
`.claude-plugin/marketplace.json`, e a descoberta é por convenção de diretório na raiz do plugin.
`claude/agents/` não seria descoberto. A localização não foi escolhida por gosto: é a única que
funciona.

**D2 — Sem subdiretórios em `agents/`.** Um subdiretório muda o namespace para
`plugin:subdir:agent-name` e altera o nome de invocação. Agrupar agentes por domínio custaria o nome
que o usuário digita.

**D3 — O mapa agente -> grupo mora em `generate.sh`, não no frontmatter.** A whitelist de campos do
Claude Code é `name/description/model/color/tools`; um campo extra é risco sem ganho. O custo é uma
segunda fonte de verdade, pago com o mesmo guard pré-escrita que `GROUP_THEME` já tem
(`generate.sh:69-82`): um agente sem grupo derruba o script **antes** do primeiro `mkdir` e antes do
`rm -rf plugins/`, com a árvore intacta.

**D4 — A lista de agentes vai num parêntese separado, e o gate é irmão do H3.** O
`MEMBERSHIP_CLAIM` de `scripts/validate-repo-hygiene.py:42` é `\((\d+) skills?: ([^)]*)\)`: o
`[^)]*` engoliria qualquer coisa acrescentada dentro do mesmo parêntese. A descrição publicada passa
a ser `<tema> (N skills: …) (M agents: …)`, e um check irmão confere a segunda lista contra
`plugins/<g>/agents/`. Publicar sem lista nenhuma seria mais barato e foi recusado: a lei do
repositório é que uma contagem publicada tem um conjunto que a árvore confirma, e omitir os agentes
os tornaria invisíveis no marketplace.

**D5 — Nenhum dos três agentes escreve arquivo.** É a aplicação direta do terceiro anti-padrão de
`agent-delegation`. `bug-hunter-analyst` devolve os ataques e os casos de teste a escrever; quem
escreve é o loop principal, onde ficam autoria, revisão e desfazer. `tools` é declarado sempre, no
mínimo que o contrato exige.

**D6 — `skill-auditor` é advisory por construção, e o gate diz isso.** Ele cobre o que os checks
C1–C13 não sabem checar — doutrina restatada, cross-ref com semântica errada, claim sem medição. Um
agente nunca substitui um validador: `scripts/validate-skills.py` continua sendo a autoridade sobre
tudo que é mecânico.

**D7 — Nenhum dos três declara `model` fixo.** `inherit` é o default recomendado, e fixar um nome de
modelo aqui contradiria a própria regra de `agent-delegation` de escrever critério em vez de lista
de modelos. O tiering é escolhido no despacho, não congelado no arquivo.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Quando um trabalho vira agente; menor privilégio em `tools`; contrato de saída; tiering | `agent-delegation` | already canonical — esta change **usa** a regra e escreve a razão de admissão de cada agente contra ela |
| Escada de pesquisa, rotulagem de claim, relatório de não-encontrado | `verify-before-claiming` | link — o contrato de saída do `grounding-researcher` aponta para lá em vez de reproduzir a escada |
| Metodologia adversarial | `bug-hunter` | link — o `bug-hunter-analyst` executa o método daquela skill e não o restata |
| Como uma skill é escrita: frontmatter, casa canônica, claim medido | `skills-authoring` | already canonical — o `skill-auditor` audita contra essa spec, não contra um checklist próprio |
| Composição do catálogo publicado | `skills-catalog` | link + MODIFIED — passa a dizer que um agente não é uma skill do catálogo |
| Composição e autoria da camada de agentes | `agents-catalog` (esta change) | **new** — a casa canônica da nova classe de artefato |
| Volume de código | `lean-code` | link — o validador novo é stdlib-only, como os irmãos |

## Risks / Trade-offs

- **A camada inchar.** Mitigado pelo teste de admissão de `agent-delegation` e pela lista fechada de
  três; um quarto agente é outro item de backlog, com a razão escrita.
- **Duas fontes de verdade pelo D3.** Mitigado pelo guard pré-escrita e por um critério de aceite que
  exige provar a falha com a árvore intacta.
- **O parêntese novo derrubar o H3.** Mitigado pelo D4 e por rodar `validate-repo-hygiene.py` antes e
  depois.
- **`bug-hunter-analyst` acabar escrevendo teste.** Mitigado por `tools` sem `Write`/`Edit` (D5) —
  incapacidade, não pedido.
- **A promessa multi-ferramenta parecer quebrada.** É reduzida de fato, e por isso é declarada no
  README em vez de omitida.
- **O formato do frontmatter de agente mudar no harness.** É a razão de `agent-delegation` não o
  descrever: o formato mora em `agents-catalog`, que é onde a mudança dói uma vez só.
