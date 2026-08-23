## 1. Evidence & Sources (MANDATORY)

<!-- Sempre o PRIMEIRO grupo: prove antes de escrever. Registre o COMANDO e um fragmento da SAÍDA
     CRUA, nunca uma conclusão. Doutrina: skill verify-before-claiming. -->

- [x] E.1 Todo caminho local que este change usa foi ABERTO e lido em `f99695a` em 2026-08-23, não
      recordado: `scripts/validate-spec-rite.py` (a linha 227, `os.environ.get("PR_BODY", "")`, e as
      regex `WAIVER` / `WAIVER_NO_REASON`), `.github/workflows/ci.yml` (o passo *OpenSpec rite gate*
      e seu bloco `env:`), `openspec/specs/skills-catalog/spec.md` (o requisito *The rite gates
      evidence before it gates quality*, cujo texto integral o delta reproduz),
      `skills/execute-backlog/references/spec-rite.md` e `README.md` (para confirmar que **não**
      nomeiam o transporte), e `openspec/changes/archive/2026-08-23-add-spec-rite-gate/design.md`
      (a decisão original de transporte, que este change corrige)
- [x] E.2 Probado em 2026-08-23, não suposto:
      `gh run view 32648727841 --log --job 97216916829 | awk '/OpenSpec rite gate.*group.Run bash/,/endgroup/'`
      -> `env:` / `PR_BODY: Closes #89` seguido do corpo inteiro do PR #90 — é a medição que motiva
      este change;
      `grep -n "PR_BODY" README.md skills/execute-backlog/references/spec-rite.md` -> sem saída
      (nenhum doc nomeia o transporte, logo nenhum doc muda);
      docs do GitHub Actions (docs.github.com, variables reference, lidas em 2026-08-23) ->
      `GITHUB_EVENT_PATH` = *"The path to the file on the runner that contains the full event webhook
      payload"*;
      `openspec --version` -> `1.6.0`
- [x] E.3 Lacuna nomeada, não preenchida com substituto plausível: as docs descrevem o arquivo como
      "full event webhook payload" mas não enumeram `pull_request.body` nele. A inferência é sólida
      — `github.event` é esse mesmo payload e é o que hoje alimenta o `env` — porém só a execução de
      CI deste PR confirma. Por isso o override e a degradação para corpo vazio existem, e por isso
      um critério de aceite é o `grep` no log do run real. Nenhuma outra lacuna.
- [x] E.4 Follow-ups listados, não executados aqui: (a) declarar `spec_rite` no
      `.github/backlog.yml` deste repositório em vez de depender do default fail-closed; (b) auditar
      outros passos do `ci.yml` caso algum passe a receber entrada de terceiro; (c) `openspec
      templates` sem `--schema` ignorar o `openspec/config.yaml` (follow-up herdado do change
      anterior, ainda aberto)

## 2. Transporte: do env para o payload do evento

- [x] 2.1 `read_pr_body` em `scripts/validate-spec-rite.py`: `PR_BODY` quando definido, senão
      `pull_request.body` do arquivo em `GITHUB_EVENT_PATH`, senão vazio — precedência declarada em
      comentário
- [x] 2.2 Leitura defensiva: `json.load` em `try/except` estreito; payload ausente, ilegível ou sem a
      chave vira corpo vazio com aviso, nunca traceback
- [x] 2.3 `.github/workflows/ci.yml`: remover o bloco `env:` do passo do gate
- [x] 2.4 Cabeçalho do script atualizado: de onde a dispensa é lida e por que não do ambiente

## 3. Cobertura do leitor novo

- [x] 3.1 `--selftest` cobre: payload sintético em arquivo temporário lido, arquivo ausente tratado,
      override `PR_BODY` vencendo o payload
- [x] 3.2 Os cenários `S0`/`S1`/`S2` e os seis casos de falso positivo continuam intactos e verdes

## 4. Quality Gates (MANDATORY)

<!-- Revisão adversarial dos skills tocados — não happy-path. -->

- [x] Q.1 Frontmatter uniforme em cada `SKILL.md` tocado: nenhum skill é tocado por este change, e
      isso é declarado aqui em vez de deixado em branco
- [x] Q.2 Todo conteúdo de skill tocado em inglês: nenhum skill tocado (ver Q.1)
- [x] Q.3 Triggers de description testáveis: nenhuma description muda
- [x] Q.4 Zero doutrina duplicada: a regra "um gate não publica o que lê" entra **dentro** do
      requisito que já governa a dispensa, não num requisito vizinho, conforme a tabela Canonical
      Home do `design.md`
- [x] Q.5 Exemplos de código em inglês: o código tocado é script de CI, com identificadores em
      inglês vindos do Glossary da issue #92 (`read_pr_body`, `GITHUB_EVENT_PATH`, `PR_BODY`)

## 5. Validation & Closure (MANDATORY)

<!-- Sempre o último grupo. "Pronto" é verificável, não é opinião. -->

- [x] V.1 `openspec validate fix-waiver-transport --strict` verde
- [x] V.2 `bash scripts/validate-rite.sh` verde neste branch e `--selftest` verde
- [x] V.3 `bash generate.sh && git diff --exit-code` limpo; `validate-skills.py`,
      `selftest-validate-skills.py` e `validate-repo-hygiene.py` verdes
- [x] V.4 Run `32650044909` (job `97220085306`, PR #93): o bloco `env:` sumiu — o cabeçalho vai de
      `shell: /usr/bin/bash -e {0}` direto para `##[endgroup]` — e o grep por seis trechos exclusivos
      do corpo do PR (`canal de divulgação`, `add-mask`, `Known gaps`, `read_pr_body() lê`,
      `O que foi descartado`, `Spec-rite: fix-waiver-transport`) retorna `0` em todos. O gate seguiu
      medindo: `spec-rite gate: 0 findings (base origin/master, 8 changed path(s), 1 active change(s))`
- [ ] V.5 `openspec archive fix-waiver-transport --yes` — **após o merge**, em PR separado
