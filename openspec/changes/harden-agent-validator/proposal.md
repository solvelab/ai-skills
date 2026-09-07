# Change: Endurecer o validador de agentes contra os oito achados

## Why

`scripts/validate-agents.py` foi entregue pelo PR #202 com A1–A7 e um selftest de 22 casos. Na prova
de campo daquele mesmo PR, o agente `bug-hunter-analyst` — publicado por ele — foi apontado para o
validador que o publicou e devolveu **oito** ataques, mais uma seção *TRIED AND FOUND NOTHING* com
seis linhas que não produziram nada e a razão de cada uma.

Dois deles são **falso verde**, não crash, e por isso são os graves:

1. **Campo obrigatório com null explícito passa tudo.** `field not in meta` testa só a presença da
   chave. `name:` sem valor satisfaz A1, e cada check seguinte é guardado por `if X is not None:` e
   pula. Um agente com os cinco campos nulos sai `findings: 0`: bypass completo do núcleo do gate.
   O subcaso `tools: ~` é o mais afiado — o comentário do próprio check diz que omitir `tools`
   concede tudo, e um null explícito é equivalente a omitir em runtime.
2. **`agents/` ausente faz o validador sair 0 sem checar órfão.** `main()` retorna antes de
   `check_layout()`. Apagado ou renomeado o diretório canônico com cópias ainda em
   `plugins/*/agents/`, a única checagem que pegaria isso é a que nunca roda.

Os outros seis: três entradas de arquivo derrubam a execução por exceção não tratada (diretório com
sufixo `.md`, bytes não-UTF-8 ou symlink pendurado, surrogate solto no `name` estourando no `print`),
uma expansão de âncora YAML sem teto de recurso, o A7 comparando **stems** e não conteúdo (uma cópia
gerada que divergiu passa), e uma decisão nunca escrita sobre `##\tWhen to invoke`.

## What Changes

- **Presença passa a ser valor presente, não chave presente.** Um campo obrigatório com valor nulo é
  tratado como ausente, e os checks seguintes deixam de ser puláveis por null.
- **`check_layout()` roda sempre**, mesmo sem `agents/`: é a checagem de órfão, e a ausência do
  diretório canônico é justamente um dos estados que ela precisa reprovar.
- **Nenhuma entrada de arquivo derruba a execução.** Diretório com sufixo `.md`, arquivo ilegível e
  symlink pendurado viram achado nomeado, e os demais agentes continuam sendo checados.
- **Âncoras e aliases YAML são recusados** no frontmatter de agente, o que remove a classe inteira da
  bomba de expansão em vez de tentar limitá-la.
- **A saída é à prova de caractere não codificável**, para que um surrogate solto vire achado legível
  em vez de estourar no meio da listagem.
- **A7 passa a comparar conteúdo**, não só nome: uma cópia gerada que divergiu da fonte canônica é
  achado.
- **A decisão sobre o espaço depois dos `##` é escrita e implementada**: qualquer espaço em branco é
  aceito, porque é o que um renderizador de Markdown aceita.
- O selftest cresce com um caso por defeito, cada um declarando o check que deve provocar — a lei que
  aquele arquivo já aplica, e que reprova também quando o defeito é pego pelo check errado.

**Não muda**: nenhum agente é criado, removido ou editado; nenhuma skill é tocada; `generate.sh`, o
H4 e o `README` ficam como estão.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `agents-catalog`: MODIFIED *A published agent declares its admission and its privilege* — o
  requisito passa a dizer que um campo obrigatório declarado sem valor é ausente, e que o gate não
  termina por exceção diante de entrada malformada. MODIFIED *Agents have a single canonical home and
  no orphans* — a lei de órfão passa a dizer o que compara (nome **e** conteúdo) e que a ausência do
  diretório canônico é ela própria um estado a reprovar.

## Impact

- `scripts/validate-agents.py` e `scripts/selftest-validate-agents.py`; nada mais em `scripts/`.
- Nenhuma mudança em `.github/workflows/ci.yml`: os dois steps já existem e passam a exercitar as
  regras novas.
- Os três agentes publicados continuam aprovando sem edição — o gate fica mais estrito, e eles já o
  cumpriam.
