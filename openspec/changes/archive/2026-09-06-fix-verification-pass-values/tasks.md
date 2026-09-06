## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `1b7b592` (topo de `master`, 2026-09-06):

      - `skills/claude-statusline/SKILL.md` — 9,9K; a seção `## Verify` em `:130-142`, com o bloco
        `bash` que canaliza um JSON de exemplo para `~/.claude/statusline.sh` e passa por
        `sed 's/\x1b\[[0-9;]*m//g'`; a frase "to confirm optional segments disappear cleanly" logo
        abaixo.
      - `skills/claude-statusline/references/statusline.sh` — 12,2K, o script que a skill entrega.
      - `skills/documentation/references/examples.md` — as nove linhas de saída esperada; a de `:158`
        é `# Expected: All containers start without errors`, e as outras oito nomeiam valor.
      - `openspec/specs/skills-authoring/spec.md:703` — o requisito *A prescribed verification states
        what passes*, com quatro cenários, entrado por `2026-09-06-update-documentation-prerequisites`.
      - `openspec/changes/archive/2026-09-06-update-documentation-prerequisites/design.md` — a `D3`,
        que decide o requisito sem validador e registra a medição que sustenta a decisão.

- [x] E.2 Ferramentas e fontes sondadas: comando -> fragmento da saída

      - Varredura por comentário de saída esperada em `skills/*/**/*.md` (regex
        `# (Expected|Esperado|Should print|Output)`) -> `linhas de saída esperada no catálogo: 9`,
        todas em `skills/documentation/references/examples.md` e `references/templates.md`.
      - Varredura por prosa com verbo de verificação (`verify|confirm|check that|conferir que`) ->
        `linhas em prosa que prescrevem verificação: 67, em 17 skills`, com
        `documentation 16`, `verify-before-claiming 6`, `claude-statusline 5`, `k8s-tune-resources 5`.
      - `echo '<json do documento>' | bash skills/claude-statusline/references/statusline.sh | sed …`
        -> três linhas: `🤖 Opus 4.8 | ⚡ medium | 🧠 thinking enabled | ⏱️  1h 26m | 💰 $2.47`,
        `📝 +1347 -156 | ↑ In 135k $0.10 · ♻️ 95% · ↓ Out 2k $0.05`,
        `📊 ctx ▓▓▓▓▓░░░ 63% | 🚦 5h ▓▓▓▓░░░░ 57% | 7d ▓▓▓▓▓▓░░ 84%`; `exit=0`.
      - O mesmo script com `current_usage: null`, fora de repositório git -> duas linhas:
        `🤖 Opus 4.8 | ⚡ medium | 🧠 thinking disabled | 💰 $0.00` e `📊 ctx ▓▓▓▓▓░░░ 63%`.
      - `openspec validate fix-verification-pass-values --strict` ->
        `Change 'fix-verification-pass-values' is valid`.

- [x] E.3 O que não deu para sondar

      As 67 linhas de prosa não foram julgadas uma a uma: foram amostradas as duas skills com passo
      executável (`claude-statusline` e `k8s-tune-resources`), e só a primeira tinha violação. As
      outras 15 skills ficaram sem julgamento individual, então o número deste change é **piso, não
      censo** — e é assim que ele é reportado. Também não foi sondado o comportamento do
      `statusline.sh` em terminal sem suporte a emoji ou a barra de blocos: a saída medida é a de um
      terminal UTF-8, e o documento não afirma nada sobre os outros.

- [x] E.4 Escopo e desdobramentos

      Um desdobramento fica registrado: julgar as 15 skills restantes das 17 que a segunda varredura
      marcou. Não entra aqui porque o custo de ler 67 linhas de prosa agora é maior que o de abrir um
      item quando um terceiro caso aparecer — e o critério que abriu **este** item era justamente
      "mais de um caso", que já foi satisfeito com dois.

## 2. As duas correções

- [x] 2.1 `claude-statusline`: a seção `## Verify` passa a trazer a saída medida
- [x] 2.2 `claude-statusline`: "disappear cleanly" vira os segmentos nomeados
- [x] 2.3 `documentation/references/examples.md:158`: a ausência vira valor observável
- [x] 2.4 `metadata.version` das duas skills sobe

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi exercitado pelo seu ponto de entrada real

      A seção `## Verify` é uma instrução executável, e o ponto de entrada dela é o próprio comando
      que ela manda rodar — com o script que a skill entrega, não com o instalado na máquina.

      - entry point: `echo '<o JSON do documento>' | bash skills/claude-statusline/references/statusline.sh | sed 's/\x1b\[[0-9;]*m//g'`
        -> `🤖 Opus 4.8 | ⚡ medium | 🧠 thinking enabled | ⏱️  1h 26m | 💰 $2.47`, mais duas linhas,
        `exit=0`
      - entry point: o mesmo com `current_usage: null` e fora de repositório git ->
        `🤖 Opus 4.8 | ⚡ medium | 🧠 thinking disabled | 💰 $0.00` e `📊 ctx ▓▓▓▓▓░░░ 63%`
      - entry point: `bash generate.sh` -> `Generated wrappers for 35 skills`
      - entry point: `python3 scripts/validate-skills.py` -> `skills checked: 35   findings: 0`

- [x] S.2 Matriz de casos medida, como contagens

      Varredura: 133 arquivos de skill lidos; 9/9 linhas de saída esperada julgadas uma a uma, com
      8/9 corretas e 1/9 fraca; 67 linhas de prosa marcadas em 17 skills, das quais 2/17 skills
      amostradas por terem passo executável, com 1/2 em violação. Confirmados: 2 casos — o gatilho do
      `E.4` da change de origem era "mais de um".

      Correção: 2/2 casos fechados. Saída do `## Verify` medida em 2/2 cenários (cheio e vazio),
      com 3 linhas e 2 linhas respectivamente. Versões: 2/2 skills tocadas com bump.

      Portões: 35/35 skills sem achado; 22/22 classes de defeito no selftest; 4/4 na higiene;
      12/12 padrões de segredo; 6/6 items do rito validados.

- [x] S.3 O que escapou ou se comportou diferente do esperado

      Uma coisa. A **primeira varredura devolveu zero achados**, o que contradizia o que já se sabia —
      o `templates.md` tem três `# Expected` visíveis a olho nu. A causa era o filtro que eu tinha
      posto para olhar só dentro de cerca de código: o `templates.md` traz cercas **escapadas** dentro
      de blocos markdown, e o pareamento não-guloso da regex casava o abre-cerca externo com o
      escape interno, cortando 8.364 dos 13.042 caracteres do arquivo. Sem o filtro, os 9 achados
      aparecem. É a mesma classe do defeito que o requisito cobre: um instrumento cujo resultado
      esperado — zero — é satisfeito por um erro de leitura, e não distingue "não há violação" de
      "não olhei".

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado
      Evidência: o loop do `ci.yml` replicado -> `frontmatter fail=0 sobre 35 skills`;
      `claude-statusline` em `1.3.0` e `documentation` em `3.1.1`, ambos semver,
      `author: solvelab`, `license: MIT`, `compatibility` presente, `name` == diretório.
- [x] Q.2 Todo conteúdo de skill tocado em inglês (locale do catálogo)
      Evidência: as duas seções reescritas são inglês; `check-identifier-locale.py --selftest` ->
      `selftest OK`; `validate-skills.py` -> `skills checked: 35   findings: 0`.
- [x] Q.3 Gatilhos da description testáveis e sem colisão
      Evidência: `git diff master -- skills/ | grep -cE '^[-+] *description'` -> `0`; nenhuma
      description foi tocada, e nenhum gatilho se moveu.
- [x] Q.4 Sem doutrina duplicada
      Evidência: a regra do valor que aprova continua só no `skills-authoring`; o `claude-statusline`
      **aplica** a regra sem reafirmá-la, e o `examples.md` corrige um exemplo sem reescrever a regra
      do `templates.md`. Tabela Canonical Home do `design.md`: quatro linhas, três `already canonical`
      e uma `link`.
- [x] Q.5 Todo exemplo de código em skill tocada usa identificador em inglês
      Evidência: os blocos novos são saída de terminal, sem identificador; o `# Expected` reescrito do
      `examples.md` cita `Started`, `Error` e `Exited`, que são strings do próprio `docker compose`;
      detector de locale -> `findings: 0`.

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate --strict` verde e `validate-rite.sh` verde
      Evidência: `openspec validate fix-verification-pass-values --strict` ->
      `Change 'fix-verification-pass-values' is valid`; `bash scripts/validate-rite.sh` ->
      `rite gate OK`, `Totals: 6 passed, 0 failed`.
- [x] V.2 Descoberta do catálogo intacta
      Evidência: `ls -d skills/*/ | wc -l` -> `35`, inalterado; nenhuma skill criada, removida ou
      renomeada; `bash generate.sh` -> `Generated wrappers for 35 skills`;
      `validate-repo-hygiene.py` -> `repo hygiene: 0 findings`, que cobre as contagens publicadas.
- [x] V.3 README e docs atualizados onde o change altera composição ou uso
      Evidência: nenhuma mudança de composição ou de uso — duas seções de conteúdo e dois bumps.
      `README.md` intocado de propósito; o check H2 da higiene é o que acusaria contagem defasada, e
      está verde.
- [x] V.4 `openspec archive fix-verification-pass-values --yes` depois do merge do PR
      Evidência: PR #168 mergeado em 2026-09-06 (`c9c2634` na master);
      `openspec archive fix-verification-pass-values --yes` -> `skills-authoring: update`,
      `~ 1 modified`, `Change 'fix-verification-pass-values' archived`; `openspec list` -> a change
      saiu das ativas.
