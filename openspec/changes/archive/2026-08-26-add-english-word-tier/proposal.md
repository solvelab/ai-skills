# Change: Perguntar se a palavra é inglesa, em vez de caçar português

## Why

O detector decide hoje por `"esta palavra está na minha lista de português?"`. A lista tem 24 verbos,
~60 substantivos e uma regex de morfologia. O vocabulário aberto é a língua inteira, então cada
palavra adicionada conserta exatamente uma palavra. Medido em 2026-08-26, depois de já ter ampliado o
léxico na change anterior:

```
prazo   -> None      chave -> None      apuracao -> None
```

A regra do mantenedor não é "evite as palavras da lista" — é **todo código é inglês**. Um checador
cuja resposta padrão é "passa" não consegue expressar essa regra: a direção da falha está invertida,
porque o desconhecido é tratado como aprovado.

## What Changes

- Tier novo `en-unknown`: um segmento que não está no dicionário inglês, nem na allowlist, nem em
  `DOMAIN_KEEP`/`KEYWORDS`, nem abaixo de `MIN_SEGMENT`, é reportado.
- `skills/code-locale/references/english-words.txt.gz` — lista de **domínio público** (`dwyl/english-words`,
  Unlicense), filtrada para comprimento ≥ 4. Medido: 370.105 palavras originais, 369.652 após o
  filtro, 3,7 MB em texto e **1,1 MB comprimida**; lida com o módulo `gzip` da stdlib.
- `skills/code-locale/references/programming-words.txt` — vocabulário de programação que dicionário
  natural nenhum carrega (`printf`, `stdin`, `argparse`, `rglob`, `yaml`…), curado e MIT.
- **Regra de composto**: um segmento que se divide em duas palavras conhecidas é conhecido. Medido em
  13 de 13 compostos reais deste repositório: `selftest` -> `self+test`, `allowlist` -> `allow+list`,
  `frontmatter` -> `front+matter`, `bytecode` -> `byte+code`.
- **Advisory por padrão**: achado `en-unknown` é impresso e contado à parte, e **não** muda o exit
  code. `--gate-unknown` o torna bloqueante para quem quiser.
- `--en-dict PATH` troca a lista embutida por outra; caminho ilegível é erro explícito, nunca queda
  silenciosa para "limpo".
- Os tiers `pt-*` continuam gatando exatamente como hoje; confiança alta continua alta.

**Não é BREAKING**: nenhum exit code muda sem a flag nova, e nenhum nome existente é renomeado.

## Capabilities

### New Capabilities

_Nenhuma._

### Modified Capabilities

- `skills-catalog`: uma requirement ADICIONADA — o check passa a fazer também a pergunta de mundo
  fechado, e a resposta dela é advisory até que o ruído seja medido em campo. É requirement nova, e
  não emenda de `The identifier-locale check reads the path it is given`, porque aquela governa **o
  que** é lido e esta governa **como se decide** que um nome está errado.

## Impact

- `skills/code-locale/references/check-identifier-locale.py`, mais dois arquivos de dados novos em
  `references/`.
- `skills/code-locale/SKILL.md`, `claude/global/hooks/locale-rite.py` (advisory mostrado como advisory).
- Espelhos gerados: o `generate.sh` copia `references/` para `plugins/`, então a lista comprimida
  aparece duas vezes no repositório — 2,2 MB no total. `scripts/validate-repo-hygiene.py` gata apenas
  bytecode Python (`__pycache__/`, `.py[cod]`), verificado no código do gate, então um `.gz` de dados
  passa.
- Consumidores: quem roda o check ganha uma seção advisory na saída; o exit code só muda com a flag.

## Por que não o dicionário do sistema

`/usr/share/hunspell/en_US.dic` está instalado nesta máquina e tem 79.013 entradas, mas **não contém
`read`, `input`, `context`, `math`, `detail`, `reset`, `decode` nem `struct`** — verificado linha a
linha, o arquivo salta de `react/V` para `readability/SM`. Um dicionário com buracos em palavras-base
transformaria `read` em achado. A lista de domínio público contém todas as oito.
