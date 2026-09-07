# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `41fe221` (master, base de `backlog/206-regroup-plugins-by-domain`) em 2026-09-07:

      - `generate.sh:44-62` — `GROUP_THEME` inteiro, `group_of()` e `category_of()`; `:69-82` o guard
        pré-escrita; `:224-234` a cópia das skills; `:241-268` `group_description()`; `:300-380` o
        laço de plugins e o bloco Python que reescreve `marketplace.json` e o manifesto raiz,
        incluindo as duas saídas por `sys.exit` quando grupo e entrada não casam.
      - `.github/workflows/ci.yml:96-125` — o step de frontmatter, com `CATEGORIES` na linha 98.
      - `openspec/specs/skills-authoring/spec.md` — *Uniform frontmatter metadata* inteiro, incluindo
        o cenário *The documented set matches the enforced set*, copiado por completo no delta.
      - `openspec/specs/skills-catalog/spec.md` — a lista de requisitos e *Catalog composition after
        the quality review*, para não colidir com o requisito novo.
      - `scripts/validate-repo-hygiene.py:33-49` (`COUNT_FILES`, `MEMBERSHIP_CLAIM`,
        `AGENT_MEMBERSHIP_CLAIM`) e `:151-200` (H3/H4 e a exigência de entrada por grupo).
      - `.claude-plugin/marketplace.json:43-44` — a entrada `ai-skills-game`.
      - `README.md:59-70` (tabela de plugins), `:74`, `:95` e `:714` — as três menções a
        `ai-skills-game` fora da tabela.
      - `skills/assettoserver-ops/SKILL.md`, `skills/assettoserver-plugin/SKILL.md`,
        `skills/assettoserver-csp-lua/SKILL.md` — frontmatter das três que mudam de categoria.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      A restrição que motiva a change, na documentação do Claude Code
      (code.claude.com/docs/en/skills.md): *"Plugin skills are not affected by `skillOverrides` —
      manage those through `/plugin` instead"*. `claude plugin disable --help` não tem flag por skill.

      Custo medido com o catálogo instalado, `claude plugin details`:
      `ai-skills-devops` -> `assettoserver-ops ~260`, `helm-migration ~270`, `k8s-tune-resources ~240`;
      `ai-skills-game` -> `assettoserver-csp-lua ~370`, `assettoserver-plugin ~300`, dez `r3f-*` somando ~1.440.

      Escala medida num workspace real de 31 repositórios configurados em 2026-09-07:
      `ai-skills-devops` habilitado em **30**, `ai-skills-backend` em 17, `ai-skills-frontend` em 8,
      `ai-skills-game` em 2. Nenhum dos 30 tem qualquer coisa de Assetto Corsa.

      `openspec new change regroup-plugins-by-project-domain --schema skills-rite` ->
      `Schema: skills-rite`; `openspec validate regroup-plugins-by-project-domain --strict` ->
      `Change 'regroup-plugins-by-project-domain' is valid`.

      `grep -n "CATEGORIES=" .github/workflows/ci.yml` ->
      `98:          CATEGORIES="backend testing fivem game devops docs git process nui frontend tooling"`.

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Duas lacunas, nenhuma preenchida com substituto plausível:

      (a) **Quantos consumidores fora deste workspace instalam `ai-skills-game` ou
      `ai-skills-devops`, e por qual skill.** O repositório é público e não há telemetria; não dá para
      saber quem perde `assettoserver-*` nesta mudança. É exatamente por isso que D3 recusou o rename
      e D4 exige o rodapé `BREAKING CHANGE` — a decisão foi tomada assumindo consumidor desconhecido,
      não assumindo que não existe.

      (b) **Se `metadata.category` novo é aceito pelo validador de referência do padrão aberto**
      (`skills-ref`, pinado em 0.1.1 no CI). Ele valida a whitelist de **campos**, não o valor de
      `metadata.category`; a categoria é regra deste catálogo. Medido no grupo Simulation rodando o
      validador contra as três skills tocadas, não assumido aqui.

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Follow-ups anotados e **não** feitos:

      - Renomear `game` para `r3f`. Recusado nesta change por D3, com a razão escrita; se algum dia o
        catálogo aceitar uma janela de quebra de nome, é aí que entra.
      - As 10 skills `r3f-*` não citam nenhuma skill de processo — ilha desconectada do grafo de
        cross-links, já anotada em changes anteriores.
      - Endurecer o validador de agentes (#205).
      - Nenhuma skill teve conteúdo alterado: as três tocadas mudam `metadata.category` e
        `metadata.version`, e nada abaixo do frontmatter.

## 2. As três categorias

- [x] 2.1 `skills/assettoserver-ops/SKILL.md` — `category: devops` -> `assettoserver`, `metadata.version` sobe
      `category: devops` -> `assettoserver`; `metadata.version` 1.3.2 -> 1.4.0.

- [x] 2.2 `skills/assettoserver-plugin/SKILL.md` — `category: game` -> `assettoserver`, `metadata.version` sobe
      `category: game` -> `assettoserver`; `metadata.version` 1.4.1 -> 1.5.0.

- [x] 2.3 `skills/assettoserver-csp-lua/SKILL.md` — `category: game` -> `assettoserver`, `metadata.version` sobe
      `category: game` -> `assettoserver`; `metadata.version` 1.1.3 -> 1.2.0.

- [x] 2.4 Nenhuma linha abaixo do frontmatter das três foi tocada

      O diff das três é só `category` e `version`: nenhuma linha abaixo do frontmatter foi tocada.

## 3. Conjunto controlado e gerador

- [x] 3.1 `.github/workflows/ci.yml:98` — `CATEGORIES` ganha `assettoserver`
      `CATEGORIES` passa a conter `assettoserver`. O step do CI rodado localmente sobre as 38
      skills: **38/38 aprovadas** com o conjunto novo.

- [x] 3.2 `openspec/specs/skills-authoring` — o conjunto documentado ganha `assettoserver` (pelo delta)
      Pelo delta desta change, no mesmo commit — o cenário *The documented set matches the
      enforced set* exige que o documento e o gate mudem juntos.

- [x] 3.3 `generate.sh` — `GROUP_THEME[assettoserver]` novo; temas de `game` e `devops` perdem o domínio que saiu
      `[assettoserver]` novo; `[game]` passa a "React Three Fiber conventions for 3D on the web";
      `[devops]` passa a "Kubernetes/Helm migration and cluster resource tuning".

- [x] 3.4 `.claude-plugin/marketplace.json` — entrada `ai-skills-assettoserver` (o gerador falha se grupo e entrada não casarem, nos dois sentidos)

      Provado quebrando de propósito: removida a entrada, `./generate.sh` ->
      `❌ generate.sh: plugin group(s) with no marketplace entry: assettoserver — add the entry to
      .claude-plugin/marketplace.json.` Restaurada, o gerador volta a passar.

## 4. Publicação

- [x] 4.1 `./generate.sh` roda e produz `plugins/assettoserver/skills/` com as três
      `ls plugins/assettoserver/skills/` -> `assettoserver-csp-lua`, `assettoserver-ops`,
      `assettoserver-plugin`.

- [x] 4.2 `plugins/game/skills/` fica só com as 10 `r3f-*`; `plugins/devops/skills/` só com `helm-migration` e `k8s-tune-resources`
      `plugins/game/skills/` -> as 10 `r3f-*`, e nada mais. `plugins/devops/skills/` ->
      `helm-migration`, `k8s-tune-resources`.

- [x] 4.3 `README.md` — tabela de plugins, e a nota do bloco r3f que hoje diz que `ai-skills-game` também traz AssettoServer
      Tabela de plugins com a linha nova e as duas encolhidas; a nota do bloco r3f deixa de dizer
      que `ai-skills-game` também traz AssettoServer e passa a dizer por que não traz mais.

- [x] 4.4 Tabela de migração no `README.md`; a nota do `CHANGELOG.md` vem do rodapé
      `BREAKING CHANGE` do commit, porque `@semantic-release/changelog` gera aquele arquivo e
      editá-lo à mão seria sobrescrito no próximo release
      Tabela de migração no `README.md`, logo antes do bloco de instalação manual, com as quatro
      situações e a razão de cada uma. A nota do changelog sai do rodapé `BREAKING CHANGE` do commit.

- [x] 4.5 Segunda execução de `./generate.sh` não produz diff

      Duas execuções seguidas de `./generate.sh` deixam a árvore idêntica (md5 do
      `git status --porcelain --untracked-files=all` igual nas duas).

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      O caminho real de um grupo de plugin é ser carregado por uma sessão. Medido de um diretório que
      **não** é este repositório, com os três grupos tocados apontados direto da árvore gerada:

      `claude -p "…" --plugin-dir plugins/assettoserver --plugin-dir plugins/devops` ->

          ai-skills-assettoserver:assettoserver-csp-lua
          ai-skills-assettoserver:assettoserver-ops
          ai-skills-assettoserver:assettoserver-plugin
          ai-skills-devops:helm-migration
          ai-skills-devops:k8s-tune-resources
          assettoserver-ops present in devops group: no

      Com `--plugin-dir plugins/game` junto, o total sobe para 28 = 13 do escopo user + 15 dos três
      grupos (3 + 2 + 10), e as dez de `game` são todas `r3f-*`.

      Descrições publicadas, derivadas da árvore pelo gerador:

          assettoserver: … (3 skills: assettoserver-csp-lua, assettoserver-ops, assettoserver-plugin)
          game:          … (10 skills: r3f-animation, …, r3f-shaders)
          devops:        … (2 skills: helm-migration, k8s-tune-resources)

- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      - Grupos que tinham de publicar exatamente o seu domínio e publicaram: **3/3**
        (`assettoserver` 3 skills, `game` 10, `devops` 2).
      - Skills que tinham de sair de um grupo e saíram: **3/3** — `assettoserver-ops` de `devops`,
        `assettoserver-plugin` e `assettoserver-csp-lua` de `game`.
      - Skills que tinham de **não** se mover e não se moveram: **35/35** (as 10 `r3f-*` incluídas).
      - Guard que tinha de falhar e falhou: **1/1** — grupo sem entrada no marketplace derruba o
        gerador nomeando o grupo.
      - Gates que tinham de ficar verdes e ficaram: **5/5** — `validate-skills.py` 38/0,
        `validate-agents.py` 3/0, `validate-repo-hygiene.py` 0 (H3 e H4), o step de categoria do CI
        38/38, `agentskills validate` nas três tocadas.
      - Geração determinística: **2/2** execuções com árvore idêntica.

      Escape conhecido que continuou em silêncio, de propósito: não há detector que meça se um grupo
      mistura domínios — a regra nova de `skills-catalog` é julgamento humano contra a árvore, e o
      requisito diz isso ao exigir que a evidência seja a lista de skills, não uma afirmação.

- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      Três coisas, nenhuma silenciada:

      (a) **Eu escrevi "12 skills `r3f-*`" em proposal, design e tasks. São 10.** O número veio da
      linha do README que contava o grupo `ai-skills-game` inteiro, incluindo as duas de AssettoServer.
      Corrigido nos três arquivos antes do commit, e registrado aqui em vez de apagado: um número
      copiado de uma linha que contava outra coisa é exatamente a classe de erro que o rito existe
      para pegar.

      (b) **O `CHANGELOG.md` não recebe a tabela de migração por edição.**
      `@semantic-release/changelog` gera aquele arquivo; escrever nele à mão seria sobrescrito no
      próximo release. A tarefa 4.4 foi reescrita antes de ser ticada, e a nota sai do rodapé
      `BREAKING CHANGE` do commit.

      (c) **A instalação local desta máquina continua na 2.35.0 e não vê o reagrupamento.** O cache de
      plugin é pinado por versão, e `claude plugin update` responde `already at the latest version`
      enquanto o VERSION não subir. Por isso a prova de campo usou `--plugin-dir` contra a árvore, e
      por isso os repositórios do workspace só passam a ver os grupos novos depois do release.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
      `python3 scripts/validate-skills.py` -> `skills checked: 38   findings: 0`; o step de
      frontmatter do CI rodado localmente aprova 38/38 com o conjunto controlado novo.

- [x] Q.2 All touched skill content in English (catalog locale)
      As três skills tocadas continuam em inglês; nada abaixo do frontmatter mudou. A prosa desta
      change e do PR segue o português do repositório (`code-locale`).

- [x] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
      Nenhuma `description` foi tocada, logo nenhum gatilho mudou e não há colisão nova a medir.

- [x] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
      Nenhuma doutrina foi restatada: esta change não escreve doutrina, move três skills de grupo.
      O requisito novo de `skills-catalog` linka a restrição do harness em vez de reproduzi-la.

- [x] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

      Nenhum exemplo de código foi tocado. C9 rodou sobre as 38 skills sem achados.

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate regroup-plugins-by-project-domain --strict` green
      `openspec validate regroup-plugins-by-project-domain --strict` ->
      `Change 'regroup-plugins-by-project-domain' is valid`; `bash scripts/validate-rite.sh` ->
      `rite gate OK`.

- [x] V.2 Catalog discovery intact: 38 skills, 11 grupos, nenhum órfão, H3 e H4 verdes
      38 skills, 11 grupos. `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`
      (H3 e H4). `python3 scripts/validate-agents.py` -> `agents checked: 3   findings: 0`.
      `agentskills validate` aprova as três skills tocadas — fecha a lacuna E.3(b): o validador de
      referência não julga o valor de `metadata.category`.

- [x] V.3 README atualizado na tabela de plugins, na nota do bloco r3f e na tabela de migração
      Tabela de plugins, nota do bloco r3f e tabela de migração, as três no `README.md`.

- [ ] V.4 `openspec archive regroup-plugins-by-project-domain --yes` after all groups above are `[x]`
