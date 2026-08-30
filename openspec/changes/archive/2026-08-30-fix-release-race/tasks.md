## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `7738d94` (`chore(release): 2.15.0`), topo de `master` em 2026-08-30:

      - `.github/workflows/ci.yml` — 191 linhas; job `release` em 132-191, `concurrency` em 19-21,
        `actions/checkout@v5` do release em 142-145 sem `ref`, `npx semantic-release` em 174,
        step `check_release` em 176-191.
      - `.releaserc.json` — `branches: ["master"]`, `tagFormat: "v${version}"`,
        `@semantic-release/git` com `message: "chore(release): ${nextRelease.version} [skip ci]"`.
      - `openspec/specs/skills-catalog/spec.md:487` — requisito
        *"The repository itself is gated, not only its skills"*, com o cenário
        *"The uncovered part is declared, not implied"*.
      - `openspec/config.yaml` — `schema: skills-rite`.

- [x] E.2 Ferramentas e comportamentos externos probados contra a versão instalada

      ```
      npm pack semantic-release@25 --silent
      -> semantic-release-25.0.9.tgz
      ```

      ```
      grep -rn "behind the remote" package/
      -> package/index.js:92:          `The local branch ${context.branch.name} is behind the remote one, therefore a new version won't be published.`
      ```

      ```
      sed -n '86,96p' package/index.js
      ->   try {
      ->     try {
      ->       await verifyAuth(options.repositoryUrl, context.branch.name, { cwd, env });
      ->     } catch (error) {
      ->       if (!(await isBranchUpToDate(options.repositoryUrl, context.branch.name, { cwd, env }))) {
      ->         logger.log(
      ->           `The local branch ${context.branch.name} is behind the remote one, therefore a new version won't be published.`
      ->         );
      ->         return false;
      ```

      ```
      sed -n '209,216p' package/lib/git.js
      -> export async function verifyAuth(repositoryUrl, branch, execaOptions) {
      ->   try {
      ->     await execa("git", ["push", "--dry-run", "--no-verify", "--", repositoryUrl, `HEAD:${branch}`], execaOptions);
      ```

      ```
      sed -n '296,303p' package/lib/git.js
      -> export async function isBranchUpToDate(repositoryUrl, branch, execaOptions) {
      ->   return (
      ->     (await getGitHead(execaOptions)) ===
      ->     (await execa("git", ["ls-remote", "--heads", "--", repositoryUrl, branch], execaOptions)).stdout.match(
      ```

      O exit code que esse `return false` produz, em `package/cli.js:43-63`:

      ```
      sed -n '54,56p' package/cli.js
      ->     await (await import("./index.js")).default(options);
      ->     return 0;
      ->   } catch (error) {
      ```

      A falha de campo que motivou a change, na run que a produziu:

      ```
      gh run view 32959050372 --log --job <Semantic Release>
      -> [10:37:41 AM] [semantic-release] › ℹ  The local branch master is behind the remote one, therefore a new version won't be published.
      ```

      ```
      gh run view 32959050372 --json jobs -q '.jobs[] | "\(.name): \(.conclusion)"'
      -> Validate: success
      -> Semantic Release: success
      ```

- [x] E.3 O que não pôde ser probado

      Nada ficou por probar. Os dois pontos que poderiam ter virado achismo — o texto exato da
      mensagem e o código de saída do processo — foram lidos no pacote publicado, acima. O
      comportamento de `actions/checkout` num evento `push` não foi lido no código da action, mas
      não precisa ser: a run 32959050372 é a prova empírica de que o HEAD do runner ficou atrás do
      remoto, que é o único fato de que a change depende.

- [x] E.4 Checagem de escopo

      A change faz só o que a proposta pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up:

      - O step `Check if new release was created` (linhas 176-191) escreve `new_release=false` tanto
        para "nada a publicar" quanto para "não consegui publicar"; depois desta change o segundo
        caso falha antes de chegar lá, mas o step continua ambíguo se outro motivo de recusa
        aparecer.
      - O job `release` não tem timeout declarado.
      - `npm install -g` a cada run (linha 169) é reinstalação completa com cache só de `~/.npm`.

## 2. Publicação sobre o topo do branch

- [x] 2.1 `actions/checkout` do job `release` passa a receber `ref: master`, mantendo
      `fetch-depth: 0`, com o comentário que explica por que a serialização por `concurrency` torna
      isso seguro e por que o commit pode ser mais novo que o do `validate` desta run (D1)
- [x] 2.2 O step `Run semantic-release` grava a saída em arquivo, preservando o comportamento atual
      de falhar quando o próprio semantic-release falha (D3)
- [x] 2.3 Step novo falha o job quando a saída contém `is behind the remote one`, com mensagem
      `::error::` que nomeia a causa e o que fazer (D3)
- [x] 2.4 O step do tripwire declara dentro de si o próprio ponto cego: casa uma string de uma
      versão pinada do semantic-release e fica mudo se o upstream reescrever a mensagem (D4)
- [x] 2.5 `concurrency` (linhas 19-21) fica intocado, e a razão fica escrita junto ao tripwire (D2)

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 O tripwire foi exercitado pelo caminho real, com a saída observada

      O trecho de shell do step foi extraído literalmente do workflow e rodado sobre os logs
      **reais** do job `Semantic Release`, baixados com
      `gh run view <id> --log --job <Semantic Release>`:

      ```
      bash tripwire.sh   # semantic-release.log = log da run 32959050372 (behind the remote)
      -> ::error::semantic-release refused to publish: the checked-out branch is behind the remote one. [...] Nothing was published by this run.
      -> exit 1
      ```

      ```
      bash tripwire.sh   # semantic-release.log = log da run 32957035719 (docs #101, nada a publicar)
      -> (sem saida)
      -> exit 0
      ```

      ```
      bash tripwire.sh   # semantic-release.log = log da run 32959201966 (publicou v2.15.0)
      -> (sem saida)
      -> exit 0
      ```

      O que cada log de fato dizia, medido antes de rodar o tripwire:

      ```
      grep -oE "There are no relevant changes.*|is behind the remote one.*|Published release .*" log-*.txt
      -> 32959050372: is behind the remote one, therefore a new version won't be published.
      -> 32957035719: There are no relevant changes, so no new version is released.
      -> 32959201966: Published release 2.15.0 on default channel
      ```

      O `set -o pipefail` do step 2.2 também foi exercitado, porque sem ele o `tee` mascara a falha
      do semantic-release:

      ```
      bash -e -c 'falha() { return 1; }; falha 2>&1 | tee /dev/null; echo "sem pipefail exit=$?"'
      -> sem pipefail exit=0
      bash -e -c 'set -o pipefail; falha() { return 1; }; falha 2>&1 | tee /dev/null; echo "com pipefail exit=$?"'
      -> (nenhuma saida: o -e abortou no pipeline, que e o comportamento desejado)
      ```

      O `ref: master` (2.1) foi comprovado no merge desta própria change — o job `release` só roda
      em `push` para `master`, então a run do pull request não o executava. Run
      [33321015762](https://github.com/solvelab/ai-skills/actions/runs/33321015762), commit de merge
      `3f21979`:

      ```
      gh run view 33321015762 --log --job <Semantic Release>
      -> Checking out the ref
      -> /usr/bin/git checkout --progress --force -B master refs/remotes/origin/master
      -> The next release version is 2.15.1
      -> Created tag v2.15.1
      -> Published release 2.15.1 on default channel
      -> New release detected: v2.15.1 (was: v2.15.0)
      ```

      ```
      gh run view 33321015762 --json conclusion,jobs
      -> conclusion: success
      -> job Validate: success
      -> job Semantic Release: success
      ```

      O step `Fail if the release was skipped because the checkout was behind` executou nessa run e
      ficou mudo, que é o comportamento correto quando a publicação acontece. A string
      `is behind the remote one` aparece duas vezes no log do **job**, mas só porque o runner ecoa o
      próprio script do step (linhas 314-316 do log); o tripwire lê `semantic-release.log`, o arquivo
      com a saída do processo, e não o log do job — por isso não auto-disparou.

- [x] S.2 Matriz de casos medida, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | Tinha de disparar e disparou | 1/1 | run 32959050372 (checkout atrás do remoto) |
      | Tinha de ficar mudo e ficou | 2/2 | run 32957035719 (nada a publicar), run 32959201966 (publicou) |
      | Escape conhecido ficou mudo | 1/1 | mensagem do upstream reescrita — ver S.3 |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      Um escape, conhecido e declarado dentro do próprio step (D4): o tripwire casa a string
      `is behind the remote one`. Reescrita a mensagem pelo upstream, ele fica mudo sem avisar —
      medido:

      ```
      sed 's/is behind the remote one/is not up to date with the remote/' log-32959050372.txt > semantic-release.log
      bash tripwire.sh
      -> exit 0   (mudo, como o step declara)
      ```

      A mitigação é o pin de versão que já existe na instalação (`semantic-release@25`, linha 169 do
      workflow antes desta change). Nada mais escapou nem se comportou de forma diferente do
      esperado.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — **não se aplica**: esta change não toca
      nenhuma skill
- [x] Q.2 Conteúdo de skill tocado em inglês — **não se aplica** pelo mesmo motivo; o delta de spec
      desta change está em inglês, como o catálogo exige
- [x] Q.3 Gatilhos de descrição testáveis — **não se aplica**: nenhuma descrição de skill muda
- [x] Q.4 Sem doutrina duplicada: a regra "um check declara o que não cobre" é aplicada pelo
      workflow e não reescrita nele; ver a tabela de Canonical Home em `design.md`
- [x] Q.5 Identificadores em inglês no que a change introduz — ids de step, nome de arquivo de log e
      chaves de YAML — conforme o glossário da issue #104 e `code-locale`

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate fix-release-race --strict` verde
- [x] V.2 Descoberta do catálogo intacta: contagem de skills inalterada, sem órfão ou renomeado
- [x] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo — **não se
      aplica**: nada da composição muda
- [x] V.4 `openspec archive fix-release-race --yes` depois que todos os grupos acima estiverem `[x]`
