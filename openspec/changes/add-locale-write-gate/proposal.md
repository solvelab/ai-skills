# Change: Cobrir o caminho no detector de locale e fechar o gate na hora da escrita

## Why

A doutrina do `code-locale` nomeia "module, package, file and directory names" como camada máquina, e
o docstring do detector afirma checar "identifiers, file and module names". O detector não lê o
caminho: seu único uso de `path` é o filtro de vendor (`skills/code-locale/references/check-identifier-locale.py:302`).
Medido em 2026-08-26 com Python 3.14.5:

```
$ python3 skills/code-locale/references/check-identifier-locale.py /tmp/.../servicos_pedido/calculo_frete.py
findings: 0
exit=0
$ python3 skills/code-locale/references/check-identifier-locale.py --diff /tmp/.../fake.diff
findings: 0
exit=0
```

O corpo do arquivo está em inglês; `servicos` e `calculo` são exatamente o defeito que a doutrina
nomeia, no artefato que o docstring diz cobrir, e os dois modos passam. Escopo documentado ≠ escopo
implementado.

Além disso, nada roda o detector no momento em que o nome é escrito. O detector é ferramenta de
revisão que alguém precisa invocar, e o passo de CI deste repositório gata apenas o script contra si
mesmo. Entre a doutrina estar no contexto e o código ser escrito não há medição — que é precisamente
a falha que os dois ritos já entregues (`backlog-rite.py`, `verify-rite.py`) foram construídos para
fechar nas suas próprias regras. Relato de campo do mantenedor (issue #95, 2026-08-26): nomes de
arquivo e identificadores em português continuam aparecendo em sessões novas, com a skill instalada.

## What Changes

- `skills/code-locale/references/check-identifier-locale.py` ganha um **tier de caminho**: os
  segmentos do caminho (diretórios + radical do arquivo) passam pelos mesmos tiers dos
  identificadores, em modo arquivo e em modo `--diff`.
- O tier de caminho respeita as regras já existentes: `is_vendored()`, `MIN_SEGMENT`, `DOMAIN_KEEP` e
  a allowlist `.identifier-locale-allow`, que é a única dispensa possível para um nome de arquivo —
  um arquivo não carrega comentário `locale-ok:`.
- Em `--diff`, o caminho é checado **apenas para arquivos adicionados** (`--- /dev/null`), mantendo a
  filosofia "código novo é inglês; nome existente migra por tier" do `references/migration.md`.
- Novo `claude/global/hooks/locale-rite.py`: hook `PostToolUse` em `Write`/`Edit` que roda o detector
  contra o caminho escrito e o conteúdo escrito, e devolve os achados ao assistente. Silencioso
  quando limpo, nunca bloqueante.
- `NOUNS` ganha `servico`, `servicos`, `calculo`, `relatorio`, `relatorios` — **desvio de escopo
  autorizado pelo mantenedor em 2026-08-26**, registrado como comentário na issue #95. A issue
  excluía ampliar o léxico; sem essas cinco palavras, `servicos_pedido/calculo_frete.py` era pego
  apenas por `pedido` e um diretório `servicos/` puro passava batido, o que deixava o critério de
  aceite falso. Nenhuma delas colide com palavra inglesa (`service`, `calculus`, `report` são as
  formas inglesas), e a assertion do próprio script é o que mantém isso honesto.
- `--selftest` cobre os tiers novos; `.github/workflows/ci.yml` gata o hook como gata os demais
  ("the gate is itself gated").
- `README.md` documenta o wiring do terceiro hook ao lado dos dois existentes.

**Não é BREAKING.** Nenhum nome existente é renomeado, nenhum comando muda de forma, e o modo
`--diff` continua sendo o modo de adoção.

## Capabilities

### New Capabilities

_Nenhuma._ Nenhum skill novo entra no catálogo.

### Modified Capabilities

- `skills-catalog`: duas requirements ADICIONADAS. A primeira fecha a distância entre o que o
  detector declara cobrir e o que ele lê — o caminho é artefato da camada máquina como qualquer
  identificador. A segunda estende ao locale a forma que a capability já especifica para os outros
  dois ritos (hook entregue, condicional, sem estado): o rito de locale passa a ser medido no momento
  da escrita, não apenas na revisão.

## Impact

- `skills/code-locale/references/check-identifier-locale.py`, `skills/code-locale/SKILL.md`,
  `claude/global/hooks/locale-rite.py` (novo), `.github/workflows/ci.yml`, `README.md`.
- `openspec/specs/skills-catalog/spec.md`, depois do archive.
- Espelhos gerados por `./generate.sh` (`claude/ codex/ cursor/ copilot/ plugins/`) — o passo de CI
  "Wrappers in sync with skills/" exige a regeneração.
- Composição do catálogo: inalterada. Nenhum skill entra, sai ou muda de nome, então a descoberta via
  `npx skills add` continua encontrando os mesmos 34.
- Consumidores do catálogo: quem já usa o detector ganha achados novos apenas em caminho de arquivo
  adicionado; quem não usa não muda nada. O hook é wiring do usuário em `~/.claude/settings.json`.
