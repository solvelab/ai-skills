# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recorded from memory

      Lidos em `74b2875` (master, base de `backlog/216-statusline-render-budget`) em 2026-09-07:

      - `skills/claude-statusline/references/statusline.sh` — o bloco git da linha 2 (as quatro
        chamadas, `git remote get-url origin`, `git symbolic-ref`, `git status --porcelain`,
        `git rev-parse --git-dir`) e o bloco de tokens, para confirmar que o cursor é keyed por
        `session_id` e não por caminho.
      - `skills/claude-statusline/SKILL.md` — as linhas 109 e 131, que recomendam cachear
        `git status` por `session_id`, e a seção que declara o estado persistido.
      - `openspec/specs/skills-catalog/spec.md` — *Shipped scripts state what they persist*, *A
        shipped script reads the quantity its host publishes* e *A shipped script's output is a
        function of its input* (esta última adicionada em `74b2875`), para saber o que já está
        coberto e o que esta change precisa acrescentar.
      - `openspec/changes/archive/2026-09-07-refactor-statusline-token-accounting/tasks.md` — o box
        E.4 e o S.2, origem dos dois itens.

- [x] E.2 Every external tool, flag or behaviour this change asserts was probed; the command and a
      fragment of its output are recorded

      **Custo individual das quatro chamadas git**, média de 20 execuções no `ai-skills`
      (1032 arquivos versionados):

      ```
      git remote get-url origin        1 ms
      git symbolic-ref --short HEAD    1 ms
      git status --porcelain           9 ms
      git rev-parse --git-dir          1 ms
      ```

      **Decomposição do render frio** no transcript de 40 173 321 bytes:

      ```
      cat > /dev/null            151 ms   (quase tudo syscall de escrita)
      grep -c '"usage"'            3 ms
      jq (parse completo)        336 ms
      grep '"usage"' | jq        288 ms   (o pré-filtro quase não paga: 21.6 MB dos 40 têm usage)
      ```

      **O cursor sobrevive ao `--resume`**: o transcript de 40 MB abrange
      `2026-08-23T14:50:32.990Z` a `2026-08-30T15:42:08.021Z` — sete dias — com um único
      `sessionId` (`3dd26d41-…`). Uma sessão não roda sete dias seguidos; é retomada, mesmo id,
      mesmo arquivo, mesmo cursor.

      **Ganho medido do cache**, 20 renders cada, mesmo payload e mesmo repositório:

      ```
      master:  43 ms/render
      novo:    29 ms/render      delta: -14 ms (-33%)
      ```

      A primeira tentativa cacheava o **texto** do porcelain e mediu **43 ms contra 43 ms**, ganho
      zero: o `cksum` da chave e o escape de newline custavam o que o `git status` custava. Cachear
      as duas **contagens** deixa o caminho de acerto sem nenhum fork e também elimina os dois
      `grep -c`, o que explica os 14 ms serem maiores que os 9 do `git status`.

      **Ferramentas**: `openspec --version` -> `1.6.0`;
      `openspec validate update-statusline-render-budget --strict` -> `is valid`;
      `bash -c 'echo $BASH_VERSION'` -> `5.2.37(1)-release`, e `EPOCHSECONDS` responde dentro dele.

- [x] E.3 Anything that could NOT be probed is written down as an open question

      Duas lacunas, em `design.md` § *Open Questions*:

      1. **A validade de 2 segundos não foi calibrada por medição.** Ela foi escolhida por
         raciocínio; quantos renders acontecem por segundo numa sessão real não foi medido, porque
         esta máquina não tem `refreshInterval` configurado e sem ele os renders são disparados por
         evento. Errar a validade muda quanto se economiza, nunca a correção.
      2. **O custo de `git status --porcelain` num repositório grande de verdade não foi medido.**
         Os 9 ms vêm de um repositório de 1032 arquivos. O argumento de que escala é estrutural — o
         comando percorre a árvore — e não uma medição em escala.

- [x] E.4 Adjacent improvements were listed as follow-ups rather than performed

      Três coisas vistas e **não** feitas:

      1. As três chamadas git de 1 ms poderiam ser cacheadas também. Não foram, e o requisito ADDED
         desta change é justamente a regra que proíbe fazer isso sem medição.
      2. A poda de 30 dias do diretório de estado só dispara quando um `usage_state` novo é criado.
         Os arquivos `.git` do cache são pegos pela mesma poda, já que ela varre o diretório
         inteiro, mas a condição de disparo continua acoplada ao outro arquivo. Fica como está.
      3. O contador poderia distinguir untracked (`??`) dos modificados, que hoje não aparecem em
         nenhum dos dois contadores. É mudança de comportamento visível e não pertence a um item de
         orçamento de render.

## 2. Implementação

- [x] 2.1 Cachear as duas contagens de `git status --porcelain` por sessão e diretório, validade de
      2 s, caminho de acerto sem forks (D1, D2, D3) — #216
- [x] 2.2 Deixar branch, remote e git-dir sem cache (D1) — #216
- [x] 2.3 Nenhuma mudança de código para #219: a decisão é `wontfix`, registrada em D4

## 3. Documentação e espelhos

- [x] 3.1 `SKILL.md`: as recomendações passam a descrever o que o script faz; o estado novo é
      declarado conforme *Shipped scripts state what they persist*; versão bumpada
- [x] 3.2 `./generate.sh` para regenerar os espelhos

## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi EXERCITADO pelo caminho do usuário, com entry point e saída OBSERVADA

      Entry point: `bash skills/claude-statusline/references/statusline.sh < <payload>`, `HOME`
      isolado, contra o repositório de trabalho real.

      `git status --porcelain | grep -c '^.[MD]'` -> `1`, e o render:

      ```
      🔗 ai-skills | 🌱 backlog/216-statusline-render-budget | ✚ 1 | ↑ In 453.8M ~$330.91 · ♻️ 98% · ↓ Out 785k ~$23.99
      ```

      Frio e com cache produzem a mesma contagem.

- [x] S.2 Matriz de casos como contagens

      - **4/4** transições da validade, com arquivo **versionado** (o primeiro teste usou um
        untracked e não mexeu no contador — `✚` conta modificados, não untracked; o teste estava
        errado, não o código): git real 1 -> render `✚ 1`; edita, git real 2, render ainda `✚ 1`
        (cache quente); após 2.2 s, render `✚ 2`; reverte, após 2.2 s, render `✚ 1`.
      - **2/2** invalidações por diretório: payload apontando para `/tmp` -> linha 2 sem repo, sem
        branch e sem contador; voltando ao repositório -> `🔗 ai-skills | 🌱 … | ✚ 1` de volta.
      - **5/5** renders idênticos do mesmo payload — o cache não introduziu não-determinância, o que
        importa porque o requisito de determinância entrou no catálogo na change anterior.
      - **1/1** medição de ganho: 43 ms -> 29 ms por render, 20 execuções cada.
      - **2/2** correções de contagem conferidas contra o git: `staged=0 modified=1` no git,
        `✚ 1` no render, frio e cacheado.

- [x] S.3 O que escapou

      Três coisas, nomeadas:

      1. **Nenhum repositório grande foi exercitado.** O ganho de 14 ms é de um repositório de 1032
         arquivos; a premissa de que cresce com a árvore é estrutural, não medida em escala.
      2. **Concorrência entre dois renders escrevendo o cache não foi testada.** O registro é escrito
         inteiro num `printf` só, e o pior caso é um render ler um registro pela metade — que o
         guarda de dígitos descarta, caindo no caminho frio. Não observado.
      3. **`refreshInterval: 1` não foi exercitado**, então a cadência real de renders por segundo —
         que é o que decide quanto a validade de 2 s economiza — segue não medida.

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter da `claude-statusline` intacto e versão bumpada
- [x] Q.2 Conteúdo em inglês na skill; nenhum identificador novo em português
- [x] Q.3 Triggers da description continuam testáveis e sem colisão
- [x] Q.4 Zero doutrina duplicada; a tabela Canonical Home do `design.md` respeitada
- [x] Q.5 Gates do repositório verdes — comandos e saídas no corpo do PR

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate update-statusline-render-budget --strict` -> `is valid`
- [x] V.2 `bash scripts/validate-rite.sh` -> `rite gate OK`
- [x] V.3 Descoberta do catálogo intacta: as mesmas 38 skills versionadas
- [x] V.4 A composição do catálogo não mudou; o que mudou está no `SKILL.md` da skill
- [x] V.5 `openspec archive update-statusline-render-budget --yes` na mesma diff do PR (S1)
