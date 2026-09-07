# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `21f228c` (master, base de `backlog/183-tdd-skill`) em 2026-09-06:

      - `openspec/specs/skills-authoring/spec.md:11-21` — o mapa canônico inteiro, copiado por
        completo no delta antes de ganhar a entrada `tdd`.
      - `openspec/specs/skills-catalog/spec.md` — o requisito *A published cost claim carries
        re-runnable backing*, incluindo os dois cenários que #182 acrescentou.
      - `skills/execute-backlog/SKILL.md:121-130` — passos 8, 9 e 10, onde entra a linha opt-in.
      - `skills/bug-hunter/SKILL.md:4` (a description) e `:90-98` (a seção *See also*).
      - `skills/lean-code/SKILL.md:123-131` — o piso de uma checagem, com a frase que já delega a
        `bug-hunter` o que vem depois.
      - `skills/python-rest-api/SKILL.md` — frontmatter e a seção `## Testing`.
      - `research/tdd/arms-block.md` (o texto medido), `research/tdd/protocol.md` (a linha NO-CLAIM
        e o Amendment 1), `research/tdd/results.md` (a leitura condição por condição).
      - `generate.sh:39-68`, `:224-234`, `:241-268`; `.github/workflows/ci.yml:49-68` e `:131-151`.
      - `README.md:61` (tabela de plugins) e `README.md:607-617` (tabela de skills backend/testing).
      - `openspec/changes/archive/2026-09-06-add-lean-code-doctrine/` — proposal, design e os dois
        deltas, como molde de skill de doutrina com casa canônica.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      `openspec new change add-tdd-skill --schema skills-rite` ->
      `Created change 'add-tdd-skill' at openspec/changes/add-tdd-skill/`

      `openspec validate add-tdd-skill --strict` -> `Change 'add-tdd-skill' is valid`

      `grep -m1 'version:' skills/bug-hunter/SKILL.md` -> `  version: 2.2.5`; idem
      `lean-code` -> `1.0.0`, `execute-backlog` -> `1.8.3`, `python-rest-api` -> `1.4.2` — as quatro
      que sobem por `scripts/validate-skill-version.py`.

      `grep -c "^#### Scenario:"` no requisito *A published cost claim…* -> `10` (estado publicado
      depois de #188).

      `grep -rniE "\btdd\b|test-driven|red[- ]green|test first|failing test" skills/ claude/ plugins/`
      -> só `skills/claude-statusline/SKILL.md:79` (`green <50`), limiar de cor.

      `openspec list` -> `No active changes found.` antes desta change.

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Duas lacunas, nenhuma preenchida com substituto plausível:

      (a) **Se a `description` da skill `tdd` colide, na prática, com os gatilhos de `bug-hunter`.**
      O gate Q.3 é revisão humana; não há detector automático de colisão de trigger no repositório
      (`scripts/validate-skills.py` checa presença de cláusula `Do NOT use for`, não colisão). O que
      dá para provar é a presença da fronteira nas duas descriptions; que ela resolva o roteamento
      em uso é observação de campo, e fica aberta.

      (b) **Se a skill publicada reproduz o efeito medido no bloco.** #182 mediu
      `research/tdd/arms-block.md` como bloco always-on, não a skill carregada como project skill.
      O arm `skill` existe no harness e não rodou. Fica aberta e nomeada como follow-up em E.4 —
      **não** é resolvida por esta change, e a skill não afirma nada sobre isso.

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Follow-ups anotados e **não** feitos:

      - Rodar o arm `skill` de `research/tdd/` contra a skill publicada, para saber se ela reproduz
        o efeito do bloco (a lacuna (b) de E.3). O harness já suporta: `--prepare-arms` passa a
        preparar o terceiro arm assim que `skills/tdd/SKILL.md` existir.
      - Tarefas com folga em `green` para a pergunta de correção, escolhidas a partir de um run
        só-baseline (levantado por #182, registrado lá).
      - Tracks de TDD para outros stacks além de pytest.
      - Inverter a ordem default de `execute-backlog` — decisão separada, fora desta change por D1.

      Nada em `research/`, `generate.sh` ou `.github/workflows/` foi alterado.

## 2. A skill

- [x] 2.1 `skills/tdd/SKILL.md` com frontmatter uniforme (name == diretório, `description` folded
      ≤1024 no valor YAML-parseado, `metadata.author: solvelab`, `metadata.version` semver,
      `metadata.category: testing`, `license: MIT`, `compatibility` ≤500)
- [x] 2.2 A doutrina não contradiz `research/tdd/arms-block.md`, conferida linha a linha
- [x] 2.3 Seção de quando o ciclo **não** se aplica, linkando o piso de `lean-code` sem repeti-lo
- [x] 2.4 `Do NOT use for` na description: quebrar código já escrito é `bug-hunter`, suíte de API é
      `api-resilience-testing`, o piso de uma checagem é `lean-code`
- [x] 2.5 Bloco `Verified against` dizendo o que foi probado, a data, e que **não há ganho medido a
      citar** — a medição existe e deu NO-CLAIM
- [x] 2.6 `skills/tdd/references/track-python-pytest.md` com a mecânica do ciclo em pytest,
      linkando o stack de teste de `python-rest-api` em vez de repeti-lo
- [x] 2.7 Nenhum número de ganho em `skills/tdd/**`

      `grep -rnE "[0-9]+/[0-9]+|[0-9]+ ?%|\$[0-9]" skills/tdd/` -> nenhuma linha.
      `grep -c "research/tdd" skills/tdd/SKILL.md` -> `5`: a skill aponta o registro cinco vezes e
      não cita cifra nenhuma. Os três ponteiros no corpo usam a URL do GitHub, porque um wrapper
      copiado não resolve caminho do clone (C12 de `scripts/validate-skills.py`, que pegou isso).

## 3. Casa canônica e cross-links

- [x] 3.1 `openspec/specs/skills-authoring/spec.md` — mapa canônico ganha `test order → tdd` (pelo
      delta desta change, no archive)
- [x] 3.2 `skills/execute-backlog/SKILL.md` passo 8 — uma linha opt-in; ordem default intacta
- [x] 3.3 `skills/bug-hunter/SKILL.md` — cross-link e fronteira temporal na description
- [x] 3.4 `skills/lean-code/SKILL.md` — cross-link do piso para `tdd`
- [x] 3.5 `skills/python-rest-api/SKILL.md` — cross-link do stack de teste
- [x] 3.6 `metadata.version` sobe nas quatro skills editadas

## 4. Catálogo

- [x] 4.1 `./generate.sh` rodado e wrappers commitados junto
- [x] 4.2 `README.md` — linha na tabela de plugins (`:61`) e na tabela de skills (`:607-617`)

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)

      O caminho do usuário desta skill é o CLI carregando `skills/tdd` numa sessão. Com a skill no
      checkout, o harness de `research/tdd` passa a preparar o terceiro arm sozinho:

      `python3 research/tdd/run.py --prepare-arms --arms-root <scratch>/tdd-arms3 --rules-ref 5a65437
      --claude-block research/tdd/arms-block.md` ->
      `arm skill  claude-snippet.md = sentinel + always-on block; workspace gets .claude/skills/tdd
      copied from /home/diegops/ai-skills/skills/tdd` -> `preflight OK`

      `python3 research/tdd/run.py --probe-isolation --arms-root <scratch>/tdd-arms3 --model
      claude-haiku-4-5-20251001` -> `probe PASSED isolation=settings-sources cost=$0.192`, com
      `skill  sentinel 3/3  hook-events 0 (maintainer 0)  caveman-marker-untouched 3/3
      skill-visible 1/1`

      Fonte de verdade lida direto do transcrito, o evento `system/init` que lista o que o CLI de
      fato carregou: `skill` -> `['tdd', 'deep-research', ...]`, 18 skills, **`tdd` presente**;
      `baseline` e `block` -> 17 skills, **`tdd` ausente**.

      Esta é a prova de que a skill **carrega e é oferecida ao roteador**. Não é a medição do arm
      `skill`, que é follow-up declarado em E.3 (b) e E.4 e **não** foi rodada.
- [x] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent

      **Tinham de disparar e dispararam**: `tdd` no `system/init` do arm `skill` 1/1; preflight OK
      3/3 arms; sonda PASS 3/3 arms; sentinela 3/3 em cada arm; `validate-skills.py` reconhecendo
      37 skills 1/1; `validate-skill-version.py` vendo 5 skills alteradas com 5 bumps.

      **Tinham de ficar em silêncio e ficaram**: `tdd` ausente do `init` em `baseline` e `block`
      2/2; eventos de hook do mantenedor 0 em 12 chamadas; marcador caveman intacto 3/3;
      `grep` de número em `skills/tdd/**` -> 0 ocorrências; drift de wrapper depois de
      `generate.sh` -> 0; findings em `validate-skills.py` -> 0 sobre 37 skills.

      **Escapes conhecidos que ficaram em silêncio**: a matriz paga do arm `skill` não rodou (é
      follow-up); não há detector automático de colisão de trigger entre `tdd` e `bug-hunter`, e a
      lacuna (a) de E.3 continua aberta por isso.
- [x] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

      Duas coisas, ambas registradas:

      1. **O modelo se auto-reportou errado.** Perguntado pela sonda quais skills tinha
         disponíveis, o arm `skill` respondeu `'SKILLS: none\nDONE'` — enquanto o evento
         `system/init` da mesma sessão listava `tdd`. O veredito está certo porque o harness
         prefere o `init` à resposta do modelo, mas a consequência é que **perguntar ao modelo
         quais skills ele tem não é instrumento confiável**; o evento do carregador é. Vale para
         qualquer sonda futura deste repositório.
      2. **`validate-repo-hygiene.py` pegou duas contagens paradas no README** (`:51` e `:95`
         diziam 36 com 37 skills no tree) que a tabela de skills sozinha não teria mostrado.
         Corrigidas; H2 voltou a 0 findings.

      Nada mais se comportou diferente do previsto.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme nas cinco `SKILL.md` tocadas, valores conferidos e não só presença

      `description` de `tdd` medida no valor YAML-parseado -> **1019** caracteres (limite 1024; a
      primeira redação tinha 1147 e foi cortada). `compatibility` -> 205 (limite 500).
      `python3 scripts/validate-skills.py` -> `skills checked: 37   findings: 0`.
- [x] Q.2 Todo conteúdo de skill em inglês, incluindo o track

      `skills/tdd/SKILL.md` e `references/track-python-pytest.md` inteiramente em inglês, como o
      resto do catálogo; a prosa deste `tasks.md` segue em português como o repositório.
- [x] Q.3 Triggers testáveis e sem colisão com `bug-hunter`; `Do NOT use for` presente dos dois lados

      A fronteira é temporal e está escrita nas duas descriptions: `tdd` -> *"Do NOT use to break
      code already written or hunt edge cases after the fact (that is bug-hunter)"*; `bug-hunter`
      -> *"nor for deciding whether the test is written before the code (that is tdd, which runs
      before the change while this rite runs after it)"*. Nenhum gatilho de `tdd` repete um de
      `bug-hunter`: os de lá são "bug hunt", "adversarial test", "break it", "anti-forge"; os daqui
      são "TDD", "test-driven", "red-green", "write the test first", "teste primeiro".
      **Limite declarado**: não existe detector de colisão neste repositório — dá para provar a
      presença da fronteira, não o roteamento em uso (lacuna (a) de E.3).
- [x] Q.4 Nenhuma doutrina duplicada: o piso é linkado, a metodologia adversarial é linkada, a
      tabela Canonical Home do `design.md` declara cada uma

      A seção *When the cycle does not apply* linka `lean-code` para o piso e diz explicitamente
      que decide *quando* a checagem é escrita, não *quanto* teste a mudança deve. O track linka o
      stack de `python-rest-api` em vez de repeti-lo. `lean-code` ganhou a linha recíproca no
      mesmo lugar onde já delegava a `bug-hunter`.
- [x] Q.5 Exemplos de código em inglês (`code-locale`)

      Todo identificador dos exemplos do track é inglês (`parse_duration`, `percent_change`,
      `test_a_bare_number_is_rejected`); nenhum `# locale-ok` foi necessário.

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-tdd-skill --strict` green

      `openspec validate add-tdd-skill --strict` -> `Change 'add-tdd-skill' is valid`
      `bash scripts/validate-rite.sh` -> `Totals: 3 passed, 0 failed (3 items)`, `rite gate OK`
- [x] V.2 Catalog discovery intact: 37 skills, `ai-skills-testing` com 3, sem órfão

      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings` (H2 e H3 conferem
      contagem publicada contra o tree). `validate-skill-version.py` -> `5 skill(s) changed, 5 with
      content changes`, 0 findings. `scan-secrets.py` -> `no credentials found`.
      `bash generate.sh` + `git status` -> sem drift.
- [x] V.3 README atualizado nas duas tabelas

      Tabela de plugins (`README.md:61`) -> `ai-skills-testing` passa a listar
      `api-resilience-testing`, `bug-hunter`, `tdd`. Tabela de skills backend/testing ganha a linha
      de `tdd`. Duas contagens paradas em `:51` e `:95` corrigidas de 36 para 37, apontadas por H2.
- [ ] V.4 `openspec archive add-tdd-skill --yes` after all groups above are `[x]`
