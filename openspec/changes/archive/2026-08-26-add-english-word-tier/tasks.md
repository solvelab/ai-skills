## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos abertos e lidos, não recordados, no commit `9697de4` (2026-08-26):
      `skills/code-locale/references/check-identifier-locale.py` (`VERBS`, `NOUNS`, `MORPHOLOGY`,
      `ENGLISH_COLLISIONS`, `DOMAIN_KEEP`, `KEYWORDS`, `classify`, `segments`, `scan_text`,
      `scan_path`, `main`, KNOWN LIMIT), `skills/code-locale/SKILL.md`,
      `claude/global/hooks/locale-rite.py`, `scripts/validate-repo-hygiene.py` (regex `BYTECODE`),
      `generate.sh` (cópia de `references/` para `plugins/`)
- [x] E.2 Probes e medições, 2026-08-26:
      `classify('prazo')` -> `None`, `classify('chave')` -> `None` (o furo que motiva a change);
      `wc -l /usr/share/hunspell/en_US.dic` -> `79014`, e `grep -c "^read\(/\|$\)"` -> `0` no mesmo
      arquivo, que salta de `react/V` para `readability/SM` — dicionário do sistema tem buraco em
      palavra-base; `curl` do `words_alpha.txt` -> `370105` palavras, `content-length: 4234910`,
      `LICENSE.md` -> `released into the public domain`;
      medição de ruído sobre 961 segmentos deste repositório -> hunspell `34.7%`, hunspell com
      desflexão `13.1%`, lista de domínio público `10.3%`;
      split de composto -> `13/13` resolvidos (`selftest` -> `self+test`, `bytecode` -> `byte+code`)
- [x] E.3 Não probado, registrado em design.md como pergunta aberta: a taxa de ruído em repositório
      de terceiros com base legada. Este repositório é código deliberadamente inglês, então sua taxa
      não representa a de fora, e nada é afirmado sobre ela.
- [x] E.4 Escopo: entrega o tier advisory e as duas listas. Listado e **não** executado — tornar o
      tier bloqueante por padrão, que depende da medição de campo e é item próprio; e a fronteira
      `data`/`local`/`total`, que nenhuma das duas perguntas alcança e segue declarada no KNOWN LIMIT.

## 2. Dados

- [x] 2.1 `english-words.txt.gz` gerado do `words_alpha` (domínio público), filtrado para ≥ 3 letras
      — e não `MIN_SEGMENT` (4), porque a regra de composto precisa de `one` para resolver `oneline` —
      só `a-z`, ordenado, com proveniência em `english-words.SOURCE.md`
- [x] 2.4 `not-english.txt`: subtração auditada das 12 entradas que a lista importada carregava e
      não são inglesas (medido: 11 de 28 palavras PT comuns estavam nela)
- [x] 2.2 `programming-words.txt` curado a partir dos desconhecidos medidos neste repositório
- [x] 2.3 Proveniência, licença e data registradas onde o revisor lê antes de confiar

## 3. Tier `en-unknown`

- [x] 3.1 Carga preguiçosa das duas listas, uma vez por execução
- [x] 3.2 `is_english()` com a regra de composto (duas palavras conhecidas)
- [x] 3.3 Achado advisory, contado à parte, sem alterar exit code
- [x] 3.4 `--gate-unknown` torna os advisory bloqueantes
- [x] 3.5 `--en-dict PATH` substitui a lista; caminho ilegível é erro explícito
- [x] 3.6 Precedência: segmento já reportado por tier `pt-*` não repete
- [x] 3.7 KNOWN LIMIT atualizado com o que a pergunta de mundo fechado não alcança

## 4. Superfície e espelhos

- [x] 4.1 `--selftest` cobre disparo e silêncio do tier novo
- [x] 4.2 `locale-rite.py` mostra advisory como advisory, sem confundir com bloqueante
- [x] 4.3 `SKILL.md` documenta as duas perguntas e quando cada uma gata
- [x] 4.4 `./generate.sh` re-executado; espelhos idênticos

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 Hook real exercitado pelo caminho do harness, 2026-08-26.
      `python3 claude/global/hooks/locale-rite.py < payload.json` com `prazos/deadline.py` ->
      `code-locale: 2 unrecognised words (advisory) in the last write` e
      `tmp/prazos/deadline.py: prazos  [path-en-unknown: 'prazos']`;
      `python3 skills/code-locale/references/check-identifier-locale.py --en-dict /nao/existe` ->
      `error: --en-dict '/nao/existe' is not a readable file`;
      `--gate-unknown` sobre o mesmo arquivo -> `exit=1`, sem a flag -> advisory reportado e
      `findings: 1` apenas do tier gating.
- [x] S.2 Matriz medida: 10/10 casos com o veredito esperado — 2/2 gating (`pedido_id`,
      `api/servicos/`), 3/3 advisory (`prazo`, `chave_acesso`, diretório `prazos/`), 5/5 silenciosos
      (inglês, composto, vocabulário de programação, comentário PT, palavra das duas línguas).
      Selftest do detector: 7 tiers de conteúdo, 16 clean, 6 tiers de caminho, 9 clean de caminho,
      2 tiers `en-unknown`, 5 clean de `en-unknown`. Hook: 12/12 decisões.
      Ruído de campo neste repositório: **4/977 segmentos = 0,41%**, contra a meta declarada de <2%;
      antes das duas listas era 99/961 = 10,3%.
- [x] S.3 Escapou e está declarado: `dados` e `valor` seguem passando as duas perguntas, porque são
      palavras das duas línguas (`dado` é inglês de marcenaria) — KNOWN LIMIT 16, e removê-las
      dispararia em código inglês correto. Os 4 achados advisory que sobram no repo (`gdir`, `rtext`,
      `segs`, `unprobeable`) são abreviações e cunhagens deste projeto: mantidos de propósito, porque
      um tier advisory existe justamente para pôr isso na frente de um humano.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter do `code-locale` uniforme, `metadata.version` bumpado, `compatibility` ainda
      verdadeira (stdlib-only: `gzip` é stdlib)
- [x] Q.2 Conteúdo tocado do skill em inglês
- [x] Q.3 Gatilhos da descrição seguem testáveis e sem colisão
- [x] Q.4 Sem doutrina duplicada; links em vez de restatement
- [x] Q.5 Exemplos de código com identificadores ingleses

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-english-word-tier --strict` verde
- [x] V.2 Catálogo intacto: `python3 scripts/validate-skills.py` verde, 34 skills
- [x] V.3 README / docs atualizados onde o uso muda
- [x] V.4 `openspec archive add-english-word-tier --yes` depois do merge
