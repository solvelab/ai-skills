# Change: Especializar por regime físico, não por taxonomia de objeto

## Why

`decision.md` do item #107 fechou com "uma nova skill `svg-animation`" e deixou o desenho da skill
para o item seguinte. Este é o item seguinte, e o desenho mudou por evidência medida.

Aplicando o método a 22 objetos e às 12 primitivas, os defeitos ficaram registrados em
`research/svg-animation/method.md` (dez ensaios) e `measurements.md`. Classificados pelo tipo de
conhecimento que faltava, de ~25 defeitos:

```
perspectiva / eixo errado          4    gaivota vista de baixo em corpo de perfil; torção da
                                        tartaruga usada como remada; paralaxe invertida em 3 cenas
acoplamento entre grandezas        3    velocidade da gota independente do diâmetro; celeridade
                                        independente do comprimento de onda; período orbital escolhido
classe de sistema errada           3    paralaxe em estrelas, que estão no infinito; glitter como
                                        teste na superfície desenhada quando 89% da inclinação não
                                        é desenhada; laço periódico para sistema excitado por ruído
plataforma / renderização          3    transform-box mordeu 3x; alpha proporcional ao fluxo em vez
                                        da magnitude; 26 fills de bounding box inteira a 1023 ms/s
processo sem critério de parada    2    doze primitivas sem lei; amplitude inventada ao lado de
                                        frequência medida, dando 968 graus/s
método de geometria                2    membros em trapézio; base de nuvem como laje e não corte
composição / legibilidade          1    copa densa demais, estrutura enterrada
ferramenta                         1    seis falsos positivos e a unidade do --cycle
CONHECIMENTO DE DOMÍNIO            6    modos de ramo; base no LCL; mecanismo do raio; biacromial
                                        0,259; nadadeira por espécie
```

**Cerca de um em quatro.** Os outros três quartos não seriam evitados por uma skill de "animais" ou
de "vegetação". A árvore é a prova mais dura: com os fatos de domínio já em mãos — 0,30 Hz para o
tronco, modos de ramo em 2, 7 e 11 Hz, amortecimento 10,6% — ela falhou quatro vezes seguidas, e
nenhuma falha foi por falta de fato. Foi amplitude inventada, modelo da classe errada, e detalhe
demais matando a legibilidade.

O que faltava não era domínio: era **um formulário do que precisa estar conhecido antes de
desenhar**, e esse formulário não depende do objeto, depende do REGIME. Árvore ao vento, bandeira,
trigal e placa pendurada são quatro domínios diferentes da divisão intuitiva e um único conjunto de
perguntas: modos próprios, amortecimento, espectro do forçamento, amplitude e sua fonte, coerência
espacial, média contra flutuação, e se o driver é estocástico.

## What Changes

- Publica `skills/svg-animation/`, cujo `SKILL.md` é o processo em fases mais um ROTEADOR que
  classifica o pedido em um ou mais regimes e carrega só os esquemas necessários.
- `references/regimes/*.md`: um esquema por regime físico, cada um com a lista de perguntas
  obrigatórias e o defeito medido que originou cada pergunta.
- `references/objects/*.md`: dossiês finos e citáveis, escritos quando o objeto é construído, não
  antecipadamente. Isso é o que escala: o número de regimes é pequeno e estável; o de dossiês
  cresce linearmente e barato.
- Três portões que a evidência exige e que nenhum esquema de domínio produziria: perspectiva antes
  de geometria, procedência obrigatória por grandeza, e comparação lado a lado ao mudar algo que
  já funcionava.

## Impact

- Capability tocada: `skills-catalog`.
- `research/svg-animation/` não muda: é a evidência, não o produto.
