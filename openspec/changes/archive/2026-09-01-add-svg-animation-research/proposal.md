# Change: Admitir prova executável como lastro de alegação técnica do catálogo

## Why

O catálogo não tem nenhuma cobertura de animação SVG. Medido em `a8405ae`, `grep -rniE '\bsvg\b'`
sobre as 34 skills devolve exatamente duas linhas, ambas URLs de badge em
`skills/documentation/references/templates.md:26-27`. O adjacente mais próximo, `r3f-animation`,
é animação 3D em three.js — seu `references/procedural-animation-patterns.md` manipula ossos
(`skeleton.bones.find`, `headBone.rotation.y`), não primitivas 2D reutilizáveis.

Decidir onde esse conhecimento deve morar exige pesquisa. E a pesquisa esbarra num problema de
forma que é do repositório, não do assunto: **o catálogo é documentação, e uma alegação de
performance não tem onde ser provada aqui.**

A primeira rodada de pesquisa já produziu o caso que torna isso concreto. Duas fontes primárias se
contradizem sobre o fato mais citado de toda a doutrina de animação SVG:

- O blog do Chrome afirma que, desde o Chromium 89, animações SVG passaram a ter aceleração por
  hardware habilitada por padrão.
- O `README.md` de `blink/renderer/core/animation`, na tag 85, dizia que o Chromium **não** suporta
  animação em thread de composição para elementos com transform SVG. No `main` de hoje, a frase
  sobre SVG simplesmente não existe mais — e ausência de menção não é prova de que a limitação caiu.

Nenhuma quantidade de leitura resolve isso. Só medição resolve. E hoje o repositório não tem lugar
para guardar a medição de forma que outra pessoa a reexecute.

## What Changes

- O repositório passa a admitir uma classe de artefato que ele não tem: **prova executável**,
  versionada, que sustenta uma alegação técnica da documentação.
- Essa prova vive fora de `skills/`, porque `generate.sh` publica apenas `skills/` — o que estiver
  fora fica versionado e revisável sem ser embarcado nos plugins dos consumidores.
- Uma alegação de custo no catálogo passa a exigir lastro: um artefato reexecutável neste
  repositório, ou um benchmark publicado nomeado. Alegação sem nenhum dos dois é removida, não
  suavizada.
- A medição passa a carregar o método: o que foi medido, como, em qual navegador e versão. Número
  sem método não é evidência.

## Capabilities

### Modified Capabilities

- `skills-catalog`: ganha o requisito de que uma alegação de custo publicada pelo catálogo tenha
  lastro reexecutável, e a regra de onde esse lastro vive em relação ao que é publicado. Hoje a
  capability governa composição do catálogo e os gates do próprio repositório
  (*"The repository itself is gated, not only its skills"*), mas nada diz sobre a evidência que
  sustenta o conteúdo técnico das skills.

## Impact

- `research/svg-animation/` — diretório novo: o relatório, a decisão arquitetural e os protótipos
  comparativos executáveis.
- Nenhuma skill é criada ou editada por esta change, então as contagens publicadas em `README.md`
  e `.claude-plugin/marketplace.json`, aferidas por `scripts/validate-repo-hygiene.py`, não se
  movem.
- Consumidores dos plugins não recebem nada de novo: o que `generate.sh` copia continua sendo só
  `skills/`.
