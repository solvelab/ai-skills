## ADDED Requirements

### Requirement: A skill que representa objetos declara o regime antes de desenhar

Uma skill do catálogo que produza representação visual de um objeto SHALL classificar o pedido em
um ou mais REGIMES antes de qualquer geometria, e SHALL carregar o esquema de cada regime
classificado. Um regime é um tipo de sistema — corpo articulado, estrutura oscilante forçada,
campo de ondas dispersivo, ensemble balístico — e não um domínio temático. A classificação por
domínio SHALL NOT substituir a classificação por regime, porque a evidência medida em
`research/svg-animation/method.md` mostra que cerca de três quartos dos defeitos registrados não
eram falta de conhecimento de domínio.

#### Scenario: pedido que combina dois regimes

- **WHEN** o pedido é uma árvore ao vento
- **THEN** a skill classifica em `growth-structure` para a geometria e em `driven-oscillator` para
  o movimento, e carrega os dois esquemas
- **AND** nenhum dos dois esquemas é um esquema de "vegetação"

#### Scenario: regime sem esquema publicado

- **WHEN** o pedido cai num regime para o qual não existe esquema em `references/regimes/`
- **THEN** a skill diz qual regime faltou e o que não pode garantir sem ele
- **AND** SHALL NOT prosseguir apresentando o resultado como se o regime tivesse sido coberto

### Requirement: Toda grandeza usada carrega procedência

Uma skill que use números para construir ou animar SHALL marcar cada grandeza como `measured`,
`derived from <X>` ou `assumed`, e uma grandeza `assumed` SHALL aparecer na entrega. A regra existe
porque o defeito mais caro registrado foi amplitude inventada escrita ao lado de frequência medida,
sem nada distinguindo as duas: 11 Hz com 14 graus dá 968 graus por segundo, uma ponta de galho a
27% da velocidade do vento, sustentada.

#### Scenario: número sem fonte

- **WHEN** uma grandeza necessária não tem valor publicado nem derivação
- **THEN** ela é marcada `assumed` e aparece na entrega com o valor adotado
- **AND** SHALL NOT ser apresentada junto das medidas sem distinção

### Requirement: Perspectiva é portão, não observação

Uma skill que represente um objeto SHALL fixar a vista antes da geometria e SHALL expressar cada
número cinemático nos eixos dessa vista. Quando o eixo principal do mecanismo não for visível na
vista escolhida, quando o objeto tiver mais de uma vista canônica, ou quando o tamanho de leitura
mudar o que precisa existir, a skill SHALL perguntar em vez de escolher.

#### Scenario: eixo do mecanismo invisível na vista

- **WHEN** o pedido é um golfinho visto de cima, e a remada do golfinho é vertical
- **THEN** a skill aponta que o movimento característico não aparece nessa vista e pergunta
- **AND** SHALL NOT desenhar a remada como se fosse lateral

### Requirement: Mudança em algo que já funcionava passa por comparação lado a lado

Quando uma skill alterar um artefato que já funcionava, SHALL produzir uma comparação lado a lado
entre a versão nova e a que ela substitui antes de manter a mudança. Verificar contra a lei diz que
a versão nova é verdadeira; não diz que a velha era melhor. Três versões sucessivas da árvore
passaram por todos os portões existentes — cinemática direta, rastreio de movimento, velocidade de
pico e custo — e cada uma era pior que a anterior.

#### Scenario: correção que regride

- **WHEN** uma alteração é verificada contra a física e passa
- **THEN** a comparação lado a lado com a versão anterior é apresentada antes de manter
- **AND** se a anterior for melhor, a alteração é revertida ou reduzida
