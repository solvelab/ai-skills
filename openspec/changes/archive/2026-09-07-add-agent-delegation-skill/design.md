# Design — skill agent-delegation

## Context

O catálogo publica 37 skills e, fora delas, três artefatos de outra natureza: 4 hooks em
`claude/global/hooks/`, 8 validadores em `scripts/`, e as árvores geradas. A escolha entre esses
tipos já foi feita várias vezes e sempre bem — o problema é que o critério nunca foi escrito.

O que existe hoje, lido em `55d8a48`:

- A doutrina de tiering e de delegação está em
  [`claude/global/personal-rules.md`](https://github.com/solvelab/ai-skills/blob/master/claude/global/personal-rules.md),
  seção *Model & Effort Tiering*, dentro de um arquivo cujo próprio cabeçalho diz que é config
  pessoal do mantenedor e que o leitor não deve adotar os defaults às cegas.
- O limite de escopo do subagente está em
  `openspec/changes/archive/2026-07-18-add-backlog-skill/design.md:20`.
- A regra "advisory não é gate" está num comentário de
  [`claude/global/hooks/verify-rite.py`](https://github.com/solvelab/ai-skills/blob/master/claude/global/hooks/verify-rite.py).

Nenhum desses três lugares é lido por quem vai escrever a próxima regra. O `README.md:536-540`
define skill e não define mais nada.

## Goals / Non-Goals

**Goals:**

- Uma casa canônica para duas perguntas: qual artefato uma regra transversal vira, e quando
  despachar um subagente se paga.
- A regra sai da config pessoal e entra no catálogo, instalável por `npx skills` como qualquer
  outra skill.
- O critério de admissão de #198 fica escrito **antes** do primeiro agente existir.
- Cada linha da tabela de fronteira ancorada num artefato real deste repositório, não em prosa
  genérica.

**Non-Goals:**

- Criar qualquer agente, o diretório `agents/`, alvo em `generate.sh` ou validador — é #198.
- Publicar número de ganho. Esta skill é doutrina estrutural (qual artefato, qual privilégio), não
  alegação de desempenho; `skills-catalog` exige baseline medido para alegação de ganho e nenhuma é
  feita aqui.
- Mudar a ordem ou o comportamento de `backlog` e `execute-backlog`.
- Substituir qualquer validador determinístico por um agente. A skill diz exatamente o contrário.

## Decisions

**D1 — A skill decide o artefato, não só a delegação.** O nome poderia ter sido
`subagent-delegation`, cobrindo só a pergunta "delego ou não". Foi rejeitado: a pergunta útil vem
antes — *isto deveria sequer ser um agente?* — e a resposta em quatro de cada cinco casos neste
repositório é "vira script" ou "vira hook". Uma skill que só ensina a delegar empurra o leitor para
delegar. O nome `agent-delegation` mantém o gatilho onde o usuário o procura, e a primeira seção do
corpo é a fronteira, não a delegação.

**D2 — A tabela de fronteira cita artefatos reais, sob a restrição do C12.**
`scripts/validate-skills.py` (C12) reprova um caminho inline sob `claude/`, `research/`, `codex/`,
`cursor/`, `copilot/` ou `plugins/`, porque uma skill instalada sozinha não os tem. Os exemplos de
hook desta skill vivem exatamente ali. Solução: hooks são citados pela URL do repositório (forma
que o próprio C12 sugere na mensagem de erro), e `scripts/…`, `skills/…` e `openspec/…` ficam como
caminho, que o check não julga. A regra não perde a âncora e o gate fica verde.

**D3 — O tiering é escrito como critério, não como lista de modelos.** `personal-rules.md` nomeia
"Opus 4.8", "Fable 5", "Haiku 4.5 / Sonnet 4.6". Nomes de modelo envelhecem em semanas; a razão
não. A skill publica a razão — dificuldade da tarefa, contexto separado do subagente, e o efeito
sobre o cache de prompt do loop principal — e usa classes ("o modelo mais capaz disponível", "um
modelo barato") em vez da lista do dia. `personal-rules.md` continua livre para nomear os modelos
do mantenedor, agora como instância local de uma regra publicada.

**D4 — `personal-rules.md` linka em vez de definir.** É a lei de casa canônica única aplicada a um
arquivo que não é skill. O arquivo é publicado como exemplo do padrão de regras globais portáteis
(`README.md`, seção *Global Personal Rules*), então deixá-lo definindo a doutrina criaria duas
fontes divergentes sobre a mesma regra — exatamente o defeito que a lei existe para impedir.

**D5 — A skill declara-se não presa a versão.** C5 exige um bloco `Verified against` com data ou a
declaração de que a skill não depende de versão de ferramenta. Esta é doutrina: uma escada de
decisão e três testes, sem CLI e sem flag. Declara-se não presa a versão, como `lean-code` já faz.
O que **é** presa a versão — o formato do frontmatter de um agente — mora em #198, não aqui.

**D6 — Fronteira com `lean-code` escrita nos dois lados.** `lean-code` decide *quanto código* uma
mudança deixa; `agent-delegation` decide *qual artefato* a regra vira e *se um subprocesso é
despachado*. As duas se tocam quando a resposta é "não escreva nada". A `description` de cada uma
nomeia a outra, e o corpo desta linka a escada de reúso em vez de repeti-la.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Qual artefato uma regra transversal vira: skill, hook, script de CI ou agente | `agent-delegation` (esta change) | **move** — o mapa canônico de `skills-authoring` ganha a entrada |
| Quando despachar um subagente se paga; tiering de modelo e effort; menor privilégio em `tools`; contrato de saída | `agent-delegation` (esta change) | **move** — sai de `claude/global/personal-rules.md`, que passa a linkar |
| Volume de código; escada de reúso antes de escrever | `lean-code` | link — esta skill linka a escada e não a repete; a fronteira é escrita nos dois lados (D6) |
| Verificação de claim, escada de pesquisa, relatório de não-encontrado, guarda de escopo | `verify-before-claiming` | link — o contrato de saída de um subagente de pesquisa aponta para lá em vez de restatar a escada |
| Metodologia adversarial; quebrar o que já foi escrito | `bug-hunter` | link — `Do NOT use for` nos dois lados; delegar a análise não é fazer a análise |
| Lei de casa canônica única | `skills-authoring` | already canonical — esta change **usa** a regra e acrescenta uma entrada ao mapa |
| Prosa segue a língua do repo; camada de máquina em inglês | `code-locale` | already canonical — não é tocada |
| Rito de desenvolvimento forçado fora da discrição do modelo | `skills-catalog` | already canonical — esta change acrescenta um requisito irmão, não redefine o rito |

## Risks / Trade-offs

- **A skill ser lida como convite a delegar.** É o risco central e é o motivo do D1: a fronteira vem
  antes da delegação, e três dos quatro caminhos da tabela não são agente. O gate Q.3 cobra que a
  `description` não colida com nada e que o `Do NOT use for` esteja presente.
- **Publicar preferência do mantenedor como doutrina.** Mitigado por D3: entra o critério, não a
  lista de modelos.
- **C12 reprovar os exemplos de hook.** Antecipado por D2; a forma URL é a que o próprio check
  sugere.
- **`description` estourar 1024 caracteres parseados**, como aconteceu com 5 de 35 skills em
  2026-09-04. Medido antes do commit pelo mesmo cálculo do C10.
- **Sobreposição percebida com `lean-code`.** Mitigado por D6 e cobrado por Q.4.
- **A doutrina envelhecer quando #198 existir.** É esperado: #198 acrescenta o formato do agente e
  linka esta skill como teste de admissão. Esta skill não descreve formato de arquivo, justamente
  para não precisar mudar quando ele mudar.
