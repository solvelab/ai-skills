# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `55d8a48` (master, base de `backlog/197-agent-delegation-skill`) em 2026-09-07:

      - `openspec/specs/skills-authoring/spec.md:1-120` — o mapa canônico inteiro (`:11-23`),
        copiado por completo no delta antes de ganhar a entrada `agent-delegation`, e o requisito
        de frontmatter uniforme (`:66-90`) com os limites parseados de 1024/500.
      - `openspec/specs/skills-catalog/spec.md:1-60` e a lista completa de `### Requirement:` —
        o padrão de nome *X has a canonical home* já usado por `Observability`, `Claim verification`
        e `Code locale`; `:309-351` lido inteiro como molde de forma.
      - `claude/global/personal-rules.md:76-90` — a seção *Model & Effort Tiering* na íntegra, e o
        cabeçalho `:3` que declara o arquivo como config pessoal do mantenedor.
      - `skills/backlog/SKILL.md:78-95` e `skills/execute-backlog/SKILL.md:90-120` — os dois únicos
        pontos do catálogo que despacham subagente.
      - `scripts/validate-skills.py` — docstring com C1–C13, e `:485-555` (a implementação de C12,
        incluindo `CATALOG_ONLY_ROOTS` e `REPO_URL_PREFIX`).
      - `generate.sh:1-130` (guards de VERSION e GROUP_THEME, `group_of`, `category_of`) e
        `:236-300` (`group_description`, loop de plugins, bloco Python das descrições).
      - `.github/workflows/ci.yml:120-178` — os steps de validação e os selftests.
      - `README.md:439-552` (estrutura do repositório, arquitetura multi-ferramenta e a definição
        "What is a skill?"), `:55-72` (tabela de plugins), `:642-655` (tabela de skills de processo).
      - `skills/lean-code/SKILL.md:1-30` — frontmatter como molde e o bloco de não-preso-a-versão.
      - `openspec/changes/archive/2026-09-07-add-tdd-skill/` — proposal, design, tasks e os dois
        deltas, como molde de change de skill de doutrina com casa canônica.
      - `openspec/changes/archive/2026-07-18-add-backlog-skill/design.md:20` — a frase que limita o
        subagente à coleta de contexto.
      - `openspec/schemas/skills-rite/schema.yaml` e os quatro templates.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      `openspec new change add-agent-delegation-skill --schema skills-rite` ->
      `Created change 'add-agent-delegation-skill' at openspec/changes/add-agent-delegation-skill/`

      `openspec validate add-agent-delegation-skill --strict` ->
      `Change 'add-agent-delegation-skill' is valid`

      `openspec list` -> `No active changes found.` antes desta change.

      `ls -1 skills/ | wc -l` -> `37`; `ls -1 plugins/workflow/skills/ | wc -l` -> `8`.

      `grep -m1 'version:' skills/verify-before-claiming/SKILL.md` -> `  version: 1.1.1`;
      `skills/bug-hunter/SKILL.md` -> `  version: 2.3.0`; `skills/lean-code/SKILL.md` -> `  version: 1.1.0`.

      `find . -type d -name agents` (fora de `.git/`) -> vazio;
      `git log --all --name-only --pretty=format: | grep -E '(^|/)agents/'` -> vazio.

      `gh auth status` -> `Token scopes: 'admin:org', …, 'project', 'repo', 'workflow', …`.

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Duas lacunas, nenhuma preenchida com substituto plausível:

      (a) **Se os gatilhos da `description` de `agent-delegation` colidem na prática com os de
      `lean-code`.** Não há detector de colisão de trigger no repositório —
      `scripts/validate-skills.py` (C13) checa a presença da cláusula `Do NOT use for`, não a
      colisão. O que se prova é a presença da fronteira nas duas descriptions; que ela resolva o
      roteamento em uso é observação de campo e fica aberta.

      (b) **Se a doutrina publicada muda o comportamento de escolha de artefato.** Não houve
      medição: `research/` não tem harness para essa pergunta e esta change não faz alegação de
      ganho. Fica aberta e nomeada como follow-up em E.4.

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Follow-ups anotados e **não** feitos:

      - Criar o diretório `agents/`, os três agentes, o mapa de grupo em `generate.sh`,
        `scripts/validate-agents.py` e seu selftest: é a issue #198, que depende desta.
      - Medir se a doutrina muda a escolha de artefato (lacuna (b) de E.3).
      - As 10 skills `r3f-*` não citam nenhuma das skills de processo — ilha desconectada do grafo
        de cross-links, achada ao mapear o catálogo. Não é escopo desta change.
      - Converter as duas chamadas de `Explore` em `backlog`/`execute-backlog` para agentes
        próprios: fora de escopo aqui e explicitamente fora de escopo em #198.

      Nada em `research/`, `generate.sh`, `scripts/` ou `.github/workflows/` foi alterado por esta
      change.

## 2. A skill

- [x] 2.1 `skills/agent-delegation/SKILL.md` com frontmatter uniforme (name == diretório,
      `description` folded com valor parseado ≤1024, `metadata.author: solvelab`,
      `metadata.version` semver, `metadata.category: process`, `license: MIT`, `compatibility` ≤500)
      `agentskills validate skills/agent-delegation/` -> `Valid skill: …/skills/agent-delegation`;
      `description` parseada = 1010 chars, `compatibility` = 278.

- [x] 2.2 Seção *artifact boundary*: escolha ordenada entre skill, hook, script de CI e agente, cada
      linha ancorada num artefato real deste repositório (D2 — hooks pela URL do repositório, para
      não violar C12)
      Três linhas (script / hook / skill), ancoradas em `scripts/validate-skills.py`, no write-gate
      de locale citado pela URL do repositório (D2) e na própria `SKILL.md`. `validate-skills.py` ->
      `skills checked: 38   findings: 0`, logo C12 e C1 verdes.

- [x] 2.3 Seção *when delegation pays*: os três testes (peso de leitura, contexto separável,
      contrato de saída estreito) e os três anti-padrões nomeados com a razão
- [x] 2.4 Seção *model and effort tiering* escrita como critério, não como lista de modelos (D3),
      preservando a razão do cache de prompt do loop principal
- [x] 2.5 Seção *least privilege and the output contract*: `tools` no mínimo necessário e contrato
      de saída escrito para todo agente definido
- [x] 2.6 `Do NOT use for` na description, com a fronteira contra `lean-code`, `bug-hunter` e
      `verify-before-claiming` (D6)
      Colisão de gatilhos medida: nenhuma frase entre aspas da `description` desta skill aparece na
      de `lean-code` (12), `bug-hunter`, `verify-before-claiming` ou `documentation` — interseção vazia
      nos quatro casos.

- [x] 2.7 Declaração de não-preso-a-versão no lugar do bloco `Verified against` (D5, C5)

## 3. Casa canônica e cross-links

- [x] 3.1 `openspec/specs/skills-authoring/spec.md` — mapa canônico ganha
      `agent-delegation` (pelo delta desta change)
- [x] 3.2 `claude/global/personal-rules.md` — a seção *Model & Effort Tiering* reduzida a link mais
      no máximo uma linha de resumo (D4)
- [x] 3.3 `skills/lean-code/SKILL.md` — cross-link e fronteira "quanto código × qual artefato"
- [x] 3.4 `skills/verify-before-claiming/SKILL.md` — cross-link do contrato de saída de pesquisa
- [x] 3.5 `skills/bug-hunter/SKILL.md` — cross-link e a fronteira "delegar a análise não é fazer a análise"
- [x] 3.6 `metadata.version` sobe nas três skills editadas

      `lean-code` 1.1.0 -> 1.2.0, `verify-before-claiming` 1.1.1 -> 1.2.0, `bug-hunter` 2.3.0 -> 2.4.0.

## 4. Catálogo

- [x] 4.1 `./generate.sh` rodado e wrappers commitados junto; segunda execução sem diff
      `./generate.sh` -> `Generated wrappers for 38 skills` e `Generated 10 category plugins`.
      Duas execuções seguidas deixam o mesmo conjunto de 26 caminhos modificados/novos: sem diff extra.

- [x] 4.2 `README.md` — linha na tabela de plugins (`:59`) e na tabela de skills de processo (`:642-655`)
- [x] 4.3 Contagem publicada de 37 para 38 conferida por `scripts/validate-repo-hygiene.py` (H3)

      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`; a descrição gerada de
      `ai-skills-workflow` passa a dizer `(9 skills: agent-delegation, …)`.

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      O caminho real de uma skill é ser instalada e carregada por uma sessão. Instalada pela mesma
      linha que `install.sh:64` usa:
      `ln -sfn /home/diegops/ai-skills/skills/agent-delegation /home/diegops/.claude/skills/agent-delegation`.
      Depois disso a skill passou a aparecer no catálogo de skills da sessão, e três sessões
      separadas a carregaram pelo Skill tool e a aplicaram a decisões reais deste repositório.

      **Run 1, primeiro rascunho (tabela única de 4 linhas).** Descoberta OK. A=script, C=hook,
      D=recusado pelo anti-padrão, E=deixado em aberto com a frase certa. **B roteou para `skill`
      quando devia rotear para subagente.** Saída observada:

      > "Nothing in the table distinguishes 'the doctrine that governs a judgement' (Skill) from
      > 'a heavy, separable, one-shot application of that judgement across 38 files' (Agent-shaped
      > work) when both conditions can be simultaneously true of the same sentence."

      Consequência medida, não hipotética: a skill como escrita teria **recusado** o `skill-auditor`
      da issue #198, que é exatamente o caso B. O defeito foi corrigido separando o corpo em duas
      perguntas — onde a regra mora (script/hook/skill) e onde o trabalho roda (loop ou subagente) —
      e declarando que um agente nunca é resposta da primeira.

      **Run 2, após a correção.** B passou a rotear para subagente. Evidência **descartada** como
      prova: o próprio executor observou que o caso B aparecia quase literalmente como exemplo
      trabalhado no corpo — "close to verbatim the skill's own illustrative example". O exemplo foi
      então trocado pela dupla regra/tarefa do `code-locale`, para que a medição seguinte medisse
      roteamento e não reconhecimento de exemplo.

      **Run 3, texto entregue, seis casos.** Todos os seis roteados como a doutrina manda; ver S.2.
      As oito frases que o executor citou como decisórias foram conferidas uma a uma contra
      `skills/agent-delegation/SKILL.md`: as oito existem verbatim. E ele afirmou, corretamente, que
      não existe no corpo nenhum exemplo trabalhado sobre `gh` nem sobre "doctrine restated inline" —
      o que prova que leu o texto atual, e não o do run 2.

- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      Run 3, sobre o texto entregue:

      - Casos que tinham de rotear e rotearam: **4/4** — A -> script determinístico,
        B -> subagente, C -> hook, F -> subagente com modelo barato e effort baixo.
      - Caso que tinha de ser recusado e foi: **1/1** — D, pelo anti-padrão "one agent per skill".
      - Caso que tinha de ficar em silêncio e ficou: **1/1** — E (onde mora o mapa agente->grupo);
        a skill declara o formato do arquivo de agente fora de escopo e o executor não inventou
        resposta.

      Run 1, sobre o primeiro rascunho, para comparação: **4/5** corretos e **1/5** errado (B).

      Colisão de gatilhos, medida fora das sessões: nenhuma das 9 frases entre aspas da `description`
      aparece na de `lean-code` (12 frases), `bug-hunter`, `verify-before-claiming` ou
      `documentation` — interseção vazia nos quatro casos.

      Escape conhecido que continuou em silêncio: não há detector automático de colisão de gatilho no
      repositório, então a medição acima é de sobreposição literal de frases, não de roteamento em
      uso. Está declarado como lacuna aberta em E.3(a).

- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      Duas coisas, nenhuma silenciada:

      (a) **O run 3 reportou um H1 que não existe.** Ele declarou ter observado
      `# Agent delegation — which artifact a rule becomes, and when to dispatch one` — o título do
      rascunho anterior. `grep -rln "which artifact a rule becomes, and when to dispatch one"` sobre
      todo o repositório (fora de `.git/`) não devolve **nada**, e o arquivo em disco, direto e pelo
      symlink de instalação, carrega
      `# Agent delegation — where a rule lives, and where the work runs`. As oito citações decisórias
      e a negativa correta sobre os exemplos provam que o corpo lido foi o atual, logo o erro está na
      linha de observação do relatório, não no roteamento. Fica registrado como o que é: uma
      observação relatada que não bate com o disco, num run cujo resto confere.

      (b) **Os casos B e F parafraseiam de perto as ilustrações da própria skill** — "reads every
      SKILL.md ... returns a defect table" contra "a sweep over forty files that ends in a twenty-line
      table"; "twenty file reads; the answer is one line" contra a mesma frase. O executor levantou
      isso sozinho e verificou que nenhum dos dois é exemplo nomeado. A semelhança não foi removida:
      tirar as ilustrações para deixar o teste mais limpo tornaria a skill pior, e o custo — que um
      run futuro possa confundir reconhecimento com roteamento — fica anotado aqui em vez de
      escondido.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
      `python3 scripts/validate-skills.py` -> `skills checked: 38   findings: 0` (C10 mede os limites
      parseados) e `agentskills validate skills/agent-delegation/` -> `Valid skill: …`. As quatro
      `SKILL.md` tocadas: `agent-delegation` 1.1.0 (nova), `lean-code` 1.2.0,
      `verify-before-claiming` 1.2.0, `bug-hunter` 2.4.0.

- [x] Q.2 All touched skill content in English (catalog locale)
      Todo o corpo da skill nova e as três linhas de cross-link estão em inglês; a prosa desta change
      e do PR segue o português do repositório (`code-locale`).

- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
      Interseção de frases entre aspas da `description`: `lean-code` vazia, `bug-hunter` vazia,
      `verify-before-claiming` vazia, `documentation` vazia. `Do NOT use for` presente nomeando as
      quatro. Roteamento medido em sessão real: 6/6 em S.2.

- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
      Nada restatado: a escada de reúso fica em `lean-code`, a escada de pesquisa e o relatório de
      não-encontrado ficam em `verify-before-claiming`, a metodologia adversarial fica em
      `bug-hunter`. As três são linkadas com uma linha cada, nos dois sentidos. C2 verde em
      `validate-skills.py`.

- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

      A skill não carrega bloco de código: é doutrina em prosa. C9 rodou sobre as 38 skills e não
      achou nada. Nenhum identificador novo nasce fora do nome do diretório da skill.

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-agent-delegation-skill --strict` green
      `openspec validate add-agent-delegation-skill --strict` ->
      `Change 'add-agent-delegation-skill' is valid`; `bash scripts/validate-rite.sh` -> `rite gate OK`
      (`Totals: 3 passed, 0 failed`).

- [x] V.2 Catalog discovery intact: 38 skills, `ai-skills-workflow` com 9, sem órfão
      `./generate.sh` -> `Generated wrappers for 38 skills` / `Generated 10 category plugins`.
      `plugins/workflow/.claude-plugin/plugin.json` passa a publicar `(9 skills: agent-delegation, …)`.
      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`, que cobre órfãos e a
      contagem publicada. Duas execuções seguidas de `generate.sh` deixam a árvore idêntica
      (md5 do `git status --porcelain` igual nas duas).

- [x] V.3 README atualizado nas duas tabelas
      `README.md`: tabela de plugins (`ai-skills-workflow` ganha `agent-delegation`), tabela de skills
      de processo (linha nova) e as contagens `all 37` -> `all 38`.

- [x] V.4 `openspec archive add-agent-delegation-skill --yes` after all groups above are `[x]`
