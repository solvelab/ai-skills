# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `master` (`ai-skills`) em 2026-09-20, base de
      `backlog/254-sprite-animation`:

      - `openspec/config.yaml` inteiro (schema `skills-rite`, as quatro portas e a nota de que
        `scripts/validate-rite.sh` é quem as posiciona, não o CLI).
      - `openspec/specs/skills-authoring/spec.md`: índice dos 22 requisitos
        (`grep -n '^#\{1,3\} '`), e na íntegra *Single canonical home per rule* (:11-83),
        *Uniform frontmatter metadata* (:84-142), *English as catalog locale* (:143-163),
        *Prescribed numbers carry the rule that produces them* (:183-218).
      - `skills/svg-animation/SKILL.md:1-40` (frontmatter, pin *Verified against*, abertura sobre
        defeito plausível) e `ls skills/svg-animation/` + `wc -l` das references
        (236 + 108 + 51 + 71 linhas).
      - `openspec/changes/archive/2026-09-10-add-terse-response-skill/`: `proposal.md` inteiro,
        `grep -n '^## ' design.md` e `tasks.md`, `specs/skills-authoring/spec.md:1-40`,
        `.openspec.yaml` (prova de que o prefixo de data é posto no arquivamento).
      - `scripts/validate-rite.sh:35-64` (nomes e posições exatas das portas).
      - `.github/backlog.yml` (Project #3; sem chave `spec_rite`, logo fail-closed).
      - `ls skills/` (39 skills) e `ls scripts/` (13 validadores).

      No `solvelab/my-company`, de onde vem toda a medição, lidos na branch
      `backlog/21-gerente-arte-propria` em 2026-09-20:
      `frontend/src/components/building/PersonFigure.tsx`,
      `useArrival.ts`, `DirectorFloor.tsx`, `Lift.tsx`,
      `frontend/src/index.css` (blocos `.person__sprite`, `@keyframes sprite-cycle`),
      `frontend/public/sprites/NOTICE`.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      `openspec --version` -> `1.6.0`

      `openspec new change 2026-09-20-add-sprite-animation-skill --schema skills-rite`
      -> `✖ Error: Change name must start with a letter` — por isso o id é
      `add-sprite-animation-skill` e a data entra no arquivamento, o que
      `archive/2026-09-10-add-terse-response-skill/.openspec.yaml` (`created: 2026-09-10`)
      confirma.

      `gh project field-list 3 --owner solvelab --format json` -> Status
      `PVTSSF_lADODxIkPc4Becf3zhY2qSU`, Size `PVTSSF_lADODxIkPc4Becf3zhY2qVM`,
      Estimate `PVTF_lADODxIkPc4Becf3zhY2qVQ`.

      Semântica de CSS, das duas páginas de especificação do MDN, não de memória:

      - `background-position` em porcentagem resolve como
        `(largura do contêiner − largura da imagem) × p`
        (<https://developer.mozilla.org/en-US/docs/Web/CSS/background-position>).
      - `steps(N)` com o termo padrão `end` produz os valores `k/N` para `k = 0..N−1`, e segura
        `100%` só no instante final
        (<https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/steps>).

      Consequência derivada das duas, e é o defeito 5:
      com `background-size: N00%`, `steps(N)` pousa em `k/N` de `−(N−1)` larguras, nunca em `−k`.

- [x] E.3 Every number this change publishes was measured, and the measurement is recorded with the
      command that produced it

      Medidas na arte (canal alfa, `PIL`, folhas do autor em
      `my-sprites/character/claude-code-person-manager-*.png`):

      - passada centro a centro, máximo entre os 8 quadros: **148 px** numa figura de **433 px**
        -> `0,342` altura de figura.
      - grupos da folha combinada em zooms diferentes: largura de cabelo deu fator `1,60` para o
        grupo sentado e largura de rosto deu outro número. **As duas medidas são inválidas entre
        vistas diferentes** — é o defeito 2, e a skill diz para não usar proxy.

      Medidas na tela (`playwright-core`, Chromium do cache do Playwright, dsf 2 e 4):

      - travessia da diretoria: `200,4 px` com boneco de `59,1 px` -> **3,39 alturas**.
      - antes da correção, com ciclo de `0,8 s` e travessia de `1,5 s`: as pernas andavam
        `1,28` altura enquanto o corpo andava `3,39` -> deslize **2,64×**.
      - depois, a 15 quadros/s e `2,64 s`: `4,95` ciclos × `0,684` = `3,39` alturas. Deslize zero.
      - `background-position-x` observado ao longo do ciclo:
        `0 / −36,3782 / −72,7564 / −109,135 / −181,891 / −218,269 / −254,647 px`, todos múltiplos
        inteiros da largura de quadro `36,3782 px`. É a prova de que
        `background-size: auto 100%` cai no quadro.

      Convenção de taxa, de terceiro e citada como convenção, não como medição própria:
      ciclo de 8 quadros a 10 quadros/s, e taxas divisoras de 60 (10/15/20/30) para não brigar com
      a composição a 60 Hz
      (<https://novasprite.tech/blog/how-many-frames-sprite-animation>,
      <https://www.spritesheets.ai/blog/how-to-create-a-walk-cycle-spritesheet>).

## 2. A skill

- [x] 2.1 `skills/sprite-animation/SKILL.md` com frontmatter no padrão
      (`name`, `description` em bloco dobrado com os gatilhos, `metadata.author: solvelab`,
      `metadata.version`, `metadata.category: frontend`, `license: MIT`, `compatibility`)
- [x] 2.2 As quatro regras, cada uma com o defeito medido ao lado
- [x] 2.3 A conta do deslize publicada como fórmula, não como constante
- [x] 2.4 `references/css-technique.md`: a técnica medida e a que falha, com a razão de
      especificação e os deslocamentos observados
- [x] 2.5 `references/cutting-sheets.md`: recorte por componente conexo, normalização de escala
      sem proxy, célula única
- [x] 2.6 Fronteira escrita contra `svg-animation` e `r3f-animation`

## 3. Casa canônica e catálogo

- [x] 3.1 Mapa canônico: a entrada está no delta
      `specs/skills-authoring/spec.md` desta change. A spec viva é atualizada no arquivamento,
      como `archive/2026-09-10-add-terse-response-skill` fez — o `terse-response` no mapa vivo é
      a prova.
- [x] 3.2 `README.md`: linha na tabela de frontend, `ai-skills-frontend` na tabela de plugins, e
      as duas contagens de 39 para 40 (`:51`, `:113`)
- [x] 3.3 `bash generate.sh` -> `Generated wrappers for 40 skills` e
      `Generated 11 category plugins`. Sem mudança no `generate.sh`: a categoria `frontend` já
      tem tema, e o guard de `GROUP_THEME` passou.
- [x] 3.4 Espelho gerado por `generate.sh`, junto com `codex/`, `cursor/` e `copilot/`
- [x] 3.5 Fronteira nos dois. Em `r3f-animation` coube na `description` (457 de 1024). Em
      `svg-animation` **não coube**: a `description` estava em 997 de 1024, e a menção mais curta
      a esta skill a levou a 1066 — C10 pegou. A fronteira foi para o corpo, antes de
      *CRITICAL: the three gates*. Versões: `svg-animation` 1.1.4 -> 1.1.5,
      `r3f-animation` 1.2.1 -> 1.2.2.

## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded

      **Caminho tentado e não alcançado, declarado:** `CLAUDE_CONFIG_DIR` de rascunho com um
      `CLAUDE.md` que faz `@…/skills/sprite-animation/SKILL.md` — o caminho de instalação de
      verdade. `claude --print --model claude-haiku-4-5-20251001` naquele diretório devolve
      `Not logged in · Please run /login`: a config isolada não tem credencial, e copiar
      credencial para um rascunho não é caminho aceitável. Fica registrado como degrau não
      alcançado, não como passo cumprido.

      **Caminho exercitado:** o texto da skill em contexto, na config real, A/B com o mesmo
      prompt e o mesmo modelo (`claude 2.1.278`, `claude-haiku-4-5-20251001`).

      Prompt: *"I have an 8-frame walk-cycle sprite sheet. My character crosses the room in 1.5
      seconds. What animation-duration should I put on the CSS sprite cycle?"*

      Sem a skill -> `` `animation-duration: 1.5s` `` … *"The CSS will cycle through all 8 frames
      during that 1.5 second cross. Each frame displays for ~187ms."* — é o defeito 4 inteiro:
      um ciclo na travessia toda, 5,3 quadros/s, nenhuma menção a passada nem a deslize.

      Com a skill -> *"Measure **stride** (foot-to-foot gap ÷ figure height) and **distance** …
      Pick fps: 10, 15, 20, or 30. Then: `duration = distance ÷ ((2 × stride × fps) ÷ 8)` …
      Without stride and distance, using 1.5s is the defect: feet will slide if the math doesn't
      align."* — recusa a constante, pede as duas medidas, devolve a fórmula e restringe a taxa.

      Prova de campo, mais forte que a sonda: os quatro defeitos foram cometidos e corrigidos em
      código de verdade no `solvelab/my-company` (PR #22), cada correção medida no navegador. As
      regras desta skill não são hipótese; são o que sobrou depois de errar.

- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      **Tinham de disparar e dispararam** (1 prompt, 3 regras observadas na mesma resposta):
      recusar a constante 1/1; pedir passada e distância 1/1; restringir a taxa a divisores de 60
      1/1.

      **Tinha de ficar calado e ficou** 1/1: *"I want a tree swaying in the wind. There is no art
      yet."* -> *"Use `svg-animation` — sprite-animation requires pre-existing frames … Read
      `skills/svg-animation/SKILL.md`"*. A skill não reclamou o pedido e citou a irmã pelo caminho
      com prefixo `skills/`, que é a forma que resolve em toda instalação.

      **Escapes conhecidos que ficaram calados**: a sonda A/B é n=1 por caso, em Haiku, e não
      mede aderência sob pressão de prazo nem em modelo maior. Não afirmo cobertura além disso.

## 5. Quality Gates (MANDATORY)

- [x] Q.1 `python3 scripts/validate-skills.py` -> `skills checked: 40   findings: 0`
- [x] Q.2 `python3 scripts/validate-skill-version.py` ->
      `0 findings (base origin/master, 3 skill(s) changed, 3 with content changes)` — as três são
      `sprite-animation` (nova, 1.0.0), `svg-animation` (1.1.5) e `r3f-animation` (1.2.2)
- [x] Q.3 `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`
- [x] Q.4 `python3 scripts/scan-secrets.py` -> `scanned 1116 files … no credentials found`
- [x] Q.5 Varredura regra a regra do `SKILL.md`: as quatro regras citam o defeito medido; a
      tabela de abertura nomeia os quatro com o número; a conta do deslize vem com os valores que
      a produziram e com a fórmula; a taxa traz a razão (composição a 60 Hz) e a convenção de
      terceiro citada como convenção. A única regra sem medição própria é a taxa convencional de
      10 quadros/s, marcada como convenção com as duas fontes.
- [x] Q.6 A tabela *Where this skill ends* nomeia quatro skills irmãs em uma linha cada, sem
      reproduzir mecanismo nenhum. C12 verde depois de trocar os links relativos pela forma
      `skills/<skill>/SKILL.md` com o nome em prosa.

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `bash scripts/validate-rite.sh` -> `rite gate OK`, com
      `spec-rite gate: 0 findings (base origin/master, 0 changed path(s), 1 active change(s))`
- [x] V.2 `openspec validate add-sprite-animation-skill --strict` ->
      `Change 'add-sprite-animation-skill' is valid`; `openspec validate --all --strict` ->
      `Totals: 4 passed, 0 failed`
- [ ] V.3 PR aberto com `Closes #254` e a tabela de evidências
- [ ] V.4 Change deixada ativa; o arquivamento é passo do mantenedor depois do merge
