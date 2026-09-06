# Change: As duas verificações do catálogo que não sabem reprovar

## Why

A change `update-documentation-prerequisites` (#154) acrescentou ao `skills-authoring` o requisito
*A prescribed verification states what passes*, e o `E.4` dela registrou que a varredura por
violações ainda não tinha sido feita.

Feita, sobre as 35 skills e 133 arquivos, em duas passadas: comentário de saída esperada (9 linhas,
todas na `documentation`) e prosa com verbo de verificação (67 linhas em 17 skills, das quais foram
julgadas as 2 skills com passo executável). Dois achados.

**`skills/claude-statusline/SKILL.md:130-142`** manda rodar o script contra um JSON de mentira e
**não diz o que a saída deve ser** — nem uma linha, nem um campo obrigatório, nem um formato. O
leitor executa, vê alguma coisa, e não tem contra o que comparar. O segundo teste da mesma seção pede
confirmar que os segmentos opcionais somem *"cleanly"*, e "cleanly" não se observa.

**`skills/documentation/references/examples.md:158`** traz `# Expected: All containers start without
errors`, que descreve uma **ausência** em vez de um valor. As outras oito linhas de saída esperada do
mesmo arquivo estão certas — `Docker version 24.x.x or higher`, `All services show "Up" status`,
`{"status": "healthy", …}` — e é o contraste que expõe esta. Exemplo é o que se imita, e este é o
exemplo da skill que escreveu a regra.

## What Changes

- `skills/claude-statusline/SKILL.md`, seção `## Verify`: a saída que o comando produz passa a estar
  escrita, **medida** rodando `references/statusline.sh` com o JSON do próprio documento; e o teste
  do caso vazio nomeia quais segmentos somem, no lugar de "cleanly".
- `skills/documentation/references/examples.md`: a linha de ausência vira um valor observável.
- `metadata.version` das duas skills sobe; árvores geradas regeneradas.
- Delta em `skills-authoring`: o requisito existente ganha o cenário que a varredura ensinou — linha
  fraca num **exemplo** de skill é defeito de primeira classe, porque exemplo é imitado.

## Deliberately not done

- **Julgar as 67 linhas de prosa uma a uma.** Foram amostradas as 2 skills com passo executável. A
  cobertura parcial é declarada aqui e no PR, conforme o cenário *Partial coverage is declared, not
  implied*; vira item próprio se esta entrega mostrar que vale.
- **Validador para o requisito.** A `D3` da change de origem mediu que um detector sobre prosa dá
  falso positivo nos dois sentidos (3 em 4 marcações), e a decisão continua valendo.
- **Reescrever a seção `## Verify` além das duas frases apontadas.** O resto dela está correto.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skills-authoring`: MODIFIED requirement *A prescribed verification states what passes* — ganha o
  cenário do exemplo. Uma saída esperada escrita num **exemplo** da skill vale como prescrição, porque
  é o que o leitor copia; e uma que descreve ausência ("without errors", "no failures") não é valor.

## Impact

- `skills/claude-statusline/SKILL.md` e `skills/documentation/references/examples.md`.
- `claude/`, `cursor/`, `plugins/` regenerados por `generate.sh`.
- Nenhuma skill entra, sai ou muda de nome: composição do catálogo e descoberta por `npx` intactas.
