# Change: Endurecer install.sh e update.sh contra árvore suja e divergência

## Why

Os dois scripts de distribuição aceitam estados que não conseguem honrar e falham de forma muda ou
crua. Medido em `d2918ed` (topo de `master` em 2026-09-04), num `HOME` falso:

- `update.sh:47` só protege contra divergência de commit (`git pull --ff-only`). Uma linha a mais
  em `VERSION`, sem commit, não barra o update; `generate.sh` roda em seguida e grava a versão suja
  em 10 `plugins/*/.claude-plugin/plugin.json` rastreados. O marketplace é servido do GitHub e o CI
  regenera de um checkout limpo, então o dano fica no clone local — mas fica até o release seguinte.
- `update.sh:59` executa `bash generate.sh >/dev/null && echo ...`. Sob `set -e` uma falha do
  `generate.sh` é engolida, porque o comando que falha está à esquerda do `&&`:

  ```
  bash -c 'set -e; f() { echo "generate boom" >&2; return 3; }; f >/dev/null && echo ok; echo "after"'
  -> generate boom
  -> after: still running
  -> exit=0
  ```

- `install.sh:148` usa `git pull` sem `--ff-only`; com divergência morre com
  `fatal: Need to specify how to reconcile divergent branches.` (exit 128) e nenhuma dica de
  recuperação, ao contrário de `update.sh:48-50`.
- `install.sh:108` lê `$2` sem guarda: `bash install.sh --tool` morre com `$2: unbound variable`.
  O valor de `--tool` só é validado depois do clone (`install.sh:158-180`): `--tool bogus` clona
  antes de falhar.
- `update.sh:6`, `update.sh:20` e `README.md:141` dizem que o update regenera "Cursor rules";
  `generate.sh` regenera `claude/`, `codex/`, `cursor/`, `copilot/` e `plugins/`.
- Nenhum step do CI executa `install.sh` ou `update.sh`. O que a documentação promete sobre eles
  não tem gate.

E a restrição que define o desenho: `README.md:216` manda o usuário editar
`claude/global/personal-rules.md` no próprio clone. Uma guarda de árvore suja que bloqueasse o
update, ou que empurrasse para `--force` (`reset --hard`), destruiria exatamente esse uso.

## What Changes

- `update.sh` continua fazendo o pull sempre. A regeneração de wrappers passa a rodar só quando as
  **entradas** do `generate.sh` estão limpas (`git status --porcelain --untracked-files=no --
  VERSION skills/` vazio); caso contrário imprime a lista e como limpar, pula a regeneração e sai 0.
  Uma falha do `generate.sh` deixa de ser engolida: vira exit ≠ 0 com a saída do erro.
- `install.sh` valida `--tool` antes de qualquer clone ou pull, rejeita `--tool` sem valor com erro
  de uso, e no re-run faz `git pull --ff-only` com a mesma mensagem e dica de `update.sh`.
- Os dois scripts declaram no cabeçalho o que a guarda não cobre.
- `update.sh:6`, `update.sh:20` e `README.md:141` passam a dizer "todos os wrappers".
- `scripts/smoke-install-scripts.sh` (novo): teste de fumaça em `HOME` temporário, clonando de um
  bare local (nunca da URL do GitHub), cobrindo cada comportamento acima; step correspondente em
  `.github/workflows/ci.yml`.

Fora de escopo, por decisão da issue: guarda de semver em `generate.sh` (outra issue reescreve esse
bloco), prompt interativo em `--force` (`curl | bash` não tem stdin), e delegar o re-run de
`install.sh` para `update.sh`.

## Capabilities

### Modified Capabilities

- `skills-catalog`: ganha o requisito de que os scripts de distribuição recusam, ou contornam com
  mensagem, os estados que não podem honrar, e de que o CI os exercita. Hoje a capability governa o
  CI do repositório em *"The repository itself is gated, not only its skills"* e a publicação em
  *"Publication does not depend on the interval between merges"*, mas nada diz sobre o caminho de
  instalação e atualização que o README documenta.

## Impact

- `install.sh`, `update.sh` — guardas, mensagens, cabeçalhos.
- `scripts/smoke-install-scripts.sh` (novo), `.github/workflows/ci.yml` — um step novo no job
  `validate`, logo após o self-test de higiene.
- `README.md:141` — uma linha de texto.
- Nenhuma skill do catálogo muda: nenhum `SKILL.md` é tocado, a contagem de skills e a descoberta
  via `npx` ficam idênticas. `generate.sh` não é tocado.
- Consumidores: quem roda `update.sh` com `VERSION` ou `skills/` editados passa a ver a regeneração
  pulada com a lista; quem roda `install.sh --tool bogus` passa a falhar antes de clonar.
