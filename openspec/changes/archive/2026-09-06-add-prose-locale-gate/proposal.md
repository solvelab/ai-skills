# Change: Medir a direção "prosa" do code-locale onde o repositório a declara

## Why

A regra do `code-locale` tem duas direções (`skills/code-locale/SKILL.md`, *The two layers*): prosa
segue a língua de trabalho do repositório; camada de máquina é inglês. Só a segunda é medida. O
detector `skills/code-locale/references/check-identifier-locale.py` **remove** comentários,
docstrings e strings antes de analisar (KNOWN LIMIT 7, `strip_prose()`), o hook `locale-rite.py`
trata "comentário em português" como caso mudo (`portuguese comment is prose, not a finding`), e
nada mede um comentário, uma docstring ou um `.md` em inglês num repositório cuja língua de trabalho
é português.

Medido pela issue #179 em 2026-09-06 no projeto do mantenedor `omnivoice-tts/server_addons` (8
`.py`, README e issues em português): 106 comentários com ≥ 4 palavras, **78 em inglês, 2 em
português, 26 ambíguos**; as docstrings de `inference.py` são inglesas. É a regra sendo ignorada na
direção que ninguém mede — a mesma lição das issues #95, #137 e #138: doutrina em contexto não
substitui um gate.

## What Changes

- **Declaração** `.code-locale` na raiz do repositório, `chave: valor` por linha, `#` para
  comentários; a chave `prose` aceita `pt-BR`, `pt`, `en`, `en-US` (normalizada para `pt`/`en`).
  Sem o arquivo, a direção "prosa" fica muda em todos os pontos (exit 0, zero achados) e
  `--explain` diz por quê. Um valor fora da lista é erro (exit 2) que nomeia o arquivo e os valores
  aceitos. O próprio catálogo **não** declara: README em inglês, changes em português — repositório
  misto, lacuna dita na skill.
- **Detector novo** `skills/code-locale/references/check-prose-locale.py`, irmão do de
  identificadores e com a mesma forma de linha de comando (`paths`, `--diff -`, `--stdin --lang
  --path`, `--root`, `--prose <lang>`, `--explain`, `--report`, `--selftest`; exit 1 só com achado
  gating, 2 em erro de uso ou declaração). Extrai comentários e docstrings com o `COMMENT_SYNTAX`
  do irmão — importado por caminho, não duplicado — e parágrafos de `.md` fora de fences e do
  frontmatter; classifica cada fragmento por palavras funcionais em duas listas fechadas
  (`prose-words-pt.txt`, `prose-words-en.txt`, interseção vazia por construção e afirmada no
  selftest, procedência em `prose-words.SOURCE.md`); ignora e **conta como pulado** o que é curto,
  código, entre aspas, URL, caminho, identificador. Gating: comentário/docstring com evidência
  forte na língua errada. Consultivo: parágrafo de `.md` e qualquer evidência fraca. Waivers:
  `locale-ok: <motivo>` na linha ou na linha acima, caminho em `.identifier-locale-allow`
  (`load_allowlist` do irmão), `LICENSE*`/`CHANGELOG*`/`NOTICE*` e árvores vendored pulados por
  padrão.
- **Refatoração no irmão**: `strip_prose()` vira wrapper fino de um tokenizador compartilhado
  (`split_prose()`) que devolve o código e os fragmentos de prosa com o tipo de cada um
  (`comment`, `docstring`, `string`); o comportamento do detector de identificadores é idêntico
  byte a byte e o selftest dele não é editado.
- **Hooks**: `locale-rite.py` localiza a declaração subindo do diretório do arquivo escrito (fallback
  `cwd`) até `.code-locale`, `.git` ou a raiz do sistema; com declaração, roda o detector de prosa
  sobre o texto escrito e, em `PreToolUse`, **nega** comentário/docstring gating com as mesmas três
  saídas no motivo; em `PostToolUse` avisa (`.md`, evidência fraca). `locale-stop-gate.py` mede o
  diff não commitado com o detector de prosa quando o repositório declara: bloqueia em gating,
  avisa em `.md`, mantém a guarda de `stop_hook_active`. Selftests com diretório temporário com e
  sem `.code-locale`, sem nunca ler a declaração ou a allowlist de quem roda.
- **Kit**: `pre-commit-locale.sh` roda o detector de prosa sobre o diff staged quando
  `$(git rev-parse --show-toplevel)/.code-locale` existe (mesma semântica de exit, mesmas dicas de
  waiver); `ci-step.md` documenta o step extra e a declaração.
- **Repo**: step `Prose-locale detector self-test` no `ci.yml`; linhas dos hooks no README mencionam
  a direção de prosa; `SKILL.md` do `code-locale` ganha a seção *Prose follows the repository*
  (formato da declaração, o que é medido, o que escapa, as saídas, por que o catálogo não declara)
  e `metadata.version` 1.4.3 -> 1.5.0; wrappers regenerados por `generate.sh`.
- **Calibração antes de publicar** (TR3): `--prose pt-BR --report` sobre `server_addons` com cada
  achado gating adjudicado à mão (precisão ≥ 0,9, senão a heurística estreita); `--prose en` sobre
  `skills/` e `claude/` do catálogo (esperado 0 gating); `--prose pt-BR` sobre
  `openspec/changes/archive` (prosa portuguesa, esperado 0 gating). As contagens vão em `tasks.md`
  S.3 e em `design.md`.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `skills-catalog`:
  - *Code locale has a canonical home* — a direção da prosa passa a ter declaração por repositório,
    detector próprio com listas fechadas de palavras funcionais, e o kit (pre-commit, CI) roda os
    dois detectores onde há declaração; sem declaração, tudo fica mudo e diz por quê.
  - *The code-locale rite is enforced at the moment of the write* — onde o repositório declara a
    prosa, comentário ou docstring na língua errada é negado no evento que precede a escrita, com as
    mesmas três saídas; `.md` e evidência fraca só avisam no evento que segue.
  - *The code-locale rite closes the turn, not only the write* — o gate de Stop mede a prosa do diff
    não commitado quando o repositório declara: bloqueia em gating, avisa em `.md`.

## Impact

- Skills tocadas: `code-locale` (SKILL.md, `references/check-identifier-locale.py`,
  `references/check-prose-locale.py` novo, `references/prose-words-pt.txt`,
  `references/prose-words-en.txt`, `references/prose-words.SOURCE.md` novos,
  `references/pre-commit-locale.sh`, `references/ci-step.md`). A composição do catálogo não muda
  (36 skills); a descrição da skill fica em 996/1024 caracteres, sem edição.
- Hooks: `claude/global/hooks/locale-rite.py`, `claude/global/hooks/locale-stop-gate.py` — os
  selftests atuais continuam verdes sem edição dos casos existentes.
- Repo: `.github/workflows/ci.yml` (um step), `README.md` (seção dos hooks), wrappers gerados
  (`claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`).
- Quem já tem os hooks wired não muda nada: sem `.code-locale` no repositório, o comportamento é o
  de hoje.

Fora de escopo, por decisão da issue: traduzir prosa existente (o `--report` lista o legado);
línguas além de PT/EN; strings de UI e mensagens de log (log keys são máquina, mensagens são prosa —
decisão registrada como KNOWN LIMIT no detector).
