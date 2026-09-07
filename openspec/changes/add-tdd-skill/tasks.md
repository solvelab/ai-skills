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

- [ ] 2.1 `skills/tdd/SKILL.md` com frontmatter uniforme (name == diretório, `description` folded
      ≤1024 no valor YAML-parseado, `metadata.author: solvelab`, `metadata.version` semver,
      `metadata.category: testing`, `license: MIT`, `compatibility` ≤500)
- [ ] 2.2 A doutrina não contradiz `research/tdd/arms-block.md`, conferida linha a linha
- [ ] 2.3 Seção de quando o ciclo **não** se aplica, linkando o piso de `lean-code` sem repeti-lo
- [ ] 2.4 `Do NOT use for` na description: quebrar código já escrito é `bug-hunter`, suíte de API é
      `api-resilience-testing`, o piso de uma checagem é `lean-code`
- [ ] 2.5 Bloco `Verified against` dizendo o que foi probado, a data, e que **não há ganho medido a
      citar** — a medição existe e deu NO-CLAIM
- [ ] 2.6 `skills/tdd/references/track-python-pytest.md` com a mecânica do ciclo em pytest,
      linkando o stack de teste de `python-rest-api` em vez de repeti-lo
- [ ] 2.7 Nenhum número de ganho em `skills/tdd/**`

## 3. Casa canônica e cross-links

- [ ] 3.1 `openspec/specs/skills-authoring/spec.md` — mapa canônico ganha `test order → tdd` (pelo
      delta desta change, no archive)
- [ ] 3.2 `skills/execute-backlog/SKILL.md` passo 8 — uma linha opt-in; ordem default intacta
- [ ] 3.3 `skills/bug-hunter/SKILL.md` — cross-link e fronteira temporal na description
- [ ] 3.4 `skills/lean-code/SKILL.md` — cross-link do piso para `tdd`
- [ ] 3.5 `skills/python-rest-api/SKILL.md` — cross-link do stack de teste
- [ ] 3.6 `metadata.version` sobe nas quatro skills editadas

## 4. Catálogo

- [ ] 4.1 `./generate.sh` rodado e wrappers commitados junto
- [ ] 4.2 `README.md` — linha na tabela de plugins (`:61`) e na tabela de skills (`:607-617`)

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme nas cinco `SKILL.md` tocadas, valores conferidos e não só presença
- [ ] Q.2 Todo conteúdo de skill em inglês, incluindo o track
- [ ] Q.3 Triggers testáveis e sem colisão com `bug-hunter`; `Do NOT use for` presente dos dois lados
- [ ] Q.4 Nenhuma doutrina duplicada: o piso é linkado, a metodologia adversarial é linkada, a
      tabela Canonical Home do `design.md` declara cada uma
- [ ] Q.5 Exemplos de código em inglês (`code-locale`)

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-tdd-skill --strict` green
- [ ] V.2 Catalog discovery intact: 37 skills, `ai-skills-testing` com 3, sem órfão
- [ ] V.3 README atualizado nas duas tabelas
- [ ] V.4 `openspec archive add-tdd-skill --yes` after all groups above are `[x]`
