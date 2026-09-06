## Context

Lido em `4ef1f3f` (2026-09-06), topo de `master`:

- `skills/code-locale/references/check-identifier-locale.py` (942 linhas): `COMMENT_SYNTAX` (203-213)
  e `EXT_LANG` (215-220) são as tabelas por linguagem; `strip_prose(line, lang, state)` (302-354)
  varre caractere a caractere e **descarta** comentários, docstrings e strings — devolve só o
  código e o delimitador de bloco aberto; `WAIVER_RE` (103), `ALLOWLIST_FILE` (102),
  `load_allowlist()` (405-415), `is_vendored()` (397), `project_relative()` (477), `scan_diff()`
  (616-685) lê `+++ b/<path>`, `@@`, e agrupa linhas `+` em runs; KNOWN LIMIT 7 registra que a prosa
  é retirada antes da análise. `--selftest` imprime `selftest OK: 7 content tiers fire, 16 clean
  cases stay silent, 6 path tiers fire, 10 path cases stay silent, 2 en-unknown tiers fire, 5
  en-unknown cases stay silent`.
- `claude/global/hooks/locale-rite.py` (655 linhas): `CHECK_PATH` (128) resolve o irmão por
  `parents[3]`; `load_check()` importa por caminho; `written_text()` (196) devolve `content`,
  `new_string`, os `new_string` de `MultiEdit`, `new_source`; `first_line_of()` (209) ancora o
  fragmento no arquivo; `findings_for()` (250) e `evaluate()` (350) decidem; `deny_reason()` (308)
  cabe em 20 linhas por construção (cabeçalho + 12 + `+N more` + advisory + 3 saídas = 18); o
  selftest tem 13 decisões `PostToolUse` e 12 `PreToolUse` com `cwd = "/tmp/locale-rite-selftest"`
  e dois `tempfile.TemporaryDirectory()`.
- `claude/global/hooks/locale-stop-gate.py` (653 linhas): `uncommitted_diff()` (233) monta o diff
  pinado contra o gitconfig; `gating_findings()` (291) chama `check.scan_diff()` e filtra
  advisory e vendored; `evaluate()` (324) devolve `{"decision": "block", "reason"}` ou
  `{"systemMessage"}` sob `stop_hook_active`; `_repo()` (391) cria repositórios temporários com
  `GIT_CEILING_DIRECTORIES`.
- `skills/code-locale/references/pre-commit-locale.sh`: `locate_check()` acha o detector em
  `$LOCALE_CHECK`, `$AI_SKILLS_HOME`, `~/ai-skills` ou por download pinado; o diff staged vai por
  `--diff -`; exit 1 só conta como recusa com a linha `findings:`; qualquer outro exit recusa como
  falha do detector.
- `skills/code-locale/references/ci-step.md`: um job, `curl` pinado por tag + `sha256sum -c`,
  `git diff origin/<base>...HEAD | python3 check-identifier-locale.py --diff - --no-english`.
- `openspec/specs/skills-catalog/spec.md`: os três requisitos que o delta modifica —
  `:662` *Code locale has a canonical home* (7 cenários), `:846` *The code-locale rite is enforced
  at the moment of the write* (11 cenários), `:1406` *The code-locale rite closes the turn, not
  only the write* (8 cenários).
- `openspec/changes/archive/2026-09-05-enforce-locale-on-write/` e
  `2026-09-04-close-ci-gate-holes/` — forma da casa.

## Goals / Non-Goals

**Goals:**

- Um repositório que declara `prose: pt-BR` (ou `en`) em `.code-locale` tem a mesma cadeia de gates
  para a prosa que a camada de máquina já tem: negação na escrita (comentário/docstring), aviso para
  `.md`, gate de Stop sobre o diff, pre-commit, step de CI.
- Sem declaração, os quatro pontos ficam **mudos** para prosa e continuam medindo identificadores
  exatamente como hoje; `--explain` diz por que está mudo.
- Precisão antes de recall: o detector só gera achado gating com evidência forte; fragmentos curtos,
  técnicos, entre aspas ou majoritariamente código são pulados e contados. Precisão adjudicada à mão
  ≥ 0,9 no corpus da issue antes de publicar.
- Nenhuma tabela duplicada: `COMMENT_SYNTAX`, `EXT_LANG`, `WAIVER_RE`, `load_allowlist`,
  `is_vendored`, `project_relative` vêm do irmão, importado por caminho.
- O detector de identificadores continua byte a byte igual; seu selftest não é editado.

**Non-Goals:**

- Traduzir prosa existente: `--report` sobre a árvore lista o legado, e só isso.
- Línguas fora de PT/EN; strings de UI e mensagens de log; texto dentro de fences de código em
  `.md`; um dicionário — a classificação é por palavras funcionais.
- Declarar a prosa do catálogo: README em inglês e changes em português; o repositório é misto e a
  skill diz isso.

## Decisions

### D1 — A declaração é um arquivo na raiz, uma chave por linha, e a ausência é silêncio

`.code-locale`, `chave: valor` por linha, `#` abre comentário. Só a chave `prose` é lida hoje;
`pt-BR`, `pt`, `en`, `en-US` normalizam para `pt`/`en`. Outro valor é erro (exit 2) que nomeia o
arquivo e os valores aceitos — um `prose: portugues` não pode abrir nem fechar a porta em silêncio.
Sem o arquivo, a direção "prosa" fica muda (exit 0, zero achados): é o que torna a regra adotável
num catálogo bilíngue e no repositório de quem nunca ouviu falar dela. A descoberta sobe do
diretório inicial até encontrar `.code-locale`, `.git` ou a raiz do sistema — `.git` para a
subida porque a declaração é do repositório, nunca de um diretório acima dele.

### D2 — O tokenizador é compartilhado, e o irmão não muda de comportamento

`strip_prose()` do detector de identificadores vira wrapper fino de `split_prose(line, lang,
state) -> (code, state, fragments)`, onde cada fragmento é `(kind, text)` com `kind` em `comment`,
`docstring`, `string`. O `kind` de um bloco vem do delimitador (`"""`/`'''` é docstring; `/* */`,
`--[[ ]]` é comentário) e o de uma linha continuada vem do `state` que já existia, então a
assinatura de `strip_prose()` e o que ela devolve não mudam. O detector de prosa importa o irmão
por `importlib` a partir de `Path(__file__).parent` — o mesmo mecanismo que os hooks já usam — e
nunca copia `COMMENT_SYNTAX`. O selftest do irmão prova que o código devolvido é o mesmo.

### D3 — Fragmentos são blocos, não linhas

Linhas consecutivas de comentário de linha (com o código da linha vazio), um bloco `"""..."""`
inteiro e um `/* */` inteiro viram **um** fragmento ancorado na primeira linha. Um comentário no fim
de uma linha de código é fragmento próprio. Mais palavras por fragmento é mais evidência por decisão
e um achado por docstring em vez de um por linha; o waiver vale em qualquer linha do fragmento ou
na linha acima da primeira, o que `scan_text()` do irmão já faz para nomes.

### D4 — Classificação por palavras funcionais em duas listas fechadas e disjuntas

Cada fragmento é limpo (trechos entre aspas e backticks, URLs, caminhos, identificadores com `_`,
camelCase, ALL_CAPS, pontilhados, números, `#tags` e `@menções` saem) e tokenizado em palavras
minúsculas com acento preservado — `só` não vira `so`, `não` não vira `nao`, porque deacentuar
cria colisões com o inglês. As listas `prose-words-pt.txt` e `prose-words-en.txt` só carregam
palavras que existem em **exatamente uma** das duas línguas: `a`, `as`, `no`, `do`, `me`, `sem`,
`via`, `so`, `ate`, `um`, `pro` ficam fora por serem ambíguas. A interseção é calculada no
carregamento e no `--selftest` e falha se não for vazia — a mesma disciplina do `ENGLISH_COLLISIONS`
do irmão. A decisão:

- menos de `MIN_WORDS = 4` palavras depois da limpeza -> `skipped:short`;
- mais da metade dos tokens crus parecem código -> `skipped:code`;
- nenhum hit em nenhuma lista -> `skipped:unknown`;
- `hits_wrong >= 2` e `hits_wrong >= 2 * hits_right + 1` -> língua errada; evidência **forte**
  quando `hits_wrong >= 3` e `hits_right == 0` -> gating para comentário/docstring, senão
  consultivo; parágrafo de `.md` é sempre consultivo.

Os limiares foram fixados pela issue e só mudam pela calibração de D7, com os números finais no
cabeçalho do detector.

### D5 — O que o detector declara que não vê (KNOWN LIMIT)

Strings de UI e mensagens de log não são medidas — chaves de log são máquina, mensagens são prosa,
e medir a string quebra toda mensagem de erro em inglês num serviço cujo cliente fala inglês; é
decisão, não esquecimento. Só PT e EN. Heurística de palavras funcionais, sem dicionário: um
fragmento sem palavra funcional é `skipped:unknown`, nunca "aprovado". Fences de código dentro de
`.md` não são medidos (o comentário dentro deles é de outra linguagem e de outro detector). Recall
parcial por desenho: precisão primeiro, porque um gate que nega errado é desligado em uma semana.

### D6 — Os hooks só medem prosa onde há declaração, e negam só o que é forte

`locale-rite.py`: depois da avaliação de identificadores, sobe do diretório do arquivo escrito
(fallback `cwd`) até `.code-locale`, `.git` ou a raiz. Com declaração, roda o detector de prosa sobre
o texto escrito (`content`, cada `new_string`, `new_source`) com a mesma âncora de `first_line_of()`.
`PreToolUse` nega em achado gating de comentário/docstring, com as três saídas no motivo — a linha
de saídas ganha, só quando há achado de prosa, uma linha dizendo que o mesmo `locale-ok:` vale na
linha do fragmento ou na de cima; o motivo continua em ≤ 19 linhas por construção. `PostToolUse`
avisa (`.md`, evidência fraca). Uma declaração inválida deixa o hook de escrita mudo para prosa
(um erro por escrita seria ruído) e o gate de Stop a nomeia numa `systemMessage` (uma vez por
turno, sem bloquear), para que um typo não desligue a regra em silêncio.
`locale-stop-gate.py`: com declaração na raiz do work tree, mede o mesmo diff com o detector de
prosa; gating bloqueia (junto com os achados de identificador, um só motivo), consultivo de `.md`
vira `systemMessage` sem bloquear; `stop_hook_active` continua nunca bloqueando duas vezes. Os
selftests novos criam diretórios temporários com e sem `.code-locale` e um `.git` que para a
subida, então nunca leem a declaração ou a allowlist de quem roda.

### D7 — Calibração medida antes de publicar

Três corridas, registradas em `tasks.md` S.3 e aqui:

- `--prose pt-BR --report` sobre `omnivoice-tts/server_addons` (somente leitura): cada achado
  gating lido e adjudicado; precisão exigida ≥ 0,90, senão a heurística estreita.
- `--prose en --report` sobre `skills/` e `claude/` do catálogo: prosa inglesa, esperado 0 gating;
  cada gating aqui é falso positivo a corrigir.
- `--prose pt-BR` sobre `openspec/changes/archive`: prosa portuguesa, esperado 0 gating (fences não
  são medidos).

Resultado (2026-09-06, `3de5bfe`, limiares da issue mantidos — `MIN_WORDS=4`, `WRONG_MIN=2`,
`STRONG_MIN=3`, `CODE_SHARE=0.5`): `server_addons` sob `pt-BR` -> **42 gating** (24 comentários,
18 docstrings), 7 consultivos, 18 pulados (7 short, 1 code, 10 unknown), 419 strings não medidas,
**precisão 42/42 = 1,00** com cada achado lido; catálogo `skills/` + `claude/` sob `en` -> **0
gating**, 1336 fragmentos medidos na língua declarada, 248 pulados; archive sob `pt-BR` -> **0
gating**, 1713 consultivos de `.md` que são parágrafos ingleses de verdade (958 em deltas de spec,
que são ingleses por regra; 755 em changes de 2026-07/08 e em 5 de setembro escritas em inglês).
Nenhum limiar foi estreitado; nenhuma palavra foi removida pela calibração — `do` saiu da lista PT
pelo selftest de interseção, antes dela. Contagens completas: `tasks.md` S.3.

Re-medição depois da revisão da change (2026-09-06, `tasks.md` 2.5 — pragmas de linter e
cabeçalhos de licença passam a `skipped:code`/`skipped:license`, kebab-case é limpo, uma linha de
contexto separa runs no `--diff`): `server_addons` -> **42 gating**, os mesmos por arquivo, cada um
relido, **42/42 = 1,00**, 7 consultivos, pulados 7 short / 4 code / 7 unknown; catálogo sob `en`
-> **0 gating**, 1342 medidos, pulados 61 / 78 / 104 / 14 waived; archive sob `pt-BR` -> **0
gating**, 1709 consultivos, 1 `license`. Os contadores do catálogo derivam com o texto do próprio
catálogo; a asserção é o gating.

### D8 — O kit roda os dois detectores só onde há declaração

`pre-commit-locale.sh`: depois do detector de identificadores, se
`$(git rev-parse --show-toplevel)/.code-locale` existe, roda `check-prose-locale.py --diff -` sobre
o mesmo diff staged, com o detector localizado **ao lado** do de identificadores (o de prosa
importa o irmão por caminho, então os dois têm de estar juntos; em modo download só o de
identificadores é baixado, e num repositório **declarado** o hook então **recusa** o commit
nomeando o que falta — a mesma regra do python3 ausente: uma gate que não consegue medir não
aprova; sem declaração o modo download segue igual). Mesma semântica de exit: 1 com `findings:`
recusa, 2 recusa nomeando a declaração inválida, qualquer outro recusa como falha do detector. `ci-step.md` documenta o step extra, condicionado a `[ -f .code-locale ]`,
e a declaração.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Prosa segue a língua do repositório; camada de máquina é inglês | `code-locale` | already canonical — a seção nova *Prose follows the repository* fica na skill; hooks, kit e README **apontam** para ela |
| Declaração `.code-locale` (formato, valores, ausência = silêncio) | `code-locale` | already canonical — definida uma vez na skill; o detector, os hooks e o kit citam o nome do arquivo e linkam |
| Waivers `locale-ok:` e `.identifier-locale-allow` | `code-locale` | already canonical — reutilizados (`WAIVER_RE`, `load_allowlist`), não redefinidos |
| O hook mede no momento da escrita; o gate de Stop fecha o turno | `skills-catalog` (spec do repositório) | already canonical — o delta modifica os dois requisitos; os docstrings declaram o KNOWN LIMIT |
| Provar antes de afirmar (calibração, probes) | `verify-before-claiming` | already canonical — D7 e `tasks.md` E.2/S.3 registram comandos e saídas |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — `split_prose`, `MIN_WORDS`, `ProseFinding`, `find_declaration`, `load_declaration`, `DECLARATION_FILE` |

## Risks / Trade-offs

- **Falso positivo em comentário técnico** -> limiar de 4 palavras, exclusão de aspas, backticks,
  URLs, caminhos e identificadores, `skipped:code` por maioria de tokens de código, gating só com
  ≥ 3 hits e 0 contrários, waiver de uma linha; precisão medida em D7 antes de publicar.
- **Repositório bilíngue** -> só quem declara é medido; o catálogo não declara e diz por quê.
- **Declaração com typo** -> exit 2 no detector e no pre-commit; hook de escrita mudo, gate de
  Stop nomeia o erro numa mensagem.
- **Custo por escrita** -> as listas têm ~100 linhas cada e são lidas uma vez por processo; o
  irmão já é importado pelo hook, e o detector de prosa o importa sem carregar a lista inglesa
  (`load_english()` é lazy).
- **Fence aberto fora do run em `--diff`** -> em modo diff um `.md` cujo fence começa numa linha
  não adicionada é lido como prosa; consultivo por construção, então nunca bloqueia; declarado.
- **Recall parcial** -> por desenho; o `--report` mostra quanto foi pulado e por quê, para que um
  `findings: 0` nunca seja lido como "tudo em português".

## Open Questions

Nenhuma sobre a forma: detector, hooks e kit seguem os irmãos já probados contra o bundle 2.1.261.
O que esta change não mede é o hook disparado pelo harness numa sessão real com um repositório
temporário declarando `pt-BR` — um subagente não dispara o hook da sessão; a corrida fica escrita
em `tasks.md` S.2 com o comando exato, para a sessão principal.
