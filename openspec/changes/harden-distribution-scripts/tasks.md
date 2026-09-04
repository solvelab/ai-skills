## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `d2918ed` (`docs(openspec): arquiva as duas changes de svg-animation`), topo de
      `master` em 2026-09-04:

      - `install.sh` — 185 linhas; `--tool` lê `$2` em 108; `git pull` sem `--ff-only` em 148;
        `case "$TOOL"` com a rejeição de valor desconhecido em 158-181, depois do clone.
      - `update.sh` — 70 linhas; "Cursor rules" em 6 e 20; `pull --ff-only` com mensagem e dica em
        47-51; `bash generate.sh >/dev/null && echo` em 59.
      - `generate.sh` — lê `VERSION` (linha 180, `VERSION_STR`) e `skills/*/SKILL.md` (78, 170);
        `rm -rf "$PLUGINS_OUT"` em 149; grava `"version": "${VERSION_STR}"` (189) em cada
        `plugins/<group>/.claude-plugin/plugin.json` (185-195). Não é editado por esta change.
      - `README.md` — linha 141 ("regenerate the Cursor wrappers"), 145 (`curl | bash`), 154 ("all
        tool wrappers"), 216 ("edit `~/ai-skills/claude/global/personal-rules.md`").
      - `.github/workflows/ci.yml` — 231 linhas; step `Repo hygiene self-test` em 102-103; o step
        novo entra logo depois dele.
      - `openspec/specs/skills-catalog/spec.md:487` — *"The repository itself is gated, not only
        its skills"*, cenário *"The uncovered part is declared, not implied"*.
      - `openspec/config.yaml` — `schema: skills-rite`.
      - `openspec/changes/archive/2026-08-30-fix-release-race/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md` — modelo de estilo desta change.
      - `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py`,
        `scripts/validate-spec-rite.py` — o que os gates exigem de `tasks.md` e do diff.

- [x] E.2 Ferramentas e comportamentos externos probados contra a versão instalada

      ```
      git --version
      -> git version 2.47.3
      openspec --version
      -> 1.6.0
      ```

      O `&&` engole a falha sob `set -e` (motivo de D3):

      ```
      bash -c 'set -e; f() { echo "generate boom" >&2; return 3; }; f >/dev/null && echo "  ok"; echo "after: still running"'
      -> generate boom
      -> after: still running
      -> exit=0
      ```

      `--tool` sem valor sob `set -u` (motivo de D4):

      ```
      bash -c 'set -euo pipefail; while [[ $# -gt 0 ]]; do case "$1" in --tool) TOOL="$2"; shift 2;; esac; done' probe --tool
      -> probe: line 1: $2: unbound variable
      -> exit=1
      ```

      O que o git diz num clone divergente, com e sem `--ff-only` (motivo de D5):

      ```
      git -C b pull
      -> hint: You have divergent branches and need to specify how to reconcile them.
      -> fatal: Need to specify how to reconcile divergent branches.
      -> exit=128
      git -C b pull --ff-only --quiet
      -> hint: Diverging branches can't be fast-forwarded, you need to either:
      -> (mais 8 linhas de hint:)
      -> fatal: Not possible to fast-forward, aborting.
      -> exit=128
      ```

      O filtro da guarda, num clone de `d2918ed` com `VERSION` editado, `skills/untracked.txt`
      criado e `README.md` editado (motivo de D1 e D2):

      ```
      git status --porcelain --untracked-files=no -- VERSION skills/
      ->  M VERSION
      git status --porcelain
      ->  M README.md
      ->  M VERSION
      -> ?? skills/untracked.txt
      ```

      O branch inicial de `git init` num `HOME` vazio (motivo de fixar `HEAD` do bare em D6):

      ```
      HOME=<vazio> git init -q dflt && git -C dflt symbolic-ref HEAD
      -> refs/heads/master
      ```

      Contagem de skills que o caso idempotente tem de reportar:

      ```
      ls skills | wc -l
      -> 35
      ```

- [x] E.3 O que não pôde ser probado

      O comportamento de `actions/checkout` num `pull_request` (HEAD destacado no commit de merge)
      não foi lido no código da action; D6 não depende dele, porque o teste faz
      `git push <bare> HEAD:refs/heads/master`, que funciona com HEAD destacado ou não. A run de CI
      do pull request é o que fecha essa lacuna. Nada mais ficou por probar.

- [x] E.4 Checagem de escopo

      A change faz só o que a issue #113 pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up:

      - `generate.sh` grava em `plugin.json` qualquer conteúdo de `VERSION` sem validar semver —
        pertence à issue que reescreve esse bloco, como a #113 registra em "Fora de escopo".
      - `install.sh` e `update.sh` duplicam o bloco de pull/mensagem em vez de compartilhar uma
        função; como os dois rodam via `curl | bash` sem o repositório presente, não há de onde
        carregar um arquivo comum.
      - O README (`README.md:154`) já dizia o certo; só a linha 141 contradizia.

## 2. update.sh — guarda de entradas, falha visível, texto

- [ ] 2.1 A regeneração roda só quando `git status --porcelain --untracked-files=no -- VERSION
      skills/` está vazio; caso contrário imprime a lista, o comando que limpa, pula a regeneração e
      não aborta o update (D1)
- [ ] 2.2 `bash generate.sh` sai do `&&`: falha vira exit ≠ 0 com a saída capturada (D3)
- [ ] 2.3 O `pull --ff-only` captura o stderr do git e o imprime indentado sob a mensagem própria e
      a dica, com `advice.diverging=false` (D5)
- [ ] 2.4 Cabeçalho e `--help` dizem "all tool wrappers" e o cabeçalho declara o que a guarda não
      cobre (D2)

## 3. install.sh — validação antes do clone, ff-only no re-run

- [ ] 3.1 `--tool` lê `${2:-}`; valor vazio é erro de uso com a lista suportada, exit 1 (D4)
- [ ] 3.2 `SUPPORTED_TOOLS` valida o valor logo após o parse, antes de `command -v git` e do clone;
      `--help` e a mensagem de erro usam a mesma lista (D4)
- [ ] 3.3 Re-run faz `git pull --ff-only` com a mesma mensagem, dica e detalhe indentado de
      `update.sh` (D5)
- [ ] 3.4 `AI_SKILLS_REPO_URL` sobrepõe `REPO_URL`, documentado no cabeçalho junto com o que a
      guarda não cobre (D6)

## 4. Teste de fumaça e gate

- [ ] 4.1 `scripts/smoke-install-scripts.sh`: bare local a partir do HEAD, `HOME` temporário por
      caso, cobrindo install padrão, re-run idempotente, `--legacy`, `--tool codex`, `--tool all`,
      `--tool bogus`, `--tool` sem valor, update limpo, update com `VERSION` sujo, update com
      `generate.sh` falhando, divergência sem `--force` (update e install) e com `--force` (D6)
- [ ] 4.2 O resumo final imprime a matriz em contagens `n/n` e o script sai 1 se qualquer caso
      falhar (D7)
- [ ] 4.3 Step novo em `.github/workflows/ci.yml`, logo após `Repo hygiene self-test`, rodando o
      teste de fumaça
- [ ] 4.4 `README.md:141` diz "all tool wrappers"

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniform on every touched SKILL.md: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [ ] Q.2 All touched skill content in English (catalog locale)
- [ ] Q.3 Description triggers testable: phrases a user would actually say route to this skill and
      do NOT collide with a sibling skill's triggers; "Do NOT use for" boundary present where overlap exists
- [ ] Q.4 No duplicated doctrine: every cross-cutting rule restated inline was replaced by a link to
      its canonical skill (see design.md Canonical Home table)
- [ ] Q.5 Every code example in a touched skill uses English identifiers, routes, keys and event
      names; a term kept in another language carries its reason inline (`code-locale`)

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate harden-distribution-scripts --strict` green
- [ ] V.2 Catalog discovery intact: skill count unchanged, no orphan/renamed leftovers
- [ ] V.3 README / docs updated where the change alters catalog composition or usage
- [ ] V.4 `openspec archive harden-distribution-scripts --yes` after all groups above are `[x]`
