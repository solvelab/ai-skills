# Design — sprite-animation

## Context

A arte em folha de quadros é o caso em que **a arte já existe** e o trabalho é
reproduzi-la sem mentir sobre ela. Isso é o oposto do que `svg-animation`
resolve, onde não há arte e o trabalho é entender o objeto antes de desenhá-lo.
Os defeitos também são de outra natureza: não são de compreensão do objeto, são
de leitura da folha e de aritmética entre a folha e a cena.

Todos os números desta skill vêm de uma sessão só, medida: `solvelab/my-company`
em 2026-09-20, boneco do gerente, quatro defeitos corrigidos com medição no
navegador. A skill não publica número que não venha dali ou de especificação.

## Goals / Non-Goals

**Goals**

- Impedir os quatro defeitos medidos, cada regra carregando o defeito que a
  produziu.
- Publicar a **fórmula** do deslize, não a constante — quem adota deriva os
  próprios números.
- Fixar a técnica CSS que foi medida e nomear a que falha, com a razão de
  especificação.

**Non-Goals**

- Substituir `svg-animation`. A fronteira é: arte pronta em quadros → esta;
  objeto a desenhar → aquela.
- Entregar ferramenta de corte. A skill prescreve o método; script é decisão do
  projeto que adotar.
- Cobrir motor de sprite, atlas ou packer. A skill cobre a técnica DOM/CSS que
  foi medida e declara o teto a partir do qual canvas passa a valer.

## Decisions

**A regra carrega o defeito, não a boa prática.** O catálogo já faz isso
(`svg-animation` abre com a classificação dos defeitos medidos). Uma regra sem
o erro ao lado vira conselho, e conselho não sobrevive a um prazo.

**A conta do deslize é a peça central.** As outras três regras evitam erro de
montagem; esta evita o defeito que ninguém vê. Ela é publicada como fórmula
porque a passada, a distância e a altura do boneco mudam por projeto:

```
avanço por ciclo = 2 × passada        (passada em alturas de figura)
velocidade       = avanço × fps ÷ quadros_por_ciclo
duração          = distância ÷ velocidade
```

**A taxa é restrita a divisores de 60.** O compositor do navegador roda a
60 Hz; uma taxa que não divide faz um quadro durar duas atualizações e o
seguinte durar três. Não é preferência, é o que a composição impõe.

**A escala entre grupos não se mede por proxy.** Cabelo e rosto mudam de
largura com o ângulo da vista. O método que funciona é comparar a mesma figura
lado a lado, alinhada pelo pé, em escalas candidatas — e a skill diz isso em
vez de propor um proxy melhor, porque não existe proxy válido entre vistas
diferentes.

**Uma folha por direção, com o sentido no nome do arquivo.** Foi o que
encerrou o defeito 1 no `my-company`. A regra não é "olhe com atenção"; é
"não haja o que interpretar".

## Canonical Home & Cross-Links (MANDATORY)

| Regra | Casa canônica | O que esta skill faz |
|---|---|---|
| Animação por folha de quadros pronta | **`sprite-animation`** (nova) | define |
| Entender o objeto antes de desenhá-lo; escolha de tecnologia de animação | `svg-animation` | linka, uma linha de fronteira |
| Animação 3D | `r3f-animation` | linka, uma linha de fronteira |
| Verificar antes de afirmar; escada de pesquisa; relatar o não-encontrado | `verify-before-claiming` | linka — os quatro defeitos são instâncias de afirmar sem medir |
| Volume de código, marcador `lean:` e o teto declarado | `lean-code` | linka — o teto DOM/CSS → canvas usa o marcador |
| Fronteira identificador/prosa | `code-locale` | linka |

`svg-animation` e `r3f-animation` ganham **uma linha** apontando para cá
quando o pedido traz arte pronta em quadros; nenhum mecanismo delas é
reproduzido aqui, e nenhum daqui é reproduzido nelas.

## Risks / Trade-offs

- **Virar tratado de animação.** Mitigação: o escopo é o que foi medido em
  2026-09-20; regra sem medição não entra, e isso está no `tasks.md` como
  gate.
- **Os números envelhecerem.** Mitigação: são de especificação (a resolução
  de porcentagem de `background-position`, a semântica de `steps()`) ou de
  geometria da arte (passada sobre altura), não de versão de ferramenta. O
  pin de `Verified against` diz exatamente isso.
- **Duplicar `svg-animation` sem perceber.** Mitigação: a tabela acima, e a
  fronteira escrita nos dois sentidos.
