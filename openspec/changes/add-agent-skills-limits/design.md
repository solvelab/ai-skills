## Context

O catálogo diz seguir o padrão Agent Skills (`README.md:25`, `:381`), cuja especificação fixa
`description` em 1–1024 caracteres e `compatibility` em 1–500. O validador de referência do
padrão é o pacote PyPI `skills-ref` (0.1.1), binário `agentskills`; em `skills_ref/validator.py`
os limites são `MAX_DESCRIPTION_LENGTH = 1024` e `MAX_COMPATIBILITY_LENGTH = 500`, medidos com
`len()` sobre o valor parseado do frontmatter, e há uma whitelist de campos aceitos
(`ALLOWED_FIELDS`, linhas 15-22).

Cinco skills estouram o teto de description e uma delas também o de compatibility. Três gates do
repositório olham para o frontmatter e nenhum mede tamanho: o loop de shell do CI (presença e
valor de campos), `scripts/validate-skills.py` C4 (description contra o corpo, sobre o bloco cru
em `:223`) e `claude plugin validate --strict` (aceita 2000 caracteres, medido na issue #112).

O spec `skills-authoring` tem um requisito que produz o excesso — *Triggers live in the
description, not the body* manda dobrar todo gatilho do corpo para a description — e nenhum que o
limite.

## Goals / Non-Goals

**Goals:**

- Todas as 35 skills passam em `agentskills validate` (skills-ref 0.1.1).
- O teto fica escrito no spec ao lado do requisito que dobra gatilhos, com a regra de para onde
  vai o que não cabe.
- O CI mede o teto duas vezes, por caminhos independentes: um check próprio auto-testado (C10) e
  o validador de referência pinado.
- Nenhuma frase de gatilho entre aspas se perde nas 5 descriptions encurtadas.

**Non-Goals:**

- Tornar fatal a linha `checks skipped` de `validate-skills.py`: o spec exige que a falta de
  ferramenta seja reportada, não que falhe (*A missing tool is reported, not passed over*).
- Reduzir o orçamento total de tokens das 35 descriptions abaixo do teto da spec.
- Mudar como o Claude Code roteia skills, ou mexer em `ci.yml:84` (`|| true` do `apt-get`).
- Cobrir a whitelist de campos do validador de referência em C10: isso é o que o step pinado faz.

## Decisions

### D1 — C10 mede o valor YAML parseado, em caracteres, com os mesmos números do validador de referência

O C4 mede o bloco cru (`fm[1]` de `text.split("---", 2)`), que carrega a indentação e as quebras
do folded scalar: 26–36 caracteres a mais que o valor parseado, medido sobre as 35 skills
(`svg-animation` dá 1024 cru contra 998 parseado). Um gate sobre o bloco cru reprovaria uma
skill que o validador de referência aceita. C10 faz `yaml.safe_load` do bloco — o PyYAML já é
dependência do C3 — e compara `len(description)` e `len(compatibility)` com
`MAX_DESCRIPTION_CHARS = 1024` e `MAX_COMPATIBILITY_CHARS = 500`, nomes do Glossary da issue #112
que espelham `MAX_DESCRIPTION_LENGTH`/`MAX_COMPATIBILITY_LENGTH` de `skills_ref/validator.py`.
`len()` em Python conta code points, não bytes, exatamente como o validador de referência — as
descriptions carregam `ã`, `ç`, `—`, e uma contagem em bytes divergiria.

Quando o PyYAML não está instalado, C10 entra na lista `checks skipped`, como o C3 já faz, e não
conta como aprovado (Non-Goal 1).

### D2 — Dois medidores independentes, não um

O step pinado do CI prova conformidade com o padrão pelo mesmo binário que um consumidor usaria;
C10 prova que o repositório entende a própria regra e a auto-testa por mutação. Se só o step
existisse, a regra viveria fora do repositório e mudaria no calendário do upstream; se só o C10
existisse, "seguimos o padrão" continuaria uma afirmação sem probe. Os dois divergirem no limite
é o risco listado na issue; a mitigação é os dois contarem `len()` do valor parseado (D1).

### D3 — O pin é exato e o comentário do step diz por quê

`skills-ref==0.1.1` na mesma linha de `pip` de `ci.yml` que instala o PyYAML, para que a falta
do pacote falhe alto no primeiro step que o usa. O comentário do step segue o estilo das linhas
127-128 do workflow (o pin do `claude-code`): um upstream novo poderia alargar ou apertar a
whitelist de campos (`validator.py:15-22`) e quebrar o build no calendário de outro. O step
declara o que cobre (nome, description, compatibility, whitelist) e o que não cobre (corpo,
referências, cross-refs, blocos de código — que ficam com `validate-skills.py`).

### D4 — A dobra respeita o teto; o que não cabe vai para o corpo ou para `references/`

O requisito *Triggers live in the description* fica; ganha a cláusula de que a dobra respeita o
teto de *Uniform frontmatter metadata*. Regra de precedência quando não cabe tudo: ficam na
description as frases de gatilho entre aspas, as condições "Use when" e a cláusula "Do NOT use"
(são o que roteia); saem primeiro as sentenças "Covers …" e os detalhes de configuração
(caminhos de arquivo, listas de degraus), que vão para a primeira linha do corpo ou para
`references/`. A tabela antes/depois das frases entre aspas fica em `tasks.md` e é o critério de
"nada se perdeu".

### D5 — `When to use this skill` entra na lista de headings meta

`skills/api-resilience-testing/SKILL.md:43` carrega uma seção `## When to use this skill` que
repete a description palavra por palavra e escapa do C8 porque `META_HEADING` só casa quatro
títulos. O regex ganha esse quinto título e a seção é removida — o conteúdo já está na
description, então nada é dobrado. A mutação nova do selftest injeta exatamente esse título.

### D6 — Ordem: gate primeiro, edição depois, no mesmo PR

O C10 é escrito antes das descriptions serem editadas e reprova as 5 (TR4 da issue). O commit
que encurta as descriptions é o que deixa o validador verde. Assim a história do branch mostra o
gate falhando sobre o estado real, não só passando sobre o estado corrigido.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Teto de caracteres de `description` e `compatibility` | `skills-authoring` (spec do repositório), requisito *Uniform frontmatter metadata* | move: a regra passa a morar no spec; C10 e o step do CI só a aplicam |
| Gatilhos moram na description, não no corpo | `skills-authoring`, requisito *Triggers live in the description, not the body* | already canonical — ganha a cláusula de teto, sem duplicar a regra em nenhuma skill |
| Um check declara o que não cobre | `skills-catalog` (*The uncovered part is declared, not implied*) + `skills-authoring` (*Partial coverage is declared, not implied*) | already canonical — C10 e o step novo aplicam a regra dentro de si |
| Prova observada, não esperada, antes de declarar entrega | `verify-before-claiming` | already canonical — o grupo de simulação de `tasks.md` cita, não reescreve |
| Prose em português, camada de máquina em inglês | `code-locale` | already canonical — os identificadores novos (`MAX_DESCRIPTION_CHARS`, `C10 frontmatter limits`) vêm do Glossary da issue #112 |
| Conteúdo que sai da description de `code-locale` (o que a skill cobre) | `code-locale` | move: da description para o primeiro parágrafo do corpo da própria skill |
| Conteúdo que sai da description de `verify-before-claiming` (degraus da escada) | `verify-before-claiming` | already canonical — os degraus já estão em `## The research ladder` e `references/research-ladder.md`; a description passa a só nomear a escada |
| Conteúdo que sai das descriptions de `backlog` / `execute-backlog` (arquivos de config, wizard) | `backlog` (`references/backlog-config.md`) | already canonical — o corpo das duas skills já aponta para lá; a description deixa de repetir os caminhos |
| `When to use this skill` de `api-resilience-testing` | `api-resilience-testing` (description) | move: seção removida, conteúdo já estava na description |

Nenhuma skill passa a reescrever doutrina de outra: as edições são só na description, no primeiro
parágrafo do corpo e na `compatibility`.

## Risks / Trade-offs

- **Cortar gatilho muda roteamento.** Mitigação: a tabela antes/depois das frases entre aspas
  (D4) é critério de aceitação, e o grupo de simulação roda 3 prompts realistas por skill editada
  contra as descriptions novas, registrando para qual skill cada um roteia.
- **`skills-ref` 0.1.x muda a whitelist ou o limite.** Mitigação: pin exato e comentário no step
  (D3); bump deliberado depois de rodar localmente.
- **C10 e o validador de referência divergem no limite.** Mitigação: ambos contam `len()` do
  valor parseado (D1); a simulação roda os dois sobre a mesma cópia inflada e registra os dois
  números.
- **O binário `agentskills` pode não estar no PATH do runner depois de `python3 -m pip install`.**
  Não há como probar o runner daqui; fica registrado como lacuna em `tasks.md` E.3 e o primeiro
  run do CI é a prova. Não existe `python -m skills_ref` como alternativa (probado: `No module
  named skills_ref.__main__`); `python -m skills_ref.cli` existe e é o fallback se o PATH falhar.
- **`backlog` fica em 1000 caracteres, a 24 do teto.** A próxima dobra de gatilho nessa skill
  tem de seguir D4 (tirar antes de pôr). O C10 é o que avisa.

## Open Questions

Nenhuma sobre o comportamento das ferramentas: os limites, o nome do binário, o modo de contagem
e a whitelist foram lidos no pacote instalado e a página da especificação foi baixada. A única
incerteza é a de ambiente do runner (PATH), registrada acima como risco e em `tasks.md` E.3.
