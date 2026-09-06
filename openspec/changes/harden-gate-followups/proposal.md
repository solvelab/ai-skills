# Change: Fechar os follow-ups dos gates — `-z` no spec-rite, vendored no `scan_diff`, selftest sem 27 cópias, `VERSION` no `ci.yml`

## Why

Cinco pontos anotados nos grupos E.4 das changes arquivadas em 2026-09-04/06 — todos sobre os
gates e o que eles deixam passar — foram reproduzidos em `e7f5fe8` (2026-09-06) antes de escrever
esta change:

1. `scripts/validate-spec-rite.py:168` lê `git diff --name-only` **sem** `-z`. Um caminho com
   caractere não-ASCII sai quotado (`"openspec/changes/probe-quoted/specs/caf\303\251.md"`), não
   começa com `openspec/`, vira ofensor e não casa com `openspec/changes/<id>/`. Medido num clone
   com uma change ativa e um arquivo `café.md` dentro dela: o gate emite `S3 unrelated change`
   contra um PR que **toca** sua própria change. `validate-skill-version.py` já corrigiu o mesmo
   ponto com `-z` + `split_nul_paths()` (#132); o irmão ficou para trás.
2. `skills/code-locale/references/check-identifier-locale.py`: `is_vendored()` (`:393`) protege
   `scan_path()` (`:525`) e o `main()` (`:878`), mas `scan_diff()` (`:612`) não a aplica. Um diff
   que adiciona `node_modules/servicos_pedido/calculo.js` com `const usuario = 1` produz 2 achados
   gatantes — o caminho fica mudo (o path tier herda a exclusão), o conteúdo não.
3. `scripts/selftest-validate-skills.py:123` faz `shutil.copytree` do repositório inteiro **por
   mutação**: 27 cópias por run, 49,1 s de parede em `e7f5fe8`; o step *Validator self-test* do CI
   paga isso a cada PR. Medido antes de escrever: as cópias são 1,9 s desses 49,1 s — o resto são
   as 27 runs do validador (1,7 s cada). A cópia única vale pelo churn e pela isolação provada, não
   pelo relógio (`design.md` D3).
4. O step *Version coherence* do `ci.yml` lê `VERSION` com `tr -d '[:space:]'` e compara por
   substring: `2.15.1dirtychange` nos três arquivos passa com `Version 2.15.1dirtychange coherent
   across manifests.` — a regex ancorada que `generate.sh:32` e `set-version.sh:15` usam desde
   #114 não chegou ao CI.
5. `README.md:443` publica `r3f-*/SKILL.md # React Three Fiber skills (10 topics)` dentro de um
   bloco de código; o gate H2/H3 ignora blocos de código por desenho e `game` tem 12 skills.

## What Changes

- `validate-spec-rite.py` lê o diff com `-z` e separa por NUL, com o helper `split_nul_paths()`
  duplicado do irmão (comentário nomeia `validate-skill-version.py` e o motivo de não importar); o
  selftest ganha um probe em repositório descartável com `core.quotePath=true` e um caminho não-ASCII
  dentro de `openspec/changes/<id>/`, que tem de registrar o diff.
- `check-identifier-locale.py`: `scan_diff()` aplica `is_vendored()` ao caminho do `+++`, pula o
  bloco inteiro (caminho e linhas adicionadas) e devolve o caminho numa lista de pulados que o
  `main()` imprime na linha `skipped (vendored/generated/minified)` que já existe; caso de selftest
  com `node_modules/` no diff; KNOWN LIMIT 12 passa a dizer o que o modo `--diff` pula.
  `code-locale` sobe para `1.4.3` e os wrappers são regenerados.
- `selftest-validate-skills.py`: uma cópia por run; cada mutação é aplicada à cópia e desfeita
  (bytes originais restaurados, arquivo criado removido, diretório criado removido) antes da
  seguinte, e a cópia é comparada byte a byte com a origem depois do laço (`LEAKED` reprova). Os 27
  casos continuam todos `CAUGHT`; tempo antes/depois registrado em `tasks.md` (49,7 s → 47,5 s,
  média de três rounds alternados).
- `ci.yml`, step *Version coherence*: `VERSION` é validado contra
  `^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$` **antes** da comparação com os manifests, e um
  valor fora da forma reprova com `::error` nomeando o valor.
- `README.md:443`: o comentário da árvore diz o que é (`one skill per topic`), sem contagem.

Nenhuma dessas mudanças é **BREAKING** para consumidores do catálogo: nenhuma skill entra, sai ou
muda de nome. O detector de locale fica **menos** ruidoso em `--diff` (um diff vendored deixa de
reprovar); o spec-rite fica **mais** correto (um PR com caminho quotado dentro da própria change
deixa de reprovar); o CI fica mais restritivo só para um `VERSION` malformado.

## Capabilities

### New Capabilities

_Nenhuma._ Nenhuma skill nova entra no catálogo.

### Modified Capabilities

- `skills-catalog`: *The repository itself is gated, not only its skills* — o gate que registra
  um pull request lê os caminhos do diff separados por NUL, para que um caminho que o git quotaria
  em modo de linha ainda ligue o diff à sua change (cenário *A quoted path still registers its
  change*).
- `skills-catalog`: *The identifier-locale check reads the path it is given* — em modo diff a
  exclusão de árvores vendored cobre o arquivo inteiro que o cabeçalho `+++` nomeia, caminho e
  linhas adicionadas, e o arquivo é contado como pulado, não como aprovado (cenário *A vendored
  path in a diff is skipped, not measured*).

## Impact

- `scripts/validate-spec-rite.py` — `changed_paths()`, novo `split_nul_paths()`, docstring, dois
  casos de selftest (helper literal + probe em repositório descartável).
- `skills/code-locale/references/check-identifier-locale.py` — `scan_diff()`, `main()`, KNOWN LIMIT
  12, um caso em `selftest_paths()` e a contagem impressa no `selftest OK`.
- `skills/code-locale/SKILL.md` — `metadata.version` 1.4.2 → 1.4.3 e a linha *Verified against*
  (contagem de casos mudos do path tier 9 → 10, data do probe); wrappers regenerados por
  `./generate.sh` (`claude/skills/code-locale/`, `plugins/workflow/skills/code-locale/`).
- `scripts/selftest-validate-skills.py` — laço de mutações; nenhuma mutação muda.
- `.github/workflows/ci.yml` — só o step *Version coherence*.
- `README.md:443` — um comentário numa árvore ilustrativa.
- Os hooks `claude/global/hooks/locale-rite.py` e `locale-stop-gate.py` importam o detector e não
  mudam; os selftests dos dois são rodados depois da edição (S.1).
- Composição do catálogo (36 skills, descoberta via `npx`) fica idêntica.
