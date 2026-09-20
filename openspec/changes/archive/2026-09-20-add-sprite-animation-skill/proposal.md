# Change: Skill sprite-animation — as quatro regras que só aparecem na tela

## Why

Em 2026-09-20, montando o boneco do gerente no `solvelab/my-company`
(issue #254), eu cometi quatro defeitos de animação por sprite na mesma
sessão. Os quatro passam em teste unitário, passam no typecheck, passam no
lint, e quebram na tela. Três só foram descobertos porque o autor olhou.

1. **Direção lida errado.** Recortei a caminhada de um grupo de uma folha
   combinada acreditando que olhava para a direita; olhava para a esquerda. O
   boneco atravessou a sala de costas.
2. **Escala medida por proxy inválido.** Para casar grupos desenhados em zooms
   diferentes, medi largura de cabelo (fator 1,60) e depois largura de rosto
   (outro número). As duas mentem entre vistas: cabelo e rosto mudam de
   largura conforme o ângulo, então comparar perfil com vista frontal não
   significa nada.
3. **Célula por pose em vez de célula única.** Alturas de 200, 190 e 185 px
   fizeram o boneco mudar de tamanho ao trocar de pose, porque o CSS renderiza
   todas na mesma altura.
4. **Duração escolhida no lugar da taxa.** Pus 0,8 s por ciclo sem conferir
   contra a velocidade da travessia. O corpo andava 3,39 alturas de boneco
   enquanto as pernas andavam 1,28: os pés deslizavam **2,64×**.

Um quinto só não aconteceu porque medi antes de confiar: o método clássico
`background-size: N00%` com `background-position` em porcentagem **não** cai
nos quadros, porque a porcentagem é resolvida sobre
`largura do elemento − largura da imagem`.

Nenhuma skill do catálogo cobre isso. `svg-animation` desenha o objeto,
`r3f-animation` é 3D, e `grep -ril sprite skills/` não devolve regra de folha
de quadros. O mapa canônico de `skills-authoring` não tem a entrada.

## What Changes

- Cria `skills/sprite-animation/` (category `frontend`): `SKILL.md` com as
  quatro regras, cada uma com o defeito medido que a produziu, mais a fronteira
  com `svg-animation`. `references/css-technique.md` com a técnica medida de
  reprodução em DOM/CSS e a alternativa que falha, e
  `references/cutting-sheets.md` com o método de recorte e normalização.
- Mapa canônico de `skills-authoring` ganha *animação por folha de quadros
  pronta* → `sprite-animation`, com a fronteira explícita contra
  `svg-animation`.
- `README.md` (tabela de skills, contagem), `generate.sh` e o plugin que
  embarca a skill.
- Espelho em `claude/skills/sprite-animation/`, gerado.

## Capabilities

### New Capabilities

- (nenhuma — `skills-catalog` ganha um requisito)

### Modified Capabilities

- `skills-catalog`: ADDED *Sprite sheet animation has a canonical home* — a
  skill que governa recorte, normalização de escala, célula, taxa de quadros e
  a conta que impede o deslize dos pés.
- `skills-authoring`: *Single canonical home per rule* — o mapa canônico ganha
  *animação por folha de quadros pronta* → `sprite-animation`.

## Impact

- Skills afetadas: nova `sprite-animation`; o plugin que a embarcar muda de
  composição (breaking para quem lê a descrição do plugin, não para nenhum
  `enabledPlugins`).
- Nenhum hook, script, node ou dependência nova:
  `find skills/sprite-animation -type f` lista só Markdown.
- Custo: zero em modelo. Toda a medição já existe, feita no `my-company` em
  2026-09-20, e está registrada nos commits daquele repositório.
- `svg-animation` e `r3f-animation` ganham uma linha de fronteira cada, não
  reescrita de conteúdo.
