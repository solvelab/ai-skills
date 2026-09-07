# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `36091e7` (master, base de `backlog/198-agents-layer`) em 2026-09-07:

      - `generate.sh:1-130` — guards de VERSION e de `GROUP_THEME`, `group_of`, `category_of`, e o
        laço de pré-checagem que falha antes do primeiro `mkdir` e antes do `rm -rf plugins/`.
      - `generate.sh:218-300` — `group_description()`, o laço de plugins e o bloco Python que
        reescreve `marketplace.json` e `.claude-plugin/plugin.json`.
      - `scripts/validate-repo-hygiene.py:33-44` — `COUNT_FILES`, `COUNT_CLAIM`,
        `UNSCOPED_COUNT_CLAIM` e `MEMBERSHIP_CLAIM`; `:78-160` — H2 e H3 inteiros, incluindo
        `plugin_groups()` e `_membership_finding()`.
      - `scripts/validate-skills.py` — docstring com C1–C13, `:351-364` (C8 e `META_HEADING`),
        `:451-484` (C11), `:485-555` (C12 e `CATALOG_ONLY_ROOTS`), `:611-624` (C7, a lei de órfão).
      - `.github/workflows/ci.yml:120-178` — os steps de validação e os selftests já existentes.
      - `README.md:439-552` — árvore de estrutura, arquitetura multi-ferramenta e *What is a skill?*.
      - `skills/agent-delegation/SKILL.md` — os três testes de admissão, os três anti-padrões e a
        regra de menor privilégio, publicados em `f6663f1`.
      - `openspec/specs/skills-catalog/spec.md:10-41` — *Catalog composition after the quality
        review*, copiado por completo no delta antes de ganhar o parágrafo novo.
      - `openspec/specs/skills-authoring/spec.md:11-23` — o mapa canônico, já com `agent-delegation`
        desde `36091e7`.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      Convenção de agente, lida nos plugins oficiais da Anthropic instalados nesta máquina em
      2026-09-07:

      `ls ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/feature-dev/` ->
      `.claude-plugin/  agents/  commands/  LICENSE  README.md`; idem `pr-review-toolkit` e
      `plugin-dev` (este último com `skills/` também).

      `cat …/feature-dev/.claude-plugin/plugin.json` -> `{ "name": "feature-dev", "description": …,
      "author": … }` — **sem** chave `agents`, logo a descoberta é por convenção de diretório.

      `…/plugin-dev/skills/agent-development/SKILL.md` -> frontmatter `name`, `description`, `model`,
      `color` obrigatórios e `tools` opcional ("If omitted, agent has access to all tools");
      `name` 3–50 minúsculas/dígitos/hífen; `description` 10–5000; system prompt 20–10000;
      seção *When to invoke* no corpo; "With subdirectories: `plugin:subdir:agent-name`".

      `openspec new change add-agents-layer --schema skills-rite` -> `Schema: skills-rite`.
      `openspec validate add-agents-layer --strict` -> `Change 'add-agents-layer' is valid`.
      `openspec list` -> `No active changes found.` antes desta change.

      `ls -1 skills/ | wc -l` -> `38`; `git log --oneline -1` -> `36091e7`.

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Três lacunas, nenhuma preenchida com substituto plausível:

      (a) **RESOLVIDA por medição, não por inferência.** A dúvida era se o Claude Code descobre
      `agents/` na raiz do bundle FULL (`source: "./"`), já que os plugins oficiais lidos têm `source`
      apontando para um subdiretório. Medido: uma sessão headless rodando de um diretório que **não** é
      este repositório, com `--plugin-dir /home/diegops/ai-skills`, lista
      `ai-skills:bug-hunter-analyst`, `ai-skills:grounding-researcher` e `ai-skills:skill-auditor`.
      A raiz do repositório carregada como plugin expõe os três, que é exatamente o que `source: "./"`
      significa. Detalhe no grupo Simulation.

      (b) **Se existe validador de referência para agentes, como `skills-ref` é para skills.** Não
      foi encontrado nenhum. O gate desta change é próprio (`validate-agents.py`), e a ausência de um
      validador upstream fica declarada: os limites que ele aplica vêm do `agent-development`
      da Anthropic lido em E.2, não de uma especificação aberta.

      (c) **Se o campo `color` é obrigatório de fato ou só documentado como obrigatório.** O
      `agent-development` diz "required"; nenhum erro foi observado com ele ausente porque nenhum
      agente sem `color` foi carregado. O validador o exige, seguindo o documento, e a lacuna fica
      registrada em vez de virar afirmação sobre o runtime.

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Follow-ups anotados e **não** feitos:

      - As 10 skills `r3f-*` não citam nenhuma skill de processo — ilha desconectada do grafo de
        cross-links, achada ao mapear o catálogo. Item próprio.
      - Converter as duas chamadas de `Explore` em `backlog` e `execute-backlog` para agentes
        próprios: declarado fora de escopo na issue #198.
      - Um quarto agente. A lista é fechada aqui; outro passa pelos três testes num item próprio.
      - `UNSCOPED_COUNT_CLAIM` cobre `topics|skills`; passa a cobrir `agents` nesta change, e não
        foram acrescentados outros substantivos.
      - A entrada FULL do marketplace e o manifesto raiz continuam dizendo `all N` só de skills, e
        **não** nomeiam os três agentes que o bundle também instala. Nomeá-los exigiria estender o
        H4 ao manifesto raiz, que é uma decisão sobre se `all N` ganha um irmão — item próprio,
        não feito aqui. Publicar a lista sem o gate seria uma contagem que a árvore não confirma.

## 2. A fonte canônica e os três agentes

- [x] 2.1 `agents/grounding-researcher.md` — executa a escada de `verify-before-claiming` para UMA
      afirmação; só leitura; contrato de saída = afirmação -> degrau alcançado -> linha de evidência,
      mais os degraus que não responderam
- [x] 2.2 `agents/bug-hunter-analyst.md` — lê um diff e devolve ataques e casos de teste a escrever;
      **sem** `Write`/`Edit` (D5)
- [x] 2.3 `agents/skill-auditor.md` — audita `skills/<name>/` contra `skills-authoring` no que
      C1–C13 não sabem checar; advisory, nunca gate (D6)
- [x] 2.4 Os três com frontmatter completo, `tools` declarado no mínimo, `model: inherit` (D7) e
      seção *When to invoke* no corpo
      `python3 scripts/validate-agents.py` -> `agents checked: 3   findings: 0`. Os três com
      `model: inherit`; `tools` declarado: `grounding-researcher` [Read, Grep, Glob, Bash, WebSearch,
      WebFetch], `bug-hunter-analyst` e `skill-auditor` [Read, Grep, Glob, Bash] — nenhum com Write
      ou Edit (D5).

- [x] 2.5 A razão de admissão de cada um, escrita contra os três testes de `agent-delegation`

      As três razões, escritas contra os três testes, ficam na tabela da seção *What is an agent?*
      do `README.md`, e não no corpo do agente: o corpo vira system prompt e a razão de admissão é
      meta-conteúdo que o agente não usa em execução.

## 3. Geração

- [x] 3.1 `generate.sh` — mapa `AGENT_GROUP` e guard pré-escrita, no mesmo lugar e com a mesma
      garantia do guard de `GROUP_THEME`
      Provado quebrando de propósito: um `agents/unmapped-agent.md` sem entrada no mapa ->
      `❌ generate.sh: no AGENT_GROUP for agent 'unmapped-agent' … Nothing was written.` O md5 de
      `git status --porcelain --untracked-files=all` antes e depois da falha é **idêntico**: a árvore
      ficou intacta, incluindo `plugins/`, que o script apaga logo adiante.

- [x] 3.2 `generate.sh` — cópia de cada agente para `plugins/<group>/agents/`
      `ls plugins/*/agents/` -> `plugins/testing/agents/bug-hunter-analyst.md`,
      `plugins/tooling/agents/skill-auditor.md`, `plugins/workflow/agents/grounding-researcher.md`.

- [x] 3.3 `generate.sh` — `group_description()` acrescenta `(M agents: …)` em parêntese **separado**
      (D4), e o bloco Python das descrições publica o mesmo texto
      `ai-skills-testing` publica `… (3 skills: api-resilience-testing, bug-hunter, tdd) (1 agent:
      bug-hunter-analyst)` — dois parênteses, e o `MEMBERSHIP_CLAIM` do H3 continua casando só com o
      primeiro. Mesmo texto no `plugin.json` do grupo e na entrada do `marketplace.json`.

- [x] 3.4 Nenhum wrapper de agente em `claude/`, `codex/`, `cursor/` ou `copilot/`

      `ls claude/ codex/ cursor/ copilot/` não tem nenhum diretório nem arquivo de agente; o único
      destino de cópia é `plugins/<group>/agents/`.

## 4. Gate

- [x] 4.1 `scripts/validate-agents.py` — frontmatter, limites, seção *When to invoke*, `tools`
      declarado, e a lei de órfão
      `python3 scripts/validate-agents.py` -> `agents checked: 3   findings: 0`. O validador achou um
      defeito real durante a escrita: a `description` do `skill-auditor` tinha dois-pontos sem aspas e
      não parseava como YAML (`A1`); as três foram convertidas para folded scalar.

- [x] 4.2 `scripts/selftest-validate-agents.py` — cada regra reprova violando e aprova cumprindo
      `python3 scripts/selftest-validate-agents.py` -> `22/22 cases passed`, cobrindo as 20 classes de
      defeito mais o caso limpo e o caso da cópia gerada COM fonte, que não é órfã. Um defeito pego
      pelo check errado também reprova.

- [x] 4.3 `scripts/validate-repo-hygiene.py` — check irmão do H3 para a lista de agentes, e
      `UNSCOPED_COUNT_CLAIM` passa a recusar `(N agents)` sem lista
      H4 provado nas duas formas: lista adulterada ->
      `names 2 agent(s) but plugins/testing/agents/ has 1 — in excess: ['ghost']`; lista removida ->
      `ships 1 agent(s) and publishes no (N agents: <names>) list`. Regenerado ->
      `repo hygiene: 0 findings`.

- [x] 4.4 `.github/workflows/ci.yml` — dois steps novos, ao lado dos de skill

      `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/ci.yml'))"` sem erro; os dois
      steps novos ficam ao lado dos de skill (`validate-agents.py` e seu selftest).

## 5. README

- [x] 5.1 Seção *What is an agent?* com a fronteira, linkando `agent-delegation`
- [x] 5.2 Linha `agents/` na árvore de estrutura e na tabela de pastas
- [x] 5.3 A tabela multi-ferramenta declara que agente é Claude-Code-only
- [x] 5.4 Os três agentes listados, com o que cada um faz

      A tabela nomeia os três com o que fazem e a razão de admissão contra os três testes.

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      O caminho real de um agente é ser descoberto por uma sessão e despachado por ela. Medido em
      sessões headless novas, rodando de um diretório que **não** é este repositório
      (`/tmp/.../plugintest`, um git init vazio), para que a descoberta viesse do plugin e não do cwd.

      **Descoberta, bundle FULL (`source: "./"`, a raiz do repositório como plugin):**

      `claude -p "…list your subagent types…" --plugin-dir /home/diegops/ai-skills` ->

          ai-skills:bug-hunter-analyst
          ai-skills:grounding-researcher
          ai-skills:skill-auditor

      **Descoberta, plugin por domínio:**

      `--plugin-dir …/plugins/testing --plugin-dir …/plugins/tooling` ->

          ai-skills-testing:bug-hunter-analyst
          ai-skills-tooling:skill-auditor

      **Despacho real, com o contrato de saída conferido:** `ai-skills:grounding-researcher`
      despachado contra uma pergunta verificável ("`scripts/validate-agents.py` define um check A7?"),
      saída observada, íntegra:

          CLAIM: `scripts/validate-agents.py` defines a check labelled A7 (rule ID "A7", enforcing
                 that the canonical directory is flat with no orphan agents).
          VERDICT: verified
          RUNG: 1 (repository's own code)
          EVIDENCE: line 12 `A7 no orphan agent in a generated tree, and the canonical directory is
                    flat`; line 134; line 141 `add(sub.name, "A7 layout",`; line 149
          UNREACHED: none
          NOTES: The rule ID is used as `"A7 layout"` in the emitted labels (lines 141, 149), not
                 bare `"A7"` — relevant if the caller is grepping for an exact string.

      Os seis campos do contrato saíram na ordem, a evidência é citável e confere com o arquivo
      (`grep -n "A7 layout"` -> 141 e 149), e o NOTES é um caveat real que o chamador usaria.

      **Controle:** o mesmo mecanismo com um agente built-in (`Explore`) devolveu
      `/home/diegops/ai-skills/scripts/validate-agents.py` em segundos, o que separa "o despacho
      aninhado funciona headless" de qualquer lentidão de tarefa (ver S.3).

- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      **Descoberta:** caminhos de instalação que tinham de expor os agentes e expuseram: **2/2**
      (bundle FULL e plugin por domínio). Agentes resolvidos por nome: **3/3** no bundle FULL,
      **2/2** nos dois plugins por domínio carregados.

      **Despacho:** agentes despachados e que devolveram o contrato: **1/1** medido
      (`grounding-researcher`), mais **1/1** de controle com agente built-in.

      **Gate `validate-agents.py`:** classes de defeito que tinham de reprovar e reprovaram
      **20/20**; casos que tinham de passar e passaram **2/2** (o agente conforme, e a cópia gerada
      COM fonte, que não é órfã). Total **22/22**, e um defeito pego pelo check **errado** também
      contaria como falha.

      **Gate H4:** formas que tinham de reprovar e reprovaram **2/2** (lista adulterada, lista
      ausente com agentes na árvore); estado correto que tinha de ficar em silêncio e ficou **1/1**.

      **Guard do `generate.sh`:** falhas que tinham de acontecer **1/1**, e a árvore que tinha de
      ficar intacta ficou (md5 de `git status --porcelain --untracked-files=all` idêntico antes e
      depois).

      **Escapes conhecidos que continuaram em silêncio, de propósito:** o contrato de saída é
      julgamento e não é medido pelo gate; que `tools` seja o mínimo possível é revisão humana; a
      razão de admissão dos três é prosa no README e não é conferida por script. Os três estão
      escritos como limite no cabeçalho de `scripts/validate-agents.py`.

- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      Três coisas, nenhuma silenciada:

      (a) **Esta sessão não enxergou os agentes novos.** Os tipos de subagente são resolvidos no
      início da sessão: despachar `skill-auditor` daqui devolveu
      `Agent type 'skill-auditor' not found`, mesmo com os arquivos no lugar e o validador verde. Não
      é defeito do artefato — é o motivo de a prova de campo ter sido feita em sessões novas, e vale
      registrar porque quem editar um agente e tentar usá-lo no mesmo turno vai bater nisso.

      (b) **Um despacho de `skill-auditor` não voltou dentro do orçamento.** Auditar
      `skills/lean-code/` (236 linhas mais references) contra `skills-authoring/spec.md` (47 KB) num
      modelo `sonnet` passou de 420 s sem produzir saída. O controle com agente built-in voltou em
      segundos no mesmo mecanismo, então o que isso mede é o tamanho da tarefa, não a fiação. Fica
      registrado como observação de custo do `skill-auditor`, e não convertido em "tudo verde".

      (c) **O `color` é exigido pelo validador porque o documento do harness o chama de
      obrigatório**, não porque um agente sem ele tenha sido observado falhando no runtime. Está em
      E.3(c) e continua aberto.

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
      Nenhuma `SKILL.md` foi tocada por esta change: ela acrescenta uma classe de artefato, não
      edita skill. `python3 scripts/validate-skills.py` -> `skills checked: 38   findings: 0`.
      O gate irmão para a classe nova é `validate-agents.py` -> `agents checked: 3   findings: 0`.

- [x] Q.2 All touched skill content in English (catalog locale)
      Os três agentes e os dois scripts em inglês (locale do catálogo); a prosa desta change e do
      PR em português, como o repositório (`code-locale`).

- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
      Gatilhos de agente são `description`, lidas pelo harness ao rotear. Nenhuma colide: o
      `bug-hunter-analyst` diz explicitamente que não é para desenhar suíte de API do zero nem para
      decidir se o teste vem antes do código; o `skill-auditor` diz que reporta e nunca é gate; o
      `grounding-researcher` diz que não revisa nem corrige código.

- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
      Nada restatado: o contrato do `grounding-researcher` aponta para `verify-before-claiming` em
      vez de reproduzir a escada; o `bug-hunter-analyst` manda ler o track de `bug-hunter` em vez de
      copiar o método; o `skill-auditor` audita contra `skills-authoring` e proíbe explicitamente
      reportar o que os C1–C13 já cobrem.

- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

      Os blocos de código dos agentes são contratos de saída, não código executável, e estão em
      inglês. Os dois scripts novos usam identificadores em inglês (`code-locale`).

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-agents-layer --strict` green
      `openspec validate add-agents-layer --strict` -> `Change 'add-agents-layer' is valid`;
      `bash scripts/validate-rite.sh` -> `rite gate OK` (`Totals: 3 passed, 0 failed`).

- [x] V.2 Catalog discovery intact: 38 skills, nenhum agente contado como skill, sem órfão
      `ls -1 skills/ | wc -l` -> `38`, inalterado. `python3 scripts/validate-agents.py` ->
      `agents checked: 3   findings: 0`, incluindo a lei de órfão (A7).
      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`, com o H4 novo ativo.
      Duas execuções seguidas de `./generate.sh` deixam a árvore idêntica.

- [x] V.3 README atualizado nas quatro frentes do grupo 5
      `README.md`: seção *What is an agent?* com os três testes e a tabela de admissão dos três
      agentes, `agents/` na árvore de estrutura e na tabela de pastas, e o parágrafo que declara
      agente como Claude-Code-only logo abaixo da tabela multi-ferramenta.

- [ ] V.4 `openspec archive add-agents-layer --yes` after all groups above are `[x]`
